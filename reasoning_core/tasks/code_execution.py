import ast, io, re, sys, os, time, random, signal, inspect, contextlib, multiprocessing as mp
from dataclasses import dataclass
from difflib import SequenceMatcher
from itertools import product

from reasoning_core.template import Task, DevTask, Problem, Config, edict, stochastic_rounding as sround
from gramforge import generate
from gramforge.grammars import mesopy_grammar


@dataclass
class MesopyCodeCfg(Config):
    difficulty: float = 0.0
    min_depth: int = 4
    max_depth: int = 15
    max_attempts: int = 180
    timeout: float = 0.5
    magnitude: int = 3
    n_functions: int = 2
    max_answer_len: int = 80
    max_steps: int = 10_000
    min_steps: int = 4
    shortcut_prob: float = 0.08
    trivial_accept_prob: float = 0.05
    trivial_probes: int = 3
    runnable_prob: float = 0.25
    syntax_error_prob: float = 0.25
    runtime_mutation_prob: float = 0.60

    def apply_difficulty(self, level):
        self.difficulty += level
        self.min_depth = sround(self.min_depth + 0.5 * level)
        self.max_depth = sround(self.max_depth + level)
        self.n_functions = sround(self.n_functions + 0.5 * level)
        self.magnitude = sround(self.magnitude + 0.5 * level)
        self.min_steps = sround(self.min_steps + 2 * level)


@dataclass
class RunReport:
    ok: bool = False
    value: str | None = None
    error: str | None = None
    args: list | None = None
    stdout: str = ""
    stderr: str = ""
    steps: int = 0
    elapsed: float = 0.0


class CapIO(io.StringIO):
    def __init__(self, cap=2000):
        super().__init__()
        self.cap = cap

    def write(self, s):
        if self.tell() < self.cap:
            super().write(s[: self.cap - self.tell()])
        return len(s)


class StepLimit(BaseException):
    pass


def fake(t, magnitude=3):
    n = max(1, int(magnitude))
    return {
        int: lambda: random.randint(-n, n),
        str: lambda: "".join(random.choices("abcxyz", k=random.randint(0, n))),
        list: lambda: [random.randint(-n, n) for _ in range(random.randint(0, n))],
    }.get(t, lambda: None)()


def endpoint_args(fn, magnitude=3):
    return [fake(p.annotation, magnitude) for p in inspect.signature(fn).parameters.values()]


def call_src(args):
    return f"endpoint({', '.join(map(repr, args))})"


def soft_score(answer, reference):
    norm = lambda x: re.sub(r"\s+", " ", str(x).strip())
    a, b = norm(answer), norm(reference)
    return 1.0 if a == b else SequenceMatcher(None, a, b).ratio()


def value_kind(x):
    return "list" if x.startswith("[") else "str" if x.startswith(("'", '"')) else "int"


def accept_steps(steps, cfg):
    if steps >= cfg.min_steps:
        return True
    if cfg.min_steps <= 0:
        return True
    return random.random() < cfg.shortcut_prob * ((steps + 1) / cfg.min_steps) ** 2


def function_triviality(reports):
    good = [r for r in reports if r.ok and r.args is not None]
    if len(good) < 2:
        return None
    if len({r.value for r in good}) == 1:
        return "constant"
    for i in range(min(map(lambda r: len(r.args), good), default=0)):
        if all(r.value == repr(r.args[i]) for r in good):
            return "identity"
    return None


def kill(p):
    if p.is_alive():
        p.terminate()
        p.join(0.05)
        if p.is_alive():
            os.kill(p.pid, signal.SIGKILL)
            p.join()


def _worker(send, code, magnitude, recursionlimit, max_steps, call_args=None, batch=False):
    out, err = CapIO(), CapIO()
    ns = {"__builtins__": __builtins__}
    steps, t0 = 0, time.perf_counter()
    sys.setrecursionlimit(recursionlimit)

    try:
        import resource

        resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2, 512 * 1024**2))
    except Exception:
        pass

    def trace(frame, event, arg):
        nonlocal steps
        if event == "line":
            steps += 1
            if steps > max_steps:
                raise StepLimit
        return trace

    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            exec(compile(code, "<mesopy>", "exec"), ns, ns)
            args = call_args if call_args is not None else endpoint_args(ns["endpoint"], magnitude)
            args_list = args if batch else None
            values = []
            for a in args_list or [args]:
                steps = 0
                sys.settrace(trace)
                try:
                    values.append(repr(ns["endpoint"](*a))[:500])
                finally:
                    sys.settrace(None)

        r = RunReport(
            True,
            values if args_list else values[0],
            None,
            args,
            out.getvalue(),
            err.getvalue(),
            steps,
            time.perf_counter() - t0,
        )

    except StepLimit:
        sys.settrace(None)
        r = RunReport(
            False,
            None,
            "TimeoutError",
            locals().get("args"),
            out.getvalue(),
            err.getvalue(),
            steps,
            time.perf_counter() - t0,
        )

    except Exception as e:
        sys.settrace(None)
        r = RunReport(
            False,
            None,
            type(e).__name__,
            locals().get("args"),
            out.getvalue(),
            err.getvalue(),
            steps,
            time.perf_counter() - t0,
        )

    try:
        send.send(r)
    except Exception:
        pass
    send.close()


def run_code(code, cfg, recursionlimit=80, call_args=None, batch=False):
    ctx = mp.get_context("fork")
    recv, send = ctx.Pipe(duplex=False)
    p = ctx.Process(target=_worker, args=(send, code, cfg.magnitude, recursionlimit, cfg.max_steps, call_args, batch))
    p.start()
    send.close()
    timeout = min(4.0, cfg.timeout + 0.01 * len(call_args)) if batch else cfg.timeout

    try:
        if recv.poll(timeout):
            r = recv.recv()
            p.join(0.05)
            kill(p)
            return r

        kill(p)
        return RunReport(error="TimeoutError", args=call_args, elapsed=timeout)

    except KeyboardInterrupt:
        kill(p)
        raise

    finally:
        recv.close()


def make_code(cfg, failure_rate, profile="full"):
    fast = profile == "runnability"
    g = mesopy_grammar(
        mode="function",
        n_functions=max(1, int(cfg.n_functions)),
        max_number=max(4, int(8 + 2 * cfg.difficulty)),
        max_params=2 + int(cfg.difficulty >= 4),
        param_types=("int", "str", "list"),
        return_types=("int", "str", "list"),
        emit_endpoint=True,
        emit_result=False,
        failure_rate=failure_rate,
        triviality_rate=max(0.05, 0.5 - 0.05 * cfg.difficulty),
        allow_recursion=not fast,
        include_loops=not fast,
        include_try_except=not fast,
        include_comprehensions=not fast,
        include_fstrings=not fast,
        include_break_continue=not fast,
        min_body_stmts=2 if fast else 1,
    )
    return generate(g, depth=cfg.max_depth, min_depth=cfg.min_depth) @ "py"


def source_endpoint_args(code, cfg):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "endpoint":
            args = []
            for arg in node.args.args:
                name = getattr(arg.annotation, "id", None)
                args.append(fake({"int": int, "str": str, "list": list}.get(name), cfg.magnitude))
            return args
    return None


def subtle_syntax_error(code):
    lines = code.splitlines()
    edits = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("def ") and "," in line:
            edits.append((i, line.replace(",", "", 1)))
        if stripped.startswith("def ") and re.search(r"\w+: \w+", line):
            edits.append((i, re.sub(r"(\w+): (\w+)", r"\1 \2", line, count=1)))
        if re.search(r"\w+\([^()\n]*,\s*[^()\n]*\)", line):
            edits.append((i, line.replace(",", "", 1)))
        if stripped.endswith(":") and stripped.split(None, 1)[0] in {"def", "if", "elif", "else", "for", "while", "try", "except"}:
            edits.append((i, line[:-1]))
    random.shuffle(edits)
    for i, replacement in edits:
        candidate = lines[:]
        candidate[i] = replacement
        candidate = "\n".join(candidate) + "\n"
        try:
            compile(candidate, "<mesopy>", "exec")
        except SyntaxError:
            return candidate
    return None


def sample_syntax_error_problem(cfg):
    for _ in range(max(1, cfg.max_attempts // 3)):
        code = make_code(cfg, failure_rate=0.0, profile="runnability")
        args = source_endpoint_args(code, cfg)
        if args is None:
            continue
        broken = subtle_syntax_error(code)
        if broken is not None:
            return broken, RunReport(False, None, "SyntaxError", args)
    raise RuntimeError("Failed to generate syntax error task")


def function_arities(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}
    return {
        node.name: len(node.args.args)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }


def function_name_scopes(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    scopes = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        names = {arg.arg for arg in node.args.args}
        names.update(
            child.id
            for child in ast.walk(node)
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)
        )
        scopes.append((node.name, node.lineno, getattr(node, "end_lineno", node.lineno), names))
    return scopes


def runtime_error_mutations(code):
    lines = code.splitlines()
    edits = []
    arities = function_arities(code)
    scopes = function_name_scopes(code)
    all_names = set().union(*(names for _, _, _, names in scopes)) if scopes else set()
    call_re = re.compile(r"\b(f\d+|endpoint)\(([^()\n]*)\)")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("def "):
            continue
        for m in call_re.finditer(line):
            args = [a.strip() for a in m.group(2).split(",") if a.strip()]
            if len(args) == arities.get(m.group(1), 0) and len(args) >= 2:
                repl = f"{m.group(1)}({', '.join(args[:-1])})"
                edits.append((i, line[: m.start()] + repl + line[m.end() :]))
        scope = next((s for s in scopes if s[1] <= i + 1 <= s[2]), None)
        if scope and scope[0] != "endpoint" and any(stripped.startswith(prefix) for prefix in ("return ", "if ", "elif ", "print(")):
            local_names = scope[3]
            foreign_names = sorted(all_names - local_names)
            ids = [
                name for name in re.findall(r"\b[a-z]\w*\b", line)
                if name not in {"if", "elif", "else", "return", "print", "len", "True", "False"}
                and not re.fullmatch(r"f\d+", name)
                and name in local_names
            ]
            if ids and foreign_names:
                name = random.choice(ids)
                replacement = random.choice(foreign_names)
                edits.append((i, re.sub(rf"\b{re.escape(name)}\b", replacement, line, count=1)))
        if re.search(r"(%|//|/)\s*[1-9]\d*", line):
            edits.append((i, re.sub(r"(%|//|/)\s*[1-9]\d*", lambda m: m.group(1) + " 0", line, count=1)))
    random.shuffle(edits)
    for i, replacement in edits:
        candidate = lines[:]
        candidate[i] = replacement
        yield "\n".join(candidate) + "\n"


def sample_mutated_runtime_error_problem(cfg):
    for _ in range(max(1, cfg.max_attempts // 3)):
        code = make_code(cfg, failure_rate=0.0, profile="runnability")
        if source_endpoint_args(code, cfg) is None:
            continue
        for candidate in runtime_error_mutations(code):
            r = run_code(candidate, cfg)
            if r.error and r.args is not None and r.error != "TimeoutError":
                return candidate, r
    raise RuntimeError("Failed to generate mutated runtime error task")


def meta(code, r):
    return edict(
        code=code,
        args=r.args,
        call=call_src(r.args),
        steps=r.steps,
        elapsed=r.elapsed,
        stdout=r.stdout,
        stderr=r.stderr,
        triviality=getattr(r, "triviality", None),
    )


def sample_problem(cfg, want_error, failure_rate, profile="full", syntax_errors=False):
    if want_error and syntax_errors:
        roll = random.random()
        if roll < cfg.syntax_error_prob:
            try:
                return sample_syntax_error_problem(cfg)
            except RuntimeError:
                pass
        elif roll < cfg.syntax_error_prob + cfg.runtime_mutation_prob:
            try:
                return sample_mutated_runtime_error_problem(cfg)
            except RuntimeError:
                pass

    for _ in range(cfg.max_attempts):
        code = make_code(cfg, failure_rate, profile)
        if "def endpoint" not in code:
            continue

        r = run_code(code, cfg)

        if want_error:
            if r.error and r.args is not None and r.error != "TimeoutError":
                return code, r

        elif r.ok and r.value is not None and len(r.value) <= cfg.max_answer_len:
            if profile == "runnability":
                triviality = None
            else:
                probes = [r] + [run_code(code, cfg) for _ in range(cfg.trivial_probes - 1)]
                triviality = function_triviality(probes)
            if (
                accept_steps(r.steps, cfg)
                and (not triviality or random.random() < cfg.trivial_accept_prob)
            ):
                r.triviality = triviality
                return code, r

    raise RuntimeError(f"Failed to generate valid task. Config: {cfg}")


class CodeRunnability(Task):
    summary = "Predict if a given Python code snippet runs successfully or raises an exception."
    def __init__(self, config=None):
        super().__init__(config=config or MesopyCodeCfg())
        self.balancing_key_ratio = 1 / 5

    def generate(self):
        want_error = random.random() >= self.config.runnable_prob
        code, r = sample_problem(
            self.config,
            want_error=want_error,
            failure_rate=0.65 if want_error else 0.05,
            profile="runnability",
            syntax_errors=True,
        )
        return Problem(metadata=meta(code, r), answer=r.error or "OK")

    def prompt(self, metadata):
        return (
            "Predict whether this Python call runs successfully or raises an exception.\n"
            f"```python\n{metadata.code}\n```\n"
            f"Call: `{metadata.call}`\n"
            "The answer is `OK` if it runs successfully; otherwise the exception class name."
        )

    def score_answer(self, answer, entry):
        reference = entry["answer"] if isinstance(entry, dict) else entry.answer
        return float(str(answer).strip() == str(reference).strip())

    def balancing_key(self, problem):
        return str(problem.answer)


class CodeExecution(Task):
    summary = "Predict the return value or stdout of executing generated Python code blocks."
    def __init__(self, config=None):
        super().__init__(config=config or MesopyCodeCfg())

    def generate(self):
        code, r = sample_problem(self.config, want_error=False, failure_rate=0.05)
        return Problem(metadata=meta(code, r), answer=r.value)

    def prompt(self, metadata):
        return (
            "Predict the value returned by this Python call.\n"
            f"```python\n{metadata.code}\n```\n"
            f"Call: `{metadata.call}`\n"
            "The answer is the exact Python `repr` of the returned value."
        )

    def score_answer(self, answer, entry):
        reference = entry["answer"] if isinstance(entry, dict) else entry.answer
        return soft_score(answer, reference)

    def balancing_key(self, problem):
        return value_kind(problem.answer)


@dataclass
class CodeInputDeductionCfg(MesopyCodeCfg):
    min_depth: int = 3
    max_depth: int = 8
    n_functions: int = 1
    lo: int = -6
    hi: int = 9
    max_len: int = 3
    alphabet: str = "abc"
    max_attempts: int = 100

    def apply_difficulty(self, level):
        self.lo = sround(self.lo - level)
        self.hi = sround(self.hi + level)
        self.max_len = sround(self.max_len + 0.5 * level)


def bounded_strings(alphabet, max_len):
    return [
        "".join(xs)
        for n in range(1, max_len + 1)
        for xs in product(alphabet, repeat=n)
    ]


class CodeInputDeduction(DevTask):
    summary = "Deduce the Python function input that yields a target output value or condition."
    def __init__(self, config=None):
        super().__init__(config=config or CodeInputDeductionCfg())
        self._mode_i = 0
        self._recent_answers = []

    def generate(self):
        cfg = self.config
        modes = ("int", "tuple", "str")
        start = self._mode_i % len(modes)
        self._mode_i += 1
        for mode in modes[start:] + modes[:start]:
            for _ in range(max(1, cfg.max_attempts // len(modes))):
                if mode == "int":
                    domain = list(range(cfg.lo, cfg.hi + 1))
                    sig, call = (("int",), "int"), lambda x: [x]
                    goal, call_text, answer_hint = f"smallest integer x in [{cfg.lo}, {cfg.hi}]", "endpoint(x)", "Answer with the integer."
                    endpoint = f"def endpoint(x):\n    return f0(x) % {random.choice((3, 4, 5))}\n"
                elif mode == "tuple":
                    domain = [(x, y) for x in range(cfg.lo, cfg.hi + 1) for y in range(cfg.lo, cfg.hi + 1)]
                    sig, call = (("int", "int"), "int"), lambda xy: list(xy)
                    goal, call_text, answer_hint = f"lexicographically smallest integer pair (x, y) with each value in [{cfg.lo}, {cfg.hi}]", "endpoint(x, y)", "Answer as `x y`."
                    endpoint = f"def endpoint(x, y):\n    return f0(x, y) % {random.choice((3, 4, 5))}\n"
                else:
                    domain = bounded_strings(cfg.alphabet, cfg.max_len)
                    sig, call = (("int",), "int"), lambda s: [sum((len(cfg.alphabet) ** i) * cfg.alphabet.index(ch) for i, ch in enumerate(reversed(s)))]
                    goal, call_text, answer_hint = f"lexicographically smallest string s over `{cfg.alphabet}` with length 1..{cfg.max_len}", "endpoint(s)", "Answer with the string."
                    endpoint = f"def endpoint(s):\n    z = 0\n    for ch in s:\n        z = {len(cfg.alphabet)} * z + {repr(cfg.alphabet)}.index(ch)\n    return f0(z) % {random.choice((3, 4, 5))}\n"
                core = generate(
                    mesopy_grammar(
                        mode="function",
                        n_functions=max(1, int(cfg.n_functions)),
                        main_signature=sig,
                        max_number=max(4, int(8 + 2 * cfg.difficulty)),
                        max_params=len(sig[0]),
                        param_types=("int",),
                        return_types=("int",),
                        emit_endpoint=False,
                        emit_result=False,
                        failure_rate=0.05,
                        triviality_rate=0.25,
                        include_print=False,
                        include_assert=False,
                        include_try_except=False,
                    ),
                    depth=cfg.max_depth,
                    min_depth=cfg.min_depth,
                ) @ "py"
                code = f"{core}\n\n{endpoint}"
                call_args = [call(x) for x in domain]
                r = run_code(code, cfg, call_args=call_args, batch=True)
                reports = [
                    RunReport(True, value, None, args, r.stdout, r.stderr, r.steps, r.elapsed)
                    for args, value in zip(call_args, r.value or [])
                ] if r.ok else [r]
                buckets = {}
                for x, r in zip(domain, reports):
                    if r.ok and r.value is not None:
                        buckets.setdefault(r.value, []).append(x)
                if function_triviality(reports):
                    continue
                choices = [(y, min(xs)) for y, xs in buckets.items() if 1 < len(xs) < len(domain)]
                choices = [c for c in choices if c[1] != domain[0]] or choices
                if choices:
                    fresh = [c for c in choices if (" ".join(map(str, c[1])) if isinstance(c[1], tuple) else str(c[1])) not in self._recent_answers]
                    choices = fresh or choices
                    target, answer = random.choice(choices)
                    if isinstance(answer, tuple):
                        answer = " ".join(map(str, answer))
                    else:
                        answer = str(answer)
                    self._recent_answers = (self._recent_answers + [answer])[-8:]
                    return Problem(
                        edict(code=code, mode=mode, goal=goal, call_text=call_text, answer_hint=answer_hint, target=target),
                        answer,
                    )
        raise RuntimeError("failed to generate code input deduction task")

    def prompt(self, m):
        return (
            f"Find the {m.goal} such that `{m.call_text} == target`.\n"
            f"{m.answer_hint}\n\n"
            f"```python\n{m.code}\n```\n\n"
            f"Target: {m.target}"
        )

    def score_answer(self, answer, entry):
        reference = entry["answer"] if isinstance(entry, dict) else entry.answer
        return float(str(answer).strip().strip("\"'") == reference)

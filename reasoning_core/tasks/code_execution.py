import ast, io, re, sys, os, time, random, signal, inspect, contextlib, multiprocessing as mp
import copy
import threading
from typing import Optional
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


def _worker(send, code, magnitude, recursionlimit, max_steps, call_args=None, batch=False, exec_only=False):
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
            if exec_only:
                r = RunReport(True, None, None, None, out.getvalue(), err.getvalue(), steps, time.perf_counter() - t0)
            else:
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
                r = RunReport(True, values if args_list else values[0], None, args, out.getvalue(), err.getvalue(), steps, time.perf_counter() - t0)

    except StepLimit:
        sys.settrace(None)
        r = RunReport(False, None, "TimeoutError", locals().get("args"), out.getvalue(), err.getvalue(), steps, time.perf_counter() - t0)

    except Exception as e:
        sys.settrace(None)
        r = RunReport(False, None, type(e).__name__, locals().get("args"), out.getvalue(), err.getvalue(), steps, time.perf_counter() - t0)

    try:
        send.send(r)
    except Exception:
        pass
    send.close()


def run_code(code, cfg=None, timeout=None, recursionlimit=80, call_args=None, batch=False, exec_only=False):
    ctx = mp.get_context("fork")
    recv, send = ctx.Pipe(duplex=False)

    magnitude = cfg.magnitude if cfg else 0
    max_steps = cfg.max_steps if cfg else 10_000

    p = ctx.Process(target=_worker, args=(send, code, magnitude, recursionlimit, max_steps, call_args, batch, exec_only))
    p.start()
    send.close()

    if timeout is None:
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
                    goal = f"smallest integer x in [{cfg.lo}, {cfg.hi}]"
                    call_text = "endpoint(x)"
                    answer_hint = "Answer with the integer."
                    endpoint = f"def endpoint(x):\n    return f0(x) % {random.choice((3, 4, 5))}\n"
                elif mode == "tuple":
                    domain = [(x, y) for x in range(cfg.lo, cfg.hi + 1) for y in range(cfg.lo, cfg.hi + 1)]
                    sig, call = (("int", "int"), "int"), lambda xy: list(xy)
                    goal = f"lexicographically smallest integer pair (x, y) with each value in [{cfg.lo}, {cfg.hi}]"
                    call_text = "endpoint(x, y)"
                    answer_hint = "Answer as `x y`."
                    endpoint = f"def endpoint(x, y):\n    return f0(x, y) % {random.choice((3, 4, 5))}\n"
                else:
                    domain = bounded_strings(cfg.alphabet, cfg.max_len)
                    sig, call = (("int",), "int"), lambda s: [
                        sum((len(cfg.alphabet) ** i) * cfg.alphabet.index(ch) for i, ch in enumerate(reversed(s)))
                    ]
                    goal = f"lexicographically smallest string s over `{cfg.alphabet}` with length 1..{cfg.max_len}"
                    call_text = "endpoint(s)"
                    answer_hint = "Answer with the string."
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
                    fresh = [
                        c for c in choices
                        if (" ".join(map(str, c[1])) if isinstance(c[1], tuple) else str(c[1]))
                        not in self._recent_answers
                    ]
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


def _run_sandbox(code: str, timeout: float) -> Optional[str]:
    r = run_code(code, timeout=timeout, exec_only=True)
    if not r.ok:
        return None
    out = r.stdout.strip()
    return out if out else None


def _too_many_pass(code: str, threshold: float = 0.25) -> bool:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return True
    stmts = [n for n in ast.walk(tree) if isinstance(n, ast.stmt)]
    passes = [n for n in stmts if isinstance(n, ast.Pass)]
    return bool(stmts) and len(passes) / len(stmts) > threshold


def _line_count(code: str) -> int:
    return len(code.strip().splitlines())


def _get_called_functions(node: ast.AST) -> set[str]:
    calls: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            calls.add(n.func.id)
    return calls


def _safe_parse(code: str) -> Optional[ast.Module]:
    try:
        return ast.parse(code)
    except Exception:
        return None


def _func_defs(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def _prune_to_reachable(code: str) -> Optional[str]:
    tree = _safe_parse(code)
    if tree is None:
        return None
    func_defs = _func_defs(tree)
    exec_stmts = [n for n in tree.body if not isinstance(n, ast.FunctionDef)]
    reachable: set[str] = set()
    frontier: set[str] = set()
    for stmt in exec_stmts:
        frontier |= _get_called_functions(stmt)
    while frontier:
        name = frontier.pop()
        if name in reachable or name not in func_defs:
            continue
        reachable.add(name)
        frontier |= _get_called_functions(func_defs[name])
    tree.body = [n for n in tree.body if not isinstance(n, ast.FunctionDef) or n.name in reachable]
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except Exception:
        return None


def _call_chain_depth(code: str) -> int:
    tree = _safe_parse(code)
    if tree is None:
        return 0
    func_defs = _func_defs(tree)
    exec_stmts = [n for n in tree.body if not isinstance(n, ast.FunctionDef)]
    memo: dict[tuple[str, frozenset], int] = {}

    def _depth(name: str, visiting: frozenset) -> int:
        key = (name, visiting)
        if key in memo:
            return memo[key]
        if name not in func_defs or name in visiting:
            return 0
        called = _get_called_functions(func_defs[name]) & func_defs.keys()
        d = 1 + max((_depth(c, visiting | {name}) for c in called), default=0)
        memo[key] = d
        return d

    top_calls: set[str] = set()
    for stmt in exec_stmts:
        top_calls |= _get_called_functions(stmt)
    top_calls &= func_defs.keys()
    if not top_calls:
        return 0
    return max(_depth(c, frozenset()) for c in top_calls)


def _func_call_signature(code: str) -> str:
    tree = _safe_parse(code)
    if tree is None:
        return ""
    func_defs = _func_defs(tree)
    exec_stmts = [n for n in tree.body if not isinstance(n, ast.FunctionDef)]
    memo: dict[tuple[str, frozenset], str] = {}

    def sig(name: str, visiting: frozenset) -> str:
        key = (name, visiting)
        if key in memo:
            return memo[key]
        if name not in func_defs or name in visiting:
            return "leaf"
        called = sorted(_get_called_functions(func_defs[name]) & func_defs.keys())
        s = f"node({','.join(sig(c, visiting | {name}) for c in called)})" if called else "leaf"
        memo[key] = s
        return s

    top_calls = sorted(set().union(*[_get_called_functions(s) for s in exec_stmts]) & func_defs.keys())
    return f"root({','.join(sig(c, frozenset()) for c in top_calls)})"


class _ReturnWrapper(ast.NodeTransformer):
    def __init__(self, dead_fn_name: str, param_name: str):
        self.dead_fn_name = dead_fn_name
        self.param_name = param_name
        self.modified = False

    def visit_Return(self, node: ast.Return) -> ast.Return:
        if node.value is None:
            return node
        self.modified = True
        wrapped = ast.Return(
            value=ast.Call(
                func=ast.Name(id=self.dead_fn_name, ctx=ast.Load()),
                args=[],
                keywords=[ast.keyword(arg=self.param_name, value=node.value)],
            )
        )
        ast.fix_missing_locations(wrapped)
        return wrapped


def _try_entangle(p_correct: str, dead_funcs: list[ast.FunctionDef], rng: random.Random) -> Optional[tuple[str, str]]:
    tree = _safe_parse(p_correct)
    if tree is None:
        return None
    p_func_defs = _func_defs(tree)
    p_func_names = set(p_func_defs.keys())
    leaves = [fname for fname, fdef in p_func_defs.items() if not (_get_called_functions(fdef) & p_func_names)]
    if not leaves:
        return None

    def is_injectable(fdef: ast.FunctionDef) -> bool:
        if len(fdef.args.args) != 1:
            return False
        for node in ast.walk(fdef):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                callee = node.func.id
                if callee == "print":
                    return False
                if callee not in p_func_names and callee != fdef.name:
                    return False
        return True

    safe_dead = [f for f in dead_funcs if is_injectable(f)]
    if not safe_dead:
        return None
    leaf_candidates = list(leaves)
    rng.shuffle(leaf_candidates)
    rng.shuffle(safe_dead)

    for leaf_name in leaf_candidates:
        for dead_fn in safe_dead:
            try:
                leaf_def = copy.deepcopy(p_func_defs[leaf_name])
                dead_fn_copy = copy.deepcopy(dead_fn)
                param_name = dead_fn.args.args[0].arg
                wrapper = _ReturnWrapper(dead_fn.name, param_name)
                new_leaf = wrapper.visit(leaf_def)
                if not wrapper.modified:
                    continue
                new_body: list[ast.stmt] = []
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef) and node.name == leaf_name:
                        new_body.append(dead_fn_copy)
                        new_body.append(new_leaf)
                    else:
                        new_body.append(node)
                new_tree = ast.Module(body=new_body, type_ignores=[])
                ast.fix_missing_locations(new_tree)
                return ast.unparse(new_tree), dead_fn.name
            except Exception:
                continue
    return None


def _patch_ren_with_entangled(ren: list[str], entangled: str, original: str) -> list[str]:
    orig_tree = _safe_parse(original)
    ent_tree = _safe_parse(entangled)
    if orig_tree is None or ent_tree is None:
        return ren
    orig_funcs = {name: ast.unparse(fd) for name, fd in _func_defs(orig_tree).items()}
    ent_funcs = _func_defs(ent_tree)
    modified = {name: node for name, node in ent_funcs.items() if name in orig_funcs and ast.unparse(node) != orig_funcs[name]}
    if not modified:
        return ren
    new_ren: list[str] = []
    for prog in ren:
        try:
            tree = ast.parse(prog)
            new_body: list[ast.stmt] = []
            changed = False
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name in modified:
                    new_body.append(copy.deepcopy(modified[node.name]))
                    changed = True
                else:
                    new_body.append(node)
            if changed:
                tree.body = new_body
                ast.fix_missing_locations(tree)
                new_ren.append(ast.unparse(tree))
            else:
                new_ren.append(prog)
        except Exception:
            new_ren.append(prog)
    return new_ren


class _ConsolidationRegistry:
    def __init__(self) -> None:
        self._seen: set[tuple[str, int]] = set()

    def _key(self, p_correct: str) -> tuple[str, int]:
        return (_func_call_signature(p_correct), _call_chain_depth(p_correct))

    def is_duplicate(self, p_correct: str) -> bool:
        return self._key(p_correct) in self._seen

    def register(self, p_correct: str) -> None:
        self._seen.add(self._key(p_correct))

    def reset(self) -> None:
        self._seen.clear()


def _inline_result_print(code: str) -> Optional[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    new_body = []
    i = 0
    while i < len(tree.body):
        s = tree.body[i]
        n = tree.body[i + 1] if i + 1 < len(tree.body) else None
        if (
            isinstance(s, ast.Assign)
            and len(s.targets) == 1
            and isinstance(s.targets[0], ast.Name)
            and s.targets[0].id == "_result"
            and n
            and isinstance(n, ast.Expr)
            and isinstance(n.value, ast.Call)
            and isinstance(n.value.func, ast.Name)
            and n.value.func.id == "print"
            and len(n.value.args) == 1
            and isinstance(n.value.args[0], ast.Name)
            and n.value.args[0].id == "_result"
        ):
            new_body.append(ast.Expr(ast.Call(func=ast.Name("print", ast.Load()), args=[s.value], keywords=[])))
            i += 2
        else:
            new_body.append(s)
            i += 1
    tree.body = new_body
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except Exception:
        return None


def _collect_func_names(code: str) -> list[str]:
    tree = _safe_parse(code)
    return list(_func_defs(tree)) if tree else []


def _apply_name_map(code: str, name_map: dict[str, str]) -> Optional[str]:
    tree = _safe_parse(code)
    if tree is None:
        return None

    class R(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.name = name_map.get(node.name, node.name)
            self.generic_visit(node)
            return node

        def visit_Call(self, node):
            self.generic_visit(node)
            if isinstance(node.func, ast.Name):
                node.func.id = name_map.get(node.func.id, node.func.id)
            return node

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Load):
                node.id = name_map.get(node.id, node.id)
            return node

    tree = R().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except Exception:
        return None


def rename_all(progs: list[str], rng: random.Random) -> Optional[list[str]]:
    names = [_collect_func_names(p) for p in progs]
    total = sum(len(n) for n in names)
    if total == 0:
        return None
    pool = rng.sample(range(1000, 9999), min(total * 4, 8999))
    rng.shuffle(pool)
    it = iter(pool)
    out = []
    for p, ns in zip(progs, names):
        m: dict[str, str] = {}
        try:
            for old in ns:
                m[old] = f"g{next(it)}"
        except StopIteration:
            return None
        r = _apply_name_map(p, m)
        if r is None:
            return None
        out.append(r)
    return out


def merge(progs: list[str], rng: random.Random) -> Optional[str]:
    try:
        trees = [ast.parse(p) for p in progs]
    except Exception:
        return None
    defs = []
    execs = []
    for t in trees:
        defs.extend(n for n in t.body if isinstance(n, ast.FunctionDef))
        execs.append([n for n in t.body if not isinstance(n, ast.FunctionDef)])
    rng.shuffle(defs)
    order = list(range(len(progs)))
    rng.shuffle(order)
    mx = max((len(e) for e in execs), default=0)
    body: list[ast.stmt] = []
    for i in range(mx):
        for idx in order:
            if i < len(execs[idx]):
                body.append(execs[idx][i])
    mod = ast.Module(body=defs + body, type_ignores=[])
    ast.fix_missing_locations(mod)
    try:
        return ast.unparse(mod)
    except Exception:
        return None


def _normalise(code: str) -> Optional[str]:
    try:
        tree = ast.parse(code)
    except Exception:
        return None
    fdefs = sorted((n for n in tree.body if isinstance(n, ast.FunctionDef)), key=lambda n: n.name)
    other = [n for n in tree.body if not isinstance(n, ast.FunctionDef)]
    tree.body = fdefs + other
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except Exception:
        return None


@dataclass
class ConsolidationConfig(Config):
    timeout: float = 3.0
    n_programs: int = 3

    depth_range: tuple = (6, 18)
    # FIX 1: was ((0, 5),) — extra parens made it a 1-tuple of a tuple
    n_classes_range: tuple = (0, 5)
    inherit_rate_range: tuple = (0.5, 0.85)
    n_functions_range: tuple = (3, 8)
    min_body_stmts_range: tuple = (3, 8)
    failure_rate_range: tuple = (0.0, 0.15)
    usage_bias_range: tuple = (0.2, 0.6)
    include_comprehensions: bool = True
    include_fstrings: bool = True
    include_ternary: bool = True
    include_break_continue: bool = True
    include_try_except: bool = True
    include_classes: bool = False

    min_call_depth: int = 2
    entangle: bool = True
    deduplicate: bool = True
    max_attempts: int = 1000

    def update(self, c: int) -> None:
        def shift(t, d):
            return (max(t[0] + d, 1), t[1] + d)

        self.n_functions_range = shift(self.n_functions_range, c)
        self.min_body_stmts_range = shift(self.min_body_stmts_range, c)
        self.depth_range = shift(self.depth_range, c)
        self.failure_rate_range = (
            max(self.failure_rate_range[0], 0.0),
            min(self.failure_rate_range[1] + 0.05 * c, 0.5),
        )
        self.usage_bias_range = (
            max(self.usage_bias_range[0] - 0.02 * c, 0.0),
            min(self.usage_bias_range[1] + 0.02 * c, 1.0),
        )
        self.max_attempts = max(int(self.max_attempts * (1 + 0.05 * c)), 200)
        self.min_call_depth = min(self.min_call_depth + c, 4)


class Consolidation(Task):
    task_name = "code_consolidation"
    balancing_key_ratio = 1.0
    _seed_counter = 0
    _seed_lock = threading.Lock()

    def __init__(self, config=None):
        super().__init__(config=config or ConsolidationConfig())
        self._registry = _ConsolidationRegistry()

    def _next_seed(self) -> int:
        with self._seed_lock:
            Consolidation._seed_counter += 1
            return (os.getpid() << 32) + Consolidation._seed_counter

    @classmethod
    def reset_pools(cls) -> None:
        pass

    def reset_registry(self) -> None:
        self._registry.reset()

    # FIX 2: added mode, n_classes, inherit_rate, emit_endpoint, emit_result, print_result
    def _sample_kwargs(self, rng: random.Random) -> dict:
        c = self.config
        return dict(
            mode="function",
            n_functions=rng.randint(*c.n_functions_range),
            min_body_stmts=rng.randint(*c.min_body_stmts_range),
            include_comprehensions=c.include_comprehensions,
            include_fstrings=c.include_fstrings,
            include_ternary=c.include_ternary,
            include_break_continue=c.include_break_continue,
            include_try_except=c.include_try_except,
            include_classes=c.include_classes,
            n_classes=rng.randint(*c.n_classes_range) if c.include_classes else 1,
            inherit_rate=rng.uniform(*c.inherit_rate_range),
            failure_rate=rng.uniform(*c.failure_rate_range),
            usage_bias=rng.uniform(*c.usage_bias_range),
            triviality_rate=0.0,
            emit_endpoint=True,
            emit_result=True,
            print_result=True,
        )

    # FIX 3: was pygram_grammar (undefined) — replaced with mesopy_grammar (already imported)
    def _generate_one(self, rng: random.Random) -> Optional[str]:
        c = self.config
        d = rng.randint(*c.depth_range)
        try:
            kwargs = self._sample_kwargs(rng)
            g = mesopy_grammar(**kwargs)
            code = generate(g, depth=d, min_depth=max(d - 3, 3), seed=rng.randint(0, 2 ** 31)) @ "py"
        except Exception:
            return None
        if _too_many_pass(code):
            return None
        return code

    def generate(self) -> Problem:
        cfg = self.config

        for _ in range(cfg.max_attempts):
            rng = random.Random(self._next_seed())

            raw = [self._generate_one(random.Random(self._next_seed())) for _ in range(cfg.n_programs)]
            if any(p is None for p in raw):
                continue

            inl = [_inline_result_print(p) for p in raw]
            if any(p is None for p in inl):
                continue

            ren = rename_all(inl, rng)
            if ren is None:
                continue

            runnable_raw: list[tuple[str, str]] = []
            for p in ren:
                r = run_code(p, timeout=cfg.timeout, exec_only=True)
                runnable_raw.append((p, r.stdout.strip() if r.ok else None))
            runnable_raw = [(p, o) for p, o in runnable_raw if o is not None]
            if len(runnable_raw) < 2:
                continue

            runnable: list[tuple[str, str]] = []
            for p_raw, expected_out in runnable_raw:
                pruned = _prune_to_reachable(p_raw)
                if pruned is None:
                    continue
                r_pruned = run_code(pruned, timeout=cfg.timeout, exec_only=True)
                if (r_pruned.stdout.strip() if r_pruned.ok else None) != expected_out:
                    continue
                runnable.append((pruned, expected_out))

            if len(runnable) < 2:
                continue

            min_d = cfg.min_call_depth
            deep_runnable = [(p, o) for p, o in runnable if _call_chain_depth(p) >= min_d]
            if not deep_runnable:
                continue

            p_correct, out = min(deep_runnable, key=lambda x: _line_count(x[0]))
            others_out = {o for p, o in runnable if p != p_correct}
            if out in others_out:
                continue

            entangled_flag = False
            p_correct_before_entangle = p_correct
            if cfg.entangle:
                p_correct_funcs = set(_func_defs(ast.parse(p_correct)))
                dead_funcs: list[ast.FunctionDef] = []
                for p in ren:
                    tree = _safe_parse(p)
                    if tree is None:
                        continue
                    for node in tree.body:
                        if isinstance(node, ast.FunctionDef) and node.name not in p_correct_funcs:
                            dead_funcs.append(node)

                entangle_result = _try_entangle(p_correct, dead_funcs, rng)
                if entangle_result is not None:
                    entangled_code, shared_fn = entangle_result
                    r_new = run_code(entangled_code, timeout=cfg.timeout, exec_only=True)
                    new_out = r_new.stdout.strip() if r_new.ok else None
                    if new_out is not None and new_out not in others_out:
                        p_correct = entangled_code
                        out = new_out
                        entangled_flag = True
                        ren = _patch_ren_with_entangled(ren, p_correct, p_correct_before_entangle)

            if cfg.deduplicate and self._registry.is_duplicate(p_correct):
                continue

            merged = merge(ren, rng)
            if merged is None or not run_code(merged, timeout=cfg.timeout, exec_only=True).ok:
                continue

            if entangled_flag:
                p_correct_funcs_final = set(_func_defs(ast.parse(p_correct)))
                merged_funcs = set(_func_defs(ast.parse(merged)))
                if not p_correct_funcs_final.issubset(merged_funcs):
                    continue

            if cfg.deduplicate:
                self._registry.register(p_correct)

            meta = edict(
                merged_code=merged,
                correct_code=p_correct,
                correct_stdout=out,
                n_programs=cfg.n_programs,
                n_runnable=len(runnable),
                call_depth=_call_chain_depth(p_correct),
                entangled=entangled_flag,
                call_graph_signature=_func_call_signature(p_correct),
            )
            return Problem(metadata=meta, answer=p_correct)

        raise RuntimeError(f"Consolidation: failed after {cfg.max_attempts} attempts")

    def prompt(self, m) -> str:
        depth_hint = f"The correct program has a call chain of depth {m.call_depth} (functions calling other functions)."
        entangle_hint = (
            "\nNote: some functions in the dead code are also called by the "
            "correct program — you must trace the full call graph to know what to keep."
            if m.get("entangled") else ""
        )
        return (
            "You are given a Python program P created by merging several independent programs.\n\n"
            f"Program P:\n```python\n{m.merged_code}\n```\n\n"
            "Each original program defined its own functions, then called them to produce output. "
            "Their definitions were collected, renamed to neutral tokens (g1234…), shuffled, and "
            "all executable statements interleaved.\n\n"
            "Exactly ONE program produces this output on its own:\n\n"
            f"```\n{m.correct_stdout}\n```\n\n"
            f"{depth_hint}{entangle_hint}\n\n"
            "Extract the MINIMAL program. Remove ALL dead code.\n"
            "RULES (any violation = failure):\n"
            "1. NEVER rename any function, class, method, or variable.\n"
            "2. Do NOT modify the body of any function you keep.\n"
            "3. Do NOT add new code.\n"
            "4. Your cleaned program must print EXACTLY the output above.\n"
            "5. It must contain ONLY what is needed — trace the full call \n"
            "graph from the exec statement(s) to find every required function.\n\n"
            "Return ONLY the cleaned Python program, no explanation."
        )

    # FIX 4: handle both dict and Problem object for metadata and answer access
    def score_answer(self, a, entry) -> int:
        if a is None:
            return 0
        m = entry["metadata"] if isinstance(entry, dict) else entry.metadata
        out = m.correct_stdout
        t = self.config.timeout
        r = run_code(a, timeout=t, exec_only=True)
        g1 = (r.stdout.strip() if r.ok else None) == out
        ref_answer = entry["answer"] if isinstance(entry, dict) else entry.answer
        g2 = _normalise(a) == _normalise(ref_answer)
        return 1 if g1 and g2 else 0

    def balancing_key(self, p) -> str:
        return str(p.metadata.n_programs)
import io, re, sys, os, time, random, signal, inspect, contextlib, multiprocessing as mp
from dataclasses import dataclass
from difflib import SequenceMatcher

from reasoning_core.template import Task, Problem, Config, edict
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

    def update(self, c):
        self.difficulty += c
        self.min_depth += c / 2
        self.max_depth += int(c)
        self.n_functions += c / 2
        self.magnitude += c / 2
        self.min_steps += int(2 * c)


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


def _worker(send, code, magnitude, recursionlimit, max_steps):
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
            args = endpoint_args(ns["endpoint"], magnitude)
            sys.settrace(trace)
            try:
                value = ns["endpoint"](*args)
            finally:
                sys.settrace(None)

        r = RunReport(
            True,
            repr(value)[:500],
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


def run_code(code, cfg, recursionlimit=80):
    ctx = mp.get_context("fork")
    recv, send = ctx.Pipe(duplex=False)
    p = ctx.Process(target=_worker, args=(send, code, cfg.magnitude, recursionlimit, cfg.max_steps))
    p.start()
    send.close()

    try:
        if recv.poll(cfg.timeout):
            r = recv.recv()
            p.join(0.05)
            kill(p)
            return r

        kill(p)
        return RunReport(error="TimeoutError", elapsed=cfg.timeout)

    except KeyboardInterrupt:
        kill(p)
        raise

    finally:
        recv.close()


def make_code(cfg, failure_rate):
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
    )
    return generate(g, depth=cfg.max_depth, min_depth=cfg.min_depth) @ "py"


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


def sample_problem(cfg, want_error, failure_rate):
    for _ in range(cfg.max_attempts):
        code = make_code(cfg, failure_rate)
        if "def endpoint" not in code:
            continue

        r = run_code(code, cfg)

        if want_error:
            if r.error and r.args is not None and r.error != "TimeoutError":
                return code, r

        elif r.ok and r.value is not None and len(r.value) <= cfg.max_answer_len:
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
    def __init__(self, config=None):
        super().__init__(config=config or MesopyCodeCfg())
        self.balancing_key_ratio = 1 / 5

    def generate(self):
        want_error = random.random() >= self.config.runnable_prob
        code, r = sample_problem(
            self.config,
            want_error=want_error,
            failure_rate=0.65 if want_error else 0.05,
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

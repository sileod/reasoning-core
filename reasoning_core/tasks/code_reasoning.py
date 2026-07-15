"""
Two Mesopy-based reasoning tasks, self-contained (no imports from the
mesopy_code module — the small runtime it needs is duplicated below).

1. TemporalReasoning
   A single Mesopy function f0 is wired into a stateful driver:

       STATE = x0
       def endpoint():
           global STATE
           STATE = f0(STATE)
           return STATE

   `endpoint()` is invoked N times in a row inside the same sandboxed
   process (so STATE really accumulates across calls), where N is drawn
   uniformly from [min_calls, max_calls]. The model is shown the code,
   the starting value, and the value STATE holds after the (hidden)
   N-th call, and must recover N. To keep the task well posed we only
   accept an N whose resulting value is unique across the whole
   1..max_calls trajectory.

2. PathConvergence
   Four independently generated int-returning Mesopy programs are run
   once each. By construction exactly one of the four results has the
   minority parity (3 odd + 1 even, or 3 even + 1 odd — chosen 50/50).
   The model must say which of the four programs (1-4) produced the
   minority-parity value.
"""

import io
import os
import re
import random
import signal
import inspect
import contextlib
import multiprocessing as mp
from dataclasses import dataclass

from reasoning_core.template import Task, Entry, Config, edict, stochastic_rounding as sround
from gramforge import generate
from gramforge.grammars import mesopy_grammar


# --------------------------------------------------------------------------
# Sandboxed execution runtime (trimmed duplicate of the one in mesopy_code.py)
# --------------------------------------------------------------------------

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


def _extract_int(s):
    m = re.search(r"-?\d+", str(s))
    return int(m.group()) if m else None


def kill(p):
    if p.is_alive():
        p.terminate()
        p.join(0.05)
        if p.is_alive():
            os.kill(p.pid, signal.SIGKILL)
            p.join()


def _worker(send, code, magnitude, recursionlimit, max_steps, call_args=None, batch=False, reports=False):
    out, err = CapIO(), CapIO()
    ns = {"__builtins__": __builtins__}
    steps, t0 = 0, __import__("time").perf_counter()
    __import__("sys").setrecursionlimit(recursionlimit)

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

    import sys
    import time

    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            exec(compile(code, "<mesopy>", "exec"), ns, ns)
            args = call_args if call_args is not None else endpoint_args(ns["endpoint"], magnitude)
            args_list = args if batch else None
            values = []
            for a in args_list or [args]:
                steps = 0
                if not reports:
                    sys.settrace(trace)
                try:
                    value = repr(ns["endpoint"](*a))[:500]
                    values.append(RunReport(ok=True, value=value, args=a) if reports else value)
                except StepLimit:
                    if not reports:
                        raise
                    values.append(RunReport(error="TimeoutError", args=a, steps=steps))
                except Exception as e:
                    if not reports:
                        raise
                    values.append(RunReport(error=type(e).__name__, args=a, steps=steps))
                finally:
                    sys.settrace(None)

        r = values if reports else RunReport(
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
        r = RunReport(False, None, "TimeoutError", locals().get("args"), out.getvalue(), err.getvalue(), steps, time.perf_counter() - t0)

    except Exception as e:
        sys.settrace(None)
        r = RunReport(False, None, type(e).__name__, locals().get("args"), out.getvalue(), err.getvalue(), steps, time.perf_counter() - t0)

    try:
        send.send(r)
    except Exception:
        pass
    send.close()


def run_code(code, cfg, recursionlimit=80, call_args=None, batch=False, reports=False):
    ctx = mp.get_context("fork")
    recv, send = ctx.Pipe(duplex=False)
    p = ctx.Process(target=_worker, args=(send, code, cfg.magnitude, recursionlimit, cfg.max_steps, call_args, batch, reports))
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
        return [] if reports else RunReport(error="TimeoutError", args=call_args, elapsed=timeout)

    except KeyboardInterrupt:
        kill(p)
        raise

    finally:
        recv.close()


# --------------------------------------------------------------------------
# Configs
# --------------------------------------------------------------------------

@dataclass
class BaseCodeCfg(Config):
    difficulty: float = 0.0
    min_depth: int = 4
    max_depth: int = 15
    max_attempts: int = 150
    timeout: float = 0.5
    magnitude: int = 3
    n_functions: int = 1
    max_steps: int = 10_000

    def apply_difficulty(self, level):
        self.difficulty += level
        self.min_depth = sround(self.min_depth + 0.5 * level)
        self.max_depth = sround(self.max_depth + level)
        self.n_functions = sround(self.n_functions + 0.5 * level)
        self.magnitude = sround(self.magnitude + 0.5 * level)


@dataclass
class TemporalCodeCfg(BaseCodeCfg):
    min_calls: int = 1
    max_calls: int = 100
    lo: int = -5
    hi: int = 5
    max_answer_len: int = 40

    def apply_difficulty(self, level):
        super().apply_difficulty(level)
        self.lo = sround(self.lo - level)
        self.hi = sround(self.hi + level)


@dataclass
class PathConvergenceCfg(BaseCodeCfg):
    n_functions: int = 2
    max_params: int = 2


# --------------------------------------------------------------------------
# Task 1: Temporal Reasoning
# --------------------------------------------------------------------------

class TemporalReasoning(Task):
    summary = "Predict how many times a stateful function was invoked to reach a recorded value."

    def __init__(self, config=None):
        super().__init__(config=config or TemporalCodeCfg())

    def _make_driver(self, cfg):
        core = generate(
            mesopy_grammar(
                mode="function",
                n_functions=max(1, int(cfg.n_functions)),
                main_signature=(("int",), "int"),
                max_number=max(4, int(8 + 2 * cfg.difficulty)),
                max_params=1,
                param_types=("int",),
                return_types=("int",),
                emit_endpoint=False,
                emit_result=False,
                failure_rate=0.0,
                triviality_rate=0.2,
                include_print=False,
                include_assert=False,
                include_try_except=False,
            ),
            depth=cfg.max_depth,
            min_depth=cfg.min_depth,
        ) @ "py"
        x0 = random.randint(cfg.lo, cfg.hi)
        code = f"{core}\nSTATE = {x0}\n\ndef endpoint():\n    global STATE\n    STATE = f0(STATE)\n    return STATE\n"
        return code, x0

    def generate_entry(self):
        cfg = self.config
        for _ in range(cfg.max_attempts):
            code, x0 = self._make_driver(cfg)
            n_max = cfg.max_calls
            reports = run_code(code, cfg, call_args=[[]] * n_max, batch=True, reports=True)

            if len(reports) < n_max or any(not r.ok for r in reports):
                continue

            values = [r.value for r in reports]
            if len(set(values)) < 0.9 * n_max:
                continue  # too repetitive (near-constant / short cycle) to be well posed

            candidates = [n for n in range(cfg.min_calls, n_max + 1) if values.count(values[n - 1]) == 1]
            if not candidates:
                continue

            n = random.choice(candidates)
            final_value = values[n - 1]
            if len(final_value) > cfg.max_answer_len:
                continue

            return Entry(edict(code=code, x0=x0, final_value=final_value, max_calls=n_max), str(n))

        raise RuntimeError("Failed to generate temporal reasoning task")

    def render_prompt(self, m):
        return (
            "The `endpoint()` function below takes no arguments and is called repeatedly. "
            f"Each call updates the global `STATE` (which starts at {m.x0}) via `STATE = f0(STATE)` "
            "and returns the new value.\n"
            f"```python\n{m.code}\n```\n"
            f"After being called some number of times between 1 and {m.max_calls}, "
            f"`STATE` equals `{m.final_value}`.\n"
            "How many times was `endpoint()` called? Answer with a single integer."
        )

    def score_answer(self, answer, entry):
        reference = entry["answer"] if isinstance(entry, dict) else entry.answer
        got = _extract_int(answer)
        return float(got is not None and got == int(reference))


# --------------------------------------------------------------------------
# Task 2: Path Convergence
# --------------------------------------------------------------------------

class PathConvergence(Task):
    summary = "Identify which of four generated programs returns the value with minority parity."

    def __init__(self, config=None):
        super().__init__(config=config or PathConvergenceCfg())

    def _make_candidate(self, cfg):
        g = mesopy_grammar(
            mode="function",
            n_functions=max(1, int(cfg.n_functions)),
            max_number=max(4, int(8 + 2 * cfg.difficulty)),
            max_params=max(1, int(cfg.max_params)),
            param_types=("int", "str", "list"),
            return_types=("int",),
            emit_endpoint=True,
            emit_result=False,
            failure_rate=0.0,
            triviality_rate=max(0.05, 0.5 - 0.05 * cfg.difficulty),
        )
        return generate(g, depth=cfg.max_depth, min_depth=cfg.min_depth) @ "py"

    def generate_entry(self):
        cfg = self.config
        target_parity = random.choice(("even", "odd"))
        want_minority = 0 if target_parity == "even" else 1
        minority, majority = [], []

        for _ in range(cfg.max_attempts):
            if len(minority) >= 1 and len(majority) >= 3:
                break

            code = self._make_candidate(cfg)
            if "def endpoint" not in code:
                continue

            r = run_code(code, cfg)
            if not (r.ok and r.value is not None):
                continue

            value = _extract_int(r.value)
            if value is None:
                continue

            if value % 2 == want_minority:
                if len(minority) < 1:
                    minority.append((code, r))
            else:
                if len(majority) < 3:
                    majority.append((code, r))

        if len(minority) < 1 or len(majority) < 3:
            raise RuntimeError("Failed to generate path convergence task")

        tagged = [(True, code, r) for code, r in minority] + [(False, code, r) for code, r in majority]
        random.shuffle(tagged)
        answer_index = next(i for i, (is_min, _, _) in enumerate(tagged) if is_min) + 1
        entries = [edict(code=code, call=call_src(r.args), value=r.value) for _, code, r in tagged]

        return Entry(edict(entries=entries, target_parity=target_parity), str(answer_index))

    def render_prompt(self, m):
        blocks = "\n\n".join(
            f"Program {i + 1}:\n```python\n{e.code}\n```\nCall: `{e.call}`"
            for i, e in enumerate(m.entries)
        )
        return (
            f"{blocks}\n\n"
            f"Exactly one of these four programs returns a value with {m.target_parity} parity; "
            "the other three share the opposite parity.\n"
            f"Which program (1-4) returns the {m.target_parity} value? Answer with a single number."
        )

    def score_answer(self, answer, entry):
        reference = entry["answer"] if isinstance(entry, dict) else entry.answer
        got = _extract_int(answer)
        return float(got is not None and got == int(reference))

    def balancing_key(self, problem):
        return problem.metadata.target_parity
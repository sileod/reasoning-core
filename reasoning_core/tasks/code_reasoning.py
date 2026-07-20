"""
Three self-contained reasoning tasks (no imports from the mesopy_code
module — the small sandboxed-execution runtime it needs is duplicated
below).

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

3. TypeInhabitation
   Given a typed toolkit of functions scraped from real installed
   libraries, plus a handful of typed leaf variables, compose a call
   expression of an exact depth that evaluates to a target type.
   Validity is checked structurally (no eval/exec/subprocess): the model
   is free to submit any well-typed composition, not just the one used
   to build the problem. Function names are masked as f0, f1, ... so an
   answer can't be produced from prior knowledge of the real library API.
   The scraping step is part of this task, not an external prerequisite:
   the first time `cfg.db_path` doesn't exist (or has no `functions`
   table), it's built automatically by introspecting `cfg.libraries`.
"""

import io
import os
import re
import sys
import time
import random
import signal
import sqlite3
import pkgutil
import inspect
import importlib
import contextlib
import multiprocessing as mp
from collections import defaultdict
from dataclasses import dataclass
from itertools import product
from typing import get_type_hints

from reasoning_core.template import Task, DevTask, Entry, Config, edict, stochastic_rounding as sround
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
            try:
                r = recv.recv()
            except EOFError:
                kill(p)
                return [] if reports else RunReport(error="ProcessKilled", args=call_args, elapsed=timeout)
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


@dataclass
class TypeInhabitationCfg(Config):
    difficulty: float = 0.0
    depth: int = 2
    n_funcs: int = 8
    max_attempts: int = 400
    db_path: str = "functions.db"
    libraries: tuple[str, ...] | None = None  # None -> DEFAULT_LIBRARIES

    def apply_difficulty(self, level):
        self.difficulty += level
        self.depth = max(1, sround(self.depth + 0.5 * level))
        self.n_funcs = max(4, sround(self.n_funcs + level))


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


# --------------------------------------------------------------------------
# Type-inhabitation toolkit (function DB + structural type checker)
# --------------------------------------------------------------------------

@dataclass
class FunctionRecord:
    name: str
    inputs: list      # list[tuple[str, str]]  (param_name, type_str)
    output: str


_SIMPLE_TYPE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
_BAD_TYPES = {"None", "NoneType", "Any", "object"}
_SPLIT_ARG = re.compile(r",\s*(?=[A-Za-z_][A-Za-z0-9_]*\s*:)")

_func_cache: dict[str, list[FunctionRecord]] = {}

# Libraries the scraper introspects when cfg.db_path doesn't exist yet.
# (Two names doc3 had wrong: the PyYAML import is "yaml", not "pyyaml";
# the shapely package is "shapely", not "shapelys".)
DEFAULT_LIBRARIES = (
    "sklearn", "pandas", "scipy", "jax", "numpy", "seaborn", "statsmodels",
    "tensorflow", "torch", "sympy", "xgboost", "cv2", "PIL", "nltk",
    "joblib", "requests", "flask", "yaml", "skimage", "pytorch_lightning",
    "transformers", "datasets", "networkx", "shapely",
)

_SCAN_SKIP_SUBSTRINGS = (
    ".tests", ".test_", "conftest", "._", "internals", "compat",
    "testing", "util", "utils", "private", "_libs",
)
_BAD_NAME_KEYWORDS = ("test", "compat", "deprecated", "deprecate")


def _is_clean_type(t):
    """A type is usable if it's a bare identifier, or a `|`-separated union of them."""
    parts = [p.strip() for p in t.split("|")]
    return bool(parts) and all(_SIMPLE_TYPE.match(p) and p not in _BAD_TYPES for p in parts)


def _parse_inputs(inputs):
    if not inputs.strip():
        return []
    parts = []
    for chunk in _SPLIT_ARG.split(inputs):
        name, _, typ = chunk.partition(":")
        parts.append((name.strip(), typ.strip()))
    return parts


def _format_type(t):
    try:
        return t.__name__
    except AttributeError:
        return str(t)


def _extract_signature(func):
    """Return (inputs_str, output_str), or None if any parameter/return is unannotated."""
    try:
        hints = get_type_hints(func)
        signature = inspect.signature(func)
    except Exception:
        return None

    inputs = []
    for name in signature.parameters:
        if name not in hints:
            return None
        inputs.append(f"{name}: {_format_type(hints[name])}")

    if "return" not in hints:
        return None
    return ", ".join(inputs), _format_type(hints["return"])


def _is_bad_function_name(name, module_name):
    full = f"{module_name}.{name}".lower()
    return any(k in full for k in _BAD_NAME_KEYWORDS)


def _scan_library(library_name, conn, visited_modules):
    """Introspect one top-level library, inserting every cleanly-typed, documented
    function it exposes into the `functions` table. Mirrors build_function_db.py."""
    try:
        package = importlib.import_module(library_name)
    except Exception:
        return 0
    if not hasattr(package, "__path__"):
        return 0

    cur = conn.cursor()
    inserted, seen = 0, set()

    for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        if any(s in module_name for s in _SCAN_SKIP_SUBSTRINGS):
            continue
        if not module_name.startswith(library_name):
            continue
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        if module in visited_modules:
            continue
        visited_modules.add(module)

        try:
            functions = inspect.getmembers(module, inspect.isfunction)
        except Exception:
            continue

        for name, func in functions:
            if name.startswith("_") or _is_bad_function_name(name, module_name):
                continue
            result = _extract_signature(func)
            if result is None:
                continue
            inputs, output = result
            if not inputs.strip():
                continue
            doc = inspect.getdoc(func)
            if not doc or len(doc.split()) < 20:
                continue
            key = (name, inputs, output)
            if key in seen:
                continue
            seen.add(key)
            cur.execute(
                "INSERT OR IGNORE INTO functions "
                "(library, module, function_name, inputs, outputs) VALUES (?, ?, ?, ?, ?)",
                (library_name, module_name, name, inputs, output),
            )
            inserted += 1

    conn.commit()
    return inserted


def _db_ready(db_path):
    """Whether db_path already has a usable `functions` table."""
    if not os.path.exists(db_path):
        return False
    try:
        conn = sqlite3.connect(db_path)
        try:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='functions'"
            ).fetchone()
            return row is not None
        finally:
            conn.close()
    except sqlite3.Error:
        return False


def build_function_db(db_path, libraries=DEFAULT_LIBRARIES):
    """Scan `libraries` and (re)build the `functions` table at db_path. Exposed as a
    public function so it can also be run standalone (see __main__ below) to
    pre-populate the cache instead of paying the scan cost on the first generate_entry().

    Importing/introspecting third-party packages (transformers, nltk, torch, ...) can
    print their own warnings and debug diagnostics; those are suppressed here since
    they come from the scanned libraries, not from this scan itself."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS functions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library TEXT,
            module TEXT,
            function_name TEXT,
            inputs TEXT,
            outputs TEXT
        )
    """)
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_func
        ON functions(module, function_name, inputs, outputs)
    """)
    conn.commit()

    visited_modules, total = set(), 0
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        for lib in libraries:
            total += _scan_library(lib, conn, visited_modules)
    conn.close()
    return total


def _load_functions(db_path, libraries=None):
    """Read + filter functions.db once per path, keeping only cleanly-typed signatures.
    Builds the DB by scraping `libraries` (default DEFAULT_LIBRARIES) the first time
    db_path doesn't exist yet -- scraping is part of this task, not a separate step."""
    if db_path not in _func_cache:
        if not _db_ready(db_path):
            build_function_db(db_path, libraries or DEFAULT_LIBRARIES)

        conn = sqlite3.connect(db_path)
        try:
            rows = conn.execute("SELECT function_name, inputs, outputs FROM functions").fetchall()
        finally:
            conn.close()

        clean, seen = [], set()
        for name, inputs, output in rows:
            output = output.strip()
            record_inputs = _parse_inputs(inputs)
            if not record_inputs or not _is_clean_type(output):
                continue
            if not all(_is_clean_type(t) for _, t in record_inputs):
                continue
            key = (name, tuple(record_inputs), output)
            if key in seen:
                continue
            seen.add(key)
            clean.append(FunctionRecord(name, record_inputs, output))
        _func_cache[db_path] = clean
    return _func_cache[db_path]


def _select_toolkit(funcs, target_type, n_funcs):
    """Pick a small connected set of functions around a target type, plus the
    leaf variables needed to feed them."""
    by_output = defaultdict(list)
    for f in funcs:
        by_output[f.output].append(f)
    if len(by_output.get(target_type, [])) < 2:
        return [], {}

    selected, seen = [], set()
    for f in random.sample(by_output[target_type], 2):
        selected.append(f)
        seen.add(f.name)

    needed = {t for f in selected for _, t in f.inputs} - {target_type}
    for t in needed:
        producers = by_output.get(t, [])
        if producers and len(selected) < n_funcs:
            f = random.choice(producers)
            if f.name not in seen:
                selected.append(f)
                seen.add(f.name)

    produced = {f.output for f in selected}
    filler = [f for f in funcs if f.name not in seen and f.output not in produced]
    random.shuffle(filler)
    for f in filler:
        if len(selected) >= n_funcs:
            break
        selected.append(f)
        seen.add(f.name)
        produced.add(f.output)

    leaf_types = {t for f in selected for _, t in f.inputs if t not in produced}
    var_types, counts = {}, defaultdict(int)
    for t in sorted(leaf_types):
        prefix = re.sub(r"\W", "", t.split(".")[-1].split("|")[0])[:3].lower() or "v"
        for _ in range(2 if random.random() < 0.4 else 1):
            name = f"{prefix}_{counts[t]}"
            counts[t] += 1
            var_types[name] = t
    return selected, var_types


def _split_top_level_commas(s):
    parts, depth, buf = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return [p for p in parts if p]


def _types_compatible(actual, expected):
    if actual == expected:
        return True
    if "|" in expected:
        return any(_types_compatible(actual, p.strip()) for p in expected.split("|"))
    if "|" in actual:
        return any(_types_compatible(p.strip(), expected) for p in actual.split("|"))
    return False


def _type_check_expr(expr, func_lookup, var_types):
    """Returns (is_valid, inferred_type, explanation) without ever eval'ing expr.
    Only understands `name(k=v, ...)` calls chained through keyword arguments."""
    expr = expr.strip()
    if expr in var_types:
        return True, var_types[expr], f"`{expr}` is a known variable"

    paren = expr.find("(")
    if paren == -1:
        return False, "?", f"Unknown token `{expr}`"

    name = expr[:paren].strip()
    func = func_lookup.get(name)
    if func is None:
        return False, "?", f"Function `{name}` not in toolkit"

    inner = expr[paren + 1:].rstrip(")")
    if not inner.strip():
        if func.inputs:
            return False, "?", f"`{name}` requires {len(func.inputs)} args but got 0"
        return True, func.output, f"`{name}()` -> {func.output}"

    provided = {}
    for part in _split_top_level_commas(inner):
        if "=" not in part:
            return False, "?", f"Non-keyword arg in `{expr}`: `{part}`"
        k, _, v = part.partition("=")
        provided[k.strip()] = v.strip()

    expected = dict(func.inputs)
    errors = []
    for pname, ptype in func.inputs:
        if pname not in provided:
            errors.append(f"Missing arg `{pname}: {ptype}`")
            continue
        ok, sub_type, reason = _type_check_expr(provided[pname], func_lookup, var_types)
        if not ok:
            errors.append(f"Arg `{pname}`: {reason}")
        elif not _types_compatible(sub_type, ptype):
            errors.append(f"Arg `{pname}` expected `{ptype}` but got `{sub_type}`")
    for k in provided:
        if k not in expected:
            errors.append(f"Unknown param `{k}`")

    if errors:
        return False, "?", "; ".join(errors)
    return True, func.output, f"`{name}(...)` -> {func.output}"


_CALL_NAME = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def _called_functions(expr):
    return _CALL_NAME.findall(expr)


def _enumerate_valid_exprs(target_type, funcs, var_types, depth, max_results=40):
    """Every well-typed composition of exact `depth`, each function used at most
    once. Used to confirm a target is reachable and to sample a reference answer."""
    by_output = defaultdict(list)
    for f in funcs:
        by_output[f.output].append(f)

    cache = {}

    def build(req_type, d, used):
        key = (req_type, d, used)
        if key in cache:
            return cache[key]
        results = []

        if d == 0:
            results = [n for n, t in var_types.items() if _types_compatible(t, req_type)]
            cache[key] = results
            return results

        for func in by_output.get(req_type, []):
            if func.name in used:
                continue
            if not func.inputs:
                if d == 1:
                    results.append(f"{func.name}()")
                continue
            for chain_param, chain_type in func.inputs:
                sub_chains = build(chain_type, d - 1, used | {func.name})
                if not sub_chains:
                    continue
                arg_options, ok = [], True
                for pname, ptype in func.inputs:
                    if pname == chain_param:
                        arg_options.append([f"{pname}={sc}" for sc in sub_chains])
                    else:
                        leaves = build(ptype, 0, used)
                        if not leaves:
                            ok = False
                            break
                        arg_options.append([f"{pname}={lf}" for lf in leaves])
                if not ok:
                    continue
                for combo in product(*arg_options):
                    results.append(f"{func.name}({', '.join(combo)})")
                    if len(results) >= max_results:
                        cache[key] = results
                        return results
        cache[key] = results
        return results

    return build(target_type, depth, frozenset())


def _mask_names(funcs):
    """Real library names are hidden as f0, f1, ... so an answer can't be produced
    from memorized knowledge of the library's real API."""
    name_map = {f.name: f"f{i}" for i, f in enumerate(funcs)}
    return name_map, {v: k for k, v in name_map.items()}


def _rename(expr, mapping):
    for old in sorted(mapping, key=len, reverse=True):
        expr = re.sub(rf"\b{re.escape(old)}\s*\(", mapping[old] + "(", expr)
    return expr


# --------------------------------------------------------------------------
# Task 3: Type Inhabitation
# --------------------------------------------------------------------------

class TypeInhabitation(DevTask):
    summary = "Compose typed functions from a toolkit into an expression that produces a target type."

    def __init__(self, config=None):
        super().__init__(config=config or TypeInhabitationCfg())

    def generate_entry(self):
        cfg = self.config
        funcs = _load_functions(cfg.db_path, cfg.libraries)
        by_output = defaultdict(list)
        for f in funcs:
            by_output[f.output].append(f)
        targets = [t for t, fs in by_output.items() if len(fs) >= 2]
        if not targets:
            raise RuntimeError(f"No viable target types found in {cfg.db_path}.")

        for _ in range(cfg.max_attempts):
            target_type = random.choice(targets)
            toolkit, var_types = _select_toolkit(funcs, target_type, cfg.n_funcs)
            if not toolkit or not var_types:
                continue

            valid_exprs = _enumerate_valid_exprs(target_type, toolkit, var_types, cfg.depth)
            if not valid_exprs:
                continue

            name_map, reverse_map = _mask_names(toolkit)
            func_lookup = {f.name: f for f in toolkit}
            toolkit_text = "\n".join(
                f"  {name_map[f.name]}({', '.join(f'{n}: {t}' for n, t in f.inputs)}) -> {f.output}"
                for f in toolkit
            )
            vars_text = "\n".join(f"  {name}: {t}" for name, t in sorted(var_types.items()))

            metadata = edict(
                toolkit_text=toolkit_text,
                vars_text=vars_text,
                target_type=target_type,
                depth=cfg.depth,
                func_lookup=func_lookup,
                var_types=var_types,
                reverse_map=reverse_map,
            )
            answer = _rename(random.choice(valid_exprs), name_map)
            return Entry(metadata=metadata, answer=answer)

        raise RuntimeError(f"Failed to generate a TypeInhabitation task. Config: {cfg}")

    def render_prompt(self, metadata):
        return (
            "You are given a typed toolkit of functions and variables.\n\n"
            f"Functions:\n{metadata.toolkit_text}\n\n"
            f"Variables:\n{metadata.vars_text}\n\n"
            f"Target type: `{metadata.target_type}`\n\n"
            f"Write a single expression of exact composition depth {metadata.depth} "
            "(exactly that many chained function calls) using only the functions and "
            "variables above, that evaluates to a value of the target type.\n"
            "Rules:\n"
            "- Every call must use keyword arguments, e.g. `f0(x=f1(y=var_a))`.\n"
            "- Use each function at most once.\n"
            "- Every argument's type must match the function's signature."
        )

    def score_answer(self, answer, entry):
        metadata = entry["metadata"] if isinstance(entry, dict) else entry.metadata
        expr = _rename(str(answer).strip(), metadata.reverse_map)

        calls = _called_functions(expr)
        if len(calls) != metadata.depth or len(set(calls)) != len(calls):
            return 0.0

        ok, ret_type, _ = _type_check_expr(expr, metadata.func_lookup, metadata.var_types)
        return 1.0 if ok and ret_type == metadata.target_type else 0.0

    def balancing_key(self, problem):
        return problem.metadata.target_type


# --------------------------------------------------------------------------
# Bushy-tree generator for CodeRepair. Unlike _enumerate_valid_exprs (which
# only ever recurses down a single chain parameter, forcing every sibling
# argument to be a bare variable), this grows a real tree: every argument of
# every call independently may be a further call or a leaf variable, so a
# function can have several sibling arguments that are themselves calls
# (e.g. f6(hidden_state=<3-deep chain>, output_size=f3(...))). Function
# uniqueness is threaded sequentially across every branch, not just the one
# "chain" branch, so it holds globally over the whole tree.
#
# A node is either ("var", name) or ("call", func_name, {pname: node, ...}).
# --------------------------------------------------------------------------

def _grow_node(target_type, by_output, var_types, used, budget, branch_prob, force_call=False):
    funcs = [f for f in by_output.get(target_type, []) if f.name not in used]
    leaves = [n for n, t in var_types.items() if _types_compatible(t, target_type)]

    want_call = budget > 0 and funcs and (force_call or not leaves or random.random() < branch_prob)
    if want_call:
        random.shuffle(funcs)
        for func in funcs:
            new_used = used | {func.name}
            args, ok = {}, True
            for pname, ptype in func.inputs:
                sub = _grow_node(ptype, by_output, var_types, new_used, budget - 1, branch_prob)
                if sub is None:
                    ok = False
                    break
                node, new_used = sub
                args[pname] = node
            if ok:
                return ("call", func.name, args), new_used
            # this candidate function couldn't be completed -- try the next one

    if leaves:
        return ("var", random.choice(leaves)), used
    return None


def _tree_call_count(node):
    if node[0] == "var":
        return 0
    return 1 + sum(_tree_call_count(sub) for sub in node[2].values())


def _grow_valid_tree(target_type, funcs, var_types, min_depth, max_depth, max_attempts=80, branch_prob=0.65):
    by_output = defaultdict(list)
    for f in funcs:
        by_output[f.output].append(f)

    for _ in range(max_attempts):
        result = _grow_node(target_type, by_output, var_types, frozenset(), max_depth, branch_prob, force_call=True)
        if result is None:
            continue
        node, _ = result
        if min_depth <= _tree_call_count(node) <= max_depth:
            return node
    return None


def _collect_call_nodes(node, _is_root=True):
    """All function-call nodes in the tree, excluding the root -- these are the
    candidate subtrees a hole could hide."""
    out = []
    if node[0] == "call":
        if not _is_root:
            out.append(node)
        for sub in node[2].values():
            out.extend(_collect_call_nodes(sub, False))
    return out


def _contains(a, b):
    """Whether node b is a or is found anywhere inside a's subtree."""
    if a is b:
        return True
    if a[0] != "call":
        return False
    return any(_contains(sub, b) for sub in a[2].values())


def _pick_holes(root, n_holes):
    """Choose up to n_holes call-nodes such that none is nested inside another."""
    candidates = _collect_call_nodes(root)
    random.shuffle(candidates)
    chosen = []
    for node in candidates:
        if len(chosen) >= n_holes:
            break
        if any(_contains(c, node) or _contains(node, c) for c in chosen):
            continue
        chosen.append(node)
    return chosen


def _render_tree(node, hole_ids, hole_labels, name_map):
    if id(node) in hole_ids:
        return hole_labels[id(node)]
    if node[0] == "var":
        return node[1]
    _, func_name, args = node
    parts = [f"{pname}={_render_tree(sub, hole_ids, hole_labels, name_map)}" for pname, sub in args.items()]
    return f"{name_map.get(func_name, func_name)}({', '.join(parts)})"


_HOLE_ANSWER = re.compile(r"\?\?(\d+)\s*=\s*(.+)")


def _parse_hole_answers(text):
    fills = {}
    for line in str(text).splitlines():
        m = _HOLE_ANSWER.match(line.strip().rstrip(","))
        if m:
            fills[int(m.group(1))] = m.group(2).strip()
    return fills


@dataclass
class CodeRepairCfg(Config):
    difficulty: float = 0.0
    min_depth: int = 4
    max_depth: int = 8
    n_holes: int = 1
    n_funcs: int = 8
    max_attempts: int = 400
    db_path: str = "functions.db"
    libraries: tuple[str, ...] | None = None  # None -> DEFAULT_LIBRARIES

    def apply_difficulty(self, level):
        self.difficulty += level
        self.min_depth = max(2, sround(self.min_depth + 0.5 * level))
        self.max_depth = max(self.min_depth + 1, sround(self.max_depth + level))
        self.n_funcs = max(4, sround(self.n_funcs + level))
        self.n_holes = max(1, min(3, sround(self.n_holes + 0.3 * level)))


# --------------------------------------------------------------------------
# Task 4: Code Repair
# --------------------------------------------------------------------------

class CodeRepair(DevTask):
    summary = "Fill in the missing sub-expression(s) of a partially-specified typed function composition."

    def __init__(self, config=None):
        super().__init__(config=config or CodeRepairCfg())

    def generate_entry(self):
        cfg = self.config
        funcs = _load_functions(cfg.db_path, cfg.libraries)
        by_output = defaultdict(list)
        for f in funcs:
            by_output[f.output].append(f)
        targets = [t for t, fs in by_output.items() if len(fs) >= 2]
        if not targets:
            raise RuntimeError(f"No viable target types found in {cfg.db_path}.")

        for _ in range(cfg.max_attempts):
            target_type = random.choice(targets)
            toolkit, var_types = _select_toolkit(funcs, target_type, cfg.n_funcs)
            if not toolkit or not var_types:
                continue

            tree = _grow_valid_tree(target_type, toolkit, var_types, cfg.min_depth, cfg.max_depth, max_attempts=400)
            if tree is None:
                continue

            holes = _pick_holes(tree, cfg.n_holes)
            if len(holes) < cfg.n_holes:
                continue  # not enough independent call-subtrees to hide; retry with a fresh tree

            total_depth = _tree_call_count(tree)
            name_map, reverse_map = _mask_names(toolkit)
            func_lookup = {f.name: f for f in toolkit}

            hole_labels = {id(node): f"??{i}" for i, node in enumerate(holes, start=1)}
            hole_meta = [
                edict(id=i, type=func_lookup[node[1]].output)
                for i, node in enumerate(holes, start=1)
            ]

            skeleton_text = _render_tree(tree, set(hole_labels), hole_labels, name_map)
            reference_answer = "\n".join(
                f"{hole_labels[id(node)]} = {_render_tree(node, set(), {}, name_map)}"
                for node in holes
            )

            toolkit_text = "\n".join(
                f"  {name_map[f.name]}({', '.join(f'{n}: {t}' for n, t in f.inputs)}) -> {f.output}"
                for f in toolkit
            )
            vars_text = "\n".join(f"  {name}: {t}" for name, t in sorted(var_types.items()))

            metadata = edict(
                toolkit_text=toolkit_text,
                vars_text=vars_text,
                skeleton_text=skeleton_text,
                target_type=target_type,
                total_depth=total_depth,
                holes=hole_meta,
                func_lookup=func_lookup,
                var_types=var_types,
                reverse_map=reverse_map,
            )
            return Entry(metadata=metadata, answer=reference_answer)

        raise RuntimeError(f"Failed to generate a CodeRepair task. Config: {cfg}")

    def render_prompt(self, metadata):
        answer_lines = "\n".join(f"??{h.id} = <expression>" for h in metadata.holes)
        holes_desc = ", ".join(f"`??{h.id}` (must have type `{h.type}`)" for h in metadata.holes)
        return (
            "You are given a typed toolkit of functions and variables, and an expression "
            "with one or more missing sub-expressions marked `??1`, `??2`, ....\n\n"
            f"Functions:\n{metadata.toolkit_text}\n\n"
            f"Variables:\n{metadata.vars_text}\n\n"
            f"Expression (overall type: `{metadata.target_type}`):\n{metadata.skeleton_text}\n\n"
            f"Missing pieces: {holes_desc}\n\n"
            "For each missing piece, write a valid expression (using only the functions and "
            "variables above) of the required type that, once substituted in, makes the whole "
            "expression well-typed.\n"
            "Rules:\n"
            "- Every call must use keyword arguments, e.g. `f0(x=f1(y=var_a))`.\n"
            "- Across the WHOLE expression -- the parts already shown plus everything you fill "
            "in -- use each function at most once.\n"
            "- Answer with exactly one line per missing piece, in this form:\n"
            f"{answer_lines}"
        )

    def score_answer(self, answer, entry):
        metadata = entry["metadata"] if isinstance(entry, dict) else entry.metadata
        fills = _parse_hole_answers(answer)
        if set(fills) != {h.id for h in metadata.holes}:
            return 0.0

        combined = metadata.skeleton_text
        for h in metadata.holes:
            combined = re.sub(rf"\?\?{h.id}(?!\d)", lambda _m, r=fills[h.id]: r, combined, count=1)

        expr = _rename(combined, metadata.reverse_map)
        calls = _called_functions(expr)
        if len(calls) != metadata.total_depth or len(set(calls)) != len(calls):
            return 0.0

        ok, ret_type, _ = _type_check_expr(expr, metadata.func_lookup, metadata.var_types)
        return 1.0 if ok and ret_type == metadata.target_type else 0.0

    def balancing_key(self, problem):
        return (problem.metadata.target_type, len(problem.metadata.holes))


# --------------------------------------------------------------------------
# Optional: pre-build the function DB instead of paying the scan cost lazily
# on the first TypeInhabitation.generate_entry() call.
#
#   python code_reasoning.py --db-path functions.db
#   python code_reasoning.py --db-path functions.db --libraries numpy pandas
# --------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Pre-build the TypeInhabitation function DB.")
    p.add_argument("--db-path", default="functions.db")
    p.add_argument("--libraries", nargs="*", default=None, help="defaults to DEFAULT_LIBRARIES")
    args = p.parse_args()

    n = build_function_db(args.db_path, args.libraries or DEFAULT_LIBRARIES)
    print(f"Inserted {n} typed functions into {args.db_path}")
"""Procedural Lean 4 theorem generation, Mathlib-backed.

Two generation paths share one shape (header, hypotheses, goal, proof body):

1. Grammar-driven goals over Int/Nat/Prop sampled with gramforge, classified by
   Lean's tactic ladder (rfl -> decide -> norm_num -> omega -> ring -> linarith
   -> tauto -> simp -> aesop). The minimum-power closing tactic is the
   "elegant strategy" used as ground truth.

2. Mathlib lemma schemas: a small curated list of named lemmas whose slots are
   filled with gramforge-sampled expressions; the proof is `exact LEMMA args`.

Lean itself is the only oracle. Install (elan + Mathlib + REPL) lives under
appdirs, so nothing leaks into the user's home or the project tree.
"""

import ast
import json
import os
import platform
import queue
import random
import re
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlretrieve

from appdirs import AppDirs
from easydict import EasyDict as edict
from gramforge import generate, init_grammar
from reasoning_core.template import Config, Problem, Task


# ============================================================================
# Appdir-managed Lean + Mathlib install
# ============================================================================

_DIRS = AppDirs("reasoning_core")
_BASE = Path(_DIRS.user_data_dir) / "lean"
_ELAN_HOME = _BASE / "elan"
_PROJECT = _BASE / "project"
_LEAN_TOOLCHAIN = "leanprover/lean4:v4.13.0"
_MATHLIB_REV = "v4.13.0"
_REPL_REV = "v4.13.0"
_ELAN_RELEASE = "v4.1.2"

BANNED_LEAN_TOKENS = (
    "sorry", "admit", "unsafe", "#eval", "native_decide",
    "set_option", "opaque", "syntax ", "macro ",
)

_LAKEFILE = f"""\
import Lake
open Lake DSL

package leanrepl

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "{_MATHLIB_REV}"

require repl from git
  "https://github.com/leanprover-community/repl" @ "{_REPL_REV}"

lean_lib LeanRepl
"""


def _elan_env():
    env = os.environ.copy()
    env["ELAN_HOME"] = str(_ELAN_HOME)
    env["PATH"] = f"{_ELAN_HOME / 'bin'}{os.pathsep}{env.get('PATH', '')}"
    return env


def _install_elan():
    if (_ELAN_HOME / "bin" / "lean").exists():
        return
    _BASE.mkdir(parents=True, exist_ok=True)
    sys_, mach = platform.system().lower(), platform.machine().lower()
    arch = "aarch64" if ("arm" in mach or "aarch64" in mach) else "x86_64"
    tgts = {"linux": f"{arch}-unknown-linux-gnu", "darwin": f"{arch}-apple-darwin"}
    if sys_ not in tgts:
        raise RuntimeError(f"Unsupported platform for auto-install: {sys_}")
    url = (f"https://github.com/leanprover/elan/releases/download/"
           f"{_ELAN_RELEASE}/elan-{tgts[sys_]}.tar.gz")
    with tempfile.TemporaryDirectory() as td:
        tar = Path(td) / "elan.tar.gz"
        urlretrieve(url, tar)
        subprocess.run(["tar", "xzf", str(tar), "-C", td], check=True)
        subprocess.run(
            [str(Path(td) / "elan-init"), "-y", "--no-modify-path",
             "--default-toolchain", _LEAN_TOOLCHAIN],
            env=_elan_env(), check=True,
        )


def _ensure_project():
    """Build a lake project with Mathlib + REPL deps under appdirs. Returns repl binary."""
    repl_bin = _PROJECT / ".lake" / "packages" / "repl" / ".lake" / "build" / "bin" / "repl"
    if repl_bin.exists():
        return repl_bin
    _install_elan()
    _PROJECT.mkdir(parents=True, exist_ok=True)
    (_PROJECT / "lakefile.lean").write_text(_LAKEFILE)
    (_PROJECT / "lean-toolchain").write_text(_LEAN_TOOLCHAIN + "\n")
    (_PROJECT / "LeanRepl.lean").write_text("import Mathlib\n")
    env = _elan_env()
    subprocess.run(["lake", "update"], cwd=_PROJECT, env=env, check=True)
    # mathlib cache: skip the multi-hour olean compile, fall back silently if unavailable
    subprocess.run(["lake", "exe", "cache", "get"], cwd=_PROJECT, env=env, check=False)
    subprocess.run(["lake", "build", "LeanRepl"], cwd=_PROJECT, env=env, check=True)
    subprocess.run(["lake", "build", "repl"], cwd=_PROJECT, env=env, check=True)
    if not repl_bin.exists():
        raise RuntimeError(f"REPL binary missing after build: {repl_bin}")
    return repl_bin


# ============================================================================
# REPL wrapper — Mathlib loaded into a persistent environment handle
# ============================================================================

class LeanRunner:
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.cache = {}
        self.proc = None
        self.stdout = queue.Queue()
        self._mathlib_env = None
        self._start()

    def _start(self):
        self.close()
        repl_bin = _ensure_project()
        self.proc = subprocess.Popen(
            ["lake", "env", str(repl_bin)],
            cwd=_PROJECT, env=_elan_env(),
            text=True, encoding="utf-8",
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        threading.Thread(target=self._read, daemon=True).start()
        try:
            resp = self._send_raw({"cmd": "import Mathlib"})
            self._mathlib_env = resp.get("env")
        except Exception:
            self._mathlib_env = None

    def _read(self):
        for line in self.proc.stdout:
            line = line.strip()
            if line:
                self.stdout.put(line)

    def close(self):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.kill()
            except Exception:
                pass
        self.proc = None

    def _send_raw(self, payload):
        self.proc.stdin.write(json.dumps(payload) + "\n\n")
        self.proc.stdin.flush()
        chunks = []
        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self._start()
                raise TimeoutError("Lean REPL timeout")
            try:
                chunks.append(self.stdout.get(timeout=remaining))
            except queue.Empty:
                self._start()
                raise TimeoutError("Lean REPL timeout")
            try:
                return json.loads("\n".join(chunks))
            except json.JSONDecodeError:
                continue

    def check(self, code):
        if code in self.cache:
            return self.cache[code]
        payload = {"cmd": code}
        if self._mathlib_env is not None:
            payload["env"] = self._mathlib_env
        try:
            result = self._send_raw(payload)
        except Exception as e:
            self._start()
            out = (False, str(e))
        else:
            msgs = result.get("messages") or []
            has_error = any(m.get("severity") == "error" for m in msgs)
            has_sorry = bool(result.get("sorries"))
            diag = "\n".join(str(m.get("data", m)) for m in msgs)
            out = (not has_error and not has_sorry, diag)
        self.cache[code] = out
        return out


_GLOBAL_RUNNER = None
def get_runner():
    global _GLOBAL_RUNNER
    if _GLOBAL_RUNNER is None:
        _GLOBAL_RUNNER = LeanRunner()
    return _GLOBAL_RUNNER


def _safe(text):
    low = str(text).lower()
    return not any(tok in low for tok in BANNED_LEAN_TOKENS)


# ============================================================================
# Config + gramforge grammars
# ============================================================================

@dataclass
class LeanConfig(Config):
    n_vars: int = 2
    expr_depth: int = 3
    n_hyps: int = 1
    n_candidates: int = 6

    def update(self, c):
        self.n_vars += c
        self.expr_depth += c
        self.n_hyps += c
        self.n_candidates += c


VAR_NAMES = tuple("abcdefghijkmn")
THEOREM_NAMES = ("ex", "claim", "target", "lemma_main", "goal")


def _vars(n):
    return list(VAR_NAMES[: max(1, n)])


def _int_lin_grammar(vars_, max_coef=4):
    """Linear Int expressions: sums/differences of variables with small coefficients."""
    g = init_grammar(["lean"], preprocess_template=lambda s: s)
    g("start(e)", "{0}")
    g("e(atom)", "{0}", weight=3)
    g("e(e,e)", "({0} + {1})")
    g("e(e,e)", "({0} - {1})")
    g("atom", "0")
    g("atom", "1")
    for c in range(2, max_coef + 1):
        g("atom", str(c))
    for v in vars_:
        g("atom", v)
        for c in range(2, max_coef + 1):
            g("atom", f"{c} * {v}")
    return g


def _int_poly_grammar(vars_, max_coef=3):
    g = _int_lin_grammar(vars_, max_coef)
    g("e(e,e)", "({0} * {1})", weight=2)
    for v in vars_:
        g("atom", f"{v}^2")
    return g


def _prop_grammar(atoms):
    g = init_grammar(["lean"], preprocess_template=lambda s: s)
    g("start(p)", "{0}")
    g("p(atom)", "{0}", weight=3)
    g("p(p,p)", "({0} ∧ {1})")
    g("p(p,p)", "({0} ∨ {1})")
    g("p(p,p)", "({0} → {1})")
    g("p(p)", "(¬ {0})")
    for a in atoms:
        g("atom", a)
    return g


def _sample(grammar, depth):
    return generate(grammar, depth=depth, mode="sequential") @ "lean"


# ============================================================================
# Strategy 1: gramforge expressions + Lean tactic oracle
# ============================================================================

# Ring axioms applied as string rewrites: produce a syntactically distinct but
# provably-equal form. `ring` will close the resulting equality.
_RING_REWRITES = (
    (re.compile(r"\(([^()]+) \+ ([^()]+)\)"),
     lambda m: f"({m.group(2)} + {m.group(1)})"),
    (re.compile(r"\(([^()]+) \* ([^()]+)\)"),
     lambda m: f"({m.group(2)} * {m.group(1)})"),
    (re.compile(r"\(([^()]+) \* \(([^()]+) \+ ([^()]+)\)\)"),
     lambda m: f"({m.group(1)} * {m.group(2)} + {m.group(1)} * {m.group(3)})"),
)


def _ring_equiv(expr, names):
    s = expr
    for _ in range(random.randint(1, 4)):
        rule, repl = random.choice(_RING_REWRITES)
        m = rule.search(s)
        if m:
            s = s[: m.start()] + repl(m) + s[m.end():]
    if random.random() < 0.4 and names:
        s = f"({s} + 0 * {random.choice(names)})"
    return s


def gen_polynomial_eq(config):
    names = _vars(int(config.n_vars))
    g = _int_poly_grammar(names)
    lhs = _sample(g, int(config.expr_depth))
    rhs = _ring_equiv(lhs, names)
    if rhs == lhs:
        return None
    return edict(
        decl=f"({' '.join(names)} : Int)", hyps=[],
        goal=f"{lhs} = {rhs}", primary="ring", kind="poly_eq",
    )


def gen_linear_ineq(config):
    """Bound each variable, then ask omega about a positive linear combination of bounds."""
    n = max(2, int(config.n_vars))
    names = _vars(n)
    hyps, bounds = [], {}
    for i, v in enumerate(names):
        b = random.randint(0, 20)
        op = random.choice(["≤", "<"])
        bounds[v] = (b, op)
        hyps.append((f"h{i}", f"{v} {op} {b}"))
    coefs = {v: random.randint(1, 4) for v in names}
    lhs = " + ".join(f"{c} * {v}" if c > 1 else v for v, c in coefs.items())
    upper = sum(c * bounds[v][0] for v, c in coefs.items())
    upper += random.randint(0, 5)  # slack keeps it provable
    op = "≤" if all(o == "≤" for _, o in bounds.values()) else "<"
    return edict(
        decl=f"({' '.join(names)} : Int)", hyps=hyps,
        goal=f"{lhs} {op} {upper}",
        primary="omega", kind="lin_ineq",
    )


def gen_divisibility(config):
    names = _vars(max(2, int(config.n_vars)))
    a, b = names[0], names[1]
    k = random.randint(2, 6)
    c1, c2 = random.randint(1, 4), random.randint(1, 4)
    sign = random.choice(["+", "-"])
    expr = f"{c1} * {a} {sign} {c2} * {b}"
    return edict(
        decl=f"({' '.join(names)} : Int)",
        hyps=[("h1", f"({k} : Int) ∣ {a}"), ("h2", f"({k} : Int) ∣ {b}")],
        goal=f"({k} : Int) ∣ ({expr})", primary="omega", kind="div",
    )


def gen_concrete(config):
    a = random.randint(1, 100)
    b = random.randint(1, 50)
    op = random.choice(["+", "*", "%"])
    res = {"+": a + b, "*": a * b, "%": a % b}[op]
    return edict(
        decl="", hyps=[],
        goal=f"({a} {op} {b} : Nat) = {res}", primary="decide", kind="concrete",
    )


_TAUT_TEMPLATES = (
    "({p} ∧ {q}) → {p}",
    "({p} ∧ {q}) → {q}",
    "{p} → ({p} ∨ {q})",
    "({p} → {q}) → (¬ {q} → ¬ {p})",
    "({p} ∨ {q}) ∧ ¬ {p} → {q}",
    "({p} → {q}) ∧ ({q} → {r}) → ({p} → {r})",
    "¬ ({p} ∧ ¬ {p})",
    "{p} ∨ ¬ {p}",
    "({p} → {q}) → (({p} ∧ {r}) → ({q} ∧ {r}))",
    "(({p} ∧ {q}) ∨ ({p} ∧ {r})) → ({p} ∧ ({q} ∨ {r}))",
)


def gen_tautology(config):
    """Tautology schema instantiated with random propositional subformulas."""
    tmpl = random.choice(_TAUT_TEMPLATES)
    atoms = [f"p{i}" for i in range(5)]
    g = _prop_grammar(atoms)
    slots = sorted(set(re.findall(r"\{(\w+)\}", tmpl)))
    bindings = {s: _sample(g, max(1, int(config.expr_depth) - 1)) for s in slots}
    formula = tmpl.format(**bindings)
    used = sorted(set(re.findall(r"\bp\d+\b", formula)))
    decl = f"({' '.join(used)} : Prop)" if used else "(p0 : Prop)"
    return edict(decl=decl, hyps=[], goal=formula, primary="tauto", kind="taut")


# ============================================================================
# Strategy 2: Mathlib lemma schemas + gramforge slot instantiation
# ============================================================================

# (lemma, hyp_templates, goal_template, type, slot_names)
_LEMMA_SCHEMAS = (
    # order
    ("le_trans",         ("{a} ≤ {b}", "{b} ≤ {c}"), "{a} ≤ {c}",                  "Int", ("a","b","c")),
    ("lt_trans",         ("{a} < {b}", "{b} < {c}"), "{a} < {c}",                  "Int", ("a","b","c")),
    ("lt_of_lt_of_le",   ("{a} < {b}", "{b} ≤ {c}"), "{a} < {c}",                  "Int", ("a","b","c")),
    ("lt_of_le_of_lt",   ("{a} ≤ {b}", "{b} < {c}"), "{a} < {c}",                  "Int", ("a","b","c")),
    # additive monotonicity
    ("add_le_add",       ("{a} ≤ {b}", "{c} ≤ {d}"), "{a} + {c} ≤ {b} + {d}",       "Int", ("a","b","c","d")),
    ("add_lt_add",       ("{a} < {b}", "{c} < {d}"), "{a} + {c} < {b} + {d}",       "Int", ("a","b","c","d")),
    ("add_le_add_left",  ("{a} ≤ {b}",),             "{c} + {a} ≤ {c} + {b}",       "Int", ("a","b","c")),
    ("add_le_add_right", ("{a} ≤ {b}",),             "{a} + {c} ≤ {b} + {c}",       "Int", ("a","b","c")),
    # divisibility
    ("dvd_add",          ("{k} ∣ {a}", "{k} ∣ {b}"), "{k} ∣ ({a} + {b})",          "Int", ("k","a","b")),
    ("dvd_sub",          ("{k} ∣ {a}", "{k} ∣ {b}"), "{k} ∣ ({a} - {b})",          "Int", ("k","a","b")),
    ("dvd_mul_of_dvd_left",  ("{a} ∣ {b}",),         "{a} ∣ ({b} * {c})",          "Int", ("a","b","c")),
    ("dvd_mul_of_dvd_right", ("{a} ∣ {b}",),         "{a} ∣ ({c} * {b})",          "Int", ("a","b","c")),
    ("dvd_trans",        ("{a} ∣ {b}", "{b} ∣ {c}"), "{a} ∣ {c}",                  "Int", ("a","b","c")),
    # absolute value / squares
    ("abs_nonneg",       (),                          "0 ≤ |{a}|",                  "Int", ("a",)),
    ("abs_add",          (),                          "|{a} + {b}| ≤ |{a}| + |{b}|", "Int", ("a","b")),
    ("sq_nonneg",        (),                          "0 ≤ {a} ^ 2",                "Int", ("a",)),
    ("mul_self_nonneg",  (),                          "0 ≤ {a} * {a}",              "Int", ("a",)),
)


def gen_lemma(config):
    name, hyp_tmpls, goal_tmpl, ty, slots = random.choice(_LEMMA_SCHEMAS)
    g = _int_lin_grammar(_vars(int(config.n_vars)), max_coef=3)
    bindings = {s: _sample(g, max(1, int(config.expr_depth) - 1)) for s in slots}
    hyps = [(f"h{i}", t.format(**bindings)) for i, t in enumerate(hyp_tmpls)]
    goal = goal_tmpl.format(**bindings)
    used = sorted(set(re.findall(r"\b([a-n])\b", " ".join(bindings.values()))))
    decl = f"({' '.join(used)} : {ty})" if used else ""
    args = " ".join(h for h, _ in hyps)
    proof = f"exact {name} {args}" if args else f"exact {name}"
    return edict(decl=decl, hyps=hyps, goal=goal, primary=proof, kind=f"lemma:{name}")


STRATEGIES = (
    gen_polynomial_eq, gen_linear_ineq, gen_divisibility,
    gen_concrete, gen_tautology, gen_lemma,
)


# ============================================================================
# Tactic ladder + instance assembly
# ============================================================================

# Earlier tactics are "more elegant" (more targeted, cheaper to verify).
TACTIC_LADDER = (
    "rfl", "decide", "norm_num", "omega", "ring",
    "linarith", "tauto", "simp", "aesop",
)


def _render(inst, name="ex"):
    hyp_str = " ".join(f"({h} : {b})" for h, b in inst.hyps)
    decl = inst.decl + " " if inst.decl else ""
    return f"theorem {name} {decl}{hyp_str} : {inst.goal} := by\n"


def _try(header, body, runner):
    return runner.check(header + "  " + body + "\n")[0]


def make_instance(config, runner):
    """Generate one labeled instance. Discards strategies whose primary proof fails."""
    for _ in range(200):
        inst = random.choice(STRATEGIES)(config)
        if not inst or not _safe(inst.goal):
            continue
        header = _render(inst)
        if not _try(header, inst.primary, runner):
            continue
        # Minimum-power tactic from the ladder = elegant proof
        elegant = next(
            (t for t in TACTIC_LADDER if _try(header, t, runner)),
            inst.primary,
        )
        # Candidate pool: ladder + the primary proof. Some will compile, some won't.
        cands = list(TACTIC_LADDER)
        if inst.primary not in cands:
            cands.append(inst.primary)
        random.shuffle(cands)
        labels = [_try(header, c, runner) for c in cands]
        if not any(labels) or all(labels):
            continue
        return edict(
            kind=inst.kind, header=header,
            primary=inst.primary, elegant=elegant,
            candidates=cands, labels=labels,
        )
    raise RuntimeError("failed to produce a Lean instance")


# ============================================================================
# Tasks
# ============================================================================

class LeanProofCompletion(Task):
    """Fill the proof body. Ground truth is the minimum-power closing tactic."""

    def __init__(self, config=LeanConfig()):
        super().__init__(config=config, timeout=120)
        self.runner = get_runner()

    def generate(self):
        inst = make_instance(self.config, self.runner)
        return Problem(
            edict(kind=inst.kind, template=inst.header + "  __ANSWER__\n"),
            inst.elegant,
        )

    def prompt(self, metadata):
        return (
            "Fill `__ANSWER__` with a Lean 4 tactic block that closes the goal.\n"
            "Mathlib is imported; tactics such as rfl, decide, norm_num, omega, ring, "
            "linarith, tauto, simp, aesop are available. The answer is only the "
            "replacement tactic block.\n\n"
            f"{metadata.template}"
        )

    def score_answer(self, answer, entry):
        if not answer or not _safe(answer):
            return 0.0
        code = entry.metadata.template.replace("__ANSWER__", str(answer).strip())
        return float(get_runner().check(code)[0])


class LeanCandidateCompilation(Task):
    """True/False on whether a single candidate proof body closes the theorem."""

    def __init__(self, config=LeanConfig()):
        super().__init__(config=config, timeout=120)
        self.runner = get_runner()
        self._want_positive = True

    def generate(self):
        inst = make_instance(self.config, self.runner)
        pool = [i for i, ok in enumerate(inst.labels) if ok == self._want_positive]
        if not pool:
            pool = list(range(len(inst.candidates)))
        idx = random.choice(pool)
        self._want_positive = not self._want_positive
        return Problem(
            edict(kind=inst.kind,
                  theorem=inst.header + "  ?\n",
                  candidate=inst.candidates[idx]),
            "True" if inst.labels[idx] else "False",
        )

    def prompt(self, metadata):
        return (
            "Decide whether the candidate Lean 4 tactic body closes the theorem.\n"
            "The answer is exactly True or False.\n\n"
            f"THEOREM WITH HOLE:\n{metadata.theorem}\n"
            f"CANDIDATE:\n{metadata.candidate}"
        )

    def score_answer(self, answer, entry):
        return float(str(answer).strip().strip("`").lower() == entry.answer.lower())


class LeanProofRepair(Task):
    """Replace a broken proof body with one that compiles."""

    def __init__(self, config=LeanConfig()):
        super().__init__(config=config, timeout=120)
        self.runner = get_runner()

    def generate(self):
        inst = make_instance(self.config, self.runner)
        bad_idx = [i for i, ok in enumerate(inst.labels) if not ok]
        if not bad_idx:
            return None
        bad = inst.candidates[random.choice(bad_idx)]
        return Problem(
            edict(kind=inst.kind,
                  broken=inst.header + "  " + bad + "\n",
                  template=inst.header + "  __ANSWER__\n"),
            inst.elegant,
        )

    def prompt(self, metadata):
        return (
            "The Lean 4 theorem below has a broken proof. Replace the proof body with "
            "one that compiles. Mathlib is imported. The answer is only the replacement "
            "tactic block.\n\n"
            f"{metadata.broken}"
        )

    score_answer = LeanProofCompletion.score_answer


class LeanCompileSelection(Task):
    """From a numbered list of candidate proofs, return the indices that compile."""

    def __init__(self, config=LeanConfig()):
        super().__init__(config=config, timeout=120)
        self.runner = get_runner()

    def generate(self):
        for _ in range(20):
            inst = make_instance(self.config, self.runner)
            pairs = list(zip(inst.candidates, inst.labels))[: max(2, int(self.config.n_candidates))]
            labels = [l for _, l in pairs]
            if not any(labels) or all(labels):
                continue
            answer = [i + 1 for i, (_, l) in enumerate(pairs) if l]
            return Problem(
                edict(kind=inst.kind,
                      theorem=inst.header + "  ?\n",
                      candidates=[c for c, _ in pairs],
                      labels=labels),
                str(answer),
            )
        raise RuntimeError("failed to assemble a balanced compile-selection instance")

    def prompt(self, metadata):
        opts = "\n".join(f"{i}. {c}" for i, c in enumerate(metadata.candidates, 1))
        return (
            "Which candidate Lean 4 tactic blocks make the theorem compile? "
            "Mathlib is imported.\n"
            "The answer is the sorted Python-style list of valid option numbers, "
            "for example [1, 4].\n\n"
            f"THEOREM WITH HOLE:\n{metadata.theorem}\n"
            f"CANDIDATES:\n{opts}"
        )

    def score_answer(self, answer, entry):
        try:
            pred = sorted({int(x) for x in ast.literal_eval(str(answer))})
        except Exception:
            pred = sorted({int(x) for x in re.findall(r"\d+", str(answer))})
        return float(pred == list(ast.literal_eval(entry.answer)))

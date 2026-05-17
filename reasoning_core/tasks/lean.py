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
import argparse
import json
import os
import platform
import queue
import random
import re
import signal
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
from reasoning_core.template import Config, DevTask, Problem


# ============================================================================
# Appdir-managed Lean + Mathlib install
# ============================================================================

_DIRS = AppDirs("reasoning_core")
_BASE = Path(_DIRS.user_data_dir) / "lean"
_ELAN_HOME = _BASE / "elan"
_PROJECT = _BASE / "project"
_INSTALL_STAMP = _PROJECT / ".reasoning_core_lean_env.json"
_LEAN_TOOLCHAIN = "leanprover/lean4:v4.29.0"
_MATHLIB_REV = "v4.29.0"
_REPL_REV = "v4.29.0"
_ELAN_RELEASE = "v4.1.2"
_PRELUDE_IMPORTS = "import Mathlib"
_LEAN_IMPORT_CMD = "import ReasoningCorePrelude"

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

lean_lib ReasoningCorePrelude
"""


def _elan_env():
    env = os.environ.copy()
    env["ELAN_HOME"] = str(_ELAN_HOME)
    env["PATH"] = f"{_ELAN_HOME / 'bin'}{os.pathsep}{env.get('PATH', '')}"
    return env


def _elan_bin(name):
    suffix = ".exe" if platform.system().lower() == "windows" else ""
    return _ELAN_HOME / "bin" / f"{name}{suffix}"


def _install_elan():
    if not _elan_bin("lean").exists():
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
    installed = subprocess.run(
        [str(_elan_bin("elan")), "toolchain", "list"],
        env=_elan_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False,
    ).stdout
    if _LEAN_TOOLCHAIN not in installed:
        subprocess.run([str(_elan_bin("elan")), "toolchain", "install", _LEAN_TOOLCHAIN],
                       env=_elan_env(), check=True)
    subprocess.run([str(_elan_bin("elan")), "default", _LEAN_TOOLCHAIN],
                   env=_elan_env(), check=True)


def _ensure_project():
    """Build a lake project with Mathlib + REPL deps under appdirs. Returns repl binary."""
    repl_bin = _PROJECT / ".lake" / "packages" / "repl" / ".lake" / "build" / "bin" / "repl"
    prelude = _PROJECT / "ReasoningCorePrelude.lean"
    prelude_olean = _PROJECT / ".lake" / "build" / "lib" / "lean" / "ReasoningCorePrelude.olean"
    stamp = {
        "lean": _LEAN_TOOLCHAIN,
        "mathlib": _MATHLIB_REV,
        "repl": _REPL_REV,
        "prelude": _PRELUDE_IMPORTS,
    }
    if repl_bin.exists() and _INSTALL_STAMP.exists():
        try:
            if json.loads(_INSTALL_STAMP.read_text()) == stamp:
                return repl_bin
        except Exception:
            pass
    if repl_bin.exists() and prelude_olean.exists() and prelude.exists():
        if prelude.read_text() == _PRELUDE_IMPORTS + "\n":
            _INSTALL_STAMP.write_text(json.dumps(stamp, sort_keys=True))
            return repl_bin
    _install_elan()
    _PROJECT.mkdir(parents=True, exist_ok=True)
    (_PROJECT / "lakefile.lean").write_text(_LAKEFILE)
    (_PROJECT / "lean-toolchain").write_text(_LEAN_TOOLCHAIN + "\n")
    (_PROJECT / "ReasoningCorePrelude.lean").write_text(_PRELUDE_IMPORTS + "\n")
    env = _elan_env()
    subprocess.run(["lake", "update"], cwd=_PROJECT, env=env, check=True)
    # mathlib cache: skip the multi-hour olean compile, fall back silently if unavailable
    subprocess.run(["lake", "exe", "cache", "get"], cwd=_PROJECT, env=env, check=False)
    subprocess.run(["lake", "build", "ReasoningCorePrelude"], cwd=_PROJECT, env=env, check=True)
    subprocess.run(["lake", "build", "repl"], cwd=_PROJECT, env=env, check=True)
    if not repl_bin.exists():
        raise RuntimeError(f"REPL binary missing after build: {repl_bin}")
    _INSTALL_STAMP.write_text(json.dumps(stamp, sort_keys=True))
    return repl_bin


def ensure_lean_mathlib(verbose=True):
    """Install or reuse Lean, Mathlib, and leanprover-community/repl in appdirs."""
    repl_bin = _ensure_project()
    if verbose:
        print(f"Lean toolchain: {_LEAN_TOOLCHAIN}")
        print(f"Mathlib project: {_PROJECT}")
        print(f"REPL binary: {repl_bin}")
    return repl_bin


# ============================================================================
# REPL wrapper — Mathlib loaded into a persistent environment handle
# ============================================================================

class LeanRunner:
    def __init__(self, timeout=360):
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
            start_new_session=True,
        )
        threading.Thread(target=self._read, daemon=True).start()
        try:
            resp = self._send_raw({"cmd": _LEAN_IMPORT_CMD})
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
                os.killpg(self.proc.pid, signal.SIGKILL)
            except Exception:
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
    n_hyps: int = 2
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


def _used_int_vars(*texts):
    return sorted(set(re.findall(r"\b([a-n])\b", " ".join(map(str, texts)))))


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


def gen_order_chain(config):
    """Random transitive chains with extra irrelevant hypotheses, solved by omega."""
    n = max(2, int(config.n_hyps))
    names = _vars(max(2, int(config.n_vars)))
    g = _int_lin_grammar(names, max_coef=3)
    terms = []
    for _ in range(n + 1):
        for _ in range(12):
            t = _sample(g, max(1, int(config.expr_depth) - 1))
            if not re.search(r"[a-n]", t):
                continue  # reject pure-constant terms (avoid vacuous hyps like 3 ≤ 2)
            if t not in terms:  # all-distinct avoids hyp cycles like a ≤ 3b ≤ a
                terms.append(t)
                break
        else:
            return None
    if len(set(terms)) < 2:
        return None
    strict_at = random.randrange(n)
    hyps = []
    for i, (a, b) in enumerate(zip(terms, terms[1:])):
        op = "<" if i == strict_at and random.random() < 0.5 else "≤"
        hyps.append((f"h{i}", f"{a} {op} {b}"))
    used = _used_int_vars(*terms)
    return edict(
        decl=f"({' '.join(used)} : Int)" if used else "",
        hyps=hyps,
        goal=f"{terms[0]} {'<' if any('<' in h for _, h in hyps) else '≤'} {terms[-1]}",
        primary="omega", kind="order_chain",
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
    """Tautology schema instantiated with disjoint propositional subformulas.

    Each slot in the template is bound to a subformula over a *disjoint* atom
    set, so the tautology doesn't collapse to a one-atom triviality.
    """
    tmpl = random.choice(_TAUT_TEMPLATES)
    slots = sorted(set(re.findall(r"\{(\w+)\}", tmpl)))
    atoms_pool = [f"p{i}" for i in range(2 * len(slots) + 1)]
    random.shuffle(atoms_pool)
    bindings = {}
    for s in slots:
        # 1–2 atoms per slot, drawn without replacement
        k = 1 if len(atoms_pool) < 2 or random.random() < 0.4 else 2
        chunk, atoms_pool = atoms_pool[:k], atoms_pool[k:]
        g = _prop_grammar(chunk)
        bindings[s] = _sample(g, max(1, int(config.expr_depth) - 1))
    formula = tmpl.format(**bindings)
    used = sorted(set(re.findall(r"\bp\d+\b", formula)))
    decl = f"({' '.join(used)} : Prop)" if used else "(p0 : Prop)"
    return edict(decl=decl, hyps=[], goal=formula, primary="tauto", kind="taut")


def gen_finset_identity(config):
    names = list("stuvwxyz")[: max(2, min(6, int(config.n_vars) + 1))]
    a, b, c = random.sample(names, 3)
    templates = (
        (f"{a} ∩ ({b} ∪ {c}) = ({a} ∩ {b}) ∪ ({a} ∩ {c})", "ext x; simp [and_or_left]"),
        (f"({a} ∪ {b}) ∩ {c} = ({a} ∩ {c}) ∪ ({b} ∩ {c})", "ext x; simp [or_and_right]"),
        (f"{a} ∪ ({b} ∩ {c}) = ({a} ∪ {b}) ∩ ({a} ∪ {c})", "ext x; simp [or_and_left]"),
        (f"{a} ∩ ({b} ∩ {c}) = ({a} ∩ {b}) ∩ {c}", "ext x; simp [and_assoc]"),
        (f"{a} ∪ ({b} ∪ {c}) = ({a} ∪ {b}) ∪ {c}", "ext x; simp [or_assoc]"),
    )
    goal, proof = random.choice(templates)
    return edict(
        decl=f"({' '.join(names)} : Finset Nat)", hyps=[],
        goal=goal, primary=proof, kind="finset_identity",
    )


def gen_set_monotone(config):
    names = list("stuvwxyz")[: max(3, min(6, int(config.n_vars) + 1))]
    s, t, u = random.sample(names, 3)
    cases = (
        ([(f"h0", f"{s} ⊆ {t}")], f"{s} ∩ {u} ⊆ {t} ∩ {u}", "intro x hx; exact ⟨h0 hx.1, hx.2⟩"),
        ([(f"h0", f"{s} ⊆ {t}")], f"{u} ∩ {s} ⊆ {u} ∩ {t}", "intro x hx; exact ⟨hx.1, h0 hx.2⟩"),
        ([(f"h0", f"{s} ⊆ {t}")], f"{s} ∪ {u} ⊆ {t} ∪ {u}", "intro x hx; rcases hx with hx | hx; exact Or.inl (h0 hx); exact Or.inr hx"),
        ([(f"h0", f"{s} ⊆ {t}")], f"{u} ∪ {s} ⊆ {u} ∪ {t}", "intro x hx; rcases hx with hx | hx; exact Or.inl hx; exact Or.inr (h0 hx)"),
    )
    hyps, goal, proof = random.choice(cases)
    return edict(
        decl=f"({' '.join(names)} : Set Int)", hyps=hyps,
        goal=goal, primary=proof, kind="set_monotone",
    )


def gen_list_length(config):
    names = list("xyzuvw")[: max(2, min(5, int(config.n_vars)))]
    xs = random.sample(names, random.randint(2, min(4, len(names))))
    concat = " ++ ".join(xs)
    length_sum = " + ".join(f"{x}.length" for x in xs)
    return edict(
        decl=f"({' '.join(xs)} : List Nat)", hyps=[],
        goal=f"({concat}).length = {length_sum}",
        primary="simp [List.length_append, Nat.add_assoc]",
        kind="list_length",
    )


# ============================================================================
# Strategy 2: Mathlib lemma schemas + gramforge slot instantiation
# ============================================================================

# (lemma, hyp_templates, goal_template, type, slot_names, proof_template)
_LEMMA_SCHEMAS = (
    # order
    ("le_trans",         ("{a} ≤ {b}", "{b} ≤ {c}"), "{a} ≤ {c}",                  "Int", ("a","b","c"), "exact le_trans h0 h1"),
    ("lt_trans",         ("{a} < {b}", "{b} < {c}"), "{a} < {c}",                  "Int", ("a","b","c"), "exact lt_trans h0 h1"),
    ("lt_of_lt_of_le",   ("{a} < {b}", "{b} ≤ {c}"), "{a} < {c}",                  "Int", ("a","b","c"), "exact lt_of_lt_of_le h0 h1"),
    ("lt_of_le_of_lt",   ("{a} ≤ {b}", "{b} < {c}"), "{a} < {c}",                  "Int", ("a","b","c"), "exact lt_of_le_of_lt h0 h1"),
    # additive monotonicity
    ("add_le_add",       ("{a} ≤ {b}", "{c} ≤ {d}"), "{a} + {c} ≤ {b} + {d}",       "Int", ("a","b","c","d"), "exact add_le_add h0 h1"),
    ("add_lt_add",       ("{a} < {b}", "{c} < {d}"), "{a} + {c} < {b} + {d}",       "Int", ("a","b","c","d"), "exact add_lt_add h0 h1"),
    ("add_le_add_left",  ("{a} ≤ {b}",),             "{c} + {a} ≤ {c} + {b}",       "Int", ("a","b","c"), "exact add_le_add_left h0 {c}"),
    ("add_le_add_right", ("{a} ≤ {b}",),             "{a} + {c} ≤ {b} + {c}",       "Int", ("a","b","c"), "exact add_le_add_right h0 {c}"),
    # divisibility
    ("dvd_add",          ("{k} ∣ {a}", "{k} ∣ {b}"), "{k} ∣ ({a} + {b})",          "Int", ("k","a","b"), "exact dvd_add h0 h1"),
    ("dvd_sub",          ("{k} ∣ {a}", "{k} ∣ {b}"), "{k} ∣ ({a} - {b})",          "Int", ("k","a","b"), "exact dvd_sub h0 h1"),
    ("dvd_mul_of_dvd_left",  ("{a} ∣ {b}",),         "{a} ∣ ({b} * {c})",          "Int", ("a","b","c"), "exact dvd_mul_of_dvd_left h0 {c}"),
    ("dvd_mul_of_dvd_right", ("{a} ∣ {b}",),         "{a} ∣ ({c} * {b})",          "Int", ("a","b","c"), "exact dvd_mul_of_dvd_right h0 {c}"),
    ("dvd_trans",        ("{a} ∣ {b}", "{b} ∣ {c}"), "{a} ∣ {c}",                  "Int", ("a","b","c"), "exact dvd_trans h0 h1"),
    # absolute value / squares
    ("abs_nonneg",       (),                          "0 ≤ |{a}|",                  "Int", ("a",), "exact abs_nonneg {a}"),
    ("abs_add",          (),                          "|{a} + {b}| ≤ |{a}| + |{b}|", "Int", ("a","b"), "exact abs_add {a} {b}"),
    ("sq_nonneg",        (),                          "0 ≤ {a} ^ 2",                "Int", ("a",), "exact sq_nonneg {a}"),
    ("mul_self_nonneg",  (),                          "0 ≤ {a} * {a}",              "Int", ("a",), "exact mul_self_nonneg {a}"),
)


def gen_lemma(config):
    name, hyp_tmpls, goal_tmpl, ty, slots, proof_tmpl = random.choice(_LEMMA_SCHEMAS)
    g = _int_lin_grammar(_vars(int(config.n_vars)), max_coef=3)
    bindings = {s: _sample(g, max(1, int(config.expr_depth) - 1)) for s in slots}
    proof_bindings = {k: f"({v})" for k, v in bindings.items()}
    hyps = [(f"h{i}", t.format(**bindings)) for i, t in enumerate(hyp_tmpls)]
    goal = goal_tmpl.format(**bindings)
    used = _used_int_vars(*bindings.values())
    decl = f"({' '.join(used)} : {ty})" if used else ""
    proof = proof_tmpl.format(**proof_bindings)
    return edict(decl=decl, hyps=hyps, goal=goal, primary=proof, kind=f"lemma:{name}")


STRATEGIES = (
    gen_polynomial_eq, gen_linear_ineq, gen_order_chain,
    gen_divisibility, gen_concrete, gen_tautology,
    gen_finset_identity, gen_set_monotone, gen_list_length,
    gen_lemma,
)


# ============================================================================
# Instance assembly (no Lean calls during generation — trust the construction)
# ============================================================================

# Per-kind static distractor table: tactics known *not* to close that kind of
# goal. The construction's primary proof is always the positive candidate.
# Distractor labels are statically False; Lean will catch a mislabel only at
# scoring time (and only for the LeanProofCompletion / Repair tasks, which use
# Lean directly).
_KIND_DISTRACTORS = {
    "lin_ineq":   ("rfl", "decide", "simp"),
    "order_chain":("rfl", "decide", "simp"),
    "div":        ("rfl", "decide", "simp"),
    "concrete":   ("rfl", "omega", "simp", "ring"),
    "poly_eq":    ("rfl", "decide", "omega"),
    "taut":       ("rfl", "decide", "omega"),
    "list_length":("rfl", "decide", "omega"),
    "finset_identity": ("rfl", "decide", "omega"),
    "set_monotone":    ("rfl", "decide", "omega", "simp"),
}
_LEMMA_DISTRACTORS = ("rfl", "decide", "omega", "simp")


def _render(inst, name="ex"):
    hyp_str = " ".join(f"({h} : {b})" for h, b in inst.hyps)
    decl = inst.decl + " " if inst.decl else ""
    return f"theorem {name} {decl}{hyp_str} : {inst.goal} := by\n"


def _candidate_pool(inst, n_candidates):
    """Build candidate proofs with labels — no Lean calls.

    The primary proof is the positive candidate; per-kind distractors are
    statically labeled negative. Shuffled order.
    """
    base = _KIND_DISTRACTORS.get(inst.kind)
    if base is None and inst.kind.startswith("lemma:"):
        base = _LEMMA_DISTRACTORS
    if base is None:
        base = ("rfl", "decide", "simp")
    distractors = [d for d in base if d != inst.primary]
    distractors = distractors[: max(1, int(n_candidates) - 1)]
    candidates = [inst.primary] + list(distractors)
    labels = [True] + [False] * len(distractors)
    pairs = list(zip(candidates, labels))
    random.shuffle(pairs)
    return [c for c, _ in pairs], [l for _, l in pairs]


def make_instance(config):
    """Sample a strategy and build a labeled instance. No Lean calls."""
    n_cand = max(2, int(getattr(config, "n_candidates", 4)))
    for _ in range(50):
        inst = random.choice(STRATEGIES)(config)
        if not inst or not _safe(inst.goal):
            continue
        header = _render(inst)
        candidates, labels = _candidate_pool(inst, n_cand)
        if not any(labels) or all(labels):
            continue
        return edict(
            kind=inst.kind, header=header,
            primary=inst.primary, elegant=inst.primary,
            candidates=candidates, labels=labels,
        )
    raise RuntimeError("failed to produce a Lean instance")


# ============================================================================
# Tasks
# ============================================================================

class LeanProofCompletion(DevTask):
    """Fill the proof body. Ground truth is the minimum-power closing tactic."""

    def __init__(self, config=LeanConfig()):
        super().__init__(config=config, timeout=120)

    def generate(self):
        inst = make_instance(self.config)
        return Problem(
            edict(kind=inst.kind, template=inst.header + "  __ANSWER__\n"),
            inst.elegant,
        )

    def prompt(self, metadata):
        return (
            "Fill `__ANSWER__` with a Lean 4 tactic block that closes the goal.\n"
            "Mathlib data/lemma modules are imported; tactics such as rfl, decide, "
            "omega, and simp are available. The answer is only the "
            "replacement tactic block.\n\n"
            f"{metadata.template}"
        )

    def score_answer(self, answer, entry):
        if not answer or not _safe(answer):
            return 0.0
        code = entry.metadata.template.replace("__ANSWER__", str(answer).strip())
        return float(get_runner().check(code)[0])


class LeanCandidateCompilation(DevTask):
    """True/False on whether a single candidate proof body closes the theorem."""

    def __init__(self, config=LeanConfig()):
        super().__init__(config=config, timeout=120)
        self._want_positive = True

    def generate(self):
        inst = make_instance(self.config)
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


class LeanProofRepair(DevTask):
    """Replace a broken proof body with one that compiles."""

    def __init__(self, config=LeanConfig()):
        super().__init__(config=config, timeout=120)

    def generate(self):
        inst = make_instance(self.config)
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


class LeanCompileSelection(DevTask):
    """From a numbered list of candidate proofs, return the indices that compile."""

    def __init__(self, config=LeanConfig()):
        super().__init__(config=config, timeout=120)

    def generate(self):
        for _ in range(20):
            inst = make_instance(self.config)
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


def main():
    parser = argparse.ArgumentParser(description="Install Lean, Mathlib, and the Lean REPL cache used by reasoning-core.")
    parser.add_argument("--quiet", action="store_true", help="only print errors")
    args = parser.parse_args()
    ensure_lean_mathlib(verbose=not args.quiet)


if __name__ == "__main__":
    main()

"""Execute a random rewrite walk over Mathlib: the vocabulary is all of Mathlib, the semantics are Lean's.

A walk starts from the left-hand side of a random Mathlib equation (its binders become the context)
and applies random rewrites found by Lean's `rw?` engine. The task gives the start term and the
lemmas used, in order, and asks for the final term (`mathlib_rewrite`), or, given the final term too, for an
intermediate one (`mathlib_rewrite_middle`).
`rw` is deterministic and every step's pattern matches exactly one subterm, so the answer is unique; it is
Lean's own pretty-printed term. Steps are given by name; a glossary states the lemmas, mixed with distractors
that also rewrite the walk's terms, so the skill is composing the rules rather than recalling them.
The walks are deliberately alien: random paths through the library, not textbook identities.
"""
import json
import random
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from reasoning_core.template import Config, DevTask, Entry, stochastic_rounding

_LEAN = Path(__file__).with_suffix(".lean")
# Compiler-generated equations are not stated mathematics.
_AUTO = re.compile(r"\.eq_\d+$|\.eq_def$|sizeOf_spec|\.match_|\._|\.proof_|\.injEq$")


def _lean():
    """The Lean runner module, imported on first generation only: it pulls in seconds of unrelated imports,
    and scoring must not depend on it."""
    from reasoning_core.tasks import math_lean
    return math_lean


def _walk_env(runner):
    """REPL environment with the walk code loaded, cached per REPL process."""
    if runner.proc is None:  # closed after a per-example alarm
        runner._start()
    if getattr(runner, "_rc_walk", (None, None))[0] is not runner.proc:
        res = runner._send_raw({"cmd": _LEAN.read_text(), "env": runner._mathlib_env})
        errors = [m["data"] for m in res.get("messages", []) if m.get("severity") == "error"]
        if errors or res.get("env") is None:
            raise RuntimeError(f"mathlib_rewrite: walk code failed to load: {errors[:2]}")
        runner._rc_walk = (runner.proc, res["env"])
    return runner._rc_walk[1]


def _eval(runner, expr, timeout=None):
    """Run a MetaM expression and return its output; "" if Lean ran past the REPL timeout. A REPL that timed
    out still owes its reply, so it is replaced: reused, its late reply would answer the next call."""
    from reasoning_core.runtime import TimeoutException
    env, default = _walk_env(runner), runner.timeout
    runner.timeout = timeout or default
    try:
        res = runner._send_raw({"cmd": f"#eval show Lean.Meta.MetaM Unit from do {expr}", "env": env})
    except TimeoutException:  # the caller's per-example alarm: drop the REPL and let the caller retry
        runner.close()
        raise
    except TimeoutError:
        runner._start()
        return ""
    finally:
        runner.timeout = default
    return "\n".join(m["data"] for m in res.get("messages", []))


_START_CACHE = []


def _starts(runner):
    """Start lemmas: Mathlib equations with a moderate left-hand side, scanned once and cached on disk."""
    if not _START_CACHE:
        lemmas = _lean()._BASE / "mathlib_eq_lemmas.tsv"
        if not lemmas.exists():
            _eval(runner, f'rcEqLemmas "{lemmas}"')
        for line in lemmas.read_text().splitlines():
            name, _, binders, depth = line.split("\t")
            if 2 <= int(depth) <= 12 and int(binders) <= 8 and not _AUTO.search(name):
                _START_CACHE.append(name)
    return _START_CACHE


_VIABLE_CACHE = {}  # starts that produced a walk: name -> steps reached, shared on disk by workers
_BUFFER = defaultdict(list)  # (steps, limits) -> finished walks, consumed one per example
_MAX_STEPS = 6  # walks always aim this far; a k-step example is a prefix of any walk of k or more steps
_BATCH = 16
_EMITTED = set()  # walks already turned into examples in this process
_USES = defaultdict(int)  # examples per start lemma in this process


def _viable_path():
    return _lean()._BASE / "mathlib_rewrite_viable.tsv"


def _viable():
    if not _VIABLE_CACHE and _viable_path().exists():
        for line in _viable_path().read_text().splitlines():
            name, _, steps = line.partition("\t")
            if steps.isdigit():  # another worker may be mid-append
                _VIABLE_CACHE[name] = max(int(steps), _VIABLE_CACHE.get(name, 0))
    return _VIABLE_CACHE


def _fill(runner, k, limits):
    """One REPL call runs a batch of walks as long as they go (up to _MAX_STEPS); each is buffered by length.

    Three quarters of the starts come from those known to produce walks of k steps, the rest explore the whole
    lemma list, so the start distribution keeps growing while failed starts stop dominating the cost."""
    viable = [n for n, s in _viable().items() if s >= k and _USES[n] < 4]
    reuse = 0.75 * min(1.0, len(viable) / 2000)  # reuse only pays off once it cannot narrow the distribution
    starts = _starts(runner)
    names = [random.choice(viable) if viable and random.random() < reuse else random.choice(starts) for _ in range(_BATCH)]
    lems = ", ".join(f"`{n}" for n in names)
    max_len, heartbeats, walk_ms, call_timeout = limits
    out = _eval(runner, f"IO.println (← rcBatch #[{lems}] {_MAX_STEPS} {random.getrandbits(30)} {max_len} "
                        f"{1 + _MAX_STEPS // 3} {heartbeats} {walk_ms})", call_timeout)
    try:
        walks = json.loads(out)
    except json.JSONDecodeError:
        return
    found = []
    for walk in walks:
        j = len(walk.get("steps", []))
        if "error" in walk or j == 0:
            continue
        sig = (walk["start"], tuple(walk["terms"]))
        if sig not in _EMITTED and len(_BUFFER[(j, limits)]) < 256:
            _EMITTED.add(sig)
            _BUFFER[(j, limits)].append(walk)
        if _viable().get(walk["start"], 0) < j:
            _VIABLE_CACHE[walk["start"]] = j
            found.append(f"{walk['start']}\t{j}\n")
    if found:
        with open(_viable_path(), "a") as f:  # shared by workers: small appends, read once per process
            f.writelines(found)


@dataclass
class MathlibRewriteConfig(Config):
    steps: float = 1.0
    glossary: bool = True  # list lemma statements, with distractors; off: names only, for models that know Mathlib
    distractors: float = 1.0  # distractor lemmas in the glossary per step: fixed, so the glossary grows only with steps
    max_len: int = 160

    def apply_difficulty(self, level):
        self.steps = min(float(_MAX_STEPS), self.steps + 0.4 * level)


_POOL = {}  # lemma -> statement, from every walk seen in this process: fallback distractors


def _body(stmt):
    """A statement without its leading ∀ binders: aliases such as `Nat.add_comm` and `add_comm` share it."""
    depth = 0
    for i, c in enumerate(stmt):
        depth += (c in "([{⦃") - (c in ")]}⦄")
        if depth == 0 and stmt.startswith(", ", i):
            return stmt[i + 2:] if stmt.startswith("∀") else stmt
    return stmt


def _glossary(walk, n):
    """The lemmas the walk uses plus n distractors, preferring other lemmas that also rewrote the walk's terms.
    A distractor never restates an equation already listed, and long statements are skipped."""
    used = {s["lemma"]: s["statement"] for s in walk["steps"]}
    alts = {a["lemma"]: a["statement"] for s in walk["steps"] for a in s.get("alts", []) if a["lemma"] not in used}
    _POOL.update(used)
    _POOL.update(alts)
    bodies = {_body(" ".join(x.split())) for x in used.values()}
    picks = {}
    rest = sorted(_POOL.keys() - used.keys() - alts.keys())
    candidates = random.sample(sorted(alts), len(alts)) + random.sample(rest, min(4 * n, len(rest)))
    for name in candidates:
        body = _body(" ".join(_POOL[name].split()))
        if len(picks) < n and name not in picks and body not in bodies and len(body) <= 120:
            picks[name] = _POOL[name]
            bodies.add(body)
    return [[name, stmt] for name, stmt in sorted({**used, **picks}.items())]  # JSON-safe pairs


class MathlibRewrite(DevTask):
    summary = "Apply a given sequence of Mathlib rewrite lemmas (rw) to a term and give the resulting term, as Lean prints it."
    config_cls = MathlibRewriteConfig
    task_version = 4
    middle = False  # ask for an intermediate term, given the final one
    preferred_batch_size = 64  # one process pays ~40 s of Lean startup, and each Lean call yields many walks
    heartbeats = 50000  # per walk, in thousands: a walk that runs out is dropped, not its batch
    walk_ms = 0  # per-walk time limit after which a walk stops extending (0: none)
    call_timeout = None  # seconds for one Lean call of _BATCH walks (None: the runner's 360 s)

    def __init__(self, config=None, **kwargs):
        super().__init__(config=config or MathlibRewriteConfig(), timeout=300, **kwargs)

    def prepare(self):
        runner = _lean().get_runner(use_mathlib=True)
        _walk_env(runner)
        _starts(runner)

    def generate_entry(self):
        if not _lean()._profile_ready(use_mathlib=True):
            raise RuntimeError("mathlib_rewrite needs the Lean + Mathlib install (see math_lean.ensure_lean_mathlib)")
        runner = _lean().get_runner(use_mathlib=True)
        k = max(2 if self.middle else 1, stochastic_rounding(self.config.steps))
        limits = (self.config.max_len, self.heartbeats, self.walk_ms, self.call_timeout)
        for attempt in range(9):
            # the shortest buffered walk that is long enough, so long walks stay available for long requests
            fits = [j for j in range(k, _MAX_STEPS + 1) if _BUFFER[(j, limits)]]
            if fits or attempt == 8:
                break
            _fill(runner, k, limits)
        if not fits:
            raise RuntimeError(f"mathlib_rewrite: no walk of {k}+ steps after 8 batches")
        bucket = _BUFFER[(fits[0], limits)]
        walk = bucket.pop(random.randrange(len(bucket)))
        walk = {**walk, "steps": walk["steps"][:k], "terms": walk["terms"][:k + 1]}
        _USES[walk["start"]] += 1
        ask = random.randrange(1, k) if self.middle else k
        glossary = _glossary(walk, stochastic_rounding(self.config.distractors * k)) if self.config.glossary else []
        meta = {"start_lemma": walk["start"], "universes": walk["universes"], "context": walk["context"], "start": walk["terms"][0],
                "steps": [{"lemma": s["lemma"], "symm": s["symm"]} for s in walk["steps"]], "glossary": glossary,
                "terms": walk["terms"], "ask": ask}
        return Entry(metadata=meta, answer=walk["terms"][ask])

    def render_prompt(self, m):
        universes = f"universe {' '.join(m['universes'])}\n" if m["universes"] else ""
        ctx = universes + ("variable " + " ".join(m["context"]) if m["context"] else "(no variables)")
        steps = "\n".join(f"  {i + 1}. {'← ' if s['symm'] else ''}{s['lemma']}" for i, s in enumerate(m["steps"]))
        glossary = "".join(f"  {name} : {' '.join(stmt.split())}\n" for name, stmt in m["glossary"])
        if glossary:
            glossary = f"Statements of the lemmas involved (some are not used):\n{glossary}"
        start = " ".join(m["start"].split())
        k, ask = len(m["steps"]), m.get("ask", len(m["steps"]))
        if ask == k:
            question = "What is the resulting term?"
        else:
            final = " ".join(m["terms"][-1].split())
            question = f"The final term is\n  {final}\nWhat is the term right after rewrite {ask}?"
        return (f"In Lean 4 with Mathlib, with\n{ctx}\n{glossary}"
                f"start from the term\n  {start}\n"
                f"and rewrite it successively (rw) with these Mathlib lemmas (← means right-to-left):\n{steps}\n"
                "Each rewrite replaces the unique instance of the lemma's left-hand side (right-hand side for ←) "
                "occurring in the current term.\n"
                "Bound variables are named by nesting depth: x₁ for the outermost binder, x₂ inside it, and so on.\n"
                f"{question} Answer with the term only, as Lean would print it.")

    def score_answer(self, answer, entry):
        return score_term(answer, entry)

    def distractor_candidates(self, entry):
        """The walk's other terms: stopping early, going one step too far, or not rewriting at all."""
        terms, ask = entry["metadata"]["terms"], entry["metadata"]["ask"]
        return [t for i, t in enumerate(terms) if i != ask]


@dataclass
class MathlibRewriteMiddleConfig(MathlibRewriteConfig):
    steps: float = 2.0


class MathlibRewriteMiddle(MathlibRewrite):
    """The same walks, read both ways: given the start and the final term, give an intermediate one."""
    summary = ("Given a start term, a sequence of Mathlib rewrite lemmas (rw) and the final term, "
               "give the term after a given intermediate step, as Lean prints it.")
    config_cls = MathlibRewriteMiddleConfig
    middle = True

    def __init__(self, config=None, **kwargs):
        super().__init__(config=config or MathlibRewriteMiddleConfig(), **kwargs)


class MathlibRewriteMiddleFast(MathlibRewriteMiddle):
    """`mathlib_rewrite_middle` with tight per-walk limits. Walks that end in an error or exception took 65%
    of Lean time (one took 98 s), and short limits stop them early at the cost of some long walks."""
    summary = ("Given a start term, a sequence of Mathlib rewrite lemmas (rw) and the final term, give the term "
               "after a given intermediate step, as Lean prints it; walks generated under tight time limits.")
    heartbeats = 20000
    walk_ms = 5000
    call_timeout = 90  # healthy calls take under 25 s; a rare Lean operation ignores heartbeats and stalls


# Answer normalization: parse both terms with Lean's precedences for the notation walks produce and compare
# trees, so spacing and redundant parentheses do not matter (coercion arrows do). Anything outside that fragment falls back to
# comparing whitespace-normalized strings, so two different terms are never merged.
_INFIX = {  # token: (precedence, associativity), as declared in Lean core / Mathlib
    "+": (65, "l"), "-": (65, "l"), "*": (70, "l"), "/": (70, "l"), "%": (70, "l"), "^": (75, "r"),
    "•": (73, "r"), "∪": (65, "l"), "∩": (70, "l"), "\\": (70, "l"), "⊔": (68, "l"), "⊓": (69, "l"),
    "⇨": (60, "r"), "∘": (90, "r"), "⁻¹'": (80, "l"), "''": (80, "l"), "++": (65, "l"), "::": (67, "r"),
    "+ᵥ": (65, "r"), "-ᵥ": (65, "l"), "×ˢ": (82, "r"),
    "=": (50, "n"), "≠": (50, "n"), "≤": (50, "n"), "<": (50, "n"), "∈": (50, "n"), "⊆": (50, "n"), "∣": (50, "n"),
}
_BINDER = {"∑": 67, "∏": 67, "⋃": 60, "⋂": 60, "⨆": 60, "⨅": 60, "fun": 0, "λ": 0}  # body precedence
_PAIRS = {"(": ")", "{": "}", "[": "]", "⟨": "⟩", "⁅": "⁆", "‖": "‖", "|": "|"}
_COERCE = {"↑", "⇑", "↥"}
_OPCH = r"+\-*/%^•∪∩\\⊔⊓⇨∘=≠≤<>∈⊆∣¬￢↑⇑↥∑∏⋃⋂⨆⨅λ"
_TOKEN = re.compile(rf"(\s*)(⁻¹'|''|=>|↦|\+\+|::|:=|//|\+ᵥ|-ᵥ|×ˢ|[()\[\]{{}}⟨⟩⁅⁆‖|,:]|[{_OPCH}]|[^\s()\[\]{{}}⟨⟩⁅⁆‖|,:{_OPCH}]+)")
_POSTFIX = re.compile(r"^(.*?)((?:ᶜ|⁻¹|⁺)*)$")
# identifiers, numerals and constant symbols; any other word may be notation with unknown precedence
_WORD = re.compile(r"(?:[\w.'!?⊥⊤∅∞]|ᶜ|⁻¹|⁺)+")
_KEYWORDS = {"if", "then", "else", "match", "with", "let", "have", "show", "by", "do", "at", "fun₀"}


class _Unsupported(Exception):
    pass


class _Parser:
    def __init__(self, text):
        self.toks, pos = [], 0
        while pos < len(text.rstrip()):
            m = _TOKEN.match(text, pos)
            if not m:
                raise _Unsupported(text[pos:])
            tok, spaced = m.group(2), bool(m.group(1)) or not self.toks
            if self.toks and not spaced and re.match(rf"[{_OPCH}]", self.toks[-1][0]) and unicodedata.category(tok[0]) in ("Lm", "No"):
                raise _Unsupported(self.toks[-1][0] + tok)  # a decorated operator such as -ᵥ or ∏ᶠ
            self.toks.append((tok, spaced))  # (token, preceded by space)
            pos = m.end()
        self.i, self.closers = 0, []

    def peek(self):
        return self.toks[self.i][0] if self.i < len(self.toks) else None

    def take(self, want=None):
        tok = self.peek()
        if tok is None or (want is not None and tok != want):
            raise _Unsupported(f"expected {want}, got {tok}")
        self.i += 1
        return tok

    def starts_arg(self):
        tok = self.peek()
        if tok is None or tok in self.closers[-1:] or tok in (")", "}", "]", "⟩", "⁆", ",", ":", "=>", "↦", ":=", "//"):
            return False
        return tok in _PAIRS or tok in _COERCE or tok in _BINDER or not (tok in _INFIX or re.match(rf"[{_OPCH}]", tok))

    def expr(self, min_prec=0):
        lhs = self.prefix()
        while (op := self.peek()) in _INFIX and _INFIX[op][0] >= min_prec:
            prec, assoc = _INFIX[self.take()]
            rhs = self.expr(prec if assoc == "r" else prec + 1)
            if assoc == "n" and self.peek() in _INFIX and _INFIX[self.peek()][0] == prec:
                raise _Unsupported("chained non-associative operator")
            lhs = (op, lhs, rhs)
        return lhs

    def prefix(self):
        tok = self.peek()
        if tok == "-":
            self.take()
            return ("neg", self.expr(75))
        if tok == "¬":
            self.take()
            return ("not", self.expr(40))
        if tok in _BINDER:
            return self.binder()
        head = self.atom()
        args = []
        while self.starts_arg():
            args.append(self.binder() if self.peek() in _BINDER else self.atom())
        return ("app", head, *args) if args else head

    def binder(self):
        kind, header, depth = self.take(), [], 0
        end = ("=>", "↦") if kind in ("fun", "λ") else (",",)
        while not (depth == 0 and self.peek() in end):
            tok = self.take()
            depth += (tok in "([{⟨") - (tok in ")]}⟩")
            header.append(tok)
        self.take()
        return (kind, _canon(" ".join(header)), self.expr(_BINDER[kind]))

    def atom(self):
        tok = self.take()
        if tok in _COERCE:  # where a coercion sits changes the term: ↑a / ↑b is not ↑(a / b)
            return (tok, self.atom())
        if tok in _PAIRS:
            close = _PAIRS[tok]
            self.closers.append(close)
            items = [self.expr()]
            if tok == "(" and self.peek() == ":":  # type ascription, as in binders (_ : x ∈ s)
                self.take()
                items = [(":", items[0], self.expr())]
            while self.peek() == ",":
                self.take()
                items.append(self.expr())
            self.take(close)
            self.closers.pop()
            node = items[0] if tok == "(" and len(items) == 1 else (tok, *items)
        elif tok in _INFIX or tok in (")", "}", "]", "⟩", "⁆", ",", ":", "=>", "↦", ":=", "//"):
            raise _Unsupported(tok)
        else:
            if not _WORD.fullmatch(tok) or tok in _KEYWORDS:
                raise _Unsupported(tok)
            base, post = _POSTFIX.match(tok).groups()
            node = base or post
            if base:
                tok = post
            else:
                tok, node = "", None
                raise _Unsupported(f"dangling postfix {post}")
            for p in re.findall(r"ᶜ|⁻¹|⁺", tok):
                node = (p, node)
        while self.i < len(self.toks) and not self.toks[self.i][1] and re.match(r"ᶜ|⁻¹(?!')|⁺|\.", self.peek()):
            suffix = self.take()  # postfix operators and field projections glued to a closing bracket
            base, post = _POSTFIX.match(suffix).groups()
            if base:
                node = ("proj", node, base)
            for p in re.findall(r"ᶜ|⁻¹|⁺", post):
                node = (p, node)
        return node


def _flat(text):
    t = str(text).strip().strip("`$").strip()
    t = re.sub(r"^lean\s*\n", "", t)
    return " ".join(t.replace("↦", "=>").replace("λ ", "fun ").split())


def _canon(text):
    """Parse tree of a printed term, or its whitespace-normalized text outside the supported notation."""
    t = _flat(text)
    try:
        parser = _Parser(t)
        tree = parser.expr()
        if parser.peek() is not None:
            raise _Unsupported(parser.peek())
        return tree
    except (_Unsupported, RecursionError):
        return t


def score_term(answer, entry):
    """Pure-Python match of a term against Lean's printed answer, up to spacing and redundant parentheses.
    No Lean at scoring time; generation already checked that the gold round-trips."""
    gold = str(entry["answer"])
    if not any(c in gold for c in _COERCE):  # the gold has no coercions, so arrows in the answer are spurious
        answer = "".join(c for c in str(answer) if c not in _COERCE)
    return float(_canon(answer) == _canon(gold))

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

ATOMS = ("N", "NP", "S")

LEXICON = {
    "a": "(NP/N)",
    "the": "(NP/N)",
    "an": "(NP/N)",
    "no": "(NP/N)",
    "every": "(NP/N)",
    "red": "(N/N)",
    "quick": "(N/N)",
    "big": "(N/N)",
    "small": "(N/N)",
    "lazy": "(N/N)",
    "fish": "N",
    "cat": "N",
    "snake": "N",
    "fox": "N",
    "dog": "N",
    "bird": "N",
    "mouse": "N",
    "whale": "N",
    "police": "NP",
    "kid": "NP",
    "hen": "NP",
    "tiger": "NP",
    "crow": "NP",
    "sings": "(S\\NP)",
    "dances": "(S\\NP)",
    "swims": "(S\\NP)",
    "runs": "(S\\NP)",
    "jumps": "(S\\NP)",
    "sleeps": "(S\\NP)",
}

WORDS_BY_CAT = {}
for _w, _c in LEXICON.items():
    WORDS_BY_CAT.setdefault(_c, []).append(_w)
ALL_CATS = sorted(WORDS_BY_CAT)


def is_atom(c):
    return c in ATOMS


def _functor(c):
    if len(c) >= 5 and c[0] == "(" and c[-1] == ")":
        inner = c[1:-1]
        depth = 0
        for i, ch in enumerate(inner):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch in "/\\" and depth == 0:
                a, x = inner[:i], inner[i + 1:]
                if x in ATOMS:
                    return a, ch, x
    return None


def fwd(a, x):
    return f"({a}/{x})"


def bwd(a, x):
    return f"({a}\\{x})"


def combine(left, right):
    f = _functor(left)
    g = _functor(right)
    if f is not None and f[2] == right:
        return f[0]
    if g is not None and g[2] == left:
        return g[0]
    if f is not None and g is not None:
        if f[2] == g[0] and g[1] == "/":
            return fwd(f[0], g[2])
        if f[2] == g[0] and g[1] == "\\":
            return bwd(f[0], g[2])
    return None


def reduce_all(cats):
    states = {tuple(cats)}
    for _ in range(12):
        if len(states) == 1 and len(next(iter(states))) == 1:
            return next(iter(states))[0]
        if any(len(s) == 1 for s in states):
            for s in states:
                if len(s) == 1:
                    return s[0]
        ns = set()
        for s in states:
            for i in range(len(s) - 1):
                r = combine(s[i], s[i + 1])
                if r is not None:
                    ns.add(s[:i] + (r,) + s[i + 2:])
        if not ns:
            return None
        states = ns
    return None


_CACHE = {}


def build(cat, n):
    """List of n lexical category strings reducing exactly to cat, or None."""
    key = (cat, n)
    if key in _CACHE:
        return _CACHE[key]
    res = _build(cat, n)
    _CACHE[key] = res
    return res


def _build(cat, n):
    if n == 1:
        return [cat] if cat in WORDS_BY_CAT else None
    args = list(ATOMS)
    random.shuffle(args)
    for arg in args:
        for split in range(1, n):
            l, r = split, n - split
            lc = build(fwd(cat, arg), l)
            if lc is None:
                continue
            rc = build(arg, r)
            if rc is None:
                continue
            seq = lc + rc
            if reduce_all(seq) == cat:
                return seq
            break
        for split in range(1, n):
            l, r = split, n - split
            lc = build(arg, l)
            if lc is None:
                continue
            rc = build(bwd(cat, arg), r)
            if rc is None:
                continue
            seq = lc + rc
            if reduce_all(seq) == cat:
                return seq
            break
    fx = _functor(cat)
    if fx is not None:
        a, _, _ = fx
        for x in args:
            if x == a:
                continue
            for split in range(1, n):
                l, r = split, n - split
                lc = build(fwd(a, x), l)
                if lc is None:
                    continue
                rc = build(fwd(x, fx[2]), r)
                if rc is None:
                    continue
                seq = lc + rc
                if reduce_all(seq) == cat:
                    return seq
                break
            for split in range(1, n):
                l, r = split, n - split
                lc = build(bwd(x, a), l)
                if lc is None:
                    continue
                rc = build(bwd(x, fx[2]), r)
                if rc is None:
                    continue
                seq = lc + rc
                if reduce_all(seq) == cat:
                    return seq
                break
    return None


@dataclass
class CcgCategoryCombinationV1Config(Config):
    seq_len: int = 3

    def apply_difficulty(self, level):
        self.seq_len = 3 + min(level, 4)


def buildable_atoms(n):
    return [a for a in ATOMS if build(a, n) is not None]


def generate_entry_for(n):
    buildable = buildable_atoms(n)
    if len(buildable) < 2:
        raise RuntimeError(f"not enough buildable atoms at length {n}: {buildable}")
    target = random.choice(buildable)
    seq = build(target, n)
    if seq is None or reduce_all(seq) != target:
        raise RuntimeError("unexpected build failure")
    words = [random.choice(WORDS_BY_CAT[c]) for c in seq]
    assert reduce_all(seq) == target
    assert seq == [LEXICON[w] for w in words]
    return target, words, seq


TASK_META = {
    "parent_source_id": None,
    "idea": "ccg_category_combination (variant 1 of 3)",
    "hypothesis": "P007",
    "changes": "new task in "
    "reasoning_core/tasks/generated/k3_formal_semantics_r4/ccg_category_combination",
    "generation": {
        "provider_name": "albert",
        "model_name": "deepseek-v4-flash",
        "harness_name": "opencode",
        "harness_version": "1.18.31",
        "agent_name": "task-search-worker",
        "settings": {"variant": None,
                     "requested_seed": 1139467751,
                     "seed_forwarded": True,
                     "temperature": None,
                     "top_p": None,
                     "pure": True,
                     "max_steps": 56,
                     "timeout_seconds": 1800,
                     "sandbox": {"name": "bubblewrap",
                                 "version": "bubblewrap 0.8.0"}}},
}


class CcgCategoryCombination(Task):
    summary = (
        "Combine CCG slash categories along a token sequence via forward/backward "
        "application and composition from a small nuclear-lexicon; answers are the "
        "fully reduced atom category for the whole sequence."
    )
    design_choice = (
        "Answer format: output the fully reduced category string for the whole "
        "sequence, with no rule names or intermediate steps."
    )
    config_cls = CcgCategoryCombinationV1Config
    task_version = 2

    def generate_entry(self):
        n = self.config.seq_len
        target, words, _seq = generate_entry_for(n)
        return Entry(metadata={"words": words}, answer=target)

    def render_prompt(self, metadata):
        return _render(metadata["words"])

    def score_answer(self, answer, entry=None):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip()
        if entry is None:
            return 0.0
        gold = entry["answer"]
        return 1.0 if a == gold else 0.0


def _render(words):
    seq = " ".join(words)
    return (
        "In Combinatory Categorial Grammar each word carries a slash category and "
        "adjacent categories combine by functional application or composition into "
        "a single category. Lexicon: a,the,an,no,every -> (NP/N); red,quick,big,"
        "small,lazy -> (N/N); fish,cat,snake,fox,dog,bird,mouse,whale -> N; "
        "police,kid,hen,tiger,crow -> NP; sings,dances,swims,runs,jumps,sleeps -> "
        "(S\\NP). "
        f"Fully combine the categories of the sequence '{seq}' into one atom. "
        "Give only the final category, e.g. 'S' or 'NP'."
    )

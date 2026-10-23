"""Generic hard negatives for any task row: no per-task code, every candidate checked by the task's verifier.

A source maps (gold, prompt, pool) to candidate answers; `negatives` draws from a policy's sources,
dedups, drops anything the task itself scores as correct, and tops up from the pool at random.

    spans   tokens of the prompt with the gold's shape (the entity, number or label a shallow reader picks)
    shape   pool answers with the gold's shape ("E3" -> "A9", "Alice" -> "Aa", "3/4" -> "9/9")
    mutate  the gold with one number nudged, two tokens swapped or one token dropped
    lexical pool answers nearest the gold by character trigrams
    random  pool answers, uniformly
"""
import itertools
import random
import re

from .intrinsic import _cpu_limit

TOKEN = re.compile(r"[\w./+-]+")
POLICIES = {"random": ("random",), "hard": ("spans", "shape", "mutate", "lexical")}


def shape(text):
    text = re.sub(r"[A-Z]+", "A", str(text).strip())
    return re.sub(r"\d+", "9", re.sub(r"[a-z]+", "a", text))


def _trigrams(text):
    text = f"  {text.lower()} "
    return {text[i:i + 3] for i in range(len(text) - 2)}


def spans(gold, prompt, pool, rng):
    """Prompt tokens shaped like the gold; those that are also answers elsewhere in the task come first."""
    want, known = shape(gold), set(pool)
    toks = [t for t in dict.fromkeys(TOKEN.findall(prompt)) if shape(t) == want]
    return [t for t in toks if t in known] or toks


def shape_matched(gold, prompt, pool, rng):
    want = shape(gold)
    return [a for a in pool if shape(a) == want]


def mutate(gold, prompt, pool, rng):
    out, nums = [], list(re.finditer(r"-?\d+", gold))
    for m in nums:
        n = int(m.group())
        out += [gold[:m.start()] + str(v) + gold[m.end():] for v in (n + 1, n - 1, 2 * n) if v != n]
    toks = gold.split()
    if len(toks) >= 2:
        i, j = rng.sample(range(len(toks)), 2)
        toks[i], toks[j] = toks[j], toks[i]
        out.append(" ".join(toks))
    if len(gold.split()) >= 3:
        out.append(" ".join(t for k, t in enumerate(gold.split()) if k != rng.randrange(len(gold.split()))))
    return out


def lexical(gold, prompt, pool, rng, top=30):
    g = _trigrams(gold)
    return sorted(pool, key=lambda a: -len(g & _trigrams(a)) / (len(g | _trigrams(a)) or 1))[:top]


SOURCES = {"spans": spans, "shape": shape_matched, "mutate": mutate, "lexical": lexical,
           "random": lambda gold, prompt, pool, rng: list(pool)}


_WARM = set()


def is_wrong(candidate, row, seconds=2, first=120):
    """True only when the task's own scorer rejects the candidate; a crash or a timeout is not proof.
    A task's first call gets `first` seconds: scorers import lazily (~10 s), and a cap that cuts the
    import short makes every later call re-import and time out too."""
    from reasoning_core.registry import score_answer
    cap = seconds if row["task"] in _WARM else first
    _WARM.add(row["task"])
    try:
        with _cpu_limit(cap):
            return score_answer(candidate, row) < 1
    except Exception:                   # includes _ScoreTimeout
        return False


def negatives(row, pool, k, policy="hard", seed=0, verify=True):
    """Up to `k` verified-wrong answers for `row`; `pool` = other answers of its task and level.
    Sources are interleaved round-robin (each shuffled), then the pool at random fills any gap."""
    rng, gold = random.Random(seed), str(row["answer"])
    pool = [a for a in pool if a != gold]
    lists = []
    for name in POLICIES[policy]:
        cands = SOURCES[name](gold, row["prompt"], pool, rng)
        rng.shuffle(cands)
        lists.append(cands)
    order = itertools.chain((c for group in itertools.zip_longest(*lists) for c in group if c is not None),
                            rng.sample(pool, len(pool)))
    seen, out = {gold}, []
    for c in order:
        if len(out) == k:
            break
        if c not in seen and c.strip():
            seen.add(c)
            if not verify or is_wrong(c, row):
                out.append(c)
    return out

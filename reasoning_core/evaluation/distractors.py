"""Generic hard negatives: other answers of the same task and level, ranked by similarity to the gold.

No per-task or per-format rule: every candidate is a real answer the task produced elsewhere, so it is
in-format; a policy only reorders the pool, and the task's own scorer drops anything it accepts.

    difflib the builder's composite (`Task._distractor_similarity`, as in procedural-choices); hardest of
            char n-grams, BM25, static embeddings and learned encoders under four judges (2026-10-23)
    char    cosine of character n-gram counts
    embed   cosine of static word embeddings, bekko-static-embedding-v1
    random  uniform

Grounding (as in build_procedural_choices): when every word of the gold is in the prompt, so must every
word of a negative, or it is eliminated without solving.
"""
import collections
import functools
import itertools
import random
import re

import numpy as np

from .intrinsic import _cpu_limit

EMBED = ("hotchpotch/bekko-static-embedding-v1", "c18167b8f244c1bc6de21ce9b710bac8a29c4615")
POLICIES = {"random": ("random",), "difflib": ("difflib",), "hard": ("char", "embed")}


def _ngrams(text, n=(2, 3, 4)):
    text = f" {text.lower()} "
    return collections.Counter(text[i:i + k] for k in n for i in range(len(text) - k + 1))


def char(gold, pool):
    g = _ngrams(gold)
    gn = sum(v * v for v in g.values()) ** .5 or 1

    def cos(a):
        a = _ngrams(a)
        return sum(g[k] * v for k, v in a.items()) / (gn * (sum(v * v for v in a.values()) ** .5 or 1))
    return sorted(pool, key=cos, reverse=True)


@functools.lru_cache(1)
def _static(dim=256):
    """(tokenizer, table): a static embedding is a token table; a text is the mean of its tokens' rows."""
    from huggingface_hub import hf_hub_download
    from safetensors.numpy import load_file
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(hf_hub_download(EMBED[0], "tokenizer.json", revision=EMBED[1]))
    table = next(iter(load_file(hf_hub_download(EMBED[0], "model.safetensors", revision=EMBED[1])).values()))
    return tok, np.asarray(table[:, :dim], dtype=np.float32)          # Matryoshka: a prefix is a model


def _embed(texts):
    tok, table = _static()
    out = np.stack([table[e.ids].mean(0) if e.ids else np.zeros(table.shape[1], np.float32)
                    for e in tok.encode_batch(list(texts), add_special_tokens=False)])
    return out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-9)


def embed(gold, pool):
    if not pool:
        return []
    e = _embed([gold, *pool])
    return [pool[i] for i in np.argsort(-(e[1:] @ e[0]), kind="stable")]


def difflib(gold, pool):
    from reasoning_core.template import Task
    return sorted(pool, key=lambda c: -Task._distractor_similarity(c[:300], gold[:300]))


def _words(text):
    return set(re.findall(r"\w+", str(text).lower()))


SOURCES = {"difflib": difflib, "char": char, "embed": embed, "random": lambda gold, pool: list(pool)}
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


def negatives(row, pool, k, policy="difflib", seed=0, verify=True):
    """Up to `k` verified-wrong answers for `row`; `pool` = other answers of its task and level.
    Sources' rankings are interleaved round-robin, then the pool at random fills any gap."""
    rng, gold = random.Random(seed), str(row["answer"])
    pool = [a for a in pool if a != gold and a.strip()]
    if _words(gold) <= _words(row["prompt"]):
        pool = [a for a in pool if _words(a) <= _words(row["prompt"])]
    rng.shuffle(pool)                   # ties break at random, not alphabetically
    lists = [SOURCES[name](gold, pool) for name in POLICIES[policy]]
    order = itertools.chain((c for group in zip(*lists) for c in group), rng.sample(pool, len(pool)))
    seen, out = {gold}, []
    for c in order:
        if len(out) == k:
            break
        if c not in seen:
            seen.add(c)
            if not verify or is_wrong(c, row):
                out.append(c)
    return out

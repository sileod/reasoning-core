import random
from collections import Counter

TASK_META = {'parent_source_id': None,
 'idea': 'iterated_integral_shuffle_expansion (variant 1 of 3)',
 'hypothesis': 'P012',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_compositional_generalization_r4/iterated_integral_shuffle_expansion',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1277236794,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

ALPHABET = "abcdefgh"


def shuffle_two(a, b):
    """Shuffle product of two words (as lists of letters), with multiplicity.

    The shuffle product u * v is the sum over all interleavings that preserve the
    internal order of each word; the coefficient of a resulting word counts the
    number of such interleavings.
    """
    a = list(a)
    b = list(b)
    memo = {}

    def go(i, j):
        key = (i, j)
        if key in memo:
            return memo[key]
        if i == len(a) and j == len(b):
            res = Counter({(): 1})
        else:
            res = Counter()
            if i < len(a):
                for w, c in go(i + 1, j).items():
                    res[(a[i],) + w] += c
            if j < len(b):
                for w, c in go(i, j + 1).items():
                    res[(b[j],) + w] += c
        memo[key] = res
        return res

    return go(0, 0)


def expand_product(words):
    """Expand the (associative, commutative) shuffle product of the factor words."""
    acc = Counter({(): 1})
    for w in words:
        acc = _shuffle_multiset(acc, w)
    return acc


def _shuffle_multiset(acc, b):
    out = Counter()
    for wa, c1 in acc.items():
        for w2, c2 in shuffle_two(list(wa), list(b)).items():
            out[w2] += c1 * c2
    return out


def canonical_answer(counter):
    terms = sorted(counter.items(), key=lambda kv: kv[0])
    parts = []
    for w, c in terms:
        s = "".join(w)
        if c == 1:
            parts.append(s)
        else:
            parts.append(str(c) + "*" + s)
    return " + ".join(parts)


def parse_answer(text):
    out = Counter()
    for raw in text.split("+"):
        term = raw.strip()
        if not term:
            continue
        if "*" in term:
            c, s = term.split("*")
            c = int(c.strip())
            s = s.strip()
        else:
            c = 1
            s = term
        out[tuple(s)] += c
    return out


def _render_product(words):
    return " * ".join("(" + "".join(w) + ")" for w in words)


from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class ShuffleConfig(Config):
    n_factors: int = 2
    min_len: int = 1
    max_len: int = 1

    def apply_difficulty(self, level):
        self.min_len = 1
        self.max_len = min(1 + level, 3)
        self.n_factors = 2 if level < 3 else 3


class IteratedIntegralShuffleExpansion(Task):
    summary = ("Expand products of iterated integrals by interleaving ordered "
               "integration words while retaining multiplicities over repeated "
               "letters and nested factors, returning the collected expansion as "
               "a canonical lexicographically-sorted integer-coefficient sum.")
    design_choice = ("Return the expansion as a canonical sum of distinct words "
                     "with integer coefficients, sorted lexicographically, with "
                     "like terms collected.")
    config_cls = ShuffleConfig

    def generate_entry(self):
        while True:
            words = []
            for _ in range(self.config.n_factors):
                ln = random.randint(self.config.min_len, self.config.max_len)
                words.append(tuple(random.choice(ALPHABET) for _ in range(ln)))
            counter = expand_product(words)
            if not counter:
                continue
            answer = canonical_answer(counter)
            metadata = {
                "factors": [_render_product(words)],
                "words": [list(w) for w in words],
                "n_factors": self.config.n_factors,
                "min_len": self.config.min_len,
                "max_len": self.config.max_len,
                "terms": len(counter),
                "answer": answer,
            }
            return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        product = metadata["factors"][0]
        return (
            "The shuffle product of two integration words interleaves them (each "
            "letter keeps its relative position within its own word), keeping one "
            "term per distinct interleaving and accumulating a coefficient "
            "whenever several interleavings give the same word. It extends "
            "linearly and associatively to products of several words. For "
            "example, (ab)*(c) = abc + acb + cab.\n"
            f"Expand the product {product} of iterated integrals. Give the "
            "result as a sum of distinct words, like terms collected, sorted "
            "lexicographically, writing coefficient c as 'c*word' (omit the "
            "coefficient when it is 1) and joining terms with ' + '."
        )

    def score_answer(self, answer, entry):
        try:
            return 1.0 if parse_answer(answer) == parse_answer(entry.answer) else 0.0
        except Exception:
            return 0.0

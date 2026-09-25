import random
from dataclasses import dataclass

import numpy as np

from reasoning_core.template import Config, Entry, Task

VARS = ["A", "B", "C", "D"]

TASK_META = {'parent_source_id': None,
 'idea': 'universal_matrix_identity (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_global_over_greedy_r4/universal_matrix_identity',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _fstr(factor):
    if factor[0] == "v":
        return VARS[factor[1]]
    return "[%s,%s]" % (_fstr(factor[1]), _fstr(factor[2]))


def _wordstr(word):
    return "\u00b7".join(_fstr(f) for f in word)


def _termstr(coef, word):
    return "%d\u00b7tr(%s)" % (coef, _wordstr(word))


def _exprstr(terms):
    parts = []
    for coef, word in terms:
        t = _termstr(abs(coef), word)
        if not parts:
            parts.append(("-" if coef < 0 else "") + t)
        else:
            parts.append((" \u2212 " if coef < 0 else " + ") + t)
    return "".join(parts)


def _factor_matrix(factor, mats):
    if factor[0] == "v":
        return mats[factor[1]]
    a = _factor_matrix(factor[1], mats)
    b = _factor_matrix(factor[2], mats)
    return a @ b - b @ a


def _word_matrix(word, mats):
    m = _factor_matrix(word[0], mats)
    for f in word[1:]:
        m = m @ _factor_matrix(f, mats)
    return m


def _trace_word(word, mats):
    return int(_word_matrix(word, mats).trace())


def _make_factor(nvars, comm_p):
    if random.random() < comm_p:
        a = random.randrange(nvars)
        b = random.randrange(nvars)
        return ("c", ("v", a), ("v", b))
    return ("v", random.randrange(nvars))


def _make_word(nvars, max_word, comm_p):
    length = random.randint(2, max_word)
    return [_make_factor(nvars, comm_p) for _ in range(length)]


def _make_mats(nvars, dim):
    return [
        np.array(
            [[random.randint(-3, 3) for _ in range(dim)] for _ in range(dim)]
        )
        for _ in range(nvars)
    ]


@dataclass
class UniversalMatrixIdentityConfig(Config):
    max_vars: int = 2
    dim: int = 2
    max_word: int = 3
    blocks: int = 1
    comm_p: float = 0.3

    def apply_difficulty(self, level):
        self.max_vars = 2 + (level >= 2) + (level >= 5)
        self.dim = 2 + (level >= 3) + (level >= 6)
        self.max_word = 3 + level // 2
        self.blocks = 1 + level // 2
        self.comm_p = min(0.8, 0.3 + 0.1 * level)


class UniversalMatrixIdentity(Task):
    summary = "Decide whether expressions vanish under every matrix substitution of a stated dimension, combining commutators, products, alternating sums and trace factors, and answer identity or nonidentity."
    design_choice = "Instances present the expression as a fully parenthesized term with explicit coefficients and ask for a yes/no identity answer, with difficulty from the need to test noncommutative polynomial reduction."
    config_cls = UniversalMatrixIdentityConfig

    def generate_entry(self):
        cfg = self.config
        label = random.choice([0, 1])
        mats = _make_mats(cfg.max_vars, cfg.dim)

        if label == 0:
            terms = []
            for _ in range(cfg.blocks):
                word = _make_word(cfg.max_vars, cfg.max_word, cfg.comm_p)
                m = len(word)
                r = random.randrange(1, m)
                rotated = word[r:] + word[:r]
                assert _trace_word(word, mats) == _trace_word(rotated, mats)
                c = random.choice((-2, -1, 1, 2, 3))
                terms.append((c, word))
                terms.append((-c, rotated))
            total = sum(c * _trace_word(w, mats) for c, w in terms)
            assert total == 0, "identity construction must vanish"
        else:
            terms = None
            for _ in range(200):
                ts = []
                for _ in range(cfg.blocks):
                    c = random.choice((-3, -2, -1, 1, 2, 3))
                    ts.append((c, _make_word(cfg.max_vars, cfg.max_word, cfg.comm_p)))
                wmats = _make_mats(cfg.max_vars, cfg.dim)
                if sum(c * _trace_word(w, wmats) for c, w in ts) != 0:
                    terms = ts
                    break
            if terms is None:
                raise RuntimeError("could not build a certified nonidentity")

        random.shuffle(terms)
        answer = "identity" if label == 0 else "nonidentity"
        return Entry(
            metadata={
                "dim": cfg.dim,
                "nvars": cfg.max_vars,
                "max_word": cfg.max_word,
                "blocks": cfg.blocks,
                "label": int(label),
                "expr": _exprstr(terms),
            },
            answer=answer,
        )

    def render_prompt(self, m):
        d = m.dim
        return (
            "Let A, B, C, D denote matrices of size %d\u00d7%d over the complex numbers; "
            "each letter may be replaced by any %d\u00d7%d matrix. A commutator [X,Y] is "
            "the alternating sum X\u00b7Y \u2212 Y\u00b7X, and tr(Z) is the matrix trace. "
            "Multiplication is noncommutative matrix multiplication. The expression E below "
            "is a combination of trace terms with the shown integer coefficients. E is a "
            "universal identity if its value is zero for every replacement of the letters by "
            "%d\u00d7%d matrices. For example, tr(A\u00b7B) \u2212 tr(B\u00b7A) is a universal "
            "identity, while tr(A\u00b7A) is not. State whether E is a universal identity, "
            "answering with the single word identity or nonidentity.\n\n"
            "E = %s\n\n"
            "Determine whether E vanishes for every %d\u00d7%d substitution."
            % (d, d, d, d, d, d, m.expr, d, d)
        )

    def score_answer(self, answer, entry):
        return float(str(answer).strip().lower() == entry.answer)

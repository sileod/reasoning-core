import random

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'cyclic_trace_invariants (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_invariants_r4/cyclic_trace_invariants',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class CyclicTraceConfig(Config):
    length: int = 3
    distinct: int = 2

    def apply_difficulty(self, level):
        self.length = 3 + level
        self.distinct = 2 + level // 2


_SYMBOLS = ['A', 'B', 'C', 'D', 'E', 'F']


def _mat_mul(a, b):
    n = len(a)
    c = [[0] * n for _ in range(n)]
    for i in range(n):
        ci = c[i]
        for k in range(n):
            v = ai_k = a[i][k]
            if v == 0:
                continue
            bk = b[k]
            for j in range(n):
                ci[j] += v * bk[j]
    return c


def _trace(mat):
    return sum(mat[i][i] for i in range(len(mat)))


def _transpose(mat):
    n = len(mat)
    return [[mat[j][i] for j in range(n)] for i in range(n)]


def build_matrices(n, mode, rng):
    """Build concrete matrices for the n symbols according to mode."""
    mats = {}
    names = _SYMBOLS[:n]
    if mode == 0:
        for s in names:
            m = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    m[i][j] = rng.randint(-2, 2)
            mats[s] = m
    elif mode == 1:
        for s in names:
            m = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i, n):
                    v = rng.randint(-2, 2)
                    m[i][j] = v
                    m[j][i] = v
            mats[s] = m
    elif mode == 2:
        for s in names:
            m = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n):
                    v = rng.randint(-2, 2)
                    m[i][j] = v
                    m[j][i] = -v
            mats[s] = m
    else:
        pairs = n // 2 * 2
        half = pairs // 2
        for s in names[:half]:
            m = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    m[i][j] = rng.randint(-2, 2)
            mats[s] = m
            mats[s + 'T'] = _transpose(m)
        for s in names[half:]:
            m = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    m[i][j] = rng.randint(-2, 2)
            mats[s] = m
    return mats


def eval_word(word, mats):
    """word is a list of (symbol, op) where op in {'', 'T', 'X'}; returns trace."""
    sym, op = word[0]
    cur = mats[sym]
    if op == 'T':
        cur = _transpose(cur)
    elif op == 'X':
        cur = [[-cur[i][j] for j in range(len(cur))] for i in range(len(cur))]
    for (sym, op) in word[1:]:
        m = mats[sym]
        if op == 'T':
            m = _transpose(m)
        elif op == 'X':
            m = [[-m[i][j] for j in range(len(m))] for i in range(len(m))]
        cur = _mat_mul(cur, m)
    return _trace(cur)


def render_word(word):
    parts = []
    for sym, op in word:
        part = sym
        if op == 'T':
            part = sym + '^T'
        elif op == 'X':
            part = sym + '^X'
        parts.append(part)
    return parts


def _transposed(entry):
    if isinstance(entry, tuple):
        return entry[0], 'T'
    return entry


class CyclicTraceInvariants(Task):
    summary = ("Identify equalities among traces of arbitrary-size noncommuting matrix words using "
               "cyclicity and transpose laws; vary symmetric, skew, and paired-transpose factors; "
               "answer equality or a missing coefficient.")
    design_choice = ("Present each instance as two explicit matrix-word strings and ask whether "
                     "their traces are equal, with the answer restricted to 'yes' or 'no'.")
    config_cls = CyclicTraceConfig

    def generate_entry(self):
        cfg = self.config
        length = cfg.length
        n = cfg.distinct
        names = _SYMBOLS[:n]
        mode = random.randrange(4)

        mats = build_matrices(n, mode, random)

        attempts = 0
        while True:
            attempts += 1
            if attempts > 300:
                raise RuntimeError("could not construct a balanced instance")

            row = []
            for _ in range(length):
                s = random.choice(names)
                op = random.choice(('', 'T'))
                row.append((s, op))

            intent = random.choice(('yes', 'no'))

            if intent == 'yes':
                rep = random.choice(('rotate', 'transpose_reverse'))
                if rep == 'rotate':
                    word1 = row
                    k = random.randrange(1, length)
                    word2 = row[k:] + row[:k]
                else:
                    word1 = row
                    word2 = [_transposed(w) for w in reversed(row)]
            else:
                word1 = row
                word2 = list(row)
                idx = random.randrange(length)
                new_sym = random.choice([s for s in names if s != word1[idx][0]])
                word2[idx] = (new_sym, word2[idx][1])
                if random.random() < 0.4:
                    word2 = [_transposed(w) for w in word2]

            t1 = eval_word(word1, mats)
            t2 = eval_word(word2, mats)

            if intent == 'yes':
                if t1 != t2:
                    continue
                label = 'yes'
            else:
                if t1 == t2:
                    continue
                label = 'no'

            break

        word1_s = ' * '.join(render_word(word1))
        word2_s = ' * '.join(render_word(word2))

        metadata = {
            'mode': mode,
            'length': length,
            'distinct': n,
            'word1': word1_s,
            'word2': word2_s,
        }
        return Entry(metadata=metadata, answer=label)

    def render_prompt(self, metadata):
        return (
            "Working with square matrices over the reals, where matrix multiplication is NOT "
            "commutative: XY generally differs from YX. A superscript X denotes a skew-symmetric "
            "factor M with M = -M^T, and a superscript T denotes the matrix transpose. "
            "Two standard laws hold for any matrices M and N: trace(MN) = trace(NM) (cyclicity) "
            "and trace(M) = trace(M^T) (transpose invariance). "
            "Consider these two matrix words over the symbols {}:\n"
            "word 1: {}\n"
            "word 2: {}\n"
            "Are the traces of these two words equal? Answer exactly 'yes' or 'no'."
        ).format(', '.join(_SYMBOLS[:metadata['distinct']]),
                 metadata['word1'], metadata['word2'])

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        if answer == 'yes' and entry.answer == 'yes':
            return 1.0
        if answer == 'no' and entry.answer == 'no':
            return 1.0
        return 0.0

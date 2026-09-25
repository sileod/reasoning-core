import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'stabilizer_cut_entropy (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r4/stabilizer_cut_entropy',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _rank_gf2(rows):
    if not rows:
        return 0
    m = len(rows)
    n = len(rows[0])
    mat = [list(r) for r in rows]
    r = 0
    for c in range(n):
        pivot = None
        for i in range(r, m):
            if mat[i][c]:
                pivot = i
                break
        if pivot is None:
            continue
        mat[r], mat[pivot] = mat[pivot], mat[r]
        for i in range(m):
            if i != r and mat[i][c]:
                for j in range(c, n):
                    mat[i][j] ^= mat[r][j]
        r += 1
        if r == m:
            break
    return r


def _norm_fraction(s):
    try:
        f = Fraction(s)
    except Exception:
        return None
    return (f.numerator, f.denominator)


@dataclass
class CutEntropyConfig(Config):
    qubits: int = 3
    max_generators: int = 3

    def apply_difficulty(self, level):
        self.qubits = 4 + level
        self.max_generators = 3 + level


class StabilizerCutEntropy(Task):
    summary = ("Commuting independent Pauli generators, mixed X/Y/Z/I words (recombinations), "
               "and varied subsystem cuts; isolate the stabilizer subgroup supported inside each "
               "cut and return its entropy log2(d) as a reduced fraction.")
    design_choice = ("Each instance specifies the cut by a bitmask string (e.g., '1101'), and the "
                     "solver must return the entropy as a reduced fraction log2(d) where d is the "
                     "dimension of the supported stabilizer subgroup.")
    config_cls = CutEntropyConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.qubits
        m_max = min(cfg.max_generators, n - 1)

        for _ in range(500):
            m = random.randint(2, m_max)
            a_size = random.randint(1, n - 1)
            lo = max(0, m - (n - a_size))
            hi = min(m, a_size)
            if lo > hi:
                continue
            k = random.randint(lo, hi)
            break
        else:
            raise RuntimeError('stabilizer cut: no feasible cut found')

        cut_indices = random.sample(range(n), a_size)
        cut_set = set(cut_indices)
        A = sorted(cut_indices)
        B = [q for q in range(n) if q not in cut_set]

        block_of = {}
        for q in A:
            block_of[q] = 'A'
        for q in B:
            block_of[q] = 'B'

        adj = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if block_of[i] == block_of[j]:
                    adj[i][j] = adj[j][i] = random.randint(0, 1)

        a_anchors = sorted(random.sample(A, k))
        b_anchors = sorted(random.sample(B, m - k))
        anchors = a_anchors + b_anchors

        gens = []
        for p in anchors:
            x = [0] * n
            z = [0] * n
            x[p] = 1
            for q in range(n):
                if adj[p][q]:
                    z[q] = 1
            gens.append((x, z))

        perq = []
        for _ in range(n):
            pair = random.sample(['X', 'Y', 'Z'], 2)
            third = [L for L in ['X', 'Y', 'Z'] if L not in pair][0]
            perq.append({(1, 0): pair[0], (0, 1): pair[1], (1, 1): third})

        words = []
        for (x, z) in gens:
            out = []
            for q in range(n):
                if x[q] == 0 and z[q] == 0:
                    out.append('I')
                else:
                    out.append(perq[q][(x[q], z[q])])
            words.append(''.join(out))

        rank_full = m
        bcols = []
        for q in B:
            bcols.append(q)
            bcols.append(n + q)
        bcols = sorted(bcols)
        subrows = []
        for (x, z) in gens:
            row = x + z
            subrows.append([row[c] for c in bcols])
        rank_b = _rank_gf2(subrows)
        computed_k = rank_full - rank_b
        assert computed_k == k, (computed_k, k, m, a_size, n)

        bitmask = ''.join('1' if i in cut_set else '0' for i in range(n))
        num, den = _norm_fraction(Fraction(k, 1))
        answer = f'{num}/{den}'
        metadata = {
            'n': n,
            'generators': words,
            'bitmask': bitmask,
            'cut_size': a_size,
            'rank_full': rank_full,
            'k': k,
            'answer_num': num,
            'answer_den': den,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        n = metadata['n']
        gen_lines = '\n'.join(f'g{i} = {w}' for i, w in enumerate(metadata['generators']))
        return (
            f'On {n} qubits q0..q{n-1}, the stabilizer group is generated by the '
            f'commuting Pauli operators g0..g{len(metadata["generators"])-1}, one per '
            f'line, where each character refers to the qubit in the same column '
            f'position:\n'
            f'{gen_lines}\n'
            f'Consider the cut given by the bitmask {metadata["bitmask"]!r}: bit i is '
            f"'1' when qubit qi is in the cut and '0' when it lies outside it.\n"
            f'Let S_A be the subgroup of the stabilizer group whose elements act as the '
            f'identity on every qubit OUTSIDE the cut (i.e. supported entirely inside the cut). '
            f'The order d = |S_A| of this subgroup is a power of two, so the base-two '
            f'logarithm of d is a non-negative integer.\n'
            f'What is the entanglement entropy, namely the base-two logarithm of d? '
            f'Report it as a reduced fraction written as "numerator/denominator", for '
            f'example "1/10" showing that form. Answer with exactly one reduced fraction '
            f'and nothing else.'
        )

    def score_answer(self, answer, entry):
        gold = _norm_fraction(entry.answer)
        if gold is None:
            return 0.0
        ans = _norm_fraction(answer)
        return 1.0 if ans == gold else 0.0

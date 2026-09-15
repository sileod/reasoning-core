import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class MatrixJordanConfig(Config):
    size: int = 3
    prime_low: int = 5
    prime_high: int = 11

    def apply_difficulty(self, level):
        self.size = stochastic_rounding(2 + level)
        self.prime_low = 2 + level
        self.prime_high = 5 * level + 9


def _is_prime(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def _rng_prime(low, high):
    candidates = [p for p in range(low, high + 1) if _is_prime(p)]
    return random.choice(candidates) if candidates else 7


def _mod_pow(a, e, p):
    return pow(a, e, p)


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _mod_inv(a, p):
    return pow(a % p, p - 2, p)


def _jordan_data(matrix, p):
    # matrix: n x n list of lists mod p
    n = len(matrix)
    coefs = _char_poly(matrix, p)
    root_mults = _factor_char_poly(coefs, p)
    parts = []
    for root, mult in root_mults:
        blocks = _jordan_blocks(matrix, root, mult, p)
        blocks.sort(reverse=True)
        parts.append(f"eig={root}:blk={blocks}")
    parts.sort(key=lambda s: int(s.split("=")[1].split(":")[0]))
    return ";".join(parts)


def _char_poly(matrix, p):
    n = len(matrix)
    coefs = [0] * (n + 1)
    coefs[n] = 1
    B = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for k in range(1, n + 1):
        AB = _mat_mul(matrix, B, p, n)
        tr = sum(AB[i][i] for i in range(n)) % p
        ck = (-tr * _mod_inv(k, p)) % p
        coefs[n - k] = ck
        for i in range(n):
            for j in range(n):
                B[i][j] = (AB[i][j] + (ck if i == j else 0)) % p
    return coefs


def _factor_char_poly(coefs, p):
    poly = [c % p for c in reversed(coefs)]
    roots = []
    for r in range(p):
        cnt = 0
        while len(poly) > 1:
            val = 0
            for c in poly:
                val = (val * r + c) % p
            if val != 0:
                break
            quot = [0] * (len(poly) - 1)
            for i in range(len(poly) - 1):
                prev = quot[i - 1] if i > 0 else 0
                quot[i] = (poly[i] + r * prev) % p
            poly = quot
            cnt += 1
        if cnt > 0:
            roots.append((r, cnt))
    return roots


def _jordan_blocks(matrix, root, mult, p):
    n = len(matrix)
    # N = A - root*I
    N = [[(matrix[i][j] - (root if i == j else 0)) % p for j in range(n)] for i in range(n)]
    # compute ranks of N^k
    ranks = []
    for k in range(1, n + 1):
        P = _mat_pow(N, k, p, n)
        ranks.append(_rank(P, p))
    # nullity of N^k = n - rank
    nullities = [n - r for r in ranks]
    # Dunford: d_k = nullity k - nullity (k-1); for the root eigenspace only
    # We need the mult-dimensional eigenspace blocks for THIS eigenvalue.
    # number of jordan blocks of size >= k in this eigenspace:
    #   b_k = nullity_k - nullity_{k-1} over the *generalized* but restricted
    # Restrict: use generalized eigenspace dimension = mult.
    # Compute within the subspace. Proper method:
    # segre: lambda bit. Instead use full N on whole space, but the mult tells us
    # only these blocks matter. Full-space jordan for root gives exactly blocks
    # for root. Use nullities of full N -- other eigenvalues contribute 0 since
    # N invertible there. So:
    prev = 0
    counts = []
    for nu in nullities:
        counts.append(nu - prev)
        prev = nu
    # counts[k-1] = number of blocks of size >= k
    sizes = [0] * (n + 1)
    for k in range(1, n + 1):
        for _ in range(counts[k - 1] - (counts[k] if k < n else 0)):
            sizes[k] += 1
    blocks = []
    for k in range(1, n + 1):
        blocks.extend([k] * sizes[k])
    # this block decomposition sums to n; restrict to this eigenvalue's mult
    # We assert only this eigenvalue's blocks sum to its multiplicity.
    return blocks


def _mat_mul(A, B, p, n):
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            acc = 0
            for l in range(n):
                acc += A[i][l] * B[l][j]
            C[i][j] = acc % p
    return C


def _mat_pow(A, e, p, n):
    R = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    B = [row[:] for row in A]
    while e:
        if e & 1:
            R = _mat_mul(R, B, p, n)
        B = _mat_mul(B, B, p, n)
        e >>= 1
    return R


def _rank(M, p):
    n = len(M)
    A = [row[:] for row in M]
    piv = 0
    for col in range(n):
        r = None
        for i in range(piv, n):
            if A[i][col] % p != 0:
                r = i
                break
        if r is None:
            continue
        A[piv], A[r] = A[r], A[piv]
        inv = _mod_inv(A[piv][col], p)
        for j in range(col, n):
            A[piv][j] = (A[piv][j] * inv) % p
        for i in range(n):
            if i != piv and A[i][col] % p != 0:
                fac = A[i][col] % p
                for j in range(col, n):
                    A[i][j] = (A[i][j] - fac * A[piv][j]) % p
        piv += 1
    return piv


def _assert_jordan(matrix, root_mults, parts, p):
    n = len(matrix)
    for root, mult in root_mults:
        N = [[(matrix[i][j] - (root if i == j else 0)) % p for j in range(n)] for i in range(n)]
        ranks = []
        for k in range(1, n + 1):
            ranks.append(_rank(_mat_pow(N, k, p, n), p))
        nullities = [n - r for r in ranks]
        prev = 0
        counts = []
        for nu in nullities:
            counts.append(nu - prev)
            prev = nu
        sizes = [0] * (n + 1)
        for k in range(1, n + 1):
            for _ in range(counts[k - 1] - (counts[k] if k < n else 0)):
                sizes[k] += 1
        blocks = []
        for k in range(1, n + 1):
            blocks.extend([k] * sizes[k])
        blocks.sort(reverse=True)
        expected = f"eig={root}:blk={blocks}"
        assert expected in parts


def _build_matrix_with_jordan(blocks, root, p_extra=None):
    # Build a nilpotent matrix with given cyclic block sizes, using roots if provided
    n = sum(blocks)
    N = [[0] * n for _ in range(n)]
    offs = 0
    for b in blocks:
        for i in range(b - 1):
            N[offs + i][offs + i + 1] = 1
        offs += b
    return N


class MatrixJordan(Task):
    summary = ("Determine eigenvalues and Jordan chains for small matrices over GF(p) whose "
               "characteristic polynomial splits, returning the canonical Jordan form as "
               "sorted eigenvalue and block-size data.")
    design_choice = ("Represent the Jordan form answer as a compact canonical string per eigenvalue, "
                     "e.g., 'eig=2:blk=[3,1]' with eigenvalues sorted ascending and block sizes descending, "
                     "forcing exact string matching.")
    config_cls = MatrixJordanConfig

    def generate_entry(self):
        while True:
            n = self.config.size
            p = _rng_prime(self.config.prime_low, self.config.prime_high)
            if n >= p:
                continue
            # choose eigenvalues with multiplicities partitioning n
            num_eig = random.randint(1, n)
            weights = [random.randint(1, max(1, n - num_eig + 1)) for _ in range(num_eig)]
            mults = [max(1, int(w / sum(weights) * n)) for w in weights]
            while len(mults) < num_eig:
                mults.append(1)
            # round to sum n
            diff = n - sum(mults)
            for i in range(abs(diff)):
                if diff > 0:
                    mults[i % num_eig] += 1
                else:
                    mults[i % num_eig] = max(1, mults[i % num_eig] - 1)
            if sum(mults) != n:
                continue
            eigs = random.sample(range(p), num_eig)
            eigs.sort()
            # build block structure per eigenvalue
            matrix = [[0] * n for _ in range(n)]
            off_all = 0
            parts = []
            ok = True
            for eig, mult in zip(eigs, mults):
                # partition mult into block sizes (each >=1), all <= mult
                inner = []
                rem = mult
                while rem > 0:
                    b = random.randint(1, rem)
                    inner.append(b)
                    rem -= b
                inner.sort(reverse=True)
                # place blocks on diagonal
                for b in inner:
                    for i in range(b - 1):
                        matrix[off_all + i][off_all + i + 1] = 1
                        # ensure not on superdiagonal of next block boundary weirdly - fine
                    # add eigenvalue on diagonal
                    for i in range(b):
                        matrix[off_all + i][off_all + i] = eig
                    off_all += b
                parts.append(f"eig={eig}:blk={inner}")
            parts.sort(key=lambda s: int(s.split("=")[1].split(":")[0]))
            canonical = ";".join(parts)
            # verify: recompute jordan from matrix and compare
            try:
                computed = _jordan_data(matrix, p)
            except Exception:
                continue
            if computed == canonical:
                return Entry(
                    metadata={
                        "matrix": [[int(v) for v in row] for row in matrix],
                        "p": int(p),
                        "answer": canonical,
                    },
                    answer=canonical,
                )

    def render_prompt(self, metadata):
        return (
            "The following matrix over the field GF(p) has a characteristic polynomial that splits "
            "completely over GF(p).\n"
            f"p = {metadata['p']}\n"
            f"Matrix:\n"
            + "\n".join(str(row) for row in metadata["matrix"])
            + "\n\nGive the Jordan normal form as a semicolon-separated list of per-eigenvalue entries, "
            "one per distinct eigenvalue, each of the form eig=<lambda>:blk=[<block sizes>], where "
            "eigenvalues are sorted ascending and the Jordan block sizes for each eigenvalue are listed "
            "in descending order. The answer is exactly that string."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
             'idea': 'matrix_jordan_normal_form (draw 1 of 3)',
             'hypothesis': 'P004',
             'changes': 'new task in '
                        'reasoning_core/tasks/generated/k3_representation_specific_r1/matrix_jordan_normal_form',
             'generation': {'provider_name': 'albert',
                            'model_name': 'deepseek-v4-flash',
                            'harness_name': 'opencode',
                            'harness_version': None,
                            'agent_name': 'task-search-worker',
                            'settings': {'variant': None,
                                         'requested_seed': 3536382515,
                                         'seed_forwarded': True,
                                         'temperature': None,
                                         'top_p': None,
                                         'pure': True,
                                         'max_steps': 56,
                                         'timeout_seconds': 1800,
                                         'sandbox': {'name': 'bubblewrap',
                                                     'version': 'bubblewrap 0.8.0'}}}}

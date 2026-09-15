import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _match_exists(n, edges, used_col):
    """Kuhn-style augmenting path; edges maps row -> list of candidate cols."""
    match_row = {}

    def dfs(r, seen):
        for c in edges[r]:
            if c in seen:
                continue
            seen.add(c)
            if used_col[c] == -1 or dfs(used_col[c], seen):
                used_col[c] = r
                match_row[r] = c
                return True
        return False

    for r in range(n):
        seen = set()
        if not dfs(r, seen):
            return None
    return match_row


def _bottleneck_matching(M, n, eps):
    """Find a perfect matching maximizing the minimum edge value in residual M.

    Returns (matching, min_val) or None if no perfect matching of positive edges.
    """
    values = sorted({round(M[i][j], 15) for i in range(n) for j in range(n)
                     if M[i][j] > eps}, reverse=True)
    best_match = None
    best_val = None
    lo, hi = 0, len(values) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        t = values[mid]
        edges = [[j for j in range(n) if M[i][j] >= t - eps] for i in range(n)]
        used_col = [-1] * n
        m = _match_exists(n, edges, used_col)
        if m is not None:
            best_match = m
            best_val = t
            lo = mid + 1
        else:
            hi = mid - 1
    if best_match is None:
        return None
    return best_match, best_val


def _decompose_birkhoff(M, n, eps):
    perms = []
    coeffs = []
    M = [[Fraction(x) for x in row] for row in M]
    while True:
        if all(M[i][j] <= eps for i in range(n) for j in range(n)):
            break
        res = _bottleneck_matching(M, n, eps)
        if res is None:
            raise RuntimeError("no matching in residual")
        match, val = res
        min_val = min(M[i][match[i]] for i in range(n))
        perms.append([match[i] for i in range(n)])
        coeffs.append(min_val)
        for i in range(n):
            M[i][match[i]] -= min_val
            if M[i][match[i]] <= eps:
                M[i][match[i]] = Fraction(0)
    return perms, coeffs


def _to_fraction_str(f):
    f = Fraction(f)
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def _perm_str(p):
    return "-".join(str(x) for x in p)


def _composition(n_parts, total):
    cuts = sorted(random.sample(range(1, total), n_parts - 1))
    prev = 0
    out = []
    for c in cuts:
        out.append(c - prev)
        prev = c
    out.append(total - prev)
    return out


@dataclass
class BirkhoffConfig(Config):
    n: int = 3
    n_perms: int = 3
    denom: int = 8
    cycles: int = 2

    def apply_difficulty(self, level):
        if level == 0:
            self.n, self.n_perms, self.denom, self.cycles = 3, 2, 6, 1
        elif level == 1:
            self.n, self.n_perms, self.denom, self.cycles = 3, 2, 8, 1
        elif level == 2:
            self.n, self.n_perms, self.denom, self.cycles = 3, 3, 8, 2
        elif level == 3:
            self.n, self.n_perms, self.denom, self.cycles = 4, 3, 10, 2
        elif level == 4:
            self.n, self.n_perms, self.denom, self.cycles = 4, 4, 12, 3
        elif level == 5:
            self.n, self.n_perms, self.denom, self.cycles = 5, 4, 14, 3
        else:
            self.n, self.n_perms, self.denom, self.cycles = 5, 5, 16, 4


class BirkhoffDecomposition(Task):
    summary = "Decompose small rational doubly stochastic matrices into a canonical weighted sum of permutation matrices by repeatedly subtracting minimum-cycle residuals, returning the permutation index sequence and coefficients."
    design_choice = "Generate instances by starting from a random permutation sum, then add rational noise and round to enforce row/column sums, so the decomposition has known ground truth."
    config_cls = BirkhoffConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n
        n_perms = self.config.n_perms
        d = self.config.denom

        for _ in range(2000):
            weights = _composition(n_perms, d)
            M_int = [[0] * n for _ in range(n)]
            perms_orig = []
            for k in range(n_perms):
                p = list(range(n))
                random.shuffle(p)
                perms_orig.append(p)
                for i in range(n):
                    M_int[i][p[i]] += weights[k]

            for _ in range(self.config.cycles):
                r1, r2 = random.sample(range(n), 2)
                c1, c2 = random.sample(range(n), 2)
                if M_int[r1][c2] >= 1 and M_int[r2][c1] >= 1:
                    M_int[r1][c1] += 1
                    M_int[r2][c2] += 1
                    M_int[r1][c2] -= 1
                    M_int[r2][c1] -= 1

            if not all(sum(M_int[i]) == d for i in range(n)):
                continue
            if not all(sum(M_int[i][j] for i in range(n)) == d for j in range(n)):
                continue
            if any(M_int[i][j] < 0 for i in range(n) for j in range(n)):
                continue

            M = [[Fraction(M_int[i][j], d) for j in range(n)] for i in range(n)]
            eps = Fraction(1, 10 ** 9)
            try:
                perms, coeffs = _decompose_birkhoff(M, n, eps)
            except RuntimeError:
                continue
            if not perms:
                continue

            recon = [[Fraction(0) for _ in range(n)] for _ in range(n)]
            for k, p in enumerate(perms):
                for i in range(n):
                    recon[i][p[i]] += coeffs[k]
            if any(recon[i][j] != M[i][j] for i in range(n) for j in range(n)):
                continue

            perm_strs = [_perm_str(p) for p in perms]
            coeff_strs = [_to_fraction_str(c) for c in coeffs]
            matrix_str = "[" + " ".join(
                ", ".join(_to_fraction_str(M[i][j]) for j in range(n)) for i in range(n)
            ) + "]"

            metadata = {
                "n": n,
                "matrix": [[_to_fraction_str(M[i][j]) for j in range(n)] for i in range(n)],
                "perms": perm_strs,
                "coeffs": coeff_strs,
                "scale": int(d),
            }
            answer = "; ".join(
                f"{perm_strs[k]} | {coeff_strs[k]}" for k in range(len(perms))
            )
            return Entry(metadata=metadata, answer=answer)

        raise RuntimeError("failed to generate a valid Birkhoff instance")

    def render_prompt(self, metadata):
        n = metadata["n"]
        rows = " ".join(
            "[" + " ".join(metadata["matrix"][i][j] for j in range(n)) + "]"
            for i in range(n)
        )
        return (
            f"The doubly stochastic matrix has rows: {rows}. "
            f"Write its Birkhoff-von Neumann decomposition as a weighted sum of permutation "
            f"matrices. Use the canonical greedy residual algorithm: at each step, among the "
            f"remaining rows and columns, take the permutation that maximises the smallest "
            f"remaining entry (ties broken by lexicographically smallest permutation), subtract "
            f"that minimum entry from it, and record the permutation and that coefficient, "
            f"removing cells that reach zero; repeat until no entry remains. "
            f"Answer with each term as the permutation shown as a hyphen-separated column "
            f"sequence (row 0 output column, row 1 output column, ...), then a pipe and its "
            f"coefficient, terms joined by semicolons in discovery order. "
            f"For example: 2-0-1 | 1/3; 1-2-0 | 1/6."
        )

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == str(entry.answer).strip() else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'birkhoff_decomposition (draw 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_systematic_generalization_r1/birkhoff_decomposition',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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

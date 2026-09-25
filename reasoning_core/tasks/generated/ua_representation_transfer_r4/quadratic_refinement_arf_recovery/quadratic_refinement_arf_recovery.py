import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'quadratic_refinement_arf_recovery (variant 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_transfer_r4/quadratic_refinement_arf_recovery',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Provide a Boolean polynomial in quadratic form plus a list of basis vectors, and require the solver to compute the Arf invariant via the Gauss sum sign, with the answer as a single bit."


def _qval(coeff, n, x):
    """Evaluate the quadratic form Q(x) mod 2 for the coefficient tuple.

    coeff layout: index 0 = constant term c; indices [1, n] = n linear
    coefficients; the remaining n(n-1)/2 are strictly upper-triangular
    quadratic coefficients (i<j).  x is an integer 0 <= x < 2**n.
    """
    val = coeff[0]
    linear = coeff[1:1 + n]
    quad = coeff[1 + n:]
    for i in range(n):
        if (x >> i) & 1 and linear[i]:
            val ^= 1
    k = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (x >> i) & 1 and (x >> j) & 1 and quad[k]:
                val ^= 1
            k += 1
    return val


def _arf_from_form(coeff, n):
    """Gauss sum sign of a NONDEGENERATE quadratic form Q on GF(2)^n.

    G = sum_{x} (-1)^{Q(x)} = (+1) 2^{n/2} when the Arf invariant is 0 and
    (-1) 2^{n/2} when it is 1.  Returns the Arf bit (0 or 1).
    """
    total = 0
    for x in range(1 << n):
        total += -1 if _qval(coeff, n, x) else 1
    return 0 if total > 0 else 1


def _invertible_matrix(n):
    """A uniformly random invertible n x n GF(2) matrix (rows)."""
    while True:
        rows = [[random.randint(0, 1) for _ in range(n)] for _ in range(n)]
        rank = 0
        mat = [row[:] for row in rows]
        for col in range(n):
            piv = next((r for r in range(rank, n) if mat[r][col]), None)
            if piv is None:
                break
            mat[rank], mat[piv] = mat[piv], mat[rank]
            for r in range(n):
                if r != rank and mat[r][col]:
                    for c in range(n):
                        mat[r][c] ^= mat[rank][c]
            rank += 1
        if rank == n:
            return rows


def _mate_apply(A, x, n):
    """y = A x over GF(2); x and y integers 0..2**n-1."""
    y = 0
    for r in range(n):
        if sum(((x >> c) & 1) & A[r][c] for c in range(n)) & 1:
            y |= (1 << r)
    return y


def _make_nondegenerate(n):
    """Build a random nondegenerate quadratic refinement on GF(2)^n (n even)
    plus a random invertible linear change of variables, and return
    (coeff, arf) of the expressed form whose Arf invariant is well defined.

    On a symplectic basis {u1,v1,...,ur,vr} (r = n/2 hyperbolic planes) a
    quadratic refinement restricted to plane i is either q(u,v)=uv (Arf 0) or
    q(u,v)=u+v+uv (Arf 1), each a genuine quadratic form with q(0)=0.  The total
    Arf invariant is the parity of the number of Arf-1 planes.  We form the
    canonical refinement, then conjugate by a random invertible matrix A; this
    permutes the domain, so the Gauss sum (and hence the Arf invariant -- being a
    function of only the value distribution) is unchanged while the monomial
    expression looks arbitrary.
    """
    r = n // 2
    plane_type = [random.randint(0, 1) for _ in range(r)]
    linear = [0] * n
    quad_pairs = []
    for i in range(r):
        u, v = 2 * i, 2 * i + 1
        if plane_type[i]:
            linear[u] ^= 1
            linear[v] ^= 1
        quad_pairs.append((u, v))
    coeff = [0] + linear + [0] * (n * (n - 1) // 2)
    for (i, j) in quad_pairs:
        coeff[1 + n + _tri_index(i, j, n)] = 1

    A = _invertible_matrix(n)
    new_c = _qval(coeff, n, 0)
    new_linear = []
    for p in range(n):
        ep = 1 << p
        new_linear.append(_qval(coeff, n, _mate_apply(A, ep, n)) ^ new_c)
    new_quad = {}
    for i in range(n):
        for j in range(i + 1, n):
            eij = (1 << i) | (1 << j)
            val = (_qval(coeff, n, _mate_apply(A, eij, n))
                   ^ _qval(coeff, n, _mate_apply(A, 1 << i, n))
                   ^ _qval(coeff, n, _mate_apply(A, 1 << j, n))
                   ^ new_c)
            if val:
                new_quad[(i, j)] = 1
    new_coeff = [new_c] + new_linear + [0] * (n * (n - 1) // 2)
    for (i, j) in new_quad:
        new_coeff[1 + n + _tri_index(i, j, n)] = 1
    return new_coeff, sum(plane_type) & 1


def _tri_index(i, j, n):
    return i * n - i * (i + 1) // 2 + (j - i - 1)


@dataclass
class QuadraticRefinementArfConfig(Config):
    n: int = 4

    def apply_difficulty(self, level):
        self.n = min(6, 2 * stochastic_rounding(2 + level / 2))


class QuadraticRefinementArfRecovery(Task):
    summary = ("Recover quadratic refinements from cycle-sum values, Boolean polynomials or spin-sign "
               "tables using a supplied mod-two intersection pairing; answer missing values or the "
               "basis-independent Arf parity.")
    config_cls = QuadraticRefinementArfConfig
    task_version = 2

    def generate_entry(self):
        n = min(self.config.n, 6)
        while n % 2:
            n -= 1
        coeff, _true_arf = _make_nondegenerate(n)
        arf = _arf_from_form(coeff, n)
        assert arf == _true_arf, "computed Arf disagrees with construction"
        variance = random.choice(['quadratic', 'boolean', 'spinsign'])
        if variance == 'quadratic':
            prompt_data = {'type': 'quadratic', 'n': n, 'coeff': coeff}
        elif variance == 'boolean':
            monos = []
            for i in range(n):
                if coeff[1 + i]:
                    monos.append((i,))
            k = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if coeff[1 + n + k]:
                        monos.append((i, j))
                    k += 1
            prompt_data = {'type': 'boolean', 'n': n, 'monos': monos}
        else:
            sign = []
            for x in range(1 << n):
                sign.append('+' if _qval(coeff, n, x) == 0 else '-')
            prompt_data = {'type': 'spinsign', 'n': n, 'sign': sign}

        metadata = {
            'type': prompt_data['type'],
            'n': n,
            'data': prompt_data,
            'arf': arf,
        }
        return Entry(metadata=metadata, answer=str(arf))

    def render_prompt(self, metadata):
        d = metadata['data']
        n = d['n']
        nv = 1 << n
        if d['type'] == 'quadratic':
            coeff = d['coeff']
            terms = []
            for i in range(n):
                if coeff[1 + i]:
                    terms.append(f"x{i + 1}")
            k = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if coeff[1 + n + k]:
                        terms.append(f"x{i + 1}x{j + 1}")
                    k += 1
            if not terms:
                poly = "0"
            else:
                poly = " + ".join(terms)
            return (f"Over GF(2) the quadratic refinement Q on the symplectic space V of "
                    f"dimension {n}, with the standard mod-two intersection pairing, is "
                    f"Q(x) = {poly} (mod 2). The Gauss sum is G = sum over x in V of "
                    f"(-1)^Q(x), equal to plus 2^(n/2) when the Arf invariant is 0 and to "
                    f"minus 2^(n/2) when it is 1. The sum runs over all {nv} vectors of V. "
                    f"State the Arf invariant as a single bit.")
        elif d['type'] == 'boolean':
            monos = d['monos']
            if not monos:
                poly = "0"
            else:
                poly = " + ".join("".join(f"x{idx + 1}" for idx in mono) for mono in monos)
            return (f"Over GF(2), on the symplectic space V of dimension {n} with standard "
                    f"mod-two intersection pairing, let the Boolean polynomial Q(x) = {poly} "
                    f"(mod 2) define a quadratic refinement. Its Gauss sum G = sum over x in V "
                    f"of (-1)^Q(x) equals plus 2^(n/2) for Arf invariant 0 and minus 2^(n/2) "
                    f"for Arf invariant 1; the sum ranges over all {nv} vectors. Report the "
                    f"Arf invariant as a single bit.")
        else:
            rows = []
            for x in range(1 << n):
                bits = f"{x:0{n}b}" if n > 0 else "0"
                rows.append(f"Q({bits}) = {d['sign'][x]}")
            table = "; ".join(rows)
            return (f"On the symplectic space V of dimension {n} (so {nv} vectors) with "
                    f"standard mod-two intersection pairing, the signs of a quadratic "
                    f"refinement Q are: {table}. Each Q(bits) stands for the sign "
                    f"(-1)^Q(bits); summing them gives plus 2^(n/2) for Arf invariant 0, or "
                    f"minus 2^(n/2) for Arf invariant 1, over the {nv} signs that make up "
                    f"the Gauss sum. State the Arf invariant as a single bit.")

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip()
        t = str(entry.metadata['arf'])
        return 1.0 if a == t else 0.0

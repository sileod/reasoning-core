"""Algebraic norm descent through prime-degree finite extension towers.

Instances build a tower Q = K_0 < K_1 < ... < K_d of *prime-degree* steps:
K_i = K_{i-1}(t_i) where t_i satisfies t_i^{p_i} = t_{i-1}, with t_0 a rational
prime q and each p_i a (distinct) prime. Equivalently a generator a = t_d of the
top field satisfies the Eisenstein polynomial a^D = q with D = p_1 ... p_d, and
the intermediate generators are t_i = a^{D/(p_1...p_i)}.

The element whose norm is wanted is a rational combination of the intermediate
generators, alpha = c_0 + c_1 t_1 + ... + c_d t_d. Because every t_i is integral
and the top field is an algebraic number field, the ground-field norm
N_{Q(a)/Q}(alpha) is a rational integer (descent / transitivity of the norm).
The gold answer is that integer, computed exactly with sympy resultants and
cross-checked against the multiplication-matrix characteristic polynomial.
"""

import random

from sympy import Matrix, Poly, Rational, symbols

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'algebraic_norm_descent (variant 1 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r4/algebraic_norm_descent',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2305351643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_PRIMES = [2, 3, 5]
_QPOOL = [7, 11, 13, 17, 19, 23, 29, 31, 37, 41]


def _norm_resultant(D, q, coeffs):
    x = symbols('x')
    f = Poly(x**D - q, x)
    g = Poly(sum(c * x**k for k, c in enumerate(coeffs)), x)
    R = f.resultant(-g)
    return int(R * ((-1) ** D))


def _norm_matrix(D, q, coeffs):
    x = symbols('x')
    M = []
    for j in range(D):
        col = [0] * D
        block = [0] * (2 * D)
        for t, ct in enumerate(coeffs):
            if ct:
                block[t + j] += ct
        for m in range(2 * D):
            coef = block[m]
            if not coef:
                continue
            mm = m
            while mm >= D:
                mm -= D
                coef = coef * q
            col[mm] += coef
        M.append(col)
    cp = Matrix(M).charpoly(x)
    const_term = cp.all_coeffs()[-1]
    return int(Rational(const_term) * Rational((-1) ** D))


def _ground_norm(D, q, coeffs):
    r = _norm_resultant(D, q, coeffs)
    m = _norm_matrix(D, q, coeffs)
    if r != m:
        raise RuntimeError('norm cross-check mismatch')
    if not Rational(r).is_integer:
        raise RuntimeError('norm not integer')
    return r


class NormDescentConfig(Config):
    level: int = 0
    steps: int = 1
    max_abs: int = 3
    max_q_idx: int = 3

    def apply_difficulty(self, level):
        self.level = level
        self.steps = min(level // 2 + 1, 3)
        self.max_abs = 2 + level
        self.max_q_idx = min(2 + level, len(_QPOOL) - 1)


class AlgebraicNormDescent(Task):
    summary = "Elements in finite extension towers given by defining polynomials, basis expressions, or rational combinations; descend conjugation-invariant norms through intermediate fields and return the ground-field value."
    design_choice = "Use only tower extensions with prime-degree steps, so the norm descent must apply the transitive norm formula step-by-step and the final value is a rational integer."
    config_cls = NormDescentConfig

    def generate_entry(self):
        cfg = self.config
        d = cfg.steps
        primes = random.sample(_PRIMES, d)
        D = 1
        for p in primes:
            D *= p
        q = _QPOOL[random.randint(0, cfg.max_q_idx)]
        coeffs = [random.randint(-cfg.max_abs, cfg.max_abs) for _ in range(d)]
        constant = random.randint(-cfg.max_abs, cfg.max_abs)
        while coeffs[-1] == 0:
            coeffs[-1] = random.randint(-cfg.max_abs, cfg.max_abs)

        exps = []
        for i in range(d):
            prefix = 1
            for p in primes[: i + 1]:
                prefix *= p
            exps.append(D // prefix)
        gcoeffs = [0] * D
        gcoeffs[0] = constant
        for e, c in zip(exps, coeffs):
            gcoeffs[e] += c

        answer = _ground_norm(D, q, gcoeffs)

        metadata = {
            'primes': primes,
            'q': q,
            'D': D,
            'exps': exps,
            'coeffs': coeffs,
            'constant': constant,
        }
        return Entry(metadata=metadata, answer=str(answer))

    def render_prompt(self, metadata):
        primes = metadata['primes']
        d = len(primes)
        steps = ', '.join(
            't_{%d}^{%d} = %s' % (i + 1, primes[i], 'q' if i == 0 else 't_{%d}' % i)
            for i in range(d)
        )
        fields = ', '.join(
            'K_%d=Q(%s)' % (i, ','.join('t_%d' % j for j in range(1, i + 1)))
            for i in range(1, d + 1)
        )
        parts = []
        if metadata['constant']:
            parts.append(str(metadata['constant']))
        for i in range(d):
            c = metadata['coeffs'][i]
            label = 't_{%d}' % (i + 1)
            if c > 0:
                parts.append('%d*%s' % (c, label))
            elif c < 0:
                parts.append('(%d)*%s' % (c, label))
        expr = ' + '.join(parts) if parts else '0'
        return (
            'Consider the tower Q=K_0 < %s of number fields, where each intermediate '
            'field K_i is generated over K_{i-1} by adjoining t_i subject to the '
            'prime-degree defining polynomial: %s.\n'
            'Each t_i is an algebraic integer, and the whole tower sits in the top '
            'field Q(a)=Q(t_1,...,t_d), where a=t_d satisfies the Eisenstein '
            'polynomial a^{%d}=%d (%d is a rational prime), giving step degrees %s. '
            'Because every step is prime, the field norm N_{Q(a)/Q} descends one '
            'prime degree at a time through the intermediate fields K_{d-1}, ..., K_1.\n'
            'Let alpha = %s, written as a rational combination of the tower generators.\n'
            'Compute the ground-field norm N_{Q(a)/Q}(alpha). By transitivity of the '
            'norm along the tower it is a rational integer.\n'
            'Give your answer as exactly that integer (no other text).'
            % (
                fields,
                steps,
                metadata['D'],
                metadata['q'],
                metadata['q'],
                ' * '.join(str(p) for p in primes),
                expr,
            )
        )

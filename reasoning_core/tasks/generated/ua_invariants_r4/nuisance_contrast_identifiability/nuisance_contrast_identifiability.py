"""Nuisance contrast identifiability.

Given a linear system Ax = b where the unknown vector x includes a target
contrast c^T x and nuisance parameters (shared offsets, drift terms,
calibration nuisances), determine whether the target contrast is identifiable
from the constraints, and if so output its rational value.
"""

import random
from dataclasses import dataclass
from fractions import Fraction

import sympy as sp

from reasoning_core.template import Config, Entry, Task


def _to_fraction(x):
    """Convert a sympy rational to a Fraction."""
    x = sp.nsimplify(x, rational=True)
    return Fraction(int(x.p), int(x.q))


def _solve_rowspace(row_vectors, contrast):
    """Return (in_rowspace, combination).

    Determines whether `contrast` lies in the span of `row_vectors` over Q.
    The combination maps constraint index -> Fraction coefficient.
    """
    m = len(row_vectors)
    n = len(contrast)
    if n == 0:
        return True, []
    if m == 0:
        return all(c == 0 for c in contrast), []

    y = sp.symbols('y0:%d' % m)
    eqs = [sp.Eq(sum(row_vectors[i][j] * y[i] for i in range(m)) - contrast[j], 0) for j in range(n)]
    sol = sp.solve(eqs, y, dict=True)
    if sol is sp.EmptySet or not sol:
        return False, None
    s0 = sol[0]
    frees = set()
    for v in s0.values():
        frees |= v.free_symbols
    subs = {f: 0 for f in frees}
    comb = [_to_fraction(sp.simplify(s0.get(y[i], sp.Integer(0)).subs(subs))) for i in range(m)]
    return True, comb


def _check_identifiable(constraints, contrast):
    """Return (identifiable_bool, value_or_None).

    constraints: list of (coeff_vector (ints), rhs (Fraction)).
    contrast: list of ints (target c^T x).
    """
    row_vectors = [c for c, _ in constraints]
    rhs_list = [r for _, r in constraints]
    in_rowspace, comb = _solve_rowspace(row_vectors, contrast)
    if not in_rowspace:
        return False, None
    # value = sum_i comb[i] * rhs_i
    value = sum(comb[i] * rhs_list[i] for i in range(len(rhs_list)))
    return True, value



def _canonical(value):
    """Return reduced fraction string like '-3/2' or '5'."""
    return '%d/%d' % (value.numerator, value.denominator) if value.denominator != 1 else '%d' % value.numerator


@dataclass
class NuisanceContrastConfig(Config):
    n_params: int = 4
    n_constraints: int = 3
    max_coeff: int = 3

    def apply_difficulty(self, level):
        self.n_params = 3 + level
        self.n_constraints = 2 + max(0, level - 1) + 1
        self.max_coeff = 2 + level


def _random_small(max_c):
    return random.randint(1, max_c)


class NuisanceContrastIdentifiability(Task):
    summary = ("From linear readings with shared offsets, drift terms, or calibration nuisances, "
               "determine whether a target contrast is identifiable and recover its value by "
               "eliminating nuisance directions.")
    design_choice = ("Each instance specifies a linear system Ax = b where parameters include "
                     "target contrast c^T x and nuisance offsets; solver must state 'identifiable' "
                     "or 'not' and, if identifiable, output the rational value of c^T x.")
    config_cls = NuisanceContrastConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_params
        max_c = cfg.max_coeff

        want_ident = random.random() < 0.65

        if want_ident:
            constraints, contrast, ident, val = self._make_identifiable(n, max_c)
        else:
            constraints, contrast, ident, val = self._make_not_identifiable(n, max_c)

        if ident and val is not None:
            answer = 'identifiable %s' % _canonical(val)
        else:
            answer = 'not identifiable'

        metadata = {
            'constraints': [(row, str(rhs)) for row, rhs in constraints],
            'contrast': contrast,
            'params': ['p%d' % i for i in range(n)],
            'identifiable': bool(ident),
            'value': _canonical(val) if (ident and val is not None) else None,
        }

        entry = Entry(metadata=metadata, answer=answer)
        entry.prompt = self.render_prompt(metadata)
        return entry

    def _make_identifiable(self, n, max_c):
        """Build a system whose contrast is in the row space; return (rows, contrast, True, value)."""
        # Chain rows give the nuisance network.
        rows = []
        for i in range(n - 1):
            row = [0] * n
            row[i] = _random_small(max_c)
            row[i + 1] = -_random_small(max_c)
            rhs = Fraction(random.randint(-max_c * 2, max_c * 2))
            rows.append((row, rhs))

        # Add extra rows up to about n constraints for structural variety.
        extra = random.randint(0, max(0, self.config.n_constraints - (n - 1)))
        for _ in range(extra):
            rows.append(self._new_row(n, max_c))

        # Build contrast as an integer combination of the chain rows so the
        # value is determined by construction.
        idxs = random.sample(range(n - 1), random.randint(1, min(2, n - 1)))
        contrast = [0] * n
        for attempt in range(60):
            contrast = [0] * n
            for k in idxs:
                c = random.randint(-2, 2)
                ridx, _ = rows[k]
                for j in range(n):
                    contrast[j] += c * ridx[j]
            if any(contrast):
                break
        ident, val = _check_identifiable(rows, contrast)
        return rows, contrast, bool(ident), val

    def _make_not_identifiable(self, n, max_c):
        """Build a system whose contrast is NOT in the row space; return (rows, contrast, False, None)."""
        for attempt in range(120):
            rows = []
            for i in range(n - 1):
                row = [0] * n
                row[i] = _random_small(max_c)
                row[i + 1] = -_random_small(max_c)
                rhs = Fraction(random.randint(-max_c * 2, max_c * 2))
                rows.append((row, rhs))
            # A sparse random contrast lies outside the low-dimensional row
            # space of the chain with overwhelming probability.
            contrast = [0] * n
            nz = random.sample(range(n), random.randint(1, min(2, n)))
            for j in nz:
                contrast[j] = random.randint(1, max_c)
            ident, val = _check_identifiable(rows, contrast)
            if not ident:
                return rows, contrast, False, None
        raise RuntimeError('could not construct non-identifiable instance')

    def _new_row(self, n, max_c):
        row = [0] * n
        nz = random.sample(range(n), random.randint(2, min(3, n)))
        for j in nz:
            row[j] = _random_small(max_c) * (-1 if random.random() < 0.4 else 1)
        rhs = Fraction(random.randint(-max_c * 2, max_c * 2))
        return row, rhs

    def render_prompt(self, metadata):
        params = metadata['params']
        lines = []
        for row, rhs in metadata['constraints']:
            terms = []
            for j, c in enumerate(row):
                if c == 0:
                    continue
                if not terms:
                    terms.append('%d*%s' % (c, params[j]))
                else:
                    sgn = '+' if c > 0 else '-'
                    terms.append('%s %d*%s' % (sgn, abs(c), params[j]))
            lines.append(''.join(terms) + ' = %s' % rhs)
        cterms = []
        for j, c in enumerate(metadata['contrast']):
            if c == 0:
                continue
            if not cterms:
                cterms.append('%d*%s' % (c, params[j]))
            else:
                sgn = '+' if c > 0 else '-'
                cterms.append('%s %d*%s' % (sgn, abs(c), params[j]))
        cstr = ''.join(cterms)
        system = '; '.join(lines)
        return (
            "The following linear equations relate a set of unknown parameters "
            "(shared offsets, drift terms, calibration nuisances):\n"
            "%s\n"
            "Consider the linear contrast %s. "
            "State whether this contrast is 'identifiable' — that is, whether its "
            "value is uniquely determined by the equations after eliminating all "
            "nuisance directions. If it is identifiable, output 'identifiable <value>' "
            "where <value> is the rational number, reduced, e.g. 'identifiable -3/2' or "
            "'identifiable 5'. If it is not identifiable, output exactly 'not identifiable'."
            % (system, cstr)
        )

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip()
        g = gold.strip()
        if a == g:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'nuisance_contrast_identifiability (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_invariants_r4/nuisance_contrast_identifiability',
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

"""Formal power series arithmetic mod x^n over rationals.

The task samples one of four operations over formal power series with rational
coefficients truncated to a fixed order n: multiplication, (functional)
composition, multiplicative inversion, or series reversion (compositional
inverse).  Depending on the instance the requested output is either the full
coefficient list up to order n or only the index of the first nonzero
coefficient together with its value.  All arithmetic is carried out with exact
python Fractions via the standard coefficient recurrences, and each computed
answer is verified against the defining identity before it is returned.
"""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


def _rand_frac(max_num, max_den):
    for _ in range(200):
        num = random.randint(-max_num, max_num)
        den = random.randint(1, max_den)
        if num != 0:
            return Fraction(num, den)
    return Fraction(1, 1)


def _rand_series(order, max_num, max_den, const=None):
    out = []
    for i in range(order):
        if i == 0 and const == 0:
            out.append(Fraction(0))
        elif i == 0 and const == "nz":
            out.append(_rand_frac(max_num, max_den))
        elif i == 0 and const is None and random.random() < 0.4:
            out.append(Fraction(0))
        else:
            out.append(_rand_frac(max_num, max_den))
    return out


def _mul(A, B, n):
    C = [Fraction(0)] * n
    for i in range(n):
        ai = A[i]
        if ai == 0:
            continue
        for j in range(n - i):
            C[i + j] += ai * B[j]
    return C


def _comp(A, B, n):
    """Composition A(B(x)) mod x^n; requires B[0] == 0."""
    C = [Fraction(0)] * n
    Bp = [Fraction(0)] * n
    Bp[0] = Fraction(1)
    for i in range(n):
        a = A[i]
        if a != 0:
            for k in range(n):
                C[k] += a * Bp[k]
        if i + 1 < n:
            Bp = _mul(Bp, B, n)
    return C


def _inv(A, n):
    """Multiplicative inverse mod x^n; requires A[0] != 0."""
    C = [Fraction(0)] * n
    C[0] = Fraction(1, 1) / A[0]
    a0 = A[0]
    for k in range(1, n):
        s = Fraction(0)
        for i in range(1, k + 1):
            s += A[i] * C[k - i]
        C[k] = -s / a0
    return C


def _rev(F, n):
    """Compositional inverse (reversion) mod x^n; requires F[0]==0, F[1]!=0."""
    a1 = F[1]
    G = [Fraction(0)] * n
    G[1] = Fraction(1, 1) / a1
    for k in range(2, n):
        Gt = list(G)
        Gt[k] = Fraction(0)
        known = _comp(F, Gt, n)[k]
        G[k] = -known / a1
    return G


def _first_nonzero(C):
    for idx, val in enumerate(C):
        if val != 0:
            return idx, val
    return None


def _fmt_coeffs(C):
    return ", ".join(str(c) for c in C)


def _fmt_series(label, coeffs):
    return (label + " = [" + _fmt_coeffs(coeffs) +
            "] meaning " + label + "(x) = " + " + ".join(
                ("" if c == 0 else f"{c}" if i == 0 else f"{c} x^{i}")
                for i, c in enumerate(coeffs)).strip(" + "))


def _parse_list(s):
    s = s.strip().strip("[]()")
    parts = [p for p in s.replace(",", " ").split() if p.strip()]
    try:
        return tuple(Fraction(p) for p in parts)
    except Exception:
        return None


def _parse_first(s):
    s = s.strip().strip("()")
    parts = [p for p in s.replace(",", " ").split() if p.strip()]
    if len(parts) != 2:
        return None
    try:
        return (int(parts[0]), Fraction(parts[1]))
    except Exception:
        return None


@dataclass
class TruncatedSeriesConfig(Config):
    order: int = 3
    max_num: int = 2
    max_den: int = 3

    def apply_difficulty(self, level):
        self.order = int(3 + 0.8 * level + 0.5)
        self.max_num = 2 + 2 * level
        self.max_den = 2 + level


TASK_META = {'parent_source_id': None,
 'idea': 'truncated_series_operations (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_inference_modes_r4/truncated_series_operations',
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


class TruncatedSeriesOperations(Task):
    summary = ("Formal power series arithmetic mod x^n over rationals: multiply, "
               "compose, invert, and revert series via coefficient recurrences; "
               "answers are the coefficient list at a requested order or the first "
               "nonzero term of the result.")
    design_choice = ("Choose the requested output as either the full coefficient list "
                     "up to a fixed order n, or only the index of the first nonzero "
                     "coefficient and its value, forcing solvers to handle truncation "
                     "differently.")
    config_cls = TruncatedSeriesConfig

    def generate_entry(self):
        order = self.config.order
        max_num = self.config.max_num
        max_den = self.config.max_den
        n = max(2, order)

        for _ in range(100):
            op = random.choice(["multiply", "compose", "invert", "revert"])
            regime = random.choice(["list", "first"])
            if op in ("invert", "revert"):
                regime = "list"

            G = None
            if op == "multiply":
                F = _rand_series(n, max_num, max_den, const=None)
                G = _rand_series(n, max_num, max_den, const=None)
                result = _mul(F, G, n)
            elif op == "compose":
                F = _rand_series(n, max_num, max_den, const=None)
                G = _rand_series(n, max_num, max_den, const=0)
                result = _comp(F, G, n)
            elif op == "invert":
                F = _rand_series(n, max_num, max_den, const="nz")
                result = _inv(F, n)
            else:  # revert
                F = _rand_series(n, max_num, max_den, const=0)
                if n < 2 or F[1] == 0:
                    F[1] = _rand_frac(max_num, max_den)
                result = _rev(F, n)

            if regime == "first":
                fst = _first_nonzero(result)
                if fst is None:
                    continue
                idx, val = fst
                answer = f"{idx} {str(val)}"
                if not (0 <= idx < n and val != 0):
                    continue
            else:
                answer = _fmt_coeffs(result)

            # verify against the defining identity where one exists
            if op == "invert":
                ident = [Fraction(int(i == 0)) for i in range(n)]
                if _mul(F, result, n) != ident:
                    continue
            elif op == "revert":
                ident = [Fraction(int(i == 1)) for i in range(n)]
                if _comp(F, result, n) != ident:
                    continue

            metadata = {
                "operation": op,
                "order": n,
                "F": [str(c) for c in F],
                "G": None if G is None else [str(c) for c in G],
                "output": regime,
            }
            return Entry(metadata=metadata, answer=answer)

        raise RuntimeError("truncated_series_operations: could not build an instance")

    def render_prompt(self, metadata):
        op = metadata["operation"]
        n = metadata["order"]
        F = [Fraction(c) for c in metadata["F"]]
        G = None if metadata["G"] is None else [Fraction(c) for c in metadata["G"]]
        out = metadata["output"]

        lines = []
        lines.append(
            f"We work with formal power series over the rationals, truncated modulo "
            f"x^{n}; only the coefficients at degrees 0..{n - 1} are kept."
        )
        lines.append(_fmt_series("F", F))
        if G is not None:
            lines.append(_fmt_series("G", G))

        if op == "multiply":
            lines.append(f"Compute the product F(x)*G(x) truncated to order {n}.")
            solver = "use the coefficient convolution recurrence"
        elif op == "compose":
            lines.append(
                f"G has zero constant term. Compute the functional composition "
                f"F(G(x)) truncated to order {n} by the recurrence on powers of G."
            )
            solver = "use the composition recurrence"
        elif op == "invert":
            lines.append(
                f"F has nonzero constant term. Compute the multiplicative inverse "
                f"1/F(x) truncated to order {n} by the series inversion recurrence."
            )
            solver = "use the multiplicative inversion recurrence"
        else:  # revert
            lines.append(
                f"F has zero constant term and linear coefficient nonzero. Compute "
                f"the compositional inverse G with F(G(x)) = x, truncated to order "
                f"{n}, via reversion (Lagrange-style coefficient recurrence)."
            )
            solver = "use the reversion recurrence"

        if out == "list":
            lines.append(
                f"Give the first {n} coefficients of the resulting series (degrees "
                f"0..{n - 1}) as a comma-separated list, integers rendered without a "
                f"denominator. Example of the format: "
                f"'1, 2/3, -4, 0'."
            )
        else:
            lines.append(
                f"The result may have leading zero coefficients. Give the index k >= 0 "
                f"of the first nonzero coefficient and its value, separated by a "
                f"space. Example of the format: '2 3/4'. Work out the truncation "
                f"({solver}) and report the leading term."
            )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry["answer"]
        mode = entry["metadata"]["output"]
        if mode == "list":
            g = _parse_list(gold)
            a = _parse_list(answer)
            if g is None or a is None:
                return 0.0
            return 1.0 if a == g else 0.0
        g = _parse_first(gold)
        a = _parse_first(answer)
        if g is None or a is None:
            return 0.0
        return 1.0 if a == g else 0.0

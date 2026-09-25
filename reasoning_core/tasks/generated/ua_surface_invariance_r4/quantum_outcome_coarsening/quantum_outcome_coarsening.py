import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'quantum_outcome_coarsening (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_surface_invariance_r4/quantum_outcome_coarsening',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


I = ((1, 0), (0, 1))
X = ((0, 1), (1, 0))
Z = ((1, 0), (0, -1))
_PAULIS = (I, X, Z)


def _matmul_frac(A, B):
    return tuple(
        tuple(
            sum(A[r][k] * B[k][c] for k in range(2))
            for c in range(2)
        )
        for r in range(2)
    )


def _matadd_frac(A, B):
    return tuple(tuple(A[r][c] + B[r][c] for c in range(2)) for r in range(2))


def _paulcomb(a, b, c):
    return _matadd_frac(
        _matadd_frac(_scal(a, I), _scal(b, X)), _scal(c, Z))


def _scal(s, A):
    return tuple(tuple(s * A[r][c] for c in range(2)) for r in range(2))


def _conjtrans(A):
    return tuple(tuple(A[c][r] for c in range(2)) for r in range(2))


STATE0 = ((1, 0), (0, 0))


def _kraus_output(M, rho0=STATE0):
    Mt = _conjtrans(M)
    return _matmul_frac(_matmul_frac(M, rho0), Mt)


def _frac_str(f):
    return str(f) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def _make_kraus(max_abs):
    while True:
        a, b, c = (random.randint(-max_abs, max_abs) for _ in range(3))
        if (a, b, c) == (0, 0, 0):
            continue
        M = _paulcomb(Fraction(a), Fraction(b), Fraction(c))
        if any(any(x != 0 for x in row) for row in M):
            return M


def _build_instance(max_abs, max_den):
    Ma = _make_kraus(max_abs)
    Mb = _make_kraus(max_abs)
    Ma = _add_denominator(Ma, max_den)
    Mb = _add_denominator(Mb, max_den)
    rho_a = _kraus_output(Ma)
    rho_b = _kraus_output(Mb)
    rho = _matadd_frac(rho_a, rho_b)
    trace = rho[0][0] + rho[1][1]
    if trace <= 0:
        return None
    rho = _scal(Fraction(1) / trace, rho)
    r00, r11 = rho[0][0], rho[1][1]
    r01 = rho[0][1]
    if not (0 <= r00 <= 1 and 0 <= r11 <= 1 and r00 * r11 >= r01 * r01):
        return None
    return Ma, Mb, (r00, r01, r11)


def _add_denominator(M, max_den):
    if max_den <= 1:
        return M
    out = []
    for row in M:
        nrow = []
        for x in row:
            d = random.randint(1, max_den)
            nrow.append(x / d)
        out.append(tuple(nrow))
    return tuple(out)


@dataclass
class QuantumOutcomeCoarseningV1Config(Config):
    max_abs: int = 2
    max_den: int = 1

    def apply_difficulty(self, level):
        self.max_abs = 2 + 2 * level
        self.max_den = max(1, 1 + level)


class QuantumOutcomeCoarsening(Task):
    summary = ("Two-branch qubit instruments from Kraus operators over real Paulis with "
               "rational coefficients: trace out the forgotten outcome and return the "
               "normalized conditional density state as three space-separated fractions.")
    design_choice = ("Instances give a list of Kraus operators for a two-branch instrument; "
                     "the solver must return the normalized conditional state after tracing "
                     "out the forgotten outcome, expressed as a fraction vector.")
    config_cls = QuantumOutcomeCoarseningV1Config
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        inst = None
        for _ in range(200):
            inst = _build_instance(cfg.max_abs, cfg.max_den)
            if inst is not None:
                break
        if inst is None:
            raise RuntimeError("no valid instrument found")
        Ma, Mb, (r00, r01, r11) = inst
        answer = " ".join(_frac_str(f) for f in (r00, r01, r11))
        if not ((0 <= r00 <= 1 and 0 <= r11 <= 1 and r00 * r11 >= r01 * r01)):
            raise RuntimeError("unreachable non-state")
        return Entry(
            metadata={
                "kraus_a": [[_frac_str(Ma[r][c]) for c in range(2)] for r in range(2)],
                "kraus_b": [[_frac_str(Mb[r][c]) for c in range(2)] for r in range(2)],
                "input": "|0>",
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        a = metadata["kraus_a"]
        b = metadata["kraus_b"]
        return (
            "A two-branch quantum instrument acts on the qubit state |0> = (1,0)^T. "
            "Branch 1 applies the Kraus operator A = "
            f"[[{a[0][0]}, {a[0][1]}], [{a[1][0]}, {a[1][1]}]] and branch 2 applies "
            f"B = [[{b[0][0]}, {b[0][1]}], [{b[1][0]}, {b[1][1]}]]. "
            "The outcome of the measurement is forgotten, so after the instrument we hold "
            "the incoherent mixture rho = (A |0><0| A^T + B |0><0| B^T) / p, where p is the "
            "normalization (trace) and A^T is the transpose (all coefficients are real). "
            "Report the normalized conditional state rho as its three independent real "
            "entries [rho00, rho01, rho11] where rho01 = rho10, as three space-separated "
            "fractions (for example '1/2 0 1/2' or '1 0 0'). Give only those three fractions."
        )

    def score_answer(self, answer, entry):
        return _score_state(answer, entry.answer)


def _score_state(answer, gold):
    try:
        parts = [p.strip() for p in str(answer).split()]
        if len(parts) != 3:
            return 0.0
        got = []
        for p in parts:
            if "/" in p:
                n, d = p.split("/")
                if not (n.lstrip("-").isdigit() and d.isdigit() and int(d) != 0):
                    return 0.0
                got.append(int(n) / int(d))
            elif p.lstrip("-").isdigit():
                got.append(int(p))
            else:
                return 0.0
        g = [float(Fraction(x) if "/" in x else int(x)) for x in gold.split()]
        return 1.0 if all(abs(ga - gg) < 1e-9 for ga, gg in zip(got, g)) else 0.0
    except Exception:
        return 0.0

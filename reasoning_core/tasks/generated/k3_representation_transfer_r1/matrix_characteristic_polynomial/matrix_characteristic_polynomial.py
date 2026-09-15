import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'matrix_characteristic_polynomial (draw 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_transfer_r1/matrix_characteristic_polynomial',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 382564971,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


@dataclass
class MatrixCharacteristicPolynomialV2Config(Config):
    n: int = 2

    def apply_difficulty(self, level):
        self.n = min(4, max(2, 2 + (level // 2)))


class MatrixCharacteristicPolynomial(Task):
    summary = ("Compute the exact characteristic polynomial of a small integer matrix from traces "
               "of matrix powers via the Faddeev-LeVerrier recurrence, using only symmetric "
               "matrices with entries in [-3,3] to exploit symmetry, and returning the integer "
               "coefficient vector in ascending degree order (constant term first, leading 1 last).")
    config_cls = MatrixCharacteristicPolynomialV2Config
    design_choice = ("Use only symmetric matrices with entries in [-3,3], forcing trace-based "
                     "computation to exploit symmetry; answer vector in ascending degree order.")

    def generate_entry(self):
        n = self.config.n
        for _ in range(200):
            mat = _draw_symmetric(n)
            if not _has_variation(mat):
                continue
            traces = _faddeev_leverrier(mat, n)
            descending = _coeffs_from_traces(traces, n)
            if _is_constant_answer(descending, n):
                continue
            asc = list(reversed(descending))
            answer = _format_vector(asc)
            return Entry(
                metadata={"n": n, "matrix": mat, "traces": traces,
                          "coeffs": asc, "descending": descending},
                answer=answer,
            )
        raise RuntimeError("matrix_characteristic_polynomial: no valid instance drawn")

    def render_prompt(self, metadata):
        n = metadata["n"]
        traces = metadata["traces"]
        parts = [f"tr(A^{k})={traces[k - 1]}" for k in range(1, n + 1)]
        indices = ", ".join(f"c_{k}" for k in range(n, 0, -1)) + ", 1"
        return (
            f"An unknown n={n} symmetric integer matrix A is characterized only by traces of its "
            f"powers: {', '.join(parts)}. "
            f"Using the Faddeev-LeVerrier recurrence "
            f"(c_k = -(s_k + c_1 s_{{k-1}} + ... + c_{{k-1}} s_1)/k, where s_k = tr(A^k) and "
            f"c_1 = -s_1), "
            f"determine the characteristic polynomial of A. "
            f"Report the coefficient vector in ascending degree order, starting with the constant "
            f"term and ending with the leading coefficient, as the list "
            f"[{indices}]. "
            f"The answer is this list of integers, e.g. [-4, 0, 1] for x^2 - 4."
        )


def _draw_symmetric(n):
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            v = random.randint(-3, 3)
            m[i][j] = v
            m[j][i] = v
    return m


def _matmul(a, b):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def _faddeev_leverrier(mat, n):
    traces = []
    a = mat
    for _ in range(n):
        traces.append(sum(a[i][i] for i in range(n)))
        a = _matmul(a, mat)
    return traces


def _coeffs_from_traces(traces, n):
    c = [0] * (n + 1)
    c[0] = 1
    for k in range(1, n + 1):
        acc = traces[k - 1]
        for i in range(1, k):
            acc += c[i] * traces[k - 1 - i]
        c[k] = -acc // k
    return c


def _has_variation(mat):
    entries = [mat[i][j] for i in range(len(mat)) for j in range(len(mat))]
    return len(set(entries)) >= 2


def _is_constant_answer(coeffs, n):
    return coeffs == [1] + [0] * n


def _format_vector(coeffs):
    return "[" + ", ".join(str(v) for v in coeffs) + "]"


def _parse_vector(s):
    s = s.strip()
    if not (s.startswith("[") and s.endswith("]")):
        raise ValueError("bad format")
    inner = s[1:-1].strip()
    if not inner:
        raise ValueError("empty")
    return [int(t.strip()) for t in inner.split(",")]


def score_answer(answer, entry):
    try:
        got = _parse_vector(answer)
    except Exception:
        return 0.0
    if entry is None:
        return 0.0
    md = entry.metadata if hasattr(entry, "metadata") else entry
    want = md.get("coeffs") if isinstance(md, dict) else getattr(md, "coeffs", None)
    if want is None:
        return 0.0
    if got == list(want):
        return 1.0
    return 0.0

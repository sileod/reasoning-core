import random
from dataclasses import dataclass
from fractions import Fraction

from sympy import Matrix as SymMatrix

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'local_quantum_sufficiency (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_invariants_r4/local_quantum_sufficiency',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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


@dataclass
class LocalQuantumSufficiencyV1Config(Config):
    n_qubits: int = 2
    max_terms: int = 2
    query_cap: int = 1
    denom: int = 3

    def apply_difficulty(self, level):
        self.n_qubits = min(2 + level // 2, 4)
        self.max_terms = 2 + (1 if level >= 3 else 0) + (1 if level >= 6 else 0)
        self.query_cap = min(1 + (1 if level >= 2 else 0) + (1 if level >= 5 else 0),
                             self.n_qubits)
        self.denom = 3 + level


def _frac_str(fr):
    fr = Fraction(fr)
    if fr.denominator == 1:
        return str(fr.numerator)
    return "%d/%d" % (fr.numerator, fr.denominator)


def _unit_qubit(denom):
    m = random.randint(2, denom)
    n = random.randint(1, m - 1)
    D = m * m + n * n
    a = Fraction(m * m - n * n, D)
    b = Fraction(2 * m * n, D)
    if random.random() < 0.5:
        a = -a
    if random.random() < 0.5:
        b = -b
    return a, b


def _tensor_vec(vecs):
    v = [Fraction(1)]
    for w in vecs:
        v = [x * y for x in v for y in w]
    return v


def _outer(v):
    return [[x * y for y in v] for x in v]


def _basis_str(r, keep):
    s = ""
    L = len(keep)
    for j in range(L):
        s += "0" if not ((r >> (L - 1 - j)) & 1) else "1"
    return s


def _assemble(r, t, keep, trac, n):
    idx = 0
    for j in range(n):
        if j in keep:
            bit = (r >> (len(keep) - 1 - keep.index(j))) & 1
        else:
            bit = (t >> (len(trac) - 1 - trac.index(j))) & 1
        idx = (idx << 1) | bit
    return idx


def _partial_trace(M, n, keep):
    kset = set(keep)
    trac = [q for q in range(n) if q not in kset]
    m_keep = 1 << len(keep)
    m_trace = 1 << len(trac)
    result = [[Fraction(0)] * m_keep for _ in range(m_keep)]
    for r in range(m_keep):
        for c in range(m_keep):
            total = Fraction(0)
            for t in range(m_trace):
                total += M[_assemble(r, t, keep, trac, n)][_assemble(c, t, keep, trac, n)]
            result[r][c] = total
    return result


def _ket_amplitudes(term0_states, keep):
    amps = {}
    m = 1 << len(keep)
    for r in range(m):
        amp = Fraction(1)
        for j, q in enumerate(keep):
            bit = (r >> (len(keep) - 1 - j)) & 1
            a, b = term0_states[q]
            amp *= b if bit else a
        amps[_basis_str(r, keep)] = amp
    return amps


def _ket_str(amps):
    terms = []
    for basis in sorted(amps):
        fr = amps[basis]
        if fr == 0:
            continue
        terms.append("%s|%s>" % (_frac_str(fr), basis))
    return "+".join(terms)


def _density_str(rho):
    m = len(rho)
    parts = []
    for r in range(m):
        for c in range(m):
            val = rho[r][c]
            if val == 0:
                continue
            parts.append("(%s,%s)=%s" % (_basis_str(r, list(range(m))), _basis_str(c, list(range(m))), _frac_str(val)))
    return ";".join(parts)


def _rank(rho):
    return SymMatrix([[Fraction(x) for x in row] for row in rho]).rank()


def _build_answer(n, terms_data, probs, query):
    keep = list(query)
    m = 1 << len(keep)
    rho_full = None
    for k, states in enumerate(terms_data):
        v = _tensor_vec([states[q] for q in range(n)])
        d = [[x * y * probs[k] for y in v] for x in v]
        if rho_full is None:
            rho_full = d
        else:
            for i in range(len(d)):
                for j in range(len(d)):
                    rho_full[i][j] += d[i][j]
    rho_S = _partial_trace(rho_full, n, keep)

    tr = sum(rho_S[i][i] for i in range(m))
    if tr != 1:
        return None
    for i in range(m):
        if rho_S[i][i] < 0:
            return None

    if len(terms_data) == 1:
        amps = _ket_amplitudes(terms_data[0], keep)
        ket = _ket_str(amps)
        if not ket:
            return None
        ket_density = _outer([amps[_basis_str(r, keep)] for r in range(m)])
        for i in range(m):
            for j in range(m):
                if ket_density[i][j] != rho_S[i][j]:
                    return None
        return {"answer": ket, "form": "ket"}

    dstr = _density_str(rho_S)
    if not dstr:
        return None
    return {"answer": dstr, "form": "density"}


class LocalQuantumSufficiency(Task):
    summary = ("Extract the reduced state accessible to selected subsystems by partial-tracing "
               "rational pure ket or mixed density descriptions of qubits in varied tensor "
               "orderings, returning a canonical ket when the reduced state is pure and a "
               "canonical density-matrix string when mixed, with subsystems ordered by the "
               "query index list.")
    design_choice = ("return a canonical ket string for the pure reduced state, or a "
                     "density-matrix string for mixed cases, with subsystems ordered by the "
                     "query's index list.")
    config_cls = LocalQuantumSufficiencyV1Config

    def generate_entry(self):
        cfg = self.config
        for _ in range(200):
            n = cfg.n_qubits
            qs = random.randint(1, cfg.query_cap)
            query = random.sample(range(n), qs)
            random.shuffle(query)

            K = random.randint(1, cfg.max_terms)
            terms_data = []
            for _k in range(K):
                states = {q: _unit_qubit(cfg.denom) for q in range(n)}
                terms_data.append(states)
            ns = [random.randint(1, 4) for _ in range(K)]
            total = sum(ns)
            probs = [Fraction(x, total) for x in ns]
            probs[0] += 1 - sum(probs)

            res = _build_answer(n, terms_data, probs, query)
            if res is None:
                continue
            if _rank(self._reduced(terms_data, probs, query, n)) != 1 and res["form"] == "ket":
                continue
            metadata = {
                "n_qubits": int(n),
                "query": [int(q) for q in query],
                "num_terms": int(K),
                "amplitudes": {
                    str(k): {
                        "prob": str(probs[k]),
                        "single": {str(q): [_frac_str(terms_data[k][q][0]),
                                            _frac_str(terms_data[k][q][1])]
                                   for q in range(n)},
                    } for k in range(K)},
                "form": res["form"],
            }
            return Entry(metadata=metadata, answer=res["answer"])
        raise RuntimeError("failed to draw a valid local_quantum_sufficiency example")

    def _reduced(self, terms_data, probs, query, n):
        keep = list(query)
        m = 1 << len(keep)
        rho_full = None
        for k, states in enumerate(terms_data):
            v = _tensor_vec([states[q] for q in range(n)])
            d = [[x * y * probs[k] for y in v] for x in v]
            if rho_full is None:
                rho_full = d
            else:
                for i in range(len(d)):
                    for j in range(len(d)):
                        rho_full[i][j] += d[i][j]
        return _partial_trace(rho_full, n, keep)

    def render_prompt(self, metadata):
        order = ",".join(str(q) for q in metadata["query"])
        desc = []
        for k in range(metadata["num_terms"]):
            amp = metadata["amplitudes"][str(k)]
            prod = " (x) ".join(
                "(%s|0>+%s|1>)_{q%d}" % (amp["single"][str(q)][0], amp["single"][str(q)][1], q)
                for q in range(metadata["n_qubits"])
            )
            desc.append("p%d=%-4s   %s" % (k, amp["prob"], prod))
        state_line = "\n".join(desc)
        return (
            "A two-level system per qubit is described in the computational basis |0>,|1>. "
            "The joint state over %d qubits q0..q%d is the following (already normalized) "
            "convex combination of product pure states, one term per line with its probability "
            "p_k and its tensor product of single-qubit states in the order q0,q1,...:\n%s\n\n"
            "Partially trace out every qubit except the subsystems whose indices are the query "
            "list [%s], kept in exactly that order, to obtain the reduced (marginal) state "
            "accessible to those subsystems. The reduced state is a density operator; when it is "
            "pure (rank one) give it as a ket string whose basis strings are ordered by the query "
            "index list and whose nonzero rational amplitudes appear sorted lexicographically by "
            "basis string, e.g. 3/5|00>+-4/5|11>; when it is mixed give the nonzero density-matrix "
            "entries as (row_basis,col_basis)=value, semicolon-separated and row-major over the "
            "same basis ordering, e.g. (00,00)=1/2;(00,11)=-1/2;(11,00)=-1/2;(11,11)=1/2. "
            "Fractions reduced and signs on the numerator. Give only that ket string or entry "
            "string, nothing else." % (metadata["n_qubits"], metadata["n_qubits"] - 1,
                                       state_line, order)
        )


def score_answer(answer, entry):
    return 1.0 if str(answer).strip() == str(entry["answer"]).strip() else 0.0

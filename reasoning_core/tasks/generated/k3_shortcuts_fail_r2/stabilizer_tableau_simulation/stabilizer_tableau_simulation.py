import random
from dataclasses import dataclass

import numpy as np

from reasoning_core.template import Config, Entry, Task


_PAULIS = (
    np.eye(2, dtype=complex),
    np.array([[0, 1], [1, 0]], dtype=complex),
    np.array([[1, 0], [0, -1]], dtype=complex),
    np.array([[0, -1j], [1j, 0]], dtype=complex),
)
_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_S = np.diag([1, 1j])


def multiply(a, b):
    ra, xa, za = a
    rb, xb, zb = b
    x = [u ^ v for u, v in zip(xa, xb)]
    z = [u ^ v for u, v in zip(za, zb)]
    phase = (2 * (ra + rb) + sum(u * v for u, v in zip(xa, za))
             + sum(u * v for u, v in zip(xb, zb))
             + 2 * sum(u * v for u, v in zip(za, xb))
             - sum(u * v for u, v in zip(x, z))) % 4
    assert phase in (0, 2)
    return [phase // 2, x, z]


def evolve(rows, gates):
    rows = [[r, x[:], z[:]] for r, x, z in rows]
    for gate in gates:
        kind, q = gate[:2]
        for row in rows:
            _, x, z = row
            if kind == "H":
                row[0] ^= x[q] & z[q]
                x[q], z[q] = z[q], x[q]
            elif kind == "S":
                row[0] ^= x[q] & z[q]
                z[q] ^= x[q]
            elif kind == "CNOT":
                t = gate[2]
                row[0] ^= x[q] & z[t] & (x[t] ^ z[q] ^ 1)
                x[t] ^= x[q]
                z[q] ^= z[t]
            else:
                raise ValueError(kind)
    return rows


def group_elements(rows):
    n = len(rows)
    for mask in range(1 << n):
        row = [0, [0] * n, [0] * n]
        for i in range(n):
            if mask & (1 << i):
                row = multiply(row, rows[i])
        yield mask, row


def random_gates(n, count):
    kinds = ["H", "S", "CNOT"] + random.choices(["H", "S", "CNOT"], k=count - 3)
    random.shuffle(kinds)
    return [[kind, *random.sample(range(n), 2)] if kind == "CNOT"
            else [kind, random.randrange(n)] for kind in kinds]


def pauli_matrix(row):
    r, x, z = row
    matrix = np.array([[(-1) ** r]], dtype=complex)
    for a, b in zip(x, z):
        matrix = np.kron(matrix, _PAULIS[a + 2 * b])
    return matrix


def verify_measurement(rows, gates, qubit, basis, outcome):
    n = len(rows)
    dim = 1 << n
    matrices = [pauli_matrix(row) for row in rows]
    state = None
    for j in range(dim):
        candidate = np.eye(dim, dtype=complex)[:, j]
        for matrix in matrices:
            candidate = (candidate + matrix @ candidate) / 2
        norm = np.linalg.norm(candidate)
        if norm > 1e-8:
            state = candidate / norm
            break
    assert state is not None
    assert all(np.allclose(matrix @ state, state) for matrix in matrices)
    for gate in gates:
        kind, q = gate[:2]
        if kind == "CNOT":
            indices = np.arange(dim)
            perm = indices ^ (((indices >> (n - 1 - q)) & 1) << (n - 1 - gate[2]))
            state = state[perm]
        else:
            tensor = np.moveaxis(state.reshape([2] * n), q, 0)
            tensor = (_H if kind == "H" else _S) @ tensor.reshape(2, -1)
            state = np.moveaxis(tensor.reshape([2] * n), 0, q).reshape(-1)
    x, z = [0] * n, [0] * n
    x[qubit], z[qubit] = {"X": (1, 0), "Y": (1, 1), "Z": (0, 1)}[basis]
    assert outcome in (0, 1)
    assert np.allclose(pauli_matrix([0, x, z]) @ state, (-1) ** outcome * state)


@dataclass
class StabilizerTableauSimConfig(Config):
    n_qubits: int = 3
    n_gates: int = 8

    def apply_difficulty(self, level):
        self.n_qubits = min(5, 3 + int(level) // 3)
        self.n_gates = 8 + 3 * int(level)


class StabilizerTableauSimulation(Task):
    summary = "Update varied signed stabilizer tableaux of X/Z bit pairs through Hadamard, phase and CNOT gate sequences, then report a forced single-qubit X, Y or Z measurement outcome as zero or one."
    design_choice = "Answer as a single forced measurement outcome (0 or 1) for a designated qubit, where the tableau is evolved through a random gate sequence and the measurement basis is chosen to be deterministic."
    config_cls = StabilizerTableauSimConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n_qubits
        for _ in range(256):
            rows = [[0, [0] * n, [int(i == j) for j in range(n)]] for i in range(n)]
            rows = evolve(rows, random_gates(n, 5 + 3 * n))
            for _ in range(2 * n):
                a, b = random.sample(range(n), 2)
                rows[a] = multiply(rows[a], rows[b])
            gates = random_gates(n, random.randint(self.config.n_gates, self.config.n_gates + 4))
            final = evolve(rows, gates)
            options = []
            for mask, (_, x, z) in group_elements(final):
                support = [q for q in range(n) if x[q] or z[q]]
                if len(support) == 1 and mask.bit_count() >= 2:
                    q = support[0]
                    options.append((mask, q, {(1, 0): "X", (0, 1): "Z", (1, 1): "Y"}[x[q], z[q]]))
            if not options:
                continue
            mask, qubit, basis = random.choice(options)
            for row in rows:
                row[0] = random.randrange(2)
            final = evolve(rows, gates)
            measured = [0, [0] * n, [0] * n]
            for i, row in enumerate(final):
                if mask & (1 << i):
                    measured = multiply(measured, row)
            outcome = measured[0]
            group = list(group_elements(rows))
            assert len({(tuple(row[1]), tuple(row[2])) for _, row in group}) == 1 << n
            verify_measurement(rows, gates, qubit, basis, outcome)
            return Entry(metadata={"n_qubits": n, "rows": rows, "gates": gates,
                                   "measured_qubit": qubit, "basis": basis}, answer=str(outcome))
        raise RuntimeError("No deterministic local measurement in 256 candidate tableaux")

    def render_prompt(self, metadata):
        n = metadata["n_qubits"]
        names = "ABCDEFG"[:n]
        rows = "; ".join(("-" if r else "+") + " " + " ".join(f"{a}{b}" for a, b in zip(x, z))
                         for r, x, z in metadata["rows"])
        gates = "; ".join(g[0] + " " + " ".join(names[q] for q in g[1:]) for g in metadata["gates"])
        return (
            f"A Clifford-circuit simulator stores {n} independent commuting stabilizer generators. "
            f"The initial pure state is the simultaneous plus-one eigenstate of these signed rows. "
            f"Columns are qubits {', '.join(names)} in that order. Each pair is xz: "
            "00=I, 10=X, 01=Z, 11=Y; the leading sign multiplies the whole tensor product.\n"
            f"Initial rows: {rows}\n"
            f"Apply gates left to right: {gates}\n"
            "H is Hadamard; S=diag(1,i); CNOT lists control then target. "
            "Use the Gottesman-Knill tableau algorithm, tracking signs: conjugate every generator "
            "by each gate, and multiply rows if needed to obtain the measured Pauli. "
            f"Measure {metadata['basis']} on qubit {names[metadata['measured_qubit']]}, with identity "
            "on every other qubit. This measurement is guaranteed deterministic. "
            "Report zero for eigenvalue plus one or one for eigenvalue minus one, as a single digit "
            "(format example: 0). Keep the column order above; there are "
            f"{n} qubits in total."
        )

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip() == entry.answer)


TASK_META = {'parent_source_id': None,
 'idea': 'stabilizer_tableau_simulation (variant 2 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r2/stabilizer_tableau_simulation',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1211525277,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

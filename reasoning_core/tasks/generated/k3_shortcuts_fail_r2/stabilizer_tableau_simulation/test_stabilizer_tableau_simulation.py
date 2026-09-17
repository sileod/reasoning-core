import json
import random
from itertools import product

import numpy as np
import pytest

from reasoning_core.tasks.generated.k3_shortcuts_fail_r2.stabilizer_tableau_simulation import (
    stabilizer_tableau_simulation as mod,
)


def _unitary(gate, n):
    kind, q = gate[:2]
    if kind == "CNOT":
        matrix = np.zeros((1 << n, 1 << n), dtype=complex)
        for col in range(1 << n):
            bits = list(f"{col:0{n}b}")
            if bits[q] == "1":
                bits[gate[2]] = str(1 - int(bits[gate[2]]))
            matrix[int("".join(bits), 2), col] = 1
        return matrix
    local = np.array([[1, 1], [1, -1]]) / np.sqrt(2) if kind == "H" else np.diag([1, 1j])
    matrix = np.array([[1]], dtype=complex)
    for i in range(n):
        matrix = np.kron(matrix, local if i == q else np.eye(2))
    return matrix


def _density_expectation(metadata):
    n = metadata["n_qubits"]
    identity = np.eye(1 << n)
    rho = identity.astype(complex)
    for row in metadata["rows"]:
        rho = rho @ (identity + mod.pauli_matrix(row)) / 2
    assert np.isclose(np.trace(rho), 1)
    assert np.allclose(rho @ rho, rho)
    for gate in metadata["gates"]:
        unitary = _unitary(gate, n)
        rho = unitary @ rho @ unitary.conj().T
    q = metadata["measured_qubit"]
    x, z = [0] * n, [0] * n
    x[q], z[q] = {"X": (1, 0), "Y": (1, 1), "Z": (0, 1)}[metadata["basis"]]
    return np.trace(rho @ mod.pauli_matrix([0, x, z]))


@pytest.mark.parametrize("gate", [["H", 0], ["H", 1], ["S", 0], ["S", 1],
                                 ["CNOT", 0, 1], ["CNOT", 1, 0]])
def test_all_signed_two_qubit_paulis_under_each_gate(gate):
    unitary = _unitary(gate, 2)
    for bits in product(range(2), repeat=5):
        row = [bits[0], list(bits[1:3]), list(bits[3:5])]
        original = json.loads(json.dumps(row))
        updated = mod.evolve([row], [gate])[0]
        assert row == original
        assert np.allclose(mod.pauli_matrix(updated), unitary @ mod.pauli_matrix(row) @ unitary.conj().T)


def test_commuting_row_products():
    rows = [[r, list(x), list(z)] for r in range(2)
            for x in product(range(2), repeat=2) for z in product(range(2), repeat=2)]
    for a, b in product(rows, repeat=2):
        ma, mb = mod.pauli_matrix(a), mod.pauli_matrix(b)
        if np.allclose(ma @ mb, mb @ ma):
            assert np.allclose(mod.pauli_matrix(mod.multiply(a, b)), ma @ mb)
        else:
            with pytest.raises(AssertionError):
                mod.multiply(a, b)


def test_gold_and_independent_density_simulation():
    random.seed(999)
    task = mod.StabilizerTableauSimulation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(8):
            entry = task.generate_example()
            assert entry.answer in ("0", "1")
            assert np.isclose(_density_expectation(entry.metadata), (-1) ** int(entry.answer))
            assert task.score_answer(entry.answer, entry) == 1
            for bad in ("", "junk", "01", "0.0", str(1 - int(entry.answer)), None):
                assert task.score_answer(bad, entry) == 0
            restored = json.loads(json.dumps(entry.metadata))
            assert task.render_prompt(restored) == task.render_prompt(entry.metadata)


def test_balanced_labels_and_varied_bases_at_every_level():
    random.seed(4242)
    task = mod.StabilizerTableauSimulation()
    for level in range(7):
        task.config.set_level(level)
        entries = [task.generate_entry() for _ in range(100)]
        assert 30 <= sum(int(e.answer) for e in entries) <= 70
        assert {e.metadata["basis"] for e in entries} == {"X", "Y", "Z"}
        assert len({task.render_prompt(e.metadata) for e in entries}) == 100


def test_level_scaling_and_mock_scorer():
    task = mod.StabilizerTableauSimulation()
    sizes = []
    for level in range(7):
        task.config.set_level(level)
        sizes.append((task.config.n_qubits, task.config.n_gates))
    assert all(a[0] <= b[0] and a[1] < b[1] for a, b in zip(sizes, sizes[1:]))
    entry = task.generate_entry()
    assert mod.StabilizerTableauSimulation.score_answer(None, entry.answer, entry) == 1


def test_verifier_rejects_wrong_and_random_outcomes():
    rows = [[0, [0, 0], [1, 0]], [0, [0, 0], [0, 1]]]
    mod.verify_measurement(rows, [], 0, "Z", 0)
    with pytest.raises(AssertionError):
        mod.verify_measurement(rows, [], 0, "Z", 1)
    with pytest.raises(AssertionError):
        mod.verify_measurement(rows, [["H", 0]], 0, "Z", 0)

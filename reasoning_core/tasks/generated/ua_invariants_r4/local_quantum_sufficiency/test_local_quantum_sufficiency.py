import random
from fractions import Fraction

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_invariants_r4.local_quantum_sufficiency.local_quantum_sufficiency import (
    LocalQuantumSufficiency,
    score_answer,
)


def test_gold_scores_one():
    t = LocalQuantumSufficiency()
    for _ in range(20):
        x = t.generate_example()
        assert score_answer(x.answer, x) == 1.0


def test_junk_and_empty_not_one():
    t = LocalQuantumSufficiency()
    x = t.generate_example()
    for bad in ("", "junk", "1/2|0>", "import os", "   "):
        assert score_answer(bad, x) < 1.0


def test_levels_vary_and_valid():
    t = LocalQuantumSufficiency()
    configs = []
    for level in range(7):
        t.config.set_level(level)
        x = t.generate_example()
        assert score_answer(x.answer, x) == 1.0
        cfg = (t.config.n_qubits, t.config.max_terms, t.config.query_cap)
        configs.append(cfg)
    assert len(set(configs)) > 1


def test_reduced_state_is_domain_valid():
    t = LocalQuantumSufficiency()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(10):
            x = t.generate_example()
            n = x.metadata["n_qubits"]
            query = x.metadata["query"]
            m = 1 << len(query)
            amp = x.metadata["amplitudes"]
            probs = [Fraction(amp[str(k)]["prob"]) for k in range(x.metadata["num_terms"])]
            assert abs(sum(probs) - 1) < 1e-12
            for k in range(x.metadata["num_terms"]):
                for q in range(n):
                    a = Fraction(amp[str(k)]["single"][str(q)][0])
                    b = Fraction(amp[str(k)]["single"][str(q)][1])
                    assert a * a + b * b == 1
                    assert a > 0 or a <= 0


def test_both_pure_and_mixed_form_appear():
    t = LocalQuantumSufficiency()
    forms = set()
    for _ in range(60):
        x = t.generate_example()
        forms.add(x.metadata["form"])
    assert forms == {"ket", "density"}


def test_deterministic_under_seed():
    random.seed(12345)
    t1 = LocalQuantumSufficiency()
    e1 = t1.generate_example()
    random.seed(12345)
    t2 = LocalQuantumSufficiency()
    e2 = t2.generate_example()
    assert e1.answer == e2.answer
    assert e1.prompt == e2.prompt


def test_entry_is_entry_with_metadata():
    t = LocalQuantumSufficiency()
    x = t.generate_example()
    assert isinstance(x, Entry)
    assert x.answer
    assert x.prompt

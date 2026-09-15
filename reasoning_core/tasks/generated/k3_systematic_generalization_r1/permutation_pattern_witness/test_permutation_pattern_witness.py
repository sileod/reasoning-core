import random

from reasoning_core.tasks.generated.k3_systematic_generalization_r1.permutation_pattern_witness.permutation_pattern_witness import (
    contains_with_witness,
    PermutationPatternWitness,
)


def test_generate_gold():
    random.seed(42)
    t = PermutationPatternWitness()
    for _ in range(50):
        e = t.generate_entry()
        assert t.score_answer(e.answer, e) == 1.0


def test_score_rejects_junk():
    random.seed(1)
    t = PermutationPatternWitness()
    for _ in range(30):
        e = t.generate_entry()
        assert t.score_answer("", e) < 1.0
        assert t.score_answer("garbage", e) < 1.0
        assert t.score_answer(None, e) < 1.0


def test_label_balance():
    random.seed(7)
    t = PermutationPatternWitness()
    yes = 0
    total = 300
    for _ in range(total):
        e = t.generate_entry()
        if e.metadata["contains"]:
            yes += 1
    frac = yes / total
    assert 0.5 < frac < 0.9


def test_witness_correctness_against_bruteforce():
    import itertools

    random.seed(5)
    n = 8
    for _ in range(300):
        text = list(range(1, n + 1))
        random.shuffle(text)
        k = 4
        chosen = sorted(random.sample(range(n), k))
        pat = [text[c] for c in chosen]
        g = contains_with_witness(text, pat)
        best = None
        for combo in itertools.combinations(range(n), k):
            if all(text[c] == pat[i] for i, c in enumerate(combo)):
                if best is None or combo < best:
                    best = combo
        assert g == list(best)


def test_negative_is_really_absent():
    import itertools

    random.seed(9)
    t = PermutationPatternWitness()
    for _ in range(40):
        e = t.generate_entry()
        if not e.metadata["contains"]:
            pat = e.metadata["pattern"]
            text = e.metadata["text"]
            k = len(pat)
            n = len(text)
            for combo in itertools.combinations(range(n), k):
                assert not all(text[c] == pat[i] for i, c in enumerate(combo))


def test_levels_produce_examples():
    t = PermutationPatternWitness()
    for level in range(7):
        t.config.set_level(level)
        random.seed(int(level))
        e = t.generate_entry()
        assert t.score_answer(e.answer, e) == 1.0

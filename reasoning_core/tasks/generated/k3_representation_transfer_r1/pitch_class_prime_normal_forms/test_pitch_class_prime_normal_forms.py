from reasoning_core.tasks.generated.k3_representation_transfer_r1.pitch_class_prime_normal_forms.pitch_class_prime_normal_forms import (
    PitchClassPrimeNormalForms,
    _prime_form,
    _symmetric,
)


def test_prime_form_starts_on_zero():
    for _ in range(200):
        entry = PitchClassPrimeNormalForms().generate_example()
        assert entry.metadata["prime_form"][0] == 0


def test_prime_form_size_matches():
    for _ in range(200):
        entry = PitchClassPrimeNormalForms().generate_example()
        assert len(entry.metadata["prime_form"]) == len(entry.metadata["pcs"])


def test_prime_form_is_contained_form():
    for _ in range(200):
        entry = PitchClassPrimeNormalForms().generate_example()
        pf = entry.metadata["prime_form"]
        pcs = entry.metadata["pcs"]
        origins = {tuple(sorted(pcs))}
        origins.add(tuple(sorted((12 - x) % 12 for x in pcs)))
        found = False
        for base in origins:
            for start in range(len(base)):
                seq = [base[(start + i) % len(base)] for i in range(len(base))]
                seq = [(x - seq[0]) % 12 for x in seq]
                if tuple(seq) == tuple(pf):
                    found = True
        assert found


def test_score_answer_gold():
    task = PitchClassPrimeNormalForms()
    for _ in range(100):
        entry = task.generate_example()
        assert task.score_answer(str(entry.metadata["prime_form"]), entry) == 1.0


def test_score_answer_junk():
    task = PitchClassPrimeNormalForms()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("garbage", entry) == 0.0
    assert task.score_answer("[0, 0, 0]", entry) == 0.0


def test_symmetric_detection():
    assert _symmetric([0, 6])
    assert _symmetric([0, 4, 8])
    assert not _symmetric([0, 1, 2])

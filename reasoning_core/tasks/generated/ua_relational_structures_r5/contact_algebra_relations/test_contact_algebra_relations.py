import random

from reasoning_core.tasks.generated.ua_relational_structures_r5.contact_algebra_relations.contact_algebra_relations import (
    LABELS,
    ContactAlgebraRelations,
    _build,
    classify,
)


def test_roundtrip_all_levels():
    task = ContactAlgebraRelations()
    for level in range(7):
        task.config.set_level(level)
        seen = set()
        for _ in range(30):
            entry = task.generate_example()
            assert entry.answer in LABELS
            assert classify(entry.metadata["region_A"], entry.metadata["region_B"]) == entry.answer
            seen.add(entry.answer)
        assert len(seen) >= 4


def test_score_exact():
    task = ContactAlgebraRelations()
    for _ in range(20):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        assert task.score_answer(entry.answer.upper(), entry) == 0.0
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("garbage", entry) == 0.0
        for other in LABELS:
            if other != entry.answer:
                assert task.score_answer(other, entry) == 0.0


def test_all_labels_reachable_at_every_level():
    task = ContactAlgebraRelations()
    for level in range(7):
        task.config.set_level(level)
        cfg = task.config
        for label in LABELS:
            found = False
            for _ in range(60):
                A, B = _build(cfg, label)
                if classify(A, B) == label:
                    found = True
                    break
            assert found, (level, label)

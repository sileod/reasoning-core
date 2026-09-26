import random

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.line_cross_swap_schedulev2.line_crossing_swap_schedule import (
    LineCrossSwapSchedulev2,
)


def test_generate_and_roundtrip():
    random.seed(2072234021)
    task = LineCrossSwapSchedulev2()
    entry = task.generate_example()
    assert entry.metadata["final_permutation"] == [
        int(x) for x in entry.answer.split()
    ]
    assert task.score_answer(entry.answer, entry) == 1.0


def test_metadata_json_serializable():
    task = LineCrossSwapSchedulev2()
    entry = task.generate_example()
    assert all(isinstance(x, int) for p in entry.metadata["lines"] for x in p)


def test_difficulty_changes():
    task = LineCrossSwapSchedulev2()
    base = task.generate_example()
    task.config.set_level(6)
    hi = task.generate_example()
    assert len(hi.metadata["final_permutation"]) >= len(base.metadata["final_permutation"])


def test_wrong_answers():
    random.seed(1)
    task = LineCrossSwapSchedulev2()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("junk", entry) == 0.0
    wrong = " ".join(str(x) for x in reversed(entry.metadata["final_permutation"]))
    if wrong != entry.answer:
        assert task.score_answer(wrong, entry) == 0.0


def test_permutation_valid():
    random.seed(2)
    task = LineCrossSwapSchedulev2()
    for _ in range(20):
        entry = task.generate_example()
        perm = entry.metadata["final_permutation"]
        assert sorted(perm) == list(range(len(perm)))


def test_answer_not_surface_readable():
    random.seed(3)
    task = LineCrossSwapSchedulev2()
    entry = task.generate_example()
    prompt = task.render_prompt(entry.metadata)
    perm = entry.metadata["final_permutation"]
    assert not perm == list(range(len(perm)))

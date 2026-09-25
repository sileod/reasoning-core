import random

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.intransitive_information_purge.intransitive_information_purge import (
    IntransitiveInformationPurge,
    PurgeConfig,
    _purged_indices,
)


def test_prompt_determines_answer():
    task = IntransitiveInformationPurge()
    for _ in range(20):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_balanced_labels():
    random.seed(1234)
    task = IntransitiveInformationPurge()
    counts = {}
    for _ in range(200):
        e = task.generate_example()
        counts[e.answer] = counts.get(e.answer, 0) + 1
    # not all the same answer
    assert len(counts) > 5


def test_garbage_rejected():
    task = IntransitiveInformationPurge()
    e = task.generate_example()
    assert task.score_answer("", e) < 1.0
    assert task.score_answer("9999", e) < 1.0
    assert task.score_answer("garbage", e) < 1.0


def test_difficulty_changes():
    c = PurgeConfig()
    c.set_level(5)
    assert c.n_actions > PurgeConfig().n_actions

def test_verifier_matches_generator():
    for _ in range(50):
        s = random.randrange(0, 5)
        o = random.randrange(1, 6)
        acts = [(random.randrange(0, 5), random.randrange(1, 6)) for _ in range(8)]
        keep = _purged_indices(acts, 6)
        # each kept source must reach observer
        for i in keep:
            reachable = {acts[i][0]}
            changed = True
            while changed:
                changed = False
                for j in range(i + 1, len(acts)):
                    a, b = acts[j]
                    if a in reachable and b not in reachable:
                        reachable.add(b)
                        changed = True
            assert 5 in reachable, (i, acts)

import random

from reasoning_core.tasks.generated.ua_dynamic_structures_r5.orbital_impulse_rebaselining.orbital_impulse_rebaselining import (
    OrbitalImpulseRebaselining,
    _gold_vals,
)


def test_gold_scores_1():
    task = OrbitalImpulseRebaselining()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_garbage_scores_0():
    task = OrbitalImpulseRebaselining()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("garbage", ex) == 0.0
        assert task.score_answer(None, ex) == 0.0
        assert task.score_answer(123, ex) == 0.0


def test_positive_h():
    task = OrbitalImpulseRebaselining()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            g = _gold_vals(ex.metadata)
            assert g["h"] > 0 if "h" in g else True
            if "rp" in g:
                assert g["rp"] > 0
            if "ra" in g:
                assert g["ra"] > g["rp"]


def test_answer_not_surface():
    task = OrbitalImpulseRebaselining()
    task.config.set_level(1)
    for _ in range(30):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        words = prompt.split()
        assert not prompt.rstrip().endswith(ex.answer)
        assert ex.answer.split()[0] not in words[:2]


def test_deterministic_seed():
    random.seed(7)
    t1 = OrbitalImpulseRebaselining()
    e1 = t1.generate_example()
    random.seed(7)
    t2 = OrbitalImpulseRebaselining()
    e2 = t2.generate_example()
    assert e1.answer == e2.answer
    assert e1.metadata["mode"] == e2.metadata["mode"]


def test_type_variety_at_each_level():
    task = OrbitalImpulseRebaselining()
    for level in (0, 3, 6):
        task.config.set_level(level)
        seen = set()
        for _ in range(100):
            ex = task.generate_example()
            g = _gold_vals(ex.metadata)
            if "type" in g:
                seen.add(g["type"])
        assert len(seen) >= 3

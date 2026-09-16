import random

from reasoning_core.tasks.generated.k3_relational_structures_r1.kinship_relation_resolution.kinship_relation_resolution import (
    KinshipConfig,
    KinshipRelationResolution,
)


def test_config_scales():
    cfg = KinshipConfig()
    low = cfg.depth
    cfg.set_level(6)
    assert cfg.depth >= low
    assert cfg.branch >= KinshipConfig().branch


def test_gold_scores_one():
    task = KinshipRelationResolution()
    for _ in range(40):
        task.config.set_level(random.randint(0, 6))
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_bad_answers_fail():
    task = KinshipRelationResolution()
    task.config.set_level(3)
    for _ in range(30):
        ex = task.generate_example()
        assert task.score_answer("zzz not a real designation", ex) == 0.0
        assert task.score_answer("", ex) == 0.0
        other = {"first cousins", "second cousins", "third cousins"} - {ex.answer.lower()}
        if other:
            assert task.score_answer(sorted(other)[0], ex) < 1.0


def test_all_levels_generate():
    task = KinshipRelationResolution()
    seen = set()
    for level in range(0, 7):
        task.config.set_level(level)
        for _ in range(10):
            ex = task.generate_example()
            task.score_answer(ex.answer, ex) == 1.0
            seen.add(ex.answer)
    assert len(seen) > 2


def test_answer_domain():
    task = KinshipRelationResolution()
    for level in range(0, 7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            md = ex.metadata
            assert md["depth_a"] >= 1
            assert md["depth_b"] >= 1
            assert ex.answer == md["designation"]


def _independent_designation(parents, a, b):
    def line(person):
        out, cur = [], person
        while cur is not None:
            out.append(cur)
            cur = parents.get(cur)
        return out

    la, lb = line(a), line(b)
    common = set(la) & set(lb)
    best = min(common, key=lambda c: la.index(c) + lb.index(c))
    da, db = la.index(best), lb.index(best)
    dg = min(da, db)
    rv = abs(da - db)
    degree = {1: "first", 2: "second", 3: "third", 4: "fourth",
              5: "fifth", 6: "sixth"}.get(dg, f"{dg}th")
    if rv == 0:
        return f"{degree} cousins"
    if rv == 1:
        return f"{degree} cousins once removed"
    return f"{degree} cousins {rv} times removed"


def test_gold_is_reality():
    task = KinshipRelationResolution()
    for level in range(0, 7):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            md = ex.metadata
            parents = dict(md["parents"])
            expected = _independent_designation(parents, md["a"], md["b"])
            assert expected == md["designation"]
            assert expected == ex.answer


def test_metadata_json_serializable():
    import json

    task = KinshipRelationResolution()
    for level in range(0, 7):
        task.config.set_level(level)
        ex = task.generate_example()
        json.dumps(task.generate_example().to_dict())

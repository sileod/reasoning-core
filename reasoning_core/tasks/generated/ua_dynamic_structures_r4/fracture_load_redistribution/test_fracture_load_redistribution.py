import random

from reasoning_core.tasks.generated.ua_dynamic_structures_r4.fracture_load_redistribution.fracture_load_redistribution import (
    FractureLoadRedistribution,
    _run,
)


def test_gold_scores_1():
    task = FractureLoadRedistribution()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_survivors_positive_load():
    task = FractureLoadRedistribution()
    for _ in range(20):
        ex = task.generate_example()
        metadata = ex.metadata
        answer = ex.answer
        pairs = [p.split("=") for p in answer.split(";")]
        labels = {p[0] for p in pairs}
        assert all(p[0] in metadata["labels"] for p in pairs)
        assert all(p[1].isdigit() and int(p[1]) >= 0 for p in pairs)
        assert labels.issubset(set(metadata["labels"]))


def test_garbage_scores_0():
    task = FractureLoadRedistribution()
    for _ in range(10):
        ex = task.generate_example()
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("garbage", ex) == 0.0
        assert task.score_answer(None, ex) == 0.0
        assert task.score_answer(123, ex) == 0.0


def test_deterministic_seed():
    random.seed(42)
    t1 = FractureLoadRedistribution()
    e1 = t1.generate_example()
    random.seed(42)
    t2 = FractureLoadRedistribution()
    e2 = t2.generate_example()
    assert e1.answer == e2.answer


def test_answer_not_last_number():
    task = FractureLoadRedistribution()
    task.config.set_level(1)
    for _ in range(30):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        ans = ex.answer
        assert not prompt.rstrip().endswith(ans)


def test_survivor_loads_below_threshold():
    task = FractureLoadRedistribution()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            metadata = ex.metadata
            surviving = {}
            for p in ex.answer.split(";"):
                lab, val = p.split("=")
                surviving[lab] = int(val)
            for lab in surviving:
                assert surviving[lab] <= metadata["thresholds"][lab]
            for lab in metadata["labels"]:
                assert (lab in surviving) == (surviving.get(lab) is not None)


def test_run_match_metadata_order():
    task = FractureLoadRedistribution()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            m = ex.metadata
            edges = {lab: list(m["edges"][lab]) for lab in m["labels"]}
            active, load = _run(
                list(m["labels"]),
                edges,
                dict(m["thresholds"]),
                dict(m["initial_load"]),
                list(m["increments"]),
                list(m["removals"]),
            )
            expect = ";".join(
                f"{lab}={int(load[lab])}"
                for lab in sorted(m["labels"], key=lambda x: int(x[1:]))
                if lab in active
            )
            assert expect == ex.answer

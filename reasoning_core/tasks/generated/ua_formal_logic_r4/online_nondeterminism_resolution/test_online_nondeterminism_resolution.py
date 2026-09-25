import random

random.seed(798610012)

from reasoning_core.tasks.generated.ua_formal_logic_r4.online_nondeterminism_resolution import online_nondeterminism_resolution as mod


def test_generate_and_score():
    task = mod.OnlineNondeterminismResolution()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert ex.answer in ("yes", "no")
            assert task.score_answer(ex.answer, ex) == 1.0
            assert task.score_answer(ex.answer.upper(), ex) == 1.0
            assert task.score_answer("", ex) == 0.0
            assert task.score_answer("maybe", ex) == 0.0
            md = ex.metadata
            needed = md["needed"]
            max_bound = md["max_bound"]
            assert (ex.answer == "yes") == (needed <= max_bound)


def test_balance_labels():
    task = mod.OnlineNondeterminismResolution()
    from collections import Counter
    for level in (0, 2, 5):
        task.config.set_level(level)
        c = Counter()
        for _ in range(60):
            ex = task.generate_example()
            c[ex.answer] += 1
        assert c.get("yes", 0) > 0 and c.get("no", 0) > 0
        tot = c["yes"] + c["no"]
        excess = abs(c["yes"] - c["no"]) / tot
        assert excess <= 0.6, (level, c)


def test_metadata_json_serializable():
    import json
    task = mod.OnlineNondeterminismResolution()
    for level in (0, 6):
        task.config.set_level(level)
        ex = task.generate_example()
        json.dumps(ex.metadata)

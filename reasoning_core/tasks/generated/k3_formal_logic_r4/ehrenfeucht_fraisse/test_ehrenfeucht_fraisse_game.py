import random

from reasoning_core.tasks.generated.k3_formal_logic_r4.ehrenfeucht_fraisse_game \
    import ehrenfeucht_fraisse_game as m
from reasoning_core.template import Task


def test_gold_scoring():
    random.seed(1)
    task = m.EhrenfeuchtFraisseV2()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert ex.answer in ("Duplicator",) or ex.answer.startswith("Spoiler; ")


def test_all_levels_produce_both_outcomes():
    random.seed(2)
    task = m.EhrenfeuchtFraisseV2()
    for level in (0, 2, 5):
        seen_spoiler = seen_duplicator = False
        for _ in range(60):
            ex = task.generate_example(level=level)
            if ex.answer == "Duplicator":
                seen_duplicator = True
            else:
                seen_spoiler = True
        assert seen_spoiler, f"level {level} never produced a Spoiler win"
        assert seen_duplicator, f"level {level} never produced a Duplicator win"


def test_metadata_json_roundtrip():
    import json
    random.seed(3)
    task = m.EhrenfeuchtFraisseV2()
    ex = task.generate_example(level=5)
    assert isinstance(json.loads(json.dumps(dict(ex.metadata))), dict)


def test_prompt_is_concise():
    random.seed(4)
    task = m.EhrenfeuchtFraisseV2()
    ex6 = task.generate_example(level=6)
    assert len(task.tokenizer.encode(ex6.prompt)) <= 2048

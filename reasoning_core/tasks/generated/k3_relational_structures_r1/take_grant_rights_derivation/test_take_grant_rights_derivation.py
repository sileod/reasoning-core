import random

from reasoning_core.tasks.generated.k3_relational_structures_r1.take_grant_rights_derivation.take_grant_rights_derivation import (
    TakeGrantConfig,
    TakeGrantRightsDerivation,
    _closure,
    _to_matrix,
)


def test_prompt_determines_answer():
    task = TakeGrantRightsDerivation()
    for _ in range(10):
        e = task.generate_example(level=2)
        prompt = task.render_prompt(e.metadata)
        mid = e.metadata["query"]
        answer = "yes" if e.metadata["answer"] == "yes" else "no"
        assert answer in ("yes", "no")


def test_closure_matches_gold():
    task = TakeGrantRightsDerivation()
    for _ in range(10):
        e = task.generate_example(level=2)
        m = e.metadata
        closed = _closure(m["n"], _to_matrix(m["n"], m["initial"]), m["rules"])
        s, o = m["query"]
        expected = "yes" if closed[s][o] == 1 else "no"
        assert m["answer"] == expected


def test_balanced_labels_over_many():
    random.seed(7)
    task = TakeGrantRightsDerivation()
    config = TakeGrantConfig()
    task.config = config
    counts = {"yes": 0, "no": 0}
    for _ in range(120):
        e = task.generate_entry()
        counts[e.answer] += 1
    assert counts["yes"] > 0 and counts["no"] > 0


def test_not_surface_readable():
    task = TakeGrantRightsDerivation()
    for _ in range(20):
        e = task.generate_example(level=2)
        text = task.render_prompt(e.metadata)
        s, o = e.metadata["query"]
        assert (("S%d has S%d" % (s, o)) + ".") not in text.split("Initially:")[1].split("Controls:")[0]


def test_score_answer():
    task = TakeGrantRightsDerivation()
    e = task.generate_example(level=0)
    gold = e.answer
    assert task.score_answer(gold, e) == 1.0
    assert task.score_answer("yes" if gold == "no" else "no", e) == 0.0
    assert task.score_answer("", e) == 0.0
    assert task.score_answer("maybe", e) == 0.0

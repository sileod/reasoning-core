import json
import pickle

import pytest

from reasoning_core.decision import Decision, jev_row
from reasoning_core.template import Entry


def _decisions():
    return [Decision("B", instructions="Pick", criteria={"A": None, "B": "bee"},
                     soft={"A": 0.25, "B": 0.75}),
            Decision("yes", instructions="Spam?", type="noul", soft=0.8),
            Decision(2, instructions="Rate", criteria=["low", "mid", "high"], type="score")]


@pytest.mark.parametrize("d", _decisions())
def test_decision_is_the_answer_string_and_survives_round_trips(d):
    assert d == {"choice": "B", "noul": "Yes", "score": "2"}[d.question["type"]]
    entry = Entry({"decision": d.to_dict()}, d)
    back = Entry.from_dict(json.loads(json.dumps(entry.to_dict())))
    assert isinstance(back.answer, Decision) and back.answer.to_dict() == d.to_dict()
    assert pickle.loads(pickle.dumps(d)).to_dict() == d.to_dict()


@pytest.mark.parametrize("kw", [dict(label="Z", criteria={"A": None}),
                                dict(label="A", criteria={"A": None}, soft={"A": 0.5}),
                                dict(label="A", criteria={"A": None}, type="vote")])
def test_decision_rejects_invalid_specs(kw):
    with pytest.raises(ValueError):
        Decision(kw.pop("label"), instructions="", **kw)


def test_state_seed_reproduces_the_state_and_groups_rows():
    import random
    from reasoning_core import get_task
    t = get_task("hidden_source")
    random.seed(0)
    a = t.generate_example(level=3, state_seed=7)
    random.seed(1)   # a different global RNG: the state comes from the seed alone
    b = t.generate_example(level=3, state_seed=7)
    assert a.metadata.payload == b.metadata.payload and a.answer.to_dict() == b.answer.to_dict()
    ra, rb = jev_row(a), jev_row(b)
    assert ra["id"].split(":")[:3] == rb["id"].split(":")[:3] == ["hidden_source", "3", "7"]
    assert all(isinstance(v, str) for v in ra.values()) and json.loads(ra["question"])["type"] == ra["primitive"]

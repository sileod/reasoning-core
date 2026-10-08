import json
import pickle

import pytest

from reasoning_core.template import Decision, Entry


def _decisions():
    return [Decision("B", state={"q": "x"}, instructions="Pick", criteria={"A": None, "B": "bee"},
                     soft={"A": 0.25, "B": 0.75}),
            Decision("yes", state="msg", instructions="Spam?", type="noul", soft=0.8),
            Decision(2, state="s", instructions="Rate", criteria=["low", "mid", "high"], type="score")]


@pytest.mark.parametrize("d", _decisions())
def test_decision_is_the_answer_string_and_survives_round_trips(d):
    assert d == {"choice": "B", "noul": "Yes", "score": "2"}[d.question["type"]]
    entry = Entry({"decision": d.to_dict()}, d)
    back = Entry.from_dict(json.loads(json.dumps(entry.to_dict())))
    assert isinstance(back.answer, Decision) and back.answer.to_dict() == d.to_dict()
    assert pickle.loads(pickle.dumps(d)).to_dict() == d.to_dict()
    row = d.jev_row()
    assert all(isinstance(v, str) for v in row.values()) and json.loads(row["question"])["type"] == row["primitive"]


@pytest.mark.parametrize("kw", [dict(label="Z", criteria={"A": None}),
                                dict(label="A", criteria={"A": None}, soft={"A": 0.5}),
                                dict(label="A", criteria={"A": None}, type="vote")])
def test_decision_rejects_invalid_specs(kw):
    with pytest.raises(ValueError):
        Decision(kw.pop("label"), state="", instructions="", **kw)

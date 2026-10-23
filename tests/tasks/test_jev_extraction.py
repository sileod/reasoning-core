import json

import pytest

from reasoning_core import get_task, score_answer
from reasoning_core.decision import Extraction, extraction_row, score_extraction
from reasoning_core.template import Entry

TASKS = ["record_field_extraction", "state_update_extraction", "conditional_list_extraction", "log_query_extraction",
         "typed_mention_extraction", "business_document_extraction", "nested_structure_extraction", "html_extraction", "date_range_extraction", "spec_match_extraction",
         "lookalike_field_extraction"]


@pytest.mark.parametrize("name", TASKS)
def test_gold_spans_are_verbatim_and_score_one(name):
    task = get_task(name)
    for level in (0, 4):
        for seed in range(15):
            x = task.generate_example(level=level, state_seed=seed)
            row = extraction_row(x)
            for field, answer in zip(row["fields"], row["answers"]):
                assert answer["null"] == (not answer["values"])
                assert all(row["state"][v["start"]:v["end"]] == v["text"] for v in answer["values"])
            assert score_answer(x.answer, x.to_dict()) == 1
            back = Entry.from_dict(json.loads(json.dumps(x.to_dict(), default=str)))
            assert isinstance(back.answer, Extraction) and back.answer == x.answer
            assert x == task.generate_example(level=level, state_seed=seed) or \
                x.metadata.payload == task.generate_example(level=level, state_seed=seed).metadata.payload


def test_score_extraction_gives_per_field_credit():
    gold = json.dumps({"city": "Lima", "ids": ["K-1", "K-2"], "phone": None})
    assert score_extraction(gold, gold) == 1
    assert score_extraction('```json\n{"city": "lima.", "ids": ["K-2", "K-1"], "phone": null}\n```', gold) == 1
    assert score_extraction('{"city": "Quito", "ids": ["K-1"], "phone": "123"}', gold) == pytest.approx((2 / 3) / 3)
    assert score_extraction("no json", gold) == 0


def test_extraction_rejects_two_values_for_a_text_field():
    fields = [{"name": "city", "type": "text", "instruction": "The city."}]
    with pytest.raises(ValueError):
        Extraction("Lima or Quito", fields, {"city": [(0, 4), (8, 13)]})

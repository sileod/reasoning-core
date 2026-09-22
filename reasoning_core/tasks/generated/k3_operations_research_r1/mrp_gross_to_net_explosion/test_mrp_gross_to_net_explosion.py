import copy
import json
import random

import pytest

from reasoning_core.tasks.generated.k3_operations_research_r1.mrp_gross_to_net_explosion.mrp_gross_to_net_explosion import (
    MrpExplosionConfig,
    MrpGrossToNetExplosion,
    format_schedule,
    parse_schedule,
    solve_mrp,
    verify_schedule,
)


def diamond():
    return {
        "item_names": list("ABCD"), "horizon": 8,
        "bom": [["A", "B", 2], ["A", "C", 1], ["B", "D", 1], ["C", "D", 2]],
        "onhand": {"A": 1, "B": 3, "C": 2, "D": 4},
        "lead": {"A": 1, "B": 2, "C": 1, "D": 1},
        "lot": {"A": 4, "B": 5, "C": 1, "D": 6},
        "demand": [[6, "A", 10], [8, "A", 3]],
        "receipts": [[6, "A", 2], [5, "B", 2], [3, "D", 3]],
    }


def test_shared_component_hand_computed_plan():
    m = diamond()
    expected = "(2,D,12);(3,B,15);(3,D,12);(4,C,6);(4,D,6);(5,A,8);(5,B,5);(5,D,6);(6,C,4);(7,A,4)"
    assert format_schedule(solve_mrp(m)) == expected
    verify_schedule(m, parse_schedule(expected))


@pytest.mark.parametrize("mutation", ["quantity", "period", "missing", "extra", "duplicate", "reversed"])
def test_verifier_rejects_wrong_plan(mutation):
    m = diamond()
    rows = solve_mrp(m)
    t, i, q = rows[0]
    if mutation == "quantity":
        rows[0] = (t, i, q + 6)
    elif mutation == "period":
        rows[0] = (t - 1, i, q)
    elif mutation == "missing":
        rows.pop(0)
    elif mutation == "extra":
        rows.insert(0, (1, "A", 4))
    elif mutation == "duplicate":
        rows.insert(0, rows[0])
    else:
        rows.reverse()
    with pytest.raises(AssertionError):
        verify_schedule(m, rows)


def test_scheduled_receipts_do_not_explode():
    m = diamond()
    m["demand"] = [[6, "A", 10]]
    m["receipts"] = [[6, "A", 10]]
    assert solve_mrp(m) == []
    verify_schedule(m, [])


def test_future_receipt_cannot_cover_earlier_requirement():
    m = {"item_names": ["A"], "horizon": 5, "bom": [], "onhand": {"A": 2},
         "lead": {"A": 1}, "lot": {"A": 4}, "demand": [[3, "A", 9], [5, "A", 4]],
         "receipts": [[4, "A", 3]]}
    assert solve_mrp(m) == [(2, "A", 8)]
    verify_schedule(m, [(2, "A", 8)])


def test_independent_and_dependent_demand_are_combined():
    m = {"item_names": ["A", "B"], "horizon": 5, "bom": [["A", "B", 2]],
         "onhand": {"A": 0, "B": 0}, "lead": {"A": 1, "B": 1},
         "lot": {"A": 1, "B": 5}, "demand": [[5, "A", 3], [4, "B", 3]], "receipts": []}
    assert solve_mrp(m) == [(3, "B", 10), (4, "A", 3)]
    verify_schedule(m, solve_mrp(m))


@pytest.mark.parametrize("answer", ["", "junk", "(0,A,1)", "(1,A,0)", "(1,A,-2)",
                                     "(1,A,nan)", "(1,A,2);(1,A,2)", "(2,A,1);(1,A,1)",
                                     "(1,B,2);(1,A,2)", "(1,A,1.0)", "(01,A,1)", None])
def test_parser_rejects_noncanonical_schedules(answer):
    with pytest.raises(ValueError):
        parse_schedule(answer)


def test_scoring_uses_no_self_and_enforces_order():
    class NoAttributes:
        def __getattribute__(self, name):
            raise AssertionError(name)

    entry = MrpGrossToNetExplosion().generate_entry()
    score = MrpGrossToNetExplosion.score_answer
    assert score(NoAttributes(), entry.answer, entry) == 1
    for wrong in ["", "junk", None, entry.answer + ";(1,Z,1)"]:
        assert score(NoAttributes(), wrong, entry) == 0
    rows = parse_schedule(entry.answer)
    if len(rows) > 1:
        assert score(NoAttributes(), format_schedule(list(reversed(rows))), entry) == 0


@pytest.mark.parametrize("level", range(7))
def test_generation_levels_and_json_roundtrip(level):
    task = MrpGrossToNetExplosion()
    task.config.set_level(level)
    answers = set()
    for _ in range(12):
        entry = task.generate_entry()
        m = json.loads(json.dumps(dict(entry.metadata)))
        rows = parse_schedule(entry.answer)
        verify_schedule(m, rows)
        assert format_schedule(solve_mrp(m)) == entry.answer
        assert task.render_prompt(m) == task.render_prompt(entry.metadata)
        assert len(task.tokenizer.encode(task.render_prompt(m))) < 2048
        assert task.score_answer(entry.answer, entry) == 1
        answers.add(entry.answer)
    assert len(answers) > 1


def test_input_order_does_not_change_plan():
    m = diamond()
    reversed_m = copy.deepcopy(m)
    for key in ["item_names", "bom", "receipts", "demand"]:
        reversed_m[key].reverse()
    assert solve_mrp(m) == solve_mrp(reversed_m)


def test_fixed_seed_reproduces_instance_without_generator_reseeding():
    state = random.getstate()
    try:
        task = MrpGrossToNetExplosion()
        first = task.generate_entry()
        after = random.getstate()
        random.setstate(state)
        second = task.generate_entry()
        assert dict(first.metadata) == dict(second.metadata)
        assert first.answer == second.answer
        assert after == random.getstate()
        assert state != after
    finally:
        random.setstate(state)


def test_difficulty_reset_is_not_incremental():
    config = MrpExplosionConfig()
    config.set_level(6)
    high = config.to_dict()
    config.set_level(0)
    assert config.layers == 3
    config.set_level(6)
    assert config.to_dict() == high

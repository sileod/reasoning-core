import importlib
import json
import random
from itertools import product

import pytest

_mod = importlib.import_module(
    "reasoning_core.tasks.generated.k3_cognitive_psychology_r1."
    "evidential_felicity_verdicts.evidential_felicity_verdicts"
)


@pytest.fixture()
def task():
    state = random.getstate()
    random.seed(11)
    yield _mod.EvidentialFelicityVerdicts()
    random.setstate(state)


def record(kind, person, fact, parents=(), time=1):
    return {"kind": kind, "person": person, "fact": fact,
            "parents": list(parents), "time": time, "sense": "heard"}


def query(time=20, person=0, fact=0, mode="set"):
    return {"time": time, "person": person, "fact": fact, "mode": mode,
            "priority": ["reportative", "inferential", "direct"]}


@pytest.mark.parametrize("level", range(7))
def test_levels_generate(task, level):
    task.config.set_level(level)
    answers = set()
    modes = set()
    multi = False
    for _ in range(30):
        entry = task.generate_entry()
        assert task.score_answer(entry.answer, entry) == 1.0
        answers.add(entry.answer)
        restored = json.loads(json.dumps(entry.metadata))
        assert task.render_prompt(restored) == task.render_prompt(entry.metadata)
        for q, gold in zip(entry.metadata["queries"], entry.answer.splitlines()):
            modes.add(q["mode"])
            multi |= "," in gold
            _mod.verify_gold(entry.metadata["records"], entry.metadata["withdrawals"], q, gold)
        for junk in ("", " ", "maybe", "direct,tactile", entry.answer + "\nreportative"):
            assert task.score_answer(junk, entry) == 0.0
    assert len(answers) >= 6
    assert modes == {"set", "clash"}
    assert multi


def test_transmission_does_not_copy_type():
    records = [record("direct", 0, 0), record("reportative", 1, 0, [0], 3),
               record("reportative", 2, 0, [1], 5)]
    assert _mod.verdict(records, [], query(person=2)) == "reportative"
    assert _mod.verdict(records, [], query(person=0)) == "direct"


def test_withdrawal_cascades_at_cutoff():
    records = [record("direct", 0, 0), record("inferential", 0, 1, [0], 3),
               record("reportative", 1, 1, [1], 5), record("direct", 1, 1, time=7)]
    withdrawals = [{"record": 0, "time": 8}]
    assert _mod.verdict(records, withdrawals, query(time=7, person=1, fact=1)) == "direct,reportative"
    assert _mod.verdict(records, withdrawals, query(time=8, person=1, fact=1)) == "direct"
    assert _mod.active_records(records, withdrawals, 8) == {3}


def test_all_premises_required_and_alternative_warrants():
    records = [record("direct", 0, 0), record("direct", 0, 1, time=3),
               record("inferential", 0, 2, [0, 1], 5),
               record("inferential", 0, 2, [1], 7)]
    withdrawals = [{"record": 0, "time": 6}]
    assert _mod.licensed_types(records, withdrawals, query(time=6, fact=2)) == []
    assert _mod.verdict(records, withdrawals, query(time=7, fact=2)) == "inferential"


def test_priority_ignores_unlicensed_and_is_not_always_direct():
    records = [record("direct", 0, 0), record("reportative", 0, 0, [0], 3)]
    assert _mod.verdict(records, [], query(mode="clash")) == "reportative"
    assert _mod.verdict(records, [], query(time=2, mode="clash")) == "direct"


def test_scorer_enforces_order_and_no_duplicates(task):
    entry = _mod.Entry(metadata={}, answer="direct,reportative\ninferential")
    assert task.score_answer(" direct, reportative\ninferential\n", entry) == 1.0
    for answer in ("reportative,direct\ninferential", "direct,reportative,\ninferential",
                   "direct,direct,reportative\ninferential", "Direct,reportative\ninferential",
                   "direct,reportative", None, 42):
        assert task.score_answer(answer, entry) == 0.0

    class NoAttributes:
        def __getattribute__(self, name):
            raise AssertionError(name)

    assert _mod.EvidentialFelicityVerdicts.score_answer(NoAttributes(), entry.answer, entry) == 1.0


def test_exhaustive_active_states():
    records = [record("direct", 0, 0), record("direct", 0, 1, time=3),
               record("inferential", 0, 2, [0, 1], 5),
               record("reportative", 1, 2, [2], 7)]
    for withdrawn in product((False, True), repeat=4):
        withdrawals = [{"record": i, "time": 8} for i, value in enumerate(withdrawn) if value]
        for time in range(1, 10):
            fixed_points = []
            for bits in product((False, True), repeat=4):
                if all(bits[i] == (r["time"] <= time and not (withdrawn[i] and time >= 8)
                                   and all(bits[p] for p in r["parents"]))
                       for i, r in enumerate(records)):
                    fixed_points.append({i for i, bit in enumerate(bits) if bit})
            assert fixed_points == [_mod.active_records(records, withdrawals, time)]


def test_verifier_rejects_wrong_gold():
    with pytest.raises(AssertionError):
        _mod.verify_gold([record("direct", 0, 0)], [], query(), "inferential")


def test_seed_replay(task):
    state = random.getstate()
    first = task.generate_entry()
    random.setstate(state)
    second = task.generate_entry()
    assert first.metadata == second.metadata
    assert first.answer == second.answer

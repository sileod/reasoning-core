import random

from reasoning_core.tasks.generated.k3_verification_repair_r1.misra_gries_counters.misra_gries_counters import (
    MisraGriesConfig,
    MisraGriesCounters,
)


def _sim(seq, k, alphabet):
    counter = {}
    for x in seq:
        if x in counter:
            counter[x] += 1
        elif len(counter) < k - 1:
            counter[x] = 1
        else:
            for key in list(counter):
                counter[key] -= 1
                if counter[key] == 0:
                    del counter[key]
    return counter


def test_gold_answer_matches_independent_simulation():
    for level in (0, 3, 6):
        task = MisraGriesCounters()
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_entry()
            gold = _sim(entry.metadata["seq"], entry.metadata["k"], entry.metadata["alphabet"])
            if not gold:
                expected = "none"
            else:
                expected = ",".join(f"{k}:{gold[k]}" for k in sorted(gold))
            assert entry.answer == expected


def test_score_answer_exact():
    task = MisraGriesCounters()
    task.config.set_level(1)
    entry = task.generate_entry()
    assert task.score_answer(entry.answer, entry) == 1.0
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("junk", entry) == 0.0


def test_score_answer_whitespace_tolerant():
    task = MisraGriesCounters()
    task.config.set_level(1)
    entry = task.generate_entry()
    spaced = ",".join(f"{p.strip()} " for p in entry.answer.split(",")).strip()
    assert task.score_answer(spaced, entry) == 1.0


def test_difficulty_changes_config():
    task = MisraGriesCounters()
    base = MisraGriesConfig()
    task.config.set_level(6)
    assert task.config.n > base.n
    assert task.config.alphabet >= base.alphabet


def test_empty_counter_reports_none():
    from reasoning_core.template import Entry

    task = MisraGriesCounters()
    entry = Entry(metadata={"seq": [], "k": 3}, answer="none")
    assert task.score_answer("none", entry) == 1.0
    assert task.score_answer("0:1", entry) == 0.0


def test_metadata_json_serializable():
    task = MisraGriesCounters()
    import json

    task.config.set_level(4)
    for _ in range(10):
        e = task.generate_entry()
        json.dumps(e.metadata)


def test_mixed_gold_answers_not_constant():
    random.seed(2267388306)
    answers = set()
    task = MisraGriesCounters()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(30):
            answers.add(task.generate_entry().answer)
    assert len(answers) > 2

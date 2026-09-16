import importlib.util
from pathlib import Path

_MOD_PATH = Path(__file__).with_name("case_government_assignment.py")
_spec = importlib.util.spec_from_file_location("case_government_assignment", _MOD_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CaseGovernmentAssignment = _mod.CaseGovernmentAssignment


def _task():
    return CaseGovernmentAssignment()


def test_gold_scores_one_and_distractors_differ_in_one_np():
    task = _task()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(40):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1
            expected = task.score_answer  # gold rescorable
            gold_cases = list(ex.metadata["cases"])
            candidates = ex.metadata["candidates"]
            assert candidates.count(gold_cases) == 1
            for c in candidates:
                diffs = sum(1 for a, b in zip(c, gold_cases) if a != b)
                assert diffs <= 1
            assert ex.answer in "ABCDEFGH"
            assert expected(ex.answer, ex) == 1.0


def test_junk_and_other_candidates_not_full_credit():
    task = _task()
    seen = 0
    for _ in range(300):
        ex = task.generate_example()
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("banana", ex) == 0.0
        assert task.score_answer("Z", ex) == 0.0
        for l, cand in zip("ABCDEFGH", ex.metadata["candidates"]):
            if l != ex.answer:
                assert task.score_answer(l, ex) == 0.0
                seen += 1
    assert seen > 0


def test_answers_balanced_per_level():
    task = _task()
    for level in (0, 3, 6):
        task.config.set_level(level)
        answers = [task.generate_example().answer for _ in range(120)]
        distinct = len(set(answers))
        assert distinct >= 2, f"level {level} produced only one answer: {set(answers)}"
        most = max(answers.count(a) for a in set(answers))
        assert most / len(answers) < 0.8, f"level {level} label prior too high"


def test_difficulty_changes_config():
    task = _task()
    base = task.config.np_count
    task.config.set_level(0)
    task.config.set_level(6)
    assert task.config.np_count >= base

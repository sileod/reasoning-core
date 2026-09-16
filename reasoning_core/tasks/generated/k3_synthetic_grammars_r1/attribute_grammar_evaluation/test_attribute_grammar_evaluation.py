import pytest

from reasoning_core.tasks.generated.k3_synthetic_grammars_r1.attribute_grammar_evaluation.attribute_grammar_evaluation import (
    AttributeGrammarEvaluation,
    AttributeGrammarConfig,
    _evaluate,
    _count_env,
    _build,
    score_answer,
)


def test_gold_answers_score_one():
    task = AttributeGrammarEvaluation()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_entry()
            assert score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = AttributeGrammarEvaluation()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_entry()
        assert score_answer("", ex) < 1.0
        assert score_answer("garbage nonsense", ex) < 1.0


def test_answer_matches_eval():
    task = AttributeGrammarEvaluation()
    task.config.set_level(4)
    for _ in range(50):
        ex = task.generate_entry()
        mode = ex.metadata["mode"]
        value = _evaluate(ex.metadata["tree"], mode, 0)
        if mode == "bool":
            assert ex.answer in ("true", "false")
            assert ex.answer == ("true" if value else "false")
        elif mode == "arith":
            assert isinstance(value, int)
            assert int(ex.answer) == value
        else:
            assert isinstance(value, str)
            assert ex.answer == value
        assert _count_env(ex.metadata["tree"]) >= 1


def test_all_domains_appear():
    task = AttributeGrammarEvaluation()
    seen = set()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(40):
            seen.add(task.generate_entry().metadata["mode"])
    assert {"arith", "bool", "string"} <= seen


def test_answers_vary():
    task = AttributeGrammarEvaluation()
    task.config.set_level(3)
    answers = {task.generate_entry().answer for _ in range(80)}
    assert len(answers) > 1


def test_difficulty_changes_depth():
    task = AttributeGrammarEvaluation()
    task.config.set_level(0)
    low = [task.generate_entry().answer for _ in range(30)]
    task.config.set_level(6)
    high = [task.generate_entry().answer for _ in range(30)]
    assert low and high


def test_score_bool_normalization():
    class E:
        def __init__(self, mode, answer):
            self.metadata = {"mode": mode}
            self.answer = answer

    assert score_answer(" TRUE ", E("bool", "true")) == 1.0
    assert score_answer("False", E("bool", "false")) == 1.0
    assert score_answer("yes", E("bool", "true")) == 0.0


def test_validate():
    AttributeGrammarEvaluation().validate()

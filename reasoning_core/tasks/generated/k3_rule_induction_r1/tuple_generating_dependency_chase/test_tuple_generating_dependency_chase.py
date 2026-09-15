import random

from reasoning_core.tasks.generated.k3_rule_induction_r1.tuple_generating_dependency_chase.tuple_generating_dependency_chase import (
    TupleGeneratingDependencyChase,
)


def _roundtrip(task, level):
    task.config.set_level(level)
    entry = task.generate_example()
    assert task.score_answer(entry.answer, entry) == 1.0


def test_levels_0_2_5():
    task = TupleGeneratingDependencyChase()
    for level in (0, 2, 5):
        _roundtrip(task, level)


def test_junk_scores_zero():
    task = TupleGeneratingDependencyChase()
    task.config.set_level(2)
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("garbage", entry) == 0.0


def test_wrong_answer_scores_zero():
    task = TupleGeneratingDependencyChase()
    task.config.set_level(2)
    entry = task.generate_example()
    derived = sorted(entry.metadata["derived"])
    import ast
    wrong = ast.literal_eval(entry.answer)
    if wrong:
        mutated = list(wrong)
        mutated[0] = tuple([v + 1 if i == 0 else v for i, v in enumerate(mutated[0])]) if mutated[0] else ()
        assert task.score_answer(repr(mutated), entry) == 0.0


def test_gold_is_derived_superset_of_facts():
    task = TupleGeneratingDependencyChase()
    task.config.set_level(5)
    entry = task.generate_example()
    facts = set(entry.metadata["facts"])
    derived = set(entry.metadata["derived"])
    assert facts.issubset(derived)


def test_deterministic_under_seed():
    import random
    random.seed(123)
    a = TupleGeneratingDependencyChase()
    a.config.set_level(3)
    e1 = a.generate_example()
    random.seed(123)
    b = TupleGeneratingDependencyChase()
    b.config.set_level(3)
    e2 = b.generate_example()
    assert e1.answer == e2.answer


def test_no_constant_answer_across_levels():
    task = TupleGeneratingDependencyChase()
    answers = set()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(20):
            answers.add(task.generate_example().answer)
    assert len(answers) > 5

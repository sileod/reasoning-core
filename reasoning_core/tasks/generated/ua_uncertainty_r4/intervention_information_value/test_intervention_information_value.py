from reasoning_core.tasks.generated.ua_uncertainty_r4.intervention_information_value.intervention_information_value import (
    InterventionInformationValue,
    _scaled_prior_value,
    _scaled_info_value,
)


def test_generate_and_score():
    task = InterventionInformationValue()
    for _ in range(40):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_difficulty_changes():
    task = InterventionInformationValue()
    c0 = task.config
    task.config.set_level(6)
    assert task.config.num_states >= c0.num_states
    assert task.config.num_actions >= c0.num_actions
    assert task.config.outcomes_per_experiment >= c0.outcomes_per_experiment


def test_answers_vary():
    task = InterventionInformationValue()
    seen = {task.generate_example().answer for _ in range(60)}
    assert len(seen) >= 2


def test_winner_is_argmax():
    task = InterventionInformationValue()
    for _ in range(30):
        x = task.generate_example()
        m = x.metadata
        net_by_name = {e["name"]: e["net_value"] for e in m["experiments"]}
        best = max(net_by_name.values())
        winners = [n for n, v in net_by_name.items() if v == best]
        winners = sorted(winners)
        assert m["answer_name"] == winners[0]
        assert m["answer_net"] == best


def test_value_formula_reproduces_metadata():
    task = InterventionInformationValue()
    x = task.generate_example()
    m = x.metadata
    prior_val = _scaled_prior_value(m["counts"], m["payoffs"])
    assert prior_val == m["prior_value"]
    total = sum(m["counts"])
    for e in m["experiments"]:
        info = _scaled_info_value(m["counts"], m["payoffs"], e["outcomes"])
        assert info - prior_val - e["cost"] * total == e["net_value"]


def test_junk_answers_fail():
    task = InterventionInformationValue()
    x = task.generate_example()
    assert task.score_answer("junk", x) == 0.0
    assert task.score_answer("", x) == 0.0
    assert task.score_answer(None, x) == 0.0


def test_all_levels_generate():
    task = InterventionInformationValue()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0

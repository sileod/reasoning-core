import random

import pytest

from reasoning_core.template import Task

from reasoning_core.tasks.generated.k3_relational_structures_r1.mealy_moore_machine_conversion.mealy_moore_machine_conversion import (
    MealyMooreMachineConversion,
    mealy_to_moore,
    moore_to_mealy,
    render_mealy,
    render_moore,
    _verify_m2m,
    _verify_m2o,
)


@pytest.mark.parametrize("level", [0, 1, 2, 3, 4, 5, 6])
def test_generate_and_score(level):
    task = MealyMooreMachineConversion()
    task.config.set_level(level)
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_wrong_answers_fail():
    task = MealyMooreMachineConversion()
    task.config.set_level(0)
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("junk", x) < 1.0
    assert task.score_answer(f"S9:S0", x) < 1.0


def test_roundtrip_verifiers():
    n, m = 3, 2
    for _ in range(50):
        transitions = [[(random.randrange(n), random.choice(['0', '1'])) for _ in range(m)]
                       for _ in range(n)]
        mt, mo = mealy_to_moore(n, m, transitions)
        assert _verify_m2m(n, m, transitions, mt, mo)


def test_both_directions_occur():
    task = MealyMooreMachineConversion()
    seen = set()
    for _ in range(60):
        x = task.generate_example()
        seen.add(x.metadata["direction"])
    assert seen == {"mealy_to_moore", "moore_to_mealy"}


def test_validate():
    MealyMooreMachineConversion().validate()

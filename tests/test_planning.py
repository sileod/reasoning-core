from unified_planning.shortcuts import BoolType, Object, Problem, UserType

from reasoning_core.tasks.planning import translate


def test_translate_uses_closed_world_initial_state():
    item = UserType("item")
    problem = Problem("closed-world-state")
    active = problem.add_fluent(
        "active",
        BoolType(),
        item=item,
        default_initial_value=True,
    )
    first = Object("first", item)
    second = Object("second", item)
    problem.add_objects([first, second])
    problem.set_initial_value(active(first), True)
    problem.set_initial_value(active(second), False)

    prompt = translate(problem)

    assert "Default value:" not in prompt
    assert "True values: active(first)" in prompt
    assert "active(second)" not in prompt
    assert "All facts not listed under True values are false." in prompt

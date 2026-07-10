from greenery import parse as gparse

from reasoning_core.tasks.regex import _distinct_equivalent_rendering, _reduced_union_superset


def test_equivalent_rendering_is_distinct_and_semantically_equal():
    regex = "(a|b)c"
    fsm = gparse(regex).to_fsm()
    equivalent = _distinct_equivalent_rendering(regex, fsm)

    assert equivalent != regex
    assert fsm.equivalent(gparse(equivalent).to_fsm())


def test_reduced_superset_does_not_embed_source_union_arm():
    regex = "a|b"
    fsm = gparse(regex).to_fsm()
    superset = _reduced_union_superset(regex, fsm, "c")

    assert regex not in superset
    assert fsm.issubset(gparse(superset).to_fsm())
    assert not fsm.equivalent(gparse(superset).to_fsm())

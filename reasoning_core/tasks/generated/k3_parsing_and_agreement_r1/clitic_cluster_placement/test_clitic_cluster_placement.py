import random

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.clitic_cluster_placement.clitic_cluster_placement import (
    CliticClusterPlacement,
    order_cluster,
)


def test_ordering_hierarchy_matches_statement():
    assert order_cluster(["lo", "me", "le"]) == "me-le-lo"
    assert order_cluster(["la", "lo"]) == "la-lo"
    assert order_cluster(["me", "nos"]) == "me-nos"
    assert order_cluster(["lo", "le", "te", "me"]) == "me-te-le-lo"
    assert order_cluster(["les", "la"]) == "les-la"


def test_generate_and_score_roundtrip():
    task = CliticClusterPlacement()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_self_consistent():
    task = CliticClusterPlacement()
    for _ in range(20):
        ex = task.generate_example()
        cluster, host = ex.answer.split("|")
        assert order_cluster(cluster.split("-")) == cluster
        md = ex.metadata
        if md["mode"] == "second":
            assert host == md["verb"]
        elif md["mode"] == "finite":
            assert host == md["verb"]
        else:
            assert host == md["matrix"]
            assert host != md["inf"]


def test_all_modes_reachable():
    task = CliticClusterPlacement()
    modes = set()
    for _ in range(200):
        ex = task.generate_example()
        modes.add(ex.metadata["mode"])
    assert modes == {"second", "finite", "raised"}


def test_difficulty_changes_config():
    task = CliticClusterPlacement()
    task.config.set_level(0)
    c0 = task.config.clitic_max
    task.config.set_level(6)
    assert task.config.clitic_max == 4
    assert task.config.clitic_min == 4
    assert task.config.clitic_max >= c0


def test_wrong_answers_do_not_score():
    task = CliticClusterPlacement()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("junk", ex) == 0.0
    assert task.score_answer("999x|$#", ex) == 0.0


def test_all_levels_generate():
    task = CliticClusterPlacement()
    for level in range(7):
        for _ in range(10):
            ex = task.generate_example(level=level)
            assert task.score_answer(ex.answer, ex) == 1.0
            assert 2 <= len(ex.metadata["clitics"]) <= 4


def test_host_never_the_infinitive_in_raised_mode():
    task = CliticClusterPlacement()
    for _ in range(100):
        ex = task.generate_example(level=6)
        md = ex.metadata
        if md["mode"] == "raised":
            cluster, host = ex.answer.split("|")
            assert host == md["matrix"]
            assert host != md["inf"]
            assert cluster == md["cluster"]


def test_cluster_size_respects_level_bounds():
    task = CliticClusterPlacement()
    for _ in range(50):
        assert len(task.generate_example(level=0).metadata["clitics"]) == 2
    for _ in range(50):
        sizes = {len(task.generate_example(level=6).metadata["clitics"]) for _ in range(5)}
        assert sizes == {4}


def test_prompt_states_rule_and_format():
    task = CliticClusterPlacement()
    ex = task.generate_example()
    assert "me < nos < te < vos < le < les < la < lo" in ex.prompt
    assert "cluster|host" in ex.prompt
    assert "me-le|compro" in ex.prompt

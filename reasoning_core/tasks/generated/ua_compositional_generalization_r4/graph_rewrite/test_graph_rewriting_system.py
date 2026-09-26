import random

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.graph_rewrite.graph_rewriting_system import (
    GraphRewriteV2,
    _apply,
    _contains,
    _exhaust,
    _fmt_graph,
    _smallest_match,
)


def _matches_expectation(ex):
    meta = ex.metadata
    mode = meta["mode"]
    if mode == "derive":
        assert ex.answer == meta["answer_sequence"]
        for g in ex.answer.split("->"):
            nodes = g.split("|")[0]
            assert nodes, "empty node list in sequence"
    elif mode == "count":
        assert ex.answer == str(meta["applications"])
        assert int(ex.answer) >= 0
    else:
        assert ex.answer in ("Yes", "No")


def test_gold_scores_one():
    t = GraphRewriteV2()
    for _ in range(30):
        ex = t.generate_example()
        assert t.score_answer(ex.answer, ex) == 1.0
        _matches_expectation(ex)


def test_wrong_answers_fail():
    t = GraphRewriteV2()
    for _ in range(20):
        ex = t.generate_example()
        assert t.score_answer("NotAnAnswer!", ex) < 1.0
        assert t.score_answer("", ex) < 1.0


def test_difficulty_changes_config():
    t = GraphRewriteV2()
    c0 = t.config.max_nodes
    t.config.set_level(6)
    assert t.config.max_nodes >= c0


def test_all_levels_generate():
    for level in range(7):
        t = GraphRewriteV2()
        t.config.set_level(level)
        for _ in range(5):
            ex = t.generate_example()
            assert t.score_answer(ex.answer, ex) == 1.0


def test_helpers_correct():
    G = ({0, 1, 2}, {(0, 1), (1, 2)})
    rule = {"lv": frozenset({0, 1}), "le": frozenset({(0, 1)}),
            "rv": frozenset({0}), "re": frozenset(), "nacs": []}
    m = _smallest_match(G, rule)
    assert m is not None
    G2 = _apply(G, rule, m)
    seq, napp = _exhaust(G, rule)
    assert seq[0] == G
    assert napp >= 1
    assert _contains({0, 1}, {(0, 1)}, G[0], G[1]) is True
    assert _fmt_graph({0, 1}, set()) == "0,1|"


def test_reproducible_seeded():
    random.seed(3020341981)
    a = GraphRewriteV2().generate_example().__dict__["metadata"]["_deduplication_key"]
    random.seed(3020341981)
    b = GraphRewriteV2().generate_example().__dict__["metadata"]["_deduplication_key"]
    assert a == b

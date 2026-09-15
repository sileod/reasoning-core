import random

from reasoning_core.tasks.generated.wave12.dominator_analysis.dominator_analysis import (
    DominatorAnalysis,
    DominatorConfig,
)


def _dominators(graph, entry, n):
    dom = {v: set(range(n)) for v in range(n)}
    dom[entry] = {entry}
    changed = True
    while changed:
        changed = False
        for v in range(n):
            if v == entry:
                continue
            preds = [p for p in range(n) if v in graph[p]]
            if not preds:
                if dom[v] != {v}:
                    dom[v] = {v}
                    changed = True
                continue
            newd = set(range(n))
            for p in preds:
                newd &= dom[p]
            newd.add(v)
            if newd != dom[v]:
                dom[v] = newd
                changed = True
    return dom


def test_gold_scores_one():
    t = DominatorAnalysis()
    for _ in range(20):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_dominator_correct():
    t = DominatorAnalysis()
    for _ in range(50):
        e = t.generate_example()
        m = e.metadata
        graph = {u: m["graph_list"][u] for u in range(m["node_count"])}
        dom = _dominators(graph, m["entry"], m["node_count"])
        true_dom = m["candidate"] in dom[m["query_node"]]
        assert true_dom == m["true_domination"]
        gold = "yes" if true_dom else "no"
        assert e.answer == gold


def test_junk_scores_zero():
    t = DominatorAnalysis()
    for _ in range(20):
        e = t.generate_example()
        assert t.score_answer("", e) == 0.0
        assert t.score_answer("maybe", e) == 0.0
        assert t.score_answer(3, e) == 0.0


def test_balanced_labels():
    t = DominatorAnalysis()
    counts = {"yes": 0, "no": 0}
    for _ in range(200):
        e = t.generate_example()
        counts[e.answer] += 1
    assert counts["yes"] > 40
    assert counts["no"] > 40


def test_difficulty_changes():
    c = DominatorConfig()
    l0 = c.node_count
    c.apply_difficulty(3)
    assert c.node_count > l0


def test_no_surface_leak():
    t = DominatorAnalysis()
    e = t.generate_example()
    prompt = t.render_prompt(e.metadata)
    ans = "yes" if e.metadata["true_domination"] else "no"
    assert ans not in prompt.split()

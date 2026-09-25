import random

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_scope_and_binding_r4.quotation_reference_composition.quotation_reference_composition import (
    QuotationReferenceComposition,
    QuotationConfig,
    denote_form,
    render_form,
)


def make_task(level=0):
    task = QuotationReferenceComposition()
    task.config.set_level(level)
    return task


def test_generate_and_score():
    for level in range(0, 7):
        task = make_task(level)
        for _ in range(30):
            x = task.generate_example()
            assert isinstance(x, Entry)
            assert x.answer in ("yes", "no")
            assert task.score_answer(x.answer, x) == 1.0


def test_junk_scores_zero():
    task = make_task()
    x = task.generate_example()
    for junk in ("", "maybe", "42", "yes please", "No!"):
        assert task.score_answer(junk, x) < 1.0


def test_denotation_equality_consistent():
    task = make_task(3)
    for _ in range(40):
        x = task.generate_example()
        env = {}
        for name, (kind, data) in x.metadata["bindings"].items():
            env[name] = (kind, data)
        f1 = parse_rendered(x.metadata["expr1"])
        f2 = parse_rendered(x.metadata["expr2"])
        same = denote_form(f1, env) == denote_form(f2, env)
        got = "yes" if same else "no"
        assert got == x.answer


def parse_rendered(text):
    toks = text.split()
    if toks[0] == "'":
        return ("quote", [(_p(k)) for k in toks[1:]])
    return ("bare", toks[0])


def _p(tok):
    if tok.startswith(","):
        return ("s", tok[1:])
    return ("a", tok)


def test_both_labels_present():
    counts = {"yes": 0, "no": 0}
    random.seed(1)
    task = make_task(4)
    for _ in range(200):
        x = task.generate_example()
        counts[x.answer] += 1
    assert counts["yes"] > 0 and counts["no"] > 0


def test_yes_pair_wordings_differ():
    random.seed(7)
    task = make_task(3)
    for _ in range(60):
        x = task.generate_example()
        if x.answer == "yes":
            assert x.metadata["expr1"] != x.metadata["expr2"]


def test_difficulty_changes():
    c0 = QuotationConfig()
    c6 = QuotationConfig()
    c0.apply_difficulty(0)
    c6.apply_difficulty(6)
    assert c6.n_vars > c0.n_vars
    assert c6.max_units > c0.max_units

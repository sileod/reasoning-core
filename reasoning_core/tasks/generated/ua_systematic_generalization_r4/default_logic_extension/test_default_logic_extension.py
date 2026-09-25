import random

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.default_logic_extension.default_logic_extension import (
    DefaultLogicExtension,
    all_extensions, gamma_closure, applicable_default, neg,
    MODE_ALL, MODE_SOME, MODE_APPLICABLE,
)


def _make():
    return DefaultLogicExtension(config=DefaultLogicExtension.config_cls())


def test_neg():
    assert neg('a') == 'not a'
    assert neg('not a') == 'a'


def test_extension_invariants():
    task = _make()
    seen_nonempty = False
    for _ in range(40):
        a, f, d = task.build_instance()
        exts = all_extensions(f, d, a)
        if not exts:
            continue
        seen_nonempty = True
        for e in exts:
            assert set(f).issubset(e)
            assert gamma_closure(f, d, e) == e
    assert seen_nonempty


def test_gold_answer_scores_one_all():
    task = _make()
    for _ in range(40):
        e = task.generate_entry()
        assert task.score_answer(e.answer, e) == 1.0
        if e.metadata['mode'] == MODE_ALL:
            # the listed extensions must be exactly the fixed points
            a = e.metadata['atoms']
            f = list(e.metadata['facts'])
            d = e.metadata['defaults']
            d = [tuple(tuple(x) for x in dd) for dd in d]
            gold = set(frozenset(x) for x in e.metadata['extensions'])
            assert gold == all_extensions(f, d, a)


def test_some_mode_correctness():
    task = _make()
    somes = 0
    for _ in range(200):
        e = task.generate_entry()
        if e.metadata['mode'] != MODE_SOME:
            continue
        somes += 1
        assert e.answer in ('Yes', 'No')
        assert task.score_answer(e.answer, e) == 1.0
        ext = e.metadata['extensions']
        formula = set(e.metadata['formula'])
        present = any(set(x).issuperset(formula) for x in ext)
        assert (e.answer == 'Yes') == present
    assert somes >= 10


def test_applicable_mode_correctness():
    task = _make()
    apps = 0
    for _ in range(200):
        e = task.generate_entry()
        if e.metadata['mode'] != MODE_APPLICABLE:
            continue
        apps += 1
        assert e.answer in ('Yes', 'No')
        assert task.score_answer(e.answer, e) == 1.0
        gi = set(e.metadata['given_extension'])
        d = tuple(tuple(x) for x in e.metadata['defaults'][e.metadata['checked_default']])
        assert (e.answer == 'Yes') == applicable_default(gi, d)
    assert apps >= 10


def test_gold_answer_scores_one():
    task = _make()
    for _ in range(60):
        e = task.generate_entry()
        assert task.score_answer(e.answer, e) == 1.0


def test_balance_yes_no():
    task = _make()
    yes = no = 0
    for _ in range(200):
        e = task.generate_entry()
        if e.metadata['mode'] in (MODE_SOME, MODE_APPLICABLE):
            if e.answer == 'Yes':
                yes += 1
            else:
                no += 1
    assert yes > 0 and no > 0


def test_validate_module():
    task = _make()
    task.validate(n_samples=5)


def test_junk_does_not_score():
    task = _make()
    for _ in range(10):
        e = task.generate_entry()
        assert task.score_answer('', e) < 1.0
        assert task.score_answer('xyzzy', e) < 1.0


def test_all_three_modes_occur():
    task = _make()
    seen = set()
    for _ in range(200):
        seen.add(task.generate_entry().metadata['mode'])
    assert seen == {MODE_ALL, MODE_SOME, MODE_APPLICABLE}

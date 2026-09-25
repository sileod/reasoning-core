import random

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.evidence_reuse_equivalence.evidence_reuse_equivalence import (
    EvidenceReuseEquivalence,
    _expand,
)


def test_generate_and_score_all_levels():
    task = EvidenceReuseEquivalence()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            f1 = set(ex.metadata['frag1'])
            f2 = set(ex.metadata['frag2'])
            expect = 'yes' if f1 == f2 else 'no'
            assert ex.answer == expect
            assert task.score_answer(ex.answer, ex) == 1.0
            assert task.score_answer('junk', ex) < 1.0
            assert task.score_answer('', ex) < 1.0
            assert task.score_answer('maybe', ex) < 1.0


def test_label_balance_across_levels():
    random.seed(1277236794)
    task = EvidenceReuseEquivalence()
    for level in range(7):
        task.config.set_level(level)
        counts = {'yes': 0, 'no': 0}
        for _ in range(200):
            ex = task.generate_example()
            counts[ex.answer] += 1
        total = counts['yes'] + counts['no']
        assert total > 0
        assert 0.35 <= counts['yes'] / total <= 0.65, (level, counts)


def test_support_set_consistency():
    task = EvidenceReuseEquivalence()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            assert set(ex.metadata['frag1']) <= set(ex.metadata['ids'])
            assert set(ex.metadata['frag2']) <= set(ex.metadata['ids'])


def test_expand_preserves_set():
    random.seed(1)
    for _ in range(50):
        support = ['A', 'B', 'C']
        out = _expand(support, 3)
        assert set(out) == set(support)
        assert len(out) >= len(support)


def test_prompt_mentions_both_fragments():
    task = EvidenceReuseEquivalence()
    task.config.set_level(2)
    ex = task.generate_example()
    prompt = task.render_prompt(ex.metadata)
    assert 'Derivation 1 cites' in prompt
    assert 'Derivation 2 cites' in prompt


def test_difficulty_changes_config():
    task = EvidenceReuseEquivalence()
    base = task.config.to_dict()
    task.config.set_level(5)
    high = task.config.to_dict()
    assert base != high

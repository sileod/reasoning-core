import json

from reasoning_core.tasks.generated.ua_relational_structures_r4.branch_sensitive_resource_audit.branch_sensitive_resource_audit import (
    BranchSensitiveResourceAudit,
    _eval_node,
)


def test_roundtrip():
    task = BranchSensitiveResourceAudit()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        json.dumps(dict(ex.metadata))


def test_junk_scores_zero():
    task = BranchSensitiveResourceAudit()
    ex = task.generate_example()
    assert task.score_answer('', ex) == 0.0
    assert task.score_answer('import fakemodule', ex) == 0.0


def test_usage_recompute():
    task = BranchSensitiveResourceAudit()
    for _ in range(20):
        ex = task.generate_example()
        md = ex.metadata
        recomputed = _eval_node(md['tree'], md['n'], md['resources'])
        assert all(recomputed[r] == md['usage'][r] for r in md['resources'])


def test_violators_match_usage():
    task = BranchSensitiveResourceAudit()
    for _ in range(20):
        ex = task.generate_example()
        md = ex.metadata
        expected = sorted(r for r in md['resources'] if md['usage'][r] > md['capacities'][r])
        assert md['violators'] == expected


def test_answer_format_none():
    task = BranchSensitiveResourceAudit()
    ex = task.generate_example()
    an = ex.answer
    if an == 'none':
        assert ex.metadata['violators'] == []


def test_answer_order():
    task = BranchSensitiveResourceAudit()
    seen = set()
    for _ in range(300):
        ex = task.generate_example()
        seen.add(ex.answer)
    assert len(seen) > 5

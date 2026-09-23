from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.design_column_alias_audit.design_column_alias_audit import (
    DesignColumnAliasAudit,
    TASK_META,
    design_choice,
)

TASK_NAME = 'design_column_alias_audit'


def test_meta_present():
    assert TASK_META['hypothesis'] == 'P004'
    assert TASK_META['parent_source_id'] is None
    assert design_choice.startswith('Generate run sheets')


def test_generate_and_score():
    task = DesignColumnAliasAudit()
    for level in range(0, 7):
        task.config.set_level(level)
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_answer_valid_domain():
    task = DesignColumnAliasAudit()
    for level in range(0, 7):
        task.config.set_level(level)
        x = task.generate_example()
        a = x.answer
        assert isinstance(a, str)
        cols = x.metadata['columns']
        if a != 'none':
            for pair in a.split(','):
                n1, n2 = pair.split('-')
                assert n1 in cols and n2 in cols
                assert n1 != n2
                assert n1 == sorted((n1, n2))[0]
        else:
            # verify no pair aliased: re-derive from design
            factors = x.metadata['factors']
            design = x.metadata['design']
            n_rows = x.metadata['n_rows']
            signs = {}
            for col in cols:
                if len(col) == 1:
                    i = factors.index(col)
                    signs[col] = [row[i] for row in design]
                else:
                    idxs = [factors.index(p) for p in col]
                    signs[col] = [int(_prod(row[i] for i in idxs)) for row in design]
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    ip = sum(a * b for a, b in zip(signs[cols[i]], signs[cols[j]]))
                    assert abs(ip) != n_rows


def _prod(it):
    p = 1
    for x in it:
        p *= x
    return p


def test_wrong_answers():
    task = DesignColumnAliasAudit()
    for level in (0, 3, 6):
        task.config.set_level(level)
        x = task.generate_example()
        assert task.score_answer('', x) < 1.0
        assert task.score_answer('garbage!!', x) < 1.0
        assert task.score_answer('none', x) < 1.0 or x.answer == 'none'
        if x.answer != 'none':
            assert task.score_answer('none', x) == 0.0


def test_difficulty_changes_config():
    task = DesignColumnAliasAudit()
    base = task.config.to_dict()
    task.config.set_level(5)
    high = task.config.to_dict()
    assert base != high

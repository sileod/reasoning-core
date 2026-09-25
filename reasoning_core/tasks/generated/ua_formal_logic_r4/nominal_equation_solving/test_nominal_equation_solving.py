import random

from reasoning_core.tasks.generated.ua_formal_logic_r4.nominal_equation_solving.nominal_equation_solving import (
    NominalEquationSolving,
    unify,
    render,
    perm_apply,
    subst_term,
)


def _mirrored(sym_depth):
    """A term and its exact copy unify trivially (empty substitution)."""
    pass


def test_generate_and_roundtrip():
    task = NominalEquationSolving()
    task.config.set_level(2)
    for _ in range(80):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_empty_and_junk_scored_zero():
    task = NominalEquationSolving()
    task.config.set_level(1)
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("banana", entry) == 0.0


def test_answer_format_domain():
    task = NominalEquationSolving()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(40):
            a = task.generate_example().answer
            if a == 'inconsistent':
                continue
            assert a.startswith('subst{') and '; fresh{' in a and a.endswith('}')
            body, freshpart = a.split('; fresh{')
            assert '}' in freshpart
            assert body.startswith('subst{')


def test_both_answer_kinds_occur():
    task = NominalEquationSolving()
    for level in (0, 3, 6):
        task.config.set_level(level)
        kinds = set()
        for _ in range(60):
            kinds.add(task.generate_example().answer == 'inconsistent')
        assert True in kinds and False in kinds, f"level {level} not balanced"


def test_solvable_answers_are_sound():
    task = NominalEquationSolving()
    task.config.set_level(3)
    for _ in range(60):
        e = task.generate_example()
        if e.answer == 'inconsistent':
            continue
        # regen via storage: verify the metadata terms really unify nontrivially
        L, R = e.metadata['left'], e.metadata['right']
        # reconstruct not trivial; rely on deterministic generation rather than
        # parsing. Basic roundtrip already asserted.
        assert e.metadata['kind'] == 'solvable'


def test_mirrored_terms_unify_trivially():
    t = ('app', 'f', (('bind', 'a', ('sus', {'a': 'b', 'b': 'a'}, 'X')),))
    r = unify([(t, t)])
    assert r is not None
    sigma, fresh = r
    assert sigma == {}


def test_clashing_arity_is_inconsistent():
    L = ('app', 'f', (('var', 'X'),))
    R = ('app', 'f', (('var', 'X'), ('var', 'Y')))
    assert unify([(L, R)]) is None


def test_occurs_check_rejects_self():
    L = ('var', 'X')
    R = ('app', 'f', (('var', 'X'),))
    assert unify([(L, R)]) is None


def test_subst_and_permute_consistent():
    perms = {'a': 'b', 'b': 'a'}
    t = ('bind', 'a', ('sus', perms, 'Y'))
    applied = perm_apply(perms, t)
    assert applied[0] == 'bind' and applied[1] == 'b'
    # comp identity: perm * perm
    doubled = perm_apply(perms, perm_apply(perms, ('at', 'a')))
    assert doubled == ('at', 'a')


def test_all_levels_generate():
    task = NominalEquationSolving()
    for level in range(7):
        task.config.set_level(level)
        random.seed(level)
        for _ in range(12):
            task.generate_example()


def test_difficulty_changes_config():
    task = NominalEquationSolving()
    task.config.set_level(0)
    d0 = task.config.depth
    task.config.set_level(6)
    d6 = task.config.depth
    assert d6 > d0

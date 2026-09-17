import itertools
import json
import random

import numpy as np
import pytest

from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.degree_construction_equivalence.degree_construction_equivalence import (
    DegreeConstructionEquivalence,
    check_constraints,
    domain,
    meaning,
    strict_constraints,
    wording,
)


@pytest.fixture(autouse=True)
def fixed_randomness():
    state = random.getstate()
    random.seed(3536382515)
    yield
    random.setstate(state)


@pytest.mark.parametrize('level', [0, 1, 2, 3, 4, 5, 6])
def test_generation_and_balance(level):
    task = DegreeConstructionEquivalence()
    task.config.set_level(level)
    answers = []
    for _ in range(32):
        entry = task.generate_entry()
        answers.append(entry.answer)
        assert task.score_answer(entry.answer, entry) == 1
        restored = json.loads(json.dumps(dict(entry.metadata)))
        assert task.render_prompt(restored) == task.render_prompt(entry.metadata)
        n = len(restored['labels'])
        points, _, _, _ = domain(n, restored['maximum'])
        left, right = [check_constraints(side, points) for side in restored['constructions']]
        assert (entry.answer == 'yes') == np.array_equal(left, right)
        assert left.any() and right.any()
        if entry.answer == 'no':
            assert (left != right).any()
    assert 8 <= answers.count('yes') <= 24
    assert set(answers) == {'yes', 'no'}


def test_all_encodings_against_direct_meaning():
    points, atoms, masks, _ = domain(4, 3)
    for atom, mask in zip(atoms, masks):
        assert np.array_equal(check_constraints([atom], points), mask)
        for coefficients, bound in strict_constraints(atom, 4):
            assert len(coefficients) == 4
            assert isinstance(bound, int)


@pytest.mark.parametrize('atom, values, expected', [
    (('more', 0, 1, 0), [2, 2, 0, 0], False),
    (('enough', 0, 1, 0), [2, 2, 0, 0], True),
    (('equal', 0, 1, 0), [2, 3, 0, 0], False),
    (('equal', 0, 1, 0), [0, 0, 3, 3], True),
    (('gap', 0, 1, 2), [3, 1, 0, 0], True),
    (('gap', 0, 1, 2), [2, 1, 0, 0], False),
    (('too', 0, 0, 2), [2, 0, 0, 0], False),
    (('too', 0, 0, 2), [3, 0, 0, 0], True),
    (('threshold', 0, 0, 2), [2, 0, 0, 0], True),
    (('most', 0, 0, 0), [3, 1, 3, 0], False),
    (('most', 0, 0, 0), [3, 1, 2, 0], True),
    (('correlative', 0, 2, 0), [3, 3, 1, 2], True),
    (('correlative', 0, 2, 0), [3, 2, 1, 2], False),
    (('correlative', 0, 2, 0), [1, 1, 3, 3], False),
])
def test_boundary_semantics(atom, values, expected):
    points = np.array([values])
    assert bool(meaning(atom, points)[0]) == expected
    assert bool(check_constraints([atom], points)[0]) == expected


def test_transitive_equivalence_and_off_by_one():
    points = np.array(list(itertools.product(range(4), repeat=4)))
    common = [('more', 0, 1, 0), ('more', 1, 2, 0)]
    base = check_constraints(common, points)
    assert np.array_equal(base, check_constraints(common + [('gap', 0, 2, 2)], points))
    assert not np.array_equal(base, check_constraints(common + [('gap', 0, 2, 3)], points))
    assert np.array_equal(check_constraints([('too', 0, 0, 1)], points),
                          check_constraints([('threshold', 0, 0, 2)], points))


def test_scorer_without_self_and_invalid_answers():
    class NoAttributes:
        def __getattribute__(self, name):
            raise AssertionError(name)

    entry = DegreeConstructionEquivalence().generate_entry()
    for answer in ('', 'yes no', 'yes.', 'no.', 'garbage', None, [], 1):
        assert DegreeConstructionEquivalence.score_answer(NoAttributes(), answer, entry) == 0
    assert DegreeConstructionEquivalence.score_answer(NoAttributes(), entry.answer.upper(), entry) == 1
    assert DegreeConstructionEquivalence.score_answer(NoAttributes(), 'no' if entry.answer == 'yes' else 'yes', entry) == 0


def test_fixed_seed_and_difficulty():
    task = DegreeConstructionEquivalence()
    first = task.generate_entry()
    random.seed(3536382515)
    second = task.generate_entry()
    assert first.answer == second.answer
    assert task.render_prompt(first.metadata) == task.render_prompt(second.metadata)
    base = dict(vars(task.config))
    task.config.set_level(1)
    assert vars(task.config) != base
    task.config.set_level(0)
    assert task.config.n_context == 1


def test_surface_collision_and_family_coverage():
    task = DegreeConstructionEquivalence()
    seen = {}
    families = set()
    for _ in range(100):
        entry = task.generate_entry()
        prompt = task.render_prompt(entry.metadata)
        assert seen.setdefault(prompt, entry.answer) == entry.answer
        families.update(atom[0] for side in entry.metadata['constructions'] for atom in side)
    assert families == {'more', 'enough', 'equal', 'gap', 'too', 'threshold', 'most', 'correlative'}
    points, atoms, _, _ = domain(4, 3)
    labels = ['A beads', 'A buttons', 'B beads', 'B buttons']
    rendered = {}
    for atom in atoms:
        for alternate in (False, True):
            text = wording(atom, labels, alternate)
            signature = meaning(atom, points).tobytes()
            assert rendered.setdefault(text, signature) == signature

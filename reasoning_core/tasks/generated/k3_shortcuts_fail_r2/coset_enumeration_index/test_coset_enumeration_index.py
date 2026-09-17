import json
import random
import re

import pytest

from reasoning_core.tasks.generated.k3_shortcuts_fail_r2.coset_enumeration_index import coset_enumeration_index as module


SEED = 2639544549
FAMILIES = ('dihedral', 'abelian', 'tetrahedral', 'octahedral', 'icosahedral')


@pytest.fixture(autouse=True)
def preserve_rng():
    state = random.getstate()
    random.seed(SEED)
    yield
    random.setstate(state)


@pytest.mark.parametrize('level', range(7))
def test_generated_cosets_match_explicit_partition(level):
    task = module.CosetEnumerationIndex()
    task.config.set_level(level)
    for _ in range(4):
        entry = task.generate_entry()
        metadata = json.loads(json.dumps(entry.metadata))
        images = [tuple(p) for p in metadata['images']]
        group = module.closure(images)
        subgroup = module.closure([module.evaluate(w, images) for w in metadata['subgroup']])
        cosets = {frozenset(module.multiply(h, g) for h in subgroup) for g in group}
        assert len(cosets) == int(entry.answer)
        assert sum(map(len, cosets)) == len(group)
        assert len(group) == metadata['group_order']
        assert len(subgroup) == metadata['subgroup_order']
        assert len(metadata['coset_table']) == len(cosets)
        assert task.render_prompt(metadata) == task.render_prompt(entry.metadata)
        assert task.score_answer(entry.answer, entry) == 1.0
        assert task.score_answer(' +00' + entry.answer + '\n', entry) == 1.0
        for junk in ('', 'yes', '-3', '1.5', '12a', str(int(entry.answer) + 1), None):
            assert task.score_answer(junk, entry) == 0.0


@pytest.mark.parametrize('family', FAMILIES)
def test_presentations_and_basis_changes(family):
    relators, images = module.presentation(family, 8)
    group = module.closure(images)
    identity = tuple(range(len(images[0])))
    expected_order = {'dihedral': 2 * len(images[0]), 'abelian': len(images[0]),
                      'tetrahedral': 12, 'octahedral': 24, 'icosahedral': 60}[family]
    assert len(group) == expected_order
    assert module.enumerate_index(relators, [[]])[0] == expected_order
    for axis in (0, 1):
        for sign in (-1, 1):
            replacements = [[1], [2]]
            other = sign * (2 - axis)
            replacements[axis].append(other)
            changed = list(images)
            changed[axis] = module.multiply(images[axis], module.evaluate([-other], images))
            new_relators = [module.substitute(w, replacements) for w in relators]
            assert all(module.evaluate(w, changed) == identity for w in new_relators)
            assert module.closure(changed) == group
            for word in ([1], [2], [1, 2, -1, -2], [2, 1, 1, -2]):
                new_word = module.substitute(word, replacements)
                assert module.evaluate(new_word, changed) == module.evaluate(word, images)
                subgroup = module.closure([module.evaluate(word, images)])
                assert module.enumerate_index(new_relators, [new_word])[0] == len(group) // len(subgroup)


def test_word_helpers_and_prompt_round_trip():
    assert module.multiply((1, 0, 2), (2, 1, 0)) == (1, 2, 0)
    assert module.inverse((1, 2, 0)) == (2, 0, 1)
    assert module.reduce_word([1, 2, -2, -1]) == []
    assert module.substitute([1, -2], [[1], [2, -1]]) == [1, 1, -2]
    assert module.format_word([]) == 'e'
    assert module.format_word([1, 1, -2, 2, 2]) == 'a^2*b^-1*b^2'
    for _ in range(100):
        word = random.choices([1, -1, 2, -2], k=random.randrange(30))
        text = module.format_word(word)
        parsed = []
        if text != 'e':
            for factor in text.split('*'):
                match = re.fullmatch(r'([ab])(?:\^(-?\d+))?', factor)
                assert match
                letter = 1 if match[1] == 'a' else 2
                power = int(match[2] or 1)
                parsed.extend([letter if power > 0 else -letter] * abs(power))
        assert parsed == word


def test_difficulty_distribution_and_prompt():
    task = module.CosetEnumerationIndex()
    configs = []
    for level in (0, 3, 6):
        task.config.set_level(level)
        configs.append((task.config.max_rotation, task.config.basis_changes, task.config.word_length))
        families, answers = set(), set()
        for _ in range(32):
            entry = task.generate_entry()
            families.add(entry.metadata['family'])
            answers.add(entry.answer)
            prompt = task.render_prompt(entry.metadata)
            assert 'Todd–Coxeter' in prompt
            assert 'not their normal closure' in prompt
            assert 'right cosets Hg' in prompt
            assert len(prompt) < 4500
        assert families == set(FAMILIES)
        assert len(answers) >= 5
    assert all(a < b for a, b in zip(configs, configs[1:]))
    task.config.set_level(0)
    assert (task.config.max_rotation, task.config.basis_changes, task.config.word_length) == configs[0]


def test_scorer_does_not_use_self():
    class Inaccessible:
        def __getattribute__(self, name):
            raise AssertionError(name)
    entry = module.Entry(metadata={}, answer='12')
    scorer = module.CosetEnumerationIndex.score_answer
    assert scorer(Inaccessible(), '12', entry) == 1.0
    assert scorer(Inaccessible(), '120', entry) == 0.0
    assert scorer(Inaccessible(), '1' * 10000, entry) == 0.0


def test_incomplete_solver_is_rejected(monkeypatch):
    def fail(*args, **kwargs):
        raise ValueError('coset limit')
    monkeypatch.setattr(module, 'enumerate_index', fail)
    with pytest.raises(RuntimeError, match='48 attempts'):
        module.CosetEnumerationIndex().generate_entry()


def test_wrong_solver_index_is_rejected(monkeypatch):
    monkeypatch.setattr(module, 'enumerate_index', lambda *args: (1, [[0, 0, 0, 0]]))
    with pytest.raises(AssertionError):
        module.CosetEnumerationIndex().generate_entry()

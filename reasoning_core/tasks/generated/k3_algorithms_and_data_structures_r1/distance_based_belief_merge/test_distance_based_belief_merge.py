import itertools
import json
import random

import pytest

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_algorithms_and_data_structures_r1.distance_based_belief_merge.distance_based_belief_merge import (
    BeliefMergeConfig,
    DistanceBasedBeliefMerge,
    RULES,
    _aggregate,
    _merged_models,
    _verify_gold,
)


@pytest.fixture(autouse=True)
def fixed_randomness():
    state = random.getstate()
    random.seed(2267388306)
    yield
    random.setstate(state)


def oracle(bases, rule):
    n = len(next(iter(bases.values()))[0])
    scores = {}
    for bits in itertools.product('01', repeat=n):
        model = ''.join(bits)
        distances = [min(sum(a != b for a, b in zip(model, other)) for other in base)
                     for base in bases.values()]
        scores[model] = {
            'sum': sum(distances),
            'max': max(distances),
            'lex': tuple(sorted(distances, reverse=True)),
        }[rule]
    return sorted(model for model, value in scores.items() if value == min(scores.values()))


@pytest.mark.parametrize('rule', RULES)
def test_exhaustive_two_variable_bases(rule):
    models = ['00', '01', '10', '11']
    families = [list(base) for size in range(2, 5)
                for base in itertools.combinations(models, size)]
    for a, b in itertools.product(families, repeat=2):
        bases = {'A': a, 'B': b}
        winners = _merged_models(bases, rule)
        assert winners == oracle(bases, rule)
        _verify_gold(bases, rule, winners)


def test_operators_have_distinct_semantics():
    bases = {'A': ['000', '001'], 'B': ['110', '111']}
    assert _merged_models(bases, 'sum') == [format(x, '03b') for x in range(8)]
    assert _merged_models(bases, 'max') == ['010', '011', '100', '101']
    bases = {'A': ['00', '11'], 'B': ['01', '10'], 'C': ['00', '01']}
    assert _merged_models(bases, 'max') == ['00', '01', '10', '11']
    assert _merged_models(bases, 'lex') == ['00', '01']
    assert _aggregate('lex', [2, 0, 1]) == (2, 1, 0)
    with pytest.raises(ValueError):
        _aggregate('unknown', [0, 1])


@pytest.mark.parametrize('rule', RULES)
def test_common_models_and_full_ties(rule):
    bases = {'A': ['00', '01'], 'B': ['01', '10']}
    assert _merged_models(bases, rule) == ['01']
    universe = [format(x, '02b') for x in range(4)]
    assert _merged_models({'A': universe, 'B': universe}, rule) == universe


def test_verifier_rejects_incomplete_and_nonoptimal_answers():
    bases = {'A': ['000', '001'], 'B': ['110', '111']}
    for wrong in ([], ['000'], ['010'], ['010', '011', '100', '101', '111']):
        with pytest.raises(AssertionError):
            _verify_gold(bases, 'max', wrong)


@pytest.mark.parametrize('level', range(7))
def test_generated_instances(level):
    task = DistanceBasedBeliefMerge()
    task.config.set_level(level)
    answers = set()
    rules = set()
    for _ in range(30):
        entry = task.generate_entry()
        metadata = json.loads(json.dumps(entry.metadata))
        bases = metadata['bases']
        assert 2 <= len(bases) <= 3
        assert all(2 <= len(models) <= 4 for models in bases.values())
        assert all(len(models) == len(set(models)) for models in bases.values())
        assert not set.intersection(*(set(models) for models in bases.values()))
        assert entry.answer.split(', ') == oracle(bases, metadata['rule'])
        assert task.score_answer(entry.answer, entry) == 1.0
        assert task.render_prompt(metadata) == task.render_prompt(entry.metadata)
        answers.add(entry.answer)
        rules.add(metadata['rule'])
    assert len(answers) > 5
    assert rules == set(RULES)


def test_scorer_requires_complete_canonical_order_without_self():
    class ForbiddenSelf:
        def __getattribute__(self, name):
            raise AssertionError(name)

    entry = Entry(metadata={'num_vars': 3}, answer='001, 100')
    score = DistanceBasedBeliefMerge.score_answer
    for correct in ('001, 100', '001,100', '\n001,  100\n'):
        assert score(ForbiddenSelf(), correct, entry) == 1.0
    for wrong in ('', 'junk', '001', '100, 001', '001, 001, 100', '001, 100,',
                  '[001, 100]', '1, 4', '001, 101', '0 01, 100', None, 4):
        assert score(ForbiddenSelf(), wrong, entry) == 0.0


@pytest.mark.parametrize('rule', RULES)
def test_source_and_bit_permutation_invariance(rule):
    bases = {'A': ['000', '101'], 'B': ['011', '110'], 'C': ['001', '111']}
    winners = _merged_models(bases, rule)
    renamed = {'A': bases['C'], 'B': bases['A'], 'C': bases['B']}
    assert _merged_models(renamed, rule) == winners
    rotated = {name: [model[1:] + model[:1] for model in models]
               for name, models in bases.items()}
    assert _merged_models(rotated, rule) == sorted(model[1:] + model[:1] for model in winners)


def test_difficulty_resets_and_scales():
    config = BeliefMergeConfig()
    config.set_level(0)
    initial = (config.num_vars, config.num_bases, config.models_per_base)
    config.set_level(6)
    assert (config.num_vars, config.num_bases, config.models_per_base) == (6, 3, 4)
    config.set_level(0)
    assert (config.num_vars, config.num_bases, config.models_per_base) == initial


def test_generation_calls_independent_verifier(monkeypatch):
    calls = []

    def checked(bases, rule, winners):
        _verify_gold(bases, rule, winners)
        calls.append((bases, rule, winners))

    monkeypatch.setitem(DistanceBasedBeliefMerge.generate_entry.__globals__, '_verify_gold', checked)
    entry = DistanceBasedBeliefMerge().generate_entry()
    assert len(calls) == 1
    assert calls[0][2] == entry.answer.split(', ')


def test_rejection_budget_is_bounded(monkeypatch):
    calls = []

    def identical_models(population, k):
        calls.append(k)
        return list(range(k))

    monkeypatch.setattr(random, 'sample', identical_models)
    with pytest.raises(RuntimeError, match='could not build instance'):
        DistanceBasedBeliefMerge().generate_entry()
    assert len(calls) == 400


def test_repeated_seed_reproduces_instances():
    sequences = []
    for _ in range(2):
        random.seed(2267388306)
        task = DistanceBasedBeliefMerge()
        examples = []
        for level in (0, 2, 5, 6):
            task.config.set_level(level)
            for _ in range(5):
                entry = task.generate_entry()
                examples.append((task.render_prompt(entry.metadata), entry.answer))
        sequences.append(examples)
    assert sequences[0] == sequences[1]


def test_prompt_explicitly_specifies_domain_metric_and_ties():
    task = DistanceBasedBeliefMerge()
    entry = task.generate_entry()
    for rule in RULES:
        entry.metadata['rule'] = rule
        prompt = task.render_prompt(entry.metadata)
        assert 'not just the listed models' in prompt
        assert 'Hamming distance counts differing bit positions' in prompt
        assert 'include all ties' in prompt
        assert 'without duplicates' in prompt
        assert 'format example:' in prompt
        if rule == 'lex':
            assert 'largest to smallest' in prompt

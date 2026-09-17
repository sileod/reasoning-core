import json
import random
from itertools import combinations, product

from reasoning_core.tasks.generated.k3_controlled_nli_r1.definitional_unfolding_subsumption.definitional_unfolding_subsumption import (
    DefinitionalUnfoldingSubsumption,
    UnfoldingConfig,
    canonical_basis,
    canonical_model,
    entails,
    satisfies,
    unfold,
)


def test_distinct_roles_preserved():
    node = unfold([['part', ['Blue']], ['link', ['Blue']]], {})
    assert len(node[1]) == 2
    assert not entails(unfold([['part', ['Blue']]], {}), node)


def test_existentials_do_not_merge_witnesses():
    split = [['part', ['Blue']], ['part', ['Round']]]
    joint = [['part', ['Blue', 'Round']]]
    assert entails(unfold(joint, {}), unfold(split, {}))
    assert not entails(unfold(split, {}), unfold(joint, {}))
    assert not satisfies(canonical_model(split, {}), joint, {})


def test_one_witness_can_match_multiple_requirements():
    specific = [['part', ['Blue', ['link', ['Round']]]]]
    general = [['part', ['Blue']], ['part', [['link', ['Round']]]]]
    assert entails(unfold(specific, {}), unfold(general, {}))
    assert satisfies(canonical_model(specific, {}), general, {})


def test_deep_acyclic_aliases():
    defs = {'H': ['Blue'], 'J': [['part', ['H']]], 'K': ['J', 'Round']}
    direct = ['Round', ['part', ['Blue']]]
    assert unfold(['K'], defs) == unfold(direct, {})
    assert satisfies(canonical_model(direct, {}), ['K'], defs)
    assert not entails(unfold(['J'], defs), unfold(['K'], defs))


def test_basis_redundancy_equivalence_and_tie_break():
    nodes = {'Aster': unfold(['Blue'], {}), 'Birch': unfold(['Blue'], {}),
             'Cedar': unfold(['Round'], {})}
    assert canonical_basis(list(nodes), nodes) == ['Aster', 'Cedar']
    assert canonical_basis([], {}) == []


def test_joint_coverage_tie_break():
    nodes = {'Aster': unfold(['Blue', 'Light'], {}),
             'Birch': unfold(['Blue', 'Round'], {}),
             'Cedar': unfold(['Round', 'Rigid'], {})}
    assert canonical_basis(list(nodes), nodes) == ['Aster', 'Cedar']
    assert canonical_basis(['Aster', 'Birch'], nodes) == ['Aster', 'Birch']


def test_structural_comparison_against_all_two_individual_models():
    expressions = [[], ['Blue'], ['Round'], ['Blue', 'Round'],
                   [['part', []]], [['part', ['Blue']]],
                   [['part', ['Round']]], [['part', ['Blue', 'Round']]],
                   [['part', ['Blue']], ['part', ['Round']]]]
    models = []
    for bits in product([False, True], repeat=8):
        labels = [{name for j, name in enumerate(['Blue', 'Round']) if bits[2*i+j]}
                  for i in range(2)]
        edges = [[('part', j) for j in range(2) if bits[4+2*i+j]] for i in range(2)]
        models.append((labels, edges))
    for a, b in product(expressions, repeat=2):
        semantic = all(not satisfies(m, a, {}) or satisfies(m, b, {}) for m in models)
        assert entails(unfold(a, {}), unfold(b, {})) == semantic


def test_generation_gold_and_exhaustive_minimality():
    random.seed(138)
    task = DefinitionalUnfoldingSubsumption()
    for level in range(7):
        task.config.set_level(level)
        answers = set()
        for _ in range(12):
            entry = task.generate_entry()
            m = entry.metadata
            definitions = m['definitions']
            models = [canonical_model(q, definitions) for q in m['queries']]
            common = sorted(n for n in m['names'] if all(satisfies(v, [n], definitions) for v in models))
            valid = []
            for size in range(len(common) + 1):
                for subset in combinations(common, size):
                    model = canonical_model(subset, definitions)
                    if all(satisfies(model, [n], definitions) for n in common):
                        valid.append(subset)
            best = min(valid, key=lambda x: (len(x), x))
            assert entry.answer == (' & '.join(best) or 'TOP')
            assert task.score_answer(entry.answer, entry) == 1
            assert task.score_answer('', entry) == 0
            assert task.score_answer('yes', entry) == 0
            assert task.score_answer('banana', entry) == 0
            assert task.score_answer(entry.answer.lower(), entry) == 0
            restored = json.loads(json.dumps(m))
            assert task.render_prompt(restored) == task.render_prompt(m)
            answers.add(entry.answer)
        assert len(answers) > 3


def test_scorer_has_no_self_access_and_enforces_order():
    class Poison:
        def __getattribute__(self, name):
            raise AssertionError(name)

    task = DefinitionalUnfoldingSubsumption()
    entry = task.generate_entry()
    assert DefinitionalUnfoldingSubsumption.score_answer(Poison(), entry.answer, entry) == 1
    entry.answer = 'Aster & Cedar'
    assert task.score_answer('Cedar & Aster', entry) == 0
    assert task.score_answer('Aster & Cedar & Cedar', entry) == 0


def test_conjunction_order_duplicates_and_nested_scopes():
    expr = ['Blue', ['part', ['Round', ['link', ['Light']]]]]
    reordered = [['part', [['link', ['Light']], 'Round']], 'Blue', 'Blue']
    misplaced = ['Blue', 'Round', ['part', [['link', ['Light']]]]]
    assert unfold(expr, {}) == unfold(reordered, {})
    assert not entails(unfold(misplaced, {}), unfold(expr, {}))
    assert not entails(unfold(expr, {}), unfold(misplaced, {}))


def test_reproducible_generation_and_rng_not_reseeded(monkeypatch):
    state = random.getstate()
    task = DefinitionalUnfoldingSubsumption()
    first = task.generate_entry()
    random.setstate(state)
    second = task.generate_entry()
    assert first.answer == second.answer
    assert first.metadata == second.metadata

    def forbidden(*args, **kwargs):
        raise AssertionError('Generator reseeded the RNG')

    monkeypatch.setattr(random, 'seed', forbidden)
    task.generate_entry()


def test_config_scaling_resets():
    cfg = UnfoldingConfig()
    cfg.set_level(0)
    base = (cfg.candidates, cfg.depth, cfg.width)
    cfg.set_level(6)
    assert all(a < b for a, b in zip(base, (cfg.candidates, cfg.depth, cfg.width)))
    cfg.set_level(0)
    assert base == (cfg.candidates, cfg.depth, cfg.width)

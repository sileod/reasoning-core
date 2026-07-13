import pytest
import z3

import reasoning_core.tasks.coreference as coreference_module

from reasoning_core.tasks.coreference import (
    DESC,
    DESC_EVENT,
    INTRO,
    NAME,
    PRONOUN,
    Coreference,
    CoreferenceCSP,
    CoreferenceCSPConfig,
    CoreferenceConfig,
    Factor,
    _Entity,
    _add_event,
    _heuristic_observations,
    _indef,
    _mention,
    _rows_score,
    _sample_mappings,
    compile_evidence,
    compile_z3,
    domains_from_evidence,
    entailed_value,
    entailment_status,
    factor_holds,
    gac_round,
    generate_csp_balanced_batch,
    event_matches_for_mention,
    min_proof_depth,
    necessary_constraints,
    query_genders,
    resolve_mention,
    validate_query,
)


def _entities():
    return (
        _Entity(0, 'John', 'm', 'doctor', ('quiet', 'tall')),
        _Entity(1, 'Mary', 'f', 'lawyer', ('kind', 'young')),
        _Entity(2, 'Paul', 'm', 'teacher', ('loud', 'short')),
        _Entity(3, 'Anna', 'f', 'nurse', ('old', 'stern')),
    )


def _fixed_chain(depth=3):
    john, mary, paul, anna = _entities()
    lines, mentions = [], []
    _add_event(lines, mentions, _mention(john, 'a male doctor named John', INTRO),
               _mention(mary, 'a female lawyer named Mary', INTRO), 'met')
    _add_event(lines, mentions, _mention(paul, 'a male teacher named Paul', INTRO),
               _mention(anna, 'a female nurse named Anna', INTRO), 'called')
    pair = _add_event(lines, mentions, _mention(john, 'the doctor', DESC),
                      _mention(mary, 'the lawyer', DESC), 'praised')
    for _ in range(1, depth):
        pair = _add_event(lines, mentions, _mention(john, 'He', PRONOUN),
                          _mention(mary, 'her', PRONOUN), 'helped')
    return lines, mentions, pair


@pytest.mark.parametrize('depth', [1, 2, 3])
def test_exact_minimum_proof_depth(depth):
    _, mentions, pair = _fixed_chain(depth)
    for query in pair:
        assert set(resolve_mention(query['idx'], mentions)) == {query['entity']}
        assert min_proof_depth(query, mentions) == depth
        assert validate_query(query, mentions, depth)


def test_long_pronoun_chain_is_not_confused_with_direct_description():
    _, mentions, pair = _fixed_chain(3)
    seed = mentions[pair[0]['idx'] - 4]
    assert seed['mode'] == DESC
    assert min_proof_depth(seed, mentions) == 1
    assert min_proof_depth(pair[0], mentions) == 3


def test_later_introduction_does_not_change_earlier_description():
    john, mary, _, _ = _entities()
    other = _Entity(4, 'Mark', 'm', 'doctor', ('old', 'short'))
    lines, mentions = [], []
    _add_event(lines, mentions, _mention(john, 'a male doctor named John', INTRO),
               _mention(mary, 'a female lawyer named Mary', INTRO), 'met')
    query, _ = _add_event(lines, mentions, _mention(john, 'the doctor', DESC),
                          _mention(mary, 'Mary', NAME), 'called')
    _add_event(lines, mentions, _mention(other, 'a male doctor named Mark', INTRO),
               _mention(mary, 'Mary', NAME), 'helped')
    assert set(resolve_mention(query['idx'], mentions)) == {john}


def test_event_descriptions_ignore_current_and_future_events():
    john, mary, paul, anna = _entities()
    lines, mentions = [], []
    _add_event(lines, mentions, _mention(john, 'a male doctor named John', INTRO),
               _mention(mary, 'a female lawyer named Mary', INTRO), 'called')
    spec = {'verb': 'called', 'target_pos': 'subject', 'argument': mary}
    query, _ = _add_event(
        lines, mentions,
        dict(_mention(john, 'the person who called Mary', DESC_EVENT),
             event_desc=spec),
        _mention(anna, 'a female nurse named Anna', INTRO), 'called')
    _add_event(lines, mentions, _mention(paul, 'a male teacher named Paul', INTRO),
               _mention(mary, 'Mary', NAME), 'called')
    assert event_matches_for_mention(query, mentions) == [john]


def test_generated_names_are_all_modeled_mentions():
    entry = Coreference().generate_entry()
    lines = entry.metadata.sentences.splitlines()
    for line_idx, line in enumerate(lines):
        for entity in entry.metadata.pool:
            if entity.name in line:
                assert any(m['line_idx'] == line_idx and m['entity'] == entity
                           for m in entry.metadata.mentions)


@pytest.mark.parametrize('field', [
    'n_ambiguous_mentions', 'n_constraints', 'n_rules',
    'n_identity_links', 'n_state_changes',
])
def test_unsound_global_modes_fail_clearly(field):
    config = CoreferenceConfig()
    setattr(config, field, 1)
    with pytest.raises(ValueError, match='disabled'):
        Coreference(config).generate_entry()


def test_role_queries_fail_until_identity_necessity_is_validated():
    with pytest.raises(ValueError, match='Role queries are disabled'):
        Coreference(CoreferenceConfig(p_compositional_query=1)).generate_entry()


@pytest.mark.parametrize('correct', [0, 20])
def test_balancing_rejects_positive_and_inverse_shortcuts(correct):
    rows = {('nearest_same_gender_name', ('pron', 3)): [20, 20, correct, 10.0]}
    assert not _rows_score(rows, eps=0.1, min_n=20)[1]


def test_balancing_accepts_chance_level_accuracy():
    rows = {('nearest_same_gender_name', ('pron', 3)): [20, 20, 10, 10.0]}
    assert _rows_score(rows, eps=0.1, min_n=20)[1]


def test_csp_factor_primitives_and_synchronous_gac():
    different = Factor('different', (0, 1))
    participant = Factor('previous_participant', (2, 0, 1))
    assert factor_holds(different, (0, 1))
    assert not factor_holds(different, (1, 1))
    assert factor_holds(participant, (1, 0, 1))
    assert not factor_holds(participant, (2, 0, 1))
    domains = {0: {0}, 1: {1}, 2: {0, 1, 2}}
    assert gac_round(domains, [participant])[2] == {0, 1}


def test_csp_entailed_value_on_tiny_problem():
    mentions = [{'idx': 0}, {'idx': 1}]
    domains = {0: {0, 1}, 1: {1}}
    factors = [Factor('different', (0, 1))]
    variables, constraints = compile_z3(mentions, [], domains, factors)
    assert entailed_value(variables[0], constraints, domains[0]) == 0


def test_csp_lexical_evidence_can_be_masked():
    entities = _entities()[:2]
    lines, mentions = [], []
    _add_event(lines, mentions,
               _mention(entities[0], 'John', NAME),
               _mention(entities[1], 'Mary', NAME))
    evidence = compile_evidence(mentions, entities)
    domains = domains_from_evidence(mentions, entities, evidence)
    masked = domains_from_evidence(mentions, entities, evidence, {0})
    assert domains[0] == {entities[0].eid}
    assert masked[0] == {entity.eid for entity in entities}


@pytest.mark.parametrize('family', ['permutation', 'relational'])
@pytest.mark.parametrize('depth', [1, 2, 3, 4, 5, 6, 7, 8])
def test_csp_generator_certifies_requested_propagation_depth(family, depth):
    task = CoreferenceCSP(CoreferenceCSPConfig(
        family=family, target_depth=depth, balanced_generation=False,
        max_attempts=20))
    entry = task.generate_entry()
    query_idx = entry.metadata.q['idx']
    query_key = str(query_idx)
    trace = entry.metadata.propagation_trace
    assert entry.metadata.answer_eid in trace[-1][query_key]
    assert entry.metadata.propagation_depth == depth
    assert len(trace[-2][query_key]) > 1
    assert len(trace[-1][query_key]) == 1
    assert all(entry.metadata.initial_domains.values())
    assert entry.metadata.full_csp_sat
    assert entry.metadata.z3_entailed
    assert not entry.metadata.answer_name_in_distractors
    assert len(entry.metadata.necessary_factor_indices) == depth
    assert ({'pair_transition', 'event_role'} &
            set(entry.metadata.necessary_factor_kinds))
    if family == 'relational':
        assert entry.metadata.prefix_entailed is False
        assert len(entry.metadata.post_query_necessary_factor_indices) >= 1
        assert 'event_role' in entry.metadata.necessary_factor_kinds
        assert entry.metadata.necessary_factor_kinds.count(
            'pair_transition') == depth - 1
        assert any(entry.metadata.factors[i].sentence >
                   entry.metadata.q['line_idx']
                   for i in entry.metadata.necessary_factor_indices)
    else:
        if depth > 1:
            assert entry.metadata.mappings.count('swap') >= 1
        assert entry.metadata.necessary_factor_kinds == [
            'pair_transition'] * depth
    assert task.score_answer(entry.answer, entry) == 1


def test_csp_odd_pool_introduces_each_entity_once_and_excludes_answer_distractors():
    task = CoreferenceCSP(CoreferenceCSPConfig(
        family='mixed', n_entities=7, balanced_generation=False))
    entry = task.generate_entry()
    introductions = [mention['entity'].eid for mention in entry.metadata.mentions
                     if mention['mode'] == INTRO]
    assert sorted(introductions) == sorted(entity.eid
                                           for entity in entry.metadata.pool)
    distractor_start = (len(entry.metadata.sentences.splitlines()) -
                        task.config.n_distractor_sentences)
    assert all(not (mention['line_idx'] >= distractor_start and
                    mention['mode'] == NAME and
                    mention['entity'].eid == entry.metadata.answer_eid)
               for mention in entry.metadata.mentions)


def test_csp_shared_role_is_not_fixed_to_doctor():
    roles = set()
    config = CoreferenceCSPConfig(family='permutation',
                                  balanced_generation=False)
    for _ in range(30):
        entry = CoreferenceCSP(config).generate_entry()
        roles.add(entry.metadata.q['entity'].role)
    assert len(roles) > 1


def test_csp_shortcut_strata_separate_family_and_use_description_domain():
    task = CoreferenceCSP(CoreferenceCSPConfig(
        family='relational', n_same_gender_distractors=4,
        balanced_generation=False))
    raw = task.generate_raw_candidate()
    strata = {observation[0][1]
              for observation in _heuristic_observations(raw)}
    assert strata == {('relational', task.config.target_depth, 2,
                       raw.q['pos'])}


def test_default_permutation_depth_has_both_parities_and_query_positions():
    task = CoreferenceCSP(CoreferenceCSPConfig(
        family='permutation', balanced_generation=False))
    entries = [task.generate_entry() for _ in range(40)]
    assert {entry.metadata.mappings.count('swap') % 2
            for entry in entries} == {0, 1}
    assert {entry.metadata.q['pos'] for entry in entries} == {
        'subject', 'object'}
    assert {(entry.metadata.q['pos'], entry.metadata.query_source_position)
            for entry in entries} == {
        ('subject', 'subject'), ('subject', 'object'),
        ('object', 'subject'), ('object', 'object')}


def test_symmetric_families_do_not_force_anchor_or_complement_answers():
    task = CoreferenceCSP(CoreferenceCSPConfig(
        family='relational', balanced_generation=False))
    correctness = {'last_unique_anchor': set(),
                   'other_than_last_anchor': set(),
                   'transition_parity_ignored': set()}
    for _ in range(40):
        raw = task.generate_raw_candidate()
        for (name, _), _, correct, _ in _heuristic_observations(raw):
            if name in correctness:
                correctness[name].add(bool(correct))
    assert all(values == {False, True} for values in correctness.values())


def test_depth_one_permutation_supports_both_mappings():
    assert {_sample_mappings(1, 0.5, require_swap=False)[0]
            for _ in range(100)} == {'same', 'swap'}


def test_depth_one_balancing_has_no_impossible_permutation_strata():
    config = CoreferenceCSPConfig(
        family='permutation', target_depth=1, balanced_generation=False,
        shortcut_min_n=1, max_attempts=20)
    batch = generate_csp_balanced_batch(
        CoreferenceCSP(config), 4, oversample=8, eps=1.0)
    assert {(item.q['pos'], item.query_source_position) for item in batch} == {
        ('subject', 'subject'), ('subject', 'object'),
        ('object', 'subject'), ('object', 'object')}


def test_unknown_z3_result_is_not_a_necessity_certificate(monkeypatch):
    class UnknownSolver:
        def set(self, **kwargs):
            pass

        def add(self, *constraints):
            pass

        def check(self):
            return z3.unknown

    mentions = [{'idx': 0}, {'idx': 1}]
    domains = {0: {0, 1}, 1: {1}}
    factors = [Factor('different', (0, 1))]
    variables, constraints = compile_z3(mentions, [], domains, factors)
    monkeypatch.setattr(coreference_module.z3, 'Solver', UnknownSolver)
    assert entailment_status(0, 0, variables, constraints) is None
    assert necessary_constraints(
        0, 0, mentions, [], domains, factors) is None


def test_gender_heuristics_do_not_read_hidden_query_entity():
    male = _Entity(0, 'John', 'm', 'doctor', ('quiet', 'tall'))
    female = _Entity(1, 'Mary', 'f', 'doctor', ('kind', 'young'))
    lines, mentions = [], []
    _add_event(lines, mentions, _mention(male, _indef(male), INTRO),
               _mention(female, _indef(female), INTRO))
    query, _ = _add_event(lines, mentions,
                          _mention(male, 'the doctor', DESC),
                          _mention(female, 'Mary', NAME))
    assert query_genders(query, mentions, [male, female]) == {'m', 'f'}

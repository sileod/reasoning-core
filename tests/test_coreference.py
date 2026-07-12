import pytest

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
    _mention,
    _rows_score,
    compile_z3,
    entailed_value,
    factor_holds,
    gac_round,
    event_matches_for_mention,
    min_proof_depth,
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


@pytest.mark.parametrize('depth', [1, 2, 3, 4, 5, 6])
def test_csp_generator_certifies_requested_propagation_depth(depth):
    task = CoreferenceCSP(CoreferenceCSPConfig(target_depth=depth,
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
    assert task.score_answer(entry.answer, entry) == 1

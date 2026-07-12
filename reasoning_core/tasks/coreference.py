import random
from dataclasses import dataclass
from itertools import product

import z3

from reasoning_core.template import Config, Entry, Task, edict


ROLES = ['doctor', 'lawyer', 'teacher', 'engineer', 'pilot', 'chef',
         'writer', 'nurse', 'banker', 'farmer', 'scientist', 'baker']
ATTR_GROUPS = [['tall', 'short'], ['young', 'old'],
               ['quiet', 'loud'], ['kind', 'stern']]
VERBS = ['met', 'called', 'praised', 'avoided', 'questioned', 'greeted',
         'thanked', 'watched', 'helped']
NAMES_M = ['John', 'Paul', 'Mark', 'Leo', 'Tom', 'Sam', 'Max', 'Ben',
           'Adam', 'Noah', 'Luke', 'Eric', 'Jack', 'Hugo', 'Alan', 'Owen']
NAMES_F = ['Mary', 'Anna', 'Jane', 'Eve', 'Sara', 'Lucy', 'Zoe', 'Rita',
           'Emma', 'Nora', 'Lily', 'Mia', 'Rose', 'Iris', 'Lena', 'Kate']
PRON = {'m': ('He', 'him'), 'f': ('She', 'her')}
INTRO, NAME, DESC, DESC_EVENT, PRONOUN = (
    'intro', 'name', 'desc', 'desc_event', 'pron')


@dataclass(frozen=True)
class _Entity:
    eid: int
    name: str
    gender: str
    role: str
    attrs: tuple


@dataclass(frozen=True)
class Derivation:
    entity: _Entity
    rule: str
    dependencies: tuple
    evidence: tuple
    depth: int

    @property
    def signature(self):
        return (self.rule, self.dependencies, self.evidence)


def _pool(n, single_gender=False):
    if n < 2:
        raise ValueError("Coreference requires at least two entities")
    if n > len(NAMES_M) + len(NAMES_F):
        raise ValueError("Not enough distinct names for the requested entities")
    if single_gender:
        names = random.sample(random.choice([NAMES_M, NAMES_F]), n)
        genders = ['m' if names[0] in NAMES_M else 'f'] * n
    else:
        low = 2 if n >= 4 else 1
        n_m = random.randint(max(low, n - len(NAMES_F)),
                             min(n - low, len(NAMES_M)))
        names = random.sample(NAMES_M, n_m) + random.sample(NAMES_F, n - n_m)
        genders = ['m'] * n_m + ['f'] * (n - n_m)
    pairs = list(zip(names, genders))
    random.shuffle(pairs)
    return [_Entity(i, name, gender, random.choice(ROLES),
                    tuple(sorted(random.choice(group)
                                 for group in random.sample(ATTR_GROUPS, 2))))
            for i, (name, gender) in enumerate(pairs)]


def _indef(entity):
    gender = 'male' if entity.gender == 'm' else 'female'
    words = (*entity.attrs, gender, entity.role)
    desc = ' '.join(words)
    article = 'an' if desc[0].lower() in 'aeiou' else 'a'
    return f"{article} {desc} named {entity.name}"


def _surface_parts(surface):
    words = (surface[4:] if surface.lower().startswith('the ') else surface).split()
    return words[-1].lower(), tuple(word.lower() for word in words[:-1])


def _matches_desc(entity, role, attrs):
    return entity.role == role and set(attrs) <= set(entity.attrs)


def _desc(entity, visible):
    """Return a shortest visible description unique to ``entity``."""
    same_role = [candidate for candidate in visible if candidate.role == entity.role]
    if len(same_role) == 1:
        return f"the {entity.role}"
    for attr in entity.attrs:
        if sum(attr in candidate.attrs for candidate in same_role) == 1:
            return f"the {attr} {entity.role}"
    if sum(set(entity.attrs) <= set(candidate.attrs)
           for candidate in same_role) == 1:
        return f"the {' '.join(entity.attrs)} {entity.role}"
    return None


def _descriptions(entity, visible):
    """Return every available description of ``entity``, unique or not."""
    descriptions = [f"the {entity.role}"]
    descriptions.extend(f"the {attr} {entity.role}" for attr in entity.attrs)
    descriptions.append(f"the {' '.join(entity.attrs)} {entity.role}")
    return [description for description in dict.fromkeys(descriptions)
            if entity in {candidate for candidate in visible
                          if _matches_desc(candidate, *_surface_parts(description))}]


def _order(mention):
    return (mention['line_idx'], 0 if mention['pos'] == 'subject' else 1)


def _before(query, mentions):
    return [mention for mention in mentions if _order(mention) < _order(query)]


def _visible_entities(query, mentions, masked=frozenset()):
    return {
        mention['entity']
        for mention in _before(query, mentions)
        if mention['mode'] == INTRO and mention['idx'] not in masked
    }


def _pronoun_gender(surface):
    return 'm' if surface.lower() in ('he', 'him') else 'f'


def _pronoun_antecedents(query, mentions):
    """Nearest earlier, gender-compatible mention in the parallel position."""
    gender = _pronoun_gender(query['surface'])
    earlier = _before(query, mentions)
    for event_idx in sorted({m['event_idx'] for m in earlier}, reverse=True):
        tier = [m for m in earlier
                if m['event_idx'] == event_idx and m['pos'] == query['pos']
                and m['entity'].gender == gender]
        if tier:
            return tuple(m['idx'] for m in tier)
    return ()


def _dedupe(proofs):
    out = {}
    for proof in proofs:
        key = (proof.entity, proof.depth, proof.signature)
        out[key] = proof
    return sorted(out.values(), key=lambda p: (p.depth, p.signature))


def resolve_mention(mention_idx, mentions, masked=frozenset(), _cache=None,
                    _visiting=frozenset()):
    """Resolve a mention from visible evidence, returning every derivation.

    Gold entities label explicit introductions and validate generated mentions;
    pronouns and descriptions are resolved independently of their gold label.
    """
    masked = frozenset(masked)
    cache = {} if _cache is None else _cache
    key = (mention_idx, masked)
    if key in cache:
        return cache[key]
    if mention_idx in masked or mention_idx in _visiting:
        return {}

    query = mentions[mention_idx]
    visiting = _visiting | {mention_idx}
    proofs = []
    if query['mode'] in (INTRO, NAME):
        proofs.append(Derivation(query['entity'], 'explicit_name', (),
                                 (mention_idx,), 0))
    elif query['mode'] == DESC:
        role, attrs = _surface_parts(query['surface'])
        for entity in _visible_entities(query, mentions, masked):
            if _matches_desc(entity, role, attrs):
                intros = tuple(m['idx'] for m in _before(query, mentions)
                               if m['mode'] == INTRO and m['entity'] == entity
                               and m['idx'] not in masked)
                proofs.append(Derivation(entity, 'description', intros,
                                         intros, 1))
    elif query['mode'] == PRONOUN:
        antecedents = _pronoun_antecedents(query, mentions)
        if len(antecedents) == 1:
            antecedent = antecedents[0]
            resolved = resolve_mention(antecedent, mentions, masked, cache,
                                       visiting)
            for candidates in resolved.values():
                for proof in candidates:
                    dependencies = tuple(sorted(set(
                        proof.dependencies + (antecedent,))))
                    proofs.append(Derivation(
                        proof.entity, 'parallel_pronoun', dependencies,
                        (antecedent,), proof.depth + 1))
    elif query['mode'] == DESC_EVENT:
        spec = query['event_desc']
        for event in _events(mentions):
            if event['line_idx'] >= query['line_idx'] or event['verb'] != spec['verb']:
                continue
            target_pos = spec['target_pos']
            arg_pos = 'object' if target_pos == 'subject' else 'subject'
            arg_proofs = resolve_mention(event[arg_pos], mentions, masked,
                                         cache, visiting)
            target_proofs = resolve_mention(event[target_pos], mentions, masked,
                                            cache, visiting)
            for arg in arg_proofs.get(spec['argument'], ()):
                for target_list in target_proofs.values():
                    for target in target_list:
                        deps = tuple(sorted(set(arg.dependencies + target.dependencies +
                                                (event[arg_pos], event[target_pos]))))
                        proofs.append(Derivation(
                            target.entity, 'event_description', deps,
                            (event['idx'],), 1 + max(arg.depth, target.depth)))

    result = {}
    for proof in _dedupe(proofs):
        result.setdefault(proof.entity, []).append(proof)
    cache[key] = result
    return result


def _events(mentions):
    events = {mention['event']['idx']: mention['event']
              for mention in mentions if mention.get('event')}
    return [events[idx] for idx in sorted(events)]


def event_matches_for_mention(query, mentions):
    """Compatibility helper: unique matching entities, never event occurrences."""
    return sorted(resolve_mention(query['idx'], mentions), key=lambda e: e.eid)


def min_proof_depth(query, mentions):
    resolved = resolve_mention(query['idx'], mentions)
    proofs = resolved.get(query['entity'], ())
    return min((proof.depth for proof in proofs), default=None)


def _minimal_proofs(query, mentions):
    resolved = resolve_mention(query['idx'], mentions)
    if set(resolved) != {query['entity']}:
        return []
    depth = min(proof.depth for proof in resolved[query['entity']])
    return [proof for proof in resolved[query['entity']] if proof.depth == depth]


def _load_bearing(query, mentions, proof):
    for dependency in proof.dependencies:
        resolved = resolve_mention(query['idx'], mentions, {dependency})
        depths = [candidate.depth
                  for candidate in resolved.get(query['entity'], ())]
        if depths and min(depths) <= proof.depth:
            return False
    return True


def validate_query(query, mentions, target_depth):
    proofs = _minimal_proofs(query, mentions)
    return (len(proofs) == 1 and proofs[0].depth == target_depth and
            _load_bearing(query, mentions, proofs[0]))


def antecedent_path(query, mentions):
    """Generator provenance only; correctness uses ``resolve_mention``."""
    path, current, seen = [], query, set()
    while current['idx'] not in seen:
        path.append(current)
        seen.add(current['idx'])
        antecedents = _pronoun_antecedents(current, mentions) if current['mode'] == PRONOUN else ()
        if len(antecedents) != 1:
            break
        current = mentions[antecedents[0]]
    return list(reversed(path))


def _get_hops(query, mentions):
    return min_proof_depth(query, mentions)


def _add_event(lines, mentions, subject, obj, verb=None):
    line_idx = len(lines)
    subject = dict(subject, idx=len(mentions), line_idx=line_idx,
                   event_idx=line_idx, sent=line_idx, pos='subject', event=None)
    mentions.append(subject)
    obj = dict(obj, idx=len(mentions), line_idx=line_idx, event_idx=line_idx,
               sent=line_idx, pos='object', event=None)
    mentions.append(obj)
    verb = verb or random.choice(VERBS)
    event = {'idx': line_idx, 'line_idx': line_idx, 'event_idx': line_idx,
             'sent': line_idx, 'verb': verb,
             'subject': subject['idx'], 'object': obj['idx']}
    mentions[-2]['event'] = event
    mentions[-1]['event'] = event
    cap = subject['surface'][:1].upper() + subject['surface'][1:]
    lines.append(f"({line_idx + 1}) {cap} {verb} {obj['surface']}.")
    return mentions[-2], mentions[-1]


def _mention(entity, surface, mode):
    return {'entity': entity, 'surface': surface, 'mode': mode,
            'antecedent': None, 'scope': None, 'event_desc': None,
            'ambiguous': False}


def _build_discourse(pool, target_depth, n_distractors):
    if target_depth < 1:
        raise ValueError("target_hops must be at least 1")
    opposite = [(a, b) for a in pool for b in pool
                if a.gender != b.gender and a != b]
    subject, obj = random.choice(opposite)
    order = random.sample(pool, len(pool))
    lines, mentions = [], []

    for i in range(0, len(order), 2):
        pair = order[i:i + 2]
        if len(pair) == 1:
            pair.append(random.choice(order[:i]))
        refs = [_mention(e, _indef(e), INTRO) if e == order[i]
                or e not in {m['entity'] for m in mentions}
                else _mention(e, e.name, NAME)
                for e in pair]
        _add_event(lines, mentions, refs[0], refs[1])

    for _ in range(n_distractors):
        # Repeating either chain entities or distractors lets batch balancing
        # decorrelate explicit-name recency from the answer.
        a, b = random.sample(pool, 2)
        _add_event(lines, mentions, _mention(a, a.name, NAME),
                   _mention(b, b.name, NAME))

    subject_desc, object_desc = _desc(subject, pool), _desc(obj, pool)
    if not subject_desc or not object_desc:
        return None
    pair = _add_event(lines, mentions, _mention(subject, subject_desc, DESC),
                      _mention(obj, object_desc, DESC))
    for _ in range(1, target_depth):
        pair = _add_event(
            lines, mentions,
            _mention(subject, PRON[subject.gender][0], PRONOUN),
            _mention(obj, PRON[obj.gender][1], PRONOUN))
    return lines, mentions, pair


def _candidate_domain(query, mentions):
    gender = query['entity'].gender
    return {entity for entity in _visible_entities(query, mentions)
            if entity.gender == gender}


def h_nearest_same_gender_name(query, mentions):
    for mention in reversed(_before(query, mentions)):
        if (mention['mode'] in (INTRO, NAME) and
                mention['entity'].gender == query['entity'].gender):
            return mention['entity']
    return None


def h_first_same_gender_name(query, mentions):
    for mention in _before(query, mentions):
        if mention['mode'] == INTRO and mention['entity'].gender == query['entity'].gender:
            return mention['entity']
    return None


def h_previous_sentence_name(query, mentions):
    matches = [mention['entity'] for mention in _before(query, mentions)
               if mention['line_idx'] == query['line_idx'] - 1
               and mention['mode'] in (INTRO, NAME)
               and mention['entity'].gender == query['entity'].gender]
    return matches[0] if len(set(matches)) == 1 else None


HEURISTICS = {
    'nearest_same_gender_name': h_nearest_same_gender_name,
    'first_same_gender_name': h_first_same_gender_name,
    'previous_sentence_name': h_previous_sentence_name,
}
BALANCE_HEURISTICS = set(HEURISTICS)


def _as_raw_item(item):
    if isinstance(item, dict) and 'q' in item:
        return item
    return item.metadata


def _heuristic_rows(items):
    rows = {}
    for item in items:
        for key, prediction, is_correct, chance in _heuristic_observations(item):
            n, covered, n_correct, chance_sum = rows.get(key, [0, 0, 0, 0.0])
            n += 1
            if prediction is not None:
                covered += 1
                n_correct += is_correct
                chance_sum += chance
            rows[key] = [n, covered, n_correct, chance_sum]
    return rows


def _heuristic_observations(item):
    raw = _as_raw_item(item)
    query, mentions = raw['q'], raw['mentions']
    depth = raw.get('min_proof_depth') or min_proof_depth(query, mentions)
    stratum = (query['mode'], depth)
    domain = _candidate_domain(query, mentions)
    chance = 1 / len(domain) if domain else 0.0
    return [((name, stratum), prediction, prediction == query['entity'], chance)
            for name, heuristic in HEURISTICS.items()
            for prediction in (heuristic(query, mentions),)]


def shortcut_report(items):
    report = []
    for (name, stratum), (n, covered, correct, chance_sum) in sorted(
            _heuristic_rows(items).items()):
        report.append({
            'heuristic': name,
            'stratum': stratum,
            'n': n,
            'coverage': covered / n if n else 0.0,
            'accuracy': correct / covered if covered else None,
            'chance_accuracy': chance_sum / covered if covered else None,
        })
    return report


def _rows_score(rows, eps, min_n):
    score, acceptable = 0.0, True
    for (name, _), (_, covered, correct, chance_sum) in rows.items():
        if name not in BALANCE_HEURISTICS or covered < min_n:
            continue
        deviation = abs(correct / covered - chance_sum / covered)
        score += max(0.0, deviation - eps) ** 2
        acceptable &= deviation <= eps
    return score, acceptable


def _shortcut_score(items, eps=0.08, min_n=20):
    return _rows_score(_heuristic_rows(items), eps, min_n)


def shortcut_stats_ok(items, eps=0.08, min_n=20):
    return _shortcut_score(items, eps, min_n)[1]


def subsample_shortcut_balanced(candidates, n_final, eps=0.08, min_n=20):
    remaining = list(candidates)
    random.shuffle(remaining)
    selected, totals = [], {}
    observations = {id(item): _heuristic_observations(item) for item in remaining}
    while remaining and len(selected) < n_final:
        scored = []
        for i, item in enumerate(remaining):
            trial = {key: row[:] for key, row in totals.items()}
            _add_observations(trial, observations[id(item)])
            scored.append((_rows_score(trial, eps, 1)[0], random.random(), i))
        _, _, best = min(scored)
        item = remaining.pop(best)
        selected.append(item)
        _add_observations(totals, observations[id(item)])
    return selected


def _add_observations(rows, observations):
    for key, prediction, correct, chance in observations:
        n, covered, n_correct, chance_sum = rows.get(key, [0, 0, 0, 0.0])
        rows[key] = [n + 1,
                     covered + (prediction is not None),
                     n_correct + (correct if prediction is not None else 0),
                     chance_sum + (chance if prediction is not None else 0.0)]


def generate_balanced_batch(task, n_final, oversample=20, eps=0.08):
    candidates = [task.generate_raw_candidate()
                  for _ in range(n_final * oversample)]
    selected = subsample_shortcut_balanced(
        candidates, n_final, eps, task.config.shortcut_min_n)
    if len(selected) != n_final or not shortcut_stats_ok(
            selected, eps, task.config.shortcut_min_n):
        raise RuntimeError("Could not construct a shortcut-balanced batch")
    return selected


@dataclass
class CoreferenceConfig(Config):
    n_entities: int = 6
    n_distractors: int = 2
    p_desc_event: float = 0.0
    target_hops: int = 3
    single_gender_pool: bool = False
    balanced_generation: bool = False
    oversample: int = 8
    balance_batch_size: int = 64
    shortcut_eps: float = 0.10
    shortcut_min_n: int = 20
    p_compositional_query: float = 0.0
    n_ambiguous_mentions: int = 0
    n_constraints: int = 0
    n_rules: int = 0
    n_identity_links: int = 0
    n_state_changes: int = 0
    require_same_gender_distractor: bool = True

    def apply_difficulty(self, level):
        self.n_entities += level
        self.n_distractors += level
        self.target_hops += level


class Coreference(Task):
    summary = "Resolve reference chains whose shortest proof has a known depth."
    config_cls = CoreferenceConfig

    def __init__(self, config=None):
        super().__init__(config=config or CoreferenceConfig())
        self._balanced_buffer = []

    def _validate_config(self):
        cfg = self.config
        unsupported = {
            name: getattr(cfg, name)
            for name in ('n_ambiguous_mentions', 'n_constraints', 'n_rules',
                         'n_identity_links', 'n_state_changes')
            if getattr(cfg, name)
        }
        if unsupported:
            names = ', '.join(sorted(unsupported))
            raise ValueError(
                f"Global coreference mode is disabled pending assignment-aware semantics: {names}")
        if cfg.p_compositional_query:
            raise ValueError(
                "Role queries are disabled pending identity-necessity validation")
        if cfg.p_desc_event:
            raise ValueError(
                "Generated event descriptions are disabled pending compositional realization")
        if cfg.single_gender_pool:
            raise ValueError(
                "single_gender_pool is incompatible with non-reflexive paired chains")

    def generate_raw_candidate(self):
        self._validate_config()
        cfg = self.config
        for _ in range(300):
            pool = _pool(cfg.n_entities)
            built = _build_discourse(pool, cfg.target_hops, cfg.n_distractors)
            if not built:
                continue
            lines, mentions, final_pair = built
            query = random.choice(final_pair)
            if (cfg.require_same_gender_distractor and
                    len(_candidate_domain(query, mentions)) < 2):
                continue
            if not validate_query(query, mentions, cfg.target_hops):
                continue
            proof = _minimal_proofs(query, mentions)[0]
            problem = self._build(query, lines, mentions, proof)
            return edict({
                'problem': problem,
                'q': query,
                'mentions': mentions,
                'pool': pool,
                'hops': proof.depth,
                'min_proof_depth': proof.depth,
                'proof_signature': proof.signature,
                'mode': query['mode'],
                'target_hops': cfg.target_hops,
            })
        raise RuntimeError("Could not generate a valid coreference problem")

    def generate_entry(self):
        cfg = self.config
        if not cfg.balanced_generation:
            return self.generate_raw_candidate()['problem']
        if not self._balanced_buffer:
            self._balanced_buffer = generate_balanced_batch(
                self, max(1, cfg.balance_batch_size), cfg.oversample,
                cfg.shortcut_eps)
        return self._balanced_buffer.pop()['problem']

    def _build(self, query, lines, mentions, proof):
        sentence = query['line_idx'] + 1
        trace = (f"s{sentence} {query['mode']} '{query['surface']}' | "
                 f"depth={proof.depth}; dependencies={proof.dependencies} -> "
                 f"{query['entity'].name}")
        metadata = edict({
            'sentences': '\n'.join(lines),
            'q_sentence': sentence,
            'q_position': query['pos'],
            'q_expression': query['surface'],
            'query_kind': 'name',
            'q': query,
            'mentions': mentions,
            'pool': sorted(_visible_entities(query, mentions), key=lambda e: e.eid),
            'target_hops': self.config.target_hops,
            'hops': proof.depth,
            'min_proof_depth': proof.depth,
            'proof_signature': proof.signature,
            'all_minimal_proofs': [proof.signature],
            'realized_distractor_count': self.config.n_distractors,
            'realized_ambiguity_count': 0,
            'realized_constraint_count': 0,
            'identity_required_for_answer': True,
            'diagnostic_trace': trace,
        })
        return Entry(metadata=metadata, answer=query['entity'].name)

    def render_prompt(self, metadata):
        return (
            "Interpret each expression using only earlier sentences. Pronouns "
            "continue the nearest gender-compatible reference in the same "
            "grammatical position.\n\n"
            f"{metadata['sentences']}\n\n"
            f"In sentence {metadata['q_sentence']}, who does the "
            f"{metadata['q_position']} expression "
            f"'{metadata['q_expression']}' refer to?\n"
            "The answer is one name."
        )

    def score_answer(self, answer, entry):
        def normalize(value):
            words = str(value or '').strip().strip('.').strip("'\"").split()
            return (words or [''])[-1].lower()
        return float(normalize(answer) == normalize(entry.answer))


@dataclass(frozen=True)
class Factor:
    kind: str
    scope: tuple
    data: tuple = ()
    sentence: int = 0


@dataclass
class CSPSeed:
    pool: list
    mention_specs: list
    event_specs: list
    query_idx: int
    intended_gold: int


def initial_domains(mentions, pool):
    by_gender = {
        gender: {entity.eid for entity in pool if entity.gender == gender}
        for gender in ('m', 'f')
    }
    domains = {}
    for mention in mentions:
        idx = mention['idx']
        if mention['mode'] in (INTRO, NAME):
            domains[idx] = {mention['entity'].eid}
        elif mention['mode'] == DESC:
            role, attrs = _surface_parts(mention['surface'])
            domains[idx] = {
                entity.eid for entity in _visible_entities(mention, mentions)
                if _matches_desc(entity, role, attrs)
            }
        elif mention['mode'] == PRONOUN:
            domains[idx] = set(by_gender[_pronoun_gender(mention['surface'])])
        else:
            raise ValueError(f"Unsupported CSP mention mode: {mention['mode']}")
    return domains


def compile_factors(mentions):
    factors = []
    for event in _events(mentions):
        factors.append(Factor('different',
                              (event['subject'], event['object']),
                              sentence=event['line_idx']))
    for mention in mentions:
        if mention['mode'] != PRONOUN:
            continue
        previous = mention['line_idx'] - 1
        events = [event for event in _events(mentions)
                  if event['line_idx'] == previous]
        if events:
            event = events[0]
            factors.append(Factor(
                'previous_participant',
                (mention['idx'], event['subject'], event['object']),
                sentence=mention['line_idx']))
    return factors


def factor_holds(factor, values):
    if factor.kind == 'different':
        return values[0] != values[1]
    if factor.kind == 'previous_participant':
        return values[0] == values[1] or values[0] == values[2]
    raise ValueError(factor.kind)


def compile_z3(mentions, pool, domains, factors):
    del pool
    variables = {mention['idx']: z3.Int(f"m{mention['idx']}")
                 for mention in mentions}
    constraints = []
    for idx, domain in domains.items():
        constraints.append(z3.Or(*[variables[idx] == value
                                   for value in sorted(domain)]))
    for factor in factors:
        xs = [variables[idx] for idx in factor.scope]
        if factor.kind == 'different':
            constraints.append(xs[0] != xs[1])
        elif factor.kind == 'previous_participant':
            constraints.append(z3.Or(xs[0] == xs[1], xs[0] == xs[2]))
        else:
            raise ValueError(factor.kind)
    return variables, constraints


def possible_values(variable, constraints, domain):
    possible = set()
    for value in domain:
        solver = z3.Solver()
        solver.add(*constraints, variable == value)
        if solver.check() == z3.sat:
            possible.add(value)
    return possible


def entailed_value(variable, constraints, domain):
    possible = possible_values(variable, constraints, domain)
    return next(iter(possible)) if len(possible) == 1 else None


def revise_factor(factor, domains):
    scope = factor.scope
    revised = {idx: set(domains[idx]) for idx in scope}
    for position, idx in enumerate(scope):
        others = scope[:position] + scope[position + 1:]
        for value in domains[idx]:
            for other_values in product(*(domains[j] for j in others)):
                values = list(other_values)
                values.insert(position, value)
                if factor_holds(factor, tuple(values)):
                    break
            else:
                revised[idx].discard(value)
    return revised


def gac_round(domains, factors):
    proposals = {idx: set(values) for idx, values in domains.items()}
    for factor in factors:
        for idx, values in revise_factor(factor, domains).items():
            proposals[idx] &= values
    return proposals


def propagation_trace(query_idx, domains, factors, max_rounds=100):
    current = {idx: set(values) for idx, values in domains.items()}
    trace = [current]
    for _ in range(max_rounds):
        if len(current[query_idx]) == 1:
            break
        updated = gac_round(current, factors)
        if any(not values for values in updated.values()):
            return None
        if updated == current:
            break
        current = updated
        trace.append(current)
    return trace


def propagation_depth(query_idx, domains, factors):
    trace = propagation_trace(query_idx, domains, factors)
    if trace is None or len(trace[-1][query_idx]) != 1:
        return None
    return len(trace) - 1


def is_entailed(query_idx, gold, variables, constraints):
    solver = z3.Solver()
    solver.add(*constraints, variables[query_idx] != gold)
    return solver.check() == z3.unsat


def necessary_constraints(query_idx, gold, mentions, pool, domains, factors):
    necessary = []
    for i in range(len(factors)):
        reduced = factors[:i] + factors[i + 1:]
        variables, constraints = compile_z3(mentions, pool, domains, reduced)
        if not is_entailed(query_idx, gold, variables, constraints):
            necessary.append(i)
    return necessary


def minimal_support(query_idx, gold, mentions, pool, domains, factors):
    """Version-one support certificate: individually necessary factors."""
    return necessary_constraints(query_idx, gold, mentions, pool, domains,
                                 factors)


@dataclass
class CoreferenceCSPConfig(Config):
    n_entities: int = 6
    n_same_gender: int = 4
    n_sentences: int = 6
    target_depth: int = 3
    min_query_domain: int = 2
    candidate_width: int = 2
    p_name: float = 0.15
    p_partial_desc: float = 0.45
    p_pronoun: float = 0.40
    n_distractor_sentences: int = 2
    antecedent_window: int = 1
    balanced_generation: bool = False
    balance_batch_size: int = 64
    oversample: int = 12
    shortcut_eps: float = 0.10
    shortcut_min_n: int = 20
    max_attempts: int = 1000

    def apply_difficulty(self, level):
        self.apply_depth_difficulty(level)

    def apply_depth_difficulty(self, level):
        self.target_depth += level
        self.n_sentences += level

    def apply_width_difficulty(self, level):
        self.n_entities += level
        self.n_same_gender += level
        self.candidate_width += level

    def apply_noise_difficulty(self, level):
        self.n_distractor_sentences += level


class CoreferenceCSP(Task):
    summary = "Resolve globally entailed coreferences at a certified propagation depth."
    config_cls = CoreferenceCSPConfig

    def __init__(self, config=None):
        super().__init__(config=config or CoreferenceCSPConfig())
        self._balanced_buffer = []

    def _sample_seed(self):
        cfg = self.config
        if cfg.target_depth < 1:
            raise ValueError("target_depth must be at least 1")
        if cfg.antecedent_window != 1:
            raise ValueError("Only previous-sentence anaphora is supported")
        width = max(2, cfg.candidate_width, cfg.n_same_gender)
        if width > len(NAMES_M):
            raise ValueError("n_same_gender/candidate_width exceeds the name pool")
        n = max(cfg.n_entities, width + 2)
        gender = random.choice(('m', 'f'))
        names = random.sample(NAMES_M if gender == 'm' else NAMES_F, width)
        candidates = [
            _Entity(i, name, gender, 'doctor',
                    tuple(group[(i >> bit) & 1]
                          for bit, group in enumerate(ATTR_GROUPS)))
            for i, name in enumerate(names)
        ]
        other_names = random.sample(NAMES_F if gender == 'm' else NAMES_M,
                                    n - width)
        others = [
            _Entity(width + i, name, 'f' if gender == 'm' else 'm',
                    ROLES[(i + 1) % len(ROLES)],
                    tuple(group[i % 2] for group in ATTR_GROUPS[:2]))
            for i, name in enumerate(other_names)
        ]
        pool = candidates + others
        gold, _ = random.sample(candidates, 2)
        blocker = random.choice(others)
        return CSPSeed(pool, [], [], -1, gold.eid), gold, blocker

    def _realize_seed(self, sampled):
        seed, gold, blocker = sampled
        lines, mentions = [], []
        order = list(seed.pool)
        random.shuffle(order)
        for i in range(0, len(order), 2):
            pair = order[i:i + 2]
            if len(pair) == 1:
                pair.append(random.choice(order[:i]))
            _add_event(lines, mentions,
                       _mention(pair[0], _indef(pair[0]), INTRO),
                       _mention(pair[1], _indef(pair[1]), INTRO))

        # A narrow description anchors the tree. Each following pronoun has a
        # broad same-gender domain and adds exactly one synchronous GAC round;
        # the opposite-gender object cannot be its antecedent.
        subject, _ = _add_event(
            lines, mentions,
            _mention(gold, 'the ' + ' '.join((*gold.attrs, gold.role)), DESC),
            _mention(blocker, blocker.name, NAME))
        query = subject
        for _ in range(self.config.target_depth):
            query, _ = _add_event(
                lines, mentions,
                _mention(gold, PRON[gold.gender][0], PRONOUN),
                _mention(blocker, blocker.name, NAME))
        seed.query_idx = query['idx']
        distractors = [entity for entity in seed.pool
                       if entity not in (gold, blocker)]
        for _ in range(self.config.n_distractor_sentences):
            a, b = random.sample(distractors, 2)
            _add_event(lines, mentions, _mention(a, a.name, NAME),
                       _mention(b, b.name, NAME))
        return seed, lines, mentions

    def _validate_candidate(self, seed, lines, mentions, domains, factors):
        query_idx = seed.query_idx
        if len(domains[query_idx]) < self.config.min_query_domain:
            return None
        variables, constraints = compile_z3(mentions, seed.pool, domains, factors)
        gold = entailed_value(variables[query_idx], constraints,
                              domains[query_idx])
        if gold != seed.intended_gold:
            return None
        trace = propagation_trace(query_idx, domains, factors)
        depth = propagation_depth(query_idx, domains, factors)
        if depth != self.config.target_depth or trace is None:
            return None
        if len(trace[depth - 1][query_idx]) <= 1 or len(trace[depth][query_idx]) != 1:
            return None
        necessary = minimal_support(query_idx, gold, mentions, seed.pool,
                                    domains, factors)
        query = mentions[query_idx]
        audit_domains = lambda item: {str(idx): sorted(values)
                                      for idx, values in item.items()}
        metadata = edict({
            'sentences': '\n'.join(lines), 'q': query, 'mentions': mentions,
            'pool': seed.pool, 'propagation_depth': depth, 'factors': factors,
            'initial_domains': audit_domains(domains),
            'final_domains': audit_domains(trace[-1]),
            'propagation_trace': [audit_domains(item) for item in trace],
            'necessary_factor_indices': necessary,
            'necessary_sentence_indices': sorted({factors[i].sentence
                                                  for i in necessary}),
            'initial_query_domain_size': len(domains[query_idx]),
            'final_query_domain_size': len(trace[-1][query_idx]),
            'identity_required_for_answer': True, 'z3_entailed': True,
            'q_sentence': query['line_idx'] + 1,
            'q_position': query['pos'], 'q_expression': query['surface'],
            'answer_eid': gold,
            'realized_distractor_count': self.config.n_distractor_sentences,
        })
        # EasyDict recursively converts mappings and rejects integer keys.
        # Preserve the natural mention-indexed domain representation verbatim.
        return Entry(metadata=metadata,
                     answer=next(e.name for e in seed.pool if e.eid == gold))

    def generate_raw_candidate(self):
        for _ in range(self.config.max_attempts):
            seed, lines, mentions = self._realize_seed(self._sample_seed())
            domains = initial_domains(mentions, seed.pool)
            if any(not values for values in domains.values()):
                continue
            factors = compile_factors(mentions)
            candidate = self._validate_candidate(seed, lines, mentions,
                                                 domains, factors)
            if candidate is not None:
                return edict({'problem': candidate, 'q': candidate.metadata.q,
                              'mentions': mentions, 'pool': seed.pool,
                              'propagation_depth': self.config.target_depth})
        raise RuntimeError("Could not generate a valid CSP coreference problem")

    def generate_entry(self):
        return self.generate_raw_candidate()['problem']

    def render_prompt(self, metadata):
        return (
            "Interpret all expressions jointly.\n\n"
            "- A name refers to the named person.\n"
            "- A description may refer to any previously introduced person matching all of its words.\n"
            "- A pronoun refers to a gender-compatible participant of the previous sentence.\n"
            "- The subject and object of one sentence are different people.\n"
            "- Later sentences may disambiguate expressions in earlier sentences.\n\n"
            f"{metadata['sentences']}\n\n"
            f"In sentence {metadata['q_sentence']}, who does the "
            f"{metadata['q_position']} expression '{metadata['q_expression']}' refer to?\n"
            "The answer is one name."
        )

    score_answer = Coreference.score_answer

import random
import itertools
from dataclasses import dataclass
from reasoning_core.template import Task, Entry, Config, edict

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
AGENT_NOUN = {'called': 'caller'}
INTRO, NAME, DESC, DESC_EVENT, PRONOUN = 'intro', 'name', 'desc', 'desc_event', 'pron'


@dataclass(frozen=True)
class _Entity:
    eid: int; name: str; gender: str; role: str; attrs: tuple


def _pool(n, single_gender=False):
    if single_gender:
        n = min(n, len(NAMES_M), len(NAMES_F))
        gender = random.choice(['m', 'f'])
        names = random.sample(NAMES_M if gender == 'm' else NAMES_F, n)
        genders = [gender] * n
    else:
        n = min(n, len(NAMES_M) + len(NAMES_F))
        lo, hi = max(1, n - len(NAMES_F)), min(n - 1, len(NAMES_M))
        n_m = random.randint(lo, hi) if lo <= hi else lo
        names = random.sample(NAMES_M, n_m) + random.sample(NAMES_F, n - n_m)
        genders = ['m'] * n_m + ['f'] * (n - n_m)
    pairs = list(zip(names, genders)); random.shuffle(pairs)
    return [_Entity(i, pairs[i][0], pairs[i][1], random.choice(ROLES),
                    tuple(sorted(random.choice(g)
                                 for g in random.sample(ATTR_GROUPS, 2))))
            for i in range(n)]


def _indef(e):
    desc = e.role
    det = "an" if desc[0].lower() in 'aeiou' else "a"
    return f"{det} {desc} named {e.name}"


def _attr_fact(e, attr):
    return f"{e.name} was {attr}."


def _desc(e, pool):
    """Minimal definite NP uniquely picking e out of scope, else None."""
    same = [x for x in pool if x.role == e.role]
    if len(same) == 1:
        return f"the {e.role}"
    for a in e.attrs:
        if sum(a in x.attrs for x in same) == 1:
            return f"the {a} {e.role}"
    if sum(set(e.attrs) <= set(x.attrs) for x in same) == 1:
        return f"the {' '.join(e.attrs)} {e.role}"
    return None


def _surface_parts(surface):
    surf = surface[4:] if surface.startswith('the ') else surface
    parts = surf.split()
    return parts[-1], parts[:-1]


def _matches_desc(e, role, attrs):
    return e.role == role and all(a in e.attrs for a in attrs)


def global_matches_for_surface(q, pool):
    role, attrs = _surface_parts(q['surface'])
    return [x for x in pool if _matches_desc(x, role, attrs)]


def scope_matches_for_surface(q, scope):
    role, attrs = _surface_parts(q['surface'])
    return [x for x in scope if _matches_desc(x, role, attrs)]


def _display_ref(m):
    if m['mode'] in (INTRO, NAME, PRONOUN):
        return m['entity'].name
    s = m['surface']
    return s[:1].lower() + s[1:]


def _event_surface(event, target_pos, arg):
    verb = event['verb']
    arg_ref = _display_ref(arg)
    if target_pos == 'subject':
        forms = []
        if verb in AGENT_NOUN:
            forms.append(f"the {AGENT_NOUN[verb]}")
        forms.extend([f"the person who {verb} {arg_ref}",
                      f"the one who {verb} {arg_ref}"])
        return random.choice(forms)
    return random.choice([f"the person {arg_ref} {verb}",
                          f"the one {arg_ref} {verb}"])


def event_matches_for_mention(q, mentions):
    event = q.get('event_desc')
    if not event:
        return []
    out = []
    agent_verb = next((v for v, n in AGENT_NOUN.items()
                       if q['surface'] == f"the {n}"), None)
    for e in {m['event']['idx']: m['event'] for m in mentions if m.get('event')}.values():
        if e['verb'] != event['verb']:
            continue
        target_pos = event['target_pos']
        if agent_verb:
            if e['verb'] == agent_verb and target_pos == 'subject':
                out.append(mentions[e['subject']]['entity'])
            continue
        arg_key = 'object' if target_pos == 'subject' else 'subject'
        if mentions[e[arg_key]]['entity'] != mentions[event[arg_key]]['entity']:
            continue
        out.append(mentions[e[target_pos]]['entity'])
    return out


def _recent_scope(mentions, sent, window=3):
    return {
        m['entity']
        for m in mentions
        if max(0, sent - window) <= m['sent'] < sent
    }


def _has_same_gender_distractor(e, mentions, sent, window):
    ctx = _recent_scope(mentions, sent, window)
    return any(x.gender == e.gender and x != e for x in ctx)


def _mention_rank(m):
    return (m['sent'], 0 if m['pos'] == 'subject' else 1)


def _latest_mention(entity, mentions, sent=None, scope=None):
    cands = [m for m in mentions if m['entity'] == entity]
    if sent is not None:
        cands = [m for m in cands if m['sent'] < sent]
    if scope is not None:
        cands = [m for m in cands if m['entity'] in scope]
    return max(cands, key=_mention_rank) if cands else None


def _pronoun_gender(surface):
    s = surface.lower()
    if s in ('he', 'him'):
        return 'm'
    if s in ('she', 'her'):
        return 'f'
    return None


def _pronoun_salience_antecedent(gender, mentions, sent, cur_subj, pos, window=3):
    preferred_pos = 'subject' if pos == 'subject' else 'object'
    for s in range(sent - 1, max(-1, sent - window - 1), -1):
        preferred = [m for m in mentions
                     if m['sent'] == s and m['pos'] == preferred_pos]
        preferred = [m for m in preferred
                     if m['entity'].gender == gender and
                     not (pos == 'object' and m['entity'] == cur_subj)]
        if len(preferred) == 1:
            return preferred[0]
    return None


def _desc_antecedent(entity, mentions, sent, scope):
    if entity not in scope:
        return None
    ant = _latest_mention(entity, mentions, sent=sent, scope=scope)
    return ant


def _event_desc(entity, mentions, sent):
    events = {m['event']['idx']: m['event'] for m in mentions
              if m.get('event') and m['event']['sent'] < sent}
    choices = []
    for event in events.values():
        for target_pos, arg_pos in (('subject', 'object'), ('object', 'subject')):
            target = mentions[event[target_pos]]
            if target['entity'] != entity:
                continue
            arg = mentions[event[arg_pos]]
            if arg['mode'] not in (INTRO, NAME, DESC):
                continue
            q = {
                'surface': _event_surface(event, target_pos, arg),
                'mode': DESC_EVENT,
                'entity': entity,
                'event_desc': dict(event, target_pos=target_pos),
                'antecedent': target['idx'],
            }
            if len(event_matches_for_mention(q, mentions)) == 1:
                choices.append((q['surface'], target['idx'], q['event_desc']))
    return random.choice(choices) if choices else (None, None, None)


def _sample_chain_positions(n, chain_len, max_gap=3):
    for _ in range(100):
        pos = sorted(random.sample(range(n), chain_len))
        if pos[0] <= max_gap and all(b - a <= max_gap for a, b in zip(pos, pos[1:])):
            return pos
    pos = [random.randrange(min(max_gap, n))]
    while len(pos) < chain_len:
        lo = pos[-1] + 1
        hi = min(n - (chain_len - len(pos)), pos[-1] + max_gap)
        pos.append(random.randint(lo, hi))
    return pos


def _plan(pool, chain_len, n_distractors, max_gap=3):
    """Locally coherent discourse without a globally privileged target."""
    n = chain_len + n_distractors
    cur = tuple(random.sample(pool, 2))
    chain_positions = set(_sample_chain_positions(n, chain_len, max_gap=max_gap))
    out = []

    for i in range(n):
        if i == 0 or i in chain_positions:
            keep = random.choice(cur)
            other = random.choice([e for e in pool if e != keep])
            cur = (keep, other) if random.random() < 0.5 else (other, keep)
        else:
            anchor = random.choice(cur)
            similar = [e for e in pool if e != anchor and
                       (e.gender == anchor.gender or e.role == anchor.role)]
            other = random.choice(similar or [e for e in pool if e != anchor])
            cur = (anchor, other) if random.random() < 0.5 else (other, anchor)
        out.append(cur)

    return out


def antecedent_path(q, mentions):
    path = []
    cur = q
    seen = set()
    while cur and id(cur) not in seen:
        path.append(cur)
        seen.add(id(cur))
        ant = cur.get('antecedent')
        if ant is None:
            break
        cur = mentions[ant]
    return list(reversed(path))


def _get_hops(m, mentions):
    return max(0, len(antecedent_path(m, mentions)) - 1)


def _local_candidate_entities(q, mentions, pool, pronoun_window=3):
    if q['mode'] == PRONOUN:
        gender = _pronoun_gender(q['surface'])
        cur_subj = None
        if q['pos'] == 'object':
            subj = [m for m in mentions
                    if m['sent'] == q['sent'] and m['pos'] == 'subject']
            cur_subj = subj[0]['entity'] if subj else None
        ents = {
            m['entity']
            for m in mentions
            if max(0, q['sent'] - pronoun_window) <= m['sent'] < q['sent']
            and m['entity'].gender == gender
            and m['entity'] != cur_subj
        }
        return sorted(ents, key=lambda e: e.eid)
    if q['mode'] == DESC:
        scope = q.get('scope') or []
        return sorted(scope_matches_for_surface(q, scope), key=lambda e: e.eid)
    if q['mode'] == DESC_EVENT:
        return sorted(set(event_matches_for_mention(q, mentions)), key=lambda e: e.eid)
    return [q['entity']]


def _entity_for_idx(idx, assignment, mentions):
    return assignment.get(idx, mentions[idx]['entity'])


def _event_entities(event, assignment, mentions):
    return (_entity_for_idx(event['subject'], assignment, mentions),
            _entity_for_idx(event['object'], assignment, mentions))


def _assignment_ok(assignment, mentions, constraints, rules):
    events = {m['event']['idx']: m['event'] for m in mentions if m.get('event')}.values()
    for c in constraints:
        kind = c['kind']
        if kind == 'identity':
            ok = (_entity_for_idx(c['left'], assignment, mentions) ==
                  _entity_for_idx(c['right'], assignment, mentions))
        elif kind == 'not_identity':
            ok = (_entity_for_idx(c['left'], assignment, mentions) !=
                  _entity_for_idx(c['right'], assignment, mentions))
        elif kind == 'event_role':
            event = mentions[c['mention']]['event']
            idx = event[c['pos']]
            ok = _entity_for_idx(idx, assignment, mentions).role == c['role']
        elif kind == 'no_same_object':
            ok = True
            evs = list(events)
            for a in evs:
                for b in evs:
                    if a['idx'] == b['idx']:
                        continue
                    if a['verb'] == c['verb1'] and b['verb'] == c['verb2']:
                        sa, oa = _event_entities(a, assignment, mentions)
                        sb, ob = _event_entities(b, assignment, mentions)
                        if sa == sb and oa == ob:
                            ok = False
                            break
                if not ok:
                    break
        else:
            ok = True
        if not ok:
            return False
    for rule in rules:
        for event in events:
            subj, obj = _event_entities(event, assignment, mentions)
            if event['verb'] == rule['verb'] and subj.role == rule['subject_role']:
                if (obj.role == rule['object_role']) == rule.get('polarity', True):
                    continue
                return False
    return True


def solve_global_assignments(mentions, pool, constraints=None, rules=None,
                             pronoun_window=3):
    constraints = constraints or []
    rules = rules or []
    variables, domains = [], []
    for m in mentions:
        if m.get('ambiguous'):
            domain = _local_candidate_entities(m, mentions, pool, pronoun_window)
            variables.append(m['idx'])
            domains.append(domain or [m['entity']])
    if not variables:
        return [{}]

    out = []
    for values in itertools.product(*domains):
        assignment = dict(zip(variables, values))
        if _assignment_ok(assignment, mentions, constraints, rules):
            out.append(assignment)
    return out


def globally_pins_query(q, mentions, pool, constraints=None, rules=None,
                        pronoun_window=3):
    constraints = constraints or []
    rules = rules or []
    variables, domains = [], []
    for m in mentions:
        if m.get('ambiguous'):
            variables.append(m['idx'])
            domains.append(_local_candidate_entities(m, mentions, pool, pronoun_window)
                           or [m['entity']])
    vals = set()
    for values in itertools.product(*domains):
        assignment = dict(zip(variables, values))
        if not _assignment_ok(assignment, mentions, constraints, rules):
            continue
        vals.add(_entity_for_idx(q['idx'], assignment, mentions))
        if len(vals) > 1:
            return False
    return vals == {q['entity']}


def surface_antecedent(q, mentions, pronoun_window=3):
    if q['mode'] == PRONOUN:
        gender = _pronoun_gender(q['surface'])
        cur_subj = None
        if q['pos'] == 'object':
            subj = [m for m in mentions
                    if m['sent'] == q['sent'] and m['pos'] == 'subject']
            cur_subj = subj[0]['entity'] if subj else None
        return _pronoun_salience_antecedent(gender, mentions, q['sent'],
                                            cur_subj, q['pos'],
                                            pronoun_window)
    if q['mode'] == DESC:
        scope = q.get('scope') or []
        matches = scope_matches_for_surface(q, scope)
        if len(matches) != 1 or matches[0] != q['entity']:
            return None
        return _desc_antecedent(q['entity'], mentions, q['sent'], set(scope))
    if q['mode'] == DESC_EVENT:
        matches = event_matches_for_mention(q, mentions)
        if len(matches) != 1 or matches[0] != q['entity']:
            return None
        ant = q.get('antecedent')
        return mentions[ant] if ant is not None else None
    return None


def surface_identifiable(q, mentions, pronoun_window=3):
    ant = surface_antecedent(q, mentions, pronoun_window)
    return ant is not None and ant.get('idx') == q.get('antecedent')


def _surface_salience_name_pred(q, mentions, pronoun_window=3):
    ant = surface_antecedent(q, mentions, pronoun_window)
    if ant is not None and ant['mode'] in (INTRO, NAME):
        return ant['entity']
    return None


def _query_candidates(mentions, pool, target_hops=2, cfg=None, challenge=None):
    counts = {}
    for m in mentions:
        counts[m['entity']] = counts.get(m['entity'], 0) + 1

    top = max(counts.values())
    unique_top = list(counts.values()).count(top) == 1
    cands = []
    direct_constraint_cands = []

    for m in mentions:
        if m['mode'] not in (PRONOUN, DESC, DESC_EVENT):
            continue
        use_global = cfg and any([
            cfg.n_ambiguous_mentions, cfg.n_constraints, cfg.n_rules,
            cfg.n_identity_links, cfg.n_state_changes,
        ])
        if use_global and not m.get('ambiguous'):
            continue
        if not use_global and not surface_identifiable(m, mentions,
                                                       cfg.pronoun_window if cfg else 3):
            continue
        if use_global and not globally_pins_query(
                m, mentions, pool,
                (challenge or {}).get('constraints'),
                (challenge or {}).get('rules'),
                cfg.pronoun_window):
            continue
        direct_constraint = use_global and _constraint_lookup_pred(m, mentions, challenge or {}) == m['entity']
        hops = _get_hops(m, mentions)
        if hops != target_hops:
            continue
        if unique_top and counts[m['entity']] == top:
            continue

        if m['mode'] == DESC:
            if len(global_matches_for_surface(m, pool)) < 2:
                continue
        elif m['mode'] == DESC_EVENT:
            if len(event_matches_for_mention(m, mentions)) != 1:
                continue
        elif cfg and cfg.require_same_gender_distractor:
            if not _has_same_gender_distractor(m['entity'], mentions, m['sent'],
                                               cfg.pronoun_window):
                continue
            ant = mentions[m['antecedent']]
            if not (1 < m['sent'] - ant['sent'] <= cfg.pronoun_window):
                continue

        if target_hops >= 2:
            ant = mentions[m['antecedent']]
            if ant['mode'] in (INTRO, NAME):
                continue
            path = antecedent_path(m, mentions)
            if len(path) <= 2:
                continue
            if _surface_salience_name_pred(m, mentions,
                                           cfg.pronoun_window if cfg else 3) == m['entity']:
                continue
            if (cfg and cfg.require_opaque_link_for_multihop and
                    (not any(p['mode'] in (DESC, DESC_EVENT) for p in path[:-1]) or
                     not any(p['mode'] == PRONOUN for p in path[:-1]))):
                continue

        if direct_constraint:
            direct_constraint_cands.append(m)
        else:
            cands.append(m)

    return cands or direct_constraint_cands


def _pick(e, pool, introduced, mentions, sent, cur_subj, pos, p_pron, p_desc,
          p_desc_event=0.4, pronoun_window=3, ambiguous_budget=None):
    if e not in introduced:
        return _indef(e), INTRO, None, None, None, False
    prefs = []
    if random.random() < p_pron: prefs.append(PRONOUN)
    if random.random() < p_desc_event: prefs.append(DESC_EVENT)
    if random.random() < p_desc: prefs.append(DESC)
    prefs.append(NAME)
    for m in prefs:
        if m == PRONOUN:
            if ambiguous_budget and ambiguous_budget[0] > 0:
                q = {'mode': PRONOUN, 'surface': PRON[e.gender][0 if pos == 'subject' else 1],
                     'sent': sent, 'pos': pos, 'entity': e}
                domain = _local_candidate_entities(q, mentions, pool, pronoun_window)
                ant = _latest_mention(e, mentions, sent=sent)
                if ant is not None and e in domain and len(domain) >= 2:
                    ambiguous_budget[0] -= 1
                    return q['surface'], PRONOUN, ant['idx'], None, None, True
            ant = _pronoun_salience_antecedent(e.gender, mentions, sent, cur_subj,
                                               pos, pronoun_window)
            if ant is not None and ant['entity'] == e:
                return PRON[e.gender][0 if pos == 'subject' else 1], PRONOUN, ant['idx'], None, None, False
        if m == DESC_EVENT:
            d, ant, event = _event_desc(e, mentions, sent)
            if d:
                return d, DESC_EVENT, ant, None, event, False
        if m == DESC:
            scope = _recent_scope(mentions, sent)
            d = _desc(e, scope or pool)
            ant = _desc_antecedent(e, mentions, sent, scope)
            if d and ant is not None:
                return d, DESC, ant['idx'], list(scope), None, False
        if m == NAME:
            return e.name, NAME, None, None, None, False
    return e.name, NAME, None, None, None, False


def _emit(plan, pool, p_pron, p_desc, p_desc_event=0.4, pronoun_window=3,
          n_ambiguous_mentions=0):
    introduced, lines, mentions = set(), [], []
    ambiguous_budget = [n_ambiguous_mentions]
    for _, (s_e, o_e) in enumerate(plan):
        sent = len(lines)
        v = random.choice(VERBS)
        new_entities = [e for e in (s_e, o_e) if e not in introduced]
        s_ref, s_mode, s_ant, s_scope, s_event, s_amb = _pick(
            s_e, pool, introduced, mentions, sent, None, 'subject',
            p_pron, p_desc, p_desc_event, pronoun_window, ambiguous_budget)
        introduced.add(s_e)
        o_ref, o_mode, o_ant, o_scope, o_event, o_amb = _pick(
            o_e, pool, introduced, mentions, sent, s_e, 'object',
            p_pron, p_desc, p_desc_event, pronoun_window, ambiguous_budget)
        introduced.add(o_e)
        cap = lambda s: s[:1].upper() + s[1:]
        lines.append(f"({sent+1}) {cap(s_ref)} {v} {o_ref}.")
        mentions.append({'idx': len(mentions), 'sent': sent, 'pos': 'subject',
                         'surface': s_ref, 'mode': s_mode, 'entity': s_e,
                         'antecedent': s_ant, 'scope': s_scope,
                         'event_desc': s_event, 'event': None,
                         'ambiguous': s_amb})
        mentions.append({'idx': len(mentions), 'sent': sent, 'pos': 'object',
                         'surface': o_ref, 'mode': o_mode, 'entity': o_e,
                         'antecedent': o_ant, 'scope': o_scope,
                         'event_desc': o_event, 'event': None,
                         'ambiguous': o_amb})
        event = {'idx': sent, 'sent': sent, 'verb': v,
                 'subject': mentions[-2]['idx'], 'object': mentions[-1]['idx']}
        mentions[-2]['event'] = event
        mentions[-1]['event'] = event
        for e in new_entities:
            for attr in e.attrs:
                lines.append(f"({len(lines)+1}) {_attr_fact(e, attr)}")
    return lines, mentions


def _expr_ref(m):
    return f"the {m['pos']} expression in sentence {m['sent'] + 1}"


def _event_constraint_line(c, mentions):
    event = mentions[c['mention']]['event']
    target_pos = c['pos']
    arg_pos = 'object' if target_pos == 'subject' else 'subject'
    arg = mentions[event[arg_pos]]
    surface = _event_surface(event, target_pos, arg)
    return f"{surface[:1].upper() + surface[1:]} was a {c['role']}."


def _add_global_challenge(lines, mentions, pool, cfg):
    constraints, rules, identity_links, state_changes = [], [], [], []
    targets = [m for m in mentions if m.get('ambiguous')]
    random.shuffle(targets)

    grouped = {}
    for m in targets:
        grouped.setdefault(m['entity'], []).append(m)
    linked_rhs = set()
    for ms in grouped.values():
        if len(ms) < 2 or len(identity_links) >= cfg.n_identity_links:
            continue
        a, b = ms[0], ms[1]
        constraints.append({'kind': 'identity', 'left': a['idx'], 'right': b['idx']})
        identity_links.append((a['idx'], b['idx']))
        linked_rhs.add(b['idx'])
        lines.append(f"({len(lines)+1}) The people referred to by '{a['surface']}' in sentence {a['sent'] + 1} and '{b['surface']}' in sentence {b['sent'] + 1} were the same person.")

    ordered_targets = (
        [m for m in targets if m['idx'] in linked_rhs] +
        [m for m in targets if m['idx'] not in linked_rhs]
    )
    for m in ordered_targets[:cfg.n_constraints]:
        c = {'kind': 'event_role', 'mention': m['idx'],
             'pos': m['pos'], 'role': m['entity'].role}
        constraints.append(c)
        lines.append(f"({len(lines)+1}) {_event_constraint_line(c, mentions)}")

    evs = list({m['event']['idx']: m['event'] for m in mentions if m.get('event')}.values())
    for a in evs:
        for b in evs:
            if a['idx'] == b['idx'] or a['verb'] == b['verb']:
                continue
            sa, oa = mentions[a['subject']]['entity'], mentions[a['object']]['entity']
            sb, ob = mentions[b['subject']]['entity'], mentions[b['object']]['entity']
            if sa == sb and oa != ob and len(constraints) < cfg.n_constraints:
                c = {'kind': 'no_same_object', 'verb1': a['verb'], 'verb2': b['verb']}
                constraints.append(c)
                lines.append(f"({len(lines)+1}) No one both {a['verb']} and {b['verb']} the same person.")
                break
        if len(constraints) >= cfg.n_constraints:
            break

    same_entity = {}
    for m in mentions:
        if m['mode'] in (PRONOUN, DESC, DESC_EVENT):
            same_entity.setdefault(m['entity'], []).append(m)
    pairs = []
    for ms in same_entity.values():
        if len(ms) >= 2:
            pairs.extend((a, b) for a, b in zip(ms, ms[1:])
                         if a.get('ambiguous') or b.get('ambiguous'))
    random.shuffle(pairs)
    remaining_links = max(0, cfg.n_identity_links - len(identity_links))
    for a, b in pairs[:remaining_links]:
        constraints.append({'kind': 'identity', 'left': a['idx'], 'right': b['idx']})
        identity_links.append((a['idx'], b['idx']))
        lines.append(f"({len(lines)+1}) {_expr_ref(a).capitalize()} and {_expr_ref(b)} referred to the same person.")

    events = {m['event']['idx']: m['event'] for m in mentions if m.get('event')}.values()
    rule_choices = []
    for event in events:
        subj = mentions[event['subject']]['entity']
        obj = mentions[event['object']]['entity']
        rule = {'verb': event['verb'], 'subject_role': subj.role,
                'object_role': obj.role, 'polarity': True}
        if _assignment_ok({}, mentions, [], [rule]):
            rule_choices.append(rule)
    random.shuffle(rule_choices)
    for rule in rule_choices[:cfg.n_rules]:
        rules.append(rule)
        lines.append(
            f"({len(lines)+1}) In this story, {rule['subject_role']}s only "
            f"{rule['verb']} {rule['object_role']}s."
        )

    introduced = sorted({m['entity'] for m in mentions}, key=lambda e: e.eid)
    for e in random.sample(introduced, min(cfg.n_state_changes, len(introduced))):
        new_role = random.choice([r for r in ROLES if r != e.role])
        state_changes.append({'entity': e, 'role': new_role, 'sent': len(lines)})
        lines.append(f"({len(lines)+1}) After that, {e.name} became a {new_role}.")

    return {
        'constraints': constraints,
        'rules': rules,
        'identity_links': identity_links,
        'state_changes': state_changes,
    }


def _current_role(entity, challenge=None):
    role = entity.role
    for change in (challenge or {}).get('state_changes', []):
        if change['entity'] == entity:
            role = change['role']
    return role


def _mentions_before(q, mentions):
    return [m for m in mentions
            if (m['sent'], 0 if m['pos'] == 'subject' else 1) <
            (q['sent'], 0 if q['pos'] == 'subject' else 1)]


def _same_gender(q, mentions):
    return [m for m in _mentions_before(q, mentions)
            if m['entity'].gender == q['entity'].gender]


def h_nearest_same_gender_name(q, mentions):
    for m in reversed(_same_gender(q, mentions)):
        if m['mode'] in (INTRO, NAME):
            return m['entity']
    return None


def h_nearest_same_gender_mention(q, mentions):
    ms = _same_gender(q, mentions)
    return ms[-1]['entity'] if ms else None


def h_prev_sentence_unique_gender(q, mentions):
    ents = {m['entity'] for m in mentions
            if m['sent'] == q['sent'] - 1 and
            m['entity'].gender == q['entity'].gender}
    return next(iter(ents)) if len(ents) == 1 else None


def h_prev_sentence_unique_non_subject_gender(q, mentions):
    ents = {m['entity'] for m in mentions
            if m['sent'] == q['sent'] - 1 and m['pos'] != 'subject' and
            m['entity'].gender == q['entity'].gender}
    return next(iter(ents)) if len(ents) == 1 else None


def h_global_desc_lookup(q, mentions, pool):
    if q['mode'] != DESC:
        return None
    matches = global_matches_for_surface(q, pool)
    return matches[0] if len(matches) == 1 else None


def h_last_mentioned(q, mentions):
    ms = _mentions_before(q, mentions)
    return ms[-1]['entity'] if ms else None


def h_most_frequent(q, mentions):
    counts = {}
    for m in _mentions_before(q, mentions):
        counts[m['entity']] = counts.get(m['entity'], 0) + 1
    if not counts:
        return None
    top = max(counts.values())
    ents = [e for e, n in counts.items() if n == top]
    return ents[0] if len(ents) == 1 else None


def h_surface_salience_name(q, mentions):
    return _surface_salience_name_pred(q, mentions)


def h_one_step_antecedent_name(q, mentions):
    ant = q.get('antecedent')
    if ant is None:
        return None
    m = mentions[ant]
    return m['entity'] if m['mode'] in (INTRO, NAME) else None


def h_immediate_antecedent_oracle(q, mentions):
    ant = q.get('antecedent')
    return mentions[ant]['entity'] if ant is not None else None


def _constraint_lookup_pred(q, mentions, challenge):
    for c in challenge.get('constraints', []):
        if c['kind'] == 'event_role' and c['mention'] == q['idx']:
            domain = _local_candidate_entities(q, mentions, [], 999)
            matches = [e for e in domain if e.role == c['role']]
            return matches[0] if len(matches) == 1 else None
    return None


def h_constraint_lookup(q, mentions):
    return _constraint_lookup_pred(q, mentions, q.get('challenge') or {})


HEURISTICS = {
    'nearest_same_gender_name': lambda q, mentions, pool: h_nearest_same_gender_name(q, mentions),
    'nearest_same_gender_mention': lambda q, mentions, pool: h_nearest_same_gender_mention(q, mentions),
    'previous_sentence_unique_gender': lambda q, mentions, pool: h_prev_sentence_unique_gender(q, mentions),
    'prev_sentence_unique_non_subject_gender': lambda q, mentions, pool: h_prev_sentence_unique_non_subject_gender(q, mentions),
    'global_desc_lookup': h_global_desc_lookup,
    'last_mentioned': lambda q, mentions, pool: h_last_mentioned(q, mentions),
    'most_frequent': lambda q, mentions, pool: h_most_frequent(q, mentions),
    'surface_salience_name': lambda q, mentions, pool: h_surface_salience_name(q, mentions),
    'one_step_antecedent_name': lambda q, mentions, pool: h_one_step_antecedent_name(q, mentions),
    'immediate_antecedent_oracle': lambda q, mentions, pool: h_immediate_antecedent_oracle(q, mentions),
    'constraint_lookup': lambda q, mentions, pool: h_constraint_lookup(q, mentions),
}
BALANCE_HEURISTICS = set(HEURISTICS) - {'immediate_antecedent_oracle'}


def _as_raw_item(item):
    if isinstance(item, dict) and 'q' in item:
        return item
    return item.metadata


def _heuristic_rows(items):
    rows = {}
    for item in items:
        raw = _as_raw_item(item)
        q, mentions, pool = raw['q'], raw['mentions'], raw['pool']
        stratum = (q['mode'], _get_hops(q, mentions))
        for name, fn in HEURISTICS.items():
            pred = fn(q, mentions, pool)
            key = (name, stratum)
            n, covered, correct = rows.get(key, [0, 0, 0])
            n += 1
            if pred is not None:
                covered += 1
                correct += int(pred == q['entity'])
            rows[key] = [n, covered, correct]
    return rows


def shortcut_report(items):
    report = []
    for (name, stratum), (n, covered, correct) in sorted(_heuristic_rows(items).items()):
        report.append({
            'heuristic': name,
            'stratum': stratum,
            'n': n,
            'accuracy': (correct / covered) if covered else None,
            'coverage': covered / n if n else 0.0,
        })
    return report


def _shortcut_score(items, eps=0.08, min_n=20):
    score = 0.0
    bad = False
    for (name, _), (_, covered, correct) in _heuristic_rows(items).items():
        if name not in BALANCE_HEURISTICS:
            continue
        if covered < min_n:
            continue
        acc = correct / covered
        delta = abs(acc - 0.5)
        score += delta
        bad = bad or delta > eps
    return score, not bad


def shortcut_stats_ok(items, eps=0.08, min_n=20):
    return _shortcut_score(items, eps, min_n)[1]


def subsample_shortcut_balanced(candidates, n_final, eps=0.08, min_n=20):
    random.shuffle(candidates)
    selected = []
    for item in candidates:
        if len(selected) >= n_final:
            break
        trial = selected + [item]
        if shortcut_stats_ok(trial, eps=eps, min_n=min_n):
            selected.append(item)
    if len(selected) >= n_final:
        return selected

    selected = []
    cur_score = 0.0
    remaining = []
    for item in candidates:
        if len(selected) >= n_final:
            break
        trial = selected + [item]
        score, _ = _shortcut_score(trial, eps=eps, min_n=min_n)
        if not selected or score <= cur_score + eps:
            selected.append(item)
            cur_score = score
        else:
            remaining.append((score, item))
    if len(selected) < n_final:
        remaining.sort(key=lambda x: x[0])
        selected.extend(item for _, item in remaining[:n_final - len(selected)])
    if len(selected) < n_final:
        seen = {id(x) for x in selected}
        selected.extend(x for x in candidates if id(x) not in seen)
    return selected[:n_final]


def generate_balanced_batch(task, n_final, oversample=20, eps=0.08):
    candidates = [task.generate_raw_candidate()
                  for _ in range(n_final * oversample)]
    return subsample_shortcut_balanced(candidates, n_final, eps=eps,
                                       min_n=task.config.shortcut_min_n)


@dataclass
class CoreferenceConfig(Config):
    n_entities: int = 6
    chain_len: int = 4
    n_distractors: int = 4
    p_pronoun: float = 0.7
    p_desc: float = 0.5
    p_desc_event: float = 0.4
    p_shortcut: float = 0.05   # prob. of using a shorter chain for diversity
    target_hops: int = 3
    single_gender_pool: bool = True
    balanced_generation: bool = True
    oversample: int = 4
    balance_batch_size: int = 256
    shortcut_eps: float = 0.08
    shortcut_min_n: int = 20
    pronoun_window: int = 8
    p_compositional_query: float = 0.35
    n_ambiguous_mentions: int = 0
    n_constraints: int = 0
    n_rules: int = 0
    n_identity_links: int = 0
    n_state_changes: int = 0
    require_same_gender_distractor: bool = True
    require_opaque_link_for_multihop: bool = True
    p_group_filler: float = 0.0

    def apply_difficulty(self, level):
        self.n_entities += level
        self.chain_len += level
        self.n_distractors += level
        self.target_hops += level


class Coreference(Task):
    summary = "Resolve multi-hop entity coreference chains and pronouns in natural text."
    def __init__(self, config=CoreferenceConfig()):
        super().__init__(config=config)
        self._balanced_buffer = []

    def generate_raw_candidate(self):
        cfg = self.config
        if cfg.n_entities < 2:
            raise ValueError("Coreference requires at least 2 entities")
        for _ in range(1000):
            clen = cfg.chain_len
            if clen > 2 and random.random() < cfg.p_shortcut:
                clen = random.randint(2, clen - 1)
            pool = _pool(cfg.n_entities, cfg.single_gender_pool)
            plan = _plan(pool, clen, cfg.n_distractors)
            lines, mentions = _emit(plan, pool, cfg.p_pronoun, cfg.p_desc,
                                    cfg.p_desc_event,
                                    cfg.pronoun_window,
                                    cfg.n_ambiguous_mentions)
            challenge = _add_global_challenge(lines, mentions, pool, cfg)

            cands = _query_candidates(mentions, pool, target_hops=cfg.target_hops,
                                      cfg=cfg, challenge=challenge)
            if not cands:
                continue
            event_descs = [m for m in cands if m['mode'] == DESC_EVENT]
            prons = [m for m in cands if m['mode'] == PRONOUN]
            if event_descs and random.random() < 0.6:
                q = random.choice(event_descs)
            elif prons and random.random() < 0.7:
                q = random.choice(prons)
            else:
                q = random.choice(cands)
            q['challenge'] = challenge
            hops = _get_hops(q, mentions)
            return edict({
                'problem': self._build(q, lines, mentions, pool, hops, challenge),
                'q': q,
                'mentions': mentions,
                'pool': pool,
                'challenge': challenge,
                'hops': hops,
                'mode': q['mode'],
                'target_hops': cfg.target_hops,
            })
        raise RuntimeError("Could not generate a valid coreference problem")

    def generate_entry(self):
        cfg = self.config
        if not cfg.balanced_generation:
            return self.generate_raw_candidate()['problem']
        if not self._balanced_buffer:
            n = max(1, cfg.balance_batch_size)
            self._balanced_buffer = generate_balanced_batch(
                self, n, cfg.oversample, cfg.shortcut_eps)
        return self._balanced_buffer.pop()['problem']

    def _build(self, q, lines, mentions, pool, hops=None, challenge=None):
        target = q['entity']
        query_kind = 'role' if random.random() < self.config.p_compositional_query else 'name'
        answer = _current_role(target, challenge) if query_kind == 'role' else target.name
        sid = q['sent'] + 1
        if q['mode'] == PRONOUN:
            g = 'female' if target.gender == 'f' else 'male'
            ant = mentions[q['antecedent']]
            ant_sid = ant['sent'] + 1
            if q['pos'] == 'object':
                subj = next(m['entity'].name for m in mentions
                            if m['sent'] == q['sent']
                            and m['pos'] == 'subject')
                diagnostic_trace = (f"s{sid} pron '{q['surface']}' | "
                                    f"subject={subj}; salient s{ant_sid} "
                                    f"{ant['pos']} {g} -> {target.name}")
            else:
                diagnostic_trace = (f"s{sid} pron '{q['surface']}' | "
                                    f"salient s{ant_sid} {ant['pos']} "
                                    f"{g} -> {target.name}")
        elif q['mode'] == DESC:
            role, attrs = _surface_parts(q['surface'])
            matches = sorted(x.name for x in pool
                             if x.role == role
                             and all(a in x.attrs for a in attrs))
            filt = f"role={role}" + (f", attrs={list(attrs)}" if attrs else "")
            diagnostic_trace = (f"s{sid} desc '{q['surface']}' | {filt} | "
                                f"{{{', '.join(matches)}}} -> {target.name}")
        else:
            event = q['event_desc']
            arg_key = 'object' if event['target_pos'] == 'subject' else 'subject'
            arg = mentions[event[arg_key]]
            diagnostic_trace = (f"s{sid} event-desc '{q['surface']}' | "
                                f"{event['target_pos']} of {event['verb']} "
                                f"with {_display_ref(arg)} -> {target.name}")
        meta = edict({
            'sentences':    "\n".join(lines),
            'q_sentence':   sid,
            'q_position':   q['pos'],
            'q_expression': q['surface'],
            'query_kind':   query_kind,
            'q':            q,
            'mentions':     mentions,
            'pool':         pool,
            'challenge':    challenge or {},
            'target_hops':  self.config.target_hops,
            'hops':         hops,
            'diagnostic_trace': diagnostic_trace,
        })
        return Entry(metadata=meta, answer=answer)

    def render_prompt(self, metadata):
        if metadata.get('query_kind') == 'role':
            return (
                f"{metadata['sentences']}\n\n"
                f"In sentence {metadata['q_sentence']}, what role does the "
                f"person referred to by the {metadata['q_position']} expression "
                f"'{metadata['q_expression']}' have?\n"
                f"The answer is one role word."
            )
        return (
            f"{metadata['sentences']}\n\n"
            f"In sentence {metadata['q_sentence']}, what does the "
            f"{metadata['q_position']} expression "
            f"'{metadata['q_expression']}' refer to?\n"
            f"The answer is the person's name."
        )

    def score_answer(self, answer, entry):
        norm = lambda s: (str(s or '').strip().strip('.').strip("'\"").split() or [''])[-1].lower()
        return float(norm(answer) == norm(entry.answer))

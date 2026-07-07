import random
from dataclasses import dataclass
from reasoning_core.template import Task, Problem, Config, edict

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
INTRO, NAME, DESC, PRONOUN = 'intro', 'name', 'desc', 'pron'


@dataclass(frozen=True)
class _Entity:
    eid: int; name: str; gender: str; role: str; attrs: tuple


def _pool(n):
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
    desc = f"{' '.join(e.attrs)} {e.role}"
    det = "an" if desc[0].lower() in 'aeiou' else "a"
    return f"{det} {desc} named {e.name}"


def _desc(e, pool):
    """Minimal definite NP uniquely picking e out of pool, else None."""
    same = [x for x in pool if x.role == e.role]
    if len(same) == 1:
        return f"the {e.role}"
    for a in e.attrs:
        if sum(a in x.attrs for x in same) == 1:
            return f"the {a} {e.role}"
    if sum(set(e.attrs) <= set(x.attrs) for x in same) == 1:
        return f"the {' '.join(e.attrs)} {e.role}"
    return None


def _pron_ok(e, prev_ents, cur_subj, pos):
    if pos == 'object' and e == cur_subj:       # Principle B
        return False
    if e not in prev_ents:                      # must be in previous sentence
        return False
    ctx = prev_ents | ({cur_subj} if cur_subj else set())
    return not any(x.gender == e.gender and x != e for x in ctx)


def _plan(pool, chain_len, n_distractors):
    """Locally coherent discourse without a globally privileged target."""
    n = chain_len + n_distractors
    cur = tuple(random.sample(pool, 2))
    out = [cur]

    for i in range(1, n):
        if i < chain_len or random.random() < 0.45:
            keep = random.choice(cur)
            other = random.choice([e for e in pool if e != keep])
            cur = (keep, other) if random.random() < 0.5 else (other, keep)
        else:
            cur = tuple(random.sample(pool, 2))
        out.append(cur)

    return out


def _query_candidates(mentions, pool, target_hops=2):
    counts = {}
    for m in mentions:
        counts[m['entity']] = counts.get(m['entity'], 0) + 1

    top = max(counts.values())
    unique_top = list(counts.values()).count(top) == 1
    cands = []

    for m in mentions:
        if m['mode'] not in (PRONOUN, DESC):
            continue
        if unique_top and counts[m['entity']] == top:
            continue

        if m['mode'] == DESC:
            surf = m['surface'][4:] if m['surface'].startswith('the ') else m['surface']
            role = surf.split()[-1]
            if sum(x.role == role for x in pool) == 1:
                continue

        cands.append(m)

    if not cands:
        return []

    def get_hops(m):
        if m['mode'] in (INTRO, NAME):
            return 0
        prev = [p for p in mentions
                if p['sent'] < m['sent'] and p['entity'] == m['entity']]
        if not prev:
            return 0
        return 1 + get_hops(max(prev, key=lambda x: x['sent']))

    cands.sort(key=lambda m: abs(get_hops(m) - target_hops))
    best_dist = abs(get_hops(cands[0]) - target_hops)
    return [c for c in cands if abs(get_hops(c) - target_hops) == best_dist]


def _pick(e, pool, introduced, prev_ents, cur_subj, pos, p_pron, p_desc):
    if e not in introduced:
        return _indef(e), INTRO
    prefs = []
    if random.random() < p_pron: prefs.append(PRONOUN)
    if random.random() < p_desc: prefs.append(DESC)
    prefs.append(NAME)
    for m in prefs:
        if m == PRONOUN and _pron_ok(e, prev_ents, cur_subj, pos):
            return PRON[e.gender][0 if pos == 'subject' else 1], PRONOUN
        if m == DESC:
            d = _desc(e, pool)
            if d: return d, DESC
        if m == NAME:
            return e.name, NAME
    return e.name, NAME


def _emit(plan, pool, p_pron, p_desc):
    introduced, lines, mentions = set(), [], []
    for i, (s_e, o_e) in enumerate(plan):
        prev = {m['entity'] for m in mentions if m['sent'] == i - 1}
        v = random.choice(VERBS)
        s_ref, s_mode = _pick(s_e, pool, introduced, prev, None,
                              'subject', p_pron, p_desc)
        introduced.add(s_e)
        o_ref, o_mode = _pick(o_e, pool, introduced, prev, s_e,
                              'object', p_pron, p_desc)
        introduced.add(o_e)
        cap = lambda s: s[:1].upper() + s[1:]
        lines.append(f"({i+1}) {cap(s_ref)} {v} {o_ref}.")
        mentions.extend([
            {'sent': i, 'pos': 'subject', 'surface': s_ref, 'mode': s_mode, 'entity': s_e},
            {'sent': i, 'pos': 'object',  'surface': o_ref, 'mode': o_mode, 'entity': o_e},
        ])
    return lines, mentions


@dataclass
class CoreferenceConfig(Config):
    n_entities: int = 6
    chain_len: int = 3
    n_distractors: int = 4
    p_pronoun: float = 0.7
    p_desc: float = 0.5
    p_shortcut: float = 0.05   # prob. of using a shorter chain for diversity
    target_hops: int = 2

    def apply_difficulty(self, level):
        self.n_entities += level
        self.chain_len += level
        self.n_distractors += level
        self.target_hops += level


class Coreference(Task):
    def __init__(self, config=CoreferenceConfig()):
        super().__init__(config=config)

    def generate(self):
        cfg = self.config
        if cfg.n_entities < 2:
            raise ValueError("Coreference requires at least 2 entities")
        for _ in range(100):
            clen = cfg.chain_len
            if clen > 2 and random.random() < cfg.p_shortcut:
                clen = random.randint(2, clen - 1)
            pool = _pool(cfg.n_entities)
            plan = _plan(pool, clen, cfg.n_distractors)
            lines, mentions = _emit(plan, pool, cfg.p_pronoun, cfg.p_desc)

            cands = _query_candidates(mentions, pool, target_hops=cfg.target_hops)
            if not cands:
                continue
            prons = [m for m in cands if m['mode'] == PRONOUN]
            if prons and random.random() < 0.7:
                return self._build(random.choice(prons), lines, mentions, pool)
            return self._build(random.choice(cands), lines, mentions, pool)
        raise RuntimeError("Could not generate a valid coreference problem")

    def _build(self, q, lines, mentions, pool):
        target = q['entity']
        sid = q['sent'] + 1
        if q['mode'] == PRONOUN:
            prev_names = sorted(m['entity'].name for m in mentions
                                if m['sent'] == q['sent'] - 1)
            g = 'female' if target.gender == 'f' else 'male'
            if q['pos'] == 'object':
                subj = next(m['entity'].name for m in mentions
                            if m['sent'] == q['sent']
                            and m['pos'] == 'subject')
                cot = (f"s{sid} pron '{q['surface']}' | "
                       f"s{sid-1}: {{{', '.join(prev_names)}}}; "
                       f"subject={subj} | "
                       f"unique non-subject {g} → {target.name}")
            else:
                cot = (f"s{sid} pron '{q['surface']}' | "
                       f"s{sid-1}: {{{', '.join(prev_names)}}} | "
                       f"unique {g} → {target.name}")
        else:
            surf = q['surface'][4:] if q['surface'].startswith('the ') else q['surface']
            parts = surf.split()
            role, attrs = parts[-1], parts[:-1]
            matches = sorted(x.name for x in pool
                             if x.role == role
                             and all(a in x.attrs for a in attrs))
            filt = f"role={role}" + (f", attrs={list(attrs)}" if attrs else "")
            cot = (f"s{sid} desc '{q['surface']}' | {filt} | "
                   f"{{{', '.join(matches)}}} → {target.name}")
        meta = edict({
            'sentences':    "\n".join(lines),
            'q_sentence':   sid,
            'q_position':   q['pos'],
            'q_expression': q['surface'],
            'cot':          cot,
        })
        return Problem(metadata=meta, answer=target.name)

    def prompt(self, metadata):
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

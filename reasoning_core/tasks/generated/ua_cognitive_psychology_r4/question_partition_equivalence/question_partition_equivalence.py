import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'question_partition_equivalence (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_cognitive_psychology_r4/question_partition_equivalence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Enumerate all worlds explicitly as small integers and compute partitions "
                 "by evaluating each question against each world; the answer is a canonical "
                 "list of partition blocks, and equivalence is determined by set equality.")


@dataclass
class QuestionPartitionEquivalenceV2Config(Config):
    n_worlds: int = 4
    max_val: int = 8
    max_depth: int = 1
    max_alts: int = 2

    def apply_difficulty(self, level):
        self.n_worlds = 4 + level
        self.max_val = 8 + 4 * level
        self.max_depth = 1 + level // 2
        self.max_alts = 2 + level // 3


_ATOMS = {
    'eq': lambda p, v: v == p[0],
    'gt': lambda p, v: v > p[0],
    'ge': lambda p, v: v >= p[0],
    'lt': lambda p, v: v < p[0],
    'le': lambda p, v: v <= p[0],
    'even': lambda p, v: v % 2 == 0,
    'odd': lambda p, v: v % 2 == 1,
    'mod': lambda p, v: v % p[0] == p[1],
    'range': lambda p, v: p[0] <= v <= p[1],
}

_ATOM_TEXT = {
    'eq': lambda p: f"equal to {p[0]}",
    'gt': lambda p: f"greater than {p[0]}",
    'ge': lambda p: f"at least {p[0]}",
    'lt': lambda p: f"less than {p[0]}",
    'le': lambda p: f"at most {p[0]}",
    'even': lambda p: "even",
    'odd': lambda p: "odd",
    'mod': lambda p: f"congruent to {p[1]} modulo {p[0]}",
    'range': lambda p: f"between {p[0]} and {p[1]} inclusive",
}


def _eval(e, v):
    tag = e[0]
    if tag == 'atom':
        kind, params = e[1], e[2]
        return _ATOMS[kind](params, v)
    if tag == 'not':
        return not _eval(e[1], v)
    if tag == 'and':
        return _eval(e[1], v) and _eval(e[2], v)
    if tag == 'or':
        return _eval(e[1], v) or _eval(e[2], v)
    raise ValueError(tag)


def _render(e):
    tag = e[0]
    if tag == 'atom':
        kind, params = e[1], e[2]
        return _ATOM_TEXT[kind](params)
    if tag == 'not':
        return f"not ({_render(e[1])})"
    if tag == 'and':
        return f"({_render(e[1])} and {_render(e[2])})"
    if tag == 'or':
        return f"({_render(e[1])} or {_render(e[2])})"
    raise ValueError(tag)


def _rand_atom(max_val):
    kind = random.choice(['eq', 'gt', 'ge', 'lt', 'le', 'even', 'odd', 'mod', 'range'])
    if kind == 'eq':
        return ('atom', 'eq', (random.randint(0, max_val),))
    if kind == 'gt':
        return ('atom', 'gt', (random.randint(0, max_val),))
    if kind == 'ge':
        return ('atom', 'ge', (random.randint(0, max_val),))
    if kind == 'lt':
        return ('atom', 'lt', (random.randint(1, max_val + 1),))
    if kind == 'le':
        return ('atom', 'le', (random.randint(0, max_val - 1),))
    if kind in ('even', 'odd'):
        return ('atom', kind, ())
    if kind == 'mod':
        d = random.randint(2, max(max_val, 3))
        return ('atom', 'mod', (d, random.randint(0, d - 1)))
    a = random.randint(0, max_val - 1)
    b = random.randint(a, max_val)
    return ('atom', 'range', (a, b))


def _rand_pred(depth, max_val):
    if depth <= 0:
        return _rand_atom(max_val)
    op = random.choice(['not', 'and', 'or', 'atom'])
    if op == 'atom':
        return _rand_atom(max_val)
    if op == 'not':
        return ('not', _rand_pred(depth - 1, max_val))
    return (op, _rand_pred(depth - 1, max_val), _rand_pred(depth - 1, max_val))


def _nonconstant_pred(max_val, depth):
    for _ in range(100):
        p = _rand_pred(depth, max_val)
        vals = {_eval(p, v) for v in range(max_val + 1)}
        if len(vals) == 2:
            return p
    raise RuntimeError("could not build a non-constant predicate")


def _inner_nodes(e):
    if not isinstance(e, tuple) or not e:
        return []
    if e[0] == 'atom':
        return []
    res = [e]
    for c in e[1:]:
        if isinstance(c, tuple):
            res.extend(_inner_nodes(c))
    return res


def _replace(e, target, newt):
    if e is target:
        return newt
    if isinstance(e, tuple) and e[0] in ('not', 'and', 'or'):
        if e[0] == 'not':
            sub = _replace(e[1], target, newt)
            return (e[0], sub)
        return (e[0], _replace(e[1], target, newt), _replace(e[2], target, newt))
    return e


def _local_equiv(t):
    cands = [('not', ('not', t))]
    if t[0] == 'and':
        cands.append(('not', ('or', ('not', t[1]), ('not', t[2]))))
    elif t[0] == 'or':
        cands.append(('not', ('and', ('not', t[1]), ('not', t[2]))))
    elif t[0] == 'not' and t[1][0] == 'and':
        cands.append(('or', ('not', t[1][1]), ('not', t[1][2])))
    elif t[0] == 'not' and t[1][0] == 'or':
        cands.append(('and', ('not', t[1][1]), ('not', t[1][2])))
    return random.choice(cands)


def _rewrite(pred):
    nodes = _inner_nodes(pred)
    target = random.choice(nodes) if nodes else pred
    newt = _local_equiv(target)
    return _replace(pred, target, newt)


def _alt_label(alts, w):
    for i, a in enumerate(alts):
        if w in a:
            return i
    return None


def _rand_alts(worlds, max_alts):
    hi = min(len(worlds), max_alts)
    k = random.randint(2, hi) if hi >= 2 else 1
    n_pick = random.randint(k, len(worlds))
    chosen = random.sample(worlds, n_pick)
    random.shuffle(chosen)
    cuts = sorted(random.sample(range(1, n_pick), k - 1)) if k > 1 else []
    groups = []
    prev = 0
    for cut in cuts + [n_pick]:
        groups.append(tuple(sorted(chosen[prev:cut])))
        prev = cut
    return groups


def _partition(q, worlds):
    if q['type'] == 'polar':
        f = lambda w: _eval(q['pred'], w)
    elif q['type'] == 'alt':
        f = lambda w: _alt_label(q['alts'], w)
    else:
        f = lambda w: ('v', w)
    blocks = {}
    for w in worlds:
        blocks.setdefault(f(w), []).append(w)
    return frozenset(frozenset(b) for b in blocks.values())


def _render_q(q):
    if q['type'] == 'polar':
        return f"Is the world {_render(q['pred'])}?"
    if q['type'] == 'alt':
        groups = ', '.join('{' + ', '.join(map(str, a)) + '}' for a in q['alts'])
        return (f"Which one of the following groups is the world in: {groups}? "
                f"(If it is in none, the answer is 'none of the above'.)")
    return "What number is the world? (Give its exact value.)"


def _rand_question(worlds, max_val, max_depth, max_alts, allow_kinds):
    kind = random.choice(allow_kinds)
    if kind == 'polar':
        return {'type': 'polar', 'pred': _nonconstant_pred(max_val, max_depth)}
    if kind == 'alt':
        return {'type': 'alt', 'alts': _rand_alts(worlds, max_alts)}
    return {'type': 'const'}


class QuestionPartitionEquivalence(Task):
    summary = ("Polar, alternative and constituent questions over finite possible worlds, "
               "including coordinated and restricted questions; compute their induced answer "
               "partitions and decide whether they ask the same thing.")
    config_cls = QuestionPartitionEquivalenceV2Config
    task_version = 2
    balancing_key_ratio = 1.0

    def generate_entry(self):
        c = self.config
        worlds = sorted(random.sample(range(0, c.max_val + 1), c.n_worlds))
        label = random.choice(['yes', 'no'])
        kinds = ['polar', 'polar', 'polar', 'alt', 'const']

        q1 = _rand_question(worlds, c.max_val, c.max_depth, c.max_alts, kinds)
        p1 = _partition(q1, worlds)

        if label == 'yes':
            if q1['type'] == 'polar':
                pred2 = _rewrite(q1['pred'])
                q2 = {'type': 'polar', 'pred': pred2}
                for _ in range(50):
                    if _partition(q2, worlds) == p1:
                        break
                    pred2 = _rewrite(q1['pred'])
                    q2 = {'type': 'polar', 'pred': pred2}
            elif q1['type'] == 'alt':
                alts2 = list(q1['alts'])
                random.shuffle(alts2)
                if alts2 == list(q1['alts']) and len(alts2) >= 2:
                    alts2 = list(reversed(alts2))
                q2 = {'type': 'alt', 'alts': alts2}
            else:
                q2 = {'type': 'alt', 'alts': [tuple([w]) for w in worlds]}
            # safety: both must induce the same partition for "yes"
            for _ in range(100):
                if _partition(q2, worlds) == p1:
                    break
                if q1['type'] == 'polar':
                    q2 = {'type': 'polar', 'pred': _rewrite(q1['pred'])}
                else:
                    break
        else:
            for _ in range(200):
                q2 = _rand_question(worlds, c.max_val, c.max_depth, c.max_alts, kinds)
                if _partition(q2, worlds) != p1:
                    break
            else:
                raise RuntimeError("could not build a non-equivalent second question")

        p2 = _partition(q2, worlds)
        assert (label == 'yes') == (p1 == p2), "constructed label inconsistent with partitions"

        text1 = _render_q(q1)
        text2 = _render_q(q2)
        payload = {
            'worlds': worlds,
            'q1': text1,
            'q2': text2,
        }
        metadata = {
            'payload': payload,
            'worlds': worlds,
            'q1_spec': q1,
            'q2_spec': q2,
            'label': label,
        }
        return Entry(metadata=metadata, answer=label)

    def render_prompt(self, metadata):
        worlds = ', '.join(map(str, metadata['payload']['worlds']))
        return (
            f"There are {len(metadata['payload']['worlds'])} possible worlds, numbered: "
            f"{worlds}.\n\n"
            f"Question one: {metadata['payload']['q1']}\n\n"
            f"Question two: {metadata['payload']['q2']}\n\n"
            f"Do these two questions induce the same partition of the possible worlds -- "
            f"that is, do they ask the same thing? Answer exactly \"yes\" or \"no\"."
        )

    def score_answer(self, answer, entry):
        ref = entry['answer']
        ans = str(answer).strip().lower()
        if ans in ('yes', 'no'):
            return 1.0 if ans == ref else 0.0
        return 0.0

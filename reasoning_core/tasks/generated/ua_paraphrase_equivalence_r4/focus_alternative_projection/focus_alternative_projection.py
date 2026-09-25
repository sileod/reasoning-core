import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'focus_alternative_projection (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_paraphrase_equivalence_r4/focus_alternative_projection',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 368817805,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _full(domain):
    return frozenset(range(domain))


def _eval(node, domain):
    k = node['k']
    if k == 'const':
        return frozenset([node['v']])
    if k in ('focus', 'up'):
        return _full(domain)
    if k in ('comp', 'pred'):
        c = _eval(node['c'], domain)
        if k == 'comp':
            return _full(domain) - c
        return c & frozenset(node['ext'])
    l = _eval(node['l'], domain)
    r = _eval(node['r'], domain)
    if k == 'conj':
        return l & r
    return l | r


def _count_down(node):
    if node['k'] in ('const', 'focus'):
        return 1
    if node['k'] in ('up', 'comp', 'pred'):
        return 1 + _count_down(node['c'])
    return 1 + _count_down(node['l']) + _count_down(node['r'])


def _count_focus(node):
    if node['k'] == 'focus':
        return 1
    if node['k'] == 'const':
        return 0
    if node['k'] in ('up', 'comp', 'pred'):
        return _count_focus(node['c'])
    return _count_focus(node['l']) + _count_focus(node['r'])


def _count_pred(node):
    if node['k'] == 'pred':
        return 1 + _count_pred(node['c'])
    if node['k'] in ('up', 'comp'):
        return _count_pred(node['c'])
    if node['k'] in ('conj', 'disj'):
        return _count_pred(node['l']) + _count_pred(node['r'])
    return 0


def _is_leaf(k):
    return k in ('const', 'focus')


def _build(domain, depth, focus_prob):
    kinds = ['pred', 'comp', 'conj', 'disj', 'up']
    weights = [0.34, 0.18, 0.20, 0.16, 0.12]
    limit = 60
    for _ in range(limit):
        node = _node(domain, depth, kinds, weights, focus_prob)
        if _count_focus(node) < 1 or _count_down(node) > 26:
            continue
        res = _eval(node, domain)
        if res and len(res) < domain:
            return node, res
    node = _node(domain, depth, kinds, weights, focus_prob)
    return node, _eval(node, domain)


def _node(domain, depth, kinds, weights, focus_prob):
    if depth <= 0 or random.random() < 0.30:
        if random.random() < focus_prob:
            return {'k': 'focus', 'v': random.randrange(domain)}
        return {'k': 'const', 'v': random.randrange(domain)}
    kind = random.choices(kinds, weights=weights)[0]
    if kind == 'pred':
        ext = sorted(random.sample(range(domain),
                     random.choice([1, 1, 2, 2, 2, 3, 3])))
        return {'k': 'pred', 'ext': ext,
                'c': _node(domain, depth - 1, kinds, weights, focus_prob)}
    if kind == 'comp':
        return {'k': 'comp',
                'c': _node(domain, depth - 1, kinds, weights, focus_prob)}
    if kind == 'up':
        return {'k': 'up',
                'c': _node(domain, depth - 1, kinds, weights, focus_prob)}
    if kind == 'conj':
        return {'k': 'conj',
                'l': _node(domain, depth - 1, kinds, weights, focus_prob),
                'r': _node(domain, depth - 1, kinds, weights, focus_prob)}
    return {'k': 'disj',
            'l': _node(domain, depth - 1, kinds, weights, focus_prob),
            'r': _node(domain, depth - 1, kinds, weights, focus_prob)}


def _format_set(s, domain):
    if not s:
        return 'empty'
    return '{%s}' % ','.join(str(x) for x in sorted(s))


@dataclass
class FAPConfig(Config):
    domain: int = 5
    depth: int = 2
    focus_prob: float = 0.4

    def apply_difficulty(self, level):
        self.domain = 5 + (level >= 4)
        self.depth = 2 + level // 3
        self.focus_prob = 0.45


class FocusAlternativeProjection(Task):
    summary = ("Compute alternative denotations (subsets of a finite domain) induced by "
               "focused constituents, composed through predicates, complement/union/"
               "intersection modifiers, binary conjunction, and nested focus operators; "
               "return the resulting alternative set.")
    design_choice = ("A small explicit alternative-semantics model: unfocused constants "
                     "denote singletons, focused constants project the whole domain, and "
                     "predicates restrict, complement inverts, conjuncts intersect, "
                     "disjuncts union, and the focus operator widens to the full domain. "
                     "The solver outputs the resulting subset.")
    config_cls = FAPConfig

    def generate_entry(self):
        dom = self.config.domain
        node, result = _build(dom, self.config.depth, self.config.focus_prob)
        result = sorted(result)
        answer = _format_set(result, dom)
        return Entry(metadata={
            'domain': dom,
            'tree': node,
            'answer': answer,
        }, answer=answer)

    def render_prompt(self, metadata):
        dom = metadata['domain']
        lines = []
        lines.append("We work in a tiny alternative-semantics model over the domain of "
                     "individuals D = {%s}." % ','.join(str(i) for i in range(dom)))
        lines.append("Every expression denotes a set of individuals (its alternatives). "
                     "The composition rules are:")
        lines.append("  - an unfocused constant n denotes the singleton {n};")
        lines.append("  - a focused constant n* denotes the whole domain D;")
        lines.append("  - a predicate P with extension E restricts: P(X) = X INTERSECT E;")
        lines.append("  - the complement modifier ~ inverts: ~(X) = D minus X;")
        lines.append("  - conjunction joins requirements: A AND B = A INTERSECT B;")
        lines.append("  - disjunction collects options: A OR B = A UNION B;")
        lines.append("  - the focus operator UP widens any option set to the whole D.")
        lines.append("")
        lines.append("Displayed expression:")
        lines.append(_render(node := metadata['tree'], dom))
        lines.append("")
        lines.append("Give the resulting alternative set, written as {a,b,c} in ascending "
                     "order, or the bare word 'empty' if the resulting set is empty.")
        return "\n".join(lines)


def _render(node, dom):
    k = node['k']
    if k == 'const':
        return str(node['v'])
    if k == 'focus':
        return '%d*' % node['v']
    if k == 'up':
        return 'UP(%s)' % _render(node['c'], dom)
    if k == 'comp':
        return '~(%s)' % _render(node['c'], dom)
    if k == 'pred':
        return 'P{%s}(%s)' % (','.join(str(x) for x in node['ext']),
                              _render(node['c'], dom))
    if k == 'conj':
        return '(%s AND %s)' % (_render(node['l'], dom), _render(node['r'], dom))
    return '(%s OR %s)' % (_render(node['l'], dom), _render(node['r'], dom))


def score_answer(answer, entry):
    got = answer.strip() if isinstance(answer, str) else ''
    return 1.0 if got == entry.answer else 0.0

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'monotonicity_context_signatures (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scope_and_binding_r4/monotonicity_context_signatures',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


_UP_Q = ('every', 'all', 'each', 'at least two')
_DOWN_Q = ('no', 'few', 'not every')
_POL_WORD = {'+': 'upward', '-': 'downward', '0': 'nonmonotone'}
_OP_ROLES = {
    'Q_up': "its restrictor is the upward-monotone quantifier 'Q'",
    'Q_down': "its restrictor is the downward-monotone quantifier 'Q'",
    'NEG': 'negation, "not"',
    'AND': 'conjunction, "and"',
}
_OP_WEIGHTS = [('Q_up', 0.32), ('Q_down', 0.32), ('NEG', 0.26), ('AND', 0.10)]


def _flip(s):
    if s == '+':
        return '-'
    if s == '-':
        return '+'
    return '0'


def _apply_op(op, s):
    if s == '0':
        return '0'
    if op in ('Q_up', 'NONE'):
        return s
    if op in ('Q_down', 'NEG'):
        return _flip(s)
    if op == 'AND':
        return '0'
    return s


def _context_above(tree, marked):
    s = '+'
    for i in range(len(tree) - 1, marked, -1):
        s = _apply_op(tree[i]['op'], s)
    return s


def _compose(leaf, ctx):
    if leaf == '0' or ctx == '0':
        return '0'
    return '+' if leaf == ctx else '-'


def _build(leaves, op_prob, marked):
    choices = [op for op, _ in _OP_WEIGHTS]
    weights = [w for _, w in _OP_WEIGHTS]
    tree = []
    for i in range(leaves):
        pol_s = random.choice(['+', '-'])
        if random.random() < op_prob:
            op = random.choices(choices, weights=weights)[0]
            if op == 'Q_up':
                lex = random.choice(_UP_Q)
            elif op == 'Q_down':
                lex = random.choice(_DOWN_Q)
            else:
                lex = None
            node = {'id': i, 'pol': pol_s, 'op': op, 'lex': lex}
        else:
            node = {'id': i, 'pol': pol_s, 'op': 'NONE', 'lex': None}
        tree.append(node)
    ctx = _context_above(tree, marked)
    leaf_pol = tree[marked]['pol']
    answer = _compose(leaf_pol, ctx)
    return tree, answer


@dataclass
class MCSConfig(Config):
    leaves: int = 2
    op_prob: float = 0.5

    def apply_difficulty(self, level):
        self.leaves = int(2 + 1.2 * level)
        self.op_prob = 0.5 + 0.07 * level


class MonotonicityContextSignatures(Task):
    summary = ("Propagate upward, downward and nonmonotone entailment signatures "
               "through quantified restrictors, nuclear scopes, negation and "
               "conjunction; return the polarity sign at a marked constituent.")
    design_choice = ("Provide a mini-proof tree of logical forms with quantifier and "
                     "connective structure; the solver must output the polarity sign "
                     "('+', '-', '0') for the marked leaf after propagating through all "
                     "operators.")
    config_cls = MCSConfig

    def generate_entry(self):
        leaves = self.config.leaves
        marked = random.randrange(leaves)
        tree, answer = _build(leaves, self.config.op_prob, marked)
        return Entry(metadata={
            'tree': tree,
            'marked': marked,
            'answer': answer,
        }, answer=answer)

    def render_prompt(self, metadata):
        tree = metadata['tree']
        lines = []
        lines.append("Displayed below is a fragment of a logical-form tree, written as "
                     "leaves indexed left to right from 0.")
        lines.append("Nesting: when both leaf[i] and leaf[i+1] exist, leaf[i] lies inside "
                     "the scope (restrictor/nuclear scope) of the operator at leaf[i+1]; "
                     "the outermost operator is at the highest index.")
        lines.append("Every leaf also carries its own polarity sign: + means upward "
                     "monotone, - means downward monotone, 0 means nonmonotone.")
        lines.append("The polarity context at the marked leaf (*) is computed by "
                     "threading the outermost operator inward, starting from a positive "
                     "position, and applying, in order:")
        lines.append("  - restrictor of an upward-monotone quantifier (every/all/each/"
                     "at least two): context unchanged;")
        lines.append("  - restrictor of a downward-monotone quantifier (no/few/not "
                     "every): context sign reversed;")
        lines.append("  - negation 'not': context sign reversed;")
        lines.append("  - conjunction 'and': context becomes nonmonotone 0.")
        lines.append("The sign at the marked constituent is its own polarity multiplied "
                     "onto that context: equal signs give +, opposite signs give -, and "
                     "a 0 anywhere gives 0.")
        lines.append("")
        for node in tree:
            marker = '  <-- marked (*)' if node['id'] == metadata['marked'] else ''
            spec = _OP_ROLES[node['op']] if node['op'] != 'NONE' else 'no operator'
            if node['lex'] is not None:
                spec = spec.replace("'Q'", "'%s'" % node['lex'])
            lines.append("leaf[%d]: %s; inherent polarity %s%s"
                         % (node['id'], spec, _POL_WORD[node['pol']], marker))
        lines.append("")
        lines.append("State just the sign of the marked constituent.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        got = answer.strip() if isinstance(answer, str) else ''
        return 1.0 if got == entry.answer else 0.0

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

RESOURCE_NAMES = ['cpu', 'mem', 'io', 'net', 'gpu', 'disk', 'tpu']

design_choice = "Answer as a canonical list of resource identifiers whose usage violates the stated discipline, with each identifier as a bracketed token."

TASK_META = {'parent_source_id': None,
 'idea': 'branch_sensitive_resource_audit (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_relational_structures_r4/branch_sensitive_resource_audit',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class BranchAuditConfig(Config):
    n_resources: int = 4
    depth: int = 2
    amount_max: int = 8
    aff_base: int = 4
    cap_slack: int = 6

    def apply_difficulty(self, level):
        self.n_resources = min(3 + level, len(RESOURCE_NAMES))
        self.depth = min(1 + level, 4)
        self.amount_max = 6 + 2 * level
        self.aff_base = 3 + level
        self.cap_slack = 4 + 2 * level


def _stmt_use(stmt, n):
    _, res, form = stmt
    if form[0] == 'const':
        return res, form[1]
    return res, form[1] * n + form[2]


def _eval_node(node, n, resources):
    kind, kids = node
    child_ds = []
    for k in kids:
        if k[0] == 'stmt':
            res, val = _stmt_use(k, n)
            dd = {r: 0 for r in resources}
            dd[res] = val
            child_ds.append(dd)
        else:
            child_ds.append(_eval_node(k, n, resources))
    if kind == 'choice':
        return {r: max(d[r] for d in child_ds) for r in resources}
    out = {r: 0 for r in resources}
    for d in child_ds:
        for r in resources:
            out[r] += d[r]
    return out


def _gen_stmt(resources, cfg, n):
    res = random.choice(resources)
    if random.random() < 0.5:
        return ('stmt', res, ('const', random.randint(1, cfg.amount_max)))
    return ('stmt', res, ('affine', random.randint(1, 3),
                          random.randint(0, cfg.aff_base)))


def _gen_node(resources, cfg, depth, n):
    if depth <= 0 or random.random() < 0.5:
        k = random.randint(1, 3)
        return ('seq', [_gen_stmt(resources, cfg, n) for _ in range(k)])
    kind = random.choice(('seq', 'par', 'choice'))
    nchild = random.randint(2, 3)
    kids = [_gen_node(resources, cfg, depth - 1, n) for _ in range(nchild)]
    return (kind, kids)


def _expr_str(form):
    t = form[0]
    if t == 'const':
        return str(form[1])
    a, b = form[1], form[2]
    if a == 1 and b == 0:
        return "n"
    if b == 0:
        return "%d*n" % a
    return "%d*n+%d" % (a, b)


def _render_lines(node, indent=0):
    pad = "  " * indent
    kind, kids = node
    if kind == 'seq':
        lines = [pad + "seq:"]
    elif kind == 'par':
        lines = [pad + "par:"]
    else:
        lines = [pad + "either/or:"]
    for k in kids:
        if k[0] == 'stmt':
            _, res, form = k
            lines.append(pad + "  uses " + res + " " + _expr_str(form))
        else:
            lines.extend(_render_lines(k, indent + 1))
    return lines


def _norm_answer(s):
    s = s.strip().lower()
    if not s:
        return None
    if s in ('none', '[]', '()'):
        return ()
    toks = []
    for w in s.replace('[', ' ').replace(']', ' ').split():
        w = w.strip()
        if w:
            toks.append(w)
    return tuple(sorted(set(toks)))


def _score(answer, entry):
    gold = tuple(sorted(entry.metadata['violators']))
    parsed = _norm_answer(answer)
    if parsed is None:
        return 0.0
    return 1.0 if parsed == gold else 0.0


class BranchSensitiveResourceAudit(Task):
    summary = ("Audit resource use in nested sequential, exclusive-choice (max), and "
               "parallel (additive) blocks; vary linear and affine obligations plus local "
               "creation and transfer; identify resources whose usage violates the stated "
               "discipline.")
    config_cls = BranchAuditConfig
    task_version = 1

    def generate_entry(self):
        cfg = self.config
        resources = random.sample(RESOURCE_NAMES, cfg.n_resources)
        n = random.randint(2, 4)
        node = _gen_node(resources, cfg, cfg.depth, n)
        usage = _eval_node(node, n, resources)
        capacities = {}
        violators = []
        for r in resources:
            u = usage[r]
            if u > 0 and random.random() < 0.5:
                cap = random.randint(0, u - 1)
            else:
                cap = random.randint(u, u + cfg.cap_slack)
            capacities[r] = int(cap)
            if u > cap:
                violators.append(r)
        violators.sort()
        assert usage == _eval_node(node, n, resources)
        answer = ' '.join('[' + r + ']' for r in violators) if violators else 'none'
        metadata = {
            'resources': resources,
            'n': int(n),
            'capacities': {r: int(capacities[r]) for r in resources},
            'usage': {r: int(usage[r]) for r in resources},
            'violators': violators,
            'tree': node,
            'answer': answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        cap_parts = ", ".join("%s=%d" % (r, metadata['capacities'][r])
                              for r in metadata['resources'])
        body = "\n".join(_render_lines(metadata['tree']))
        return (
            "A resource-audit problem. A program is a tree of blocks. In a 'seq' "
            "(sequential) block every child runs and uses of a resource add across "
            "children. In a 'par' (parallel) block every branch runs concurrently so uses "
            "of a resource also add across branches. In an 'either/or' (choice) block only "
            "one branch runs, so a resource's use is the maximum across the branches. Each "
            "statement 'uses <res> <expr>' obligates that resource by <expr>; an expression "
            "A*n+B is evaluated at the given value of n (plain numbers are constants). A "
            "resource violates the discipline if its total use across the whole program "
            "exceeds its capacity.\n\n"
            "Variable n = %d.\n"
            "Capacities: %s.\n\n"
            "Program:\n%s\n\n"
            "List every resource whose use exceeds its capacity, in lexicographic (alphabetical) "
            "order, each as a bracketed token separated by spaces, e.g. [cpu] [mem]. "
            "If no resource violates, answer: none." % (metadata['n'], cap_parts, body)
        )

    def score_answer(self, answer, entry):
        return _score(answer, entry)

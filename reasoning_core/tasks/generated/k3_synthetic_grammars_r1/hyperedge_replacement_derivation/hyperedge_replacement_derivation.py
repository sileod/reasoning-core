"""Hyperedge-replacement derivation: apply productions to nonterminal edges.

Each instance defines a small hyperedge-replacement grammar with one nonterminal
``A`` of fixed arity. The start graph is a set of terminal context edges plus
several nonterminal edges, each addressed by its tentacle attachment vertices.
Replacing a nonterminal edge glues the chosen production onto those attachment
points: boundary ``b_k`` maps to attachment ``k`` and internal nodes ``i_j``
become consecutively numbered fresh vertices. The final graph is the context
edges plus every edge introduced by all replacements; the answer is the sorted
list of final edges (source, target, label).
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TERMINALS = ('x', 'y', 'z')

TASK_META = {'parent_source_id': None,
 'idea': 'hyperedge_replacement_derivation (draw 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_synthetic_grammars_r1/hyperedge_replacement_derivation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class HyERConfig(Config):
    num_nt: int = 1
    arity: int = 2
    ctx_edges: int = 2
    max_prods: int = 1
    prod_i_nodes: int = 1
    prod_edges: int = 2

    def apply_difficulty(self, level):
        self.num_nt = 1 + level
        self.ctx_edges = 2 + level
        self.arity = 2 + (1 if level >= 3 else 0)
        self.max_prods = 2 if level >= 2 else 1
        self.prod_i_nodes = 2 if level >= 2 else 1
        self.prod_edges = 2 + (level // 2)


def _build_context(cfg, nv):
    """Context terminal edges over vertices 1..nv. Returns list of (s,t,L)."""
    edges = []
    for _ in range(cfg.ctx_edges):
        s = random.randint(1, nv)
        t = random.randint(1, nv)
        while t == s:
            t = random.randint(1, nv)
        label = random.choice(TERMINALS)
        edges.append((s, t, label))
    return edges


def _build_nt_edges(cfg, nv):
    """Nonterminal edges as ('A', (attach...)) with attachment vertices drawn,
    with replacement/sharing, from 1..nv so different edges glue together."""
    edges = []
    for _ in range(cfg.num_nt):
        attach = tuple(random.sample(range(1, nv + 1), cfg.arity))
        edges.append(('A', attach))
    return edges


def _build_productions(cfg):
    """One or more productions for nonterminal A, each usable at any arity."""
    prods = []
    for _ in range(random.randint(1, cfg.max_prods)):
        ar = cfg.arity
        b_tokens = ['b%d' % k for k in range(ar)]
        n_internal = random.randint(0, cfg.prod_i_nodes)
        i_tokens = ['i%d' % k for k in range(n_internal)]
        nodes = b_tokens + i_tokens
        edges = []
        for it in i_tokens:
            edges.append((random.choice(b_tokens), it, random.choice(TERMINALS)))
        for _ in range(cfg.prod_edges):
            edges.append((random.choice(nodes), random.choice(nodes),
                          random.choice(TERMINALS)))
        prods.append((b_tokens, i_tokens, edges))
    return prods


def _derive(cfg, ctx, nt_edges, prods, nv):
    """Apply every nonterminal edge in order, mapping attachments and fresh ids.

    Returns the full final edge list (context + all introduced edges).
    """
    result = [list(e) for e in ctx]
    fresh = nv + 1
    for _label, attach in nt_edges:
        b_tokens, i_tokens, pedges = random.choice(prods)
        mapping = {}
        for k, b in enumerate(b_tokens):
            mapping[b] = attach[k]
        for it in i_tokens:
            mapping[it] = fresh
            fresh += 1
        for (u, v, l) in pedges:
            result.append([mapping[u], mapping[v], l])
    return result


def _canonical_str(edges):
    ordered = sorted((int(s), int(t), str(l)) for s, t, l in edges)
    return ';'.join('(%d,%d,%s)' % (s, t, l) for s, t, l in ordered)


def _parse_edges(text):
    parsed = []
    for chunk in str(text).split(';'):
        chunk = chunk.strip().strip('(').strip(')').strip()
        if not chunk:
            continue
        parts = [p.strip() for p in chunk.split(',')]
        parsed.append((int(parts[0]), int(parts[1]), parts[2]))
    return sorted(parsed)


class HyperedgeReplacementDerivation(Task):
    summary = ("Execute a hyperedge-replacement derivation: replace each addressed "
               "nonterminal edge with its production's graph, gluing tentacles at "
               "attachment points; answer the final edge list, degree sequence, or "
               "port count.")
    design_choice = ("Choose answer as the sorted list of final edges "
                     "(source,target,label) with labels from a fixed alphabet, so "
                     "solvers must track identity across replacements.")
    config_cls = HyERConfig
    task_version = 2

    def _render_production(self, b_tokens, i_tokens, edges):
        internal = ('[' + ', '.join(i_tokens) + ']') if i_tokens else '[]'
        body = '; '.join('(%s, %s, %s)' % (u, v, l) for u, v, l in edges)
        return 'boundary [%s], internal %s, edges: %s' % (
            ', '.join(b_tokens), internal, body)

    def render_prompt(self, metadata):
        ar = metadata['arity']
        nv = metadata['nv']
        a_body = ', '.join('a%d' % k for k in range(ar))
        b_body = ', '.join('b%d' % k for k in range(ar))
        ctx_body = '; '.join('(%d, %d, %s)' % (s, t, l)
                             for s, t, l in metadata['ctx'])
        prod_lines = '\n'.join(
            'P%d: %s' % (i + 1, self._render_production(*p))
            for i, p in enumerate(metadata['productions']))
        nt_lines = '\n'.join(
            ' - A(%s)' % ', '.join(str(v) for v in attach)
            for _label, attach in metadata['nt_edges'])
        return (
            "You have a hyperedge-replacement grammar. Terminal edge labels are "
            "drawn from the set {x, y, z}. There is one nonterminal A of arity %d: "
            "an A edge is written A(%s) and its tentacles attach at the listed "
            "vertices. The boundary of every A-production is [%s]; internal fresh "
            "vertices introduced by a replacement are i0, i1, ... in the order "
            "listed.\n\nReplacing an A edge A(%s) removes the nonterminal and adds "
            "each production edge (u, v, l), substituting boundary b_k by the k-th "
            "attachment a_k and internal i_j by a new vertex. New vertices are "
            "numbered consecutively starting at %d across replacements in the "
            "address order, and within one replacement in internal-node order. The "
            "context edges stay in the final graph.\n\nProductions for A:\n%s\n\n"
            "Start graph vertices are 1..%d. Context edges:\n  %s\n\nReplace the "
            "nonterminal edges in this address order:\n%s\n\nGive the final sorted "
            "list of all edges (context plus every introduced edge), each as "
            "(source, target, label), sorted lexicographically by (source, target, "
            "label) and separated by ';'. Source and target are vertex numbers and "
            "the label is x, y or z. Example answer format: (1,2,x);(3,3,y); isolate "
            "the answer on its own final line."
            % (ar, a_body, b_body, a_body, nv + 1, prod_lines, nv, ctx_body, nt_lines)
        )

    def generate_entry(self):
        cfg = self.config
        nv = max(3, cfg.ctx_edges + 1, cfg.arity + cfg.num_nt)
        ctx = _build_context(cfg, nv)
        nt_edges = _build_nt_edges(cfg, nv)
        prods = _build_productions(cfg)
        result = _derive(cfg, ctx, nt_edges, prods, nv)
        answer = _canonical_str(result)
        for s, t, l in result:
            assert isinstance(s, int) and isinstance(t, int), "vertex must be int"
            assert 1 <= s <= 1000 and 1 <= t <= 1000, "vertex out of domain"
            assert l in TERMINALS, "label outside terminal alphabet"
        return Entry(
            metadata={
                'arity': int(cfg.arity),
                'nv': int(nv),
                'ctx': [list(e) for e in ctx],
                'nt_edges': [[lbl, list(attach)] for lbl, attach in nt_edges],
                'productions': [
                    [list(b_tokens), list(i_tokens),
                     [list(e) for e in edges]]
                    for b_tokens, i_tokens, edges in prods],
                'num_replaced': int(len(nt_edges)),
            },
            answer=answer,
        )

    def score_answer(self, answer, entry):
        try:
            gold = _parse_edges(entry.answer)
            return 1.0 if _parse_edges(answer) == gold else 0.0
        except Exception:
            return 0.0

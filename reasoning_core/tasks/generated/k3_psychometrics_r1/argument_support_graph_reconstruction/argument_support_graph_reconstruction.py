import random
from dataclasses import dataclass

import networkx as nx
from lark import Lark, Transformer

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'argument_support_graph_reconstruction (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_psychometrics_r1/argument_support_graph_reconstruction',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

TOKENS = (
    'frost', 'tide', 'ember', 'ledger', 'beacon', 'sediment', 'reagent',
    'canopy', 'quartz', 'harbor', 'moss', 'vent', 'lantern', 'granite',
    'delta', 'cinder', 'fathom', 'rampart', 'orchard', 'siphon',
)
PARSER = Lark(r'''
    ?start: expr
    ?expr: TOKEN -> claim
         | "(" TOKEN "because" premises ")" -> backward
         | "(" TOKEN "since" premises ")" -> backward
         | "(" "given" "that" premises "," TOKEN ")" -> forward
         | "(" premises ";" "therefore" TOKEN ")" -> forward
    premises: expr ("and" expr)*
    TOKEN: /[a-z]+/
    %import common.WS
    %ignore WS
''', parser='lalr')


class _SupportReader(Transformer):
    def claim(self, items):
        return str(items[0]), []

    def premises(self, items):
        return items

    def backward(self, items):
        head, premises = items
        edges = []
        for premise, inner_edges in premises:
            edges.extend(inner_edges)
            edges.append((premise, str(head)))
        return str(head), edges

    def forward(self, items):
        premises, head = items
        return self.backward([head, premises])


def _read_argument(argument, claims):
    token_to_index = {token: index for index, token in claims}
    head, edges = _SupportReader().transform(PARSER.parse(argument))
    return token_to_index[head], sorted(
        (token_to_index[a], token_to_index[b]) for a, b in edges
    )


def _canonical(edges):
    return ';'.join(f'{a}->{b}' for a, b in sorted(edges))


def _render_argument(node, children, tokens):
    head = tokens[node]
    if not children[node]:
        return head
    branches = list(children[node])
    random.shuffle(branches)
    premises = ' and '.join(_render_argument(child, children, tokens) for child in branches)
    cue = random.choice(('because', 'since', 'given that', 'therefore'))
    if cue == 'given that':
        return f'(given that {premises}, {head})'
    if cue == 'therefore':
        return f'({premises}; therefore {head})'
    return f'({head} {cue} {premises})'


@dataclass
class ArgumentSupportConfig(Config):
    max_claims: int = 5
    max_arms: int = 3

    def apply_difficulty(self, level):
        self.max_claims = min(len(TOKENS), stochastic_rounding(5 + 2 * level))
        self.max_arms = max(2, stochastic_rounding(3 + level / 2))


class ArgumentSupportGraphReconstruction(Task):
    summary = "Scrambled claim tokens with nested because, since, therefore, and given-that cues mark support chains, branching trees, or convergent fans: restore the direct support edge set as a numerically sorted adjacency string."
    design_choice = "Instances present claims as shuffled tokens; solvers output a canonical adjacency string like '1->3;2->3;4->5' listing support edges, with ties broken by node index."
    task_name = 'argument_support_graph_reconstruction'
    task_version = 2
    config_cls = ArgumentSupportConfig

    def generate_entry(self):
        n = random.randint(max(4, self.config.max_claims - 2), self.config.max_claims)
        tokens = random.sample(TOKENS, n)
        labels = random.sample(range(1, n + 1), n)
        family = random.choice(('chain', 'tree', 'fan'))
        parents = []
        if family == 'fan':
            arms = random.randint(2, min(n - 1, self.config.max_arms))
            tips = list(range(1, arms + 1))
            parents = [0] * arms
            for node in range(arms + 1, n):
                arm = random.randrange(arms)
                parents.append(tips[arm])
                tips[arm] = node
        else:
            for node in range(1, n):
                parent = node - 1 if family == 'chain' else random.randrange(node)
                if family == 'tree' and node == 2:
                    parent = 0
                parents.append(parent)
        children = [[] for _ in range(n)]
        for node, parent in enumerate(parents, 1):
            children[parent].append(node)
        edges = sorted((labels[node], labels[parent]) for node, parent in enumerate(parents, 1))
        claims = [[labels[node], tokens[node]] for node in range(n)]
        random.shuffle(claims)
        argument = _render_argument(0, children, tokens)
        answer = _canonical(edges)
        recovered_head, recovered_edges = _read_argument(argument, claims)
        applied = [tuple(map(int, edge.split('->'))) for edge in answer.split(';')]
        assert applied == recovered_edges == edges
        assert recovered_head == labels[0]
        graph = nx.DiGraph(applied)
        assert set(graph) == set(labels)
        assert nx.is_arborescence(graph.reverse())
        assert len(edges) == n - 1
        return Entry(metadata={
            'claims': claims, 'argument': argument, 'edges': [list(e) for e in edges],
            'family': family, 'n_claims': n,
        }, answer=answer)

    def render_prompt(self, metadata):
        claims = '; '.join(f'{index}={token}' for index, token in metadata['claims'])
        return (
            'An editor replaced each claim by a single token. The claim index is fixed, '
            f'but this token list is shuffled: {claims}.\n\n'
            'Reconstruct the direct support links in the argument below by bottom-up parsing. '
            'A bare token denotes that claim. In (X because P) or (X since P), each premise '
            'in P supports X. In (given that P, X) or (P; therefore X), each premise in P '
            'also supports X. All four forms conclude X. The word "and" separates premises; '
            'a parenthesized argument used as a premise contributes only its conclusion '
            'to the enclosing link, while retaining its own internal links. Parentheses '
            'fix scope. Record only these explicit links, not transitive links.\n\n'
            f'{metadata["argument"]}\n\n'
            'Output each edge as supporter->supported using claim indices. Sort by the '
            'supporter index numerically, then by the supported index numerically; include '
            'each edge once. Join with semicolons and no spaces. Example format: '
            '1->3;2->3;4->5. Output only the adjacency string.'
        )

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip() == entry.answer)

    def distractor_candidates(self, entry):
        edges = [tuple(edge) for edge in entry.metadata['edges']]
        yield _canonical([(b, a) for a, b in edges])
        yield _canonical(edges[:-1])
        yield _canonical(nx.transitive_closure_dag(nx.DiGraph(edges)).edges())

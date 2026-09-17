import random
from dataclasses import dataclass
from itertools import combinations

from reasoning_core.template import Config, Entry, Task, render_payload

TASK_META = {'parent_source_id': None,
 'idea': 'definitional_unfolding_subsumption (variant 2 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_controlled_nli_r1/definitional_unfolding_subsumption',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 241712510,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

ATOMS = ['Blue', 'Bright', 'Light', 'Rigid', 'Round', 'Smooth']
ROLES = ['part', 'link', 'cover']
NAMES = ['Aster', 'Birch', 'Cedar', 'Dahlia', 'Elm', 'Fern', 'Grove',
         'Hazel', 'Iris', 'Juniper', 'Laurel', 'Maple', 'Oak', 'Pine', 'Reed', 'Willow']


def show(expr):
    return ' & '.join(x if isinstance(x, str) else
                      f'exists {x[0]}.({show(x[1])})' for x in expr) or 'TOP'


def unfold(expr, definitions):
    atoms, edges = set(), []
    for term in expr:
        if isinstance(term, str):
            if term in definitions:
                ns, rs = unfold(definitions[term], definitions)
                atoms.update(ns)
                edges.extend(rs)
            else:
                atoms.add(term)
        else:
            edges.append((term[0], unfold(term[1], definitions)))
    return tuple(sorted(atoms)), tuple(sorted(set(edges)))


def entails(specific, general):
    return (set(general[0]) <= set(specific[0]) and
            all(any(r == s and entails(a, b) for r, a in specific[1])
                for s, b in general[1]))


def canonical_model(expr, definitions):
    labels, edges = [], []

    def add(terms):
        index = len(labels)
        labels.append(set())
        edges.append([])

        def fill(items):
            for item in items:
                if isinstance(item, str):
                    if item in definitions:
                        fill(definitions[item])
                    else:
                        labels[index].add(item)
                else:
                    child = add(item[1])
                    edges[index].append((item[0], child))

        fill(terms)
        return index

    add(expr)
    return labels, edges


def satisfies(model, expr, definitions, vertex=0):
    labels, edges = model
    for term in expr:
        if isinstance(term, str):
            if term in definitions:
                if not satisfies(model, definitions[term], definitions, vertex):
                    return False
            elif term not in labels[vertex]:
                return False
        elif not any(role == term[0] and satisfies(model, term[1], definitions, child)
                     for role, child in edges[vertex]):
            return False
    return True


def merge(nodes):
    return (tuple(sorted(set(a for node in nodes for a in node[0]))),
            tuple(sorted(set(edge for node in nodes for edge in node[1]))))


def canonical_basis(common, nodes):
    target = merge([nodes[name] for name in common])
    for size in range(len(common) + 1):
        for subset in combinations(sorted(common), size):
            if entails(merge([nodes[name] for name in subset]), target):
                return list(subset)
    raise RuntimeError('No defined subsumer basis')


def obscure(expr, definitions, probability=0.45):
    result = []
    for term in expr:
        if isinstance(term, str):
            if term in definitions and random.random() < probability:
                result.extend(obscure(definitions[term], definitions, probability * 0.4))
            else:
                result.append(term)
        else:
            result.append([term[0], obscure(term[1], definitions, probability)])
    random.shuffle(result)
    return result


@dataclass
class UnfoldingConfig(Config):
    candidates: int = 6
    depth: int = 1
    width: int = 2

    def apply_difficulty(self, level):
        self.candidates = min(10, 6 + int(level))
        self.depth = min(5, 1 + int(level) // 2)
        self.width = min(4, 2 + int(level) // 3)


class DefinitionalUnfoldingSubsumption(Task):
    summary = 'Acyclic definition boxes over stated concept and role names: unfold into nested existential restriction conjunctions and test subsumption between queries by structural comparison; answers are the least defined common subsumer as a canonical conjunction of lexicographically sorted names.'
    design_choice = 'Answer format: the least defined subsumer as a canonical conjunction string, with names sorted lexicographically.'
    config_cls = UnfoldingConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        definitions = {}
        helpers = []
        for i in range(cfg.depth + 1):
            name = f'H{i}'
            terms = random.sample(ATOMS, random.randint(1, cfg.width))
            filler = [random.choice(helpers)] if helpers else random.sample(ATOMS, 2)
            terms.append([random.choice(ROLES), filler])
            definitions[name] = terms
            helpers.append(name)
        features = random.sample(ATOMS, 3) + helpers
        features += [[random.choice(ROLES), [random.choice(helpers)]] for _ in range(3)]
        names = random.sample(NAMES, cfg.candidates)
        for i, name in enumerate(names):
            terms = random.sample(features, random.randint(1, cfg.width))
            if i and random.random() < 0.45:
                terms.append(random.choice(names[:i]))
            definitions[name] = terms
        seeds = random.sample(names, random.randint(1, min(3, cfg.width)))
        queries = []
        for _ in range(2):
            chosen = seeds + random.sample(names, random.randint(0, 2))
            terms = [term for name in chosen for term in definitions[name]]
            terms += random.sample(ATOMS, random.randint(0, 2))
            queries.append(obscure(terms, definitions))
        nodes = {name: unfold([name], definitions) for name in names}
        qnodes = [unfold(query, definitions) for query in queries]
        common = sorted(name for name in names if all(entails(q, nodes[name]) for q in qnodes))
        basis = canonical_basis(common, nodes)
        qmodels = [canonical_model(query, definitions) for query in queries]
        checked = sorted(name for name in names if all(satisfies(m, [name], definitions)
                                                       for m in qmodels))
        assert checked == common
        answer_model = canonical_model(basis, definitions)
        assert all(satisfies(m, basis, definitions) for m in qmodels)
        assert all(satisfies(answer_model, [name], definitions) for name in common)
        verified = None
        for size in range(len(basis) + 1):
            for subset in combinations(common, size):
                model = canonical_model(subset, definitions)
                if all(satisfies(model, [name], definitions) for name in common):
                    verified = subset
                    break
            if verified is not None:
                break
        assert tuple(basis) == verified
        answer = ' & '.join(basis) or 'TOP'
        payload = {
            'Vocabulary': 'Primitive concepts: ' + ', '.join(ATOMS) + '. Roles: ' + ', '.join(ROLES) + '.',
            'Definitions': '\n'.join(f'{name} := {show(expr)}' for name, expr in definitions.items()),
            'Eligible names': ', '.join(sorted(names)),
            'Queries': '\n'.join(f'{label} := {show(expr)}' for label, expr in zip(['Q', 'R'], queries)),
        }
        return Entry(answer=answer, metadata={'definitions': definitions, 'names': names,
                                             'queries': queries, 'common': common,
                                             'basis': basis, 'payload': payload})

    def render_prompt(self, metadata):
        return (
            'An ontology catalog needs the tightest shared description of two queries, using only '
            'the eligible defined names. Definitions are equivalences and acyclic. Primitive '
            'concepts are independent sets; roles are arbitrary binary relations, with no other axioms. '
            'X & Y is intersection; exists r.(X) means having at least one r-successor in X. '
            'Different restrictions may use different successors. TOP contains every individual.\n'
            'Use definitional unfolding and the EL structural subsumption algorithm: S is subsumed '
            'by T when every root atom of T occurs in S and each restriction of T is matched by '
            'a same-role restriction of S whose filler is recursively subsumed by the filler '
            'of that restriction of T.\n'
            + render_payload(metadata['payload']) + '\n'
            'Find the least defined common subsumer: a conjunction of eligible names containing '
            'both Q and R in every model, and contained in every other such conjunction. '
            'Among equivalent conjunctions choose the fewest distinct names, then the '
            'lexicographically smallest sorted name list. Output only those case-sensitive names '
            "joined by ' & ', for example 'Aster & Cedar'; output TOP for the empty conjunction."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return float(answer.strip() == entry.answer)

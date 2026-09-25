import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


RELS = ['p', 'q', 'r', 's', 't']
WIDTHS = [1, 1, 2, 2]


def _fmt(atom):
    return atom[0] + '(' + ','.join(atom[1]) + ')'


def _match_atom(target, source, assign):
    if source[0] != target[0]:
        return None
    assign = dict(assign)
    for sv, tv in zip(source[1], target[1]):
        if sv[0] == 'v':
            if sv in assign:
                if assign[sv] != tv:
                    return None
            else:
                assign[sv] = tv
        else:
            if sv != tv:
                return None
    return assign


def _unify(target, source):
    if len(target) != len(source):
        return False
    target = list(target)
    def rec(remaining, assign):
        if not remaining:
            return True
        first = remaining[0]
        for i in range(len(target)):
            merged = _match_atom(target[i], first, assign)
            if merged is not None:
                t = target.pop(i)
                if rec(remaining[1:], merged):
                    return True
                target.insert(i, t)
        return False
    return rec(list(source), {})


def _branch(parent, L):
    path = [L]
    cur = parent[L]
    while cur != -1:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path


def _has_descent(seq, parent, A, L):
    path = _branch(parent, L)
    if A not in path:
        return False
    sub = path[path.index(A):]
    for i in range(len(sub) - 1):
        if len(seq[sub[i + 1]]) < len(seq[sub[i]]):
            return True
    return False


def _valid(seq, parent, A, L):
    if not _unify(seq[A], seq[L]):
        return False
    return _has_descent(seq, parent, A, L)


def _valid_ancestors(seq, parent, L):
    return [a for a in _branch(parent, L) if a != L and _valid(seq, parent, a, L)]


def _ground_seq(node_id):
    seq = [('q', (('c%d' % node_id),))]
    count = random.randint(1, 2)
    for _ in range(count):
        rel = random.choice(RELS)
        width = random.choice(WIDTHS)
        terms = tuple('c%d' % random.randrange(1000, 100000) for _ in range(width))
        seq.append((rel, terms))
    seq.sort(key=_fmt)
    return seq


@dataclass
class CyclicProofClosureConfig(Config):
    min_nodes: int = 5
    max_nodes: int = 6

    def apply_difficulty(self, level):
        self.min_nodes = 7 + level
        self.max_nodes = 9 + level * 2


class CyclicProofClosure(Task):
    summary = ("Complete cyclic proof skeletons by linking one open leaf to a compatible ancestor, "
               "respecting substitution-based matching and a stated descent progress condition on the "
               "closing cycle; return the single valid back-link ancestor id or 'impossible'.")
    design_choice = ("Instances present proof trees with exactly one open leaf; answer is the single "
                     "ancestor node index if a valid back-link exists, else the word 'impossible'.")
    config_cls = CyclicProofClosureConfig
    task_version = 2

    def generate_entry(self):
        n_nodes = random.randint(self.config.min_nodes, self.config.max_nodes)
        solvable = random.random() < 0.58
        spine = random.randint(4, min(n_nodes, max(4, n_nodes - 1)))
        L = spine - 1 if solvable else n_nodes - 1
        seq = [None] * n_nodes
        parent = [-1] * n_nodes
        children = [[] for _ in range(n_nodes)]

        for i in range(1, spine):
            parent[i] = i - 1
            children[i - 1].append(i)

        for i in range(spine, n_nodes):
            candidates = [j for j in range(i) if j != L]
            p = random.choice(candidates)
            parent[i] = p
            children[p].append(i)

        for i in range(n_nodes):
            if i != L:
                seq[i] = _ground_seq(i)

        chosen = None
        if solvable:
            a = random.randrange(1, spine - 2)
            chosen = a
            seq[a] = _ground_seq(a)
            while len(seq[a]) != 2:
                seq[a] = _ground_seq(a)
            c = len(seq[a])
            parent_of_leaf = parent[L]
            seq[parent_of_leaf] = _ground_seq(parent_of_leaf)
            while len(seq[parent_of_leaf]) != c + 1:
                seq[parent_of_leaf] = _ground_seq(parent_of_leaf)
            leaf_atoms = list(seq[a])
            if random.random() < 0.5:
                for idx in range(len(leaf_atoms)):
                    terms = list(leaf_atoms[idx][1])
                    got_var = False
                    for j in range(len(terms)):
                        if terms[j][0] == 'c' and random.random() < 0.5:
                            terms[j] = 'v0'
                            got_var = True
                            break
                    if got_var:
                        leaf_atoms[idx] = (leaf_atoms[idx][0], tuple(terms))
                        break
            seq[L] = sorted(leaf_atoms, key=_fmt)
        else:
            seq[L] = _ground_seq(2000000 + L)

        ancestors = _valid_ancestors(seq, parent, L)
        if solvable:
            if ancestors != [chosen]:
                return None
        else:
            if ancestors:
                return None

        metadata = {
            'nodes': [
                {
                    'id': i,
                    'seq': list(s),
                    'children': list(children[i]),
                }
                for i, s in enumerate(seq)
            ],
            'root': 0,
            'open_leaf': L,
        }
        answer = 'impossible' if not solvable else str(chosen)
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        for node in metadata['nodes']:
            seq = ', '.join(_fmt(tuple(a)) for a in node['seq'])
            lines.append('%d: {%s} -> [%s]' % (
                node['id'], seq, ', '.join(str(c) for c in node['children'])))
        body = '\n'.join(lines)
        return (
            "Below is a cyclic proof tree skeleton. Node %d is the root; node %d is the single "
            "open leaf (it has no children). Each line lists a node id, its sequent (a set of "
            "atoms), and its children. Constants are written like c5; variables like v0.\n\n"
            "%s\n\n"
            "Close the proof by linking the open leaf to one ancestor via a back-link. A back-link "
            "to ancestor A is valid iff both hold: (Matching) the leaf sequent unifies with A's "
            "ground sequent under some substitution, so the two become the same multiset of atoms; "
            "and (Progress) on the root-to-leaf branch between A and the open leaf, at least one "
            "edge strictly decreases the number of atoms (the closing cycle is progressive).\n\n"
            "Report the single ancestor node id that admits a valid back-link, or the word "
            "'impossible' if no ancestor does. Answer with just that."
        ) % (metadata['root'], metadata['open_leaf'], body)

    def score_answer(self, answer, entry):
        ref = str(entry['answer']).strip()
        ans = str(answer).strip()
        return 1.0 if ans == ref else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'cyclic_proof_closure (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_inference_modes_r4/cyclic_proof_closure',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'anyon_fusion_reassociation (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dynamic_structures_r4/anyon_fusion_reassociation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

VAC = "1"
A = "A"


def _fuse_set(a, b):
    if a == VAC:
        return {b}
    if b == VAC:
        return {a}
    return {VAC, A}


def _random_bracket(n):
    trees = [A] * n
    while len(trees) > 1:
        i = random.randrange(len(trees) - 1)
        trees = trees[:i] + [(trees[i], trees[i + 1])] + trees[i + 2:]
    return trees[0]


def _reachable(node):
    if node == A:
        return {A}
    l, r = node
    lr = _reachable(l)
    rr = _reachable(r)
    out = set()
    for a in lr:
        for b in rr:
            out |= _fuse_set(a, b)
    return out


def _assign(node, parent):
    if node == A:
        return A
    l, r = node
    lr = sorted(_reachable(l))
    rr = sorted(_reachable(r))
    choices = []
    for a in lr:
        for b in rr:
            if parent in _fuse_set(a, b):
                choices.append((a, b))
    a, b = random.choice(choices)
    return (_assign(l, a), _assign(r, b), parent)


def _count_leaves(node):
    if node == A:
        return 1
    l, r, _ = node
    return _count_leaves(l) + _count_leaves(r)


def _find_r_vertices(node):
    if not isinstance(node, tuple):
        return []
    l, r, ch = node
    res = []
    if l == A and r == A:
        res.append((node, ch))
    res += _find_r_vertices(l)
    res += _find_r_vertices(r)
    return res


def _find_f_leads(node):
    if not isinstance(node, tuple):
        return []
    l, r, ch = node
    res = []
    if isinstance(l, tuple):
        ll, lr, lc = l
        if ll == A and lr == A and r == A:
            res.append((node, "left", ch, lc))
    if isinstance(r, tuple):
        rl, rr, rc = r
        if rl == A and rr == A and l == A:
            res.append((node, "right", ch, rc))
    res += _find_f_leads(l)
    res += _find_f_leads(r)
    return res


def _node_leafrange(node, start, target):
    if node is target:
        return start, _count_leaves(node)
    if node == A:
        return None
    l, r, _ = node
    n = _count_leaves(l)
    a = _node_leafrange(l, start, target)
    if a is not None:
        return a
    return _node_leafrange(r, start + n, target)


def _render(node):
    if node == A:
        return A
    l, r, ch = node
    return f"({_render(l)} \u2297 {_render(r)})^{ch}"


@dataclass
class AnyonFusionConfig(Config):
    n: int = 3

    def apply_difficulty(self, level):
        self.n = 3 + level


class AnyonFusionReassociation(Task):
    summary = "Track fusion states through tree reassociations, particle exchanges and specified fusion outcomes using supplied fusion, F and R tables; return a queried unnormalized amplitude."
    design_choice = "Use a single fixed anyon type set with random tree bracketings, and query the amplitude after exactly one F-move and one R-move in a specified order."
    config_cls = AnyonFusionConfig

    def generate_entry(self):
        n = self.config.n
        for _ in range(500):
            t = _random_bracket(n)
            ct = _assign(t, VAC)
            rverts = _find_r_vertices(ct)
            fleads = _find_f_leads(ct)
            if not rverts or not fleads:
                continue

            rnode, c = random.choice(rverts)
            flead = random.choice(fleads)
            fn, shape, d, n_in = flead

            # consistency checks the generator enforces
            assert _node_leafrange(ct, 0, rnode) is not None
            if d == VAC:
                assert n_in == A, "a vacuum outer charge forces an A inner channel"
            else:
                assert d == A and d in _fuse_set(n_in, A)
            assert c in _fuse_set(A, A)

            R = {VAC: random.choice([-1, 1]), A: random.choice([-1, 1])}
            F = {
                VAC: {A: {A: random.choice([-2, -1, 1, 2])}},
                A: {ni: {m: random.choice([-2, -1, 1, 2]) for m in (VAC, A)}
                    for ni in (VAC, A)},
            }

            if d == VAC:
                m_query = A
            else:
                m_query = random.choice([VAC, A])

            amplitude = R[c] * F[d][n_in][m_query]
            assert isinstance(amplitude, int)

            rspan = _node_leafrange(ct, 0, rnode)
            fspan = _node_leafrange(ct, 0, fn)
            leaf_count = _count_leaves(ct)
            assert rspan is not None and fspan is not None
            assert rspan[1] == 2 and fspan[1] == 3

            metadata = {
                "n": int(n),
                "leaf_count": int(leaf_count),
                "tree_render": _render(ct),
                "types": [VAC, A],
                "fusion_rule": "1*x=x; A*A=1 or A",
                "r_table": {"r1": int(R[VAC]), "rA": int(R[A])},
                "f1_AA": int(F[VAC][A][A]),
                "fA_matrix": [[int(F[A][ni][m]) for m in (VAC, A)] for ni in (VAC, A)],
                "r_braid": {"leaf_from": int(rspan[0] + 1), "leaf_to": int(rspan[0] + 2),
                            "channel": c},
                "f_move": {"leaf_from": int(fspan[0] + 1),
                           "leaf_to": int(fspan[0] + 3), "shape": shape,
                           "outer_charge": d, "inner_channel": n_in,
                           "query_channel": m_query},
                "amplitude": int(amplitude),
            }
            return Entry(metadata=metadata, answer=str(int(amplitude)))
        raise RuntimeError("failed to generate an admissible fusion instance")

    def render_prompt(self, metadata):
        braid = metadata["r_braid"]
        fmove = metadata["f_move"]
        f2 = metadata["fA_matrix"]
        fline = (
            f"F[1]: reassociating with outer charge 1, inner channel A -> A has "
            f"coefficient {metadata['f1_AA']}.\n"
            f"F[A]: reassociating with outer charge A is the 2x2 matrix "
            f"[[{f2[0][0]}, {f2[0][1]}], [{f2[1][0]}, {f2[1][1]}]] "
            f"indexed by [old inner channel][new inner channel] over (1, A)."
        )
        order = "R-move first, then F-move"
        return (
            f"An anyon fusion category has types 1 (vacuum) and A. "
            f"Fusion follows 1*x = x and A*A = 1 or A.\n"
            f"Braiding an A,A pair is diagonal in its fusion outcome: "
            f"R[1] = {metadata['r_table']['r1']} and R[A] = {metadata['r_table']['rA']}.\n"
            f"Reassociation (F) of a 3-anyon subtree flips the grouping "
            f"((x*y)*z) <-> (x*(y*z)); its coefficients depend only on the outer "
            f"charge and the inner channel:\n{fline}\n"
            f"The current fusion state of the {metadata['leaf_count']} A-anyons "
            f"(a \u00b7 inside means fused, superscript is the fusion charge) is:\n"
            f"{metadata['tree_render']}\n"
            f"Apply the moves in this order: {order}.\n"
            f"R-move: braid the adjacent A-anyons at leaf positions "
            f"{braid['leaf_from']} and {braid['leaf_to']} "
            f"(they currently fuse to channel {braid['channel']}).\n"
            f"F-move: reassociate the three consecutive leaves "
            f"{fmove['leaf_from']},{fmove['leaf_from']+1},{fmove['leaf_to']} "
            f"(combined charge {fmove['outer_charge']}, present inner channel "
            f"{fmove['inner_channel']}), flipping the grouping.\n"
            f"After these moves, what is the amplitude to the configuration where the "
            f"reassociated inner pair fuses to channel {fmove['query_channel']}?\n"
            f"The answer is one integer (the unnormalized amplitude)."
        )

    def score_answer(self, answer, entry):
        return _score_amplitude(answer, entry["answer"])


def _score_amplitude(answer, gold):
    try:
        a = int(str(answer).strip())
        g = int(str(gold).strip())
    except (ValueError, TypeError):
        return 0.0
    return 1.0 if a == g else 0.0

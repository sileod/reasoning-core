import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'proof_net_link_repair (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_verification_repair_r4/proof_net_link_repair',
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

design_choice = ("Represent each proof structure as a compact string of link types and "
                 "terminal labels; the answer is either a switching assignment string or a "
                 "canonical swap command like 'swap 3 7'.")


def _is_acyclic(par_links, tensor_edges, ax_edges, par_bits, num_nodes):
    adj = [[] for _ in range(num_nodes)]
    for a, b, c in tensor_edges:
        adj[a].append(c)
        adj[c].append(a)
        adj[b].append(c)
        adj[c].append(b)
    for (a, b, c), bit in zip(par_links, par_bits):
        x = b if bit else a
        adj[x].append(c)
        adj[c].append(x)
    for u, v in ax_edges:
        adj[u].append(v)
        adj[v].append(u)
    color = [0] * num_nodes
    sys_limit = num_nodes + 2
    stack = []

    def dfs(root):
        stack.append((root, -1, 0))
        while stack:
            x, p, idx = stack.pop()
            if idx == 0:
                color[x] = 1
            adv = 0
            for j in range(idx, len(adj[x])):
                y = adj[x][j]
                if y == p:
                    continue
                if color[y] == 1:
                    return True
                if color[y] == 0:
                    stack.append((x, p, j + 1))
                    stack.append((y, x, 0))
                    break
            else:
                color[x] = 2
        return False

    for i in range(num_nodes):
        if color[i] == 0:
            if dfs(i):
                return False
    return True


def _all_acyclic(par_links, tensor_edges, ax_pairs, num_nodes):
    n = len(par_links)
    for m in range(1 << n):
        bits = [(m >> i) & 1 for i in range(n)]
        if not _is_acyclic(par_links, tensor_edges, ax_pairs, bits, num_nodes):
            return False
    return True


def _min_cyclic_switching(par_links, tensor_edges, ax_pairs, num_nodes):
    n = len(par_links)
    for m in range(1 << n):
        bits = [(m >> i) & 1 for i in range(n)]
        if not _is_acyclic(par_links, tensor_edges, ax_pairs, bits, num_nodes):
            return "".join("1" if b else "0" for b in bits)
    return None


def _swap_endpoints(ax_links, i, j):
    la, pa, qa = ax_links[i]
    lb, pb, qb = ax_links[j]
    out = [tuple(x) for x in ax_links]
    out[i] = (la, pa, qb)
    out[j] = (lb, pb, qa)
    return out


def _min_repair_pair(par_links, tensor_edges, ax_links, num_nodes):
    best = None
    n = len(ax_links)
    for i in range(n):
        for j in range(i + 1, n):
            if ax_links[i][0] != ax_links[j][0]:
                continue
            swapped = _swap_endpoints(ax_links, i, j)
            pairs = [(u, v) for (_, u, v) in swapped]
            if _all_acyclic(par_links, tensor_edges, pairs, num_nodes):
                best = (i, j)
                return best
    return best


def _build(num_axioms, alphabet_size):
    alphabet = [chr(ord("a") + i) for i in range(alphabet_size)]
    for _ in range(120):
        try:
            inst = _build_once(num_axioms, alphabet)
            if inst is not None:
                return inst
        except RuntimeError:
            continue
    raise RuntimeError("could not build a valid broken proof structure")


def _build_once(num_axioms, alphabet):
    ax_links = []
    uid = 0
    for _ in range(num_axioms):
        lab = random.choice(alphabet)
        ax_links.append((lab, uid, uid + 1))
        uid += 2
    num_leaves = uid

    nets = [[a, b] for (_, a, b) in ax_links]
    par_links = []
    tensor_edges = []
    while not (len(nets) == 1 and len(nets[0]) == 1):
        multi = [i for i, rl in enumerate(nets) if len(rl) >= 2]
        if len(nets) > 1:
            if multi and random.random() < 0.5:
                ni = random.choice(multi)
                r1, r2 = random.sample(nets[ni], 2)
                c = uid
                uid += 1
                par_links.append((r1, r2, c))
                nets[ni] = [x for x in nets[ni] if x != r1 and x != r2] + [c]
            else:
                i, j = random.sample(range(len(nets)), 2)
                r1 = nets[i][0] if nets[i] else None
                r2 = nets[j][0] if nets[j] else None
                c = uid
                uid += 1
                if r1 is None or r2 is None:
                    continue
                tensor_edges.append((r1, r2, c))
                nets[i] = [x for x in nets[i] if x != r1] + [c]
                nets[j] = [x for x in nets[j] if x != r2]
                nets[i] = nets[i] + [x for x in nets[j]]
                nets.pop(j)
        else:
            r1, r2 = random.sample(nets[0], 2)
            c = uid
            uid += 1
            par_links.append((r1, r2, c))
            nets[0] = [x for x in nets[0] if x != r1 and x != r2] + [c]
    num_nodes = uid
    if num_nodes != 4 * num_axioms - 1:
        return None

    correct_pairs = [(u, v) for (_, u, v) in ax_links]
    if not _all_acyclic(par_links, tensor_edges, correct_pairs, num_nodes):
        return None

    same = [(i, j) for i in range(num_axioms) for j in range(i + 1, num_axioms)
            if ax_links[i][0] == ax_links[j][0]]
    if not same:
        return None
    random.shuffle(same)
    for bp in same:
        broken = _swap_endpoints(ax_links, bp[0], bp[1])
        broken_pairs = [(u, v) for (_, u, v) in broken]
        if _all_acyclic(par_links, tensor_edges, broken_pairs, num_nodes):
            continue
        return (ax_links, broken, par_links, tensor_edges, num_nodes)
    return None


def _render_links(ax_links, par_links, tensor_edges):
    lines = []
    for idx, (lab, u, v) in enumerate(ax_links):
        lines.append("axiom %d: n%d--n%d [%s]" % (idx, u, v, lab))
    for pidx, (a, b, c) in enumerate(par_links):
        lines.append("par P%d: n%d %s n%d -> n%d" % (pidx, a, BOT, b, c))
    for a, b, c in tensor_edges:
        lines.append("tensor: n%d %s n%d -> n%d" % (a, TENS, b, c))
    return "; ".join(lines)


BOT = "\u2aaf"
TENS = "\u2297"


def render_prompt(metadata):
    ak = metadata["ax_links"]
    pat = metadata["par_links"]
    te = metadata["tensor_edges"]
    body = _render_links(ak, pat, te)
    if metadata["mode"] == "A":
        return (
            "An MLL proof structure is described by these links (the n{id} are formula "
            "nodes; leaves carry atom labels and are paired by axiom links; '\u2297' is a "
            "tensor and '\u2aaf' is a par link, each with two premises and one conclusion): "
            + body +
            ". A switching keeps, for every \u2aaf (par) link, exactly one of its two "
            "premise edges (0 = keep the first premise, 1 = keep the second premise); tensor "
            "and axiom edges are always kept. The par links appear in order P0, P1, ... The "
            "structure is a proof net only if every switching is acyclic. A switching "
            "assignment is a bit string, position i for Pi. Find a switching that is cyclic, "
            "proving this is NOT a proof net, and return the lexicographically smallest such "
            "bit string. Answer with that bit string only."
        )
    return (
        "An MLL proof structure is described by these links (axiom links pair atoms of the "
        "same label; '\u2297' is tensor and '\u2aaf' is par, each with two premises and one "
        "conclusion): " + body +
        ". A switching keeps, for every \u2aaf (par) link, exactly one premise edge; the "
        "structure is a proof net only if every switching is acyclic. This structure is NOT a "
        "proof net. Swapping the atom endpoints of two axiom links (which must carry the same "
        "atom label) can restore correctness so that every switching is acyclic. Axiom links "
        "are numbered 0,1,... in the order listed above. Return the canonical repair, the "
        "lexicographically smallest pair {i,j} with i<j of same-label axiom links whose swap "
        "makes every switching acyclic, as 'swap i j'."
    )


@dataclass
class ProofNetConfig(Config):
    num_axioms: int = 3
    alphabet_size: int = 2

    def apply_difficulty(self, level):
        self.num_axioms = stochastic_rounding(3 + level * 0.7,
                                              seed=random.randrange(2 ** 32))
        self.alphabet_size = min(5, 2 + level)


class ProofNetLinkRepair(Task):
    summary = "Audit multiplicative linear-logic proof structures across tensor, par, and axiom links by checking every switching; return a failing switching witness or an axiom-link swap restoring correctness."
    config_cls = ProofNetConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        ax_links, broken, par_links, tensor_edges, num_nodes = _build(
            cfg.num_axioms, cfg.alphabet_size)
        mode = random.choice(["A", "B"])
        if mode == "A":
            answer = _min_cyclic_switching(par_links, tensor_edges,
                                           [(u, v) for (_, u, v) in broken], num_nodes)
            if answer is None:
                raise RuntimeError("mode A but no cyclic switching")
        else:
            i, j = _min_repair_pair(par_links, tensor_edges, broken, num_nodes)
            answer = "swap %d %d" % (i, j)
        metadata = {
            "num_nodes": int(num_nodes),
            "ax_links": [[str(l), int(u), int(v)] for (l, u, v) in broken],
            "par_links": [[int(a), int(b), int(c)] for (a, b, c) in par_links],
            "tensor_edges": [[int(a), int(b), int(c)] for (a, b, c) in tensor_edges],
            "mode": mode,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return render_prompt(metadata)

    def score_answer(self, answer, entry):
        return score_answer(answer, entry)


def score_answer(answer, entry):
    md = entry.metadata
    par_links = [tuple(int(x) for x in t) for t in md["par_links"]]
    tensor_edges = [tuple(int(x) for x in t) for t in md["tensor_edges"]]
    ax_links = [tuple(x) for x in md["ax_links"]]
    ax_links = [(l, int(u), int(v)) for (l, u, v) in ax_links]
    nn = int(md["num_nodes"])
    if md["mode"] == "A":
        if not isinstance(answer, str):
            return 0.0
        s = answer.strip()
        if len(s) != len(par_links) or set(s) - set("01"):
            return 0.0
        bits = [1 if ch == "1" else 0 for ch in s]
        if _is_acyclic(par_links, tensor_edges, [(u, v) for (_, u, v) in ax_links],
                       bits, nn):
            return 0.0
        gold = _min_cyclic_switching(par_links, tensor_edges,
                                     [(u, v) for (_, u, v) in ax_links], nn)
        return 1.0 if s == gold else 0.0
    if not isinstance(answer, str):
        return 0.0
    parts = answer.split()
    if len(parts) != 3 or parts[0] != "swap":
        return 0.0
    try:
        i = int(parts[1])
        j = int(parts[2])
    except ValueError:
        return 0.0
    if not (0 <= i < j < len(ax_links)):
        return 0.0
    if ax_links[i][0] != ax_links[j][0]:
        return 0.0
    gold = _min_repair_pair(par_links, tensor_edges, ax_links, nn)
    if gold is None:
        return 0.0
    return 1.0 if (i, j) == gold else 0.0

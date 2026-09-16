"""Ordered labeled tree pattern occurrence counting.

Each instance gives an ordered labeled host tree (as adjacency lists) and a smaller
ordered labeled pattern tree. An *embedding* of the pattern into the host is an
injective label-preserving map of pattern nodes into host nodes such that the image of
each pattern node's ordered children lie in pairwise distinct, ordered child-subtrees
of the image host node. The answer is the total number of such rooted occurrences
(an integer count).
"""

import random
from dataclasses import dataclass
from itertools import permutations

from reasoning_core.template import Config, Entry, Task

TARGETS = [0, 1, 2, 2, 3, 3, 4, 5, 6, 7]

TASK_META = {'parent_source_id': None,
 'idea': 'tree_pattern_occurrence_count (draw 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dynamic_structures_r1/tree_pattern_occurrence_count',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

LABELS = ["a", "b", "c", "d", "e", "f", "g"]
WILDCARD = "*"


@dataclass
class TreePatternCountConfig(Config):
    host_nodes: int = 5
    pattern_nodes: int = 2
    label_alpha: int = 2

    def apply_difficulty(self, level):
        self.host_nodes = 5 + (level // 2)
        self.pattern_nodes = min(2 + (level // 2), 4)
        if self.pattern_nodes > self.host_nodes - 1:
            self.pattern_nodes = max(1, self.host_nodes - 1)
        self.label_alpha = 2 + (level >= 2)


class _Node:
    __slots__ = ("label", "children")

    def __init__(self, label):
        self.label = label
        self.children = []


def _random_label(alpha):
    return random.choice(LABELS[:alpha])


def _make_random_tree(n, alpha):
    nodes = [_Node(_random_label(alpha)) for _ in range(n)]
    for i in range(1, n):
        parent = random.randrange(i)
        nodes[parent].children.append(nodes[i])
    return nodes


def _make_ordered_pattern(n, alpha):
    nodes = [_Node(_random_label(alpha)) for _ in range(n)]
    for i in range(1, n):
        parent = random.randrange(i)
        nodes[parent].children.append(nodes[i])
    n_wild = sum(1 for _ in range(n) if random.random() < 0.3)
    for idx in random.sample(range(n), min(n_wild, n)):
        nodes[idx].label = WILDCARD
    return nodes


def _pattern_subcnt(u, h, subcnt, cnt):
    total = cnt.get((id(u), id(h)), 0)
    for ch in h.children:
        total += _pattern_subcnt(u, ch, subcnt, cnt)
    return total


def _pattern_cnt(u, h, subcnt, cnt):
    if u.label != WILDCARD and u.label != h.label:
        return 0
    if not u.children:
        return 1
    host_children = h.children
    k = len(u.children)
    if k > len(host_children):
        return 0
    dp = [0] * (k + 1)
    dp[0] = 1
    for x in host_children:
        weight = [_pattern_subcnt(c, x, subcnt, cnt) for c in u.children]
        newdp = dp[:]
        for placed in range(k):
            if dp[placed] and weight[placed]:
                newdp[placed + 1] += dp[placed] * weight[placed]
        dp = newdp
    return dp[k]


def _count_embeddings(host_root, pattern_root):
    H, P = host_root, pattern_root

    def fill(node_h, node_p):
        key = (id(node_p), id(node_h))
        if key in cnt:
            return
        cnt[key] = _pattern_cnt(node_p, node_h, subcnt, cnt)
        subcnt[key] = cnt[key]
        for ch in node_h.children:
            fill(ch, node_p)
            subcnt[key] += subcnt[(id(node_p), id(ch))]

    cnt = {}
    subcnt = {}
    for p in reversed(P):
        for h in H:
            fill(h, p)
    root_key = (id(P[0]), id(H[0]))
    return subcnt.get(root_key, 0)


def _root_paths(root):
    paths = {}

    def walk(node, path):
        paths[id(node)] = list(path)
        for i, ch in enumerate(node.children):
            walk(ch, path + [i])

    walk(root, [])
    return paths


def _brute_force(host_root, pattern_root):
    H, P = host_root, pattern_root
    paths = _root_paths(H[0])
    m = len(P)
    count = 0
    for perm in permutations(range(len(H)), m):
        img = list(perm)
        ok = True
        for j in range(m):
            if P[j].label != WILDCARD and P[j].label != H[img[j]].label:
                ok = False
                break
        if not ok:
            continue
        for j in range(m):
            children = P[j].children
            if not children:
                continue
            hn = H[img[j]]
            parent_path = paths.get(id(hn))
            positions = []
            for ci in children:
                path = paths.get(id(H[img[P.index(ci)]]))
                if parent_path is None or path is None:
                    positions.append(None)
                    continue
                if not (len(path) > len(parent_path) and
                        path[:len(parent_path)] == parent_path):
                    positions.append(None)
                    continue
                positions.append(path[len(parent_path)])
            if any(p is None for p in positions):
                ok = False
                break
            if len(set(positions)) != len(positions) or positions != sorted(positions):
                ok = False
                break
        if ok:
            count += 1
    return count


def _render_adjacency(nodes):
    lines = []
    index = {id(n): i for i, n in enumerate(nodes)}
    for n in nodes:
        children = [str(index[id(c)]) for c in n.children]
        line = f"{index[id(n)]} {n.label}"
        if children:
            line += " -> " + ",".join(children)
        lines.append(line)
    return lines


class TreePatternOccurrenceCount(Task):
    summary = "Count all rooted embeddings of a small ordered labeled pattern tree inside a larger ordered labeled host where each pattern node maps to a same-label host node and its children occupy distinct ordered child-subtrees, with wildcard-subtree labels allowed; answer is the integer occurrence count."
    design_choice = "Answer as integer count of all rooted embeddings, with host and pattern both given as adjacency lists with node labels."
    config_cls = TreePatternCountConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        alpha = cfg.label_alpha
        tgt = random.choice(TARGETS)
        best = None
        best_dist = 1 << 31
        for _ in range(400):
            host = _make_random_tree(cfg.host_nodes, alpha)
            pattern = _make_ordered_pattern(cfg.pattern_nodes, alpha)
            count = _count_embeddings(host, pattern)
            if count == 0 and count != tgt:
                continue
            if tgt == 0:
                if count == 0:
                    break
                continue
            if max(tgt - 1, 1) <= count <= tgt + 2:
                break
            if count > 0:
                dist = abs(count - tgt)
                if dist < best_dist:
                    best = (host, pattern, count)
                    best_dist = dist
        else:
            if best is None:
                host = _make_random_tree(cfg.host_nodes, alpha)
                pattern = _make_ordered_pattern(cfg.pattern_nodes, alpha)
                count = _count_embeddings(host, pattern)
            else:
                host, pattern, count = best
        assert isinstance(count, int) and count >= 0
        assert count == _brute_force(host, pattern), "gold mismatch"
        return self._entry(host, pattern, count)

    def _entry(self, host, pattern, count):
        host_adj = _render_adjacency(host)
        pattern_adj = _render_adjacency(pattern)
        metadata = {
            "host": host_adj,
            "pattern": pattern_adj,
            "count": count,
        }
        return Entry(metadata=metadata, answer=str(count))

    def score_answer(self, answer, entry):
        got = parse_count(answer)
        if got is None:
            return 0.0
        return 1.0 if got == int(entry.answer) else 0.0

    def render_prompt(self, metadata):
        host = "\n".join("  " + ln for ln in metadata["host"])
        pattern = "\n".join("  " + ln for ln in metadata["pattern"])
        return (
            "An ordered tree is given as adjacency lists, one line per node: "
            "\"<index> <label> -> <child-index>,<child-index>\" in left-to-right "
            "child order (root is index 0, labels are single letters). A pattern "
            "label '*' matches any host label. Count every rooted embedding of the "
            "pattern tree into the host: an injective map of pattern nodes to host "
            "nodes where each pattern node maps to a host node of the same label and "
            "the children of every pattern node occupy pairwise distinct "
            "child-subtrees of the host image, in the given order. Two embeddings "
            "that differ at any node position are counted separately.\n"
            f"Host tree:\n{host}\n"
            f"Pattern tree:\n{pattern}\n"
            "How many rooted embeddings are there? Answer with the integer count only."
        )


def parse_count(answer):
    try:
        return int(str(answer).strip())
    except ValueError:
        return None


def _extract_nodes(adj):
    nodes = []
    for ln in adj:
        left, _, right = ln.partition(" -> ")
        parts = left.split()
        idx = int(parts[0])
        label = parts[1]
        children = [int(x) for x in right.split(",")] if right else []
        nodes.append((idx, label, children))
    return nodes


def _rebuild(adj):
    raw = _extract_nodes(adj)
    nodes = [_Node(lb) for _, lb, _ in raw]
    mapping = {idx: j for j, (idx, _, _) in enumerate(raw)}
    for j, (_, _, children) in enumerate(raw):
        for c in children:
            nodes[j].children.append(nodes[mapping[c]])
    return nodes


def _count_from_metadata(metadata):
    host = _rebuild(metadata["host"])
    pattern = _rebuild(metadata["pattern"])
    return _count_embeddings(host, pattern)

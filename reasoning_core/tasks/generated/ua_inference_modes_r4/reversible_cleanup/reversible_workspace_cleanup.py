import heapq
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'reversible_workspace_cleanup (variant 2 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_inference_modes_r4/reversible_workspace_cleanup',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1705404348,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class WorkspaceConfig(Config):
    n_leaves: int = 3
    leaf_max: int = 7
    int_max: int = 10
    int_min: int = 1
    base_min: int = 1

    def apply_difficulty(self, level):
        self.n_leaves = 3 + 2 * level
        self.leaf_max = 5 + 3 * level
        self.int_max = 7 + 5 * level


def _build(n_leaves, leaf_max, int_max, int_min, base_min):
    nodes = []
    counter = [0]

    def new_node(weight, left=-1, right=-1, leaf=False):
        idx = counter[0]
        nodes.append({"w": int(weight), "l": int(left), "r": int(right), "leaf": bool(leaf)})
        counter[0] += 1
        return idx

    def gen(leaves):
        if leaves == 1:
            return new_node(random.randint(base_min, leaf_max), leaf=True)
        lsz = random.randint(1, leaves - 1)
        left = gen(lsz)
        right = gen(leaves - lsz)
        return new_node(random.randint(int_min, int_max), left, right)

    root = gen(n_leaves)
    return nodes, root


def su_needed(nodes, idx):
    nd = nodes[idx]
    if nd["leaf"]:
        return nd["w"]
    lreg = su_needed(nodes, nd["l"])
    rreg = su_needed(nodes, nd["r"])
    lw = nodes[nd["l"]]["w"]
    rw = nodes[nd["r"]]["w"]
    peak_a = max(lreg, lw + rreg)
    peak_b = max(rreg, rw + lreg)
    return max(min(peak_a, peak_b), nd["w"])


def _total(nodes, mask):
    t = 0
    for i, nd in enumerate(nodes):
        if (mask >> i) & 1:
            t += nd["w"]
    return t


def brute_needed(nodes, root):
    n = len(nodes)
    goal = 1 << root
    dist = {0: 0}
    heap = [(0, 0)]
    while heap:
        peak, mask = heapq.heappop(heap)
        if peak > dist.get(mask, 1 << 60):
            continue
        if mask & goal:
            return peak
        for i, nd in enumerate(nodes):
            if nd["leaf"] and not ((mask >> i) & 1):
                nm = mask | (1 << i)
                npk = max(peak, _total(nodes, nm))
                if npk < dist.get(nm, 1 << 60):
                    dist[nm] = npk
                    heapq.heappush(heap, (npk, nm))
        for i, nd in enumerate(nodes):
            if not nd["leaf"] and not ((mask >> i) & 1):
                if ((mask >> nd["l"]) & 1) and ((mask >> nd["r"]) & 1):
                    nm = (mask & ~((1 << nd["l"]) | (1 << nd["r"]))) | (1 << i)
                    npk = max(peak, _total(nodes, nm))
                    if npk < dist.get(nm, 1 << 60):
                        dist[nm] = npk
                        heapq.heappush(heap, (npk, nm))
    return None


def _verify(nodes, root):
    gold = su_needed(nodes, root)
    if len(nodes) <= 11:
        b = brute_needed(nodes, root)
        if b != gold:
            raise RuntimeError("verifier mismatch: su=%r brute=%r" % (gold, b))
    return gold


def _render(nodes, root):
    lines = []
    order = list(range(len(nodes) - 1, -1, -1))
    for i in order:
        nd = nodes[i]
        if nd["leaf"]:
            lines.append("value %d (size %d): base material" % (i, nd["w"]))
        else:
            lines.append("value %d (size %d): combine value %d and value %d"
                         % (i, nd["w"], nd["l"], nd["r"]))
    prompt = (
        "We maintain a workspace holding intermediate results. Every value that is "
        "present consumes workspace equal to its size in resource tokens. Base "
        "materials are provided directly: loading one makes it resident and "
        "consumes its size. Combining two values replaces both of their tokens "
        "with the combined value's tokens, and you may drop a resident value "
        "when it is no longer needed. Using the Sethi-Ullman / tree register "
        "allocation order, compute the minimal peak number of resource tokens "
        "that are resident at any one moment needed to produce the root value.\n"
        + "\n".join(lines)
        + "\nThe answer is one integer: the minimal peak token count."
    )
    return prompt


class ReversibleCleanupV2(Task):
    task_name = "reversible_cleanup"
    summary = ("Plan creation and erasure of intermediate binary-operation results "
               "when combination and loading both require their operands or the "
               "free base materials to remain present; vary tree shapes, token "
               "sizes and shared subtree dependencies, returning the shortest "
               "clean computation as the minimal peak resident token count.")
    design_choice = ("Encode the workspace as a multiset of resource tokens with "
                     "capacities, where each step consumes and produces tokens; "
                     "the answer is a minimal token-count plan.")
    config_cls = WorkspaceConfig

    def generate_entry(self):
        cfg = self.config
        nodes = None
        root = None
        for _ in range(200):
            nodes, root = _build(cfg.n_leaves, cfg.leaf_max, cfg.int_max,
                                 cfg.int_min, cfg.base_min)
            try:
                gold = _verify(nodes, root)
            except RuntimeError:
                continue
            if gold >= 0:
                break
        if nodes is None:
            raise RuntimeError("could not build a valid instance")
        meta = {"nodes": nodes, "root": int(root), "gold": int(gold)}
        return Entry(metadata=meta, answer=str(int(gold)))

    def render_prompt(self, metadata):
        return _render(metadata["nodes"], metadata["root"])

    def score_answer(self, answer, entry):
        gold = entry.metadata["gold"]
        if isinstance(answer, str):
            answer = answer.strip()
        try:
            val = int(answer)
        except (TypeError, ValueError):
            return 0.0
        return 1.0 if val == gold else 0.0

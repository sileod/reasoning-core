import random
from collections import deque
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class ArcConsistencyConfig(Config):
    domain_size: int = 4
    num_vars: int = 4
    extra_density: float = 0.4
    wipeout_prob: float = 0.5

    def apply_difficulty(self, level):
        self.num_vars = stochastic_rounding(self.num_vars + 2 * level)
        self.domain_size = min(7, int(self.domain_size + self.domain_size * 0.25 * level))
        self.extra_density = min(0.8, self.extra_density + 0.05 * level)
        self.wipeout_prob = 0.5


def _propagate(domains, neighbors, allowed):
    domains = {v: set(d) for v, d in domains.items()}
    work = deque()
    for xi in neighbors:
        for xj in neighbors[xi]:
            work.append((xi, xj))
    while work:
        xi, xj = work.popleft()
        if not domains[xi]:
            continue
        if not domains[xj]:
            domains[xi] = set()
            for xk in neighbors[xi]:
                if xk != xj:
                    work.append((xk, xi))
            continue
        survived = set()
        removed = False
        for a in domains[xi]:
            viable = False
            for b in domains[xj]:
                if (a, b) in allowed.get((xi, xj), set()):
                    viable = True
                    break
            if viable:
                survived.add(a)
            else:
                removed = True
        if not survived:
            domains[xi] = set()
            for xk in neighbors[xi]:
                if xk != xj:
                    work.append((xk, xi))
        elif removed:
            domains[xi] = survived
            for xk in neighbors[xi]:
                if xk != xj:
                    work.append((xk, xi))
    return domains


class ArcConsistencyReduction(Task):
    summary = "Propagate binary allowed-pair constraints over small finite domains until arc-consistent, returning every variable's surviving sorted domain or the variable where wipeout occurs."
    config_cls = ArcConsistencyConfig

    def generate_entry(self):
        cfg = self.config
        num_vars = int(cfg.num_vars)
        domain_size = int(cfg.domain_size)

        while True:
            want_wipeout = random.random() < cfg.wipeout_prob

            n = random.randint(max(3, num_vars - 1), num_vars) if want_wipeout else num_vars
            if want_wipeout:
                k = random.randint(2, 3)
                m = random.randint(2, max(3, n - k))
            else:
                k = 0
                m = n

            domains = {}
            anchors = {}
            for v in range(m):
                size = random.randint(1, min(domain_size, num_vars))
                domains[v] = list(range(size))
                anchors[v] = random.choice(domains[v])

            neighbors = {v: [] for v in domains}
            edges = []
            for v in range(m - 1):
                neighbors[v].append(v + 1)
                neighbors[v + 1].append(v)
                edges.append((v, v + 1))
            for i in range(m):
                for j in range(i + 1, m):
                    if j == i + 1:
                        continue
                    if random.random() < cfg.extra_density:
                        neighbors[i].append(j)
                        neighbors[j].append(i)
                        edges.append((i, j))

            allowed = {}
            for (i, j) in edges:
                pairs = {(anchors[i], anchors[j])}
                for a in domains[i]:
                    for b in domains[j]:
                        if random.random() < 0.35:
                            pairs.add((a, b))
                pairs = sorted(pairs)
                allowed[(i, j)] = pairs
                allowed[(j, i)] = [(b, a) for (a, b) in pairs]

            if want_wipeout:
                for v in range(m, m + k):
                    domains[v] = [0]
                    neighbors[v] = []
                for v in range(m, m + k - 1):
                    a = v
                    b = v + 1
                    neighbors[a].append(b)
                    neighbors[b].append(a)
                    allowed[(a, b)] = []
                    allowed[(b, a)] = []

            result = _propagate(domains, neighbors, allowed)
            wiped = sorted(v for v in domains if not result[v])

            if want_wipeout:
                if not wiped:
                    continue
                answer = ("wipeout", wiped)
            else:
                if wiped:
                    continue
                answer = ("domains", [sorted(result[v]) for v in range(num_vars)])

            merged_domains_full = {str(v): sorted(d) for v, d in domains.items()}
            allowed_render = {}
            for k in sorted(allowed.keys(), key=lambda kk: (kk[0], kk[1])):
                if k[0] < k[1]:
                    allowed_render[f"{k[0]}-{k[1]}"] = sorted(set(allowed[k]))
            adj = {str(k): sorted(v) for k, v in neighbors.items()}

            if answer[0] == "domains":
                answer_str = "|".join(",".join(str(x) for x in sd) for sd in answer[1])
            else:
                answer_str = "w:" + ",".join(str(x) for x in answer[1])

            metadata = {
                "domains": merged_domains_full,
                "neighbors": adj,
                "allowed": allowed_render,
                "answer_kind": answer[0],
                "answer": answer[1],
                "answer_str": answer_str,
            }

            return Entry(metadata=metadata, answer=answer_str)

    def render_prompt(self, metadata):
        lines = []
        lines.append(
            "We have finite-domain variables and binary constraints, each constraint "
            "listing which pairs of values are allowed together. Apply arc-consistency "
            "(AC-3 style) by removing values that have no supporting partner in a "
            "neighbour's domain, and keep propagating until the network stops changing."
        )
        lines.append("Variables and their current domains:")
        n = len(metadata["domains"])
        for i in range(n):
            d = metadata["domains"][str(i)] if str(i) in metadata["domains"] else metadata["domains"][i]
            lines.append(f"  x{i}: {{{', '.join(str(x) for x in d)}}}")
        lines.append("Constraints, as allowed pairs 'a|b' meaning x_i=a with x_j=b:")
        sorted_keys = sorted(metadata["allowed"].keys(), key=lambda k: tuple(int(x) for x in k.split("-")))
        for key in sorted_keys:
            i, j = (int(x) for x in key.split("-"))
            pairs = metadata["allowed"][key]
            if pairs:
                pair_str = "; ".join(f"{u}|{v}" for (u, v) in pairs)
            else:
                pair_str = "none (no pairs allowed at all)"
            lines.append(f"  x{i}--x{j}: {pair_str}")
        lines.append("")
        if metadata["answer_kind"] == "wipeout":
            lines.append(
                "After full propagation some variables' domains become empty (a "
                "wipeout). Give the sorted comma-separated indices of exactly the "
                "variables whose domain is empty at the arc-consistent fixed point."
            )
            lines.append(
                "Answer format: the letter 'w', a colon, then the sorted indices, e.g. w:1,4"
            )
        else:
            lines.append(
                "Give every variable's surviving domain after arc-consistency, as "
                "comma-separated sorted values per variable, variables joined by '|' "
                "in index order. An empty domain is written as nothing between bars."
            )
            lines.append(
                "Answer format example: with x0={0,2}, x1 empty, x2={1}, the answer is: 0,2||1"
            )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        answer = answer.strip()
        gold = entry.metadata["answer_str"]
        if answer == gold:
            return 1.0
        kind = entry.metadata["answer_kind"]
        if kind == "wipeout":
            return 0.0
        parts = answer.split("|")
        expected = gold.split("|")
        if len(parts) != len(expected):
            return 0.0
        for p, g in zip(parts, expected):
            pvals = [int(x) for x in p.split(",") if x != ""]
            gvals = [int(x) for x in g.split(",") if x != ""]
            if pvals != gvals:
                return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'arc_consistency_reduction (draw 1 of 1)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_compositional_generalization_r1/arc_consistency_reduction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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

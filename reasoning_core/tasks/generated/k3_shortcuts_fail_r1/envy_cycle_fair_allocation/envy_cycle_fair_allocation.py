"""Envy-freeness up to one item via the envy-cycle elimination algorithm."""

import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'envy_cycle_fair_allocation (draw 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r1/envy_cycle_fair_allocation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


@dataclass
class EnvyCycleConfig(Config):
    n_agents: int = 3
    n_items: int = 4
    val_range: int = 10

    def apply_difficulty(self, level):
        self.n_agents = 3 + level
        self.n_items = (3 + level) * 2
        self.val_range = 6 + level


def _make_valuations(n_agents, n_items, val_range):
    vals = []
    for _ in range(n_agents):
        row = [random.randint(0, val_range) for _ in range(n_items)]
        vals.append(row)
    return vals


def _envy_graph(allocation, valuations, n_agents, n_items):
    """adjacency[i] = list of j that i envies (values j's bundle > own)."""
    own = []
    for a in range(n_agents):
        bundle = [i for i in range(n_items) if allocation[i] == a]
        own.append(sum(valuations[a][i] for i in bundle))
    adj = [[] for _ in range(n_agents)]
    for a in range(n_agents):
        for b in range(n_agents):
            if a != b:
                b_bundle = [i for i in range(n_items) if allocation[i] == b]
                val_b = sum(valuations[a][i] for i in b_bundle)
                if val_b > own[a]:
                    adj[a].append(b)
    return adj


def _find_cycle(n_agents, adj):
    color = [0] * n_agents
    parent = [-1] * n_agents
    cycle = None

    def dfs(u):
        nonlocal cycle
        color[u] = 1
        for v in adj[u]:
            if cycle is not None:
                return
            if color[v] == 0:
                parent[v] = u
                dfs(v)
            elif color[v] == 1:
                seg = []
                cur = u
                while cur != v:
                    seg.append(cur)
                    cur = parent[cur]
                seg.append(v)
                seg.append(u)
                cycle = seg
                return
        color[u] = 2

    for node in range(n_agents):
        if color[node] == 0:
            dfs(node)
            if cycle is not None:
                break
    return cycle


def _swap_along_cycle(cycle, allocation, n_items):
    items = list(range(n_items))
    for it in items:
        owner = allocation[it]
        if owner in cycle:
            idx = cycle.index(owner)
            nxt = cycle[(idx + 1) % len(cycle)]
            allocation[it] = nxt


def _alloc_from_round_robin(vals, n_agents, n_items):
    order = list(range(n_agents))
    allocation = [None] * n_items
    for turn in range(n_items):
        agent = order[turn % n_agents]
        avail = [i for i in range(n_items) if allocation[i] is None]
        pick = avail[random.randrange(len(avail))]
        allocation[pick] = agent
    return allocation


def _top_cycle_elimination(allocation, valuations, n_agents, n_items):
    while True:
        adj = _envy_graph(allocation, valuations, n_agents, n_items)
        cycle = _find_cycle(n_agents, adj)
        if cycle is None:
            return list(allocation)
        _swap_along_cycle(cycle, allocation, n_items)


class EnvyCycleFairAllocation(Task):
    summary = (
        "Allocate indivisible goods to agents with additive valuations so the "
        "outcome is envy-free up to one item: sequence picks in round-robin "
        "order, then detect and cancel envy via trades along envy cycles; "
        "answer is the item-to-agent assignment."
    )
    design_choice = (
        "Present the initial allocation as a sequence of picks made by agents "
        "in a round-robin order, and require the solver to output the final "
        "assignment after resolving all envy cycles."
    )
    config_cls = EnvyCycleConfig

    def generate_entry(self):
        for _ in range(1000):
            n_agents = self.config.n_agents
            n_items = (self.config.n_items)
            vals = _make_valuations(n_agents, n_items, self.config.val_range)
            init = _alloc_from_round_robin(vals, n_agents, n_items)
            final = _top_cycle_elimination(list(init), vals, n_agents, n_items)
            assert n_agents >= 1 and n_items >= n_agents
            if _is_ef1(final, vals, n_agents, n_items):
                return Entry(
                    metadata={
                        "n_agents": n_agents,
                        "n_items": n_items,
                        "valuations": vals,
                        "round_robin_order": list(range(n_agents)),
                        "initial_allocation": init,
                        "final_allocation": final,
                    },
                    answer=_format_assignment(final),
                )
        raise RuntimeError("failed to generate EF1 instance")

    def render_prompt(self, metadata):
        n_agents = metadata["n_agents"]
        n_items = metadata["n_items"]
        vals = metadata["valuations"]
        init = metadata["initial_allocation"]
        lines = []
        lines.append(
            "Agents choose items in round-robin order. On each turn, an agent "
            "takes one of the remaining items (the choice is arbitrary)."
        )
        lines.append("")
        lines.append("Valuations (rows are agents, columns are items):")
        agent_labels = ",".join("A{}".format(a) for a in range(n_agents))
        lines.append("items:  " + " ".join("I{}".format(i) for i in range(n_items)))
        for a in range(n_agents):
            lines.append(
                "A{}:    ".format(a)
                + " ".join(str(vals[a][i]) for i in range(n_items))
            )
        lines.append("")
        lines.append(
            "Pick order is {} (first round), repeating until every item is "
            "taken.".format(",".join("A{}".format(a) for a in range(n_agents)))
        )
        lines.append(
            "This produces the initial item-to-agent allocation "
            "(item label: owning agent): " + _format_assignment(init)
        )
        lines.append("")
        lines.append(
            "Now resolve envy: recompute which agent envies which (an agent "
            "envies you if it values your bundle strictly more than its own), "
            "then apply the envy-cycle elimination algorithm -- repeatedly "
            "find a directed cycle in the envy graph and rotate every item "
            "along the cycle one step (the cycle owner passes its items to the "
            "next agent). Repeat until no envy cycle remains."
        )
        lines.append("")
        lines.append(
            "Give the final envy-free-up-to-one-item allocation as "
            "item-to-agent pairs in increasing item-index order, each of the "
            "form I{item}:A{agent}, joined by spaces."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        expected = _format_assignment(entry.metadata["final_allocation"])
        return 1.0 if _normalize(answer) == _normalize(expected) else 0.0


def _normalize(s):
    return " ".join(_clean_pair(p) for p in _tokenize(s))


def _tokenize(s):
    if not isinstance(s, str):
        return []
    import re
    return re.findall(r"[A-Za-z]+\d+", s)


def _clean_pair(p):
    import re
    m = re.fullmatch(r"([A-Za-z]+)(\d+)", p)
    if not m:
        return p
    return "{}:{}".format(m.group(1), m.group(2))


def _format_assignment(alloc):
    parts = []
    for i, owner in enumerate(alloc):
        parts.append("I{}:A{}".format(i, owner))
    return " ".join(parts)


def _is_ef1(final, vals, n_agents, n_items):
    bundles = [[] for _ in range(n_agents)]
    for i in range(n_items):
        bundles[final[i]].append(i)
    own = []
    for a in range(n_agents):
        own.append(sum(vals[a][i] for i in bundles[a]))
    for i in range(n_agents):
        for j in range(n_agents):
            if i == j:
                continue
            best_removed = -1
            for removed in bundles[j]:
                bj = sum(vals[i][x] for x in bundles[j] if x != removed)
                if bj > best_removed:
                    best_removed = bj
            if best_removed > own[i]:
                return False
    return True

"""Filter action traces under directed, non-transitive information-flow policies."""

import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'intransitive_information_purge (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dependence_relevance_r4/intransitive_information_purge',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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


@dataclass
class PurgeConfig(Config):
    n_agents: int = 4
    n_actions: int = 6
    edge_prob: float = 0.5

    def apply_difficulty(self, level):
        self.n_agents = 3 + level
        self.n_actions = 4 + 2 * level
        self.edge_prob = min(0.5 + 0.05 * level, 0.8)


def _purged_indices(actions, n_agents):
    """Return indices of actions whose source can reach the observer via a path
    of later actions' permitted edges. Edges are active only after they appear."""
    keep = []
    observer = n_agents - 1
    n = len(actions)
    for i in range(n):
        src, _ = actions[i]
        reachable = {src}
        changed = True
        while changed:
            changed = False
            for j in range(i + 1, n):
                a, b = actions[j]
                if a in reachable and b not in reachable:
                    reachable.add(b)
                    changed = True
        if observer in reachable:
            keep.append(i)
    return keep


class IntransitiveInformationPurge(Task):
    summary = ("Filter action traces under directed information-flow policies where permission "
               "need not be transitive; retain actions that can reach an observer through later "
               "permitted transmissions; answer the retained subsequence.")
    design_choice = ("Represent policies as a directed graph among agents; each action has a "
                     "source and listener; retain actions whose source can reach the observer via "
                     "a path of later actions' permitted edges.")
    config_cls = PurgeConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_agents
        while True:
            actions = []
            for _ in range(cfg.n_actions):
                s = random.randrange(n - 1)
                o = random.randrange(1, n)
                actions.append((s, o))
            keep = _purged_indices(actions, n)
            if len(keep) == 0:
                continue
            break
        metadata = {
            "agents": [f"A{i}" for i in range(n)],
            "actions": [[f"A{s}", f"A{o}"] for (s, o) in actions],
            "observer": f"A{n - 1}",
            "keep": keep,
        }
        answer = ",".join(str(i) for i in keep)
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        lines.append("A system tracks information flow among agents "
                     + ", ".join(metadata["agents"][:-1]) + " and observer "
                     + metadata["observer"] + ".")
        lines.append("Actions happen in order, one per line. Action k has a source and a "
                     "listener: 'source -> listener'. The edge it permits is in force only "
                     "after that action has happened, for every later action.")
        lines.append("Permitted edges are directed and NOT transitive: an edge A->B and an "
                     "edge B->C does not permit A->C unless a later action permits A->C "
                     "directly.")
        lines.append("Retain every action k whose source can reach the observer by repeatedly "
                     "following the permitted edges of actions with index greater than k. "
                     "Answer the retained action indices in increasing order as a "
                     "comma-separated list, e.g. '1,3'.")
        for i, (s, o) in enumerate(metadata["actions"]):
            lines.append(f"{i}: {s} -> {o}")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        ans = answer.strip()
        if ans == gold:
            return 1.0
        return 0.0

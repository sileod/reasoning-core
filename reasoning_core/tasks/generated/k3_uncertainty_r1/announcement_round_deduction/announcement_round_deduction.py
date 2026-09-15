"""Public-round deduction: agents with hidden binary hats announce ignorance until someone deduces their own."""

import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class AnnouncementRoundDeductionV3Config(Config):
    num_agents: int = 7
    max_rounds: int = 7

    def apply_difficulty(self, level):
        self.num_agents = 7 + int(level * 0.7)
        self.max_rounds = 7 + int(level * 0.7)


def _initial_worlds(n):
    """All hat assignments (Red=1, Blue=0) consistent with the public fact:
    'at least one agent wears a Red hat' (muddy-children initial announcement)."""
    return [tuple((bit >> i) & 1 for i in range(n)) for bit in range(1, 2 ** n)]


def _simulate(n, world, max_rounds):
    """Return (first_agent_index, round_of_first_deduction) or None if never.

    Round 1.. : whoever can name their own hat says so; worlds inconsistent with a
    unanimous 'nobody knows' are exactly those where some agent's value was pinned.
    """
    S = set(_initial_worlds(n))
    world = tuple(world)
    for r in range(1, max_rounds + 1):
        # For each agent a, group worlds by the view a has (all hats except a's own),
        # recording the set of values a's own hat takes within a group.
        views = []
        for a in range(n):
            vals = {}
            for w in S:
                view = w[:a] + w[a + 1:]
                vals.setdefault(view, set()).add(w[a])
            views.append(vals)
        knows = set()
        for w in S:
            for a in range(n):
                if len(views[a][w[:a] + w[a + 1:]]) == 1:
                    knows.add(w)
                    break
        if world in knows:
            forced = [a for a in range(n) if len(views[a][world[:a] + world[a + 1:]]) == 1]
            return (min(forced), r)
        S = S - knows
        if not S:
            return None
    return None


class AnnouncementRoundDeduction(Task):
    summary = "Simulate public rounds in which every agent who still cannot name their own unseen attribute says so at once; eliminate inconsistent worlds after each round and answer which agent deduces their attribute and on which round."

    config_cls = AnnouncementRoundDeductionV3Config
    task_version = 2

    def generate_entry(self):
        n = self.config.num_agents
        R = self.config.max_rounds
        while True:
            world = tuple(random.randint(0, 1) for _ in range(n))
            if all(v == 0 for v in world):
                continue
            result = _simulate(n, world, R)
            if result is None:
                continue
            agent, rnd = result
            assert 0 <= agent < n and 1 <= rnd <= R
            return Entry(
                metadata={
                    "num_agents": n,
                    "world": [int(v) for v in world],
                    "agent": int(agent),
                    "round": int(rnd),
                },
                answer=f"A{agent} on round {rnd}",
            )

    def render_prompt(self, metadata):
        n = metadata["num_agents"]
        world = metadata["world"]
        parts = []
        for i in range(n):
            color = "Red" if world[i] else "Blue"
            if i == metadata["agent"]:
                parts.append(f"A{i} cannot see their own hat;")
            else:
                parts.append(f"A{i} wears a {color} hat;")
        seen = " ".join(parts)
        return (
            f"Agents A0..A{n-1} each wear a hat that is either Red or Blue; each agent sees "
            f"everyone else's hat but not their own. It is publicly announced that at least one "
            f"agent wears a Red hat. In each round, every agent who still cannot name their own "
            f"hat color says 'I don't know' all at once, and then worlds inconsistent with that "
            f"announcement are dismissed. The hats: {seen} "
            f"After how many rounds does the first agent deduce their own hat color, and which "
            f"agent (lowest index among those who deduce in that round) is it? "
            f"Answer as \"A<index> on round <number>\", e.g. \"A0 on round 1\"."
        )

    def distractor_candidates(self, entry):
        n = entry.metadata["num_agents"]
        g = entry.metadata["agent"]
        r = entry.metadata["round"]
        cands = []
        for rr in (r + 1, r - 1, r + 2):
            if rr >= 1:
                cands.append(f"A{g} on round {rr}")
        cands.append(f"A{g} on round {r}")
        for gg in ((g + 1) % n, (g - 1) % n):
            cands.append(f"A{gg} on round {r}")
        return cands

    def score_answer(self, answer, entry):
        parsed = _parse_answer(answer)
        if parsed is None:
            return 0.0
        agent, rnd = parsed
        if agent == entry.metadata["agent"] and rnd == entry.metadata["round"]:
            return 1.0
        return 0.0


def _parse_answer(text):
    m = re.fullmatch(r"A(\d+) on round (\d+)", str(text).strip())
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)))


TASK_META = {'parent_source_id': None,
 'idea': 'announcement_round_deduction (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_uncertainty_r1/announcement_round_deduction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1259343118,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

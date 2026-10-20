"""Plan with conjunctive and alternative prerequisites over finite action systems.

Levels increase graph size, prerequisite depth, unavailable actions, and OR prerequisites. An exact shortest-path
search supplies unambiguous labels even when several plans are valid. Ported from
tasksource.jev.procedural.goal_directed_planning; its level tables stop at 4.
"""
import random
from collections import deque
from dataclasses import dataclass

from reasoning_core.decision import Decision, pose
from reasoning_core.template import Config, Task

COUNTS = [str(i) for i in range(8)] + ["8 or more", "unreachable"]
N_ACTIONS = [3, 5, 7, 9, 12]
SEMANTICS = ("An action completes its associated step. It may be executed only if it is available, incomplete, "
             "every requires_all step is complete, and at least one requires_any step is complete (if the "
             "requires_any list is nonempty). Completed steps stay complete. The goal is reached when every "
             "listed goal step is complete. Minimize the number of newly executed actions; initially completed "
             "steps require no action. Executing actions already complete is not permitted.")


def _encode(state):
    tasks = state["steps"]
    names = {t["id"]: i for i, t in enumerate(tasks)}
    goal = sum(1 << names[x] for x in state["goal"])
    initial = sum(1 << i for i, t in enumerate(tasks) if t["completed"])
    rules = [(1 << i, sum(1 << names[x] for x in t["requires_all"]),
              sum(1 << names[x] for x in t["requires_any"]), t["available"])
             for i, t in enumerate(tasks)]
    return initial, goal, rules


def _successors(mask, rules, forbidden=-1):
    for i, (bit, all_bits, any_bits, available) in enumerate(rules):
        if (i != forbidden and available and not mask & bit and mask & all_bits == all_bits
                and (not any_bits or mask & any_bits)):
            yield i, mask | bit


def _shortest(state, start=None, forbidden=-1):
    initial, goal, rules = _encode(state)
    start = initial if start is None else start
    if start & goal == goal:
        return 0
    visited = {start}
    queue = deque([(start, 0)])
    while queue:
        mask, distance = queue.popleft()
        for _, after in _successors(mask, rules, forbidden):
            if after in visited:
                continue
            if after & goal == goal:
                return distance + 1
            visited.add(after)
            queue.append((after, distance + 1))
    return None


@dataclass
class GoalDirectedPlanningConfig(Config):
    def apply_difficulty(self, level):
        pass  # the generator reads the level


class GoalDirectedPlanning(Task):
    summary = ("Shortest plans over steps with requires_all/requires_any prerequisites, unavailable actions and "
               "multi-step goals; ask reachability, plan length, applicability, optimal-first and required actions.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or GoalDirectedPlanningConfig())

    def generate_entry(self, state_seed=None, question=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, level = random.Random(state_seed), min(self.config.level, 4)
        n = N_ACTIONS[level]
        names = [f"S{k}" for k in rng.sample(range(1, 90), n)]
        steps = []
        for i in range(n):
            parents = list(range(i))
            if level == 0 or i == 0:
                both = []
            elif level == 1:
                both = [i - 1] if rng.random() < 0.8 else []
            else:
                both = rng.sample(parents, min(len(parents), rng.randint(1, min(3, level))))
            any_of = []
            if level >= 3 and len(parents) >= 2 and rng.random() < 0.5:
                candidates = [j for j in parents if j not in both]
                if len(candidates) >= 2:
                    any_of = rng.sample(candidates, rng.randint(2, min(3, len(candidates))))
            completed = rng.random() < [0.0, 0.12, 0.2, 0.25, 0.16][level]
            available = rng.random() >= [0.0, 0.0, 0.07, 0.11, 0.13][level]
            steps.append({"id": names[i], "completed": completed, "available": available,
                          "requires_all": [names[j] for j in both],
                          "requires_any": [names[j] for j in any_of]})
        goal_indices = rng.sample(range(n // 2, n), 2 if level >= 3 and rng.random() < 0.45 else 1)
        for i in goal_indices:
            steps[i]["completed"] = False
        state = {"steps": steps, "goal": [names[i] for i in sorted(goal_indices)], "semantics": SEMANTICS}
        distance = _shortest(state)
        initial, _, rules = _encode(state)
        applicable = dict(_successors(initial, rules))
        probe = rng.randrange(n)
        if applicable and rng.random() < 0.65:
            probe = rng.choice(sorted(applicable))
        after_probe = _shortest(state, applicable[probe]) if probe in applicable else None
        optimal_first = distance is not None and probe in applicable and after_probe == distance - 1
        without_probe = _shortest(state, forbidden=probe)
        required = distance is not None and (without_probe is None or without_probe > distance)
        first_legal = steps[min(applicable, key=lambda i: int(steps[i]["id"][1:]))]["id"] if applicable else "none"
        options = [t["id"] for t in steps] + ["none"]
        name = steps[probe]["id"]
        questions = {
            "goal_reachable": Decision(distance is not None, type="noul", instructions=
                                       "Can all goal steps be completed from the initial state?"),
            "minimal_actions": Decision(9 if distance is None else min(distance, 8), type="score", criteria=COUNTS,
                                        instructions="How many newly executed actions are needed by a shortest "
                                                     "valid plan?"),
            "probe_applicable": Decision(probe in applicable, type="noul", instructions=
                                         f"Can {name} be executed immediately?"),
            "probe_optimal_first": Decision(optimal_first, type="noul", instructions=
                                            f"Can executing {name} first begin a shortest valid plan to the goal?"),
            "probe_required": Decision(required, type="noul", instructions=
                                       f"Must every shortest valid plan execute {name}?"),
            "first_legal_action": Decision(first_legal, criteria=dict.fromkeys(options), instructions=
                "Which currently executable action has the smallest numeric step ID? Choose none if no action "
                "is executable."),
        }
        return pose(questions, state, state_seed, question)

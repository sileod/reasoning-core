import random
from dataclasses import dataclass, field
from collections import deque

from reasoning_core.template import Config, Entry, Task


COMPLEMENT_FLAGS = ['a', 'b', 'c', 'd']


def _successors(state, action):
    state = set(state)
    if any(f not in state for f in action['requires']):
        return [state]
    if any(f in state for f in action['forbids']):
        return [state]
    outs = []
    for adds, clears in action['outcomes']:
        s = set(state)
        for f in adds:
            s.add(f)
        for f in clears:
            s.discard(f)
        outs.append(s)
    return outs


def _apply_to_belief(belief, action):
    nb = set()
    for st in belief:
        for ns in _successors(st, action):
            nb.add(frozenset(ns))
    return frozenset(nb)


def _goal_ok_all(belief, goal):
    return all(goal <= st for st in belief)


def _find_plan(actions, initials, budget, goal):
    start_belief = frozenset(frozenset(init) for init in initials)
    if _goal_ok_all(start_belief, goal):
        return ()
    start = (start_belief, budget)
    visited = {start}
    q = deque([(start, ())])
    while q:
        (belief, res), plan = q.popleft()
        for a in actions:
            if a['cost'] > res:
                continue
            nres = res - a['cost']
            if nres < 0:
                continue
            nb = _apply_to_belief(belief, a)
            ns = (nb, nres)
            if ns in visited:
                continue
            nplan = plan + (a['name'],)
            if _goal_ok_all(nb, goal):
                return nplan
            visited.add(ns)
            q.append((ns, nplan))
    return None


def _random_subset(flags, rng=random, lo=0, hi=None):
    if hi is None:
        hi = len(flags)
    k = rng.randrange(lo, hi + 1)
    return sorted(rng.sample(flags, k))


@dataclass
class ConformantActionConfig(Config):
    num_flags: int = 3
    num_initial: int = 2
    num_actions: int = 3
    budget: int = 4
    min_plan: int = 1
    max_plan: int = 3
    branches: int = 1
    try_limit: int = 2000

    def apply_difficulty(self, level):
        self.num_flags = 3 if level < 4 else 4
        self.num_initial = 2 + (1 if level >= 2 else 0) + (1 if level >= 4 else 0)
        self.num_actions = 3 + (1 if level >= 2 else 0) + (1 if level >= 4 else 0)
        self.budget = 4 + level
        self.branches = 2 if level >= 3 else 1
        self.min_plan = 1 if level < 2 else 2
        self.max_plan = max(1, min(level, 2 + level))


class ConformantActionSynthesis(Task):
    summary = ("Plan across hidden initial states and nondeterministic effects without "
               "observations, including irreversible actions and resource caps; return a "
               "shortest fixed action sequence guaranteed to reach the goal.")
    design_choice = ("Encode initial-state uncertainty as a set of flags in the state vector, "
                     "with actions guarded by flags; answers are strings like 'A;B;C' over a "
                     "fixed action alphabet.")
    config_cls = ConformantActionConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(cfg.try_limit):
            flags = COMPLEMENT_FLAGS[:cfg.num_flags]
            initials = []
            seen = set()
            while len(initials) < cfg.num_initial:
                st = frozenset(_random_subset(flags))
                if st not in seen:
                    seen.add(st)
                    initials.append(sorted(st))
            goal_flags = _random_subset(flags, lo=1, hi=max(1, cfg.num_flags - 1))
            goal = frozenset(goal_flags)

            actions = []
            names = [chr(ord('A') + i) for i in range(cfg.num_actions)]
            for name in names:
                requires = _random_subset(flags) if random.random() < 0.5 else []
                forbids = _random_subset(flags) if random.random() < 0.35 else []
                max_branch = cfg.branches
                nb = random.randint(1, max_branch)
                outcomes = []
                for _b in range(nb):
                    adds = _random_subset(flags) if random.random() < 0.7 else []
                    clears = _random_subset(flags) if random.random() < 0.3 else []
                    outcomes.append((adds, clears))
                cost = random.randint(1, 2)
                actions.append({
                    'name': name,
                    'requires': requires,
                    'forbids': forbids,
                    'outcomes': outcomes,
                    'cost': cost,
                })

            plan = _find_plan(actions, initials, cfg.budget, goal)
            if plan is None:
                continue
            if not (cfg.min_plan <= len(plan) <= cfg.max_plan):
                continue

            total_cost = sum(a['cost'] for a in actions if a['name'] in set(plan))
            if total_cost > cfg.budget:
                continue

            serializable_actions = [
                {
                    'name': a['name'],
                    'requires': list(a['requires']),
                    'forbids': list(a['forbids']),
                    'outcomes': [[list(adds), list(clears)] for adds, clears in a['outcomes']],
                    'cost': a['cost'],
                }
                for a in actions
            ]
            answer = ';'.join(plan)
            metadata = {
                'flags': list(flags),
                'initials': [list(i) for i in initials],
                'actions': serializable_actions,
                'budget': cfg.budget,
                'goal': goal_flags,
                'answer': answer,
            }
            entry = Entry(metadata=metadata, answer=answer)
            if self.score_answer(answer, entry) == 1:
                return entry
        raise RuntimeError("conformant_action_synthesis: could not generate a valid plan")

    def render_prompt(self, metadata):
        flags = metadata['flags']
        initial_lines = "\n".join(
            "  - {" + ", ".join(i) + "}"
            for i in metadata['initials']
        )
        action_lines = []
        for a in metadata['actions']:
            req = ", ".join(a['requires']) if a['requires'] else "none"
            forb = ", ".join(a['forbids']) if a['forbids'] else "none"
            outs = " | ".join(
                "{" + (", ".join(adds) if adds else "nothing") + " set, "
                + (", ".join(clears) if clears else "nothing") + " clear}"
                for adds, clears in a['outcomes']
            )
            action_lines.append(
                f"  {a['name']} (cost {a['cost']}, requires {req}, forbids {forb}): "
                f"possible outcomes are {outs}"
            )
        actions_text = "\n".join(action_lines)
        goal_text = ", ".join(metadata['goal'])
        return (
            f"You control a system with flags {', '.join(flags)}. Each flag is either set or "
            f"clear, and you get no observations, so you must act blind. The system starts in "
            f"exactly one of these hidden states (the listed flags are set, the rest are clear):\n"
            f"{initial_lines}\n"
            f"\n"
            f"Each available action is guarded by its 'requires' (flags that must be set) and "
            f"'forbids' (flags that must be clear) conditions, and does nothing if its guards are "
            f"not met. The listed possible outcomes are nondeterministic: exactly one occurs "
            f"whenever the action applies, and clearing a flag is irreversible.\n"
            f"{actions_text}\n"
            f"\n"
            f"Your total action cost may not exceed the resource budget of {metadata['budget']}.\n"
            f"\n"
            f"Find the shortest action sequence (fewest actions) that, no matter which hidden "
            f"start state or which nondeterministic outcome occurs, guarantees that flags "
            f"{goal_text} are all set. Answer as a semicolon-separated list of action names with "
            f"no spaces; for example 'A;B;C' means do A, then B, then C."
        )

    def score_answer(self, answer, entry):
        stripped = str(answer).strip()
        return 1.0 if stripped == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'conformant_action_synthesis (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_inference_modes_r4/conformant_action_synthesis',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

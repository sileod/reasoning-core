import random

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'planning_graph_mutex_expansion (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_non_local_structured_r4/planning_graph_mutex_expansion',
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


class PlanningGraphMutexConfig(Config):
    num_facts: int = 6
    num_actions: int = 6

    def apply_difficulty(self, level):
        base = PlanningGraphMutexConfig()
        self.num_facts = base.num_facts + level
        self.num_actions = base.num_actions + 2 * level


def _mutex_actions(fm, a, b):
    ca = set(a["add"]) | set(a["del"])
    cb = set(b["add"]) | set(b["del"])
    if (ca & cb) or (set(a["add"]) & set(b["del"])) or (set(b["add"]) & set(a["del"])):
        return True
    for x in set(a["pre"]) | ca:
        for y in set(b["pre"]) | cb:
            if (x, y) in fm:
                return True
    return False


def first_mutex_free_level(facts, init, actions, goal, max_level=14):
    facts = list(facts)
    n = len(facts)
    fm = set()
    present = [set(init)]

    def check(lev):
        if not set(goal).issubset(present[lev]):
            return False
        for i in range(len(goal)):
            for j in range(i + 1, len(goal)):
                if (goal[i], goal[j]) in fm:
                    return False
        return True

    if check(0):
        return 0
    for level in range(max_level):
        pl = present[level]
        acc = []
        for a in actions:
            pre = set(a["pre"])
            if not pre.issubset(pl):
                continue
            plist = list(a["pre"])
            ok = True
            for x in range(len(plist)):
                for y in range(x + 1, len(plist)):
                    if (plist[x], plist[y]) in fm:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                acc.append(a)
        amtx = {name: set() for name in (a["name"] for a in acc)}
        for i in range(len(acc)):
            for j in range(i + 1, len(acc)):
                if _mutex_actions(fm, acc[i], acc[j]):
                    amtx[acc[i]["name"]].add(acc[j]["name"])
                    amtx[acc[j]["name"]].add(acc[i]["name"])
        new_present = set(pl)
        for a in acc:
            new_present.update(a["add"])
        present.append(new_present)
        new_fm = set()
        for i in range(n):
            for j in range(i + 1, n):
                fi, fj = facts[i], facts[j]
                if fi not in new_present or fj not in new_present:
                    continue
                if (fi, fj) in fm:
                    new_fm.add((fi, fj))
                    new_fm.add((fj, fi))
                    continue
                inter = False
                for a in acc:
                    if (fi in a["add"] and fj in a["del"]) or (fi in a["del"] and fj in a["add"]):
                        inter = True
                        break
                if inter:
                    new_fm.add((fi, fj))
                    new_fm.add((fj, fi))
                    continue
                addp = [a for a in acc if fi in a["add"]]
                addq = [a for a in acc if fj in a["add"]]
                if addp and addq:
                    allm = all(
                        (x["name"] in amtx and y["name"] in amtx[x["name"]])
                        for x in addp for y in addq)
                    if allm:
                        new_fm.add((fi, fj))
                        new_fm.add((fj, fi))
        fm = new_fm
        if check(level + 1):
            return level + 1
    return -1


def _filler(cfg, facts, protected):
    free = [f for f in facts if f not in protected]
    if not free:
        return []
    acts = []
    for ai in range(cfg.num_actions):
        pre = sorted(random.sample(free, random.randint(0, min(2, len(free)))))
        adds = sorted(random.sample(free, random.randint(1, min(2, len(free)))))
        dels = sorted(random.sample(free, random.randint(0, min(1, len(free)))))
        acts.append({"name": "f%d" % ai, "pre": pre, "add": adds, "del": dels})
    return acts


def _chain(cfg, start, length, gate_name):
    facts = []
    ring = []
    for i in range(length):
        facts.append("p%d" % (start + i))
    gate = "p%d" % (start + length)
    facts.append(gate)
    actions = []
    for i, cf in enumerate(facts[:-1]):
        pre = [] if i == 0 else [facts[i - 1]]
        actions.append({"name": "c%d_%d" % (start, i), "pre": pre, "add": [cf], "del": []})
    actions.append({"name": gate_name, "pre": [facts[-2]] if length else [], "add": [gate], "del": []})
    return facts, actions, gate


def _construct(cfg, target):
    if target == 0:
        facts = ["p%d" % i for i in range(cfg.num_facts)]
        goal = sorted(random.sample(facts, 2))
        actions = _filler(cfg, facts, set(goal))
        return facts, set(facts), actions, goal
    if target == -1:
        facts = ["p%d" % i for i in range(cfg.num_facts)]
        g, h = facts[0], facts[1]
        actions = [
            {"name": "aG", "pre": [], "add": [g], "del": [h]},
            {"name": "aH", "pre": [], "add": [h], "del": [g]},
        ]
        actions += _filler(cfg, facts, {g, h})
        return facts, set(facts[2:]), actions, [g, h]
    facts_all = []
    actions = []
    chain_a, acts, g = _chain(cfg, 0, target - 1, "gA")
    facts_all += chain_a
    actions += acts
    b_start = len(chain_a)
    chain_b, acts, h = _chain(cfg, b_start, target - 1, "gB")
    facts_all += chain_b
    actions += acts
    facts = facts_all
    pad = cfg.num_facts - len(facts)
    if pad > 0:
        for i in range(pad):
            facts.append("q%d" % i)
    protected = set(facts_all) | {g, h}
    actions = actions + _filler(cfg, facts, protected)
    init = set(f for f in facts if f not in protected)
    return facts, init, actions, [g, h]


def _relabel(facts, init, actions, goal):
    order = list(facts)
    perm = {}
    shuffled = sorted(order, key=lambda _: random.random())
    for old, new in zip(order, shuffled):
        perm[old] = new
    rf = [perm[f] for f in facts]
    rinit = {perm[f] for f in init}
    racts = [{"name": a["name"],
              "pre": [perm[f] for f in a["pre"]],
              "add": [perm[f] for f in a["add"]],
              "del": [perm[f] for f in a["del"]]} for a in actions]
    rgoal = [perm[f] for f in goal]
    return rf, rinit, racts, rgoal


class PlanningGraphMutexExpansion(Task):
    summary = ("Grow a planning graph level-wise: add actions whose preconditions are "
               "present and pairwise non-mutex, propagate action and fact mutex relations; "
               "answer a goal's first present or first mutex-free level, or -1.")
    design_choice = ("Answer as an integer: the first level index (0-based) at which "
                     "all goal facts are present and pairwise non-mutex, else -1.")
    config_cls = PlanningGraphMutexConfig

    def _pick_target(self):
        lmax = min(self.config.num_facts // 2, 5)
        pool = [0] + list(range(1, lmax + 1)) + [-1]
        return random.choice(pool)

    def generate_entry(self):
        cfg = self.config
        for _ in range(40):
            target = self._pick_target()
            facts, init, actions, goal = _construct(cfg, target)
            facts, init, actions, goal = _relabel(facts, init, actions, goal)
            res = first_mutex_free_level(facts, init, actions, goal)
            if res == target:
                return Entry(metadata={
                    "facts": facts,
                    "init": sorted(init),
                    "actions": actions,
                    "goal": goal,
                    "answer": res,
                }, answer=str(res))
        raise RuntimeError("could not construct a valid planning graph instance")

    def render_prompt(self, metadata):
        lines = [
            "A planning graph over facts grows level by level; level zero holds exactly the "
            "initial facts. At each level an action is added only if all its preconditions are "
            "present at that level and are pairwise non-mutex. Two added actions are mutex if "
            "one interferes with the other (their add/delete sets overlap, or one deletes an add "
            "of the other), or if a precondition of one is mutex with a precondition or effect "
            "of the other. In the added level, fact p is mutex with fact q if one of the added "
            "actions adds p and deletes q (or adds q and deletes p), or if the pair was already "
            "mutex at the previous level, or if every added action that adds p is mutex with "
            "every added action that adds q. An already non-mutex pair of simultaneously present "
            "facts stays non-mutex at the next level.",
            "",
            "All facts: " + ", ".join(metadata["facts"]),
            "Initial facts: {" + ", ".join(sorted(metadata["init"])) + "}",
            "",
            "Actions (precondition -> adds; deletes):",
        ]
        for a in metadata["actions"]:
            lines.append(
                "  %s: pre {%s} -> add {%s}, del {%s}" % (
                    a["name"], ", ".join(a["pre"]), ", ".join(a["add"]), ", ".join(a["del"])))
        lines.append("")
        lines.append("Goal facts: {" + ", ".join(sorted(metadata["goal"])) + "}")
        lines.append("")
        lines.append("Report the 0-based level index of the first level at which all goal facts "
                     "are present and pairwise non-mutex. If no level ever satisfies this, "
                     "output -1.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        try:
            val = int(str(answer).strip())
        except (ValueError, TypeError):
            return 0.0
        return 1.0 if val == int(entry.metadata["answer"]) else 0.0

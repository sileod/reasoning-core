import random
from dataclasses import dataclass

from reasoning_core.template import Task, Entry, Config, edict


@dataclass
class EventConfigRecoveryConfig(Config):
    n_events: int = 4
    p_depend: float = 0.35
    max_conflicts: int = 1

    def apply_difficulty(self, level):
        self.n_events = 4 + int(level * 0.6)
        self.p_depend = 0.35 + 0.06 * level
        self.max_conflicts = 1 + int(level * 0.8)


def _reach_closure(n, depends):
    reach = [set(depends[i]) for i in range(n)]
    changed = True
    while changed:
        changed = False
        for i in range(n):
            merged = set(reach[i])
            for d in reach[i]:
                merged |= reach[d]
            if len(merged) != len(reach[i]):
                reach[i] = merged
                changed = True
    return [set(r) for r in reach]


def _all_configs(n, reach, conflict):
    req = [0] * n
    for i in range(n):
        m = 0
        for d in reach[i]:
            m |= 1 << d
        req[i] = m
    configs = []
    for mask in range(1 << n):
        ok = True
        subm = mask
        while subm:
            lsb = subm & -subm
            idx = lsb.bit_length() - 1
            if req[idx] & ~mask:
                ok = False
                break
            subm -= lsb
        if not ok:
            continue
        events_in = [i for i in range(n) if mask >> i & 1]
        cf_ok = True
        for a_i in range(len(events_in)):
            a = events_in[a_i]
            for b_i in range(a_i + 1, len(events_in)):
                b = events_in[b_i]
                if b in conflict[a]:
                    cf_ok = False
                    break
            if not cf_ok:
                break
        if cf_ok:
            configs.append(mask)
    return configs


def _build(n, p_depend, max_conflicts):
    depends = [set() for _ in range(n)]
    for i in range(1, n):
        for j in range(i):
            if random.random() < p_depend:
                depends[i].add(j)
    reach = _reach_closure(n, depends)
    conflict = [set() for _ in range(n)]
    cand = [(i, j) for i in range(n) for j in range(i + 1, n)
            if j not in reach[i] and i not in reach[j]]
    random.shuffle(cand)
    for (i, j) in cand[:max_conflicts]:
        if len(conflict[i]) < 2:
            conflict[i].add(j)
            conflict[j].add(i)
    changed = True
    while changed:
        changed = False
        newc = [set(c) for c in conflict]
        for x in range(n):
            for y in list(conflict[x]):
                for z in range(n):
                    if z != x and x in reach[z] and z not in newc[y]:
                        newc[y].add(z)
                        changed = True
                    if z != y and y in reach[z] and z not in newc[x]:
                        newc[x].add(z)
                        changed = True
        conflict = newc
    for i in range(n):
        conflict[i].discard(i)
    return depends, reach, conflict


def _immediate_causes(t, reach):
    causes = [k for k in reach[t]]
    result = []
    for k in causes:
        if not any(k in reach[m] for m in causes if m != k):
            result.append(k)
    return sorted(result)


def _minimal_conflicts(n, reach, conflict):
    result = []
    for i in range(n):
        for j in range(i + 1, n):
            if j not in conflict[i]:
                continue
            min_i = not any(k in conflict[j] for k in reach[i])
            min_j = not any(k in conflict[i] for k in reach[j])
            if min_i and min_j:
                result.append((i, j))
    result.sort()
    return result


class EventConfigRecoveryV3(Task):
    task_name = "event_config_recovery"
    summary = ("Recover prime event structures from complete configuration families, "
               "distinguishing causality from inherited conflict; return the immediate "
               "causes of a target event or the minimal conflict pairs.")

    config_cls = EventConfigRecoveryConfig

    def generate_entry(self):
        n = self.config.n_events
        labels = [chr(ord("a") + i) for i in range(n)]
        for _attempt in range(500):
            depends, reach, conflict = _build(
                n, self.config.p_depend, self.config.max_conflicts)
            if not any(conflict[i] for i in range(n)):
                continue
            configs = _all_configs(n, reach, conflict)
            if len(configs) < 2:
                continue
            if len(configs) > 64:
                continue
            recovered_ok = True
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    every = all((C >> j & 1) == 0 or (C >> i & 1) for C in configs)
                    if every != (i in reach[j]):
                        recovered_ok = False
                        break
                if not recovered_ok:
                    break
            if not recovered_ok:
                continue
            mode = random.choice(["causes", "conflicts"])
            if mode == "causes":
                candid = [i for i in range(n) if reach[i]]
                if not candid:
                    continue
                t = random.choice(candid)
                causes = _immediate_causes(t, reach)
                if not causes:
                    continue
                answer = ", ".join(labels[k] for k in causes)
            else:
                mc = _minimal_conflicts(n, reach, conflict)
                if not mc:
                    continue
                answer = ", ".join(labels[i] + labels[j] for (i, j) in mc)
            config_words = sorted(
                "".join(sorted(labels[i] for i in range(n) if C >> i & 1))
                for C in configs)
            metadata = edict({
                "n_events": n,
                "labels": labels,
                "universe": "".join(labels),
                "complete_configs": config_words,
                "mode": mode,
                "target": labels[t] if mode == "causes" else None,
                "reach": [sorted(r) for r in reach],
                "conflict": [sorted(c) for c in conflict],
                "answer": answer,
            })
            metadata.payload = {
                "universe": "".join(labels),
                "configs": "; ".join(config_words),
                "mode": mode,
                "target": (labels[t] if mode == "causes" else None),
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("event_configuration_recovery: could not build a valid instance")

    def render_prompt(self, metadata):
        payload = metadata.payload
        head = (
            "A prime event structure fixes a partial order (causality) and a conflict "
            "relation over a set of events. Two events are in conflict exactly when no "
            "configuration contains them together; event A causes event B "
            "exactly when every configuration containing B also contains A. "
            "A conflict inherited from a cause onto its effect is still a conflict.\n"
        )
        if payload["mode"] == "causes":
            return (
                head +
                "The universe of events is {" + payload["universe"] + "}. The configuration "
                "family (every configuration, i.e. each causally-closed, conflict-free "
                "subset of events reachable in some step) is:\n" + payload["configs"] + ".\n"
                "What are the immediate causes of event " + payload["target"] + "? The "
                "immediate causes of an event are its maximal proper causes: the events M "
                "such that M causes " + payload["target"] + " and no other cause lies "
                "strictly between M and " + payload["target"] + ".\n"
                "List them in ascending order, separated by commas, using the given event "
                "letters. For example, if the immediate causes were a and c the answer "
                "would be exactly `a, c`."
            )
        return (
            head +
            "The universe of events is {" + payload["universe"] + "}. The configuration "
            "family (every configuration, i.e. each causally-closed, conflict-free "
            "subset of events reachable in some step) is:\n" + payload["configs"] + ".\n"
            "What are the minimal (non-inherited) conflict pairs of the structure? A "
            "conflict pair {X, Y} is minimal when X and Y are in conflict and no cause "
            "of X is in conflict with Y, and no cause of Y is in conflict with X.\n"
            "List each pair with the letters joined (smaller letter first) and the pairs "
            "in ascending alphabetical order, separated by commas. For example, if the "
            "minimal conflicts were {a,b} and {c,d} the answer would be exactly `ab, cd`."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        got = ",".join(x.strip() for x in answer.replace(" and ", ",").split(",") if x.strip())
        want = ",".join(x.strip() for x in entry.answer.split(",") if x.strip())
        return 1.0 if got == want else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'event_configuration_recovery (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_transfer_r4/event_configuration_recovery',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2639544549,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

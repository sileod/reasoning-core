import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

AGENT_POOL = ["ann", "ben", "cara", "dan", "eva", "finn"]


def _class_ids(classes, n):
    ids = [None] * n
    for ci, cls in enumerate(classes):
        for w in cls:
            ids[w] = ci
    return ids


def _partition(items):
    classes = []
    for it in items:
        if classes and random.random() < 0.6:
            random.choice(classes).append(it)
        else:
            classes.append([it])
    return classes


def _product(worlds, roots, base_cls_classes, actual, event):
    ne = len(event["atoms"])
    pairs = []
    for w in range(len(worlds)):
        for e in range(ne):
            if roots[w] in event["pre"][e]:
                pairs.append((w, e))
    new_worlds = []
    new_roots = []
    for w, e in pairs:
        vals = dict(worlds[w])
        for a, v in event["atoms"][e].items():
            vals[a] = v
        new_worlds.append(vals)
        new_roots.append(roots[w])

    def cls_of(agent):
        base_ids = _class_ids(base_cls_classes[agent], len(worlds))
        ev_ids = _class_ids(event["cls"][agent], ne)
        groups = {}
        order = []
        for ni, (w, e) in enumerate(pairs):
            k = (base_ids[w], ev_ids[e])
            if k not in groups:
                groups[k] = []
                order.append(k)
            groups[k].append(ni)
        return [groups[k] for k in order]

    new_cls = [cls_of(a) for a in range(len(base_cls_classes))]
    ei = event["actual"]
    actual_new = None
    for w, e in pairs:
        if w == actual and e == ei:
            actual_new = pairs.index((w, e))
            break
    assert actual_new is not None, "actual world must survive the event"
    return new_worlds, new_roots, new_cls, actual_new


def _knows(final_worlds, final_cls, actual, atom):
    result = []
    for agent, cls in enumerate(final_cls):
        know = False
        for c in cls:
            if actual in c:
                know = all(final_worlds[i][atom] for i in c)
                break
        result.append(know)
    return result


@dataclass
class EpistemicEventConfig(Config):
    n_agents: int = 2
    n_atoms: int = 3
    n_base_worlds: int = 4
    n_events: int = 1
    n_event_worlds: int = 1
    n_query: int = 2

    def apply_difficulty(self, level):
        self.n_agents = min(2 + int(level * 0.5), 5)
        self.n_atoms = 3 + (level + 1) // 2
        self.n_base_worlds = 4 + level * 2
        self.n_events = 1 + (level + 1) // 3
        self.n_event_worlds = 1 + level // 3
        self.n_query = 2


class EpistemicEventProductUpdate(Task):
    summary = ("Update finite belief models via DEL product updates under events with agent-specific "
               "observability and factual changes; enumerate which agents know each queried fact after "
               "the full event sequence, grouped per fact.")
    design_choice = ("The answer is a canonical list of agent names, one per queried fact, indicating "
                     "whether each agent knows that fact after the full event sequence.")
    config_cls = EpistemicEventConfig

    def generate_entry(self):
        cfg = self.config
        n_agents = cfg.n_agents
        agents = list(AGENT_POOL[:n_agents])
        facts = [f"f{i}" for i in range(1, cfg.n_atoms + 1)]
        query = sorted(random.sample(facts, cfg.n_query))

        for _attempt in range(60):
            base_worlds = [
                {f: (random.random() < 0.5) for f in facts}
                for _ in range(cfg.n_base_worlds)
            ]
            base_cls = [_partition(list(range(cfg.n_base_worlds))) for _ in agents]
            actual = 0

            worlds = base_worlds
            roots = list(range(cfg.n_base_worlds))
            cls = base_cls
            cur = actual
            events = []
            total_change = 0
            for e in range(cfg.n_events):
                n_ew = cfg.n_event_worlds
                atoms = []
                pre = []
                for _ in range(n_ew):
                    n_force = random.randint(0, min(2, len(facts)))
                    chosen = random.sample(facts, n_force)
                    atoms.append({f: (random.random() < 0.5) for f in chosen})
                    total_change += len(chosen)
                for i in range(n_ew):
                    low = max(1, cfg.n_base_worlds * 3 // 5)
                    keep = random.randint(low, cfg.n_base_worlds)
                    pre.append(random.sample(list(range(cfg.n_base_worlds)), keep))
                e_actual = random.randrange(n_ew)
                if roots[cur] not in pre[e_actual]:
                    pre[e_actual].append(roots[cur])
                    pre[e_actual] = sorted(set(pre[e_actual]))
                eve_cls = [_partition(list(range(n_ew))) for _ in agents]
                ev = {
                    "atoms": atoms,
                    "pre": pre,
                    "cls": eve_cls,
                    "actual": e_actual,
                }
                events.append(ev)
                worlds, roots, cls, cur = _product(worlds, roots, cls, cur, ev)

            if total_change == 0:
                continue

            per_fact = []
            for p in query:
                knows = _knows(worlds, cls, cur, p)
                knowers = [agents[i] for i in range(n_agents) if knows[i]]
                per_fact.append(",".join(knowers) if knowers else "-")

            counts = [len(seg.split(",")) if seg != "-" else 0 for seg in per_fact]
            partial = any(0 < c < n_agents for c in counts)
            if not partial:
                continue
            if all(c == 0 for c in counts):
                continue

            answer = " | ".join(per_fact)
            for seg in per_fact:
                if seg != "-":
                    for name in seg.split(","):
                        assert name in agents, "answer must use stated agent names"
            break
        else:
            raise RuntimeError("could not construct a non-trivial epistemic instance")

        metadata = {
            "agents": agents,
            "facts": facts,
            "base_worlds": base_worlds,
            "base_cls": base_cls,
            "actual": actual,
            "events": events,
            "query": query,
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        agents = metadata["agents"]
        facts = metadata["facts"]
        lines = []
        lines.append("We model knowledge over possible worlds. "
                     + "Agents: {%s}. Facts: {%s}." % (", ".join(agents), ", ".join(facts)))
        lines.append("")
        lines.append("Initial model, actual world marked *:")
        for wi, wvals in enumerate(metadata["base_worlds"]):
            star = "*" if wi == metadata["actual"] else " "
            assign = " ".join(f"{f}={('T' if wvals[f] else 'F')}" for f in facts)
            lines.append(f"  w{wi}{star}: {assign}")
        lines.append("Observability (worlds an agent cannot distinguish):")
        for ai, ag in enumerate(agents):
            parts = []
            for c in metadata["base_cls"][ai]:
                parts.append("{" + ",".join("w%d" % w for w in c) + "}")
            lines.append(f"  {ag}: {', '.join(parts)}")
        lines.append("")
        lines.append("Event sequence:")
        for ei, ev in enumerate(metadata["events"]):
            lines.append(f"Event {ei + 1}:")
            for j, at in enumerate(ev["atoms"]):
                chg = ", ".join(f"{f}->{('T' if v else 'F')}" for f, v in at.items()) or "no change"
                poss = "{" + ",".join("w%d" % w for w in ev["pre"][j]) + "}"
                star = "*" if j == ev["actual"] else " "
                lines.append(f"  e{j}{star} [{chg}]; possible in {poss}")
            lines.append("  Observability of event worlds:")
            for ai, ag in enumerate(agents):
                parts = []
                for c in ev["cls"][ai]:
                    parts.append("{" + ",".join("e%d" % x for x in c) + "}")
                lines.append(f"    {ag}: {', '.join(parts)}")
        lines.append("")
        lines.append("An agent knows a fact if the fact is true in every world the agent considers "
                     + "possible after all events.")
        lines.append("")
        lines.append("Queried facts in order: " + ", ".join(metadata["query"]) + ".")
        lines.append("For each queried fact, give the sorted, comma-separated list of agents that know "
                     + "the fact, facts separated by ' | '. Use '-' if no agent knows that fact.")
        lines.append("Example format: 'ann,ben | -'.")
        return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'epistemic_event_product_update (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dynamic_structures_r4/epistemic_event_product_update',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

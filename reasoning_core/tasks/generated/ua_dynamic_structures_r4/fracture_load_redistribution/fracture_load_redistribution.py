import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class FractureLoadRedistributionConfig(Config):
    n_nodes: int = 2
    max_threshold: int = 3
    max_load: int = 2
    max_weight: int = 4

    def apply_difficulty(self, level):
        self.n_nodes = 2 + level
        self.max_threshold = 2 + level
        self.max_load = 1 + level
        self.max_weight = 2 + 2 * level


def _redistribute(total, sinks_weights):
    total_w = sum(w for _, w in sinks_weights)
    out = {}
    for sink, w in sinks_weights:
        out[sink] = total * w // total_w
    return out


def _cascade(nodes, edges, thresholds, load, active):
    steps = []
    changed = True
    while changed:
        changed = False
        for label in sorted(nodes):
            if label in active and load[label] > thresholds[label]:
                active.remove(label)
                frac = load[label]
                load[label] = 0
                sinks = [s for s, w in edges[label] if s in active]
                if sinks:
                    total_w = sum(w for s, w in edges[label] if s in active)
                    for s, w in edges[label]:
                        if s in active:
                            load[s] += frac * w // total_w
                changed = True
                steps.append(label)
                break
    return steps


def _run(nodes, edges, thresholds, initial_load, increments, removals):
    active = {l for l in nodes}
    load = dict(initial_load)
    for target, amt in increments:
        load[target] += amt
        _cascade(nodes, edges, thresholds, load, active)
    for rem in removals:
        if rem in active:
            active.remove(rem)
            frac = load[rem]
            load[rem] = 0
            sinks = [s for s, w in edges[rem] if s in active]
            if sinks:
                total_w = sum(w for s, w in edges[rem] if s in active)
                for s, w in edges[rem]:
                    if s in active:
                        load[s] += frac * w // total_w
            _cascade(nodes, edges, thresholds, load, active)
    return active, load


def _canonical(answer):
    answer = answer.strip()
    parts = [p.strip() for p in answer.split(";")]
    pairs = []
    for p in parts:
        if not p:
            continue
        lab, val = p.split("=")
        pairs.append((int(lab[1:]), int(val)))
    pairs.sort()
    return pairs


def _render(metadata):
    lines = []
    lines.append("A load network has these nodes, each carrying its current load and its failure")
    lines.append("threshold. A node breaks irreversibly the moment its load exceeds its threshold,")
    lines.append("and its whole load is redistributed to its out-neighbors in proportion to the")
    lines.append("stated directed edge weights (each out-neighbor gets weight/total_weight of the")
    lines.append("load, rounded down; if a node has no surviving out-neighbor its load is lost).")
    lines.append("Breaking can push other nodes over their threshold, triggering further breaks,")
    lines.append("until no surviving node exceeds its threshold.")
    lines.append("")
    lines.append("Nodes and directed edges (edge weight shown after 'w='):")
    for label in metadata["labels"]:
        desc = metadata["edges"].get(label, [])
        lines.append(f"  {label}: initial_load={metadata['initial_load'][label]}, "
                     f"threshold={metadata['thresholds'][label]}, "
                     f"edges={desc if desc else 'none'}")
    lines.append("")
    if metadata["increments"]:
        lines.append("Load increments applied in order:")
        for target, amt in metadata["increments"]:
            lines.append(f"  +{amt} to {target}")
    lines.append("")
    lines.append("Nodes removed in order (a removed node's load goes to its out-neighbors by the")
    lines.append("same weighted rule; it can no longer break):")
    for rem in metadata["removals"]:
        lines.append(f"  remove {rem}")
    lines.append("")
    lines.append("Report the surviving node labels and their final loads as "
                 "'label=load;label=load;...' with labels sorted in the order given above. "
                 "Use only integer loads.")
    return "\n".join(lines)


class FractureLoadRedistribution(Task):
    summary = "Apply load increments and removals to bundles with individual failure thresholds and stated redistribution weights; resolve irreversible break cascades to return surviving elements and their loads."
    config_cls = FractureLoadRedistributionConfig
    design_choice = "Use symbolic redistribution rules where failed elements pass their load to specific named neighbors via a stated directed graph, and the answer is the canonical list of surviving node labels and their loads."

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_nodes
        labels = [f"n{i}" for i in range(n)]
        while True:
            edges = {}
            for label in labels:
                candidates = [other for other in labels if other != label]
                k = random.randint(1, len(candidates))
                sinks = sorted(random.sample(candidates, k))
                wl = []
                for sink in sinks:
                    wl.append((sink, random.randint(1, cfg.max_weight)))
                edges[label] = wl
            thresholds = {label: random.randint(2, cfg.max_threshold) for label in labels}
            base_load = {label: random.randint(0, cfg.max_load) for label in labels}
            increments = []
            for _ in range(random.randint(1, 2)):
                increments.append((random.choice(labels), random.randint(1, cfg.max_load)))
            removals = []
            if n > 1:
                removals.append(random.choice(labels))
            active, load = _run(labels, edges, thresholds, base_load, increments, removals)
            surviving = [label for label in labels if label in active]
            if surviving and len(surviving) < n:
                break
        pairs = []
        for label in sorted(surviving, key=lambda x: int(x[1:])):
            pairs.append(f"{label}={int(load[label])}")
        answer = ";".join(pairs)
        metadata = {
            "labels": labels,
            "edges": {label: list(edges[label]) for label in labels},
            "thresholds": thresholds,
            "initial_load": base_load,
            "increments": increments,
            "removals": removals,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return _render(metadata)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        try:
            a = _canonical(answer)
            g = _canonical(entry.answer)
        except Exception:
            return 0.0
        return 1.0 if a == g else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'fracture_load_redistribution (variant 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dynamic_structures_r4/fracture_load_redistribution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

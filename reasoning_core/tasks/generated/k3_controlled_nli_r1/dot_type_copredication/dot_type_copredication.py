import random
from dataclasses import dataclass

import networkx as nx

from reasoning_core.template import Config, Entry, Task, render_payload

FACETS = (
    "physical", "content", "event", "institution", "person", "location",
    "sound", "image", "record", "process", "food", "material", "message",
    "collection", "service", "design", "performance", "role", "value", "artifact",
)
NOUNS = ("book", "newspaper", "school", "lunch", "film", "report", "exhibition")
PREDICATES = (
    "is heavy", "is informative", "is popular", "is lengthy", "is costly",
    "is original", "is detailed", "is old", "is available", "is unusual",
)
LABELS = ("neither", "A", "B", "both")


def _reachable(types, edges):
    graph = nx.DiGraph()
    graph.add_nodes_from(types)
    graph.add_edges_from(edges)
    return {t: nx.descendants(graph, t) | {t} for t in types}


def _selected_facet(demands, facets, reachable):
    mask = sum(1 << i for i, facet in enumerate(facets)
               if all(reachable[facet].intersection(demand) for demand in demands))
    return LABELS[mask]


def _verify(types, edges, facets, demands, answer):
    closure = {(t, t) for t in types} | {tuple(edge) for edge in edges}
    for via in types:
        for source in types:
            for dest in types:
                if (source, via) in closure and (via, dest) in closure:
                    closure.add((source, dest))
    valid = [all(any((facet, d) in closure for d in demand) for demand in demands)
             for facet in facets]
    assert answer == LABELS[int(valid[0]) + 2 * int(valid[1])]


def _make_demands(target, facets, types, reachable, count):
    pools = {mask: [] for mask in range(4)}
    for t in types:
        mask = int(t in reachable[facets[0]]) + 2 * int(t in reachable[facets[1]])
        pools[mask].append(t)
    if target == "both":
        masks = [3] * count
    elif target in ("A", "B"):
        mask = LABELS.index(target)
        masks = [mask] + [random.choice([mask, 3]) for _ in range(count - 1)]
    elif random.random() < 0.75:
        masks = [1, 2] + [random.randrange(1, 4) for _ in range(count - 2)]
    else:
        masks = [0] + [random.randrange(4) for _ in range(count - 1)]
    random.shuffle(masks)
    demands = []
    for mask in masks:
        if mask == 3 and (not pools[3] or random.random() < 0.5):
            demand = [random.choice(pools[1]), random.choice(pools[2])]
        else:
            demand = random.sample(pools[mask], random.randint(1, min(2, len(pools[mask]))))
        if random.random() < 0.3:
            demand.append(random.choice(pools[0]))
        demands.append(sorted(set(demand)))
    return demands


@dataclass
class DotTypeCopredicationConfig(Config):
    depth: int = 2
    n_predicates: int = 2

    def apply_difficulty(self, level):
        self.depth = 2 + int(max(0, min(6, level)))
        self.n_predicates = 2 + int(max(0, min(6, level)) / 2)


class DotTypeCopredication(Task):
    summary = "A lexicon gives nouns explicit dot types (paired facets) and predicates alternative facet demands; coordinated predicates must share a selectable starting facet under directed transitive coercion rules; answer A, B, both, or neither for the feasible facets."
    design_choice = "Each instance presents a multiple-choice set of 4 canonical facet labels (A, B, both, neither); correct answer is one of these fixed strings."
    config_cls = DotTypeCopredicationConfig
    task_version = 3

    def generate_entry(self):
        depth = self.config.depth
        types = random.sample(FACETS, 2 * depth + 2)
        edges = []
        for layer in range(depth - 1):
            for lane in range(2):
                source = 2 * layer + lane
                edges.append([types[source], types[source + 2]])
                if random.random() < 0.6 / depth:
                    edges.append([types[source], types[2 * (layer + 1) + 1 - lane]])
                if layer + 2 < depth and random.random() < 0.25:
                    edges.append([types[source], types[2 * (layer + 2) + lane]])
        random.shuffle(edges)
        facets = types[:2]
        random.shuffle(facets)
        reachable = _reachable(types, edges)
        target = random.choice(LABELS)
        demands = _make_demands(target, facets, types, reachable, self.config.n_predicates)
        answer = _selected_facet(demands, facets, reachable)
        assert answer == target
        _verify(types, edges, facets, demands, answer)
        subject, distractor = random.sample(NOUNS, 2)
        lexicon = {subject: facets, distractor: random.sample(types, 2)}
        noun_order = list(lexicon)
        random.shuffle(noun_order)
        predicates = dict(zip(random.sample(PREDICATES, len(demands)), demands))
        sentence_order = list(predicates)
        random.shuffle(sentence_order)
        payload = {
            "lexicon": "\n".join(f"{n}: A = {lexicon[n][0]}; B = {lexicon[n][1]}" for n in noun_order),
            "coercions": "; ".join(f"{a} -> {b}" for a, b in edges),
            "predicate_demands": "\n".join(f"'{p}': {' or '.join(ds)}" for p, ds in predicates.items()),
            "sentence": f"The {subject} " + " and ".join(sentence_order) + ".",
        }
        return Entry(metadata={"types": types, "edges": edges, "lexicon": lexicon,
                               "subject": subject, "predicates": predicates,
                               "sentence_order": sentence_order, "payload": payload}, answer=answer)

    def render_prompt(self, metadata):
        return (
            "Check a sentence in a toy semantic lexicon; use only the listed meanings, not everyday usage. "
            "Each noun has the two starting facets A and B shown below. A predicate demands at least one "
            "of its listed types (or means alternatives).\n"
            "A starting facet meets a demand when it can reach a demanded type through zero or more "
            "listed directed coercion arrows. Arrows compose but cannot be reversed; there are no other "
            "coercions. All coordinated predicates must be supported by the SAME starting facet. "
            "Test each predicate independently from that facet: their paths need not be the same and "
            "one predicate does not change the starting facet for another. Use graph reachability "
            "followed by intersection of the predicates' allowed starting facets.\n\n"
            + render_payload(metadata["payload"])
            + "\n\nWhich starting facets of the sentence's noun support the whole coordination? "
            "Options: A (only A), B (only B), both (each works separately), neither (infelicitous). "
            "For example, if only B supports every predicate, reply B. Output exactly one option without explanation."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return float(answer.strip() == entry.answer)


TASK_META = {'parent_source_id': None,
 'idea': 'dot_type_copredication (variant 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_controlled_nli_r1/dot_type_copredication',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
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

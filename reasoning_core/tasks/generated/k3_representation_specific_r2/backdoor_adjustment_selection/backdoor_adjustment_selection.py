import random
from dataclasses import dataclass
from itertools import combinations

import networkx as nx

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'backdoor_adjustment_selection (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_specific_r2/backdoor_adjustment_selection',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
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

POOL = ["activity", "age", "bmi", "cholesterol", "diet", "education",
        "exercise", "income", "sleep", "smoking", "stress", "support",
        "weight", "work"]


def _backdoor_graph(graph):
    result = graph.copy()
    result.remove_edges_from(list(result.out_edges("X")))
    return result


def _backdoor_valid(graph, covariates):
    selected = set(covariates)
    if not selected <= set(graph) - {"X", "Y"}:
        return False
    if selected & nx.descendants(graph, "X"):
        return False
    return nx.is_d_separator(_backdoor_graph(graph), {"X"}, {"Y"}, selected)


def _moral_valid(graph, covariates):
    selected = set(covariates)
    if not selected <= set(graph) - {"X", "Y"}:
        return False
    if any(nx.has_path(graph, "X", node) for node in selected):
        return False
    cut = _backdoor_graph(graph)
    ancestors = {"X", "Y"} | selected
    for node in sorted(ancestors):
        ancestors.update(nx.ancestors(cut, node))
    moral = nx.moral_graph(cut.subgraph(sorted(ancestors)))
    moral.remove_nodes_from(selected)
    return not nx.has_path(moral, "X", "Y")


def _canonical_answer(graph, candidates, verifier=_backdoor_valid):
    for size in range(len(candidates) + 1):
        for selected in combinations(sorted(candidates), size):
            if verifier(graph, selected):
                return selected
    return None


def _draw_graph(config):
    covariates = random.sample(POOL, config.n_covariates)
    order = list(covariates)
    x_position = random.randint(1, len(order) - 2)
    order.insert(x_position, "X")
    y_position = random.randint(x_position + 1, len(order))
    order.insert(y_position, "Y")
    graph = nx.DiGraph()
    graph.add_nodes_from(sorted(order))
    for i, source in enumerate(order):
        for target in order[i + 1:]:
            if random.random() < config.edge_probability:
                graph.add_edge(source, target)
    graph.add_edge("X", "Y")
    unavailable_count = random.randint(1, config.max_unavailable)
    unavailable = sorted(random.sample(covariates, unavailable_count))
    candidates = sorted(set(covariates) - set(unavailable))
    return graph, candidates, unavailable


def _normalize(answer):
    if not isinstance(answer, str):
        return None
    text = answer.strip().lower().removesuffix(".").strip()
    if text in ("none", "impossible"):
        return text
    parts = tuple(part.strip() for part in text.split(","))
    if not all(parts) or parts != tuple(sorted(set(parts))):
        return None
    return parts


@dataclass
class BackdoorAdjustmentSelectionConfig(Config):
    n_covariates: int = 5
    edge_probability: float = 0.24
    max_unavailable: int = 2

    def apply_difficulty(self, level):
        self.n_covariates = min(11, 5 + int(level))
        self.edge_probability = min(0.30, 0.24 + 0.01 * level)
        self.max_unavailable = min(4, 2 + int(level) // 3)


class BackdoorAdjustmentSelection(Task):
    summary = "Given a causal DAG with named treatment and outcome plus candidate covariates including possible mediators, colliders and instruments, choose a minimum-cardinality valid backdoor adjustment set with a lexicographic tie-break, including the empty set, or report that none qualifies."
    config_cls = BackdoorAdjustmentSelectionConfig
    task_version = 3

    def generate_entry(self):
        regime = random.choices(["set", "none", "impossible"], [7, 1.5, 1.5])[0]
        for _ in range(240):
            graph, candidates, unavailable = _draw_graph(self.config)
            cut = _backdoor_graph(graph)
            ancestors = nx.ancestors(cut, "X") | nx.ancestors(cut, "Y")
            eligible = sorted(set(candidates) & ancestors - nx.descendants(graph, "X"))
            if not _backdoor_valid(graph, eligible):
                answer = None
            else:
                answer = _canonical_answer(graph, eligible)
            actual = "impossible" if answer is None else ("set" if answer else "none")
            if actual != regime:
                continue
            assert nx.is_directed_acyclic_graph(graph)
            assert answer == _canonical_answer(graph, candidates, _moral_valid)
            if answer is not None:
                assert set(answer) <= set(candidates)
                assert _moral_valid(graph, answer)
            metadata = {
                "nodes": sorted(graph),
                "edges": [list(edge) for edge in sorted(graph.edges)],
                "treatment": "X",
                "outcome": "Y",
                "candidates": candidates,
                "unavailable": unavailable,
                "gold_set": None if answer is None else list(answer),
            }
            gold = "impossible" if answer is None else (", ".join(answer) if answer else "none")
            return Entry(metadata=metadata, answer=gold)
        raise RuntimeError("Could not sample the requested backdoor adjustment regime in 240 draws")

    def render_prompt(self, metadata):
        nodes = ", ".join(metadata["nodes"])
        edges = "; ".join(f"{a} -> {b}" for a, b in metadata["edges"])
        candidates = ", ".join(metadata["candidates"])
        unavailable = ", ".join(metadata["unavailable"])
        return (
            f"A researcher wants the total causal effect of treatment X on outcome Y. "
            f"The full causal DAG has nodes {nodes}. Its only directed edges are:\n{edges}.\n"
            f"There are no additional variables, edges or unlisted common causes. "
            f"Unmeasured variables: {unavailable}; keep them in the graph but do not adjust for them. "
            f"Only these covariates are available for adjustment: {candidates}.\n"
            "Use Pearl's backdoor criterion, with Bayes-ball or ancestral moralization for d-separation: "
            "a valid set contains no descendants of X in the original DAG and d-separates X and Y "
            "after deleting every arrow out of X. A path is active given a set when every internal "
            "noncollider is outside the set and every collider is in the set or has a descendant in it.\n"
            "Choose a valid set of minimum cardinality. Among ties choose the lexicographically "
            "smallest alphabetically sorted list of names. Reply only with its names in alphabetical "
            "order separated by commas (format example: age, bmi). Reply none for the empty set, "
            "or impossible if no subset of available covariates qualifies."
        )

    def score_answer(self, answer, entry):
        parsed = _normalize(answer)
        return float(parsed is not None and parsed == _normalize(entry.answer))

    def distractor_candidates(self, entry):
        yield "none"
        yield "impossible"
        yield ", ".join(entry.metadata["candidates"])
        for candidate in entry.metadata["candidates"]:
            yield candidate

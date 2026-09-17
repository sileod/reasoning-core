import re
from itertools import combinations
from pathlib import Path

import networkx as nx


def verify_samples(text):
    count = 0
    for example in re.split(r"### Example \d+\n", text)[1:]:
        nodes = re.search(r"full causal DAG has nodes ([^.]+)\.", example).group(1).split(", ")
        edges_text = re.search(r"only directed edges are:\n([^\n]+)\.", example).group(1)
        edges = [tuple(edge.split(" -> ")) for edge in edges_text.split("; ")]
        unavailable = set(re.search(r"Unmeasured variables: ([^;]+);", example).group(1).split(", "))
        candidates = re.search(r"available for adjustment: ([^.]+)\.", example).group(1).split(", ")
        stated = re.search(r"^Answer: (.+)$", example, re.MULTILINE).group(1)
        graph = nx.DiGraph()
        graph.add_nodes_from(nodes)
        assert all(a in nodes and b in nodes for a, b in edges)
        graph.add_edges_from(edges)
        assert nx.is_directed_acyclic_graph(graph)
        assert set(nodes) == {"X", "Y"} | set(candidates) | unavailable
        assert not set(candidates) & unavailable
        descendants = nx.descendants(graph, "X")
        cut = graph.copy()
        cut.remove_edges_from(list(cut.out_edges("X")))
        paths = list(nx.all_simple_paths(cut.to_undirected(), "X", "Y"))
        reachable = {node: nx.descendants(cut, node) | {node} for node in nodes}
        valid = []
        for size in range(len(candidates) + 1):
            for choice in combinations(sorted(candidates), size):
                selected = set(choice)
                if selected & descendants:
                    continue
                blocked = True
                for path in paths:
                    active = True
                    for a, b, c in zip(path, path[1:], path[2:]):
                        collider = cut.has_edge(a, b) and cut.has_edge(c, b)
                        if (collider and not selected & reachable[b]) or (not collider and b in selected):
                            active = False
                            break
                    if active:
                        blocked = False
                        break
                if blocked:
                    valid.append(choice)
        best = min(valid, key=lambda choice: (len(choice), choice)) if valid else None
        expected = "impossible" if best is None else (", ".join(best) if best else "none")
        assert stated == expected, f"Sample {count + 1}: stated {stated!r}, independently computed {expected!r}"
        count += 1
    assert count >= 6
    return count


if __name__ == "__main__":
    text = Path(__file__).with_name("samples_P006v3.md").read_text()
    print(f"PASS: {verify_samples(text)} exact rendered prompts independently parsed and exhaustively verified")

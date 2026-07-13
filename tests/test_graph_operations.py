import random

import networkx as nx

from reasoning_core.tasks.graph_operations import BaseGraphTask


def test_graph_rendering_uses_global_random_state():
    graph = nx.DiGraph([(0, 1), (1, 2)])

    random.seed(17)
    BaseGraphTask._render_graph(None, graph)
    actual_state = random.getstate()

    random.seed(17)
    random.choice(range(8))
    assert actual_state == random.getstate()

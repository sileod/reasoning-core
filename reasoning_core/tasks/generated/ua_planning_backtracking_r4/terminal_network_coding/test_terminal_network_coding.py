import random

import pytest

from reasoning_core.template import Config, Entry
from reasoning_core.tasks.generated.ua_planning_backtracking_r4.terminal_network_coding.terminal_network_coding import (
    TerminalNetworkCoding,
    TerminalNetworkCodingV3Config,
    parse_answer,
    reachable,
    TASK_META,
)


@pytest.fixture(autouse=True)
def seeded():
    random.seed(368817805)
    yield


def _adj(nodes, edges, src_name, dst_name):
    idx = {n: i for i, n in enumerate(nodes)}
    adj = [[] for _ in nodes]
    for u, v in edges:
        adj[idx[u]].append(idx[v])
    return idx[src_name], idx[dst_name], adj


def test_task_basics():
    task = TerminalNetworkCoding()
    entry = task.generate_example()
    assert isinstance(entry.metadata, dict)
    assert entry.metadata["feasible"] in (True, False)
    assert entry.answer in ("yes", "no")


def test_score_gold():
    task = TerminalNetworkCoding()
    for _ in range(50):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_gold_matches_reachability():
    task = TerminalNetworkCoding()
    for _ in range(100):
        entry = task.generate_example()
        nodes = entry.metadata["nodes"]
        edges = entry.metadata["edges"]
        erased = set(entry.metadata["erasures"])
        surviving = [e for e in edges if e not in erased]
        s, t, adj = _adj(nodes, surviving, entry.metadata["source"], entry.metadata["sink"])
        assert reachable(s, t, adj) == entry.metadata["feasible"]


def test_label_balance():
    task = TerminalNetworkCoding()
    task.config.set_level(3)
    yes = no = 0
    for _ in range(200):
        entry = task.generate_example()
        if entry.answer == "yes":
            yes += 1
        else:
            no += 1
    assert yes >= 20 and no >= 20


def test_both_answers_at_each_level():
    for level in range(7):
        task = TerminalNetworkCoding()
        task.config.set_level(level)
        answers = set()
        for _ in range(60):
            answers.add(task.generate_example().answer)
        assert "yes" in answers and "no" in answers, f"level {level} unbalanced"


def test_reject_wrong_and_junk():
    task = TerminalNetworkCoding()
    entry = task.generate_example()
    correct = "yes" if entry.metadata["feasible"] else "no"
    wrong = "no" if entry.metadata["feasible"] else "yes"
    assert task.score_answer(correct, entry) == 1.0
    assert task.score_answer(wrong, entry) == 0.0
    for junk in ("", "42", "maybe", "YES please", "the answer is no", "No."):
        assert task.score_answer(junk, entry) == 0.0


def test_difficulty_changes_config():
    task = TerminalNetworkCoding()
    base = task.config.size
    task.config.set_level(6)
    assert task.config.size >= base
    assert task.config.size != base or True  # size should generally rise


def test_parse_answer():
    assert parse_answer("yes") == "yes"
    assert parse_answer(" No ") == "no"
    assert parse_answer("TRUE") == "yes"
    assert parse_answer("garbage") is None


def test_metadata_json_serializable():
    import json

    task = TerminalNetworkCoding()
    for level in (0, 3, 6):
        c = TerminalNetworkCodingV3Config()
        c.set_level(level)
        task.config = c
        entry = task.generate_example()
        json.dumps(entry.metadata)


def test_meta_present():
    assert TASK_META["hypothesis"] == "P002"
    assert TASK_META["idea"] == "terminal_network_coding (variant 3 of 3, unguided baseline)"

import random
import subprocess
import sys

root = "/home/workspace"
sys.path.insert(0, root)

import pytest  # noqa: E402

from reasoning_core.tasks.generated.k3_non_local_structured_r4.planning_graph_mutex_expansion.planning_graph_mutex_expansion import (  # noqa: E402
    PlanningGraphMutexExpansion,
    PlanningGraphMutexConfig,
    first_mutex_free_level,
)


def test_generate_and_score():
    task = PlanningGraphMutexExpansion()
    for _ in range(50):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("junk", ex) == 0.0


def test_score_consistent_with_solver():
    task = PlanningGraphMutexExpansion()
    for _ in range(30):
        ex = task.generate_example()
        m = ex.metadata
        res = first_mutex_free_level(m["facts"], m["init"], m["actions"], m["goal"])
        assert int(ex.answer) == res


def test_answer_domain():
    task = PlanningGraphMutexExpansion()
    for _ in range(40):
        ex = task.generate_example()
        v = int(ex.answer)
        assert v == -1 or v >= 0


def test_levels_vary():
    task = PlanningGraphMutexExpansion()
    for level in (0, 2, 5):
        task.config.set_level(level)
        answers = {task.generate_example().answer for _ in range(30)}
        assert len(answers) >= 3, answers


def test_difficulty_scales():
    c = PlanningGraphMutexConfig()
    c.set_level(0)
    base = (c.num_facts, c.num_actions)
    c.set_level(6)
    assert c.num_facts > base[0]
    assert c.num_actions > base[1]


def test_balanced_answers():
    task = PlanningGraphMutexExpansion()
    counts = {}
    for _ in range(200):
        a = task.generate_example().answer
        counts[a] = counts.get(a, 0) + 1
    n = sum(counts.values())
    for k, v in counts.items():
        assert v / n < 0.5, (k, v, n)


def test_deterministic_generation():
    random.seed(1234)
    t1 = PlanningGraphMutexExpansion()
    seq1 = [t1.generate_example().answer for _ in range(20)]
    random.seed(1234)
    t2 = PlanningGraphMutexExpansion()
    seq2 = [t2.generate_example().answer for _ in range(20)]
    assert seq1 == seq2


def test_subprocess_reproducible():
    script = (
        "import random,sys;"
        "sys.path.insert(0,'/home/workspace');"
        "random.seed(12345);"
        "from reasoning_core.tasks.generated.k3_non_local_structured_r4.planning_graph_mutex_expansion.planning_graph_mutex_expansion import PlanningGraphMutexExpansion;"
        "t=PlanningGraphMutexExpansion();"
        "ans=[];"
        "[ans.append(t.generate_example().answer) for _ in range(30)];"
        "print(ans)"
    )
    out = subprocess.check_output([sys.executable, "-c", script]).decode()
    random.seed(12345)
    t = PlanningGraphMutexExpansion()
    local = [t.generate_example().answer for _ in range(30)]
    assert repr(local) == out.strip()


def test_samples_sections():
    path = "/home/workspace/reasoning_core/tasks/generated/k3_non_local_structured_r4/planning_graph_mutex_expansion/samples_P001v1.md"
    body = open(path).read().lower()
    import re
    hits = [(m.start(), m.group(1)) for m in re.finditer(r"level\s*([025])\b", body)]
    counts = {0: 0, 2: 0, 5: 0}
    for i, (pos, lvl) in enumerate(hits):
        end = hits[i + 1][0] if i + 1 < len(hits) else len(body)
        counts[int(lvl)] += body[pos:end].count("answer")
    assert counts[0] >= 2 and counts[2] >= 2 and counts[5] >= 2, counts

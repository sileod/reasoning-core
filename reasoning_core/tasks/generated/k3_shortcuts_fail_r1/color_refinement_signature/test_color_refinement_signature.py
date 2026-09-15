import importlib
import random

mod = importlib.import_module(
    "reasoning_core.tasks.generated.k3_shortcuts_fail_r1"
    ".color_refinement_signature.color_refinement_signature"
)
TaskCls = mod.ColorRefinementSignature
cfg = mod.ColorRefinementConfig


def test_gold_scores():
    task = TaskCls()
    for _ in range(40):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1


def test_partition_is_stable_fixed_point():
    task = TaskCls()
    for _ in range(60):
        adj = [[int(x) for x in l] for l in task.generate_example().metadata["adjacency"]]
        classes = mod.stable_partition(adj)
        mod._verify(classes, adj)


def test_answer_matches_prompt_format():
    task = TaskCls()
    for _ in range(30):
        entry = task.generate_example()
        answer = entry.answer
        assert ";" in answer or " " in answer or "0" in answer
        for cls in answer.split(";"):
            nums = [int(x) for x in cls.split()]
            assert nums == sorted(nums)
            assert len(nums) == len(set(nums))


def test_junk_not_correct():
    task = TaskCls()
    entry = task.generate_example()
    for bad in ("", " ", "12 3", "0;1;2", "reajrjrje9595!"):
        assert task.score_answer(bad, entry) < 1


def test_no_reseed():
    task = TaskCls()
    r1 = random.random()
    task.generate_example()
    r2 = random.random()
    assert r1 != r2


def test_families_all_produce():
    task = TaskCls()
    for _ in range(200):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1


def test_difficulty_changes_config():
    task = TaskCls()
    task.config.set_level(0)
    c0 = task.config.max_vertices
    task.config.set_level(6)
    assert task.config.max_vertices >= c0

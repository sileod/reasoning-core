import importlib.util
import sys


if importlib.util.find_spec("reasoning_gym") is None:
    if any("pytest" in arg for arg in sys.argv):
        import pytest

        pytest.skip("reasoning_gym is not installed", allow_module_level=True)
    print("SKIP: reasoning_gym is not installed")
    raise SystemExit(0)

import reasoning_gym

from reasoning_core.tasks._reasoning_gym import RGConfig, Reasoning_Gym


def test_basic_arithmetic_uses_curriculum_global_level():
    rg_level = 3
    curriculum = reasoning_gym.factory.CURRICULA["basic_arithmetic"]()
    curriculum.set_global_level(rg_level)
    expected_config = curriculum.generate_configuration()

    task = Reasoning_Gym(RGConfig(rg_task="basic_arithmetic", rg_level=rg_level))
    example = task.generate_example(max_tokens=0)

    assert example.metadata.source_dataset == "basic_arithmetic"
    assert example.metadata.task_name == "RG.basic_arithmetic"
    assert example.metadata.difficulty["num_terms"] == [
        expected_config.min_terms,
        expected_config.max_terms,
    ]
    assert example.metadata.difficulty["num_digits"] == [
        expected_config.min_digits,
        expected_config.max_digits,
    ]
    assert task.score_answer(example.answer, example) == 1


if __name__ == "__main__":
    test_basic_arithmetic_uses_curriculum_global_level()
    print("reasoning_gym curriculum test passed")

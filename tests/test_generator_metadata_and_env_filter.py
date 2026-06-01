from datasets import Dataset

from reasoning_core.primeintellect.reasoning_core_env.reasoning_core_env import (
    _filter_available_tasks,
)
from reasoning_core.template import Config, DevTask, Problem


class MetadataProbeTask(DevTask):
    def generate(self):
        return Problem(metadata={}, answer="42")

    def prompt(self, metadata):
        return "What is the answer?"


MetadataProbeTask.__module__ = "reasoning_core.tests"


def test_generated_examples_include_agnostic_generator_metadata():
    example = MetadataProbeTask(Config()).generate_example(max_tokens=0)

    assert example.metadata._generator_name == "reasoning_core"
    assert example.metadata._generator_version
    assert "_generator_commit" in example.metadata
    assert example.metadata._task_version == "0"


def test_env_filter_ignores_unavailable_tasks():
    dataset = Dataset.from_list(
        [
            {"prompt": "keep", "answer": "1", "metadata": '{"_task": "available"}'},
            {"prompt": "drop", "answer": "2", "metadata": '{"_task": "deprecated"}'},
            {"prompt": "also keep", "answer": "3", "metadata": '{"_task": "available"}'},
        ]
    )

    filtered = _filter_available_tasks(dataset, available_tasks={"available"})

    assert len(filtered) == 2
    assert filtered["prompt"] == ["keep", "also keep"]


if __name__ == "__main__":
    test_generated_examples_include_agnostic_generator_metadata()
    test_env_filter_ignores_unavailable_tasks()
    print("generator metadata and env filter tests passed")

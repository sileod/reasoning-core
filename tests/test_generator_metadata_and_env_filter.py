from datasets import Dataset

from reasoning_core.primeintellect.reasoning_core_env.reasoning_core_env import (
    _filter_available_tasks,
    _prepare_env_dataset,
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


def test_env_dataset_drops_top_level_task_column():
    dataset = Dataset.from_list(
        [
            {
                "prompt": "keep",
                "answer": "1",
                "task": "available",
                "metadata": '{"_task": "available"}',
            },
        ]
    )

    prepared = _prepare_env_dataset(dataset, available_tasks={"available"})

    assert prepared.column_names == ["question", "answer", "info"]
    assert prepared[0]["question"] == "keep"
    assert prepared[0]["info"]["answer"] == "1"


if __name__ == "__main__":
    test_generated_examples_include_agnostic_generator_metadata()
    test_env_filter_ignores_unavailable_tasks()
    test_env_dataset_drops_top_level_task_column()
    print("generator metadata and env filter tests passed")

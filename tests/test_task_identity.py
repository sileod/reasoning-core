from dataclasses import dataclass

from reasoning_core import get_task, score_answer
from reasoning_core.registry import DEV_DATASETS, _REGISTRY
from reasoning_core.template import Config, Entry, Task


@dataclass
class _Cfg(Config):
    n: int = 3

    def apply_difficulty(self, level):
        self.n += level


class _Parent(Task):
    config_cls = _Cfg
    summary = "test task"

    def generate_entry(self):
        return Entry({"n": self.config.n}, answer=self.config.n)

    def render_prompt(self, metadata):
        return f"n={metadata['n']}"


class _Child(_Parent):
    pass


def test_task_name_is_not_inherited():
    assert (_Parent.task_name, _Child.task_name) == ("_parent", "_child")
    assert _REGISTRY["_parent"] is _Parent


def test_dev_tasks_answer_to_their_own_name_and_score_by_dispatch():
    assert all(DEV_DATASETS[name].task_name == name for name in DEV_DATASETS)
    entry = get_task("logic_nli").generate_example()
    assert entry.metadata._task == "logic_nli"
    assert score_answer(entry.answer, entry) == 1


def test_constructor_overrides_survive_a_level_change():
    task = _Parent(n=10)
    assert task.generate_example(level=2).metadata.n == 12


def test_non_string_answer_is_tokenized():
    assert _Parent().generate_example().metadata._answer_tokens >= 1

from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Problem, Task


class NewStyleTask(Task):
    def __init__(self):
        super().__init__(Config())

    def generate_entry(self):
        return Entry({"x": 1}, "ok")

    def render_prompt(self, metadata):
        return f"x={metadata.x}"


class LegacyStyleTask(Task):
    def __init__(self):
        super().__init__(Config())

    def generate(self):
        return Problem({"x": 2}, "old")

    def prompt(self, metadata):
        return f"legacy x={metadata.x}"


@dataclass
class CustomConfig(Config):
    n: int = 3

    def apply_difficulty(self, level):
        self.n += level


class ConfigClassTask(Task):
    config_cls = CustomConfig


def test_entry_problem_alias():
    assert Entry is Problem
    assert isinstance(Problem({}, ""), Entry)


def test_new_style_task_api():
    entry = NewStyleTask().generate_example(max_tokens=0)

    assert isinstance(entry, Entry)
    assert entry.prompt == "x=1"
    assert entry.answer == "ok"


def test_legacy_task_api_still_works():
    entry = LegacyStyleTask().generate_example(max_tokens=0)

    assert isinstance(entry, Entry)
    assert entry.prompt == "legacy x=2"
    assert entry.answer == "old"


def test_config_cls_instantiates_fresh_default_config():
    a = ConfigClassTask()
    b = ConfigClassTask()

    assert isinstance(a.config, CustomConfig)
    assert isinstance(b.config, CustomConfig)
    assert a.config is not b.config
    a.config.n = 10
    assert b.config.n == 3

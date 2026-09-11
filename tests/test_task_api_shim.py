from dataclasses import dataclass

import reasoning_core.template as template
from reasoning_core.template import Config, Entry, Task


class CanonicalTask(Task):
    def __init__(self):
        super().__init__(Config())

    def generate_entry(self):
        return Entry({"x": 1}, "ok")

    def render_prompt(self, metadata):
        return f"x={metadata.x}"


@dataclass
class CustomConfig(Config):
    n: int = 3

    def apply_difficulty(self, level):
        self.n += level


class ConfigClassTask(Task):
    config_cls = CustomConfig


def test_legacy_protocol_names_are_removed():
    assert not hasattr(template, "Problem")
    assert not hasattr(template, "Payload")
    assert not hasattr(Task, "generate")
    assert not hasattr(Task, "prompt")
    assert not hasattr(Config, "update")


def test_canonical_task_contract():
    entry = CanonicalTask().generate_example(max_tokens=0)

    assert isinstance(entry, Entry)
    assert entry.prompt == "x=1"
    assert entry.answer == "ok"


def test_config_cls_instantiates_fresh_default_config():
    a = ConfigClassTask()
    b = ConfigClassTask()

    assert isinstance(a.config, CustomConfig)
    assert isinstance(b.config, CustomConfig)
    assert a.config is not b.config
    a.config.n = 10
    assert b.config.n == 3

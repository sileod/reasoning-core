from types import SimpleNamespace

import pytest

from reasoning_core.integrations import synlogic


@pytest.fixture
def register_game(monkeypatch):
    monkeypatch.setattr(synlogic, "_USABLE", None)

    def register(*answers):
        class Game:
            def __init__(self):
                self.calls = 0

            def generate(self, count, **kwargs):
                answer = answers[min(self.calls, len(answers) - 1)]
                self.calls += 1
                return [SimpleNamespace(
                    answer=answer, question="Test question", metadata={}, difficulty=1,
                )]

        registry = {"fake": Game}
        monkeypatch.setattr(synlogic, "discover_games", lambda: registry)
        task = object.__new__(synlogic.Synlogic)
        task.config = synlogic.SynlogicConfig(task="fake")
        task._reg = registry
        task._games = {}
        return task

    return register


@pytest.mark.parametrize("answer", [None, "", " \t\n"])
def test_missing_answers_are_excluded_from_usable_games(register_game, answer):
    register_game(answer)

    assert synlogic.usable_games() == []


@pytest.mark.parametrize("answer", [None, "", " \t\n"])
def test_missing_answers_are_rejected_during_generation(register_game, monkeypatch, answer):
    task = register_game(answer)
    monkeypatch.setattr(synlogic, "_USABLE", [])

    with pytest.raises(RuntimeError, match="No SynLogic game generated a concrete answer"):
        task.generate_entry()

    assert task._game("fake").calls == 24
    assert synlogic._USABLE == []


@pytest.mark.parametrize("answer", [0, 0.0, False, "answer", "None", " answer ", [1, 2], {"x": 1}])
def test_concrete_answers_are_usable_and_serialized(register_game, answer):
    task = register_game(answer)

    assert synlogic.usable_games() == ["fake"]
    entry = task.generate_entry()
    assert entry.answer == str(answer)
    assert entry.metadata.source_task == "fake"


@pytest.mark.parametrize("answer", [None, "", " \t\n"])
def test_generation_retries_missing_answers_and_accepts_zero(register_game, answer):
    task = register_game(answer, 0)
    assert synlogic.usable_games() == []

    assert task.generate_entry().answer == "0"
    assert task._game("fake").calls == 2
    assert synlogic._USABLE == ["fake"]

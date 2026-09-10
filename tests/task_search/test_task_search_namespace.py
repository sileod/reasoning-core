"""The fixed filesystem a worker sees, independent of the machine it runs on."""
from pathlib import Path

import pytest

from reasoning_core.task_search.namespace import (
    HOME,
    RUNTIME,
    WORKSPACE,
    Namespace,
    require_free_root,
)


def space(tmp_path):
    return Namespace(tmp_path / "worktree", tmp_path / "runtime")


def test_translate_maps_both_roots(tmp_path):
    got = space(tmp_path)
    assert got.translate(tmp_path / "worktree") == WORKSPACE
    assert got.translate(tmp_path / "worktree" / "a" / "b.py") == WORKSPACE / "a/b.py"
    assert got.translate(tmp_path / "runtime" / "trajectory.json") == RUNTIME / "trajectory.json"


def test_translate_refuses_a_path_it_does_not_own(tmp_path):
    """Returning it unchanged would leak the host silently, which is the whole failure."""
    with pytest.raises(ValueError, match="outside the sandbox namespace"):
        space(tmp_path).translate(tmp_path / "elsewhere" / "mini.yaml")


def test_the_environment_names_no_host_directory(tmp_path):
    values = space(tmp_path).environment()
    assert values["HOME"] == str(HOME)
    assert not any(str(tmp_path) in value for value in values.values())


def test_agy_keeps_the_real_home(tmp_path):
    """It authenticates through its own installation there; nothing else needs it."""
    assert "HOME" not in space(tmp_path).environment(home=False)
    assert str(HOME) not in space(tmp_path).binds("owned", home=False)


def test_owned_path_may_not_escape_the_worktree(tmp_path):
    with pytest.raises(ValueError, match="escapes worktree"):
        space(tmp_path).binds("../outside")


def test_this_machine_can_host_the_namespace():
    """A guard, not an assertion about the code: it fails where /home holds the toolchain."""
    require_free_root()

import random

from reasoning_core.tasks.generated.wave12.filesystem_path_resolution.filesystem_path_resolution import (
    FilesystemPathResolution,
    resolve_path,
)


def test_gold_scores_1():
    random.seed(1)
    task = FilesystemPathResolution()
    for _ in range(200):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_gold_matches_resolver():
    from .filesystem_path_resolution import _collect_links, resolve_path

    random.seed(5)
    task = FilesystemPathResolution()
    for _ in range(200):
        task.config.set_level(random.choice((0, 2, 5)))
        entry = task.generate_example()
        root = {}
        cur = root
        for nm in entry.metadata["chain"]:
            nxt = {}
            cur[nm] = nxt
            cur = nxt
        for name, tgt in entry.metadata["links"]:
            root[name] = tgt
        assert resolve_path(entry.metadata["path"].split("/"), root) == entry.answer


def test_rejects_wrong_labels():
    random.seed(2)
    task = FilesystemPathResolution()
    for _ in range(200):
        entry = task.generate_example()
        for wrong in ("RESOLVED", "LOOP", "ESCAPE"):
            if wrong != entry.answer:
                assert task.score_answer(wrong, entry) == 0.0
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("garbage", entry) == 0.0
        assert task.score_answer(3, entry) == 0.0


def test_all_labels_appear():
    random.seed(7)
    task = FilesystemPathResolution()
    seen = set()
    for _ in range(600):
        entry = task.generate_example()
        seen.add(entry.answer)
    assert seen == {"RESOLVED", "LOOP", "ESCAPE"}


def test_difficulty_changes_config():
    random.seed(3)
    base = FilesystemPathResolution().config
    high = FilesystemPathResolution()
    high.config.set_level(5)
    assert high.config.depth > base.depth
    assert high.config.nlinks > base.nlinks


def test_resolve_helper():
    root = {"a": {"b": {"c": {}}, "l": "a/b"}}
    assert resolve_path(["a", "l", "c"], root) == "RESOLVED"
    assert resolve_path(["..", "..", ".."], root) == "ESCAPE"

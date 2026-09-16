import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from de_re_de_dicto_evaluation import (
    NAMES,
    ROLES,
    DeReDeDictoConfig,
    DeReDeDictoEvaluation,
)


def test_generate_example_roundtrip():
    task = DeReDeDictoEvaluation()
    x = task.generate_example()
    assert x.metadata["_task"] == "de_re_de_dicto_evaluation"
    assert task.score_answer(x.answer, x) == 1.0


def test_metadata_json_serializable():
    import json

    task = DeReDeDictoEvaluation()
    x = task.generate_example()
    json.dumps(x.metadata)


def test_answer_format():
    task = DeReDeDictoEvaluation()
    for _ in range(40):
        x = task.generate_example()
        assert x.answer in {"TT", "TF", "FT", "FF"}


def test_verdicts_match_metadata():
    task = DeReDeDictoEvaluation()
    for _ in range(200):
        x = task.generate_example()
        re = "T" if x.metadata["de_re"] else "F"
        de = "T" if x.metadata["de_dicto"] else "F"
        assert x.answer == re + de


def test_all_four_pairs_appear():
    task = DeReDeDictoEvaluation()
    seen = set()
    for _ in range(2000):
        x = task.generate_example()
        seen.add(x.answer)
    assert seen == {"TT", "TF", "FT", "FF"}


def test_score_junk():
    task = DeReDeDictoEvaluation()
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("nonsense", x) < 1.0


def test_difficulty_changes():
    cfg = DeReDeDictoConfig()
    cfg.set_level(0)
    l0 = cfg.table_size
    cfg.set_level(6)
    assert cfg.table_size > l0


def test_surface_not_answer():
    task = DeReDeDictoEvaluation()
    for _ in range(200):
        x = task.generate_example()
        table = x.metadata["world_table"]
        assert x.answer not in table.replace("\n", " ")

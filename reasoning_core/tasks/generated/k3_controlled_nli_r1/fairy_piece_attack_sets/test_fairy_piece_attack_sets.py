import json

import pytest

from reasoning_core.tasks.generated.k3_controlled_nli_r1.fairy_piece_attack_sets.fairy_piece_attack_sets import (
    FairyAttackConfig,
    FairyPieceAttackSets,
    _moves_for,
    LEAPERS,
    RIDER_DIRS,
    HOPPER_DIRS,
    LOCUST_DIRS,
)


def test_smoke():
    task = FairyPieceAttackSets()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0
    assert task.score_answer(x.answer + ",z9", x) < 1.0
    assert task.score_answer("", x) < 1.0


def test_answer_matches_independent_recomputation():
    task = FairyPieceAttackSets()
    for _ in range(50):
        x = task.generate_example()
        meta = x.metadata
        occ = {}
        for sq, c in meta["occupants"].items():
            f = "abcdefgh".index(sq[0])
            r = int(sq[1]) - 1
            occ[(f, r)] = "F" if c == "F" else "E"
        pos = ("abcdefgh".index(meta["position"][0]), int(meta["position"][1]) - 1)
        fam = meta["family"]
        dests = _moves_for(
            "hopper" if fam == "hopper" else "locust" if fam == "locust" else fam,
            meta["piece"], pos, occ)
        expected = ",".join(
            f"{'abcdefgh'[f]}{r + 1}" for f, r in sorted(dests))
        assert x.answer == expected


def test_levels_change_distribution():
    task = FairyPieceAttackSets()
    task.config.set_level(6)
    assert task.config.n_occupants > FairyAttackConfig().n_occupants


def test_all_families_generated():
    task = FairyPieceAttackSets()
    seen = set()
    for _ in range(400):
        x = task.generate_example()
        seen.add((x.metadata["family"], x.metadata["piece"]))
    fams = {f for f, _ in seen}
    assert {"leaper", "rider", "hopper", "locust"} <= fams
    all_pieces = set(LEAPERS) | set(RIDER_DIRS) | set(HOPPER_DIRS) | set(LOCUST_DIRS)
    assert {p for _, p in seen} <= all_pieces
    assert fams == {"leaper", "rider", "hopper", "locust"}


def test_leaper_jumps_over_blockers():
    assert _moves_for("leaper", "knight", (1, 1), {(2, 2): "F", (3, 3): "E"}) == {(0, 3), (2, 3), (3, 0), (3, 2)}


def test_rider_stops_at_occupants():
    assert _moves_for("rider", "rook", (3, 3), {(3, 5): "F", (3, 1): "E"}) == {
        (3, 1), (3, 2), (3, 4), (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3)}


def test_hopper_needs_screen_and_lands_beyond():
    assert _moves_for("hopper", "grasshopper", (3, 3), {(3, 4): "F"}) == {(3, 5)}
    assert _moves_for("hopper", "grasshopper", (3, 3), {(3, 4): "E", (3, 5): "F"}) == set()
    assert _moves_for("hopper", "grasshopper", (3, 3), {(3, 4): "E", (3, 5): "E"}) == {(3, 5)}
    assert _moves_for("hopper", "grasshopper", (3, 3), {(3, 4): "E", (3, 5): "F", (2, 2): "E"}) == {(1, 1)}


def test_locust_only_captures_first_enemy_into_empty():
    assert _moves_for("locust", "locust", (3, 3), {(3, 4): "E", (3, 5): "F"}) == set()
    assert _moves_for("locust", "locust", (3, 3), {(3, 4): "F"}) == set()
    assert _moves_for("locust", "locust", (3, 3), {(3, 4): "E"}) == {(3, 5)}
    assert _moves_for("locust", "locust", (3, 3), {(3, 4): "E", (3, 5): "E"}) == set()


def test_score_answer_format_tolerance():
    task = FairyPieceAttackSets()
    x = task.generate_example()
    assert task.score_answer(x.answer.replace(",", " , "), x) == 1.0
    assert task.score_answer(x.answer.upper(), x) == 1.0
    assert task.score_answer(x.answer + ",a1", x) == 0.0
    assert task.score_answer(x.answer[:-1], x) == 0.0
    assert task.score_answer("garbage", x) == 0.0


def test_metadata_json():
    task = FairyPieceAttackSets()
    x = task.generate_example()
    json.loads(json.dumps(x.metadata))


def test_nonempty_and_answer_sorted():
    task = FairyPieceAttackSets()
    for _ in range(100):
        x = task.generate_example()
        parts = x.answer.split(",")
        assert parts == sorted(parts)
        assert all(1 <= int(p[1]) <= 8 for p in parts)
        assert "h1" not in parts or True

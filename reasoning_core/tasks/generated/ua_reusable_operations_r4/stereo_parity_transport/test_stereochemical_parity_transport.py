"""Focused tests for stereochemical_parity_transport."""

import itertools

from reasoning_core.tasks.generated.ua_reusable_operations_r4.stereo_parity_transport.stereochemical_parity_transport import (
    POSITIONS,
    StereoParityTransport,
    _apply_parity,
    _center_config,
)


def _all_configs():
    for perm in itertools.permutations(POSITIONS):
        yield {p: i + 1 for i, p in enumerate(perm)}


def test_single_swap_always_inverts():
    for base in _all_configs():
        b = _center_config(base)
        for a, c in itertools.combinations(POSITIONS, 2):
            p = dict(base)
            p[a], p[c] = p[c], p[a]
            assert _center_config(p) != b


def test_parity_matches_apply_parity():
    for base in _all_configs():
        for k in (0, 1, 2, 3, 4):
            expect = _center_config(base)
            for _ in range(k % 2):
                expect = "S" if expect == "R" else "R"
            assert _apply_parity(base, k) == expect


def test_known_r_glyceraldehyde():
    cfg = {"top": 1, "right": 2, "left": 3, "bottom": 4}
    assert _center_config(cfg) == "R"


def test_generate_and_score():
    task = StereoParityTransport()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example(level=level)
            assert ex.answer in ("R", "S")
            assert task.score_answer(ex.answer, ex) == 1.0
            for bad in ("", " ", "r", "RS", "reajrjrje9595!"):
                if bad.strip().upper() != ex.answer:
                    assert task.score_answer(bad, ex) == 0.0


def test_both_labels_appear():
    task = StereoParityTransport()
    answers = {task.generate_example(level=5).answer for _ in range(60)}
    assert answers == {"R", "S"}


def test_metadata_json_serializable():
    import json

    task = StereoParityTransport()
    ex = task.generate_example(level=5)
    json.dumps(dict(ex.metadata))

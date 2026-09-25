import random

from reasoning_core.tasks.generated.ua_relational_structures_r4.event_structure_residualization.event_structure_residualization import (
    EventStructureResidualization,
    EventResidualConfig,
    _parse_ids,
    _fmt,
)


def _fresh():
    return EventStructureResidualization()


def test_gold_scores_at_every_level():
    task = _fresh()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_and_empty_never_score():
    task = _fresh()
    for _ in range(20):
        ex = task.generate_example()
        for bad in ("", " ", "reajrjrje9595!", "none", "1 2 3", "[]" if ex.answer != "[]" else "x"):
            if bad == ex.answer:
                continue
            assert task.score_answer(bad, ex) < 1.0


def test_enabled_is_subset_of_residual_not_config():
    task = _fresh()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            meta = ex.metadata
            C = set(meta["config"])
            enabled = set(_parse_ids(ex.answer))
            assert enabled.isdisjoint(C)
            assert enabled.issubset(set(meta["ids"]))


def test_distance_from_surface_shortcuts():
    task = _fresh()
    task.config.set_level(3)
    hits = 0
    n = 60
    for _ in range(n):
        ex = task.generate_example()
        prompt = ex.prompt
        numbers = []
        import re
        for tok in re.findall(r"-?\d+", prompt):
            numbers.append(tok)
        surface_guesses = {
            numbers[-1] if numbers else "",
            numbers[0] if numbers else "",
        }
        for guess in surface_guesses:
            if task.score_answer(guess, ex) == 1.0:
                hits += 1
    assert hits / n < 0.1


def test_level_changes_config():
    config = EventResidualConfig()
    config.set_level(0)
    n0 = config.n_events
    config.set_level(6)
    n6 = config.n_events
    assert n6 > n0


def test_parse_ids_handles_formats():
    assert _parse_ids("[3, 5]") == [3, 5]
    assert _parse_ids("[]") == []
    assert _parse_ids("[1,1,2]") == [1, 2]
    assert _parse_ids("3 5") == [3, 5]
    assert _parse_ids("") is None
    assert _parse_ids("   ") is None
    assert _parse_ids("ab") is None
    assert _fmt([3, 5]) == "[3, 5]"


def test_answer_independently_recomputed_from_metadata():
    task = _fresh()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            meta = ex.metadata
            C = set(meta["config"])
            rev = {}
            for a, b in meta["causal"]:
                rev.setdefault(b, []).append(a)
            excluded = set()
            for a, b in meta["conflict"]:
                if a in C:
                    excluded.add(b)
                if b in C:
                    excluded.add(a)
            recomputed = sorted(
                e for e in meta["ids"]
                if e not in C and e not in excluded
                and all(p in C for p in rev.get(e, ()))
            )
            assert _parse_ids(ex.answer) == recomputed


def test_empty_answer_is_not_dominant():
    task = _fresh()
    empties = 0
    total = 0
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(40):
            ex = task.generate_example()
            total += 1
            if ex.answer == "[]":
                empties += 1
    assert empties / total < 0.6


def test_deterministic_under_module_seed():
    a = _fresh()
    b = _fresh()
    random.seed(12345)
    ea = a.generate_example()
    random.seed(12345)
    eb = b.generate_example()
    assert ea.answer == eb.answer
    assert ea.metadata["causal"] == eb.metadata["causal"]
    assert ea.metadata["conflict"] == eb.metadata["conflict"]
    assert ea.metadata["config"] == eb.metadata["config"]

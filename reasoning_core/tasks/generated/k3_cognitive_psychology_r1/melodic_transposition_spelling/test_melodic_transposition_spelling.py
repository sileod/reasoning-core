import json
import random
from collections import Counter

import pytest

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.melodic_transposition_spelling.melodic_transposition_spelling import (
    ACC_STR, INTERVALS, LETTERS, NATURAL, MelodicTranspositionSpelling,
    _pc, _signature, _spell, _tonic, _transpose,
)


@pytest.mark.parametrize("level", range(7))
def test_gold_and_prompt_roundtrip(level):
    task = MelodicTranspositionSpelling()
    task.config.set_level(level)
    random.seed(1000 + level)
    modes = set()
    prompts = {}
    for _ in range(60):
        entry = task.generate_entry()
        m = entry.metadata
        modes.add(m["mode"])
        assert task.score_answer(entry.answer, entry) == 1.0
        for junk in ("", "junk junk junk", None, [], "F#", entry.answer + " extra"):
            assert task.score_answer(junk, entry) == 0.0
        copied = json.loads(json.dumps(m))
        prompt = task.render_prompt(copied)
        assert prompt == task.render_prompt(m)
        assert prompts.setdefault(prompt, entry.answer) == entry.answer
        source_key = _signature(m["source_signature"])
        for token, source in zip(m["melody"], m["source_notes"]):
            acc = source_key[token[0]] if len(token) == 1 else next(
                acc for acc, suffix in ACC_STR.items() if suffix == token[1:])
            assert source == [token[0], acc]
        steps = sum(stage[1] for stage in m["stages"])
        semis = sum(stage[2] for stage in m["stages"])
        for source, target in zip(m["source_notes"], m["transposed"]):
            assert (LETTERS.index(target[0]) - LETTERS.index(source[0])) % 7 == steps % 7
            assert (_pc(target) - _pc(source)) % 12 == semis % 12
        if m["mode"] == "notes":
            assert entry.answer == " ".join(map(_spell, m["transposed"]))
        else:
            assert all(_signature(m["final_signature"])[letter] == acc
                       for letter, acc in m["transposed"])
    assert modes == {"notes", "key_signature"}


@pytest.mark.parametrize("pos,tonic", [(-7, ("C", -1)), (-6, ("G", -1)),
    (-1, ("F", 0)), (0, ("C", 0)), (1, ("G", 0)), (6, ("F", 1)), (7, ("C", 1))])
def test_known_keys(pos, tonic):
    assert _tonic(pos) == tonic
    signature = _signature(pos)
    assert sum(abs(acc) for acc in signature.values()) == abs(pos)
    assert sorted((_pc((letter, acc)) - _pc(tonic)) % 12
                  for letter, acc in signature.items()) == [0, 2, 4, 5, 7, 9, 11]


@pytest.mark.parametrize("source,steps,semis,target", [
    (("C", 0), 4, 7, ("G", 0)),
    (("B", 0), 1, 2, ("C", 1)),
    (("F", 1), 2, 4, ("A", 1)),
    (("B", -1), -2, -3, ("G", 0)),
    (("F", 1), 3, 6, ("B", 1)),
    (("F", 1), 4, 6, ("C", 0)),
    (("G", 1), 6, 11, ("F", 2)),
    (("C", -1), -1, -2, ("B", -2)),
])
def test_known_spelled_intervals(source, steps, semis, target):
    assert _transpose(source, steps, semis) == target
    assert _transpose(target, -steps, -semis) == source


def test_exhaustive_against_absolute_staff_arithmetic():
    for _, steps, semis in INTERVALS:
        for direction in (-1, 1):
            for index, letter in enumerate(LETTERS):
                target_index = index + direction * steps
                target_letter = LETTERS[target_index % 7]
                target_natural = NATURAL[target_letter] + 12 * (target_index // 7)
                for acc in ACC_STR:
                    target_acc = NATURAL[letter] + acc + direction * semis - target_natural
                    expected = (target_letter, target_acc) if target_acc in ACC_STR else None
                    assert _transpose((letter, acc), direction * steps, direction * semis) == expected


def test_scorer_is_self_free_and_enforces_spelling():
    class NoAttributes:
        def __getattribute__(self, name):
            raise AssertionError(name)

    entry = Entry(metadata={"mode": "notes"}, answer="Gn F# Bbb")
    score = MelodicTranspositionSpelling.score_answer
    assert score(NoAttributes(), "  Gn  F# Bbb\n", entry) == 1.0
    for wrong in ("F## F# Bbb", "G F# Bbb", "Gn Gb An", "Gn F# Bb"):
        assert score(NoAttributes(), wrong, entry) == 0.0


@pytest.mark.parametrize("level", (0, 3, 6))
def test_determinism_and_signature_balance(level):
    def generate():
        random.seed(4200 + level)
        task = MelodicTranspositionSpelling()
        task.config.set_level(level)
        return [task.generate_entry() for _ in range(180)]

    first, second = generate(), generate()
    assert [(e.metadata, e.answer) for e in first] == [(e.metadata, e.answer) for e in second]
    counts = Counter(e.answer for e in first if e.metadata["mode"] == "key_signature")
    assert len(counts) >= 13
    assert max(counts.values()) / sum(counts.values()) < 0.2


def test_difficulty_adds_composition_depth():
    task = MelodicTranspositionSpelling()
    previous = (0, 0, 0)
    for level in range(7):
        task.config.set_level(level)
        current = (task.config.n_notes, task.config.n_stages, task.config.chromatic_prob)
        assert all(a <= b for a, b in zip(previous, current))
        previous = current
    assert task.config.n_stages == 4

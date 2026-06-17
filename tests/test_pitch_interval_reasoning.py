import random

import pytest
from music21 import converter as music21_converter

from reasoning_core.template import Problem
from reasoning_core.tasks._music_theory import (
    ABC_KEY_SIGNATURES,
    ABCContext,
    AnswerNormalizer,
    FULL_ABC_SCORE_STYLE,
    Interval,
    Note,
    NoteRenderer,
    Scale,
)
from reasoning_core.tasks.pitch_interval_reasoning import (
    MODE_NAMES,
    PitchIntervalConfig,
    PitchIntervalReasoning,
    TRANSPOSING_INSTRUMENTS,
)


def _problem(answer, answer_kind="text", **metadata):
    return Problem(metadata={"answer_kind": answer_kind, **metadata}, answer=answer)


def _abc_fragment_from_prompt(prompt):
    lines = prompt.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("L:"))
    end = next(
        (i for i in range(start, len(lines)) if lines[i].startswith("Interpret ")),
        len(lines),
    )
    return "\n".join(lines[start:end])


def _render_expected_note_answer(note, style, with_octave):
    answer_style, _answer_notation, force_answer_natural = NoteRenderer.answer_rendering(style)
    return NoteRenderer.note(
        note,
        answer_style,
        with_octave=with_octave,
        force_natural=force_answer_natural,
        quote_abc=False,
    )


def test_score_answer_normalizes_music_answer_variants():
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="interval_naming"))

    assert task.score_answer(
        "double augmented eleventh.",
        _problem("double-augmented eleventh", answer_kind="interval"),
    ) == 1.0
    assert task.score_answer("double octave", _problem("perfect fifteenth", answer_kind="interval")) == 1.0
    assert task.score_answer("B", _problem("=B", answer_kind="note", answer_notation="compact ABC notation")) == 1.0
    assert task.score_answer('"=B"', _problem("B", answer_kind="note", answer_notation="compact ABC notation")) == 1.0
    assert task.score_answer("4", _problem(4, answer_kind="integer")) == 1.0
    assert task.score_answer("4.0", _problem(4, answer_kind="integer")) == 0.0


@pytest.mark.parametrize("mode", MODE_NAMES)
def test_generated_examples_have_valid_answers_for_each_mode(mode):
    random.seed(1000 + MODE_NAMES.index(mode))
    task = PitchIntervalReasoning(PitchIntervalConfig(mode=mode))

    for level in [0, 3, 5]:
        example = task.generate_example(level=level)

        assert example.metadata.mode == mode
        assert example.prompt
        assert example.metadata.cot
        assert task.score_answer(example.answer, example) == 1.0


def test_full_abc_interval_naming_prompt_contains_parseable_score(monkeypatch):
    context = ABCContext("1/8", "4/4", "Eb", ABC_KEY_SIGNATURES["Eb"])
    monkeypatch.setattr(PitchIntervalConfig, "random_style", lambda self: FULL_ABC_SCORE_STYLE)
    monkeypatch.setattr(ABCContext, "random", classmethod(lambda cls: context))

    random.seed(5050)
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="interval_naming"))
    example = task.generate_example(level=3)
    abc_fragment = _abc_fragment_from_prompt(example.prompt)
    parsed_score = music21_converter.parse(abc_fragment, format="abc")
    parsed_chords = list(parsed_score.flatten().notes)

    assert example.metadata.style == FULL_ABC_SCORE_STYLE
    assert "Interpret the score using its key signature" in example.prompt
    assert "score note" in example.metadata.cot
    assert len(parsed_chords) == 1
    assert len(parsed_chords[0].pitches) == 2
    assert task.score_answer(example.answer, example) == 1.0


def test_interval_naming_answer_matches_metadata_notes():
    random.seed(7070)
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="interval_naming"))

    for _ in range(40):
        example = task.generate_example(level=5)
        expected = Interval.between(
            Note.parse(example.metadata.start_note),
            Note.parse(example.metadata.end_note),
        ).name()

        assert example.answer == expected


def test_pitch_count_answer_matches_metadata_pitch_classes():
    random.seed(7170)
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="pitch_count"))

    for _ in range(40):
        example = task.generate_example(level=5)
        expected = len({Note.parse(note).pc for note in example.metadata.notes})

        assert int(example.answer) == expected


def test_interval_classification_answer_matches_scale_relation():
    random.seed(7270)
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="interval_classification"))

    for _ in range(80):
        example = task.generate_example(level=5)
        scale = Scale.build(
            Note.parse(example.metadata.tonic_note),
            example.metadata.scale_mode,
        )
        expected = scale.relation_label(
            Note.parse(example.metadata.start_note),
            Note.parse(example.metadata.end_note),
        )

        assert example.answer == expected


def test_interval_arithmetic_metadata_reconstructs_answer():
    random.seed(7370)
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="interval_arithmetic"))

    for _ in range(60):
        example = task.generate_example(level=5)
        current = Interval(
            example.metadata.start_interval_quality,
            example.metadata.start_interval_number,
        )
        for step in example.metadata.operations:
            operation = step["operation"]
            if operation == "add":
                current = current.add(Interval(step["interval_quality"], step["interval_number"]))
            elif operation == "subtract":
                current = current.subtract(Interval(step["interval_quality"], step["interval_number"]))
            elif operation == "reduce_then_invert":
                current = current.reduced().inverted()
            else:
                raise AssertionError(f"Unsupported operation in metadata: {operation}")

        assert AnswerNormalizer.interval(example.answer) == AnswerNormalizer.interval(current.name())


def test_instrument_transposition_metadata_reconstructs_answer():
    random.seed(7470)
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="instrument_transposition"))
    instruments = {
        instrument: Interval(quality, number)
        for instrument, quality, number in TRANSPOSING_INSTRUMENTS
    }

    for _ in range(40):
        example = task.generate_example(level=5)
        written = Note.parse(example.metadata.written_note)
        sounding = instruments[example.metadata.instrument].construct_from(written, direction="down")
        expected = _render_expected_note_answer(sounding, example.metadata.style, with_octave=True)

        assert AnswerNormalizer.note(example.answer, example.metadata.answer_notation) == AnswerNormalizer.note(
            expected,
            example.metadata.answer_notation,
        )


def test_interval_construction_metadata_reconstructs_answer():
    random.seed(7570)
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="interval_construction"))
    seen_cases = set()

    for _ in range(80):
        example = task.generate_example(level=5)
        seen_cases.add((example.metadata.prompt_has_octave, example.metadata.answer_has_octave))
        start = Note.parse(example.metadata.start_note)
        interval = Interval(
            example.metadata.interval_quality,
            example.metadata.interval_number,
        )
        target = interval.construct_from(start, direction=example.metadata.direction)
        answer_note = target if example.metadata.answer_has_octave else target.without_octave()
        expected = _render_expected_note_answer(
            answer_note,
            example.metadata.style,
            with_octave=example.metadata.answer_has_octave,
        )

        assert AnswerNormalizer.note(example.answer, example.metadata.answer_notation) == AnswerNormalizer.note(
            expected,
            example.metadata.answer_notation,
        )

    assert seen_cases == {(True, True), (True, False), (False, False)}


def test_mode_any_samples_supported_modes_and_scores_answers():
    random.seed(2024)
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="any"))
    seen_modes = set()

    for _ in range(100):
        example = task.generate_example(level=3)
        seen_modes.add(example.metadata.mode)
        assert example.metadata.mode in MODE_NAMES
        assert task.score_answer(example.answer, example) == 1.0

    assert len(seen_modes) > 1


def test_unknown_mode_is_rejected_before_retry_loop():
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="not_a_mode"))

    with pytest.raises(ValueError, match="Unknown pitch interval mode"):
        task.generate()


def test_high_level_transposition_chain_keeps_generated_steps_valid():
    random.seed(3030)
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="transposition_chain"))

    for _ in range(100):
        example = task.generate_example(level=5)

        assert len(example.metadata.steps) == example.metadata._config["chain_len"]
        assert task.score_answer(example.answer, example) == 1.0
        assert "unsupported accidental" not in example.metadata.cot


def test_transposition_chain_metadata_reconstructs_answer():
    random.seed(7670)
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="transposition_chain"))

    for _ in range(60):
        example = task.generate_example(level=5)
        current = Note.parse(example.metadata.start_note)
        for step in example.metadata.steps:
            interval = Interval(step["interval_quality"], step["interval_number"])
            current = interval.construct_from(current, direction=step["direction"])
        expected = _render_expected_note_answer(
            current.without_octave(),
            example.metadata.style,
            with_octave=False,
        )

        assert AnswerNormalizer.note(example.answer, example.metadata.answer_notation) == AnswerNormalizer.note(
            expected,
            example.metadata.answer_notation,
        )


def test_interval_arithmetic_chain_length_tracks_chain_len():
    random.seed(4040)
    task = PitchIntervalReasoning(PitchIntervalConfig(mode="interval_arithmetic"))

    example = task.generate_example(level=5)

    assert len(example.metadata.operations) == example.metadata._config["chain_len"]
    assert {step["operation"] for step in example.metadata.operations} <= {"add", "subtract", "reduce_then_invert"}
    assert task.score_answer(example.answer, example) == 1.0


def test_interval_classification_key_complexity_limits_tonics():
    random.seed(6060)
    task = PitchIntervalReasoning(
        PitchIntervalConfig(mode="interval_classification", key_complexity=0)
    )

    for _ in range(40):
        example = task.generate_example(level=0)

        if example.metadata.scale_mode == "major":
            assert example.metadata.tonic_note == "C"
        else:
            assert example.metadata.tonic_note == "A"
        assert task.score_answer(example.answer, example) == 1.0

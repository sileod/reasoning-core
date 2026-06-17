import random
import re

import pytest
from music21 import chord as music21_chord
from music21 import key as music21_key
from music21 import roman as music21_roman

from reasoning_core.template import Problem
from reasoning_core.tasks._music_theory import (
    AnswerNormalizer,
    COMPACT_ABC_STYLE,
    FULL_ABC_SCORE_STYLE,
    Music21Adapter,
    Note,
    SPN_STYLE,
    key_tonics,
)
from reasoning_core.tasks.chord_roman_reasoning import (
    CHROMATIC_CHORDS,
    CHROMATIC_SCALE_DEGREE_FORMULAS,
    ENHARMONIC_OPENERS,
    MODE_NAMES,
    ROMAN_MAJOR_SECONDARY_SEVENTHS,
    ROMAN_MAJOR_SECONDARY_TRIADS,
    ROMAN_MINOR_SECONDARY_SEVENTHS,
    ROMAN_MINOR_SECONDARY_TRIADS,
    ChordRomanConfig,
    ChordRomanReasoning,
)


COMMON_NAME_BY_LABEL = {
    "major triad": "major triad",
    "minor triad": "minor triad",
    "diminished triad": "diminished triad",
    "augmented triad": "augmented triad",
    "major seventh": "major seventh chord",
    "dominant seventh": "dominant seventh chord",
    "minor seventh": "minor seventh chord",
    "half-diminished seventh": "half-diminished seventh chord",
    "fully diminished seventh": "diminished seventh chord",
    "minor-major seventh": "minor-augmented tetrachord",
    "augmented-major seventh": "augmented major tetrachord",
}


def _problem(answer, answer_kind="text", **metadata):
    return Problem(metadata={"answer_kind": answer_kind, **metadata}, answer=answer)


def _music21_key_from_label(label):
    tonic, mode = label.split(maxsplit=1)
    if mode == "minor":
        return music21_key.Key(tonic, "minor")
    return music21_key.Key(tonic)


def _pitch_class(note_name, answer_notation=None):
    normalized = AnswerNormalizer.note(note_name, answer_notation)
    if type(answer_notation) == str and "ABC" in answer_notation:
        match = re.fullmatch(r"(\^\^|__|\^|_|=)?([A-Ga-g])([,']*)", normalized)
        if not match:
            raise ValueError(f"Invalid compact ABC note: {note_name!r}")
        accidental_token, letter, _octave_marks = match.groups()
        accidental = {"^^": 2, "^": 1, None: 0, "=": 0, "_": -1, "__": -2}[accidental_token]
        return Note(letter.upper(), accidental).pc
    return Note.parse(normalized).pc


def _pitch_classes(note_names, answer_notation=None):
    return {_pitch_class(note, answer_notation) for note in note_names}


def _music21_pitch_name(note_name):
    return note_name.replace("bb", "--").replace("b", "-")


@pytest.mark.parametrize("mode", MODE_NAMES)
def test_generated_examples_have_valid_answers_for_each_mode(mode):
    random.seed(2000 + MODE_NAMES.index(mode))
    task = ChordRomanReasoning(ChordRomanConfig(mode=mode))

    for level in [0, 3, 5]:
        example = task.generate_example(level=level)

        assert example.metadata.mode == mode
        assert example.prompt
        assert example.metadata.cot
        assert task.score_answer(example.answer, example) == 1.0


def test_chord_quality_labels_match_music21_common_names():
    random.seed(3100 + MODE_NAMES.index("chord_quality"))
    task = ChordRomanReasoning(ChordRomanConfig(mode="chord_quality"))

    seen_sizes = set()
    for _ in range(60):
        example = task.generate_example(level=5)
        seen_sizes.add(len(example.metadata.chord_notes))
        chord = music21_chord.Chord([_music21_pitch_name(note) for note in example.metadata.chord_notes])

        assert chord.commonName == COMMON_NAME_BY_LABEL[example.answer]

    assert seen_sizes == {3, 4}


def test_enharmonic_chord_equivalence_samples_chords_with_and_without_octaves():
    seen_octave_settings = set()

    for seed in range(7000, 7060):
        random.seed(seed)
        task = ChordRomanReasoning(ChordRomanConfig(mode="enharmonic_chord_equivalence"))
        example = task.generate_example(level=5)
        seen_octave_settings.add(example.metadata.with_octave)

        assert task.score_answer(example.answer, example) == 1.0
        assert all(
            any(char.isdigit() for char in note) == example.metadata.with_octave
            for note in example.metadata.first_chord
        )
        assert all(
            any(char.isdigit() for char in note) == example.metadata.with_octave
            for note in example.metadata.second_chord
        )

    assert seen_octave_settings == {False, True}


def test_full_abc_chord_prompts_do_not_duplicate_chord_phrases():
    chord_prompt_modes = [
        "chord_quality",
        "inversion",
        "open_close_voicing",
        "enharmonic_chord_equivalence",
        "chromatic_chord_label",
        "chord_membership",
        "roman_numeral_from_chord",
    ]
    bad_fragments = [
        "the chord the chord",
        "chord tones the chord",
        "chord-tone collection the chord",
        "the chromatic chord the chord",
        "written chords the chord",
    ]

    for mode in chord_prompt_modes:
        random.seed(8100 + MODE_NAMES.index(mode))
        config = ChordRomanConfig(mode=mode)
        config.random_style = lambda: FULL_ABC_SCORE_STYLE
        task = ChordRomanReasoning(config)
        example = task.generate_example(level=5)

        assert not any(fragment in example.prompt for fragment in bad_fragments)


def test_full_abc_chord_prompts_include_key_resolution_cot():
    chord_prompt_modes = [
        "chord_quality",
        "inversion",
        "open_close_voicing",
        "enharmonic_chord_equivalence",
        "chromatic_chord_label",
        "chord_membership",
        "roman_numeral_from_chord",
    ]

    for mode in chord_prompt_modes:
        random.seed(9100 + MODE_NAMES.index(mode))
        config = ChordRomanConfig(mode=mode)
        config.random_style = lambda: FULL_ABC_SCORE_STYLE
        task = ChordRomanReasoning(config)
        example = task.generate_example(level=5)

        assert "ABC score fragment" in example.prompt
        assert "Interpret the score using its key signature" in example.prompt
        assert "score note" in example.metadata.cot


def test_chromatic_chord_labels_match_music21_roman_spellings():
    random.seed(4100)
    task = ChordRomanReasoning(ChordRomanConfig(mode="chromatic_chord_label"))
    known_figures = {label: figure for label, figure in CHROMATIC_CHORDS}
    seen_modes = set()
    seen_octave_settings = set()

    for _ in range(60):
        example = task.generate_example(level=5)
        seen_modes.add(example.metadata.key.split(maxsplit=1)[1])
        seen_octave_settings.add(example.metadata.with_octave)
        rn = music21_roman.RomanNumeral(
            known_figures[example.answer],
            _music21_key_from_label(example.metadata.key),
        )
        expected_chord_notes = [
            (pitch.nameWithOctave if example.metadata.with_octave else pitch.name).replace("-", "b")
            for pitch in rn.pitches
        ]
        expected_bass_note = (
            rn.bass().nameWithOctave
            if example.metadata.with_octave
            else rn.bass().name
        ).replace("-", "b")

        assert expected_chord_notes == example.metadata.chord_notes
        assert expected_bass_note == example.metadata.bass_note
        assert f"scale-degree formula is {CHROMATIC_SCALE_DEGREE_FORMULAS[example.answer]}" in example.metadata.cot

    assert seen_modes == {"major", "minor"}
    assert seen_octave_settings == {False, True}


def test_chromatic_chord_label_arrangement_cot_matches_octave_policy():
    seen_octave_settings = set()

    for seed in range(9200, 9300):
        random.seed(seed)
        task = ChordRomanReasoning(ChordRomanConfig(mode="chromatic_chord_label"))
        example = task.generate_example(level=5)
        seen_octave_settings.add(example.metadata.with_octave)
        arrangement_phrase = "Arrange the chord tones from the specified bass upward"

        if example.metadata.with_octave:
            assert arrangement_phrase not in example.metadata.cot
        else:
            assert arrangement_phrase in example.metadata.cot

    assert seen_octave_settings == {False, True}


@pytest.mark.parametrize("mode", ["chord_membership", "roman_numeral_from_chord"])
def test_chord_context_modes_sample_chords_with_and_without_octaves(mode):
    seen_octave_settings = set()

    for seed in range(8200, 8260):
        random.seed(seed + MODE_NAMES.index(mode))
        task = ChordRomanReasoning(ChordRomanConfig(mode=mode))
        example = task.generate_example(level=5)
        seen_octave_settings.add(example.metadata.with_octave)

        assert task.score_answer(example.answer, example) == 1.0
        assert all(
            any(char.isdigit() for char in note) == example.metadata.with_octave
            for note in example.metadata.chord_notes
        )
        if mode == "roman_numeral_from_chord":
            assert any(char.isdigit() for char in example.metadata.bass_note) == example.metadata.with_octave

    assert seen_octave_settings == {False, True}


@pytest.mark.parametrize("mode", ["roman_numeral_from_chord", "chord_from_roman_numeral"])
def test_roman_modes_round_trip_with_music21(mode):
    random.seed(5100 + MODE_NAMES.index(mode))
    task = ChordRomanReasoning(ChordRomanConfig(mode=mode))

    for _ in range(20):
        example = task.generate_example(level=5)
        rn = music21_roman.RomanNumeral(example.metadata.roman_figure, _music21_key_from_label(example.metadata.key))
        rn_pitch_classes = {pitch.pitchClass for pitch in rn.pitches}
        if mode == "roman_numeral_from_chord":
            assert rn_pitch_classes == _pitch_classes(example.metadata.chord_notes)
            assert rn.bass().pitchClass == _pitch_class(example.metadata.bass_note)
        else:
            assert rn_pitch_classes == _pitch_classes(example.metadata.chord_notes)
            assert rn.bass().pitchClass == _pitch_class(example.metadata.chord_notes[0])
            assert rn_pitch_classes == _pitch_classes(
                AnswerNormalizer.note_sequence(
                    example.answer,
                    example.metadata.answer_notation,
                ),
                example.metadata.answer_notation,
            )


def test_chord_from_roman_answer_notation_follows_prompt_style():
    expected = {
        SPN_STYLE: ("scientific pitch notation", False),
        COMPACT_ABC_STYLE: ("compact ABC notation", False),
        FULL_ABC_SCORE_STYLE: ("compact ABC notation", True),
    }

    for style, (answer_notation, explicit_accidentals) in expected.items():
        random.seed(9300)
        config = ChordRomanConfig(mode="chord_from_roman_numeral")
        config.random_style = lambda style=style: style
        task = ChordRomanReasoning(config)
        example = task.generate_example(level=5)

        assert example.metadata.answer_notation == answer_notation
        assert example.metadata.answer_explicit_accidentals is explicit_accidentals
        assert '"' not in example.answer
        assert task.score_answer(example.answer, example) == 1.0
        if explicit_accidentals:
            assert "with any accidental made explicit" in example.prompt


def test_score_answer_normalizes_roman_and_note_sequence_answers():
    task = ChordRomanReasoning(ChordRomanConfig(mode="chord_from_roman_numeral"))

    assert task.score_answer(" V 6 5. ", _problem("V65", answer_kind="roman")) == 1.0
    assert task.score_answer("vii/o65", _problem("viiø65", answer_kind="roman")) == 1.0
    assert task.score_answer("C# - E - G", _problem("C#-E-G", answer_kind="note_sequence")) == 1.0
    assert (
        task.score_answer(
            "C - ^F",
            _problem("=C-^F", answer_kind="note_sequence", answer_notation="compact ABC notation"),
        )
        == 1.0
    )
    assert task.score_answer("yes", _problem("yes", answer_kind="yes_no")) == 1.0
    assert task.score_answer("major   triad.", _problem("major triad", answer_kind="label")) == 1.0
    assert AnswerNormalizer.text("Major   Triad.") == "major triad"


def test_enharmonic_openers_use_clear_pitch_class_wording():
    assert not any("sound as the same pitch-class set" in opener for opener in ENHARMONIC_OPENERS)
    assert any("represent the same pitch-class set" in opener for opener in ENHARMONIC_OPENERS)


def test_roman_figure_sampling_uses_mode_specific_diatonic_pools(monkeypatch):
    config = ChordRomanConfig(mode="roman_numeral_from_chord")
    monkeypatch.setattr(random, "random", lambda: 1.0)
    task = ChordRomanReasoning(config)

    task._sample_chord_size = lambda: 3
    major_triads = {task._sample_roman_figure("major") for _ in range(100)}
    minor_triads = {task._sample_roman_figure("minor") for _ in range(100)}
    triad_suffixes = ("", "6", "64")
    assert major_triads <= {
        ChordRomanReasoning._with_roman_inversion(base, suffix)
        for base in ("I", "ii", "iii", "IV", "V", "vi", "viio")
        for suffix in triad_suffixes
    }
    assert minor_triads <= {
        ChordRomanReasoning._with_roman_inversion(base, suffix)
        for base in ("i", "iio", "III", "iv", "V", "VI", "viio")
        for suffix in triad_suffixes
    }

    task._sample_chord_size = lambda: 4
    major_sevenths = {task._sample_roman_figure("major") for _ in range(100)}
    minor_sevenths = {task._sample_roman_figure("minor") for _ in range(100)}
    seventh_suffixes = ("7", "65", "43", "42")
    assert major_sevenths <= {
        ChordRomanReasoning._with_roman_inversion(base, suffix)
        for base in ("I7", "ii7", "iii7", "IV7", "V7", "vi7", "vii/o7")
        for suffix in seventh_suffixes
    }
    assert minor_sevenths <= {
        ChordRomanReasoning._with_roman_inversion(base, suffix)
        for base in ("i7", "ii/o7", "III7", "iv7", "V7", "VI7", "viio7")
        for suffix in seventh_suffixes
    }


def test_roman_figure_sampling_uses_mode_specific_secondary_pools(monkeypatch):
    config = ChordRomanConfig(mode="roman_numeral_from_chord")
    monkeypatch.setattr(random, "random", lambda: 0.0)
    task = ChordRomanReasoning(config)

    task._sample_chord_size = lambda: 3
    major_triads = {task._sample_roman_figure("major") for _ in range(100)}
    minor_triads = {task._sample_roman_figure("minor") for _ in range(100)}
    triad_suffixes = ("", "6", "64")
    assert major_triads <= {
        ChordRomanReasoning._with_roman_inversion(base, suffix)
        for base in ROMAN_MAJOR_SECONDARY_TRIADS
        for suffix in triad_suffixes
    }
    assert minor_triads <= {
        ChordRomanReasoning._with_roman_inversion(base, suffix)
        for base in ROMAN_MINOR_SECONDARY_TRIADS
        for suffix in triad_suffixes
    }

    task._sample_chord_size = lambda: 4
    major_sevenths = {task._sample_roman_figure("major") for _ in range(100)}
    minor_sevenths = {task._sample_roman_figure("minor") for _ in range(100)}
    seventh_suffixes = ("7", "65", "43", "42")
    assert major_sevenths <= {
        ChordRomanReasoning._with_roman_inversion(base, suffix)
        for base in ROMAN_MAJOR_SECONDARY_SEVENTHS
        for suffix in seventh_suffixes
    }
    assert minor_sevenths <= {
        ChordRomanReasoning._with_roman_inversion(base, suffix)
        for base in ROMAN_MINOR_SECONDARY_SEVENTHS
        for suffix in seventh_suffixes
    }


@pytest.mark.parametrize(
    ("mode", "triad_pool", "seventh_pool"),
    [
        ("major", ROMAN_MAJOR_SECONDARY_TRIADS, ROMAN_MAJOR_SECONDARY_SEVENTHS),
        ("minor", ROMAN_MINOR_SECONDARY_TRIADS, ROMAN_MINOR_SECONDARY_SEVENTHS),
    ],
)
def test_secondary_roman_pools_parse_in_all_supported_keys(mode, triad_pool, seventh_pool):
    key_names = key_tonics(mode, 7)
    triad_figures = {
        ChordRomanReasoning._with_roman_inversion(base, suffix)
        for base in triad_pool
        for suffix in ("", "6", "64")
    }
    seventh_figures = {
        ChordRomanReasoning._with_roman_inversion(base, suffix)
        for base in seventh_pool
        for suffix in ("7", "65", "43", "42")
    }

    for key_name in key_names:
        key_context = (
            music21_key.Key(key_name)
            if mode == "major"
            else music21_key.Key(key_name, "minor")
        )
        for figure in triad_figures | seventh_figures:
            rn = music21_roman.RomanNumeral(figure, key_context)
            notes = [Music21Adapter.note_from_pitch(pitch) for pitch in rn.pitches]

            assert all(abs(note.accidental) <= 2 for note in notes)


def test_roman_inversion_suffixes_attach_to_chord_part():
    assert ChordRomanReasoning._with_roman_inversion("I7", "7") == "I7"
    assert ChordRomanReasoning._with_roman_inversion("I7", "65") == "I65"
    assert ChordRomanReasoning._with_roman_inversion("vii/o7", "65") == "vii/o65"
    assert ChordRomanReasoning._with_roman_inversion("V7/V", "43") == "V43/V"
    assert ChordRomanReasoning._with_roman_inversion("viio7/V", "42") == "viio42/V"


def test_key_complexity_limits_analytical_key_tonics():
    assert set(key_tonics("major", 0)) == {"C"}
    assert set(key_tonics("minor", 0)) == {"A"}
    assert set(key_tonics("major", 2)) == {"C", "G", "D", "F", "Bb"}
    assert set(key_tonics("minor", 2)) == {"A", "E", "B", "D", "G"}
    assert len(key_tonics("major", 7)) == 15
    assert len(key_tonics("minor", 7)) == 15


def test_mode_any_samples_supported_modes_and_scores_answers():
    random.seed(6200)
    task = ChordRomanReasoning(ChordRomanConfig(mode="any"))
    seen_modes = set()

    for _ in range(100):
        example = task.generate_example(level=3)
        seen_modes.add(example.metadata.mode)
        assert example.metadata.mode in MODE_NAMES
        assert task.score_answer(example.answer, example) == 1.0

    assert len(seen_modes) > 1


def test_unknown_mode_is_rejected_before_retry_loop():
    task = ChordRomanReasoning(ChordRomanConfig(mode="not_a_mode"))

    with pytest.raises(ValueError, match="Unknown chord Roman mode"):
        task.generate()

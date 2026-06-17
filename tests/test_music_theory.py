import random

import pytest
from music21 import converter as music21_converter
from music21 import interval as music21_interval
from music21 import pitch as music21_pitch

from reasoning_core.tasks._music_theory import (
    ABC_KEY_SIGNATURES,
    ABCContext,
    AnswerNormalizer,
    COMPACT_ABC_STYLE,
    ChordRenderer,
    ChordTools,
    FULL_ABC_SCORE_STYLE,
    Interval,
    Music21Adapter,
    Note,
    NoteRenderer,
    Scale,
    SPN_STYLE,
)


ACCIDENTAL_NAMES = {
    -2: "double-flat",
    -1: "flat",
    0: None,
    1: "sharp",
    2: "double-sharp",
}

MUSIC21_INTERVAL_QUALITIES = {
    "perfect": "P",
    "major": "M",
    "minor": "m",
    "augmented": "A",
    "diminished": "d",
    "double-augmented": "AA",
    "double-diminished": "dd",
}


def _to_music21_pitch(note):
    result = music21_pitch.Pitch()
    result.step = note.letter
    result.octave = note.octave
    accidental_name = ACCIDENTAL_NAMES[note.accidental]
    result.accidental = None if accidental_name is None else music21_pitch.Accidental(accidental_name)
    return result


def _from_music21_pitch(pitch):
    accidental = 0 if pitch.accidental is None else int(pitch.accidental.alter)
    return Note(pitch.step, accidental, pitch.octave)


def _to_music21_interval(interval_value):
    quality = MUSIC21_INTERVAL_QUALITIES[interval_value.quality]
    return music21_interval.Interval(f"{quality}{interval_value.number}")


@pytest.mark.parametrize(
    ("note", "expected_name", "expected_name_without_octave", "expected_pc"),
    [
        (Note("C", 0, 4), "C4", "C", 0),
        (Note("F", 1, 3), "F#3", "F#", 6),
        (Note("B", -1, 5), "Bb5", "Bb", 10),
        (Note("E", 2, 2), "E##2", "E##", 6),
        (Note("C", -2, None), "Cbb", "Cbb", 10),
    ],
)
def test_note_names_and_pitch_classes(note, expected_name, expected_name_without_octave, expected_pc):
    assert note.name() == expected_name
    assert note.pc == expected_pc
    assert note.without_octave().octave is None
    assert note.without_octave().name() == expected_name_without_octave


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("E-flat4", Note("E", -1, 4)),
        ("F double-sharp 3", Note("F", 2, 3)),
        ("c natural", Note("C", 0, None)),
        ("Bb", Note("B", -1, None)),
    ],
)
def test_note_parse_accepts_common_spellings(text, expected):
    assert Note.parse(text) == expected


def test_note_parse_rejects_invalid_note_name():
    with pytest.raises(ValueError, match="Invalid note name"):
        Note.parse("H#4")


def test_note_exact_pitch_spellings_are_pitch_equivalent():
    note = Note("C", 1, 4)
    spellings = note.exact_pitch_spellings(accidental_limit=2)
    music21_target = _to_music21_pitch(note).ps

    assert Note("B", 2, 3) in spellings
    assert Note("D", -1, 4) in spellings
    assert all(_to_music21_pitch(spelling).ps == music21_target for spelling in spellings)


def test_note_spellings_for_pitch_class_can_omit_octaves():
    spellings = Note.spellings_for_pitch_class(1, accidental_limit=2, with_octave=False)

    assert Note("C", 1) in spellings
    assert Note("D", -1) in spellings
    assert all(note.octave is None for note in spellings)
    assert all(note.pc == 1 for note in spellings)


@pytest.mark.parametrize(
    "interval_value",
    [
        Interval("perfect", 1),
        Interval("minor", 2),
        Interval("major", 3),
        Interval("augmented", 4),
        Interval("double-diminished", 5),
        Interval("minor", 10),
        Interval("major", 13),
        Interval("perfect", 15),
        Interval("double-augmented", 8),
    ],
)
def test_interval_semitones_match_music21(interval_value):
    expected_interval = _to_music21_interval(interval_value)

    assert interval_value.semitones == expected_interval.semitones


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        (Note("C", 0, 4), Note("E", 0, 4), Interval("major", 3)),
        (Note("F", 1, 3), Note("A", 0, 4), Interval("minor", 10)),
        (Note("C", 0, 4), Note("C", 0, 5), Interval("perfect", 8)),
        (Note("B", 1, 3), Note("C", 1, 4), Interval("minor", 2)),
    ],
)
def test_interval_between_matches_expected_and_music21_semitones(start, end, expected):
    actual = Interval.between(start, end)
    expected_interval = _to_music21_interval(actual)

    assert actual.quality == expected.quality
    assert actual.number == expected.number
    assert actual.semitones == expected_interval.semitones


def test_interval_between_without_octaves_uses_simple_ascending_convention():
    actual = Interval.between(Note.parse("B"), Note.parse("D"), without_octaves=True)

    assert actual == Interval("minor", 3)
    with pytest.raises(ValueError, match="Chromatic distance requires concrete interval endpoints"):
        _ = actual.chromatic_distance


@pytest.mark.parametrize(
    ("start", "interval_value", "direction"),
    [
        (Note("C", 0, 4), Interval("major", 3), "up"),
        (Note("F", 1, 4), Interval("augmented", 4), "up"),
        (Note("E", 0, 4), Interval("minor", 3), "down"),
        (Note("B", -1, 4), Interval("perfect", 5), "down"),
    ],
)
def test_interval_construct_from_matches_music21_transposition(start, interval_value, direction):
    expected_interval = _to_music21_interval(interval_value)
    music21_start = _to_music21_pitch(start)
    reverse = direction == "down"
    music21_result = expected_interval.transposePitch(music21_start, reverse=reverse)

    assert interval_value.construct_from(start, direction=direction) == _from_music21_pitch(music21_result)


def test_interval_construct_from_rejects_unsupported_accidental():
    with pytest.raises(ValueError, match="unsupported accidental"):
        Interval("double-augmented", 8).construct_from(Note("E", 1, 4), direction="up")


def test_interval_operations_and_inversion():
    assert Interval("major", 2).add(Interval("minor", 3)) == Interval("perfect", 4)
    assert Interval("perfect", 5).subtract(Interval("major", 2)) == Interval("perfect", 4)
    assert Interval("major", 10).reduced() == Interval("major", 3)
    assert Interval("augmented", 4).inverted() == Interval("diminished", 5)

    with pytest.raises(ValueError, match="invalid interval"):
        Interval("minor", 2).subtract(Interval("major", 3))


def test_open_voicing_randomizes_registers_while_skipping_a_chord_member():
    random.seed(9100)
    root_position = [
        Note("C", 0, 4),
        Note("E", 0, 4),
        Note("G", 0, 4),
        Note("B", 0, 4),
    ]

    voicings = [ChordTools.open_voicing(root_position) for _ in range(20)]
    rendered_voicings = {tuple(note.name() for note in voicing) for voicing in voicings}

    assert len(rendered_voicings) > 1
    assert all(ChordTools.skips_chord_member(voicing, root_position) for voicing in voicings)
    assert all(voicing[-1].semitone_number - voicing[0].semitone_number > 12 for voicing in voicings)
    assert all(max(note.octave for note in voicing) <= 7 for voicing in voicings)


def test_scale_build_and_relation_labels():
    c_major = Scale.build(Note.parse("C"), "major")
    assert [note.name(False) for note in c_major.degrees] == ["C", "D", "E", "F", "G", "A", "B"]
    assert c_major.relation_label(Note.parse("C"), Note.parse("E")) == "diatonic consonance"
    assert c_major.relation_label(Note.parse("C"), Note.parse("F")) == "diatonic dissonance"
    assert c_major.relation_label(Note.parse("C"), Note.parse("F#")) == "chromatic alteration"

    a_harmonic_minor = Scale.build(Note.parse("A"), "harmonic_minor")
    assert [note.name(False) for note in a_harmonic_minor.degrees] == ["A", "B", "C", "D", "E", "F", "G#"]


def test_scale_membership_is_spelling_sensitive():
    d_sharp_minor = Scale.build(Note.parse("D#"), "natural_minor")

    assert d_sharp_minor.contains(Note.parse("G#"))
    assert not d_sharp_minor.contains(Note.parse("Ab"))


def test_abc_context_resolves_implicit_and_explicit_accidentals():
    context = ABCContext("1/4", "4/4", "Bb", ABC_KEY_SIGNATURES["Bb"])

    implicit_flat = context.render_event(Note("B", -1, 4), duration=1, explicit_accidental=False)
    assert implicit_flat.token == "B"
    assert "K:Bb makes B flat" in context.resolution_sentence(implicit_flat)
    assert 'represents "_B"' in context.resolution_sentence(implicit_flat)

    explicit_sharp = context.render_event(Note("B", 1, 4), duration=1, explicit_accidental=True)
    assert explicit_sharp.token == "^B"
    assert "explicitly marks B sharp, overriding K:Bb" in context.resolution_sentence(explicit_sharp)


def test_full_abc_sequence_is_parseable_and_resolves_key_signature(monkeypatch):
    context = ABCContext("1/4", "3/4", "Bb", ABC_KEY_SIGNATURES["Bb"])
    monkeypatch.setattr(ABCContext, "random", classmethod(lambda cls: context))
    monkeypatch.setattr(random, "random", lambda: 0.99)

    score, rendered_notes, resolution_cot = NoteRenderer.sequence(
        [Note("B", -1, 4), Note("F", 1, 4)],
        FULL_ABC_SCORE_STYLE,
    )
    parsed_score = music21_converter.parse(score, format="abc")
    parsed_notes = list(parsed_score.flatten().notes)

    assert "K:Bb" in score
    assert rendered_notes == ['"_B"', '"^F"']
    assert "The key signature K:Bb makes B flat" in resolution_cot[0]
    assert "explicitly marks F sharp" in resolution_cot[1]
    assert [note.pitch.nameWithOctave for note in parsed_notes] == ["B-4", "F#4"]


def test_full_abc_chord_rendering_is_parseable_and_resolves_notes(monkeypatch):
    context = ABCContext("1/8", "4/4", "D", ABC_KEY_SIGNATURES["D"])
    monkeypatch.setattr(ABCContext, "random", classmethod(lambda cls: context))
    monkeypatch.setattr(random, "random", lambda: 0.99)

    rendered = ChordRenderer.render(
        [Note("F", 1, 4), Note("A", 0, 4), Note("C", 1, 5)],
        FULL_ABC_SCORE_STYLE,
        with_octave=True,
        shuffle=False,
    )
    parsed_score = music21_converter.parse(rendered.prompt_text, format="abc")
    parsed_chords = list(parsed_score.flatten().notes)

    assert len(parsed_chords) == 1
    assert [pitch.nameWithOctave for pitch in parsed_chords[0].pitches] == ["F#4", "A4", "C#5"]
    assert rendered.cot_text == '"^F"-"=A"-"^c"'
    assert any("K:D makes F sharp" in line for line in rendered.resolution_cot)
    assert any("score note \"A\" represents \"=A\"" in line for line in rendered.resolution_cot)


def test_abc_interval_score_requires_number_for_octave_less_interval():
    with pytest.raises(ValueError, match="requires an interval number"):
        ABCContext.interval_score_with_resolution(Note("C"), Note("E"), with_octave=False)


def test_answer_normalizer_accepts_music_answer_variants():
    assert AnswerNormalizer.interval("double augmented eleventh.") == AnswerNormalizer.interval("double-augmented eleventh")
    assert AnswerNormalizer.interval("double octave") == "perfect fifteenth"
    assert AnswerNormalizer.note("E-flat4") == "Eb4"
    assert AnswerNormalizer.note('"=B"', "compact ABC notation") == "B"
    assert AnswerNormalizer.note("B", "compact ABC notation") == "B"


def test_answer_normalizer_accepts_roman_and_note_sequence_variants():
    assert AnswerNormalizer.roman(" vii ø 6 5. ") == "vii/o65"
    assert AnswerNormalizer.note_sequence('"=C"-"^F"', "compact ABC notation") == ("C", "^F")
    assert AnswerNormalizer.note_sequence("C# - E - G") == ("C#", "E", "G")


def test_note_renderer_answer_policy_matches_prompt_style():
    assert NoteRenderer.answer_rendering(SPN_STYLE) == (
        SPN_STYLE,
        "scientific pitch notation",
        False,
    )
    assert NoteRenderer.answer_rendering(COMPACT_ABC_STYLE) == (
        COMPACT_ABC_STYLE,
        "compact ABC notation",
        False,
    )
    assert NoteRenderer.answer_rendering(FULL_ABC_SCORE_STYLE) == (
        COMPACT_ABC_STYLE,
        "compact ABC notation",
        True,
    )
    assert NoteRenderer.answer_format("compact ABC notation", with_octave=True) == (
        "one full compact ABC pitch token"
    )
    assert (
        NoteRenderer.answer_format("compact ABC notation", explicit_accidentals=True)
        == "one note name in compact ABC notation, with any accidental made explicit"
    )


def test_music21_adapter_preserves_double_accidentals():
    assert Music21Adapter.pitch_name(Note("B", -2, 3)) == "B--3"
    assert Music21Adapter.pitch_name(Note("F", 2, 4)) == "F##4"
    assert Music21Adapter.note_from_pitch(music21_pitch.Pitch("B--3"), with_octave=True) == Note("B", -2, 3)
    assert Music21Adapter.note_from_pitch(music21_pitch.Pitch("F##4"), with_octave=True) == Note("F", 2, 4)

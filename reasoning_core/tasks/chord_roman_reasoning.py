from collections.abc import Sequence
from dataclasses import dataclass
import random
from typing import Any

from music21 import key as m21_key
from music21 import roman as m21_roman

from reasoning_core.template import Config, Problem, Task, edict
from reasoning_core.tasks._music_theory import (
    AnswerNormalizer,
    CHOICE_TAILS,
    COMPACT_ABC_STYLE,
    FULL_ABC_SCORE_SHARE,
    FULL_ABC_SCORE_STYLE,
    GENERATION_RETRY_LIMIT,
    ChordRenderer,
    ChordTools,
    Interval,
    Music21Adapter,
    Note,
    NoteRenderer,
    PromptFormatter,
    Scale,
    SPN_STYLE,
    TextFormatter,
    YES_NO_TAILS,
    key_tonics,
)


TRIAD_QUALITIES = (
    "major triad",
    "minor triad",
    "diminished triad",
    "augmented triad",
)
SEVENTH_CHORD_QUALITIES = (
    "major seventh",
    "dominant seventh",
    "minor seventh",
    "half-diminished seventh",
    "fully diminished seventh",
    "minor-major seventh",
    "augmented-major seventh",
)
CHORD_QUALITIES = TRIAD_QUALITIES + SEVENTH_CHORD_QUALITIES
INVERSION_LABELS = {
    3: (
        ("root position", "5/3"),
        ("first inversion", "6"),
        ("second inversion", "6/4"),
    ),
    4: (
        ("root position", "7"),
        ("first inversion", "6/5"),
        ("second inversion", "4/3"),
        ("third inversion", "4/2"),
    ),
}
CHROMATIC_CHORDS = (
    ("Neapolitan sixth", "N6"),
    ("Italian augmented sixth", "It6"),
    ("French augmented sixth", "Fr43"),
    ("German augmented sixth", "Ger65"),
    ("Swiss augmented sixth", "Sw43"),
)
CHROMATIC_SCALE_DEGREE_FORMULAS = {
    "Neapolitan sixth": "4-b6-b2",
    "Italian augmented sixth": "b6-1-#4",
    "French augmented sixth": "b6-1-2-#4",
    "German augmented sixth": "b6-1-b3-#4",
    "Swiss augmented sixth": "b6-1-#2-#4",
}
MODE_NAMES = (
    "chord_quality",
    "inversion",
    "open_close_voicing",
    "enharmonic_chord_equivalence",
    "chromatic_chord_label",
    "chord_membership",
    "roman_numeral_from_chord",
    "chord_from_roman_numeral",
)

QUALITY_OPENERS = (
    "What is the quality of {chord} as a chord-tone collection?",
    "Classify {chord} as a chord-tone collection.",
    "Identify the quality of {chord} as chord tones.",
    "Name the quality of {chord} as a chord-tone collection.",
)
INVERSION_OPENERS = (
    "Treat {chord} as an unordered collection of chord tones; the bass note is {bass}.",
    "Use {chord} as the chord-tone collection, with {bass} as the bass note.",
    "Given {chord} as the chord-tone collection with {bass} in the bass, identify the inversion.",
    "Analyze the inversion of {chord} as a chord-tone collection when {bass} is the bass note.",
    "Use {chord} as the unordered chord tones; the bass is {bass}.",
    "For {chord} as unordered chord tones, find the inversion over bass note {bass}.",
)
INVERSION_TAILS = (
    "The answer is one inversion label followed by figured bass.",
    "Give one inversion label followed by figured bass.",
    "The expected answer is an inversion label plus figured bass.",
    "Answer with the inversion label and figured-bass symbol.",
)
OPEN_CLOSE_VOICING_OPENERS = (
    "{chord} is in which voicing?",
    "Classify the voicing of {chord}.",
    "Is {chord} in open or close voicing?",
    "Determine the voicing type of {chord}.",
    "For {chord}, identify the voicing.",
    "Label the voicing of {chord}.",
    "What voicing label applies to {chord}?",
    "Decide whether {chord} is in open or close voicing.",
)
CHROMATIC_COLLECTION_OPENERS = (
    "In {key}, label {chord} as a chord-tone collection with {bass} in the bass.",
    "In {key}, identify the chromatic label for {chord} as a chord-tone collection with bass {bass}.",
    "Analyze {chord} as a chromatic chord-tone collection with {bass} in the bass in {key}.",
    "For {key}, choose the label for {chord} as a chord-tone collection with bass {bass}.",
    "In the key of {key}, classify {chord} as a chord-tone collection with bass note {bass}.",
    "Using {key}, name the chromatic chord-tone collection represented by {chord} with {bass} in the bass.",
    "In {key}, what chromatic label fits {chord} as a chord-tone collection with bass {bass}?",
    "Given {key}, label {chord} as a chord-tone collection with bass {bass}.",
)
CHROMATIC_ORDERED_OPENERS = (
    "In {key}, label {chord}.",
    "In {key}, identify the chromatic label for {chord}.",
    "Analyze {chord} in {key}.",
    "For {key}, choose the label for {chord}.",
    "In the key of {key}, classify {chord}.",
    "Using {key}, name {chord} as a chromatic sonority.",
    "In {key}, what chromatic label fits {chord}?",
    "Given {key}, label {chord}.",
)
MEMBERSHIP_OPENERS = (
    "Is {chord} diatonic in {key}?",
    "Do all tones of {chord} belong to {key}?",
    "In {key}, is {chord} a diatonic chord?",
    "Check whether {chord} is diatonic in {key}.",
    "Does {chord} use only notes from {key}?",
    "For {key}, decide whether {chord} is diatonic.",
    "Classify membership: is {chord} inside {key}?",
    "Does {chord} fit {key} as a collection of chord tones?",
    "Is every note of {chord} contained in {key}?",
    "In the collection {key}, does {chord} stay diatonic?",
    "Determine whether {chord} is diatonic to {key}.",
    "For the key context {key}, test {chord}.",
)
ROMAN_FROM_COLLECTION_OPENERS = (
    "In {key}, treat {chord} as a chord-tone collection with {bass} in the bass.",
    "Give the Roman numeral for {chord} as a chord-tone collection with {bass} in the bass in {key}.",
    "In {key}, identify the Roman numeral of {chord} as chord tones over bass {bass}.",
    "Analyze {chord} as chord tones over bass {bass} in {key}.",
    "For {key}, what Roman numeral describes {chord} as a chord-tone collection with bass {bass}?",
    "Using {key}, label {chord} as chord tones with {bass} in the bass.",
    "In the key of {key}, Roman-numeral analyze {chord} as chord tones over {bass}.",
    "Find the compact Roman numeral for {chord} as a chord-tone collection with bass note {bass} in {key}.",
)
ROMAN_FROM_ORDERED_OPENERS = (
    "In {key}, analyze {chord}.",
    "Give the Roman numeral for {chord} in {key}.",
    "In {key}, identify the Roman numeral of {chord}.",
    "Analyze {chord} in {key}.",
    "For {key}, what Roman numeral describes {chord}?",
    "Using {key}, label {chord} as a Roman numeral.",
    "In the key of {key}, Roman-numeral analyze {chord}.",
    "Find the compact Roman numeral for {chord} in {key}.",
)
ROMAN_TAILS = (
    "The answer is one compact Roman numeral with figured-bass digits closed up.",
    "Give one compact Roman numeral, closing up figured-bass digits.",
    "The expected answer is a compact Roman numeral with no internal spaces.",
    "Answer with one compact Roman numeral and closed-up figured bass.",
)
CHORD_FROM_ROMAN_OPENERS = (
    "In {key}, spell {figure}.",
    "Spell the chord for {figure} in {key}.",
    "In {key}, give the chord tones for {figure}.",
    "Which chord tones does {figure} produce in {key}?",
    "For {key}, spell the Roman numeral {figure}.",
    "Using {key}, list the chord tones of {figure}.",
    "In the key of {key}, realize {figure} as chord tones.",
    "Write the notes produced by {figure} in {key}.",
)
NOTE_SEQUENCE_TAILS = (
    "The answer is hyphen-separated note names from bass upward in {answer_notation}.",
    "Give hyphen-separated note names from bass upward in {answer_notation}.",
    "The expected answer is a bass-upward note sequence in {answer_notation}, separated by hyphens.",
    "Answer with note names from bass upward in {answer_notation}, separated by hyphens.",
)
ENHARMONIC_OPENERS = (
    "Are {first} and {second} enharmonically equivalent as pitch-class chords?",
    "Do {first} and {second} represent the same pitch-class chord?",
    "Compare {first} and {second}: are they enharmonically equivalent pitch-class chords?",
    "Are the pitch-class contents of {first} and {second} enharmonically equivalent?",
    "Do {first} and {second} represent the same pitch-class set?",
    "Check whether {first} and {second} are enharmonically equivalent as pitch-class chords.",
    "Are {first} and {second} equivalent after reducing to pitch classes?",
    "Do {first} and {second} have matching pitch-class sets?",
)


TRIAD_INTERVALS = {
    "major triad": (("major", 3), ("perfect", 5)),
    "minor triad": (("minor", 3), ("perfect", 5)),
    "diminished triad": (("minor", 3), ("diminished", 5)),
    "augmented triad": (("major", 3), ("augmented", 5)),
}
SEVENTH_INTERVALS = {
    "major seventh": (("major", 3), ("perfect", 5), ("major", 7)),
    "dominant seventh": (("major", 3), ("perfect", 5), ("minor", 7)),
    "minor seventh": (("minor", 3), ("perfect", 5), ("minor", 7)),
    "half-diminished seventh": (("minor", 3), ("diminished", 5), ("minor", 7)),
    "fully diminished seventh": (("minor", 3), ("diminished", 5), ("diminished", 7)),
    "minor-major seventh": (("minor", 3), ("perfect", 5), ("major", 7)),
    "augmented-major seventh": (("major", 3), ("augmented", 5), ("major", 7)),
}
ROMAN_MAJOR_TRIADS = ("I", "ii", "iii", "IV", "V", "vi", "viio")
ROMAN_MAJOR_SEVENTHS = ("I7", "ii7", "iii7", "IV7", "V7", "vi7", "vii/o7")
ROMAN_MINOR_TRIADS = ("i", "iio", "III", "iv", "V", "VI", "viio")
ROMAN_MINOR_SEVENTHS = ("i7", "ii/o7", "III7", "iv7", "V7", "VI7", "viio7")
ROMAN_MAJOR_SECONDARY_TRIADS = (
    "V/ii",
    "V/iii",
    "V/IV",
    "V/V",
    "V/vi",
    "viio/ii",
    "viio/iii",
    "viio/IV",
    "viio/V",
    "viio/vi",
)
ROMAN_MAJOR_SECONDARY_SEVENTHS = (
    "V7/ii",
    "V7/iii",
    "V7/IV",
    "V7/V",
    "V7/vi",
    "viio7/ii",
    "viio7/iii",
    "viio7/IV",
    "viio7/V",
    "viio7/vi",
)
ROMAN_MINOR_SECONDARY_TRIADS = (
    "V/III",
    "V/iv",
    "V/V",
    "V/VI",
    "V/VII",
    "viio/III",
    "viio/iv",
    "viio/V",
    "viio/VI",
    "viio/VII",
)
ROMAN_MINOR_SECONDARY_SEVENTHS = (
    "V7/III",
    "V7/iv",
    "V7/V",
    "V7/VI",
    "V7/VII",
    "viio7/III",
    "viio7/iv",
    "viio7/V",
    "viio7/VI",
    "viio7/VII",
)
TRIAD_INVERSION_SUFFIXES = ("", "6", "64")
SEVENTH_INVERSION_SUFFIXES = ("7", "65", "43", "42")


@dataclass
class ChordRomanConfig(Config):
    """Configuration knobs for chord and Roman-numeral reasoning."""

    # Which generation mode to use. "any" samples uniformly among all supported modes.
    mode: str = "any"

    # Probability of sampling a seventh chord instead of a triad in modes that
    # can use either size. Triads and seventh chords remain possible at every level.
    p_seventh: float = 0.30

    # Maximum accidental complexity for generated chord spellings.
    max_accidental: int = 1

    # Maximum number of sharps/flats in analytical key signatures.
    key_complexity: int = 2

    # Probability of secondary/applied Roman material where the mode allows it.
    p_secondary: float = 0.10

    # Probability of writing prompt/answer notes in ABC notation instead of
    # scientific pitch notation. ABC examples are split into 70% compact note
    # tokens and 30% full score fragments with sampled common L/M/K headers.
    p_abc: float = 0.20

    # Maximum attempts to generate a valid instance before failing.
    max_tries: int = 256

    # Override of Config.update; called by Config.set_level() to raise difficulty.
    def update(self, c: float = 1) -> None:
        """Increase generation difficulty by updating monotonic config knobs."""
        self.p_seventh = min(0.60, self.p_seventh + 0.06 * c)
        self.max_accidental = min(2, self.max_accidental + 0.2 * c)
        self.key_complexity = min(7, self.key_complexity + c)
        self.p_secondary = min(0.70, self.p_secondary + 0.08 * c)
        self.p_abc = min(0.50, self.p_abc + 0.06 * c)

    def random_style(self) -> str:
        """Sample the note-rendering style for a prompt."""
        roll = random.random()
        if roll < FULL_ABC_SCORE_SHARE * self.p_abc:
            return FULL_ABC_SCORE_STYLE
        if roll < self.p_abc:
            return COMPACT_ABC_STYLE
        return SPN_STYLE


class ChordRomanReasoning(Task):
    """Procedural generator for chord quality, inversion, and Roman-numeral tasks."""

    # Override of Task.__init__; keeps the normal task setup and adjusts balancing.
    def __init__(self, config: ChordRomanConfig = ChordRomanConfig()) -> None:
        """Initialize the task and reduce repeats for small label spaces."""
        super().__init__(config=config)
        # The default 0.5 allows too many repeats for low-cardinality modes
        # such as yes/no equivalence and fixed-label chord-quality tasks.
        self.balancing_key_ratio = 0.3

    def _sample_mode(self) -> str:
        """Choose a concrete generation mode from the configured mode setting."""
        if self.config.mode != "any":
            if self.config.mode not in MODE_NAMES:
                raise ValueError(f"Unknown chord Roman mode: {self.config.mode}")
            return self.config.mode
        return random.choice(MODE_NAMES)

    # Override of Task.generate; returns one generated Problem.
    def generate(self) -> Problem:
        """Generate one chord/Roman reasoning problem."""
        mode = self._sample_mode()
        for _ in range(self.config.max_tries):
            try:
                # Dispatch by convention: "chord_quality" -> self._generate_chord_quality().
                return getattr(self, f"_generate_{mode}")()
            except (KeyError, ValueError, m21_roman.RomanNumeralException):
                continue
        raise RuntimeError(f"Failed to generate a chord_roman_reasoning instance for mode {mode!r}.")

    # Override of Task.prompt; prompt text is already stored in metadata.
    def prompt(self, metadata: Any) -> str:
        """Return the prompt string stored in generated metadata."""
        return metadata.prompt

    # Override of Task.score_answer; normalizes chord/Roman-specific answer formats.
    def score_answer(self, answer: object, entry: Problem) -> float:
        """Score an answer after normalizing chord/Roman answer formats."""
        expected = str(entry.answer)
        kind = entry.metadata.get("answer_kind", "text")
        if kind == "yes_no":
            return float(AnswerNormalizer.text(answer) == expected)
        if kind == "roman":
            return float(AnswerNormalizer.roman(answer) == AnswerNormalizer.roman(expected))
        if kind == "note_sequence":
            answer_notation = entry.metadata.get("answer_notation")
            return float(
                AnswerNormalizer.note_sequence(answer, answer_notation)
                == AnswerNormalizer.note_sequence(expected, answer_notation)
            )
        return float(AnswerNormalizer.text(answer) == AnswerNormalizer.text(expected))

    # Override of Task.balancing_key; limits repeats of the same mode-answer pair.
    def balancing_key(self, problem: Problem) -> str:
        """Return the batch-balancing key for this generated problem."""
        return f"{problem.metadata.mode}:{problem.answer}"

    def _problem(
        self,
        mode: str,
        prompt: str,
        answer: object,
        answer_kind: str,
        cot: Sequence[str],
        **metadata: Any,
    ) -> Problem:
        """Package prompt, answer, reasoning trace, and metadata as a Problem."""
        meta = edict(mode=mode, prompt=prompt, answer_kind=answer_kind, cot="\n".join(cot), **metadata)
        return Problem(metadata=meta, answer=str(answer))
    
    def _generate_chord_quality(self) -> Problem:
        """Generate a task asking for a triad or seventh-chord quality label."""
        style = self.config.random_style()
        size = self._sample_chord_size()
        interval_table = SEVENTH_INTERVALS if size == 4 else TRIAD_INTERVALS
        notes, quality = self._sample_chord(interval_table)
        rendered = ChordRenderer.render(notes, style)
        interval_names = [
            Interval(interval_quality, number).name()
            for interval_quality, number in interval_table[quality]
        ]
        note_style = COMPACT_ABC_STYLE if style == FULL_ABC_SCORE_STYLE else style
        root = notes[0]
        rendered_root = NoteRenderer.note(root, note_style, force_natural=style == FULL_ABC_SCORE_STYLE)
        rendered_upper_notes = [
            NoteRenderer.note(note, note_style, force_natural=style == FULL_ABC_SCORE_STYLE)
            for note in notes[1:]
        ]
        prompt = PromptFormatter.choice_prompt(
            QUALITY_OPENERS,
            CHOICE_TAILS,
            style=style,
            chord=ChordRenderer.prompt_value(rendered, style),
            options=PromptFormatter.options(CHORD_QUALITIES),
        )
        interval_phrases = [
            f"from {rendered_root} to {rendered_note} is {TextFormatter.article(interval_name)}"
            for rendered_note, interval_name in zip(rendered_upper_notes, interval_names)
        ]
        article_intervals = [TextFormatter.article(interval_name) for interval_name in interval_names]
        if len(article_intervals) == 2:
            interval_summary = " and ".join(article_intervals)
        else:
            interval_summary = f"{', '.join(article_intervals[:-1])}, and {article_intervals[-1]}"
        chord_kind = "seventh chord" if size == 4 else "triad"
        cot = rendered.resolution_cot + [
            f"Arrange the chord tones by stacking thirds to get the root-position chord "
            f"{ChordRenderer.for_cot(notes, style)}, with {rendered_root} as the root.",
            f"The intervals above the root are: {', '.join(interval_phrases)}.",
            f"A {chord_kind} with {interval_summary} above the root is {TextFormatter.article(quality)}.",
        ]
        return self._problem(
            "chord_quality",
            prompt,
            quality,
            "label",
            cot,
            chord_notes=[note.name(False) for note in notes],
            style=style,
        )

    def _generate_inversion(self) -> Problem:
        """Generate a task asking for inversion label plus figured bass."""
        style = self.config.random_style()
        size = self._sample_chord_size()
        interval_table = SEVENTH_INTERVALS if size == 4 else TRIAD_INTERVALS
        notes, quality = self._sample_chord(interval_table)
        inversion = random.randint(0, size - 1)
        bass = notes[inversion]
        rendered = ChordRenderer.render(notes, style)
        rendered_bass = NoteRenderer.note(
            bass,
            COMPACT_ABC_STYLE if style == FULL_ABC_SCORE_STYLE else style,
            force_natural=style == FULL_ABC_SCORE_STYLE,
        )
        inversion_label, figured_bass = INVERSION_LABELS[size][inversion]
        answer = f"{inversion_label} {figured_bass}"
        prompt = PromptFormatter.choice_prompt(
            INVERSION_OPENERS,
            INVERSION_TAILS,
            style=style,
            chord=ChordRenderer.prompt_value(rendered, style),
            bass=rendered_bass,
        )
        cot = rendered.resolution_cot + [
            f"Arrange the chord tones by stacking thirds to get the root-position chord "
            f"{ChordRenderer.for_cot(notes, style)}, {TextFormatter.article(quality)}.",
            f"The bass note {rendered_bass} is chord member {inversion + 1} above the root.",
            f"For a {size}-note chord, that gives {answer}.",
        ]
        return self._problem(
            "inversion",
            prompt,
            answer,
            "text",
            cot,
            chord_notes=[note.name(False) for note in notes],
            bass_note=bass.name(False),
            style=style,
        )

    def _generate_open_close_voicing(self) -> Problem:
        """Generate a task classifying a voiced chord as open or close voicing."""
        style = self.config.random_style()
        size = self._sample_chord_size()
        interval_table = SEVENTH_INTERVALS if size == 4 else TRIAD_INTERVALS
        use_close = random.choice([True, False])
        root_position, quality = self._sample_chord(
            interval_table,
            with_octave=True,
            min_root_octave=1,
            max_root_octave=6 if use_close else 4,
        )
        voiced_notes = (
            ChordTools.close_voicing(root_position)
            if use_close
            else ChordTools.open_voicing(root_position)
        )
        answer = "close voicing" if use_close else "open voicing"
        rendered = ChordRenderer.render(voiced_notes, style, with_octave=True, shuffle=False)
        prompt = PromptFormatter.choice_prompt(
            OPEN_CLOSE_VOICING_OPENERS,
            CHOICE_TAILS,
            style=style,
            chord=ChordRenderer.prompt_value(rendered, style),
            options=PromptFormatter.options(("open voicing", "close voicing")),
        )
        span = max(note.semitone_number for note in voiced_notes) - min(
            note.semitone_number for note in voiced_notes
        )
        cot = rendered.resolution_cot + [
            f"The voiced chord is {rendered.cot_text}, {TextFormatter.article(quality)}.",
            f"The outer notes span {TextFormatter.count_phrase(span)}.",
            (
                "The chord tones fit within one octave without skipping a chord member between adjacent upper notes."
                if use_close
                else "At least one adjacent pair skips over another chord member, so the voicing is open."
            ),
            f"So the answer is {answer}.",
        ]
        return self._problem(
            "open_close_voicing",
            prompt,
            answer,
            "label",
            cot,
            chord_notes=[note.name() for note in voiced_notes],
            style=style,
        )

    def _generate_enharmonic_chord_equivalence(self) -> Problem:
        """Generate a task comparing two chords by pitch-class equivalence."""
        style = self.config.random_style()
        with_octave = random.choice([False, True])
        size = self._sample_chord_size()
        interval_table = SEVENTH_INTERVALS if size == 4 else TRIAD_INTERVALS
        first, _ = self._sample_chord(interval_table, with_octave=True)
        yes = random.choice([True, False])
        max_accidental = self.config.max_accidental
        if yes:
            second = [
                ChordTools.different_spelling_same_pitch(note, max_accidental)
                for note in first
            ]
        else:
            for _ in range(GENERATION_RETRY_LIMIT):
                second, _ = self._sample_chord(interval_table, with_octave=True)
                if ChordTools.pitch_class_set(second) != ChordTools.pitch_class_set(first):
                    break
            else:
                raise ValueError("Could not construct a non-equivalent chord pair.")
        answer = "yes" if yes else "no"
        rendered_first = ChordRenderer.render(
            first,
            style,
            with_octave=with_octave,
            shuffle=not with_octave,
        )
        rendered_second = ChordRenderer.render(
            second,
            style,
            with_octave=with_octave,
            shuffle=not with_octave,
        )
        prompt = PromptFormatter.choice_prompt(
            ENHARMONIC_OPENERS,
            YES_NO_TAILS,
            style=style,
            first=ChordRenderer.prompt_value(rendered_first, style),
            second=ChordRenderer.prompt_value(rendered_second, style),
        )
        cot = rendered_first.resolution_cot + rendered_second.resolution_cot + [
            f"The first chord has pitch classes {sorted(ChordTools.pitch_class_set(first))}.",
            f"The second chord has pitch classes {sorted(ChordTools.pitch_class_set(second))}.",
            (
                "The pitch-class sets match, so the answer is yes."
                if yes
                else "The pitch-class sets differ, so the answer is no."
            ),
        ]
        return self._problem(
            "enharmonic_chord_equivalence",
            prompt,
            answer,
            "yes_no",
            cot,
            first_chord=[note.name(with_octave) for note in first],
            second_chord=[note.name(with_octave) for note in second],
            style=style,
            with_octave=with_octave,
        )

    def _generate_chromatic_chord_label(self) -> Problem:
        """Generate a task labeling Neapolitan or augmented-sixth chords."""
        style = self.config.random_style()
        with_octave = random.choice([False, True])
        label, figure, tonic, mode, rn, notes = self._sample_chromatic_chord(with_octave)
        bass = Music21Adapter.note_from_pitch(rn.bass(), with_octave=with_octave)
        rendered = ChordRenderer.render(
            notes,
            style,
            with_octave=with_octave,
            shuffle=not with_octave,
        )
        rendered_bass = NoteRenderer.note(
            bass,
            COMPACT_ABC_STYLE if style == FULL_ABC_SCORE_STYLE else style,
            with_octave=with_octave,
            force_natural=style == FULL_ABC_SCORE_STYLE,
        )
        scale_degree_formula = self._scale_degree_formula(notes, tonic)
        if scale_degree_formula != CHROMATIC_SCALE_DEGREE_FORMULAS[label]:
            raise ValueError("Chromatic chord formula does not match its label.")
        prompt = PromptFormatter.choice_prompt(
            CHROMATIC_ORDERED_OPENERS if with_octave else CHROMATIC_COLLECTION_OPENERS,
            CHOICE_TAILS,
            style=style,
            key=f"{tonic} {mode}",
            chord=ChordRenderer.prompt_value(rendered, style),
            bass=rendered_bass,
            options=PromptFormatter.options(tuple(label for label, _ in CHROMATIC_CHORDS)),
        )
        cot = rendered.resolution_cot + [
            f"Relative to tonic {tonic}, the scale-degree formula is {scale_degree_formula}.",
            f"The formula {scale_degree_formula} identifies {TextFormatter.article(label)}.",
        ]
        if not with_octave:
            cot.insert(
                len(rendered.resolution_cot),
                f"Arrange the chord tones from the specified bass upward as "
                f"{ChordRenderer.for_cot(notes, style, with_octave)}.",
            )
        return self._problem(
            "chromatic_chord_label",
            prompt,
            label,
            "label",
            cot,
            key=f"{tonic} {mode}",
            roman_figure=figure,
            chord_notes=[note.name(with_octave) for note in notes],
            bass_note=bass.name(with_octave),
            style=style,
            with_octave=with_octave,
        )

    def _generate_chord_membership(self) -> Problem:
        """Generate a task asking whether a chord is diatonic in a key."""
        style = self.config.random_style()
        with_octave = random.choice([False, True])
        max_accidental = self.config.max_accidental
        scale, key_label = self._sample_scale()
        yes = random.choice([True, False])
        notes = self._sample_diatonic_chord(scale, self._sample_chord_size())
        if not yes:
            index = random.randrange(len(notes))
            notes[index] = scale.alter_note_outside(notes[index], max_accidental)
        answer = "yes" if all(scale.contains(note) for note in notes) else "no"
        rendered_notes = ChordTools.with_ascending_octaves(notes) if with_octave else notes
        rendered = ChordRenderer.render(
            rendered_notes,
            style,
            with_octave=with_octave,
            shuffle=not with_octave,
            sep=", ",
        )
        prompt = PromptFormatter.choice_prompt(
            MEMBERSHIP_OPENERS,
            YES_NO_TAILS,
            style=style,
            chord=ChordRenderer.prompt_value(rendered, style),
            key=f"{scale.tonic.name(False)} {key_label}",
        )
        scale_note_style = COMPACT_ABC_STYLE if style == FULL_ABC_SCORE_STYLE else style
        scale_notes = ", ".join(
            NoteRenderer.note(
                note,
                scale_note_style,
                force_natural=style == FULL_ABC_SCORE_STYLE,
            )
            for note in scale.degrees
        )
        cot_chord_notes = ChordRenderer.for_cot(notes, style, with_octave=False, sep=", ")
        cot = rendered.resolution_cot + [
            f"The {scale.tonic.name(False)} {key_label} collection is {scale_notes}.",
            f"The chord tones are {cot_chord_notes}.",
            (
                "Every chord tone belongs to the collection, so the answer is yes."
                if answer == "yes"
                else "At least one chord tone is outside the collection, so the answer is no."
            ),
        ]
        return self._problem(
            "chord_membership",
            prompt,
            answer,
            "yes_no",
            cot,
            key=f"{scale.tonic.name(False)} {key_label}",
            chord_notes=[note.name(with_octave) for note in rendered_notes],
            style=style,
            with_octave=with_octave,
        )

    def _generate_roman_numeral_from_chord(self) -> Problem:
        """Generate a task asking for Roman-numeral analysis of a chord in key."""
        style = self.config.random_style()
        with_octave = random.choice([False, True])
        tonic, mode, rn, notes = self._sample_roman_context(with_octave)
        bass = Music21Adapter.note_from_pitch(rn.bass(), with_octave=with_octave)
        answer = AnswerNormalizer.roman(rn.figure)
        rendered = ChordRenderer.render(
            notes,
            style,
            with_octave=with_octave,
            shuffle=not with_octave,
        )
        rendered_bass = NoteRenderer.note(
            bass,
            COMPACT_ABC_STYLE if style == FULL_ABC_SCORE_STYLE else style,
            with_octave=with_octave,
            force_natural=style == FULL_ABC_SCORE_STYLE,
        )
        prompt = PromptFormatter.choice_prompt(
            ROMAN_FROM_ORDERED_OPENERS if with_octave else ROMAN_FROM_COLLECTION_OPENERS,
            ROMAN_TAILS,
            style=style,
            key=f"{tonic} {mode}",
            chord=ChordRenderer.prompt_value(rendered, style),
            bass=rendered_bass,
        )
        cot = rendered.resolution_cot + self._roman_analysis_cot(
            notes,
            bass,
            rn,
            answer,
            tonic,
            mode,
            style,
            rendered_bass,
        )
        return self._problem(
            "roman_numeral_from_chord",
            prompt,
            answer,
            "roman",
            cot,
            key=f"{tonic} {mode}",
            chord_notes=[note.name(with_octave) for note in notes],
            bass_note=bass.name(with_octave),
            roman_figure=answer,
            style=style,
            with_octave=with_octave,
        )

    def _roman_analysis_cot(
        self,
        notes: Sequence[Note],
        bass: Note,
        rn: m21_roman.RomanNumeral,
        answer: str,
        tonic: str,
        mode: str,
        style: str,
        rendered_bass: str,
    ) -> list[str]:
        """Explain how a chord and bass imply a Roman numeral in the key."""
        root = Music21Adapter.note_from_pitch(rn.root()).without_octave()
        root_position_notes = self._root_position_order(notes, root)
        root_position_text = ChordRenderer.for_cot(root_position_notes, style, with_octave=False)
        root_text = self._render_cot_note(root, style)
        interval_phrases = self._roman_interval_phrases(root_position_notes, style)
        quality = rn.commonName
        size = len(root_position_notes)
        inversion = self._bass_member_index(root_position_notes, bass)
        suffix = self._roman_suffix(size, inversion)
        base = self._roman_base(answer, suffix)
        member_name = ("root", "third", "fifth", "seventh")[inversion]
        inversion_label = INVERSION_LABELS[size][inversion][0]

        cot = [
            f"Arrange the chord tones by stacking thirds: {root_position_text}. The root is {root_text}.",
            f"The intervals above the root are: {interval_phrases}. Therefore, the chord is {TextFormatter.article(quality)}.",
            self._roman_function_sentence(base, root, quality, tonic, mode, style),
            (
                f"The bass {rendered_bass} is the chordal {member_name}, so the chord is in "
                f"{inversion_label} and {self._roman_suffix_phrase(suffix, size)}."
            ),
            self._roman_combination_sentence(base, suffix, answer),
        ]
        return cot

    def _generate_chord_from_roman_numeral(self) -> Problem:
        """Generate a task asking for chord spelling from a Roman numeral."""
        style = self.config.random_style()
        tonic, mode, rn, notes = self._sample_roman_context()
        answer_style, answer_notation, force_answer_natural = NoteRenderer.answer_rendering(style)
        answer_notation_detail = answer_notation
        if force_answer_natural:
            answer_notation_detail += ", with any accidental made explicit"
        answer = ChordRenderer.join(
            [
                NoteRenderer.note(
                    note,
                    answer_style,
                    force_natural=force_answer_natural,
                    quote_abc=False,
                )
                for note in notes
            ]
        )
        rendered_answer = ChordRenderer.join(
            [
                NoteRenderer.note(note, answer_style, force_natural=force_answer_natural)
                for note in notes
            ]
        )
        prompt = PromptFormatter.choice_prompt(
            CHORD_FROM_ROMAN_OPENERS,
            NOTE_SEQUENCE_TAILS,
            key=f"{tonic} {mode}",
            figure=AnswerNormalizer.roman(rn.figure),
            answer_notation=answer_notation_detail,
        )
        cot = self._chord_from_roman_cot(
            rn,
            notes,
            tonic,
            mode,
            style,
            answer_style,
            force_answer_natural,
            rendered_answer,
        )
        return self._problem(
            "chord_from_roman_numeral",
            prompt,
            answer,
            "note_sequence",
            cot,
            key=f"{tonic} {mode}",
            roman_figure=AnswerNormalizer.roman(rn.figure),
            chord_notes=[note.name(False) for note in notes],
            answer_notation=answer_notation,
            answer_explicit_accidentals=force_answer_natural,
        )

    def _chord_from_roman_cot(
        self,
        rn: m21_roman.RomanNumeral,
        notes: Sequence[Note],
        tonic: str,
        mode: str,
        prompt_style: str,
        answer_style: str,
        force_answer_natural: bool,
        rendered_answer: str,
    ) -> list[str]:
        """Explain how a Roman numeral determines chord tones from bass upward."""
        figure = AnswerNormalizer.roman(rn.figure)
        root = Music21Adapter.note_from_pitch(rn.root()).without_octave()
        bass = Music21Adapter.note_from_pitch(rn.bass()).without_octave()
        root_position_notes = self._root_position_order(notes, root)
        root_position_text = ChordRenderer.for_cot(root_position_notes, prompt_style, with_octave=False)
        quality = rn.commonName
        size = len(root_position_notes)
        inversion = self._bass_member_index(root_position_notes, bass)
        suffix = self._roman_suffix(size, inversion)
        base = self._roman_base(figure, suffix)
        member_name = ("root", "third", "fifth", "seventh")[inversion]
        inversion_label = INVERSION_LABELS[size][inversion][0]
        bass_upward_text = ChordRenderer.join(
            [
                NoteRenderer.note(
                    note,
                    answer_style,
                    force_natural=force_answer_natural,
                )
                for note in notes
            ]
        )

        return [
            self._roman_to_root_sentence(base, root, quality, tonic, mode, prompt_style),
            f"A {size}-note {quality} is built in stacked thirds as {root_position_text}.",
            self._chord_from_roman_inversion_sentence(
                figure,
                suffix,
                inversion_label,
                member_name,
                bass,
                prompt_style,
            ),
            f"Writing the chord from bass upward gives {bass_upward_text}.",
        ]

    def _sample_chord(
        self,
        interval_table: dict[str, tuple[tuple[str, int], ...]],
        with_octave: bool = False,
        root_octave: int | None = None,
        min_root_octave: int = 1,
        max_root_octave: int = 6,
    ) -> tuple[list[Note], str]:
        """Sample a root-position chord that stays within accidental limits."""
        qualities = tuple(interval_table)
        max_accidental = self.config.max_accidental
        if root_octave is not None:
            with_octave = True
            min_root_octave = root_octave
            max_root_octave = root_octave
        if min_root_octave > max_root_octave:
            raise ValueError("Minimum root octave cannot exceed maximum root octave.")
        for _ in range(GENERATION_RETRY_LIMIT):
            root = Note.random(
                self.config,
                with_octave=with_octave,
                octave_min=min_root_octave,
                octave_max=max_root_octave,
                accidental_limit=max_accidental,
            )
            quality = random.choice(qualities)
            notes = [root] + [
                Interval(interval_quality, number).construct_from(root)
                for interval_quality, number in interval_table[quality]
            ]
            if all(abs(note.accidental) <= max_accidental for note in notes):
                return notes, quality
        raise ValueError("Could not construct a chord with supported accidentals.")

    def _sample_chord_size(self) -> int:
        """Sample whether a generated mode uses a triad or seventh chord."""
        return 4 if random.random() < self.config.p_seventh else 3

    def _sample_scale(self) -> tuple[Scale, str]:
        """Sample a major or natural-minor scale context."""
        key_complexity = self.config.key_complexity
        if random.choice(["major", "minor"]) == "major":
            tonic = Note.parse(random.choice(key_tonics("major", key_complexity)))
            return Scale.build(tonic, "major"), "major"
        tonic = Note.parse(random.choice(key_tonics("minor", key_complexity)))
        return Scale.build(tonic, "natural_minor"), "natural minor"

    def _sample_key_context(self) -> tuple[str, str, m21_key.Key]:
        """Sample a music21 key context and its rendered label."""
        key_complexity = self.config.key_complexity
        if random.choice(["major", "minor"]) == "major":
            tonic = random.choice(key_tonics("major", key_complexity))
            return tonic, "major", m21_key.Key(tonic)
        tonic = random.choice(key_tonics("minor", key_complexity))
        return tonic, "minor", m21_key.Key(tonic, "minor")

    def _scale_degree_formula(self, notes: Sequence[Note], tonic: str) -> str:
        """Return a chromatic scale-degree formula relative to a tonic."""
        tonic_note = Note.parse(tonic)
        return "-".join(self._scale_degree_token(note, tonic_note) for note in notes)

    def _scale_degree_token(self, note: Note, tonic: Note) -> str:
        """Return one chromatic scale-degree token such as 'b6' or '#4'."""
        degree = ((note.step - tonic.step) % 7) + 1
        reference_pc = (tonic.pc + Interval.base_semitones_for(degree)) % 12
        alteration = (note.pc - reference_pc + 6) % 12 - 6
        if abs(alteration) > 2:
            raise ValueError("Scale-degree alteration is outside supported accidental bounds.")
        prefix = "b" *   -alteration if alteration < 0 else "#" * alteration
        return f"{prefix}{degree}"

    def _sample_chromatic_chord(
        self,
        with_octave: bool = False,
    ) -> tuple[str, str, str, str, m21_roman.RomanNumeral, list[Note]]:
        """Sample a chromatic chord label and key context within accidental bounds."""
        max_accidental = self.config.max_accidental
        key_complexity = self.config.key_complexity
        for _ in range(GENERATION_RETRY_LIMIT):
            label, figure = random.choice(CHROMATIC_CHORDS)
            if random.choice(["major", "minor"]) == "major":
                tonic = random.choice(key_tonics("major", key_complexity))
                mode = "major"
                key_context = m21_key.Key(tonic)
            else:
                tonic = random.choice(key_tonics("minor", key_complexity))
                mode = "minor"
                key_context = m21_key.Key(tonic, "minor")
            rn = m21_roman.RomanNumeral(figure, key_context)
            notes = [
                Music21Adapter.note_from_pitch(pitch, with_octave=with_octave)
                for pitch in rn.pitches
            ]
            if all(abs(note.accidental) <= max_accidental for note in notes):
                return label, figure, tonic, mode, rn, notes
        raise ValueError("Could not sample a chromatic chord within accidental bounds.")

    def _sample_roman_context(
        self,
        with_octave: bool = False,
    ) -> tuple[str, str, m21_roman.RomanNumeral, list[Note]]:
        """Sample a Roman numeral, key, and chord spelling within current bounds."""
        max_accidental = self.config.max_accidental
        for _ in range(GENERATION_RETRY_LIMIT):
            tonic, mode, key_context = self._sample_key_context()
            rn = m21_roman.RomanNumeral(self._sample_roman_figure(mode), key_context)
            notes = [
                Music21Adapter.note_from_pitch(pitch, with_octave=with_octave)
                for pitch in rn.pitches
            ]
            if all(abs(note.accidental) <= max_accidental for note in notes):
                return tonic, mode, rn, notes
        raise ValueError("Could not sample a Roman numeral within accidental bounds.")

    def _sample_roman_figure(self, mode: str) -> str:
        """Sample a Roman numeral whose size determines the possible inversions."""
        if self._sample_chord_size() == 4:
            diatonic_pool = ROMAN_MAJOR_SEVENTHS if mode == "major" else ROMAN_MINOR_SEVENTHS
            suffix = random.choice(SEVENTH_INVERSION_SUFFIXES)
            figure = self._with_roman_inversion(random.choice(diatonic_pool), suffix)
            secondary_pool = (
                ROMAN_MAJOR_SECONDARY_SEVENTHS
                if mode == "major"
                else ROMAN_MINOR_SECONDARY_SEVENTHS
            )
        else:
            diatonic_pool = ROMAN_MAJOR_TRIADS if mode == "major" else ROMAN_MINOR_TRIADS
            suffix = random.choice(TRIAD_INVERSION_SUFFIXES)
            figure = self._with_roman_inversion(random.choice(diatonic_pool), suffix)
            secondary_pool = (
                ROMAN_MAJOR_SECONDARY_TRIADS
                if mode == "major"
                else ROMAN_MINOR_SECONDARY_TRIADS
            )
        if random.random() < self.config.p_secondary:
            figure = self._with_roman_inversion(random.choice(secondary_pool), suffix)
        return figure

    @staticmethod
    def _root_position_order(notes: Sequence[Note], root: Note) -> list[Note]:
        """Order chord tones from root upward by stacked thirds, ignoring octave."""
        return sorted(
            [note.without_octave() for note in notes],
            key=lambda note: (note.step - root.step) % 7,
        )

    @staticmethod
    def _render_cot_note(note: Note, style: str) -> str:
        """Render one note for a CoT in the prompt's notation family."""
        note_style = COMPACT_ABC_STYLE if style == FULL_ABC_SCORE_STYLE else style
        return NoteRenderer.note(
            note.without_octave(),
            note_style,
            force_natural=style == FULL_ABC_SCORE_STYLE,
        )

    def _roman_interval_phrases(self, root_position_notes: Sequence[Note], style: str) -> str:
        """Describe intervals from the root to the other stacked chord tones."""
        root = root_position_notes[0]
        phrases = []
        for note in root_position_notes[1:]:
            interval = Interval.between(root, note, without_octaves=True)
            phrases.append(
                f"from {self._render_cot_note(root, style)} to {self._render_cot_note(note, style)}, "
                f"{TextFormatter.article(interval.name())}"
            )
        return "; ".join(phrases)

    @staticmethod
    def _bass_member_index(root_position_notes: Sequence[Note], bass: Note) -> int:
        """Return which root-position chord member is in the bass."""
        bass_without_octave = bass.without_octave()
        for index, note in enumerate(root_position_notes):
            if note.same_spelling(bass_without_octave):
                return index
        raise ValueError("Bass note is not one of the chord tones.")

    @staticmethod
    def _roman_suffix(size: int, inversion: int) -> str:
        """Return the compact figured-bass suffix for a chord size and inversion."""
        if size == 3:
            return TRIAD_INVERSION_SUFFIXES[inversion]
        if size == 4:
            return SEVENTH_INVERSION_SUFFIXES[inversion]
        raise ValueError(f"Unsupported chord size for Roman suffix: {size}")

    @staticmethod
    def _roman_base(figure: str, suffix: str) -> str:
        """Remove the inversion suffix from a compact Roman numeral."""
        if not suffix:
            return figure
        if "/o" in figure:
            return figure[: -len(suffix)]
        chord_part, slash, target = figure.partition("/")
        if slash:
            chord_part = chord_part[: -len(suffix)]
            return f"{chord_part}{slash}{target}"
        return figure[: -len(suffix)]

    @staticmethod
    def _roman_suffix_phrase(suffix: str, size: int) -> str:
        """Return readable wording for the Roman figured-bass suffix."""
        if suffix:
            return f"the Roman suffix is {suffix}"
        if size == 3:
            return "there is no triad suffix"
        return "there is no suffix"

    @staticmethod
    def _roman_suffix_combination_phrase(suffix: str) -> str:
        """Return suffix wording for the final Roman-numeral combination."""
        return f"suffix {suffix}" if suffix else "no suffix"

    @staticmethod
    def _roman_combination_sentence(base: str, suffix: str, answer: str) -> str:
        """Explain how the Roman base and inversion suffix form the answer."""
        if "/" in base and "/o" not in base and suffix:
            return f"Inserting suffix {suffix} before the slash in {base} gives {answer}."
        return f"Combining the base {base} with {ChordRomanReasoning._roman_suffix_combination_phrase(suffix)} gives {answer}."

    @staticmethod
    def _secondary_target(base: str) -> str | None:
        """Return the secondary target after the slash, excluding half-diminished /o."""
        if "/o" in base:
            return None
        _local_base, slash, target = base.partition("/")
        return target if slash else None

    def _roman_function_sentence(
        self,
        base: str,
        root: Note,
        quality: str,
        tonic: str,
        mode: str,
        style: str,
    ) -> str:
        """Explain why the root and quality imply the Roman base."""
        target = self._secondary_target(base)
        if target is not None:
            local_base = base.partition("/")[0]
            return (
                f"In {tonic} {mode}, {TextFormatter.article(quality)} on "
                f"{self._render_cot_note(root, style)} functions as local {local_base} "
                f"that resolves to {target}. Applied function is written with a slash, "
                f"so the Roman base is {base}."
            )

        degree = ((root.step - Note.parse(tonic).step) % 7) + 1
        return (
            f"In {tonic} {mode}, root {self._render_cot_note(root, style)} is scale degree {degree}; "
            f"with this quality, the Roman base is {base}."
        )

    def _roman_to_root_sentence(
        self,
        base: str,
        root: Note,
        quality: str,
        tonic: str,
        mode: str,
        style: str,
    ) -> str:
        """Explain how the Roman base selects a root and chord quality."""
        root_text = self._render_cot_note(root, style)
        target = self._secondary_target(base)
        if target is not None:
            local_base = base.partition("/")[0]
            return (
                f"The Roman base {base} means local {local_base} applied to {target} in {tonic} {mode}. "
                f"That gives {TextFormatter.article(quality)} on root {root_text}."
            )

        degree = ((root.step - Note.parse(tonic).step) % 7) + 1
        return (
            f"In {tonic} {mode}, Roman base {base} uses scale degree {degree}, "
            f"so the root is {root_text} and the chord quality is {TextFormatter.article(quality)}."
        )

    def _chord_from_roman_inversion_sentence(
        self,
        figure: str,
        suffix: str,
        inversion_label: str,
        member_name: str,
        bass: Note,
        style: str,
    ) -> str:
        """Explain how the figured-bass suffix chooses the bass note."""
        bass_text = self._render_cot_note(bass, style)
        if suffix:
            return (
                f"The suffix {suffix} in {figure} means {inversion_label}; "
                f"therefore, the chordal {member_name}, {bass_text}, is in the bass."
            )
        return (
            f"Because {figure} has no inversion suffix, it is in root position; "
            f"therefore, the chordal root, {bass_text}, is in the bass."
        )

    @staticmethod
    def _with_roman_inversion(figure: str, suffix: str) -> str:
        """Attach figured-bass suffix before any secondary-function slash."""
        if not suffix:
            return figure
        if "/o" in figure:
            return f"{figure[:-1] if figure.endswith('7') else figure}{suffix}"
        chord_part, slash, target = figure.partition("/")
        if chord_part.endswith("7"):
            chord_part = chord_part[:-1]
        return f"{chord_part}{suffix}{slash}{target}"

    def _sample_diatonic_chord(self, scale: Scale, size: int) -> list[Note]:
        """Sample a tertian chord from one scale collection."""
        degree_index = random.randrange(7)
        offsets = (0, 2, 4, 6)[:size]
        return [scale.degrees[(degree_index + offset) % 7] for offset in offsets]

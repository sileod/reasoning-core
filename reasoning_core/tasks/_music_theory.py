from dataclasses import dataclass
from collections.abc import Sequence
import random
import re
from typing import Any

from music21 import chord as m21_chord

LETTERS = "CDEFGAB"
STEP = {letter: i for i, letter in enumerate(LETTERS)}
NATURAL_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
PITCH_CLASS_LABELS = ("C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B")
ACC_TO_INT = {"bb": -2, "b": -1, "": 0, "#": 1, "##": 2}
INT_TO_ACC = {v: k for k, v in ACC_TO_INT.items()}
ACCIDENTAL_WEIGHTS = {
    0: 6,
    -1: 3,
    1: 3,
    -2: 1,
    2: 1,
}
GENERATION_RETRY_LIMIT = 128
SPN_STYLE = "spn"
COMPACT_ABC_STYLE = "compact_abc"
FULL_ABC_SCORE_STYLE = "full_abc_score"
FULL_ABC_SCORE_SHARE = 0.3
ABC_DEFAULT_LENGTHS = ("1/4", "1/8", "1/16")
ABC_EVENT_DURATIONS = (1, 2, 4)
ABC_OMIT_DURATION_SHARE = 0.3
ABC_METERS = ("none", "2/4", "3/4", "4/4", "6/8", "9/8", "12/8")
ABC_KEYS = ("C", "G", "D", "A", "E", "F", "Bb", "Eb", "Ab", "Am", "Em", "Bm", "F#m", "Dm", "Gm", "Cm", "Fm")
ABC_EXPLICIT_ACCIDENTAL_SHARE = 0.1
ABC_KEY_SIGNATURES = {
    "C": {},
    "G": {"F": 1},
    "D": {"F": 1, "C": 1},
    "A": {"F": 1, "C": 1, "G": 1},
    "E": {"F": 1, "C": 1, "G": 1, "D": 1},
    "F": {"B": -1},
    "Bb": {"B": -1, "E": -1},
    "Eb": {"B": -1, "E": -1, "A": -1},
    "Ab": {"B": -1, "E": -1, "A": -1, "D": -1},
    "Am": {},
    "Em": {"F": 1},
    "Bm": {"F": 1, "C": 1},
    "F#m": {"F": 1, "C": 1, "G": 1},
    "Dm": {"B": -1},
    "Gm": {"B": -1, "E": -1},
    "Cm": {"B": -1, "E": -1, "A": -1},
    "Fm": {"B": -1, "E": -1, "A": -1, "D": -1},
}
ABC_ACCIDENTAL_PREFIX = {2: "^^", 1: "^", 0: "=", -1: "_", -2: "__"}
ACCIDENTAL_WORDS = {
    2: "double sharp",
    1: "sharp",
    0: "natural",
    -1: "flat",
    -2: "double flat",
}
NUMBER_NAMES = {
    1: "unison",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
    8: "octave",
    9: "ninth",
    10: "tenth",
    11: "eleventh",
    12: "twelfth",
    13: "thirteenth",
    14: "fourteenth",
    15: "fifteenth",
    16: "sixteenth",
    17: "seventeenth",
    18: "eighteenth",
    19: "nineteenth",
    20: "twentieth",
}
BASE_INTERVAL_SEMITONES = {1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11}
PERFECT_SIMPLE_NUMBERS = {1, 4, 5}
PERFECT_INTERVAL_NAMES = {
    name for number, name in NUMBER_NAMES.items()
    if ((number - 1) % 7) + 1 in PERFECT_SIMPLE_NUMBERS
}
QUALITY_OFFSETS = {
    "perfect": 0,
    "major": 0,
    "minor": -1,
    "augmented": 1,
    "double-augmented": 2,
}
PERFECT_QUALITY_OFFSETS = {
    **QUALITY_OFFSETS,
    "diminished": -1,
    "double-diminished": -2,
}
IMPERFECT_QUALITY_OFFSETS = {
    **QUALITY_OFFSETS,
    "diminished": -2,
    "double-diminished": -3,
}
PERFECT_QUALITY_BY_OFFSET = {
    0: "perfect",
    1: "augmented",
    2: "double-augmented",
    -1: "diminished",
    -2: "double-diminished",
}
IMPERFECT_QUALITY_BY_OFFSET = {
    0: "major",
    -1: "minor",
    1: "augmented",
    2: "double-augmented",
    -2: "diminished",
    -3: "double-diminished",
}
# Interval inversion swaps the two notes of an interval. The interval number
# changes so simple numbers add to 9, and the quality changes by convention:
# major <-> minor, augmented <-> diminished, perfect stays perfect.
QUALITY_INVERSION = {
    "perfect": "perfect",
    "major": "minor",
    "minor": "major",
    "augmented": "diminished",
    "diminished": "augmented",
    "double-augmented": "double-diminished",
    "double-diminished": "double-augmented",
}
QUALITY_WEIGHTS = {
    "perfect": 5,
    "major": 5,
    "minor": 5,
    "augmented": 2,
    "diminished": 2,
    "double-augmented": 1,
    "double-diminished": 1,
}

# Conventional key-signature spellings used for key-context tasks. These are
# the standard 15 major and 15 minor key names, avoiding theoretical key
# signatures outside the usual circle-of-fifths spellings.
MAJOR_KEY_TONICS = ("Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#")
MINOR_KEY_TONICS = ("Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#")
MAJOR_KEY_COMPLEXITY = {
    "C": 0,
    "G": 1,
    "D": 2,
    "A": 3,
    "E": 4,
    "B": 5,
    "F#": 6,
    "C#": 7,
    "F": 1,
    "Bb": 2,
    "Eb": 3,
    "Ab": 4,
    "Db": 5,
    "Gb": 6,
    "Cb": 7,
}
MINOR_KEY_COMPLEXITY = {
    "A": 0,
    "E": 1,
    "B": 2,
    "F#": 3,
    "C#": 4,
    "G#": 5,
    "D#": 6,
    "A#": 7,
    "D": 1,
    "G": 2,
    "C": 3,
    "F": 4,
    "Bb": 5,
    "Eb": 6,
    "Ab": 7,
}
MINOR_SCALE_MODES = (
    ("natural_minor", "natural minor"),
    ("harmonic_minor", "harmonic minor"),
    ("melodic_minor_ascending", "melodic minor ascending"),
)


def key_tonics(mode: str, key_complexity: int = 7) -> tuple[str, ...]:
    """Return conventional key tonics within a key-signature complexity bound."""
    key_complexity = max(0, min(7, int(key_complexity)))
    if mode == "major":
        return tuple(
            tonic for tonic in MAJOR_KEY_TONICS
            if MAJOR_KEY_COMPLEXITY[tonic] <= key_complexity
        )
    if mode == "minor":
        return tuple(
            tonic for tonic in MINOR_KEY_TONICS
            if MINOR_KEY_COMPLEXITY[tonic] <= key_complexity
        )
    raise ValueError(f"Unsupported key mode: {mode}")


# Consonances are relatively stable diatonic intervals, dissonances are
# unstable but still in-key intervals, and chromatic alterations use notes
# outside the key collection.
INTERVAL_CLASS_LABELS = (
    "diatonic consonance",
    "diatonic dissonance",
    "chromatic alteration",
)
CONSONANT_INTERVAL_SIMPLE_NUMBERS = {1, 3, 5, 6}
CONSONANT_INTERVAL_QUALITIES = {"perfect", "major", "minor"}

CHOICE_TAILS = (
    "Choose from: {options}. The answer is one label from that list.",
    "Use one of these labels: {options}. The answer is one label from that list.",
    "Select exactly one label from this list: {options}.",
    "The answer is exactly one of these labels: {options}.",
    "Answer with exactly one label from: {options}.",
)
YES_NO_TAILS = (
    "The answer is exactly 'yes' or 'no'.",
    "Answer exactly 'yes' or 'no'.",
    "The expected answer is one word: 'yes' or 'no'.",
    "Give one answer, either 'yes' or 'no'.",
    "Respond with exactly one word: 'yes' or 'no'.",
)
INTEGER_TAILS = (
    "The answer is one integer.",
    "Give one integer.",
    "Answer with one integer.",
    "Respond with a single integer.",
)
NOTE_ANSWER_TAILS = (
    "The answer is {answer_format}.",
    "Give {answer_format}.",
    "Answer with {answer_format}.",
    "Provide {answer_format}.",
)

@dataclass(frozen=True)
class Note:
    """A written pitch spelling, e.g. Note("F", 1, 4) represents F#4."""

    letter: str
    accidental: int = 0
    octave: int | None = None

    @property
    def pc(self) -> int:
        """Return the pitch class, where C is 0 and B is 11."""
        return (NATURAL_PC[self.letter] + self.accidental) % 12

    @property
    def step(self) -> int:
        """Return the diatonic letter index, where C is 0 and B is 6."""
        return STEP[self.letter]

    @property
    def diatonic_number(self) -> int:
        """Return an octave-aware diatonic position for interval-number math."""
        if self.octave is None:
            raise ValueError("Cannot compute diatonic number without octave.")
        return self.octave * 7 + self.step

    @property
    def semitone_number(self) -> int:
        """Return an octave-aware chromatic position for semitone-distance math."""
        if self.octave is None:
            raise ValueError("Cannot compute semitone number without octave.")
        return self.octave * 12 + NATURAL_PC[self.letter] + self.accidental

    def name(self, with_octave: bool | None = None) -> str:
        """Render the note as a compact name such as 'F#4' or 'Bb' (scientific pitch notation)."""
        if with_octave is None:
            with_octave = self.octave is not None
        suffix = "" if not with_octave or self.octave is None else str(self.octave)
        return f"{self.letter}{INT_TO_ACC[self.accidental]}{suffix}"

    def without_octave(self) -> "Note":
        """Return the same written note without octave information."""
        return Note(self.letter, self.accidental)

    def same_spelling(self, other: "Note", include_octave: bool = False) -> bool:
        """Return whether another note has the same written spelling."""
        same_pitch_name = self.letter == other.letter and self.accidental == other.accidental
        if include_octave:
            return same_pitch_name and self.octave == other.octave
        return same_pitch_name

    def same_pitch(self, other: "Note") -> bool:
        """Return whether another note sounds as the same pitch."""
        if self.octave is None or other.octave is None:
            return self.pc == other.pc
        return self.semitone_number == other.semitone_number

    @classmethod
    def parse(cls, text: object, default_octave: int | None = None) -> "Note":
        """Parse a note in scientific pitch notation into a Note object."""
        text = "".join(AnswerNormalizer.normalize_text(text).split())
        m = re.fullmatch(r"([A-Ga-g])((?:bb)|(?:##)|b|#)?(-?\d+)?", text)
        if not m:
            raise ValueError(f"Invalid note name: {text!r}")
        letter, accidental, octave = m.groups()
        octave = default_octave if octave is None else int(octave)
        return cls(letter.upper(), ACC_TO_INT[accidental or ""], octave)

    @staticmethod
    def random_accidental(limit: int, weights_by_accidental: dict[int, float] = ACCIDENTAL_WEIGHTS) -> int:
        """Sample an accidental, favoring simpler spellings."""
        choices = [0]
        if limit >= 1:
            choices += [-1, 1]
        if limit >= 2:
            choices += [-2, 2]
        weights = [weights_by_accidental[a] for a in choices]
        return random.choices(choices, weights=weights, k=1)[0]

    @classmethod
    def random(
        cls,
        config: "PitchIntervalConfig",
        with_octave: bool = True,
        octave_min: int = 3,
        octave_max: int = 5,
        accidental_limit: int | None = None,
    ) -> "Note":
        """Sample a random written note within a modest octave range."""
        accidental_limit = config.max_accidental if accidental_limit is None else accidental_limit
        octave = random.randint(octave_min, octave_max) if with_octave else None
        return cls(random.choice(LETTERS), cls.random_accidental(accidental_limit), octave)

    def exact_pitch_spellings(self, accidental_limit: int) -> list["Note"]:
        """Return written spellings that sound as the same octave-bearing pitch."""
        if self.octave is None:
            raise ValueError("Exact-pitch spellings require an octave.")

        spellings = []
        target = self.semitone_number
        for letter in LETTERS:
            for accidental in range(-accidental_limit, accidental_limit + 1):
                octave_offset = target - NATURAL_PC[letter] - accidental
                if octave_offset % 12 == 0:
                    spellings.append(Note(letter, accidental, octave_offset // 12))
        return spellings

    @classmethod
    def spellings_for_pitch_class(
        cls,
        pc: int,
        accidental_limit: int,
        with_octave: bool = True,
        octave_min: int = 2,
        octave_max: int = 6,
    ) -> list["Note"]:
        """List note spellings for a pitch class within an accidental limit."""
        notes = []
        for letter in LETTERS:
            for accidental in range(-accidental_limit, accidental_limit + 1):
                if (NATURAL_PC[letter] + accidental) % 12 == pc:
                    octave = random.randint(octave_min, octave_max) if with_octave else None
                    notes.append(cls(letter, accidental, octave))
        return notes


@dataclass(frozen=True)
class Interval:
    """A named interval, optionally anchored to concrete start/end notes.

    The quality and number are the stable interval identity. Endpoints are
    stored only when a mode needs note-pair context; endpoint-dependent methods
    check that the needed octave information is actually present.
    """

    quality: str
    number: int
    start: Note | None = None
    end: Note | None = None

    @classmethod
    def between(cls, start: Note, end: Note, without_octaves: bool = False) -> "Interval":
        """Compute the named interval between two notes.

        With ``without_octaves=True``, use the task's simple ascending interval
        convention for octave-free note names and do not store concrete
        endpoints, because no precise compound interval is implied.
        """
        if without_octaves:
            calc_start = Note(start.letter, start.accidental, 4)
            octave = 4 if end.step >= start.step else 5
            calc_end = Note(end.letter, end.accidental, octave)
            start_for_storage = None
            end_for_storage = None
        else:
            calc_start = start
            calc_end = end
            start_for_storage = start
            end_for_storage = end
        number = abs(calc_end.diatonic_number - calc_start.diatonic_number) + 1
        semitones = abs(calc_end.semitone_number - calc_start.semitone_number)
        quality = cls.quality_from_distance(number, semitones)
        return cls(quality, number, start_for_storage, end_for_storage)

    @staticmethod
    def simple_number_for(number: int) -> int:
        """Reduce any interval number to its simple interval number."""
        return ((number - 1) % 7) + 1

    @staticmethod
    def base_semitones_for(number: int) -> int:
        """Return semitones for the major/perfect form of an interval number."""
        simple = Interval.simple_number_for(number)
        octaves = (number - 1) // 7
        return BASE_INTERVAL_SEMITONES[simple] + 12 * octaves

    @staticmethod
    def semitones_for(quality: str, number: int) -> int:
        """Return semitone size for an interval quality and number."""
        simple = Interval.simple_number_for(number)
        base = Interval.base_semitones_for(number)
        offsets = PERFECT_QUALITY_OFFSETS if simple in PERFECT_SIMPLE_NUMBERS else IMPERFECT_QUALITY_OFFSETS
        offset = offsets[quality]
        return base + offset

    @staticmethod
    def quality_from_distance(number: int, semitones: int) -> str:
        """Infer interval quality from interval number and semitone distance."""
        simple = Interval.simple_number_for(number)
        diff = semitones - Interval.base_semitones_for(number)
        table = PERFECT_QUALITY_BY_OFFSET if simple in PERFECT_SIMPLE_NUMBERS else IMPERFECT_QUALITY_BY_OFFSET
        if diff not in table:
            raise ValueError("Unsupported interval quality.")
        return table[diff]

    @staticmethod
    def quality_options(number: int, accidental_limit: int) -> list[str]:
        """Return interval qualities allowed for a number and accidental limit."""
        simple = Interval.simple_number_for(number)
        if simple in PERFECT_SIMPLE_NUMBERS:
            qualities = ["perfect"]
        else:
            qualities = ["major", "minor"]
        if accidental_limit >= 1:
            qualities += ["augmented", "diminished"]
        if accidental_limit >= 2:
            qualities += ["double-augmented", "double-diminished"]
        return [quality for quality in qualities if Interval.semitones_for(quality, number) >= 0]

    @classmethod
    def random(
        cls,
        config: "PitchIntervalConfig",
        min_number: int = 1,
        max_number: int | None = None,
        compound: bool = False,
        accidental_limit: int | None = None,
        weights_by_quality: dict[str, float] = QUALITY_WEIGHTS,
    ) -> "Interval":
        """Sample an interval quality and number from the current difficulty range."""
        max_number = max_number or config.max_interval_number
        accidental_limit = config.max_accidental if accidental_limit is None else accidental_limit
        if compound:
            low = max(9, min_number)
            high = max(low, max_number)
        else:
            low = min_number
            high = max(low, max_number)
        number = random.randint(low, high)
        qualities = cls.quality_options(number, accidental_limit)
        weights = [weights_by_quality[q] for q in qualities]
        return cls(random.choices(qualities, weights=weights, k=1)[0], number)

    def name(self) -> str:
        """Return the readable interval name, such as 'major third'."""
        return f"{self.quality} {self.number_name}"

    @property
    def number_name(self) -> str:
        """Return the interval-number name, such as 'third'."""
        return NUMBER_NAMES[self.number]

    @property
    def simple_number(self) -> int:
        """Return the simple interval number after octave reduction."""
        return self.simple_number_for(self.number)

    @property
    def base_semitones(self) -> int:
        """Return semitones in the major/perfect reference form."""
        return self.base_semitones_for(self.number)

    @property
    def semitones(self) -> int:
        """Return semitones in this named interval."""
        return self.semitones_for(self.quality, self.number)

    @property
    def step_count(self) -> int:
        """Return letter steps moved from start to target."""
        return self.number - 1

    @property
    def chromatic_distance(self) -> int:
        """Return endpoint semitone distance for a concrete note-pair interval."""
        if self.start is None or self.end is None:
            raise ValueError("Chromatic distance requires concrete interval endpoints.")
        return abs(self.end.semitone_number - self.start.semitone_number)

    def reduced(self) -> "Interval":
        """Return the simple interval obtained by removing compound octaves."""
        return Interval(self.quality, self.simple_number)

    def inverted(self) -> "Interval":
        """Return this interval's inversion."""
        inverted_number = 9 - self.simple_number
        return Interval(QUALITY_INVERSION[self.quality], inverted_number)

    def add(self, other: "Interval") -> "Interval":
        """Return the interval produced by stacking another interval above this one."""
        number = self.number + other.number - 1
        semitones = self.semitones + other.semitones
        quality = self.quality_from_distance(number, semitones)
        return Interval(quality, number)

    def subtract(self, other: "Interval") -> "Interval":
        """Return the interval left after removing another interval from this one."""
        number = self.number - other.number + 1
        semitones = self.semitones - other.semitones
        if number < 1 or semitones < 0:
            raise ValueError("Interval subtraction produced an invalid interval.")
        quality = self.quality_from_distance(number, semitones)
        return Interval(quality, number)

    def construct_from(self, start: Note, direction: str = "up") -> Note:
        """Construct the note at this interval above or below a start note."""
        return_without_octave = start.octave is None
        if return_without_octave:
            start = Note(start.letter, start.accidental, 4)

        sign = 1 if direction == "up" else -1
        target_diatonic = start.diatonic_number + sign * self.step_count
        target_octave, target_step = divmod(target_diatonic, 7)
        target_letter = LETTERS[target_step]
        target_semitone = start.semitone_number + sign * self.semitones
        natural_target = target_octave * 12 + NATURAL_PC[target_letter]
        accidental = target_semitone - natural_target
        if accidental not in INT_TO_ACC:
            raise ValueError("Constructed pitch needs an unsupported accidental.")
        if return_without_octave:
            return Note(target_letter, accidental)
        return Note(target_letter, accidental, target_octave)

    def is_consonant(self) -> bool:
        """Return whether this interval is consonant under this task's convention."""
        return (
            self.quality in CONSONANT_INTERVAL_QUALITIES
            and self.simple_number in CONSONANT_INTERVAL_SIMPLE_NUMBERS
        )

    def same_endpoint_pitches(self, other: "Interval") -> bool:
        """Return whether two concrete intervals have the same sounding endpoints."""
        if self.start is None or self.end is None or other.start is None or other.end is None:
            raise ValueError("Endpoint-pitch comparison requires concrete intervals.")
        return self.start.same_pitch(other.start) and self.end.same_pitch(other.end)


@dataclass(frozen=True)
class Scale:
    """A diatonic collection used for key-context classification tasks."""

    tonic: Note
    mode: str
    degrees: tuple[Note, ...]

    @classmethod
    def build(cls, tonic: Note, mode: str) -> "Scale":
        """Build a major, natural-minor, harmonic-minor, or melodic-minor scale."""
        if mode == "major":
            degree_intervals = (
                ("perfect", 1),
                ("major", 2),
                ("major", 3),
                ("perfect", 4),
                ("perfect", 5),
                ("major", 6),
                ("major", 7),
            )
        elif mode in {"minor", "natural_minor"}:
            degree_intervals = (
                ("perfect", 1),
                ("major", 2),
                ("minor", 3),
                ("perfect", 4),
                ("perfect", 5),
                ("minor", 6),
                ("minor", 7),
            )
        elif mode == "harmonic_minor":
            degree_intervals = (
                ("perfect", 1),
                ("major", 2),
                ("minor", 3),
                ("perfect", 4),
                ("perfect", 5),
                ("minor", 6),
                ("major", 7),
            )
        elif mode == "melodic_minor_ascending":
            degree_intervals = (
                ("perfect", 1),
                ("major", 2),
                ("minor", 3),
                ("perfect", 4),
                ("perfect", 5),
                ("major", 6),
                ("major", 7),
            )
        else:
            raise ValueError(f"Unsupported key mode: {mode}")

        degrees = tuple(
            Interval(quality, number).construct_from(tonic).without_octave()
            for quality, number in degree_intervals
        )
        return cls(tonic, mode, degrees)

    def contains(self, note: Note) -> bool:
        """Return whether a written note spelling belongs to this scale."""
        return any(note.same_spelling(degree) for degree in self.degrees)

    def chromatic_alterations(self) -> list[Note]:
        """Return one-accidental alterations of scale degrees that leave the scale."""
        alterations = []
        for degree in self.degrees:
            for direction in [-1, 1]:
                altered_acc = degree.accidental + direction
                if altered_acc in INT_TO_ACC:
                    altered = Note(degree.letter, altered_acc)
                    if not self.contains(altered):
                        alterations.append(altered)
        return alterations

    def relation_label(self, first: Note, second: Note) -> str:
        """Classify a note-to-note relation as diatonic consonance/dissonance/chromatic."""
        if not self.contains(first) or not self.contains(second):
            return "chromatic alteration"

        interval = Interval.between(first, second, without_octaves=True)
        if interval.is_consonant():
            return "diatonic consonance"
        return "diatonic dissonance"

    def alter_note_outside(self, note: Note, accidental_limit: int) -> Note:
        """Alter one note until it no longer belongs to this scale."""
        for delta in random.sample((1, -1, 2, -2), 4):
            altered = Note(note.letter, note.accidental + delta)
            if abs(altered.accidental) <= accidental_limit and not self.contains(altered):
                return altered
        raise ValueError("Could not alter note outside the scale.")


class AnswerNormalizer:
    """Normalization rules used by answer parsing and scoring."""

    @staticmethod
    def normalize_text(text: object) -> str:
        """Normalize common answer spelling variants before scoring."""
        text = (
            str(text)
            .strip()
            .rstrip(".")
            .replace("♯", "#")
            .replace("♭", "b")
            .replace("𝄪", "##")
            .replace("𝄫", "bb")
        )

        def replace_accidental_word(match: re.Match[str]) -> str:
            """Convert one regex match like 'E-flat' into compact spelling 'Eb'."""
            letter, accidental, octave = match.groups()
            accidental = accidental.lower().replace("-", " ")
            acc = {
                "flat": "b",
                "sharp": "#",
                "natural": "",
                "double flat": "bb",
                "double sharp": "##",
            }[" ".join(accidental.split())]
            return f"{letter}{acc}{octave or ''}"

        # Accept common note-answer spellings such as "E-flat", "E flat",
        # "F double-sharp", and "C natural" in addition to compact "Eb"/"F##"/"C".
        return re.sub(
            r"\b([A-Ga-g])\s*(?:-| )\s*(double\s*[- ]\s*flat|double\s*[- ]\s*sharp|flat|sharp|natural)\s*(-?\d+)?\b",
            replace_accidental_word,
            text,
        )

    @staticmethod
    def text(text: object) -> str:
        """Normalize general text answers for exact symbolic comparison."""
        return " ".join(AnswerNormalizer.normalize_text(text).lower().split())

    @staticmethod
    def interval(text: object) -> str:
        """Normalize interval-answer aliases that preserve exact interval identity."""
        text = " ".join(AnswerNormalizer.text(text).replace("-", " ").split())
        if text in {"double octave", "perfect double octave"}:
            return "perfect fifteenth"
        if text in PERFECT_INTERVAL_NAMES:
            return f"perfect {text}"
        return text

    @staticmethod
    def note(text: object, answer_notation: str | None = None) -> str:
        """Normalize note answers while preserving strict written spelling."""
        text = AnswerNormalizer.normalize_text(text).replace(" ", "")
        if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"', "`"}:
            text = text[1:-1]
        if type(answer_notation) == str and "ABC" in answer_notation:
            return re.sub(r"^=([A-Ga-g][,']*)$", r"\1", text)

        m = re.fullmatch(r"([A-Ga-g])((?:bb)|(?:##)|b|#)?(-?\d+)?", text)
        if not m:
            return text.lower()
        letter, acc, octave = m.groups()
        return f"{letter.upper()}{acc or ''}{octave or ''}"

    @staticmethod
    def roman(text: object) -> str:
        """Normalize compact Roman-numeral answers without changing case semantics."""
        return "".join(AnswerNormalizer.normalize_text(text).split()).replace("ø", "/o")

    @staticmethod
    def note_sequence(text: object, answer_notation: str | None = None) -> tuple[str, ...]:
        """Normalize a hyphen-separated sequence of note names."""
        raw_notes = AnswerNormalizer.normalize_text(text).split("-")
        return tuple(AnswerNormalizer.note(note.strip(), answer_notation) for note in raw_notes if note.strip())


@dataclass(frozen=True)
class ABCContext:
    """ABC header fields plus the key-signature accidentals implied by K:."""

    default_length: str
    meter: str
    key: str
    key_signature: dict[str, int]

    def header(self) -> str:
        """Render the ABC header text for this context."""
        return f"L:{self.default_length}\nM:{self.meter}\nK:{self.key}"

    @classmethod
    def random(cls) -> "ABCContext":
        """Sample a common ABC header context and its key signature."""
        key = random.choice(ABC_KEYS)
        return cls(
            default_length=random.choice(ABC_DEFAULT_LENGTHS),
            meter=random.choice(ABC_METERS),
            key=key,
            key_signature=ABC_KEY_SIGNATURES[key],
        )

    @staticmethod
    def pitch_body(note: Note) -> str:
        """Render the ABC letter and octave markers, without accidental prefix."""
        if note.octave is None:
            return note.letter

        absolute_diatonic_index = (note.octave - 4) * 7 + note.step
        if absolute_diatonic_index < 0:
            commas = (-absolute_diatonic_index + 6) // 7
            return f"{note.letter}{',' * commas}"
        if absolute_diatonic_index < 7:
            return note.letter
        apostrophes = (absolute_diatonic_index - 7) // 7
        octave_marks = "'" * apostrophes
        return f"{note.letter.lower()}{octave_marks}"

    @staticmethod
    def note_token(note: Note, written_accidental: int | None) -> str:
        """Render an ABC note token, optionally omitting the accidental prefix."""
        prefix = "" if written_accidental is None else ABC_ACCIDENTAL_PREFIX[written_accidental]
        return f"{prefix}{ABCContext.pitch_body(note)}"

    @staticmethod
    def duration_suffix(duration: int | None = None) -> str:
        """Render an optional ABC duration suffix after a note or chord."""
        if duration is None and random.random() < ABC_OMIT_DURATION_SHARE:
            return ""
        duration = random.choice(ABC_EVENT_DURATIONS) if duration is None else duration
        return str(duration)

    @staticmethod
    def compact_note(note: Note, force_natural: bool = False) -> str:
        """Render a compact ABC note token outside a full-score context."""
        written_accidental = note.accidental if note.accidental != 0 or force_natural else None
        return ABCContext.note_token(note, written_accidental)

    @staticmethod
    def quote_note_token(token: str) -> str:
        """Quote a standalone ABC note token so octave commas read as notation."""
        return f'"{token}"'

    def render_event(
        self,
        note: Note,
        with_octave: bool | None = None,
        duration: int | None = None,
        explicit_accidental: bool | None = None,
    ) -> "ABCRenderedNote":
        """Render one ABC event while resolving omitted accidentals through K:."""
        if with_octave is not None:
            note = Note(note.letter, note.accidental, note.octave if with_octave else None)

        key_accidental = self.key_signature.get(note.letter, 0)
        if explicit_accidental is None:
            explicit_accidental = note.accidental != key_accidental or random.random() < ABC_EXPLICIT_ACCIDENTAL_SHARE
        written_accidental = note.accidental if explicit_accidental else None
        token = self.note_token(note, written_accidental)
        duration_suffix = self.duration_suffix(duration)
        return ABCRenderedNote(
            note=note,
            token=token,
            event=f"{token}{duration_suffix}",
            explicit_accidental=explicit_accidental,
            key_accidental=key_accidental,
        )

    def score_text(self, events: Sequence[str]) -> str:
        """Render a full ABC score from already rendered events."""
        return f"{self.header()}\n  {' | '.join(events)} |] %1"

    def resolution_sentence(self, rendered: "ABCRenderedNote") -> str:
        """Explain how one ABC score token resolves after applying the key."""
        score_note = self.quote_note_token(rendered.token)
        resolved_note = NoteRenderer.note(rendered.note, COMPACT_ABC_STYLE, force_natural=True)
        word = ACCIDENTAL_WORDS[rendered.note.accidental]
        if rendered.explicit_accidental:
            override = f", overriding K:{self.key}" if rendered.key_accidental != 0 and rendered.key_accidental != rendered.note.accidental else ""
            return f"The score note {score_note} explicitly marks {rendered.note.letter} {word}{override}, so it represents {resolved_note}."

        key_word = ACCIDENTAL_WORDS[rendered.key_accidental]
        if rendered.key_accidental == 0:
            return f"In K:{self.key}, {rendered.note.letter} has no key-signature accidental, so the score note {score_note} represents {resolved_note}."
        return f"The key signature K:{self.key} makes {rendered.note.letter} {key_word}, so the score note {score_note} represents {resolved_note}."

    def score(self, notes: Sequence[Note], with_octave: bool | None = None, force_natural: bool = False) -> str:
        """Render one or more notes as a small full ABC score fragment."""
        rendered = [
            self.render_event(note, with_octave=with_octave, explicit_accidental=True if force_natural else None)
            for note in notes
        ]
        return self.score_text([note.event for note in rendered])

    @classmethod
    def random_score(cls, notes: Sequence[Note], with_octave: bool | None = None, force_natural: bool = False) -> str:
        """Render a small full ABC score fragment in a sampled context."""
        return cls.random().score(notes, with_octave, force_natural)

    @classmethod
    def interval_score(cls, start: Note, end: Note, with_octave: bool = True, interval_number: int | None = None) -> str:
        """Render two notes as one harmonic ABC interval."""
        score, _, _ = cls.interval_score_with_resolution(start, end, with_octave, interval_number)
        return score

    @classmethod
    def interval_score_with_resolution(
        cls,
        start: Note,
        end: Note,
        with_octave: bool = True,
        interval_number: int | None = None,
    ) -> tuple[str, tuple["ABCRenderedNote", "ABCRenderedNote"], "ABCContext"]:
        """Render a harmonic ABC interval and keep key-resolution data."""
        if not with_octave:
            if interval_number is None:
                raise ValueError("Rendering an octave-less full ABC interval requires an interval number.")
            start = Note(start.letter, start.accidental, 4)
            target_diatonic = start.diatonic_number + interval_number - 1
            end_octave, end_step = divmod(target_diatonic, 7)
            if end_step != end.step:
                raise ValueError("Interval number does not match the endpoint letters.")
            end = Note(end.letter, end.accidental, end_octave)
        duration_suffix = cls.duration_suffix()
        context = cls.random()
        rendered_start = context.render_event(start)
        rendered_end = context.render_event(end)
        interval_event = f"[{rendered_start.token}{rendered_end.token}]{duration_suffix}"
        return context.score_text([interval_event]), (rendered_start, rendered_end), context

@dataclass(frozen=True)
class ABCRenderedNote:
    """A score token and the resolved pitch it represents in its ABC key."""

    note: Note
    token: str
    event: str
    explicit_accidental: bool
    key_accidental: int

class NoteRenderer:
    """Rendering rules for prompt notes, answers, and note sequences."""

    @staticmethod
    def note(
        note: Note,
        style: str = SPN_STYLE,
        with_octave: bool | None = None,
        force_natural: bool = False,
        quote_abc: bool = True,
    ) -> str:
        """Render a note; quote standalone compact ABC tokens for display by default."""
        if style == SPN_STYLE:
            return note.name(with_octave)

        if style == COMPACT_ABC_STYLE:
            if with_octave is None:
                token = ABCContext.compact_note(note, force_natural)
                return ABCContext.quote_note_token(token) if quote_abc else token

            abc_note = Note(note.letter, note.accidental, note.octave if with_octave else None)
            token = ABCContext.compact_note(abc_note, force_natural)
            return ABCContext.quote_note_token(token) if quote_abc else token

        if style == FULL_ABC_SCORE_STYLE:
            return ABCContext.random_score([note], with_octave, force_natural)

        raise ValueError(f"Unsupported note rendering style: {style}")

    @staticmethod
    def sequence(notes: Sequence[Note], style: str, with_octave: bool | None = True) -> tuple[str, list[str], list[str]]:
        """Render a note sequence, resolved display tokens, and resolution CoT."""
        if style == FULL_ABC_SCORE_STYLE:
            context = ABCContext.random()
            rendered = [context.render_event(note, with_octave=with_octave) for note in notes]
            rendered_text = context.score_text([note.event for note in rendered])
            resolved_notes = [
                NoteRenderer.note(note.note, COMPACT_ABC_STYLE, force_natural=True)
                for note in rendered
            ]
            resolution_cot = [context.resolution_sentence(note) for note in rendered]
            return rendered_text, resolved_notes, resolution_cot

        rendered_notes = [NoteRenderer.note(note, style, with_octave) for note in notes]
        return ", ".join(rendered_notes), rendered_notes, []

    @staticmethod
    def pair(
        start: Note,
        end: Note,
        style: str = SPN_STYLE,
        with_octave: bool = True,
        interval_number: int | None = None,
    ) -> str:
        """Render an interval endpoint pair or full ABC harmonic interval."""
        if style == FULL_ABC_SCORE_STYLE:
            return ABCContext.interval_score(start, end, with_octave, interval_number)
        return f"{NoteRenderer.note(start, style, with_octave)}-{NoteRenderer.note(end, style, with_octave)}"

    @staticmethod
    def notation_hint(style: str) -> str:
        """Return a short prompt sentence naming the input note notation."""
        if style == SPN_STYLE:
            return "Notes are written in scientific pitch notation."
        if style == COMPACT_ABC_STYLE:
            return "Notes are written in compact ABC notation."
        if style == FULL_ABC_SCORE_STYLE:
            return "Notes are written as full ABC score fragments."
        raise ValueError(f"Unsupported note rendering style: {style}")

    @staticmethod
    def answer_rendering(prompt_style: str) -> tuple[str, str, bool]:
        """Return answer style, notation label, and explicit-natural policy."""
        answer_style = SPN_STYLE if prompt_style == SPN_STYLE else COMPACT_ABC_STYLE
        answer_notation = "scientific pitch notation" if answer_style == SPN_STYLE else "compact ABC notation"
        force_natural = prompt_style == FULL_ABC_SCORE_STYLE
        return answer_style, answer_notation, force_natural

    @staticmethod
    def answer_format(answer_notation: str, with_octave: bool | None = None, explicit_accidentals: bool = False) -> str:
        """Return the prompt phrase describing an expected note-answer format."""
        if answer_notation == "compact ABC notation" and with_octave:
            answer_format = "one full compact ABC pitch token"
            if explicit_accidentals:
                answer_format += ", with any accidental made explicit"
            return answer_format

        octave_phrase = "" if with_octave is None else f" {'with' if with_octave else 'without'} octave"
        answer_format = f"one note name{octave_phrase} in {answer_notation}"
        if explicit_accidentals:
            answer_format += ", with any accidental made explicit"
        return answer_format


class PromptFormatter:
    """Prompt-formatting helpers shared by music task generators."""

    @staticmethod
    def options(labels: Sequence[str]) -> str:
        """Render answer choices in a sampled order."""
        return ", ".join(random.sample(list(labels), len(labels)))

    @staticmethod
    def notation_instruction(style: str) -> str:
        """Return the prompt sentence for the sampled note notation."""
        if style == FULL_ABC_SCORE_STYLE:
            return "Interpret the score using its key signature."
        return NoteRenderer.notation_hint(style)

    @staticmethod
    def choice_prompt(
        opener_templates: Sequence[str],
        tail_templates: Sequence[str],
        style: str | None = None,
        notation_separator: str = " ",
        tail_separator: str = " ",
        **values: object,
    ) -> str:
        """Compose a prompt from one sampled opener and one sampled answer-format tail."""
        opener = random.choice(opener_templates).format(**values)
        tail = random.choice(tail_templates).format(**values)
        notation = f"{notation_separator}{PromptFormatter.notation_instruction(style)}" if style is not None else ""
        return f"{opener}{notation}{tail_separator}{tail}"


class Music21Adapter:
    """Conversion helpers between task Note objects and music21 objects."""

    @staticmethod
    def chord(notes: Sequence[Note]) -> m21_chord.Chord:
        """Convert task Note objects to a music21 Chord."""
        return m21_chord.Chord([Music21Adapter.pitch_name(note) for note in notes])

    @staticmethod
    def note_from_pitch(pitch: Any, with_octave: bool = False) -> Note:
        """Convert a music21 Pitch to the task's Note spelling."""
        name = pitch.nameWithOctave if with_octave else pitch.name
        return Note.parse(name.replace("-", "b"))

    @staticmethod
    def pitch_name(note: Note) -> str:
        """Render a Note spelling in music21's flat notation."""
        return note.name().replace("b", "-")


@dataclass(frozen=True)
class ChordRendering:
    """Rendered chord text plus resolved note tokens for reasoning traces."""

    prompt_text: str
    cot_text: str
    resolution_cot: list[str]


class ChordRenderer:
    """Rendering rules for chord-tone collections in prompt text and CoTs."""

    @staticmethod
    def join(rendered_notes: Sequence[str], sep: str = "-") -> str:
        """Join rendered chord tones in the project's chord-list format."""
        return sep.join(rendered_notes)

    @staticmethod
    def render(
        notes: Sequence[Note],
        style: str,
        with_octave: bool = False,
        shuffle: bool = True,
        sep: str = "-",
    ) -> ChordRendering:
        """Render chord tones in SPN, compact ABC, or one full ABC chord score."""
        ordered_notes = random.sample(list(notes), len(notes)) if shuffle else list(notes)
        if style == FULL_ABC_SCORE_STYLE:
            context = ABCContext.random()
            rendered = [context.render_event(note, with_octave=with_octave) for note in ordered_notes]
            chord_event = f"[{''.join(note.token for note in rendered)}]{ABCContext.duration_suffix()}"
            resolved_notes = [
                NoteRenderer.note(note.note, COMPACT_ABC_STYLE, force_natural=True)
                for note in rendered
            ]
            return ChordRendering(
                prompt_text=context.score_text([chord_event]),
                cot_text=ChordRenderer.join(resolved_notes, sep),
                resolution_cot=[context.resolution_sentence(note) for note in rendered],
            )

        rendered_notes = [
            NoteRenderer.note(note, style, with_octave=with_octave)
            for note in ordered_notes
        ]
        rendered_chord = ChordRenderer.join(rendered_notes, sep)
        return ChordRendering(prompt_text=rendered_chord, cot_text=rendered_chord, resolution_cot=[])

    @staticmethod
    def for_cot(
        notes: Sequence[Note],
        style: str,
        with_octave: bool = False,
        sep: str = "-",
    ) -> str:
        """Render canonical chord order in the same notation family as the prompt."""
        note_style = COMPACT_ABC_STYLE if style == FULL_ABC_SCORE_STYLE else style
        return ChordRenderer.join(
            [
                NoteRenderer.note(
                    note,
                    note_style,
                    with_octave=with_octave,
                    force_natural=style == FULL_ABC_SCORE_STYLE,
                )
                for note in notes
            ],
            sep,
        )

    @staticmethod
    def prompt_value(rendering: ChordRendering, style: str) -> str:
        """Return an inline chord value or a full-score chord reference."""
        if style == FULL_ABC_SCORE_STYLE:
            return f"the chord in this ABC score fragment:\n{rendering.prompt_text}"
        return rendering.prompt_text


class ChordTools:
    """Small chord/spelling helpers shared by chord-like task generators."""

    @staticmethod
    def with_ascending_octaves(
        notes: Sequence[Note],
        min_root_octave: int = 1,
        max_root_octave: int = 6,
    ) -> list[Note]:
        """Assign octaves so the given chord-tone order sounds upward."""
        root_octave = random.randint(min_root_octave, max_root_octave)
        voiced_notes = [Note(notes[0].letter, notes[0].accidental, root_octave)]
        for note in notes[1:]:
            octave = voiced_notes[-1].octave
            voiced_note = Note(note.letter, note.accidental, octave)
            while voiced_note.semitone_number <= voiced_notes[-1].semitone_number:
                octave += 1
                voiced_note = Note(note.letter, note.accidental, octave)
            voiced_notes.append(voiced_note)
        return voiced_notes

    @staticmethod
    def pitch_class_set(notes: Sequence[Note]) -> set[int]:
        """Return the pitch-class set represented by a chord."""
        return {note.pc for note in notes}

    @staticmethod
    def different_spelling_same_pitch(note: Note, accidental_limit: int) -> Note:
        """Choose a different spelling for the same pitch when possible."""
        spellings = [
            spelling if note.octave is not None else spelling.without_octave()
            for spelling in note.exact_pitch_spellings(accidental_limit)
            if not note.same_spelling(spelling, include_octave=True)
        ]
        if not spellings:
            return note
        return random.choice(spellings)

    @staticmethod
    def close_voicing(root_position: Sequence[Note]) -> list[Note]:
        """Return a compact voicing in one octave."""
        return list(root_position)

    @staticmethod
    def open_voicing(root_position: Sequence[Note]) -> list[Note]:
        """Return a deliberately open voicing with skipped chord members."""
        root_octave = root_position[0].octave or 4
        root_step = root_position[0].step
        for _ in range(GENERATION_RETRY_LIMIT):
            voiced_notes = [
                Note(root_position[0].letter, root_position[0].accidental, root_octave)
            ]
            for index, note in enumerate(root_position[1:], start=1):
                base_octave = note.octave
                if base_octave is None:
                    base_octave = root_octave + int(note.step < root_step and index > 0)
                octave = base_octave + random.randint(0, 2)
                voiced_notes.append(Note(note.letter, note.accidental, octave))
            voiced_notes.sort(key=lambda note: note.semitone_number)
            span = voiced_notes[-1].semitone_number - voiced_notes[0].semitone_number
            if span > 12 and ChordTools.skips_chord_member(voiced_notes, root_position):
                return voiced_notes

        if len(root_position) == 3:
            root, third, fifth = root_position
            return [
                Note(root.letter, root.accidental, root_octave),
                Note(fifth.letter, fifth.accidental, root_octave + 1),
                Note(third.letter, third.accidental, root_octave + 2),
            ]
        root, third, fifth, seventh = root_position
        return [
            Note(root.letter, root.accidental, root_octave),
            Note(fifth.letter, fifth.accidental, root_octave + 1),
            Note(third.letter, third.accidental, root_octave + 2),
            Note(seventh.letter, seventh.accidental, root_octave + 3),
        ]

    @staticmethod
    def skips_chord_member(voicing: Sequence[Note], root_position: Sequence[Note]) -> bool:
        """Return whether adjacent voiced notes skip over an available chord tone."""
        voice_numbers = sorted(note.semitone_number for note in voicing)
        voice_number_set = set(voice_numbers)
        min_octave = min(note.octave for note in voicing if note.octave is not None) - 1
        max_octave = max(note.octave for note in voicing if note.octave is not None) + 1
        member_numbers = {
            Note(member.letter, member.accidental, octave).semitone_number
            for member in root_position
            for octave in range(min_octave, max_octave + 1)
        }
        skipped_member_numbers = member_numbers - voice_number_set
        return any(
            any(lower < member_number < upper for member_number in skipped_member_numbers)
            for lower, upper in zip(voice_numbers, voice_numbers[1:])
        )


class TextFormatter:
    """Small text-formatting helpers used when composing prompts and CoTs."""

    @staticmethod
    def article(phrase: str) -> str:
        """Return a phrase prefixed with the appropriate indefinite article."""
        phrase = phrase.strip()
        if not phrase:
            raise ValueError("Cannot add an article to an empty phrase.")

        lower = phrase.lower()
        first_word = lower.split(maxsplit=1)[0]
        starts_with_vowel_sound = lower[0] in "aeio" and not lower.startswith(("uni", "use", "eu"))
        starts_with_letter_name = first_word in {"f", "l", "m", "n", "r", "s", "x"}
        use_an = starts_with_vowel_sound or starts_with_letter_name
        return f"{'an' if use_an else 'a'} {phrase}"

    @staticmethod
    def capitalize_initial(text: str) -> str:
        """Capitalize only the first character, preserving the rest of the text."""
        # Python’s built-in .capitalize() also lowercases the rest of the string.
        return text[:1].upper() + text[1:]

    @staticmethod
    def count_phrase(count: int, word: str = "semitone", plural: str | None = None) -> str:
        """Format a count with a simple plural suffix."""
        if count == 1:
            return f"{count} {word}"
        return f"{count} {plural or word + 's'}"

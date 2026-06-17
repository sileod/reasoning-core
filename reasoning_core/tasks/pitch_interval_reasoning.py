from dataclasses import dataclass
from collections.abc import Sequence
import random
from typing import Any

from reasoning_core.template import Config, Problem, Task, edict
from reasoning_core.tasks._music_theory import (
    ABCContext,
    AnswerNormalizer,
    CHOICE_TAILS,
    COMPACT_ABC_STYLE,
    FULL_ABC_SCORE_SHARE,
    FULL_ABC_SCORE_STYLE,
    GENERATION_RETRY_LIMIT,
    INTEGER_TAILS,
    INTERVAL_CLASS_LABELS,
    MINOR_SCALE_MODES,
    Note,
    NoteRenderer,
    NOTE_ANSWER_TAILS,
    PITCH_CLASS_LABELS,
    PromptFormatter,
    Scale,
    SPN_STYLE,
    TextFormatter,
    Interval,
    YES_NO_TAILS,
    key_tonics,
)

MODE_NAMES = (
    "interval_naming",
    "interval_arithmetic",
    "pitch_count",
    "interval_classification",
    "enharmonic_interval_comparison",
    "instrument_transposition",
    "interval_construction",
    "transposition_chain",
)

INTERVAL_CONSTRUCTION_CASES = (
    "prompt_octave_answer_octave",
    "prompt_octave_answer_no_octave",
    "prompt_no_octave_answer_no_octave",
)
# Common written-to-sounding transpositions used here; every instrument sounds
# the listed interval lower than written.
TRANSPOSING_INSTRUMENTS = (
    ("B-flat clarinet", "major", 2),
    ("B-flat trumpet", "major", 2),
    ("A clarinet", "minor", 3),
    ("F horn", "perfect", 5),
    ("English horn", "perfect", 5),
    ("B-flat soprano saxophone", "major", 2),
    ("E-flat alto saxophone", "major", 6),
    ("B-flat tenor saxophone", "major", 9),
    ("E-flat baritone saxophone", "major", 13),
    ("B-flat bass clarinet", "major", 9),
    ("guitar", "perfect", 8),
    ("double bass", "perfect", 8),
)

INTERVAL_NAME_OPENERS = (
    "Name the interval from {start} to {end}.",
    "Identify the interval from {start} up to {end}.",
    "What interval goes from {start} to {end}?",
    "Classify the interval formed by {start} and {end}.",
    "Determine the interval from {start} to {end}.",
    "Give the interval from {start} up to {end}.",
    "What is the written interval between {start} and {end}?",
    "Name the ascending interval whose endpoints are {start} and {end}.",
)
INTERVAL_NAME_SCORE_OPENERS = (
    "Name the interval between the two notes in this ABC score fragment:\n{score}",
    "Identify the interval shown by the two notes in this ABC score fragment:\n{score}",
    "What interval is formed by the two notes in this ABC score fragment?\n{score}",
    "Classify the interval in this ABC score fragment:\n{score}",
    "Determine the interval represented by the two notes in this ABC score fragment:\n{score}",
    "Name the harmonic interval shown in this ABC score fragment:\n{score}",
    "What written interval do the two notes in this ABC score fragment form?\n{score}",
    "Identify the interval between the two notated pitches in this ABC score fragment:\n{score}",
)
INTERVAL_NAME_TAILS = (
    "The answer is one interval name, including compound/simple size as written.",
    "Give one interval name, keeping the compound or simple size as written.",
    "Answer with one interval name, preserving whether the interval is simple or compound.",
    "The expected answer is one interval name with the written interval size preserved.",
    "Provide one interval name, using the compound or simple size shown.",
)
INTERVAL_ARITHMETIC_SINGLE_OPENERS = {
    "add": (
        "Add {operand} to {start_interval}.",
        "Combine {start_interval} with {operand} by addition.",
        "Starting from {start_interval}, add {operand}.",
        "Use interval addition to combine {start_interval} and {operand}.",
        "Find the interval produced by adding {operand} to {start_interval}.",
    ),
    "subtract": (
        "Subtract {operand} from {start_interval}.",
        "Starting from {start_interval}, subtract {operand}.",
        "Remove {operand} from {start_interval} by interval arithmetic.",
        "Use interval subtraction to take {operand} away from {start_interval}.",
        "Find the interval left after subtracting {operand} from {start_interval}.",
    ),
    "reduce_then_invert": (
        "Reduce {start_interval} to a simple interval and invert it.",
        "Starting from {start_interval}, reduce it to a simple interval, then invert it.",
        "Take {start_interval}, reduce it to simple form, and invert the result.",
        "Convert {start_interval} to its simple form, then invert that simple interval.",
        "Find the inversion after reducing {start_interval} to a simple interval.",
    ),
}
INTERVAL_ARITHMETIC_CHAIN_OPENERS = (
    "Start with {start_interval}, then {operations}.",
    "Beginning with {start_interval}, perform these steps: {operations}.",
    "Apply this interval-arithmetic chain to {start_interval}: {operations}.",
    "From {start_interval}, carry out this sequence of interval operations: {operations}.",
    "Use {start_interval} as the starting interval, then {operations}.",
    "Compute the result of this interval chain starting at {start_interval}: {operations}.",
)
INTERVAL_ONLY_TAILS = (
    "The answer is one interval name.",
    "Give one interval name.",
    "Answer with one interval name.",
    "Provide a single interval name.",
    "The expected answer is one interval name.",
)
PITCH_COUNT_OPENERS = (
    "Under pitch-class equivalence, how many distinct pitch classes are in {notes}?",
    "How many distinct pitch classes appear in {notes}?",
    "Counting enharmonically equivalent spellings as the same pitch class, how many distinct pitch classes are in {notes}?",
    "Reduce {notes} to pitch classes. How many distinct pitch classes are present?",
    "Treat octave and enharmonic spelling differences as pitch-class equivalence. How many distinct pitch classes are in {notes}?",
    "How many different pitch classes are represented by {notes}?",
    "After reducing {notes} to pitch classes, how many unique classes remain?",
    "Count the distinct pitch classes represented in {notes}.",
)
PITCH_COUNT_SCORE_OPENERS = (
    "Under pitch-class equivalence, how many distinct pitch classes are in this ABC score fragment?\n{score}",
    "How many distinct pitch classes appear in this ABC score fragment?\n{score}",
    "Counting enharmonically equivalent spellings as the same pitch class, how many distinct pitch classes are in this ABC score fragment?\n{score}",
    "Reduce the notes in this ABC score fragment to pitch classes. How many distinct pitch classes are present?\n{score}",
    "How many different pitch classes are represented in this ABC score fragment?\n{score}",
    "Count the distinct pitch classes in this ABC score fragment:\n{score}",
)
INTERVAL_CLASSIFICATION_OPENERS = (
    "In {key}, classify the note-to-note relation {relation}.",
    "For {key}, label the relation {relation}.",
    "Using {key}, classify the note-to-note relation {relation}.",
    "In the collection {key}, what label applies to the relation {relation}?",
    "Within {key}, choose the label for the relation {relation}.",
    "Using the {key} collection, classify the relation {relation}.",
    "For the key context {key}, what label fits the relation {relation}?",
    "Determine whether the relation {relation} in {key} is diatonic consonance, diatonic dissonance, or chromatic alteration.",
)
ENHARMONIC_INTERVAL_OPENERS = (
    "Are {first} and {second} enharmonically equivalent intervals?",
    "Do {first} and {second} represent enharmonically equivalent intervals?",
    "Compare {first} and {second}: are the intervals enharmonically equivalent?",
    "Do the corresponding endpoint pitches of {first} and {second} match enharmonically?",
    "Check whether {first} and {second} are enharmonically equivalent written intervals.",
    "Do {first} and {second} describe intervals with matching sounding endpoints?",
    "Are the two written intervals {first} and {second} enharmonically the same?",
    "Compare the endpoint pitches of {first} and {second}. Are the intervals enharmonically equivalent?",
)
ENHARMONIC_INTERVAL_SCORE_OPENERS = (
    "Is the interval in this ABC score fragment:\n{first}\nenharmonically equivalent to the interval in this ABC score fragment:\n{second}?",
    "Compare the interval in this ABC score fragment:\n{first}\nwith the interval in this ABC score fragment:\n{second}\nAre they enharmonically equivalent?",
    "Do these two ABC score fragments show enharmonically equivalent intervals?\nFirst fragment:\n{first}\nSecond fragment:\n{second}",
    "After interpreting the key signatures, are the intervals in these ABC score fragments enharmonically equivalent?\nFirst fragment:\n{first}\nSecond fragment:\n{second}",
    "Compare the two notated intervals below for enharmonic equivalence.\nFirst fragment:\n{first}\nSecond fragment:\n{second}",
    "Do the corresponding endpoint pitches match in these two ABC interval fragments?\nFirst fragment:\n{first}\nSecond fragment:\n{second}",
)
ABC_PAIR_YES_NO_TAILS = (
    "Interpret each ABC score using its key signature. The answer is exactly 'yes' or 'no'.",
    "Use each ABC score's key signature, then answer exactly 'yes' or 'no'.",
    "After resolving both ABC scores by key signature, give one answer: 'yes' or 'no'.",
    "Resolve both ABC scores using their key signatures, then respond with exactly 'yes' or 'no'.",
)
INSTRUMENT_TRANSPOSITION_OPENERS = (
    "{instrument_article} part writes {written}. What sounding pitch is produced?",
    "{instrument_article} part has written note {written}. What is the sounding pitch?",
    "For {instrument_article_lower} part, convert the written note {written} to sounding pitch.",
    "{instrument_article} part writes {written}; convert it to sounding pitch.",
    "{instrument_article} part has written pitch {written}. What pitch actually sounds?",
    "{instrument_article} part notates {written}. What pitch actually sounds?",
)
INSTRUMENT_TRANSPOSITION_SCORE_OPENERS = (
    "{instrument_article} part writes the note in this ABC score fragment:\n{score}\nWhat sounding pitch is produced?",
    "For {instrument_article_lower} part, convert the written note in this ABC score fragment to sounding pitch:\n{score}",
    "{instrument_article} part uses this written ABC score fragment:\n{score}\nWhat pitch sounds?",
    "{instrument_article} part uses this written ABC score fragment. What sounding pitch results?\n{score}",
    "{instrument_article} part writes the note in the ABC score fragment below. Convert it to sounding pitch:\n{score}",
    "{instrument_article} part notates the pitch in this ABC score fragment:\n{score}\nWhat pitch actually sounds?",
)
INTERVAL_CONSTRUCTION_OPENERS = (
    "Build {interval} {position} {start}.",
    "Find the note {interval} {position} {start}.",
    "Starting from {start}, build {interval} {position}.",
    "What note lies {interval} {position} {start}?",
    "Construct the note {interval} {position} {start}.",
    "From {start}, move {interval} {position}.",
)
INTERVAL_CONSTRUCTION_SCORE_OPENERS = (
    "Build {interval} {position} the note in this ABC score fragment:\n{score}",
    "Find the note {interval} {position} the note in this ABC score fragment:\n{score}",
    "Starting from the note in this ABC score fragment, build {interval} {position}:\n{score}",
    "Construct the note {interval} {position} the note shown in this ABC score fragment:\n{score}",
    "What note lies {interval} {position} the note in this ABC score fragment?\n{score}",
    "Use the note in this ABC score fragment as the starting note, then build {interval} {position}:\n{score}",
)
TRANSPOSITION_CHAIN_OPENERS = (
    "Transpose {start} {steps}.",
    "Starting from {start}, apply these transpositions in order: {steps}.",
    "Move from {start} through this transposition chain: {steps}.",
    "Begin on {start} and perform these transpositions in order: {steps}.",
    "Apply the ordered transposition sequence {steps} starting from {start}.",
    "From {start}, transpose step by step: {steps}.",
)
TRANSPOSITION_CHAIN_SCORE_OPENERS = (
    "Transpose the note in this ABC score fragment:\n{score}\nApply these transpositions in order: {steps}.",
    "Starting from the note in this ABC score fragment, apply these transpositions in order:\n{score}\n{steps}.",
    "Use the note in this ABC score fragment as the start, then transpose {steps}:\n{score}",
    "Begin with the note in this ABC score fragment and perform these transpositions in order:\n{score}\n{steps}.",
    "Apply this ordered transposition chain to the note in the ABC score fragment:\n{score}\n{steps}.",
    "Take the note in this ABC score fragment as the starting pitch, then transpose {steps}:\n{score}",
)

@dataclass
class PitchIntervalConfig(Config):
    """Configuration knobs for pitch- and interval-reasoning generation."""

    # Which generation mode to use. "any" samples uniformly among all supported modes.
    mode: str = "any"

    # Shared length knob for chain-like tasks, such as interval arithmetic
    # operation chains and sequential transpositions.
    chain_len: int = 1

    # Largest diatonic interval number allowed. 8 is an octave, 9 is a ninth,
    # 10 is a tenth, and so on; larger values make compound intervals possible.
    max_interval_number: int = 8

    # Number of note items in count-style tasks. Higher values produce longer
    # note lists with more duplicates and enharmonic distractors.
    n_candidates: int = 4

    # Maximum accidental complexity in generated spellings: 0 allows naturals,
    # 1 allows sharps/flats, and 2 allows double-sharps/double-flats.
    max_accidental: int = 1

    # Maximum number of sharps/flats in analytical key signatures.
    key_complexity: int = 2

    # Probability of writing prompt notes in ABC notation instead of scientific
    # pitch notation. ABC examples are split into 70% compact note tokens and
    # 30% full score fragments with randomly sampled common L/M/K headers.
    p_abc: float = 0.20

    # Maximum attempts to generate a valid instance before failing. Some random
    # combinations are rejected because they require unsupported spellings.
    max_tries: int = 256

    # Override of Config.update; called by Config.set_level() to raise difficulty.
    def update(self, c: float = 1) -> None:
        """Increase generation difficulty by updating monotonic config knobs."""
        self.chain_len += 0.6 * c
        self.max_interval_number = min(20, self.max_interval_number + 1.5 * c)
        self.n_candidates += c
        self.max_accidental = min(2, self.max_accidental + 0.2 * c)
        self.key_complexity = min(7, self.key_complexity + c)
        self.p_abc = min(0.50, self.p_abc + 0.06 * c)

    def random_style(self) -> str:
        """Sample the note-rendering style for a prompt."""
        roll = random.random()
        if roll < FULL_ABC_SCORE_SHARE * self.p_abc:
            return FULL_ABC_SCORE_STYLE
        if roll < self.p_abc:
            return COMPACT_ABC_STYLE
        return SPN_STYLE


class PitchIntervalReasoning(Task):
    """Procedural generator for pitch, interval, key, and transposition tasks."""

    # Override of Task.__init__; keeps the normal task setup and adjusts balancing.
    def __init__(self, config: PitchIntervalConfig = PitchIntervalConfig()) -> None:
        """Initialize the task and tighten batch balancing for low-cardinality modes."""
        super().__init__(config=config)
        # The default 0.5 allows too many repeats for low-cardinality modes
        # such as yes/no comparison and three-label interval classification.
        self.balancing_key_ratio = 0.3

    def _sample_mode(self) -> str:
        """Choose a concrete generation mode from the configured mode setting."""
        if self.config.mode != "any":
            if self.config.mode not in MODE_NAMES:
                raise ValueError(f"Unknown pitch interval mode: {self.config.mode}")
            return self.config.mode
        return random.choice(MODE_NAMES)

    # Override of Task.generate; returns one generated Problem.
    def generate(self) -> Problem:
        """Generate one pitch/interval reasoning problem."""
        mode = self._sample_mode()
        for _ in range(self.config.max_tries):
            try:
                # Dispatch by convention: "pitch_count" -> self._generate_pitch_count().
                return getattr(self, f"_generate_{mode}")()
            except (KeyError, ValueError):
                continue
        raise RuntimeError(f"Failed to generate a pitch_interval_reasoning instance for mode {mode!r}.")

    # Override of Task.prompt; prompt text is already stored in metadata.
    def prompt(self, metadata: Any) -> str:
        """Return the prompt string stored in generated metadata."""
        return metadata.prompt

    # Override of Task.score_answer; normalizes music-specific answer formats.
    def score_answer(self, answer: object, entry: Problem) -> float:
        """Score an answer after normalizing the expected music-answer format."""
        expected = str(entry.answer)
        # Older metadata may omit answer_kind, so plain text remains the fallback.
        kind = entry.metadata.get("answer_kind", "text")
        if kind == "note":
            answer_notation = entry.metadata.get("answer_notation")
            return float(AnswerNormalizer.note(answer, answer_notation) == AnswerNormalizer.note(expected, answer_notation))
        if kind == "interval":
            return float(AnswerNormalizer.interval(answer) == AnswerNormalizer.interval(expected))
        if kind == "yes_no":
            return float(AnswerNormalizer.text(answer) == expected)
        if kind == "integer":
            try:
                return float(int(answer) == int(expected))
            except Exception:
                return 0.0
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

    def _generate_interval_naming(self) -> Problem:
        """Generate a task asking for the named interval between two notes."""
        style = self.config.random_style()
        start, end, quality, number = self._sample_constructed_pair()
        interval = Interval(quality, number, start, end)
        answer = interval.name()
        note_token_style = COMPACT_ABC_STYLE if style == FULL_ABC_SCORE_STYLE else style
        rendered_start = NoteRenderer.note(start, note_token_style, force_natural=style == FULL_ABC_SCORE_STYLE)
        rendered_end = NoteRenderer.note(end, note_token_style, force_natural=style == FULL_ABC_SCORE_STYLE)
        resolution_cot = []
        if style == FULL_ABC_SCORE_STYLE:
            rendered_pair, rendered_notes, abc_context = ABCContext.interval_score_with_resolution(start, end)
            resolution_cot = [abc_context.resolution_sentence(note) for note in rendered_notes]
            prompt = PromptFormatter.choice_prompt(
                INTERVAL_NAME_SCORE_OPENERS,
                INTERVAL_NAME_TAILS,
                style=style,
                notation_separator="\n",
                score=rendered_pair,
            )
        else:
            prompt = PromptFormatter.choice_prompt(
                INTERVAL_NAME_OPENERS,
                INTERVAL_NAME_TAILS,
                style=style,
                start=rendered_start,
                end=rendered_end,
            )
        cot = resolution_cot + [
            f"Counting the note letters from the first note up to the second note, including octave changes, gives interval number {interval.number} ({interval.number_name}).",
            f"The chromatic distance from {rendered_start} to {rendered_end} is {TextFormatter.count_phrase(interval.chromatic_distance)}.",
            f"The major/perfect form of {TextFormatter.article(interval.number_name)} is {TextFormatter.count_phrase(interval.base_semitones)}.",
            f"Comparing those distances gives the quality {interval.quality}.",
            f"So the interval is {TextFormatter.article(answer)}.",
        ]
        return self._problem(
            "interval_naming",
            prompt,
            answer,
            "interval",
            cot,
            start_note=start.name(),
            end_note=end.name(),
            style=style,
        )

    def _generate_interval_arithmetic(self) -> Problem:
        """Generate a task combining named intervals by arithmetic operations."""
        start_interval, steps = self._sample_interval_arithmetic_chain()
        answer_interval = steps[-1][2]
        answer = answer_interval.name()
        start_interval_text = TextFormatter.article(start_interval.name())
        if len(steps) == 1:
            operation, operand, _ = steps[0]
            prompt = PromptFormatter.choice_prompt(
                INTERVAL_ARITHMETIC_SINGLE_OPENERS[operation],
                INTERVAL_ONLY_TAILS,
                start_interval=start_interval_text,
                operand=TextFormatter.article(operand.name()) if operand is not None else "",
            )
        else:
            operations = ", then ".join(
                self._interval_arithmetic_operation_phrase(operation, interval)
                for operation, interval, _ in steps
            )
            prompt = PromptFormatter.choice_prompt(
                INTERVAL_ARITHMETIC_CHAIN_OPENERS,
                INTERVAL_ONLY_TAILS,
                start_interval=start_interval_text,
                operations=operations,
            )

        operation_names = [operation for operation, _, _ in steps]
        cot = [
            f"Start with {TextFormatter.article(start_interval.name())}: interval number {start_interval.number} and {TextFormatter.count_phrase(start_interval.semitones)}.",
        ]
        if any(operation in {"add", "subtract"} for operation in operation_names):
            cot.append("For interval numbers, addition uses current + interval - 1, and subtraction uses current - interval + 1.")
        if "reduce_then_invert" in operation_names:
            cot.append(
                "For reduce-then-invert, first reduce compound interval numbers by subtracting 7 for each octave; "
                "then invert the simple interval so the two simple interval numbers add to 9."
            )
        current = start_interval
        for operation, operand, result in steps:
            if operation == "add":
                cot.append(
                    f"Add {TextFormatter.article(operand.name())}: interval number {current.number} + {operand.number} - 1 = {result.number}, "
                    f"and semitones {current.semitones} + {operand.semitones} = {result.semitones}."
                )
            elif operation == "subtract":
                cot.append(
                    f"Subtract {TextFormatter.article(operand.name())}: interval number {current.number} - {operand.number} + 1 = {result.number}, "
                    f"and semitones {current.semitones} - {operand.semitones} = {result.semitones}."
                )
            else:
                reduced = current.reduced()
                cot.append(
                    f"Reduce {TextFormatter.article(current.name())} to {TextFormatter.article(reduced.name())}; "
                    f"then invert it: 9 - {reduced.number} = {result.number}, and {reduced.quality} inverts to {result.quality}."
                )
            current = result
        cot.append(
            f"With interval number {answer_interval.number} and {TextFormatter.count_phrase(answer_interval.semitones)}, "
            f"the resulting interval is {TextFormatter.article(answer)}."
        )
        return self._problem(
            "interval_arithmetic",
            prompt,
            answer,
            "interval",
            cot,
            start_interval_quality=start_interval.quality,
            start_interval_number=start_interval.number,
            operations=[
                self._interval_arithmetic_metadata(operation, operand)
                for operation, operand, _ in steps
            ],
        )

    def _interval_arithmetic_operation_phrase(self, operation: str, operand: Interval | None) -> str:
        """Render one interval-arithmetic operation in a prompt."""
        if operation in {"add", "subtract"}:
            return f"{operation} {TextFormatter.article(operand.name())}"
        if operation == "reduce_then_invert":
            return "reduce to a simple interval and invert it"
        raise ValueError(f"Unsupported interval-arithmetic operation: {operation}")

    def _interval_arithmetic_metadata(self, operation: str, operand: Interval | None) -> dict[str, object]:
        """Render compact operation metadata for one interval-arithmetic step."""
        metadata: dict[str, object] = {"operation": operation}
        if operand is not None:
            metadata["interval_quality"] = operand.quality
            metadata["interval_number"] = operand.number
        return metadata

    def _generate_pitch_count(self) -> Problem:
        """Generate a task counting distinct pitch classes in a note list."""
        style = self.config.random_style()
        accidental_limit = self.config.max_accidental
        n_candidates = self.config.n_candidates
        distinct = random.randint(2, n_candidates)
        pcs = random.sample(range(12), distinct)
        notes = []
        for pc in pcs:
            notes.append(random.choice(Note.spellings_for_pitch_class(pc, accidental_limit, with_octave=True)))
        while len(notes) < n_candidates:
            pc = random.choice(pcs)
            notes.append(random.choice(Note.spellings_for_pitch_class(pc, accidental_limit, with_octave=True)))
        random.shuffle(notes)
        rendered_note_list, rendered_notes, resolution_cot = NoteRenderer.sequence(notes, style)
        if style == FULL_ABC_SCORE_STYLE:
            prompt = PromptFormatter.choice_prompt(
                PITCH_COUNT_SCORE_OPENERS,
                INTEGER_TAILS,
                style=style,
                notation_separator="\n",
                score=rendered_note_list,
            )
        else:
            prompt = PromptFormatter.choice_prompt(
                PITCH_COUNT_OPENERS,
                INTEGER_TAILS,
                style=style,
                notes=rendered_note_list,
            )
        unique_pcs = sorted({note.pc for note in notes})
        cot = resolution_cot + [
            f"{rendered_note} maps to pitch class {note.pc} ({PITCH_CLASS_LABELS[note.pc]})."
            for rendered_note, note in zip(rendered_notes, notes)
        ]
        cot.append(
            "The distinct pitch classes are "
            + ", ".join(f"{pc} ({PITCH_CLASS_LABELS[pc]})" for pc in unique_pcs)
            + f", so there are {TextFormatter.count_phrase(len(unique_pcs), 'distinct pitch class', 'distinct pitch classes')}."
        )
        return self._problem(
            "pitch_count",
            prompt,
            len(unique_pcs),
            "integer",
            cot,
            notes=[n.name() for n in notes],
            style=style,
        )

    def _generate_interval_classification(self) -> Problem:
        """Generate a task classifying a note-to-note relation in a key."""
        accidental_limit = self.config.max_accidental
        key_complexity = self.config.key_complexity
        if random.choice(["major", "minor"]) == "major":
            scale_mode = "major"
            key_label = "major"
            tonic = Note.parse(random.choice(key_tonics("major", key_complexity)))
        else:
            scale_mode, key_label = random.choice(MINOR_SCALE_MODES)
            tonic = Note.parse(random.choice(key_tonics("minor", key_complexity)))
        scale = Scale.build(tonic, scale_mode)

        label = random.choice(INTERVAL_CLASS_LABELS)
        if label == "chromatic alteration":
            first = Note.random(self.config, with_octave=False, accidental_limit=accidental_limit)
            if scale.contains(first):
                second = random.choice(scale.chromatic_alterations())
            else:
                second = Note.random(self.config, with_octave=False, accidental_limit=accidental_limit)
        else:
            candidates = [
                (first, second)
                for first in scale.degrees
                for second in scale.degrees
                if not first.same_spelling(second)
                and scale.relation_label(first, second) == label
            ]
            first, second = random.choice(candidates)

        first_in_key = scale.contains(first)
        second_in_key = scale.contains(second)
        prompt = PromptFormatter.choice_prompt(
            INTERVAL_CLASSIFICATION_OPENERS,
            CHOICE_TAILS,
            key=f"{tonic.name(False)} {key_label}",
            relation=f"{first.name(False)}-{second.name(False)}",
            options=PromptFormatter.options(INTERVAL_CLASS_LABELS),
        )
        scale_text = ", ".join(note.name(False) for note in scale.degrees)
        cot = [f"The {tonic.name(False)} {key_label} collection is {scale_text}."]
        cot.append(
            f"{first.name(False)} is {'in' if first_in_key else 'not in'} the collection, "
            f"and {second.name(False)} is {'in' if second_in_key else 'not in'} the collection."
        )
        if label == "chromatic alteration":
            cot.append("At least one note is outside the collection, so the relation is a chromatic alteration.")
        else:
            interval = Interval.between(first, second, without_octaves=True)
            consonance_word = "consonance" if label == "diatonic consonance" else "dissonance"
            cot.append(
                f"The written interval from {first.name(False)} to {second.name(False)} "
                f"is {TextFormatter.article(interval.name())}."
            )
            cot.append(f"Since both notes are diatonic and the interval is a {consonance_word}, the label is {label}.")
        return self._problem(
            "interval_classification",
            prompt,
            label,
            "label",
            cot,
            tonic_note=tonic.name(False),
            scale_mode=scale_mode,
            start_note=first.name(False),
            end_note=second.name(False),
        )

    def _generate_enharmonic_interval_comparison(self) -> Problem:
        """Generate a task comparing whether two written intervals are enharmonically equivalent."""
        style = self.config.random_style()
        accidental_limit = self.config.max_accidental
        max_interval_number = self.config.max_interval_number
        yes = random.choice([True, False])
        start1, end1, quality1, number1 = self._sample_constructed_pair(
            max_number=max_interval_number,
            max_accidental=accidental_limit,
        )
        first_interval = Interval(quality1, number1, start1, end1)
        if yes:
            candidates = []
            start_spellings = start1.exact_pitch_spellings(accidental_limit)
            end_spellings = end1.exact_pitch_spellings(accidental_limit)
            for start2 in start_spellings:
                for end2 in end_spellings:
                    if (
                        start1.same_spelling(start2, include_octave=True)
                        and end1.same_spelling(end2, include_octave=True)
                    ):
                        continue
                    try:
                        candidate_interval = Interval.between(start2, end2)
                    except ValueError:
                        continue
                    if candidate_interval.number <= max_interval_number + 1:
                        candidates.append(candidate_interval)
            if not candidates:
                raise ValueError("Could not construct an enharmonically equivalent interval pair.")
            second_interval = random.choice(candidates)
        else:
            for _ in range(GENERATION_RETRY_LIMIT):
                start2, end2, quality2, number2 = self._sample_constructed_pair(
                    max_number=max_interval_number,
                    max_accidental=accidental_limit,
                )
                second_interval = Interval(quality2, number2, start2, end2)
                if not first_interval.same_endpoint_pitches(second_interval):
                    break
            else:
                raise ValueError("Could not construct a distinct interval pair.")
        start2 = second_interval.start
        end2 = second_interval.end
        resolution_cot = []
        if style == FULL_ABC_SCORE_STYLE:
            rendered_first, first_rendered_notes, first_context = ABCContext.interval_score_with_resolution(start1, end1)
            rendered_second, second_rendered_notes, second_context = ABCContext.interval_score_with_resolution(start2, end2)
            resolution_cot = [
                *[first_context.resolution_sentence(note) for note in first_rendered_notes],
                *[second_context.resolution_sentence(note) for note in second_rendered_notes],
            ]
            prompt = PromptFormatter.choice_prompt(
                ENHARMONIC_INTERVAL_SCORE_OPENERS,
                ABC_PAIR_YES_NO_TAILS,
                tail_separator="\n",
                first=rendered_first,
                second=rendered_second,
            )
        else:
            rendered_first = NoteRenderer.pair(start1, end1, style)
            rendered_second = NoteRenderer.pair(start2, end2, style)
            prompt = PromptFormatter.choice_prompt(
                ENHARMONIC_INTERVAL_OPENERS,
                YES_NO_TAILS,
                style=style,
                first=rendered_first,
                second=rendered_second,
            )
        start_pitches_match = start1.same_pitch(start2)
        end_pitches_match = end1.same_pitch(end2)
        cot_note_style = COMPACT_ABC_STYLE if style == FULL_ABC_SCORE_STYLE else style
        force_natural_in_cot = style == FULL_ABC_SCORE_STYLE
        rendered_start1 = NoteRenderer.note(start1, cot_note_style, force_natural=force_natural_in_cot)
        rendered_start2 = NoteRenderer.note(start2, cot_note_style, force_natural=force_natural_in_cot)
        rendered_end1 = NoteRenderer.note(end1, cot_note_style, force_natural=force_natural_in_cot)
        rendered_end2 = NoteRenderer.note(end2, cot_note_style, force_natural=force_natural_in_cot)
        cot = resolution_cot + [
            f"Compare endpoint pitches: {rendered_start1} and {rendered_start2} "
            f"{'represent the same pitch' if start_pitches_match else 'do not represent the same pitch'}; "
            f"{rendered_end1} and {rendered_end2} "
            f"{'represent the same pitch' if end_pitches_match else 'do not represent the same pitch'}."
        ]
        if yes:
            cot.append("Both corresponding endpoint pitches match, so the written intervals are enharmonically equivalent and the answer is yes.")
        else:
            cot.append(
                "At least one corresponding endpoint pitch differs, so the written intervals are not enharmonically equivalent and the answer is no."
            )
        return self._problem(
            "enharmonic_interval_comparison",
            prompt,
            "yes" if yes else "no",
            "yes_no",
            cot,
            style=style,
            first_start_note=start1.name(),
            first_interval_quality=first_interval.quality,
            first_interval_number=first_interval.number,
            second_start_note=start2.name(),
            second_interval_quality=second_interval.quality,
            second_interval_number=second_interval.number,
        )

    def _generate_instrument_transposition(self) -> Problem:
        """Generate a task converting written transposing-instrument pitch to sound."""
        style = self.config.random_style()
        accidental_limit = self.config.max_accidental
        instrument, quality, number = random.choice(TRANSPOSING_INSTRUMENTS)
        written = Note.random(self.config, accidental_limit=accidental_limit)
        transposition = Interval(quality, number)
        sounding = transposition.construct_from(written, direction="down")
        interval = transposition.name()
        answer_style, answer_notation, force_answer_natural = NoteRenderer.answer_rendering(style)
        answer = NoteRenderer.note(sounding, answer_style, force_natural=force_answer_natural, quote_abc=False)
        rendered_sounding = NoteRenderer.note(sounding, answer_style, force_natural=force_answer_natural)
        answer_format = NoteRenderer.answer_format(answer_notation, explicit_accidentals=force_answer_natural)
        instrument_article_lower = TextFormatter.article(instrument)
        instrument_article = TextFormatter.capitalize_initial(instrument_article_lower)
        if style == FULL_ABC_SCORE_STYLE:
            rendered_written, rendered_written_notes, resolution_cot = NoteRenderer.sequence([written], style)
            prompt = PromptFormatter.choice_prompt(
                INSTRUMENT_TRANSPOSITION_SCORE_OPENERS,
                NOTE_ANSWER_TAILS,
                style=style,
                notation_separator="\n",
                score=rendered_written,
                instrument_article=instrument_article,
                instrument_article_lower=instrument_article_lower,
                answer_format=answer_format,
            )
            cot_written = rendered_written_notes[0]
            cot = resolution_cot
        else:
            rendered_written = NoteRenderer.note(written, style)
            prompt = PromptFormatter.choice_prompt(
                INSTRUMENT_TRANSPOSITION_OPENERS,
                NOTE_ANSWER_TAILS,
                style=style,
                instrument_article=instrument_article,
                instrument_article_lower=instrument_article_lower,
                written=rendered_written,
                answer_format=answer_format,
            )
            cot_written = rendered_written
            cot = []
        cot += [
            f"{TextFormatter.capitalize_initial(instrument)} sounds {TextFormatter.article(interval)} lower than written.",
            f"Moving {cot_written} down {TextFormatter.article(interval)} gives {rendered_sounding}.",
        ]
        return self._problem(
            "instrument_transposition",
            prompt,
            answer,
            "note",
            cot,
            instrument=instrument,
            written_note=written.name(),
            answer_notation=answer_notation,
            style=style,
        )

    def _generate_interval_construction(self) -> Problem:
        """Generate a task constructing a note above or below another by interval name."""
        style = self.config.random_style()
        accidental_limit = self.config.max_accidental
        max_interval_number = self.config.max_interval_number
        start = Note.random(self.config, accidental_limit=accidental_limit)
        interval = Interval.random(
            self.config,
            min_number=2,
            max_number=max_interval_number,
            accidental_limit=accidental_limit,
        )
        direction = random.choice(["up", "down"])
        position = "above" if direction == "up" else "below"
        end = interval.construct_from(start, direction=direction)
        prompt_answer_case = random.choice(INTERVAL_CONSTRUCTION_CASES)
        prompt_has_octave = prompt_answer_case != "prompt_no_octave_answer_no_octave"
        answer_has_octave = prompt_answer_case == "prompt_octave_answer_octave"
        reduce_to_note_name = prompt_has_octave and not answer_has_octave
        answer_style, answer_notation, force_answer_natural = NoteRenderer.answer_rendering(style)
        answer_note = end if answer_has_octave else end.without_octave()
        answer = NoteRenderer.note(
            answer_note,
            answer_style,
            with_octave=answer_has_octave,
            force_natural=force_answer_natural,
            quote_abc=False,
        )
        rendered_answer = NoteRenderer.note(
            answer_note,
            answer_style,
            with_octave=answer_has_octave,
            force_natural=force_answer_natural,
        )
        prompt_start = start if prompt_has_octave else start.without_octave()
        cot_start = NoteRenderer.note(
            prompt_start,
            answer_style,
            with_octave=prompt_has_octave,
            force_natural=style == FULL_ABC_SCORE_STYLE,
        )
        cot_end = NoteRenderer.note(
            end,
            answer_style,
            with_octave=prompt_has_octave,
            force_natural=force_answer_natural,
        )
        interval_name = interval.name()
        simple_number_name = interval.number_name
        interval_size = interval.semitones
        prompt_answer_format = NoteRenderer.answer_format(
            answer_notation,
            with_octave=answer_has_octave,
            explicit_accidentals=force_answer_natural,
        )
        followup = "Then reduce the result to a note name without octave. " if reduce_to_note_name else ""
        construction_tails = tuple(f"{followup}{tail}" for tail in NOTE_ANSWER_TAILS)
        resolution_cot = []
        if style == FULL_ABC_SCORE_STYLE:
            rendered_start_score, _, resolution_cot = NoteRenderer.sequence(
                [prompt_start],
                style,
                with_octave=prompt_has_octave,
            )
            prompt = PromptFormatter.choice_prompt(
                INTERVAL_CONSTRUCTION_SCORE_OPENERS,
                construction_tails,
                style=style,
                notation_separator="\n",
                interval=TextFormatter.article(interval_name),
                position=position,
                score=rendered_start_score,
                answer_format=prompt_answer_format,
            )
        else:
            prompt = PromptFormatter.choice_prompt(
                INTERVAL_CONSTRUCTION_OPENERS,
                construction_tails,
                style=style,
                interval=TextFormatter.article(interval_name),
                position=position,
                start=NoteRenderer.note(prompt_start, style),
                answer_format=prompt_answer_format,
            )
        cot = resolution_cot + [
            f"Start from {cot_start}.",
            f"For {TextFormatter.article(simple_number_name)}, the target letter is found by moving {TextFormatter.count_phrase(interval.step_count, 'letter step')} {direction} from {start.letter}, which gives {end.letter}.",
            f"The major/perfect reference form of {TextFormatter.article(simple_number_name)} spans {TextFormatter.count_phrase(interval.base_semitones)}; {TextFormatter.article(interval_name)} must span {TextFormatter.count_phrase(interval_size)}.",
            f"With letter {end.letter}, the spelling that gives this semitone distance is {cot_end}.",
            (
                f"The no-octave form of the result is {rendered_answer}."
                if prompt_answer_case == "prompt_octave_answer_no_octave"
                else f"So the answer is {rendered_answer}."
            ),
        ]
        return self._problem(
            "interval_construction",
            prompt,
            answer,
            "note",
            cot,
            start_note=start.name(),
            interval_quality=interval.quality,
            interval_number=interval.number,
            direction=direction,
            answer_notation=answer_notation,
            prompt_has_octave=prompt_has_octave,
            answer_has_octave=answer_has_octave,
            style=style,
        )

    def _generate_transposition_chain(self) -> Problem:
        """Generate a task applying several interval transpositions in sequence."""
        style = self.config.random_style()
        answer_style, answer_notation, force_answer_natural = NoteRenderer.answer_rendering(style)
        max_interval_number = self.config.max_interval_number
        max_accidental = self.config.max_accidental
        steps = []
        current = Note.random(
            self.config,
            with_octave=True,
            octave_min=4,
            octave_max=4,
            accidental_limit=max_accidental,
        )
        start = current
        chain_len = self.config.chain_len
        for _ in range(chain_len):
            direction, interval, nxt = self._sample_transposition_step(
                current,
                max_interval_number,
                max_accidental,
            )
            steps.append((direction, interval, current.without_octave(), nxt.without_octave()))
            current = nxt
        step_text = ", ".join(f"{direction} {TextFormatter.article(interval.name())}" for direction, interval, _, _ in steps)
        answer = NoteRenderer.note(
            current.without_octave(),
            answer_style,
            with_octave=False,
            force_natural=force_answer_natural,
            quote_abc=False,
        )
        answer_format = NoteRenderer.answer_format(
            answer_notation,
            with_octave=False,
            explicit_accidentals=force_answer_natural,
        )
        resolution_cot = []
        if style == FULL_ABC_SCORE_STYLE:
            rendered_start_score, _, resolution_cot = NoteRenderer.sequence(
                [start.without_octave()],
                style,
                with_octave=False,
            )
            prompt = PromptFormatter.choice_prompt(
                TRANSPOSITION_CHAIN_SCORE_OPENERS,
                NOTE_ANSWER_TAILS,
                style=style,
                notation_separator="\n",
                score=rendered_start_score,
                steps=step_text,
                answer_format=answer_format,
            )
        else:
            prompt = PromptFormatter.choice_prompt(
                TRANSPOSITION_CHAIN_OPENERS,
                NOTE_ANSWER_TAILS,
                style=style,
                start=NoteRenderer.note(start.without_octave(), style, with_octave=False),
                steps=step_text,
                answer_format=answer_format,
            )
            prompt = " ".join(prompt.split())
        cot = resolution_cot + [
            f"{NoteRenderer.note(before, answer_style, with_octave=False, force_natural=force_answer_natural)} "
            f"{direction} {TextFormatter.article(interval.name())} -> "
            f"{NoteRenderer.note(after, answer_style, with_octave=False, force_natural=force_answer_natural)}"
            for direction, interval, before, after in steps
        ]
        return self._problem(
            "transposition_chain",
            prompt,
            answer,
            "note",
            cot,
            start_note=start.name(False),
            steps=[
                {
                    "direction": direction,
                    "interval_quality": interval.quality,
                    "interval_number": interval.number,
                }
                for direction, interval, _, _ in steps
            ],
            answer_notation=answer_notation,
            style=style,
        )

    def _sample_transposition_step(
        self,
        current: Note,
        max_number: int,
        max_accidental: int,
    ) -> tuple[str, Interval, Note]:
        """Sample one transposition step that keeps the next spelling supported."""
        for _ in range(GENERATION_RETRY_LIMIT):
            interval = Interval.random(
                self.config,
                min_number=2,
                max_number=max_number,
                accidental_limit=max_accidental,
            )
            if interval.quality not in Interval.quality_options(interval.number, max_accidental):
                continue
            direction = random.choice(["up", "down"])
            try:
                nxt = interval.construct_from(current, direction=direction)
            except ValueError:
                continue
            if abs(nxt.accidental) <= max_accidental:
                return direction, interval, nxt
        raise ValueError("Could not sample a valid transposition-chain step.")

    def _sample_interval_arithmetic_chain(self) -> tuple[Interval, list[tuple[str, Interval | None, Interval]]]:
        """Sample a valid interval-arithmetic chain within the current difficulty."""
        operation_count = self.config.chain_len
        max_number = self.config.max_interval_number
        max_accidental = self.config.max_accidental
        if max_number < 2:
            raise ValueError("Interval-arithmetic difficulty bounds are too small.")
        for _ in range(GENERATION_RETRY_LIMIT):
            start_interval = Interval.random(
                self.config,
                min_number=2,
                max_number=max_number,
                accidental_limit=max_accidental,
            )
            if start_interval.quality not in Interval.quality_options(start_interval.number, max_accidental):
                continue
            current = start_interval
            steps = []
            try:
                for _ in range(operation_count):
                    operation, operand, current = self._sample_interval_arithmetic_step(
                        current,
                        max_number,
                        max_accidental,
                    )
                    steps.append((operation, operand, current))
            except ValueError:
                continue
            return start_interval, steps
        raise ValueError("Could not construct a suitable interval-arithmetic chain.")

    def _sample_interval_arithmetic_step(
        self,
        current: Interval,
        max_result_number: int,
        max_accidental: int,
    ) -> tuple[str, Interval | None, Interval]:
        """Sample one valid interval-arithmetic step."""
        for _ in range(GENERATION_RETRY_LIMIT):
            operation = random.choice(["add", "subtract", "reduce_then_invert"])
            try:
                return self._sample_interval_operand(current, operation, max_result_number, max_accidental)
            except ValueError:
                continue

        operations = ["add", "subtract", "reduce_then_invert"]
        random.shuffle(operations)
        for operation in operations:
            try:
                return self._sample_interval_operand(current, operation, max_result_number, max_accidental)
            except ValueError:
                continue
        raise ValueError("Could not sample a valid interval-arithmetic step.")

    def _sample_interval_operand(
        self,
        current: Interval,
        operation: str,
        max_result_number: int,
        max_accidental: int,
    ) -> tuple[str, Interval | None, Interval]:
        """Sample the operand, if any, and result for one arithmetic operation."""
        if operation == "reduce_then_invert":
            if current.number <= 8:
                raise ValueError("Only compound intervals can be reduced before inversion.")
            result = current.reduced().inverted()
            if (
                result.number <= max_result_number
                and result.quality in Interval.quality_options(result.number, max_accidental)
            ):
                return operation, None, result
            raise ValueError("Reduce-then-invert produced an unsupported interval.")

        if operation == "add":
            max_operand_number = max_result_number - current.number + 1
        elif operation == "subtract":
            max_operand_number = current.number
        else:
            raise ValueError(f"Unsupported interval-arithmetic operation: {operation}")

        if max_operand_number < 2:
            raise ValueError("No room left for the requested interval operation.")
        for _ in range(GENERATION_RETRY_LIMIT):
            operand = Interval.random(
                self.config,
                min_number=2,
                max_number=max_operand_number,
                accidental_limit=max_accidental,
            )
            if operand.quality not in Interval.quality_options(operand.number, max_accidental):
                continue
            try:
                result = current.add(operand) if operation == "add" else current.subtract(operand)
            except ValueError:
                continue
            if (
                result.number <= max_result_number
                and result.quality in Interval.quality_options(result.number, max_accidental)
            ):
                return operation, operand, result
        raise ValueError("Could not sample a valid interval operand.")

    def _sample_constructed_pair(
        self,
        with_octave: bool = True,
        min_number: int = 1,
        max_number: int | None = None,
        max_accidental: int | None = None,
        quality: str | None = None,
        number: int | None = None,
    ) -> tuple[Note, Note, str, int]:
        """Sample a start note, interval, and constructible end note."""
        max_number = max_number or self.config.max_interval_number
        max_accidental = self.config.max_accidental if max_accidental is None else max_accidental
        for _ in range(GENERATION_RETRY_LIMIT):
            start = Note.random(self.config, with_octave=True, accidental_limit=max_accidental)
            interval = (
                Interval(quality, number)
                if quality and number
                else Interval.random(
                    self.config,
                    min_number=min_number,
                    max_number=max_number,
                    accidental_limit=max_accidental,
                )
            )
            end = interval.construct_from(start, direction="up")
            if abs(end.accidental) <= max_accidental:
                if not with_octave:
                    return start.without_octave(), end.without_octave(), interval.quality, interval.number
                return start, end, interval.quality, interval.number
        raise ValueError("Could not construct a suitable interval pair.")

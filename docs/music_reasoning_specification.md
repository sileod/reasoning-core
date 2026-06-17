# Music Reasoning Tasks for Reasoning Core

This document is a working specification. Implemented behavior is authoritative where this draft and the code disagree.

This document proposes music reasoning task families for Reasoning Core. It is intentionally written in the style of the existing task implementations in `reasoning_core/tasks/` and the rules in `TASK_AUTHORING_GUIDE.md`.

In Reasoning Core, `Config.set_level(i)` resets the config and applies `update(c)` `i` times. Existing tasks such as equation systems, graph reasoning, constraint satisfaction, grammar tasks, arithmetic, and sequential induction mostly follow that pattern. They do not define a fixed curriculum where level 0 is task A and level 5 is task F.

The music tasks below therefore use **modes** for task variants and **knobs** for difficulty. A mode may be sampled randomly or fixed by config.

---

## Metadata Pattern

Implemented music families store task-owned metadata in this pattern:

- `mode`: the resolved concrete operation, such as `interval_naming`, `pitch_count`, `chord_quality`, or `roman_numeral_from_chord`;
- `prompt`: the exact generated prompt text returned by `Task.prompt()`;
- `answer_kind`: the answer-normalization family used by `score_answer`, such as `note`, `interval`, `integer`, `yes_no`, `roman`, `note_sequence`, or `label`;
- `cot`: programmatic reasoning trace generated from the same symbolic operations used to compute the answer;
- task-specific hidden state, such as source notes, interval qualities/numbers, chord notes, key labels, Roman figures, notation style, and answer notation.

Reasoning Core already adds framework metadata such as `_task`, `_level`, and `_config` in `Task.generate_example()`, so task metadata does not duplicate the task family name. The canonical answer is stored in `Problem.answer`; task-specific metadata stores enough hidden state to reconstruct or audit that answer where useful.

Difficulty should be represented in `_config`, not only in prose. For example:

```python
def update(self, c=1):
    self.context_len += c
    self.max_accidental += 0.25 * c
    self.n_candidates += c
```

This means level 0 and level 5 are the same task, but level 5 has larger or less forgiving instances.

---

## Difficulty Semantics

In implementation, there should be no hand-authored table like "level 0 does interval naming, level 1 does inversion, level 2 does enharmonic spelling." That pattern changes the task with level.

Use this interpretation instead:

- level 0 is the base config;
- level `k` is the result of applying `update(c)` `k` times;
- `update(c)` changes numeric knobs monotonically;
- modes are sampled from config or fixed by config, not unlocked by level;
- larger levels may enlarge the structural domain, such as more voices, more constraints, a larger grammar, or more candidate keys, while preserving the same answer schema.

Each task config should expose a `mode: str = "any"` field. If `mode == "any"`, `generate()` samples one concrete mode from the family; otherwise it uses the requested fixed mode. The resolved concrete mode should always be stored in `metadata["mode"]`.

**Config sketch type convention:** each config sketch should be a dataclass subclass of `Config`; otherwise subclass fields are not visible to `Config.__post_init__()` and stochastic rounding will not apply. Count-like knobs should stay annotated as `int` even when `update(c)` adds fractional increments such as `0.5 * c` or `1.5 * c`. This follows Reasoning Core's `Config` behavior: `int` fields are tracked internally as unrounded floats during updates, so the fractional part is not lost, and then stochastically rounded to integers on read. For example, `score_len: int = 1` followed by `self.score_len += 0.5 * c` has an internal value of `1.5` after one level update. Use `float` only for genuinely continuous knobs such as probabilities, weights, thresholds, or soft sampling parameters. The sketches assume `from dataclasses import dataclass`.

Level 5 should be difficult because the generated instance is larger, noisier, more constrained, or less forgiving.

---

## Low-Entropy Music Domains

Music has many small finite domains: 12 pitch classes, 24 common major/minor key signatures, a small set of diatonic triads, and a limited set of common cadences. Do not rely only on transposition for variety.

Use variety from combinations of dimensions:

- spelling: sharp, flat, double-sharp, double-flat, naturalized notes;
- register: simple vs compound intervals, octave displacement, close/open voicing;
- representation: note names, scale degrees, solfege, ABC notation, chord symbols, Roman numerals, tables, JSON;
- query form: classify, construct, validate, repair, compare, count, complete, infer;
- context size: one note, interval, chord, progression, phrase, multi-voice excerpt;
- convention: strict written spelling vs pitch-class equivalence, global vs local key, functional labels vs Roman numerals;
- controlled corruption: wrong accidental, wrong inversion, wrong local key, wrong resolution, wrong clef, wrong duration, wrong field.

---

## MusicTheoryBench (MTB) Coverage

MTB contains 98 reasoning rows. The task families below are designed to cover them.

Approximate multi-label coverage of the 98 MTB reasoning rows:

| Task family | MTB reasoning coverage signal |
|---|---|
| `pitch_interval_reasoning` | 40 |
| `chord_roman_reasoning` | 25 |
| `key_scale_mode_reasoning` | 48 |
| `rhythm_meter_reasoning` | 2 |
| `harmony_progression_reasoning` | 7 |
| `voice_leading_reasoning` | 4 |
| `formal_music_transformations` | 5 |
| `analysis_representation_reasoning` | 15 |

Rows can belong to several families. For example, an ABC score can be a representation of an interval, chord, mode, or voice-leading question.

---

# Task Families in Implementation Order

These families are ordered for implementation: start with compact, strongly verifiable domains, then move toward convention-heavy and schema-heavy generators. Each family lists modes in a single table.

## 1. `pitch_interval_reasoning`

**Stable task principle:** Given pitch, interval, key, or short notated material plus a requested query field, compute the canonical pitch/interval answer.

**Modes**

| Mode | Prompt example | Answer |
|---|---|---|
| `interval_naming` | `Name the interval from F#3 to A4. Notes are written in scientific pitch notation. The answer is one interval name, including compound/simple size as written.` | `minor tenth` |
| `interval_arithmetic` | `Start with a major tenth, then reduce to a simple interval and invert it, then add a minor third. The answer is one interval name.` | `major seventh` |
| `pitch_count` | `Under pitch-class equivalence, how many distinct pitch classes are in C4, C5, B#3, Db4, C#5, Ebb4? Notes are written in scientific pitch notation. The answer is one integer.` | `3` |
| `interval_classification` | `In C harmonic minor, classify the ascending note-to-note relation Eb-B using one of these labels: diatonic consonance, diatonic dissonance, chromatic alteration. The answer is one label from that list.` | `diatonic dissonance` |
| `enharmonic_interval_comparison` | `Are C#4-E4 and Db4-Fb4 enharmonically equivalent intervals? Notes are written in scientific pitch notation. The answer is exactly 'yes' or 'no'.` | `yes` |
| `instrument_transposition` | `A B-flat clarinet part writes D5. What sounding pitch is produced? Notes are written in scientific pitch notation. The answer is one note name in scientific pitch notation.` | `C5` |
| `interval_construction` | `Build a minor third below E. Notes are written in scientific pitch notation. The answer is one note name without octave in scientific pitch notation.` | `C#` |
| `transposition_chain` | `Transpose F# up a minor third, down a perfect fifth, then up a major second. Notes are written in scientific pitch notation. The answer is one note name without octave in scientific pitch notation.` | `E` |

**Difficulty knobs**

| Knob | Description | Modes affected | Level 0 tendency | Monotonic update effect |
|---|---|---|---|---|
| `chain_len` | Shared length knob for chain-like pitch/interval tasks. | `interval_arithmetic`, `transposition_chain` | one operation | longer composed operation chains such as add/subtract, reduce-then-invert, and transpose |
| `max_accidental` | Accidental/quality complexity used when sampling notes and interval qualities; constructed results may still require the spelling implied by the operation. | all | sampled notes use naturals, sharps, flats; simple interval qualities | sample double accidentals, double-augmented/double-diminished intervals, and stricter spelling traps |
| `key_complexity` | Maximum number of sharps/flats in analytical key signatures. | `interval_classification` | common keys up to two sharps/flats | expands to all conventional major/minor keys |
| `max_interval_number` | Largest diatonic interval number allowed in generated intervals. | `interval_naming`, `interval_arithmetic`, `enharmonic_interval_comparison`, `interval_construction`, `transposition_chain` | simple intervals | compound intervals and wider registers |
| `n_candidates` | Number of note items in count-style instances. | `pitch_count` | short note list | longer note lists with more duplicates and distractors |
| `p_abc` | Probability of rendering prompt notes in ABC notation instead of scientific pitch notation; note-answer modes use the matching answer notation policy. 70% of ABC cases use compact ABC note tokens and 30% use full ABC score fragments with randomly sampled common `L:`, `M:`, and `K:` headers. Full ABC interval pairs are rendered as bracketed harmonic intervals, and full-ABC note-answer modes ask for compact ABC answers with explicit accidentals. | `interval_naming`, `pitch_count`, `enharmonic_interval_comparison`, `instrument_transposition`, `interval_construction`, `transposition_chain` | SPN note names | more compact and full-score ABC input notation, plus compact ABC answers where applicable |

**Config sketch**

```python
@dataclass
class PitchIntervalConfig(Config):
    mode: str = "any"
    chain_len: int = 1
    max_interval_number: int = 8
    n_candidates: int = 4
    max_accidental: int = 1
    key_complexity: int = 2
    p_abc: float = 0.20
    max_tries: int = 256

    def update(self, c=1):
        self.chain_len += 0.6 * c
        self.max_interval_number = min(20, self.max_interval_number + 1.5 * c)
        self.n_candidates += c
        self.max_accidental = min(2, self.max_accidental + 0.2 * c)
        self.key_complexity = min(7, self.key_complexity + 1 * c)
        self.p_abc = min(0.50, self.p_abc + 0.06 * c)
```

**Tools:** project-owned pitch/interval spelling solver as source of truth; custom rule tables for transposing instruments.

---

## 2. `chord_roman_reasoning`

**Stable task principle:** Given a chord object and optional key/context, compute the requested canonical chord/Roman-numeral field.

**Modes**

| Mode | Prompt example | Answer |
|---|---|---|
| `chord_quality` | `Identify the quality of Bb-C#-E-G. Use one of these labels: major triad, minor triad, diminished triad, augmented triad, major seventh, dominant seventh, minor seventh, half-diminished seventh, fully diminished seventh, minor-major seventh, augmented-major seventh. The answer is one label from that list.` | `fully diminished seventh` |
| `inversion` | `Treat the chord in this ABC score fragment:\nL:1/16\nM:4/4\nK:Eb\n  [^A=BD^F] |] %1 as the chord tones and "^F" as the bass note. Interpret the ABC score using its key signature. The answer is one inversion label followed by figured bass.` | `second inversion 4/3` |
| `open_close_voicing` | `Classify the voicing "C"-"G"-"e". Notes are written in compact ABC notation. Choose from: close voicing, open voicing. The answer is one label from that list.` | `open voicing` |
| `enharmonic_chord_equivalence` | `Compare "C"-"^E"-"G"-"B" and "^B"-"F"-"__A"-"_C": are they enharmonically equivalent pitch-class chords? Notes are written in compact ABC notation. Answer exactly 'yes' or 'no'.` | `yes` |
| `chromatic_chord_label` | `In C major, what chromatic label fits C-Ab-F# over Ab? Select exactly one label from this list: French augmented sixth, Italian augmented sixth, German augmented sixth, Swiss augmented sixth, Neapolitan sixth.` | `Italian augmented sixth` |
| `chord_membership` | `Do all tones of Cb-F-Ab belong to Eb natural minor? Give one answer, either 'yes' or 'no'.` | `yes` |
| `roman_numeral_from_chord` | `In D minor, analyze the chord in this ABC score fragment:\nL:1/8\nM:6/8\nK:Fm\n  [=A=D=B^F] |] %1 with "^F" in the bass. Interpret the ABC score using its key signature. Answer with one compact Roman numeral and closed-up figured bass.` | `vi43` |
| `chord_from_roman_numeral` | `Which chord tones does vi43 produce in D minor? The expected answer is a bass-upward note sequence in compact ABC notation, with any accidental made explicit, separated by hyphens.` | `^F-=A-=B-=D` |

Prompt wording is intentionally varied in every mode. Chord-tone prompts may be written in scientific pitch notation, compact ABC notation, or full ABC score fragments. Full ABC score prompts use bracketed chord events and include a key-signature interpretation instruction; their CoTs resolve any implicit ABC accidentals before applying the chord/Roman rule. Modes with unordered chord-tone collections usually omit octaves, while voicing tasks always include octaves and several comparison/context modes sample both octave-bearing and octave-free forms. `chord_from_roman_numeral` has no input chord to render; instead, its requested answer notation follows the sampled style, with full-ABC style asking for compact ABC answer tokens with explicit accidentals. Roman-numeral modes include diatonic triads/seventh chords plus secondary dominant and secondary leading-tone functions to common non-tonic scale-degree targets. Where chord-tone order and answer-choice order are not musically significant, the generator also samples those orders to increase prompt diversity while keeping the same canonical answer semantics.

**Difficulty knobs**

| Knob | Description | Modes affected | Level 0 tendency | Monotonic update effect |
|---|---|---|---|---|
| `p_seventh` | Probability of sampling a seventh chord instead of a triad in modes that can use either size. | `chord_quality`, `inversion`, `open_close_voicing`, `enharmonic_chord_equivalence`, `chord_membership`, `roman_numeral_from_chord`, `chord_from_roman_numeral` | 30% seventh chords, 70% triads | +0.06 per level, capped at 60% seventh chords |
| `max_accidental` | Accidental complexity in generated chord tones, roots, chromatic labels, membership distractors, enharmonic respellings, and Roman-derived spellings. | all modes | simple spelling | chromatic and enharmonic spellings |
| `key_complexity` | Maximum number of sharps/flats in analytical key signatures. | `chord_membership`, `chromatic_chord_label`, `roman_numeral_from_chord`, `chord_from_roman_numeral` | common keys up to two sharps/flats | expands to all conventional major/minor keys |
| `p_secondary` | Probability of sampling secondary-dominant or secondary-leading-tone Roman material where the mode allows it. | `roman_numeral_from_chord`, `chord_from_roman_numeral` | mostly diatonic Roman numerals | more secondary/applied Roman numerals |
| `p_abc` | Probability of rendering chord-tone prompts in ABC notation where a mode has input chord tones, or note-sequence answers in compact ABC notation for `chord_from_roman_numeral`. ABC prompt cases split into 70% compact ABC note tokens and 30% full ABC score fragments with sampled common `L:`, `M:`, and `K:` headers. | all modes | mostly scientific pitch notation | more compact ABC and full ABC score prompts or compact ABC answer sequences |

**Config sketch**

```python
@dataclass
class ChordRomanConfig(Config):
    mode: str = "any"
    p_seventh: float = 0.30
    max_accidental: int = 1
    key_complexity: int = 2
    p_secondary: float = 0.10
    p_abc: float = 0.20
    max_tries: int = 256

    def update(self, c=1):
        self.p_seventh = min(0.60, self.p_seventh + 0.06 * c)
        self.max_accidental = min(2, self.max_accidental + 0.2 * c)
        self.key_complexity = min(7, self.key_complexity + 1 * c)
        self.p_secondary = min(0.70, self.p_secondary + 0.08 * c)
        self.p_abc = min(0.50, self.p_abc + 0.06 * c)
```

**Tools:** `music21.chord`, `music21.roman`, `music21.key`; custom convention layer for accepted Roman-numeral spelling and chromatic-function labels.

---

## 3. `key_scale_mode_reasoning`

**Stable task principle:** Given a key, scale, mode, or generated modal rule system plus a requested query field, compute canonical membership, key signature, scale degree, tonic, mode label, or note collection.

**Modes**

| Mode | Prompt example | Answer |
|---|---|---|
| `key_membership` | `Is E# in F# harmonic minor? The answer is exactly 'yes' or 'no'.` | `yes` |
| `stable_degree_set` | `In F# minor, list the stable scale degrees 1, 3, and 5 as note names. The answer is comma-separated note names ascending.` | `F#, A, C#` |
| `minor_scale_membership` | `Is D# in ascending E melodic minor? The answer is exactly 'yes' or 'no'.` | `yes` |
| `chromatic_scale_spelling` | `In a descending chromatic scale from D to C, what note lies between D and C? The answer is one note name.` | `Db` |
| `pentatonic_mode_collection` | `A Gong pentatonic mode on F# uses degrees 1, 2, 3, 5, 6. List its notes. The answer is comma-separated note names.` | `F#, G#, A#, C#, D#` |
| `custom_mode_degree` | `A supplied Ya-yue rule says Qing-jue is two semitones above Jue. If Jue is E, what is Qing-jue? The answer is one note name.` | `F#` |
| `messiaen_common_tones` | `Mode V Form 3 of Messiaen's finite transposition system has pitch classes {C, D, E, F#, G#, A#}; D Phrygian has {D, Eb, F, G, A, Bb, C}. How many pitch classes are common? The answer is one integer.` | `3` |
| `pythagorean_interval_term` | `In the supplied Pythagorean tuning table, limma is the diatonic semitone and apotome is the chromatic semitone. Which term names the chromatic semitone? The answer is one term.` | `apotome` |
| `generated_modal_system` | `Mode M on F starts with semitone steps 2, 1, 3, 2. List the first five notes including the tonic. The answer is comma-separated note names.` | `F, G, Ab, B, C#` |
| `scale_degree_constraints` | `Find the major key where E is scale degree 3, F is scale degree 4, and B is scale degree 7. The answer is one tonic note name.` | `C` |

**Difficulty knobs**

| Knob | Description | Modes affected | Level 0 tendency | Monotonic update effect |
|---|---|---|---|---|
| `n_constraints` | Number of clues or constraints about notes, degrees, membership, or exclusions. | `key_membership`, `minor_scale_membership`, `scale_degree_constraints` | one note or degree | multiple note, degree, and exclusion constraints |
| `n_candidates` | Number of keys, scales, modes, or collections to compare or enumerate. | `key_membership`, `minor_scale_membership`, `messiaen_common_tones`, `scale_degree_constraints` | direct answer | possible-key lists, reject-one-option, count answers |
| `system_pool_size` | Number of scale or mode systems available to the sampler. | `custom_mode_degree`, `messiaen_common_tones`, `pythagorean_interval_term`, `generated_modal_system` | common major/minor | more generated mode systems from a fixed pool |
| `max_accidental` | Spelling complexity allowed in tonics and scale members. | all except `pythagorean_interval_term` | simple spelling | double accidentals and strict names |
| `collection_size` | Number of notes or degrees in the queried/generated collection. | `stable_degree_set`, `pentatonic_mode_collection`, `messiaen_common_tones`, `generated_modal_system` | small note set | larger modal or scale collections |
| `p_custom_system` | Probability of using a nonstandard or generated modal/tuning rule table. | `custom_mode_degree`, `messiaen_common_tones`, `pythagorean_interval_term`, `generated_modal_system` | rare | more custom modal/tuning rule tables |

**Config sketch**

```python
@dataclass
class KeyScaleModeConfig(Config):
    mode: str = "any"
    n_constraints: int = 1
    n_candidates: int = 1
    collection_size: int = 3
    system_pool_size: int = 2
    max_accidental: int = 1
    p_custom_system: float = 0.15

    def update(self, c=1):
        self.n_constraints += 0.7 * c
        self.n_candidates += 0.8 * c
        self.collection_size += 0.8 * c
        self.system_pool_size += 0.5 * c
        self.max_accidental += 0.2 * c
        self.p_custom_system = min(0.75, self.p_custom_system + 0.07 * c)
```

**Tools:** `music21.key`, `music21.scale`, `music21.pitch`; generated rule tables for non-Western or artificial systems; `numpy`/`sympy` for pitch-class sets; optional `z3-solver` for unique-solution constraints.

---

## 4. `rhythm_meter_reasoning`

**Stable task principle:** Given meter and rhythmic events, compute or validate a canonical rhythmic property.

**Modes**

| Mode | Prompt example | Answer |
|---|---|---|
| `meter_classification` | `Classify 9/8 as simple or compound and duple, triple, or quadruple. The answer is two words.` | `compound triple` |
| `compound_time_signature` | `Which common compound quadruple time signature has twelve eighth-note subdivisions? The answer is one time signature.` | `12/8` |
| `duration_sum` | `Dotted eighth note plus sixteenth note plus quarter note equals what duration? The answer is one duration name.` | `half note` |
| `measure_completion` | `In 6/8, dotted quarter + blank completes the measure. What is blank? The answer is one duration name.` | `dotted quarter note` |
| `tuplet_reasoning` | `Three equal notes fill the time of one quarter note. What is each note called? The answer is one duration name.` | `triplet eighth note` |
| `rhythmic_validity` | `Does dotted quarter + eighth + quarter exactly fill one 3/4 measure? The answer is exactly 'yes' or 'no'.` | `yes` |

**Difficulty knobs**

| Knob | Description | Modes affected | Level 0 tendency | Monotonic update effect |
|---|---|---|---|---|
| `n_events` | Number of rhythmic events or durations in the instance. | `duration_sum`, `measure_completion`, `rhythmic_validity` | few durations | longer rhythmic strings |
| `n_measures` | Number of measures or metrical spans to validate or complete. | `measure_completion`, `rhythmic_validity` | one measure | multi-measure validation |
| `n_missing` | Number of blanks, corruptions, or unknown durations to solve. | `measure_completion` | zero or one | multiple blanks or repairs |
| `max_group_parts` | Maximum number of subdivisions or grouped parts in a beat/measure. | `meter_classification`, `compound_time_signature`, `tuplet_reasoning` | simple grouping | irregular grouping |
| `p_tuplet` | Probability of using tuplet durations. | `duration_sum`, `measure_completion`, `tuplet_reasoning`, `rhythmic_validity` | low | more tuplets |
| `p_tie_or_dot` | Probability of using tied or dotted durations. | `duration_sum`, `measure_completion`, `rhythmic_validity` | low | more dots and ties |

**Config sketch**

```python
@dataclass
class RhythmMeterConfig(Config):
    mode: str = "any"
    n_events: int = 3
    n_measures: int = 1
    n_missing: int = 1
    max_group_parts: int = 2
    p_tuplet: float = 0.05
    p_tie_or_dot: float = 0.10

    def update(self, c=1):
        self.n_events += c
        self.n_measures += 0.3 * c
        self.n_missing += 0.2 * c
        self.max_group_parts += 0.3 * c
        self.p_tuplet = min(0.50, self.p_tuplet + 0.05 * c)
        self.p_tie_or_dot = min(0.65, self.p_tie_or_dot + 0.06 * c)
```

**Tools:** exact `fractions.Fraction` arithmetic as source of truth; `music21.duration` and `music21.meter` for notation semantics; optional `z3-solver` for constrained missing-duration generation.

---

## 5. `harmony_progression_reasoning`

**Stable task principle:** Given a structured harmonic progression and a requested query field, compute the canonical harmonic relation, function sequence, cadence, local key, modulation decision, or continuation set.

**Modes**

| Mode | Prompt example | Answer |
|---|---|---|
| `modulation_type` | `Under the rule "modulation needs a cadence in the new key", C: I-V/V-V-I is what? The answer is one label: 'tonicization only', 'modulation', or 'neither'.` | `tonicization only` |
| `key_distance` | `From C major to E major, classify the relationship using one of these labels: closely related, distant. The answer is one label from that list.` | `distant` |
| `enharmonic_modulation` | `A German augmented sixth in C is respelled as V7 of Db. What modulation type is this? The answer is one modulation label, e.g. 'pivot-chord modulation'.` | `enharmonic modulation` |
| `pivot_chord_function` | `The chord D-F#-A is V/V in C major and what Roman numeral in G major? The answer is one Roman numeral.` | `V` |
| `modal_modulation` | `A passage changes from C Ionian to C Dorian while keeping tonic C. The answer is one modulation label.` | `modal modulation` |
| `harmonic_function` | `In C major, what function does D-F-A-C with F in the bass have? Choose from: tonic, predominant, dominant. The answer is one label from that list.` | `predominant` |
| `cadence_identification` | `At a phrase ending in C major, V-vi forms what cadence type? Choose from: authentic cadence, half cadence, plagal cadence, deceptive cadence. The answer is one label from that list.` | `deceptive cadence` |
| `local_key_tonicization` | `In C major, V/V targets which local tonic? The answer is one note name.` | `G` |
| `syntax_validity` | `In a simple T-PD-D-T grammar, can a predominant normally follow a dominant without tonic resolution? The answer is exactly 'yes' or 'no'.` | `no` |
| `functional_parse` | `Parse C: I-vi-ii6-V7-I as functions using T, PD, and D. The answer is space-separated function labels.` | `T T PD D T` |
| `harmonic_continuation` | `After C: Ger+6, which function normally follows: tonic, predominant, or dominant? The answer is one function label.` | `dominant` |

**Difficulty knobs**

| Knob | Description | Modes affected | Level 0 tendency | Monotonic update effect |
|---|---|---|---|---|
| `progression_len` | Number of chord or Roman-numeral events in the progression. | all except `key_distance` | 2-3 chords | longer phrases |
| `n_local_regions` | Number of distinct local key regions or tonic contexts. | `modulation_type`, `enharmonic_modulation`, `pivot_chord_function`, `modal_modulation`, `local_key_tonicization` | one key | tonicizations and modulations |
| `grammar_depth` | Depth of functional or harmonic grammar expansion. | `harmonic_function`, `cadence_identification`, `syntax_validity`, `functional_parse`, `harmonic_continuation` | simple T-D-T | expansions, ambiguity, applied functions |
| `n_candidates` | Number of functions, parses, labels, or continuations to compare. | all | direct label | all-valid continuations or parses |
| `p_ambiguity` | Probability of convention-dependent or multiply plausible cases. | all | low | more convention-dependent cases |
| `p_chromatic` | Probability of chromatic harmony, mixture, pivots, or enharmonic material. | `modulation_type`, `enharmonic_modulation`, `pivot_chord_function`, `local_key_tonicization`, `harmonic_continuation` | low | more mixture, pivots, enharmonic cases |

**Config sketch**

```python
@dataclass
class HarmonyProgressionConfig(Config):
    mode: str = "any"
    progression_len: int = 3
    n_local_regions: int = 1
    grammar_depth: int = 2
    n_candidates: int = 1
    p_ambiguity: float = 0.05
    p_chromatic: float = 0.10

    def update(self, c=1):
        self.progression_len += c
        self.n_local_regions += 0.3 * c
        self.grammar_depth += 0.6 * c
        self.n_candidates += 0.7 * c
        self.p_ambiguity = min(0.60, self.p_ambiguity + 0.06 * c)
        self.p_chromatic = min(0.70, self.p_chromatic + 0.08 * c)
```

**Tools:** `music21.roman` and `music21.key` for canonicalization; custom function/cadence/modulation rule tables as source of truth; optional `networkx` for key-relation graphs; optional grammar tools for parse generation.

---

## 6. `voice_leading_reasoning`

**Stable task principle:** Given one or more voice-leading transitions, validate them or return the canonical set of violations.

**Modes**

| Mode | Prompt example | Answer |
|---|---|---|
| `leading_tone_resolution` | `In a C major V-I cadence, soprano B over G-B-D resolves to which soprano note in the I chord? The answer is one note name.` | `C` |
| `chordal_seventh_resolution` | `In a C major V7-I cadence, alto F is the chordal seventh of V7. Which alto note should it resolve to in the I chord? The answer is one note name.` | `E` |
| `parallel_fifths_octaves` | `Two voices move bass C-D and soprano G-A. Identify the error type using one of these labels: parallel fifths, parallel octaves, no parallel fifths or octaves. The answer is one label from that list.` | `parallel fifths` |
| `invalid_harmonic_interval_structure` | `In SATB writing in C major, is a doubled leading tone valid? The answer is exactly 'yes' or 'no'.` | `no` |
| `satb_cadence_validation` | `C: V-I has soprano B-D and bass G-C. Does the leading tone resolve correctly? The answer is exactly 'yes' or 'no'.` | `no` |

**Difficulty knobs**

| Knob | Description | Modes affected | Level 0 tendency | Monotonic update effect |
|---|---|---|---|---|
| `n_voices` | Number of simultaneous melodic lines to track. | all | 1-2 voices | SATB or more abstract voices |
| `n_transitions` | Number of adjacent sonority-to-sonority moves. | all | one transition | short progressions |
| `n_rule_families` | Number of voice-leading rule categories active in the checker. | `parallel_fifths_octaves`, `invalid_harmonic_interval_structure`, `satb_cadence_validation` | one rule | several simultaneous rule checks |
| `n_violations` | Number of injected or reportable rule violations. | `parallel_fifths_octaves`, `invalid_harmonic_interval_structure`, `satb_cadence_validation` | 0 or 1 | all-violations output |
| `range_span` | Allowed pitch/register span used for voicing and spacing checks. | all | narrow | wider register and spacing checks |

`p_valid` is the probability that the sampler generates a valid voice-leading instance with no injected rule violation. It is a non-difficulty balancing control for the valid/invalid answer distribution, so keep it stable across levels unless there is a specific evaluation reason to bias toward valid or invalid examples.

**Config sketch**

```python
@dataclass
class VoiceLeadingConfig(Config):
    mode: str = "any"
    n_voices: int = 2
    n_transitions: int = 1
    n_rule_families: int = 1
    n_violations: int = 1
    range_span: int = 12
    p_valid: float = 0.50

    def update(self, c=1):
        self.n_voices += 0.5 * c
        self.n_transitions += 0.4 * c
        self.n_rule_families += 0.5 * c
        self.n_violations += 0.25 * c
        self.range_span += 2 * c
```

**Tools:** `music21.pitch`, `music21.interval`, `music21.chord`, `music21.roman`; custom rule checker; `z3-solver` for constrained voicing generation and satisfiability checks.

---

## 7. `formal_music_transformations`

**Stable task principle:** Given an initial formal music object and a transformation specification or examples, apply, invert, compare, or infer the transformation. The object type can be a triad, pitch-class set, motive, or harmonic pattern.

**Modes**

| Mode | Prompt example | Answer |
|---|---|---|
| `neo_riemannian_plr` | `Apply L to a C major triad. The answer is one triad name.` | `E minor` |
| `transformation_chain` | `Apply P then R to a C major triad. The answer is one triad name.` | `Eb major` |
| `pitch_set_standard_form` | `Using this convention: choose the most compact normal order, then transpose the first pitch class to 0, without considering inversion. What is the standard form of pitch-class set {2, 5, 9}? The answer is one ordered tuple with no spaces, e.g. '(0,4,7)'.` | `(0,3,7)` |
| `common_tone_comparison` | `How many common pitch classes do {0, 3, 7, 10} and {1, 4, 7, 10} share? The answer is one integer.` | `2` |
| `finite_transposition_set` | `Transpose {0, 2, 4, 6, 8, 10} by 2 semitones. The answer is one sorted pitch-class set with no spaces, e.g. '{1,3,8}'.` | `{0,2,4,6,8,10}` |
| `pitch_class_inversion` | `Invert ordered pitch classes (0, 4, 7) around 0. The answer is an ordered pitch-class tuple with no spaces, e.g. '(0,4,9)'.` | `(0,8,5)` |
| `harmonic_pattern_induction` | `A rule maps each Roman numeral up one diatonic degree: I-V becomes ii-vi. Apply it to V-I. The answer is hyphen-separated Roman numerals, e.g. 'ii-V-I'.` | `vi-ii` |
| `melodic_sequence_induction` | `Transpose motive C-D-E up a whole step. The answer is hyphen-separated note names.` | `D-E-F#` |
| `hidden_transformation_inference` | `Examples show (0,4,7)->(2,6,9) and (6,10,1)->(8,0,3). Apply the same pitch-class transformation to (3,7,10). The answer is an ordered pitch-class tuple with no spaces, e.g. '(1,5,8)'.` | `(5,9,0)` |

**Difficulty knobs**

| Knob | Description | Modes affected | Level 0 tendency | Monotonic update effect |
|---|---|---|---|---|
| `object_size` | Number of elements in the pitch set, motive, or harmonic object. | `pitch_set_standard_form`, `common_tone_comparison`, `finite_transposition_set`, `pitch_class_inversion`, `melodic_sequence_induction`, `hidden_transformation_inference` | triads or trichords | larger pitch sets or motives |
| `chain_len` | Number of transformations applied in sequence. | `neo_riemannian_plr`, `transformation_chain`, `finite_transposition_set`, `pitch_class_inversion`, `melodic_sequence_induction` | one operation | longer transformation chains |
| `search_depth` | Maximum path length or inference depth for inverse/search tasks. | `neo_riemannian_plr`, `transformation_chain`, `hidden_transformation_inference` | direct application | shortest path or inverse search |
| `n_examples` | Number of input-output examples shown for rule induction. | `harmonic_pattern_induction`, `melodic_sequence_induction`, `hidden_transformation_inference` | none or one | pattern induction from several examples |
| `n_distractors` | Number of plausible but wrong options or paths. | `transformation_chain`, `common_tone_comparison`, `hidden_transformation_inference` | none | choose among plausible transformations |
| `p_infer_rule` | Probability that the transformation rule must be inferred rather than stated. | `harmonic_pattern_induction`, `melodic_sequence_induction`, `hidden_transformation_inference` | low | more hidden-rule induction |

**Config sketch**

```python
@dataclass
class FormalTransformConfig(Config):
    mode: str = "any"
    object_size: int = 3
    chain_len: int = 1
    search_depth: int = 1
    n_examples: int = 1
    n_distractors: int = 0
    p_infer_rule: float = 0.10

    def update(self, c=1):
        self.object_size += 0.4 * c
        self.chain_len += 0.5 * c
        self.search_depth += 0.6 * c
        self.n_examples += 0.3 * c
        self.n_distractors += 0.5 * c
        self.p_infer_rule = min(0.65, self.p_infer_rule + 0.07 * c)
```

**Tools:** custom PLR and pitch-class arithmetic as source of truth; `networkx` for graph search; `numpy`/`sympy` for modular operations; `music21` for spelling and cross-checks.

---

## 8. `analysis_representation_reasoning`

**Stable task principle:** Given a score/ABC fragment or one or more structured analysis records, convert, validate, repair, complete, or diff them under a canonical schema.

**Modes**

| Mode | Prompt example | Answer |
|---|---|---|
| `score_property_extraction` | `Given the ABC chord fragment K:C [D^FAc], extract the chord and analyze it in C major. The answer is one compact Roman numeral, e.g. 'I6' or 'V65'.` | `V7/V` |
| `non_chord_tone_count` | `Given the ABC melody K:C C D E F G over a C major triad, count notes outside the chord tones C, E, and G. The answer is one integer.` | `2` |
| `abc_score_parsing` | `ABC notes ^C _D E represent which written note-name sequence? The answer is comma-separated note names in order.` | `C#, Db, E` |
| `analysis_normalization` | `Normalize "applied dominant seventh to the supertonic in C" as a Roman numeral. The answer is one Roman numeral.` | `V7/ii` |
| `romantext_repair` | `Repair the invalid Roman label "V7V" in C major when it means dominant seventh of the dominant. The answer is one canonical Roman label.` | `V7/V` |
| `score_to_romantext` | `Measure 3 in key G contains D-F#-A-C. The answer is one RomanText-style record in the format 'm<measure> <key>: <Roman>', e.g. 'm2 C: I6'.` | `m3 G: V7` |
| `representation_conversion` | `Convert key=C and roman=V7 to compact text. The answer is exactly "key: roman".` | `C: V7` |
| `semantic_diff` | `A uses V7/V; B writes D7 in key C for the same chord. Is there a semantic diff? Choose from: no semantic change, changed root, changed quality, changed inversion, changed key, changed function. The answer is one label from that list.` | `no semantic change` |

**Difficulty knobs**

| Knob | Description | Modes affected | Level 0 tendency | Monotonic update effect |
|---|---|---|---|---|
| `n_records` | Number of analysis rows, events, measures, or records. | `analysis_normalization`, `romantext_repair`, `score_to_romantext`, `representation_conversion`, `semantic_diff` | one record | multi-line analyses |
| `n_formats` | Number of representation formats involved in the conversion/check. | `abc_score_parsing`, `score_to_romantext`, `representation_conversion`, `semantic_diff` | one source and one target | multiple intermediate formats |
| `n_missing_fields` | Number of omitted schema fields to infer or repair. | `romantext_repair`, `score_to_romantext` | none or one | completion/repair with inherited defaults |
| `n_edits` | Number of corruptions, repairs, or semantic diff operations. | `romantext_repair`, `semantic_diff` | one edit | structured diff lists |
| `score_len` | Length of the score excerpt linked to the analysis record. | `score_property_extraction`, `non_chord_tone_count`, `abc_score_parsing`, `score_to_romantext` | one chord/measure | score fragments with non-chord tones |
| `p_semantic_equiv` | Probability of textually different but semantically equivalent analyses. | `analysis_normalization`, `romantext_repair`, `representation_conversion`, `semantic_diff` | low | more textually different but equivalent labels |

**Config sketch**

```python
@dataclass
class AnalysisRepresentationConfig(Config):
    mode: str = "any"
    n_records: int = 1
    n_formats: int = 1
    n_missing_fields: int = 0
    n_edits: int = 1
    score_len: int = 1
    p_semantic_equiv: float = 0.10

    def update(self, c=1):
        self.n_records += c
        self.n_formats += 0.3 * c
        self.n_missing_fields += 0.3 * c
        self.n_edits += 0.4 * c
        self.score_len += 0.5 * c
        self.p_semantic_equiv = min(0.65, self.p_semantic_equiv + 0.06 * c)
```

**Tools:** project-owned canonical record schema; `json`, `csv`, `pandas`, `pyyaml`, `tabulate`, `pyparsing`; `music21.roman` and `music21.key` for musical validation; `whatthepatch`, `difflib`, and `rapidfuzz` for diff diagnostics.

---

# Dependency and Tool Inventory

## Recommended New Dependency

- `music21`: primary symbolic music theory engine for convention-heavy primitives. Use it for pitches, intervals, chords, keys, scales, meter/duration notation, clefs, instruments, streams, score conversion, Roman numerals, RomanText-style analysis, and verification canonicalizers.

## Already Present in `pyproject.toml`

- `z3-solver`: constraint solving for voice leading, unique-key inference, valid continuation search, and missing-duration solving.
- `networkx`: graph search for Neo-Riemannian transformations, modulation/key-distance graphs, harmonic transition graphs, and shortest paths.
- `numpy`: finite sampling, pitch-class arrays, interval vectors, balancing answer classes, and modular operations.
- `sympy`: exact symbolic or modular arithmetic when pitch-class operations need transparent algebraic checks.
- `nltk`, `gramforge`, `greenery`: grammar-backed generation, parsing, and regular-language subsets.
- `pyparsing`: compact custom parsers for progressions, RomanText-like syntax, or analysis records.
- `pandas`, `pyyaml`, `tabulate`: tabular and structured representation tasks.
- `whatthepatch`, `rapidfuzz`: diff-style repair diagnostics and tolerant matching.

---

# Implementation Checklist

- Keep `mode` independent of `level`; level changes instance size and complexity only.
- Add `mode: str = "any"` to each config. When it is `"any"`, sample a concrete mode; when it is fixed, generate only that mode.
- Store the resolved concrete mode in `metadata["mode"]`.
- Prefer knobs such as `chain_len`, `context_len`, `n_constraints`, `n_candidates`, `n_records`, `n_edits`, `max_accidental`, and probabilities.
- Avoid code like `if level >= 3: mode = "secondary_dominant"`.
- Keep count-like knobs annotated as `int`; fractional updates such as `self.n_candidates += 0.5 * c` rely on Reasoning Core's stochastic rounding.
- Use `float` annotations for probabilities or continuous controls such as `self.p_chromatic = min(...)`.
- Keep non-difficulty balancing controls, such as valid/invalid mixture probabilities, separate from level-driven difficulty knobs.
- Rely on framework fields such as `_task`, `_level`, and `_config` instead of duplicating them in task-owned metadata.
- Store the hidden formal state in metadata.
- Generate `cot` from the solver's logged intermediate steps and the same symbolic operations used to compute the answer, not from a separate natural-language explanation.
- Make answer formats explicit in prompts and canonical in `score_answer`.

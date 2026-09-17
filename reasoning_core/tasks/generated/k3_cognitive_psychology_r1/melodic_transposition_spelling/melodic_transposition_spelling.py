import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

LETTERS = "CDEFGAB"
NATURAL = dict(zip(LETTERS, (0, 2, 4, 5, 7, 9, 11)))
FIFTHS = {"C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5, "F": -1}
MAJOR_STEPS = (0, 2, 4, 5, 7, 9, 11)
ACC_STR = {-2: "bb", -1: "b", 0: "n", 1: "#", 2: "##"}
INTERVALS = (
    ("minor second", 1, 1), ("major second", 1, 2),
    ("minor third", 2, 3), ("major third", 2, 4),
    ("perfect fourth", 3, 5), ("augmented fourth", 3, 6),
    ("diminished fifth", 4, 6), ("perfect fifth", 4, 7),
    ("minor sixth", 5, 8), ("major sixth", 5, 9),
    ("minor seventh", 6, 10), ("major seventh", 6, 11),
)


def _signature(pos):
    accidentals = dict.fromkeys(LETTERS, 0)
    for letter in ("FCGDAEB" if pos > 0 else "BEADGCF")[:abs(pos)]:
        accidentals[letter] = 1 if pos > 0 else -1
    return accidentals


def _tonic(pos):
    return next((letter, acc) for letter in LETTERS for acc in (-1, 0, 1)
                if FIFTHS[letter] + 7 * acc == pos)


def _pc(note):
    letter, acc = note
    return (NATURAL[letter] + acc) % 12


def _transpose(note, steps, semitones):
    letter = LETTERS[(LETTERS.index(note[0]) + steps) % 7]
    acc = (_pc(note) + semitones - NATURAL[letter] + 6) % 12 - 6
    return (letter, acc) if acc in ACC_STR else None


def _spell(note):
    return note[0] + ACC_STR[note[1]]


def _sig_str(pos):
    return f"{abs(pos)} {'sharps' if pos > 0 else 'flats'}" if pos else "no sharps or flats"


def _verify_shift(source, target, steps, semitones):
    candidates = [(letter, acc) for letter in LETTERS for acc in ACC_STR
                  if (LETTERS.index(letter) - LETTERS.index(source[0]) - steps) % 7 == 0
                  and (_pc((letter, acc)) - _pc(source) - semitones) % 12 == 0]
    assert candidates == [target]


@dataclass
class MelodicTranspositionConfig(Config):
    n_notes: int = 3
    n_stages: int = 1
    chromatic_prob: float = 0.15

    def apply_difficulty(self, level):
        self.n_notes = 3 + min(9, int(level))
        self.n_stages = 1 + min(3, int(level) // 2)
        self.chromatic_prob = min(0.6, 0.15 + 0.06 * level)


class MelodicTranspositionSpelling(Task):
    summary = "Transpose diatonic melodies, chromatically altered melodies, and major-scale fragments through stipulated signed intervals and key signatures using local courtesy accidentals and strict letter-preserving respelling; answer with explicit letter/accidental sequences or only the final key signature for scale fragments."
    design_choice = "Answer format varies: output the transposed melody as a sequence of letter-name/accidental pairs, or output only the new key signature when the melody is a scale fragment."
    config_cls = MelodicTranspositionConfig
    task_name = "melodic_transposition_spelling"
    task_version = 3

    def generate_entry(self):
        cfg = self.config
        frag = random.choice((False, True))
        final_sig = random.randint(-7, 7)
        for _ in range(300):
            stages = []
            for _ in range(cfg.n_stages):
                name, steps, semis = random.choice(INTERVALS)
                direction = random.choice((-1, 1))
                stages.append([name, direction * steps, direction * semis])
            tonic = _tonic(final_sig)
            for _, steps, semis in reversed(stages):
                tonic = _transpose(tonic, -steps, -semis)
                if tonic is None:
                    break
            if tonic is None:
                continue
            source_sig = FIFTHS[tonic[0]] + 7 * tonic[1]
            if abs(source_sig) > 7:
                continue
            key = _signature(source_sig)
            start = random.randrange(7)
            indices = [(start + i) % 7 for i in range(cfg.n_notes)] if frag else [
                random.randrange(7) for _ in range(cfg.n_notes)]
            melody = []
            tokens = []
            for index in indices:
                letter = LETTERS[(LETTERS.index(tonic[0]) + index) % 7]
                acc = key[letter]
                if not frag and random.random() < cfg.chromatic_prob:
                    acc += random.choice((-1, 1))
                melody.append((letter, acc))
                tokens.append(letter if acc == key[letter] and random.random() < 0.6
                              else _spell((letter, acc)))
            transposed = melody
            current_tonic = tonic
            valid = True
            for _, steps, semis in stages:
                shifted = [_transpose(note, steps, semis) for note in transposed]
                next_tonic = _transpose(current_tonic, steps, semis)
                if next_tonic is None or any(note is None for note in shifted):
                    valid = False
                    break
                for source, target in zip(transposed, shifted):
                    _verify_shift(source, target, steps, semis)
                _verify_shift(current_tonic, next_tonic, steps, semis)
                transposed, current_tonic = shifted, next_tonic
            if not valid:
                continue
            assert current_tonic == _tonic(final_sig)
            final_key = _signature(final_sig)
            for degree, offset in enumerate(MAJOR_STEPS):
                letter = LETTERS[(LETTERS.index(current_tonic[0]) + degree) % 7]
                assert (_pc((letter, final_key[letter])) - _pc(current_tonic)) % 12 == offset
            if frag:
                matches = [pos for pos in range(-7, 8) if _tonic(pos) == current_tonic
                           and all(_signature(pos)[letter] == acc for letter, acc in transposed)]
                assert matches == [final_sig]
                answer = _sig_str(final_sig)
            else:
                answer = " ".join(map(_spell, transposed))
                recovered = [(token[0], next(acc for acc, suffix in ACC_STR.items()
                                             if token[1:] == suffix)) for token in answer.split()]
                assert recovered == transposed
            metadata = {"source_signature": source_sig, "source_tonic": _spell(tonic),
                        "stages": stages, "melody": tokens,
                        "source_notes": [list(note) for note in melody],
                        "transposed": [list(note) for note in transposed],
                        "final_signature": final_sig,
                        "mode": "key_signature" if frag else "notes"}
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("Unable to construct a supported spelling after 300 attempts")

    def render_prompt(self, metadata):
        operations = "; then ".join(
            f"{'up' if steps > 0 else 'down'} by a{'n' if name.startswith('a') else ''} {name} "
            f"({abs(steps)} letter step{'s' if abs(steps) != 1 else ''}, "
            f"{abs(semis)} semitone{'s' if abs(semis) != 1 else ''})"
            for name, steps, semis in metadata["stages"])
        kind = "ascending major-scale fragment" if metadata["mode"] == "key_signature" else "melody"
        signature = _sig_str(metadata["source_signature"])
        if abs(metadata["source_signature"]) == 1:
            signature = signature[:-1]
        prompt = (
            f"An arranger has this {kind} in {metadata['source_tonic']} major "
            f"with {signature}: {' '.join(metadata['melody'])}.\n"
            f"Transpose the key and every note in order: {operations}.\n"
            "Use diatonic/chromatic transposition: move letters cyclically through C D E F G A B "
            "and adjust accidentals to match the semitone shift. Natural pitch classes are "
            "C=0 D=2 E=4 F=5 G=7 A=9 B=11, modulo 12; ignore octaves. "
            "Key sharps follow F C G D A E B; flats follow B E A D G C F. "
            "In the input, a bare letter uses the source key signature; n, #, b, ##, bb mean "
            "absolute offsets 0, +1, -1, +2, -2 from the natural letter, overriding the key "
            "for that note only (no carry). Redundant courtesy accidentals change nothing. "
            "Retain each shifted letter at every stage: never substitute enharmonic letters.\n"
        )
        if metadata["mode"] == "notes":
            return prompt + (
                "Return only the final notes in input order, each with an explicit accidental "
                "including n for naturals, regardless of the final key. Format example: Gn F# Bbb."
            )
        return prompt + (
            "The final key is major on the transposed source tonic (major offsets: "
            "0, 2, 4, 5, 7, 9, 11). Return only its signature as 'N sharps', 'N flats', "
            "or 'no sharps or flats'; use the plural even for one. Format example: 3 flats."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return float(" ".join(answer.split()) == entry.answer)


TASK_META = {'parent_source_id': None,
 'idea': 'melodic_transposition_spelling (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_cognitive_psychology_r1/melodic_transposition_spelling',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

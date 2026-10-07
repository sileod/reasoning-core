"""Apply a numbered list of word-level edits to a natural sentence and write the resulting sentence.

Edits replace, delete, insert before or after, swap, or move a word to the start or end; words are named by their
text (unique at that moment) or by position. Every word of the answer is checked, so the answer is long but has
no slack. Level lengthens the sentence and the edit list.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Entry, stochastic_rounding as sround

DET = ["the", "a", "every", "one", "that"]
ADJ = ["old", "quiet", "narrow", "bright", "heavy", "young", "careful", "distant", "small", "patient", "wooden", "green"]
NOUN = ["farmer", "river", "teacher", "bridge", "lantern", "village", "merchant", "garden", "letter", "engine",
        "harbor", "painter", "window", "basket", "soldier", "market"]
VERB = ["carried", "found", "painted", "watched", "repaired", "followed", "sold", "opened", "crossed", "described"]
PREP = ["across", "beside", "under", "near", "behind", "through", "toward", "past"]
TIME = ["at dawn", "before noon", "after the storm", "on Sunday", "last winter", "in silence", "by evening"]
ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]
EXTRA = ["slowly", "again", "twice", "almost", "never", "gladly", "still", "nearly", "often", "quickly"]


@dataclass
class SentenceEditingConfig(Config):
    n_phrases: float = 1
    n_edits: float = 2

    def apply_difficulty(self, level):
        self.n_phrases += 0.5 * level
        self.n_edits += 1.2 * level


def _np(rng):
    return [rng.choice(DET)] + rng.sample(ADJ, rng.randint(0, 2)) + [rng.choice(NOUN)]


def _sentence(rng, phrases):
    words = _np(rng) + [rng.choice(VERB)] + _np(rng)
    for _ in range(phrases):
        words += [rng.choice(PREP)] + _np(rng)
    return words + rng.choice(TIME).split()


def _ref(rng, words, i):
    """Name word i by its text when that text is unique, else by its position."""
    if words.count(words[i]) == 1 and rng.random() < 0.7:
        return f'"{words[i]}"'
    return f"the {ORD[i]} word" if i < len(ORD) else None


def _edit(rng, words):
    """One random edit: (instruction, new words) or None."""
    i = rng.randrange(len(words))
    ref = _ref(rng, words, i)
    if ref is None:
        return None
    new = rng.choice([w for w in ADJ + NOUN + EXTRA if w not in words])
    op = rng.choice(["replace", "delete", "insert_after", "insert_before", "swap", "to_start", "to_end"])
    w = list(words)
    if op == "replace":
        w[i] = new
        return f'Replace {ref} with "{new}".', w
    if op == "delete" and len(w) > 4:
        del w[i]
        return f"Delete {ref}.", w
    if op == "insert_after":
        w.insert(i + 1, new)
        return f'Insert "{new}" after {ref}.', w
    if op == "insert_before":
        w.insert(i, new)
        return f'Insert "{new}" before {ref}.', w
    if op == "swap":
        j = rng.randrange(len(w))
        ref2 = _ref(rng, words, j)
        if j == i or ref2 is None or w[i] == w[j]:
            return None
        w[i], w[j] = w[j], w[i]
        return f"Swap {ref} and {ref2}.", w
    if op in ("to_start", "to_end") and 0 < i < len(w) - 1:
        x = w.pop(i)
        w = [x] + w if op == "to_start" else w + [x]
        return f"Move {ref} to the {'start' if op == 'to_start' else 'end'} of the sentence.", w
    return None


class SentenceEditing(DevTask):
    summary = ("Apply an ordered list of word-level edits -- replace, delete, insert before/after, swap, move to start "
               "or end, words named by text or by position -- to a generated natural sentence and write the full "
               "resulting sentence.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or SentenceEditingConfig())

    def generate_entry(self):
        c, rng = self.config, random
        words = _sentence(rng, max(0, sround(c.n_phrases)))
        start, edits, want = list(words), [], max(1, sround(c.n_edits))
        while len(edits) < want:
            e = _edit(rng, words)
            if e:
                edits.append(e[0])
                words = e[1]
        return Entry({"sentence": " ".join(start), "edits": edits}, " ".join(words))

    def render_prompt(self, m):
        steps = "\n".join(f"{k}. {e}" for k, e in enumerate(m["edits"], 1))
        return (f"Sentence: {m['sentence']}\nApply these edits in order (positions refer to the sentence as it is "
                f"at that step):\n{steps}\nAnswer with the final sentence only, words separated by single spaces.")

    def score_answer(self, answer, entry):
        got = " ".join(str(answer).strip().rstrip(".").split())
        return float(got == entry.answer)

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

VOWELS = "aeiou"
CONS = "tksfmnlr"
SON = {c: rank for rank, group in enumerate(("tksf", "mn", "lr"), 1) for c in group}
VSON = {"a": 3, "e": 2, "o": 2, "i": 1, "u": 1}

TASK_META = {'parent_source_id': None,
 'idea': 'weight_sensitive_stress_parse (variant 2 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_controlled_nli_r1/weight_sensitive_stress_parse',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1705404348,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def parse_syllables(word):
    nuclei = []
    i = 0
    while i < len(word):
        if word[i] not in VOWELS:
            i += 1
            continue
        end = i + 1
        if end < len(word) and word[end] in VOWELS and VSON[word[i]] > VSON[word[end]]:
            end += 1
        nuclei.append((i, end))
        i = end
    if not nuclei:
        raise ValueError("A word needs a vowel")
    boundaries = [0]
    for (_, end), (start, _) in zip(nuclei, nuclei[1:]):
        boundary = start
        if boundary > end:
            boundary -= 1
            while boundary > end and SON[word[boundary - 1]] < SON[word[boundary]]:
                boundary -= 1
        boundaries.append(boundary)
    boundaries.append(len(word))
    return [word[a:b] for a, b in zip(boundaries, boundaries[1:])]


def is_heavy(syllable):
    return syllable[-1] in CONS or sum(c in VOWELS for c in syllable) == 2


def build_feet(syllables, direction):
    order = list(range(len(syllables)))
    if direction == "right":
        order.reverse()
    feet = []
    i = 0
    while i < len(order):
        size = 1
        if i + 1 < len(order) and not any(is_heavy(syllables[j]) for j in order[i:i + 2]):
            size = 2
        feet.append(sorted(order[i:i + size]))
        i += size
    return sorted(feet)


def footed_parse_answer(syllables, feet, headedness):
    return "-".join(
        ".".join(("'" if j == foot[0 if headedness == "left" else -1] else "") + syllables[j]
                 for j in foot)
        for foot in feet
    )


def verify_analysis(word, syllables, feet, heads, direction, headedness):
    assert "".join(syllables) == word
    spans = []
    offset = 0
    for syllable in syllables:
        positions = [offset + i for i, c in enumerate(syllable) if c in VOWELS]
        assert len(positions) in (1, 2)
        assert positions == list(range(positions[0], positions[-1] + 1))
        if len(positions) == 2:
            assert VSON[word[positions[0]]] > VSON[word[positions[1]]]
        spans.append((positions[0], positions[-1] + 1))
        offset += len(syllable)
    for i, (a, b) in enumerate(spans):
        if b - a == 1 and b < len(word) and word[b] in VOWELS:
            assert VSON[word[a]] <= VSON[word[b]]
        if i:
            start = sum(map(len, syllables[:i]))
            previous_end = spans[i - 1][1]
            candidates = [j for j in range(previous_end, a + 1)
                          if all(SON[word[k]] < SON[word[k + 1]] for k in range(j, a - 1))]
            assert start == min(candidates)
    assert [j for foot in feet for j in foot] == list(range(len(syllables)))
    scanning = feet if direction == "left" else list(reversed(feet))
    for i, foot in enumerate(scanning):
        assert len(foot) in (1, 2)
        if len(foot) == 2:
            assert all(not is_heavy(syllables[j]) for j in foot)
        elif not is_heavy(syllables[foot[0]]) and i + 1 < len(scanning):
            neighbor = scanning[i + 1][0 if direction == "left" else -1]
            assert is_heavy(syllables[neighbor])
    assert heads == [foot[0 if headedness == "left" else -1] for foot in feet]


@dataclass
class WeightSensitiveStressParseConfig(Config):
    chunks: int = 4
    cluster_limit: int = 2
    vowel_limit: int = 2

    def apply_difficulty(self, level):
        self.chunks = 4 + int(level)
        self.cluster_limit = 2 + int(level) // 2
        self.vowel_limit = 2 + int(level) // 3


class WeightSensitiveStressParse(Task):
    summary = "Parse segment strings with sonority-conditioned diphthongs, hiatus and maximal rising onsets, build weight-sensitive feet in either direction and headedness, and return an edge-selected stressed syllable index, the marked footed parse, or the first clash."
    design_choice = "Difficulty arises from ambiguous syllabification: input includes vowel sequences and coda consonants whose syllabification is determined by a stated sonority hierarchy, not just segment count."
    config_cls = WeightSensitiveStressParseConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        count = random.randint(cfg.chunks, cfg.chunks + 2)
        vowels = ["".join(random.choices(VOWELS, k=random.choice([1, 1, cfg.vowel_limit])))
                  for _ in range(count)]
        vowels[random.randrange(count)] = "".join(random.choices(VOWELS, k=cfg.vowel_limit))
        runs = ["".join(random.choices(CONS, k=random.choice([1, 1, 1, cfg.cluster_limit])))
                for _ in range(count - 1)]
        runs[random.randrange(count - 1)] = random.choice(CONS) + random.choice("tksf")
        word = random.choice(["", *CONS]) + vowels[0]
        word += "".join(run + vowel for run, vowel in zip(runs, vowels[1:]))
        word += random.choice(["", "", "", *CONS])
        syllables = parse_syllables(word)
        direction = random.choice(["left", "right"])
        headedness = random.choice(["left", "right"])
        edge = random.choice(["left", "right"])
        mode = random.choice(["stress", "parse", "clash"])
        feet = build_feet(syllables, direction)
        heads = [foot[0 if headedness == "left" else -1] for foot in feet]
        verify_analysis(word, syllables, feet, heads, direction, headedness)
        clashes = [a for a, b in zip(heads, heads[1:]) if b == a + 1]
        if mode == "stress":
            answer = str(heads[0 if edge == "left" else -1] + 1)
            assert 1 <= int(answer) <= len(syllables)
            assert int(answer) - 1 in heads
        elif mode == "parse":
            answer = footed_parse_answer(syllables, feet, headedness)
            recovered = [s for foot in answer.split("-") for s in foot.split(".")]
            assert [s.lstrip("'") for s in recovered] == syllables
            assert [i for i, s in enumerate(recovered) if s.startswith("'")] == heads
            assert [len(f.split(".")) for f in answer.split("-")] == list(map(len, feet))
        else:
            answer = str(clashes[0] + 1) if clashes else "none"
            adjacent = [i for i in range(len(syllables) - 1) if i in heads and i + 1 in heads]
            assert answer == (str(min(adjacent) + 1) if adjacent else "none")
        return Entry(metadata={"word": word, "syllables": syllables, "feet": feet,
                               "heads": heads, "direction": direction, "headedness": headedness,
                               "edge": edge, "mode": mode}, answer=answer)

    def render_prompt(self, metadata):
        base = (
            f"A linguist is testing this artificial prosodic grammar on the segment string {metadata['word']}.\n"
            "Use these rules, not any natural language's conventions. Sonority increases as "
            "t=k=s=f < m=n < l=r < i=u < e=o < a. Only a,e,i,o,u are vowels.\n"
            "Scan each vowel run left to right: consume two vowels as one diphthong nucleus "
            "if the first has strictly higher sonority than the second; otherwise consume one "
            "vowel as a nucleus. Repeat on unconsumed vowels. A nucleus never exceeds two vowels.\n"
            "Use the maximal-onset algorithm: between successive nuclei, give the next syllable "
            "the longest consonant suffix with strictly rising sonority (a single consonant qualifies); "
            "the rest is the preceding syllable's coda. Empty runs give empty onsets. "
            "Initial consonants belong to the first onset; final consonants to the last coda.\n"
            "A syllable is heavy exactly when it has a diphthong or a nonempty coda; otherwise light. "
            f"Build feet greedily from the {metadata['direction']} edge: a heavy syllable is a singleton; "
            "pair a light syllable with the next unconsumed syllable in the scan only if that "
            "syllable is also light; otherwise make the light syllable a singleton. Consume and repeat. "
            f"Stress the {metadata['headedness']} syllable of every pair and every singleton. "
            "Left/right always refers to written order. Index syllables from one, left to right.\n"
        )
        if metadata["mode"] == "stress":
            return base + (
                f"Return the stressed syllable index in the foot closest to the {metadata['edge']} edge. "
                "Use one integer, e.g. 7, with no explanation."
            )
        if metadata["mode"] == "parse":
            return base + (
                "Return the full footed parse in written order: join syllables within feet with '.', "
                "feet with '-', and prefix each stressed syllable with an apostrophe. "
                "Format example: 'ka.mi-'tu (a left-headed pair followed by a singleton). "
                "Copy all segments exactly; no spaces or explanation."
            )
        return base + (
            "A clash is two adjacent stressed syllables, even across feet. Return the index "
            "of the LEFT member of the leftmost clash, or none if absent. "
            "Format examples: 7 or none. No explanation."
        )

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip() == entry.answer)

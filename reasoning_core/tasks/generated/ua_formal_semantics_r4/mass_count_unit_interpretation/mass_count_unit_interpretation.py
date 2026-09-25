import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

READINGS = ("substance", "portion", "package", "kind")

NOUNS = {
    "coffee": {"portion": "cup", "package": "bag", "kind": "roast", "container": "mug"},
    "beer": {"portion": "glass", "package": "bottle", "kind": "style", "container": "pitcher"},
    "wine": {"portion": "glass", "package": "bottle", "kind": "variety", "container": "glass"},
    "paper": {"portion": "sheet", "package": "ream", "kind": "type", "container": "pile"},
    "tea": {"portion": "cup", "package": "box", "kind": "variety", "container": "pot"},
    "chocolate": {"portion": "square", "package": "box", "kind": "type", "container": "tin"},
    "whiskey": {"portion": "measure", "package": "bottle", "kind": "brand", "container": "glass"},
    "oil": {"portion": "drop", "package": "jug", "kind": "grade", "container": "drum"},
    "yogurt": {"portion": "cup", "package": "tub", "kind": "style", "container": "bowl"},
    "ice cream": {"portion": "scoop", "package": "brick", "kind": "flavor", "container": "cone"},
}

QUANTIFIERS = ("two", "three", "four", "several", "five")


def _plural(word):
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    if word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


def _unit(noun, reading):
    return NOUNS[noun][reading]


def _clause_phrase(noun, reading):
    info = NOUNS[noun]
    if reading == "substance":
        return f"there is {noun} in the {info['container']}"
    if reading == "portion":
        q = random.choice(QUANTIFIERS)
        unit = info["portion"]
        return f"he asked for {q} {_plural(unit)} of {noun}"
    if reading == "package":
        q = random.choice(QUANTIFIERS)
        unit = info["package"]
        return f"she bought {q} {_plural(unit)} of {noun}"
    if reading == "kind":
        q = random.choice(QUANTIFIERS)
        unit = info["kind"]
        return f"the shop stocks {q} {_plural(unit)} of {noun}"


def _clause_answer(noun, reading):
    if reading == "substance":
        return "substance"
    return f"{reading}: {_unit(noun, reading)}"


TASK_META = {
    "parent_source_id": None,
    "idea": "mass_count_unit_interpretation (variant 1 of 3)",
    "hypothesis": "P006",
    "changes": "new task in "
    "reasoning_core/tasks/generated/ua_formal_semantics_r4/mass_count_unit_interpretation",
    "generation": {
        "provider_name": "albert",
        "model_name": "deepseek-v4-flash",
        "harness_name": "opencode",
        "harness_version": "1.18.32",
        "agent_name": "task-search-worker",
        "settings": {
            "variant": None,
            "requested_seed": 798610012,
            "seed_forwarded": True,
            "temperature": None,
            "top_p": None,
            "pure": True,
            "max_steps": 56,
            "timeout_seconds": 1800,
            "sandbox": {"name": "bubblewrap", "version": "bubblewrap 0.8.0"},
        },
    },
}


@dataclass
class MassCountConfig(Config):
    occurrences: int = 1

    def apply_difficulty(self, level):
        self.occurrences = 1 + level // 2


class MassCountUnitInterpretation(Task):
    summary = (
        "Interpret mass and count expressions through substance, portion, package, "
        "and kind readings with explicit realization maps; compose classifiers and "
        "partitives; return the selected units or their quantity."
    )

    design_choice = (
        "Each instance presents a sentence with an ambiguous mass/count noun and four "
        "readings (substance, portion, package, kind); the solver must output the "
        "canonical reading label (e.g., 'portion') plus the unit type if specified."
    )

    config_cls = MassCountConfig
    task_version = 2

    def generate_entry(self):
        clauses = []
        sentence_parts = []
        noun_pool = sorted(NOUNS.keys())
        for _ in range(self.config.occurrences):
            noun = random.choice(noun_pool)
            reading = random.choice(READINGS)
            clauses.append((noun, reading))
            sentence_parts.append(_clause_phrase(noun, reading))

        seps = random.choice(
            [
                ", while ",
                "; meanwhile ",
                ", and ",
                ", while later ",
            ]
        ) if len(sentence_parts) > 1 else ""
        sentence = sentence_parts[0] + (
            seps.join(("", *sentence_parts[1:])) if len(sentence_parts) > 1 else ""
        )
        answer = "; ".join(_clause_answer(noun, reading) for noun, reading in clauses)
        return Entry(
            metadata={
                "sentence": sentence,
                "clauses": [{"noun": n, "reading": r} for n, r in clauses],
                "occurrences": self.config.occurrences,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        return (
            "The following sentence uses one or more mass/count nouns. For each noun "
            "occurrence, pick exactly one of four readings: "
            "'substance' (the undifferentiated material), "
            "'portion' (a serving or amount, e.g. a cup), "
            "'package' (a container or parcel, e.g. a bottle), "
            "or 'kind' (a type or variety). "
            "Report each reading; when it is a portion, package, or kind, append that "
            "unit after a colon. Separate multiple interpretations with a semicolon. "
            "Example: 'she bought two bottles of wine' -> package: bottle; "
            "'there is wine in the glass' -> substance.\n"
            f"Sentence: {metadata['sentence']}\n"
            "Answer:"
        )

    def score_answer(self, answer, entry):
        reference = entry["answer"]
        return 1.0 if str(answer).strip() == str(reference).strip() else 0.0

    def distractor_candidates(self, entry):
        for noun, reading in entry.metadata["clauses"]:
            for other in READINGS:
                if other != reading:
                    yield _clause_answer(noun, other)

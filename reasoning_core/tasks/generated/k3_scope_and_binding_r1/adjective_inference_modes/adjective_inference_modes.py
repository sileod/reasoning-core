import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'adjective_inference_modes (draw 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scope_and_binding_r1/adjective_inference_modes',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                          'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class AdjectiveInferenceModesV2Config(Config):
    n_instances: int = 1

    def apply_difficulty(self, level):
        self.n_instances = self.n_instances + level


MODES = ["intersective", "subsective", "privative"]

MODE_LETTER = {"intersective": "I", "subsective": "S", "privative": "P"}

DROP = {"intersective": 1, "subsective": 1, "privative": 1}
SWAP = {"intersective": 1, "subsective": 0, "privative": 0}
CONJ = {"intersective": 1, "subsective": 1, "privative": 0}

LEXICON = {
    "intersective": [
        ("red", "car", "truck"),
        ("blue", "ball", "sphere"),
        ("wooden", "table", "desk"),
        ("spotted", "cat", "leopard"),
        ("green", "apple", "fruit"),
        ("metal", "spoon", "utensil"),
        ("salty", "pretzel", "snack"),
        ("woolen", "sweater", "garment"),
        ("round", "coin", "disk"),
        ("sour", "lemon", "citrus"),
        ("striped", "tie", "accessory"),
        ("frozen", "lake", "body-of-water"),
        ("velvet", "curtain", "drapery"),
        ("bitter", "almond", "nut"),
        ("golden", "retriever", "dog"),
        ("hollow", "pipe", "tube"),
        ("rectangular", "rug", "mat"),
        ("muddy", "trail", "path"),
        ("fragrant", "rose", "flower"),
        ("crisp", "apple", "pome"),
        ("luminous", "beacon", "light"),
        ("damp", "towel", "cloth"),
        ("ivory", "piano-key", "key"),
        ("crimson", "tulip", "bulb"),
    ],
    "subsective": [
        ("skillful", "surgeon", "doctor"),
        ("able", "pianist", "musician"),
        ("fast", "runner", "athlete"),
        ("recent", "report", "document"),
        ("expert", "climber", "mountaineer"),
        ("talented", "actor", "performer"),
        ("seasoned", "pilot", "aviator"),
        ("gifted", "student", "learner"),
        ("proficient", "coder", "programmer"),
        ("accomplished", "lawyer", "advocate"),
        ("dependable", "courier", "deliverer"),
        ("veteran", "soldier", "fighter"),
        ("renowned", "chef", "cook"),
        ("sharp", "marksman", "shooter"),
        ("adept", "translator", "linguist"),
        ("brilliant", "strategist", "planner"),
        ("masterful", "conductor", "musician"),
        ("adroit", "negotiator", "diplomat"),
        ("deft", "artisan", "craftsman"),
        ("dexterous", "juggler", "performer"),
        ("practiced", "orator", "speaker"),
        ("consummate", "host", "hostess"),
        ("polished", "performer", "entertainer"),
        ("influential", "historian", "scholar"),
    ],
    "privative": [
        ("fake", "diamond", "gemstone"),
        ("alleged", "thief", "criminal"),
        ("former", "captain", "sailor"),
        ("pretend", "gem", "jewel"),
        ("imitation", "pearl", "jewelry"),
        ("mock", "trial", "proceeding"),
        ("phony", "rolex", "watch"),
        ("sham", "healing", "treatment"),
        ("fictitious", "character", "person"),
        ("ostensible", "cousin", "relative"),
        ("so-called", "expert", "authority"),
        ("ersatz", "coffee", "beverage"),
        ("would-be", "actor", "performer"),
        ("quasi", "scholar", "researcher"),
        ("bogus", "receipt", "document"),
        ("counterfeit", "bill", "currency"),
        ("feigned", "smile", "expression"),
        ("fabricated", "witness", "observer"),
        ("simulated", "accident", "incident"),
        ("synthetic", "diamond", "crystal"),
        ("fanciful", "creature", "animal"),
        ("illusory", "fortune", "wealth"),
        ("specious", "argument", "claim"),
        ("purported", "heir", "relative"),
    ],
}


def make_answer(mode):
    bits = "".join(str(x) for x in (DROP[mode], SWAP[mode], CONJ[mode]))
    return MODE_LETTER[mode] + bits


def _article(word):
    return "an" if word and word[0].lower() in "aeiou" else "a"


def build_instance(mode):
    adjective, noun, swap_noun = random.choice(LEXICON[mode])
    art = _article(noun)
    attrib = f"The {adjective} {noun} is {art} {noun}."
    pred = f"The {noun} is {adjective}."
    return {
        "mode": mode,
        "adjective": adjective,
        "noun": noun,
        "swap_noun": swap_noun,
        "attrib": attrib,
        "pred": pred,
    }


def render_prompt_text(insts):
    lines = [
        "Classify the adjective in each item and decide which inferences survive.",
        "For each of the following, the first sentence uses the adjective "
        "attributively (modifying the noun) and the second uses it predicatively "
        "(as a predicate of the noun).",
        "",
    ]
    for i, inst in enumerate(insts, 1):
        lines.append(f"Item {i}:")
        lines.append("  " + inst["attrib"])
        lines.append("  " + inst["pred"])
        lines.append("")
    lines.append(
        "For each item give the adjective's mode -- I (intersective), S (subsective), "
        "or P (privative) -- plus a 3-bit string encoding which of three inferences "
        "survive: (1) adjective drop (dropping the adjective still leaves a true "
        "statement), (2) noun swap (replacing the noun with a co-hypernym keeps the "
        "modified claim true), (3) conjunct split (the phrase splits into two "
        "independent predications). Answer each item as a single letter immediately "
        "followed by exactly three bits, e.g. I111. Answer the items one per line in "
        "order."
    )
    return "\n".join(lines)


def parse_answer(answer):
    if not isinstance(answer, str):
        return None
    answer = answer.strip()
    parts = [p.strip() for p in answer.replace("\n", " ").split() if p.strip()]
    out = []
    for p in parts:
        if len(p) == 4 and p[0] in "ISP" and all(c in "01" for c in p[1:]):
            out.append((p[0], p[1:]))
    return out


class AdjectiveInferenceModes(Task):
    summary = (
        "Three adjective modes (intersective, subsective, privative) rendered as "
        "attributive+predicative sentence pairs; report a mode letter I/S/P plus a "
        "3-bit string for which of adjective drop / noun swap / conjunct split "
        "inferences survive, for one or more items per example."
    )
    design_choice = (
        "Provide two short sentences per item, one using the adjective attributively "
        "and one predicatively, and require a single canonical letter (I/S/P) plus a "
        "3-bit string for inference survival."
    )
    config_cls = AdjectiveInferenceModesV2Config

    def generate_entry(self):
        n = max(1, self.config.n_instances)
        insts = [build_instance(random.choice(MODES)) for _ in range(n)]
        answers = [make_answer(inst["mode"]) for inst in insts]
        prompt = render_prompt_text(insts)
        metadata = {"instances": insts, "prompt": prompt}
        return Entry(metadata=metadata, answer=" ".join(answers))

    def render_prompt(self, metadata):
        return metadata["prompt"]

    def score_answer(self, answer, entry):
        instances = entry["metadata"]["instances"]
        parsed = parse_answer(answer)
        if parsed is None or len(parsed) != len(instances):
            return 0.0
        for (letter, bits), inst in zip(parsed, instances):
            if letter != MODE_LETTER[inst["mode"]]:
                return 0.0
            expected = "".join(str(x) for x in (DROP[inst["mode"]],
                                                SWAP[inst["mode"]],
                                                CONJ[inst["mode"]]))
            if bits != expected:
                return 0.0
        return 1.0

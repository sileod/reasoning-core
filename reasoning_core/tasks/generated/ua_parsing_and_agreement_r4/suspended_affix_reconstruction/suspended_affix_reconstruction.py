import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

PREFIXES = [
    "pre", "post", "anti", "pro", "re", "un", "in", "non", "sub", "super",
    "inter", "intra", "mid", "over", "under", "auto", "co", "counter",
    "extra", "micro", "multi", "neo", "omni", "out", "peri", "poly",
    "quasi", "semi", "ultra",
]

SUFFIXES = [
    "ness", "less", "ful", "ist", "ism", "ous", "ive", "able", "tion",
    "ment", "er", "or", "age", "al", "ic", "ial", "ian", "ity", "ize",
    "ship", "hood", "ward", "wise", "like", "ly", "fold", "scape", "dom",
]

STEMS = [
    "war", "wave", "school", "work", "heart", "mind", "body", "color",
    "sound", "light", "heat", "view", "bar", "well", "test", "race",
    "line", "period", "season", "sense", "form", "text", "hand", "kid",
    "adult", "city", "state", "land", "sea", "air", "fire", "star",
    "rock", "water", "wind", "night", "day", "sun", "moon", "cloud",
]


@dataclass
class SuspendedAffixConfig(Config):
    min_conjuncts: int = 2
    max_conjuncts: int = 2
    suffix_share_prob: float = 0.5

    def apply_difficulty(self, level):
        self.max_conjuncts = 2 + min(level, 3)
        self.suffix_share_prob = 0.3 + 0.1 * level


def _affixes(pool, n):
    return random.sample(pool, n)


def _canonical_answer(metadata):
    mode = metadata["mode"]
    stem = metadata["stem"]
    affixes = metadata["affixes"]
    if mode == "prefix":
        return " | ".join(a + stem for a in affixes)
    return " | ".join(stem + a for a in affixes)


def _surface(metadata):
    mode = metadata["mode"]
    stem = metadata["stem"]
    affixes = metadata["affixes"]
    if mode == "prefix":
        frags = [a + "-" for a in affixes[:-1]] + [affixes[-1] + "-" + stem]
    else:
        frags = [stem + "-" + affixes[0]] + ["-" + a for a in affixes[1:]]
    return " and ".join(frags)


class SuspendedAffixReconstruction(Task):
    summary = ("Recover omitted morphology in coordinated words where prefixes or suffixes "
               "take shared scope; vary nested coordination, affix compatibility and "
               "suspension boundaries; answers give each conjunct's full form.")
    design_choice = ("Each instance presents a bare coordinated stem list (e.g., 'pre- and "
                     "post-war') and the answer is the full expanded forms of all conjuncts "
                     "in fixed order.")
    config_cls = SuspendedAffixConfig

    def render_prompt(self, metadata):
        surface = _surface(metadata)
        return (
            "A coordinated phrase suspends a shared affix: a prefix or suffix that scopes "
            "over every conjunct is written once, and the conjunct stems are linked by "
            "hyphens. Recover the full expanded form of each conjunct: its own affix "
            "concatenated directly onto the shared stem, with no hyphen. List them in "
            "order, separated by ' | '. Phrase: " + surface
        )

    def generate_entry(self):
        cfg = self.config
        n = random.randint(cfg.min_conjuncts, cfg.max_conjuncts)
        prefix_share = random.random() < cfg.suffix_share_prob
        stem = random.choice(STEMS)
        if prefix_share:
            affixes = _affixes(PREFIXES, n)
            mode = "prefix"
        else:
            affixes = _affixes(SUFFIXES, n)
            mode = "suffix"
        assert len(set(affixes)) == len(affixes)
        metadata = {
            "mode": mode,
            "stem": stem,
            "affixes": affixes,
        }
        return Entry(metadata=metadata, answer=_canonical_answer(metadata))

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        gold = _canonical_answer(entry.metadata)
        return 1.0 if answer.strip() == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'suspended_affix_reconstruction (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_parsing_and_agreement_r4/suspended_affix_reconstruction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

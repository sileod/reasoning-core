import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'modifier_entailment_profiles (variant 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scope_and_binding_r4/modifier_entailment_profiles',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 382564971,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

# Fixed predicate lexicon. Base predicates a noun already entails; ORDER is the
# canonical answer ordering stated in the prompt.
BASE_PREDS = {"animate", "concrete", "material", "liquid", "container", "edible", "sharp"}
ORDER = ["animate", "concrete", "material", "liquid", "container", "edible", "sharp"]

# Denotation kinds for modifiers. Each modifier carries its predicate, its
# denotation family, and a scope flag.
#   intersective : the predicate must hold of the whole modified noun (default scope).
#   noun-relative: the predicate holds of the noun, but the modifier also lets an
#                  inner predicate pass through only if it also holds of an inner noun.
#   privative    : the predicate is negated: the modified thing entails its negation.
#   modal        : the predicate is only possible, not entailed: unsettled.
# Scope-sensitive ordering: a privative or modal modifier that wraps another modifier
# changes what the inner entailment becomes.

PRIVATIVE = {"dead", "fresh", "blank", "fake", "past", "former"}
MODAL = {"probably", "possibly", "allegedly", "likely"}
INTERSECTIVE = {
    "plastic", "metal", "wooden", "wool", "glass", "cement",
    "big", "red", "heavy", "tiny", "liquid", "glassy",
    "edible", "hollow", "bright", "cursed",
}

# Intresective modifiers each contribute one atomic base predicate, spanning
# the whole lexicon to widen the answer space.
ISP = {
    "plastic": "material", "metal": "material", "wooden": "material",
    "wool": "material", "glass": "material", "cement": "material",
    "big": "concrete", "red": "concrete", "heavy": "concrete",
    "tiny": "concrete", "liquid": "liquid", "glassy": "liquid",
    "edible": "edible", "hollow": "container", "bright": "sharp",
    "cursed": "animate",
}


def mode_for(mod):
    if mod in PRIVATIVE:
        return "privative"
    if mod in MODAL:
        return "modal"
    return "intersective"


def _sorted(answer_set):
    for p in ORDER:
        if p in answer_set:
            yield p


@dataclass
class ModifierProfilesConfig(Config):
    modifiers: int = 2
    max_privative: int = 1

    def apply_difficulty(self, level):
        self.modifiers = 2 + stochastic_rounding(self.modifiers // 1 + level % 3) % 3
        self.modifiers = 2 + (level % 3)
        self.modifiers = 2 + min(level, 3)
        self.max_privative = 1 + (level >= 3)


class ModifierEntailmentProfiles(Task):
    summary = "Compose noun modifiers with stated intersective, noun-relative, privative, and modal denotations; vary order-sensitive nesting and return the base predicates entailed, contradicted, or unsettled."
    design_choice = "Use a compositional grammar where modifier order determines scope, and the answer is a sorted list of atomic predicates in a fixed predicate lexicon, with unsettled cases omitted."
    config_cls = ModifierProfilesConfig

    def generate_entry(self):
        n = self.config.modifiers
        # Build a chain of modifiers.
        max_priv = self.config.max_privative
        for _ in range(200):
            chain = []
            for i in range(n):
                kind = random.random()
                if i == 0:
                    pool = INTERSECTIVE
                elif kind < 0.45:
                    pool = INTERSECTIVE
                elif kind < 0.75:
                    pool = MODAL
                else:
                    pool = PRIVATIVE
                chain.append(random.choice(sorted(pool)))
            if sum(1 for m in chain if mode_for(m) == "privative") <= max_priv:
                break
        else:
            chain = [random.choice(sorted(INTERSECTIVE)), random.choice(sorted(INTERSECTIVE))]

        noun_preds, contradicted, unsettled, entailed = self._eval(chain)
        answer_list = list(_sorted(entailed))
        if not answer_list:
            raise RuntimeError("unexpected empty entailment")
        answer = ",".join(answer_list)
        literal = " ".join(chain) + " " + "object"
        metadata = {
            "chain": chain,
            "phrase": literal,
            "entailed": sorted(entailed),
            "contradicted": sorted(contradicted),
            "unsettled": sorted(unsettled),
        }
        return Entry(metadata=metadata, answer=answer)

    def _eval(self, chain):
        noun_preds = set(random.sample(sorted(BASE_PREDS), random.randint(1, 4)))
        held = set(noun_preds)
        unsettled = set()
        for mod in reversed(chain):
            m = mode_for(mod)
            if m == "privative":
                held.clear()
            elif m == "modal":
                unsettled |= held
                held.clear()
        added = set()
        for idx, mod in enumerate(chain):
            if mode_for(mod) != "intersective":
                continue
            outer = chain[:idx]
            if any(mode_for(o) in ("privative", "modal") for o in outer):
                continue
            added.add(ISP[mod])
        held |= added
        contradicted = noun_preds - held
        return noun_preds, contradicted, unsettled, held

    def render_prompt(self, metadata):
        return (f"Each modifier has a stated denotation. 'dead', 'fresh', 'blank', "
                f"'fake', 'past', 'former' negate (privative). 'probably', 'possibly', "
                f"'allegedly', 'likely' make only possible (modal, unsettled). Other "
                f"modifiers add their property (intersective). Modifier order sets scope: "
                f"the LEFTmost modifier is outermost (widest scope); the modifier nearest "
                f"the noun is innermost (narrowest). Base predicates are: animate, concrete, "
                f"material, liquid, container, edible, sharp. A privative or modal at an outer "
                f"scope nullifies all inner modifiers and the noun's base predicates. "
                f"Given the phrase '{metadata['phrase']}', list the base predicates "
                f"ENTAILED. Omit contradicted and unsettled. Answer as comma-separated atoms "
                f"in the fixed order.")

    def score_answer(self, answer, entry):
        target = entry.answer
        norm = "".join(answer.split()).lower().replace("_", "")
        tnorm = "".join(target.split()).lower().replace("_", "")
        if norm == tnorm:
            return 1.0
        return 0.0


def _module_repr():
    return ModifierEntailmentProfiles

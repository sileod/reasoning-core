import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

FLAVORS = ("numeral", "some_all", "conjunction", "modal")

_ITEM_NOUNS = ["coins", "boxes", "seats", "parcels", "lights", "rooms", "gates", "tokens"]
_NUM_PRED = ["are red", "are open", "contain a prize", "are switched on",
             "hold a gem", "are occupied", "are damaged", "pass inspection"]
_QUANT_NOUNS = ["guests", "voters", "students", "members", "players", "officials"]
_QUANT_PRED = ["have arrived", "approved the motion", "passed the exam", "voted yes",
               "finished the race", "are present"]
_PROPOSITIONS = ["the mail arrived", "the store is open", "the project finished",
                 "the train is delayed", "the exam was cancelled", "the file saved",
                 "the signal reached base", "the order shipped"]
_PRED_NOUNS = ["model", "circuit", "block", "stage", "brand", "unit"]
_PRED_ADJS = ["reliable", "fast", "safe", "stable", "efficient", "compact"]
_SUBJ = ["speaker", "reporter", "operator", "expert", "manager", "analyst"]
_MODAL_NOUN = ["rain", "shipping", "the upgrade", "the repair", "the callback", "the deal"]
_MODAL_PRED = ["it rains", "the shipment arrives", "the upgrade ships", "the repair holds",
               "the callback happens", "the deal closes"]


@dataclass
class ScalarAlternativeExclusionV3Config(Config):
    min_n: int = 3
    max_n: int = 3

    def apply_difficulty(self, level):
        self.min_n = 3 + level
        self.max_n = 3 + level


def _labels_for(flavor, n):
    if flavor == "numeral":
        noun = random.choice(_ITEM_NOUNS)
        pred = random.choice(_NUM_PRED)
        return [f"at least {i} of the {n} {noun} {pred}" for i in range(1, n + 1)]
    if flavor == "some_all":
        noun = random.choice(_QUANT_NOUNS)
        pred = random.choice(_QUANT_PRED)
        return [f"at least {i} of the {n} {noun} {pred}" for i in range(1, n + 1)]
    if flavor == "conjunction":
        noun = random.choice(_PRED_NOUNS)
        adj = random.choice(_PRED_ADJS)
        pool = [f"{noun} {i} is {adj}" for i in range(1, n + 1)]
        labels = []
        for i in range(1, n + 1):
            labels.append(" and ".join(pool[:i]))
        return labels
    prop = random.choice(_PROPOSITIONS)
    return [f"it may be that {prop}", f"it must be that {prop}"]


def _parse_set(text):
    text = str(text).strip()
    if not text:
        return None
    parts = [p.strip() for p in text.split(",") if p.strip()]
    try:
        values = frozenset(int(p) for p in parts)
    except ValueError:
        return None
    return values if values else None


class ScalarAlternativeExclusion(Task):
    summary = ("Derive scalar implicatures over ordered scales (some/all, or/and, "
               "numerals, possibility modals): exclude stronger alternatives consistent "
               "with stated speaker knowledge; answer is the surviving alternative set.")
    config_cls = ScalarAlternativeExclusionV3Config

    def generate_entry(self):
        flavor = random.choice(FLAVORS)
        n = random.randint(self.config.min_n, self.config.max_n)
        if flavor == "modal":
            n = 2
        labels = _labels_for(flavor, n)
        subj = random.choice(_SUBJ)
        utterance = random.randint(1, n - 1)
        stronger = list(range(utterance + 1, n + 1))
        uncertain = [j for j in stronger if random.random() < 0.7]
        surviving = [i for i in range(1, n + 1) if i <= utterance or i in uncertain]
        answer = ",".join(str(i) for i in surviving)
        metadata = {
            "flavor": flavor,
            "labels": labels,
            "subj": subj,
            "utterance": utterance,
            "uncertain": uncertain,
            "surviving": surviving,
        }
        gold = [i for i in range(1, n + 1) if i <= utterance or i in uncertain]
        assert answer == ",".join(str(i) for i in gold), "surviving set mismatch"
        assert len(surviving) > 0, "surviving set must not be empty"
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        subj = metadata["subj"]
        lines = [
            "On an ordered scale the alternatives are listed from weakest to strongest, "
            "and each stronger alternative entails every weaker one.",
        ]
        for i, lab in enumerate(metadata["labels"], 1):
            lines.append(f"Alternative {i}: {lab}")
        lines.append(
            f"The {subj}, who is cooperative and fully competent, utters only this claim: "
            f"\"{metadata['labels'][metadata['utterance'] - 1]}\""
        )
        if metadata["uncertain"]:
            unc = ", ".join(f"alternative {j}" for j in metadata["uncertain"])
            lines.append(
                f"The {subj} is genuinely uncertain whether these stronger alternatives "
                f"hold: {unc}."
            )
        else:
            lines.append(f"The {subj} is certain about every stronger alternative.")
        lines.append(
            "By the scalar implicature, asserting a weaker alternative excludes every "
            "stronger alternative whose truth the speaker would know and be able to "
            "assert. An alternative the speaker is explicitly uncertain about is not "
            "thereby excluded and survives."
        )
        lines.append(
            "List the numbers of the alternatives that are NOT excluded, as a "
            "comma-separated list in increasing order (for example \"1,2\")."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = _parse_set(entry.answer)
        pred = _parse_set(answer)
        if gold is None or pred is None:
            return 0.0
        return 1.0 if gold == pred else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'scalar_alternative_exclusion (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scope_and_binding_r1/scalar_alternative_exclusion',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2639544549,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'nominal_compound_relation (variant 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_paraphrase_equivalence_r1/nominal_compound_relation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Present a list of candidate paraphrases; the answer is the subset of paraphrase indices whose relations match any reading, e.g., '[1,3]'"


PH = {
    "of": "composed of",
    "in": "contained in",
    "for": "intended for",
    "from": "derived from",
    "about": "about the topic of",
    "with": "containing",
    "by": "produced by",
    "at": "positioned at",
}
PREPS = list(PH.keys())
PHRASES = list(PH.values())


@dataclass
class NominalCompoundRelationV2Config(Config):
    compound_len: int = 2
    paraphrase_count: int = 4

    def apply_difficulty(self, level):
        self.compound_len = 2 if level <= 2 else 3
        self.paraphrase_count = 3 + min(level, 3)


class NominalCompoundRelation(Task):
    summary = ("Two- and three-noun compounds interpreted over a fixed inventory of modifier-head "
               "relations; enumerate bracketing and relation readings; answer whether a compound "
               "matches a given paraphrase or which paraphrases split its readings.")
    config_cls = NominalCompoundRelationV2Config
    design_choice = design_choice

    def generate_entry(self):
        config = self.config
        nouns = ["apple", "river", "stone", "glass", "story", "book", "forest",
                 "metal", "oil", "paper", "wood", "silk", "iron", "ice",
                 "garden", "city", "milk", "honey", "salt", "brick", "copper"]
        words = random.sample(nouns, config.compound_len)
        relations = random.sample(PREPS, config.compound_len - 1)

        pc = config.paraphrase_count
        k_matched = random.randint(1, (pc + 1) // 2)
        matched = sorted(random.sample(list(range(pc)), k_matched))
        distract_pool = [p for p in PREPS if p not in relations]
        if len(distract_pool) < pc - k_matched:
            distract_pool = [p for p in PREPS]
        distract = random.sample(distract_pool, pc - k_matched)

        paraphrase_preps = []
        di = 0
        for j in range(pc):
            if j in matched:
                paraphrase_preps.append(random.choice(relations))
            else:
                paraphrase_preps.append(distract[di])
                di += 1

        mod = words[0]
        head = words[-1]
        paraphrases = []
        for prep in paraphrase_preps:
            phrase = PH[prep]
            paraphrases.append(f"a {head} {phrase} a {mod}")

        answer = "[" + ", ".join(str(i) for i in matched) + "]"
        metadata = {
            "compound": list(words),
            "compound_preps": list(relations),
            "paraphrases": paraphrases,
            "paraphrase_preps": paraphrase_preps,
            "matched": list(matched),
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = ["A modifier-head compound joins a non-final modifier noun to a final head noun "
                 "through one relation from a fixed inventory. The inventory, by preposition, is: "
                 "of = composed of, in = contained in, for = intended for, from = derived from, "
                 "about = about the topic of, with = containing, by = produced by, at = positioned "
                 "at."]
        mod = metadata["compound"][0]
        head = metadata["compound"][-1]
        rel_texts = [PH[p] for p in metadata["compound_preps"]]
        comp_words = " ".join(metadata["compound"])
        joint = f"'{mod}' {rel_texts[0]} '{head}'"
        if len(rel_texts) == 2:
            lines.append(
                f"The compound '{comp_words}' carries two readings: {joint}, and "
                f"'{metadata['compound'][1]}' {rel_texts[1]} '{head}'.")
        else:
            lines.append(f"The compound '{comp_words}' reads as {joint}.")
        lines.append("Here are candidate paraphrases (index: paraphrase):")
        for j, p in enumerate(metadata["paraphrases"]):
            lines.append(f"{j}: {p}")
        lines.append("An index belongs in the answer iff its paraphrase expresses a relation the "
                     "compound carries. Give the set of indices, comma-separated inside brackets, "
                     "of every matching paraphrase, e.g. '[1,3]'. If none match, answer '[]'.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        try:
            parsed = _parse_indices(answer)
            gold = _parse_indices(entry.answer)
        except Exception:
            return 0.0
        return 1.0 if parsed == gold else 0.0


def _parse_indices(s):
    s = s.strip()
    if not (s.startswith("[") and s.endswith("]")):
        raise ValueError("not bracket-wrapped")
    inner = s[1:-1].strip()
    if not inner:
        return []
    return [int(part.strip()) for part in inner.split(",")]

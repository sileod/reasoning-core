import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'case_stacking_realization (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_parsing_and_agreement_r4/case_stacking_realization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_EXP = {
    "A": {"NOM": "na", "GEN": "an", "ERG": "sa", "ACC": "ma", "DAT": "ia"},
    "B": {"NOM": "ru", "GEN": "er", "ERG": "tu", "ACC": "vu", "DAT": "eu"},
    "C": {"NOM": "ci", "GEN": "og", "ERG": "ki", "ACC": "pi", "DAT": "au"},
}
_OWNCASES = ["NOM", "ERG", "ACC", "DAT"]
_CLASSES = ["A", "B", "C"]
_VOWELS = {"a", "e", "i", "o", "u"}
_TAIL_V = ["a", "e", "i"]
_TAIL_C = ["k", "s", "t"]


def _realized(own_case, own_class, tail, gen_classes):
    units = [_EXP[own_class][own_case]]
    for cls in gen_classes:
        units.append(_EXP[cls]["GEN"])
    out = ""
    prev = tail
    for u in units:
        if prev in _VOWELS and u[0] in _VOWELS:
            out += u[1:]
        elif prev not in _VOWELS and u[0] in _VOWELS:
            out += "j" + u
        else:
            out += u
        prev = u[-1]
    return out


@dataclass
class CaseStackingRealizationConfig(Config):
    max_possessors: int = 1

    def apply_difficulty(self, level):
        self.max_possessors = min(4, 1 + level)


class CaseStackingRealization(Task):
    summary = ("Realize stacked case on nested possessors and nominal modifiers "
               "under stated inheritance, boundary and suffix-fusion rules; answers "
               "give the ordered case exponents on a queried nominal.")
    design_choice = ("Vary the depth of the nominal stack from 1 to 4 possessors, "
                     "with the queried nominal placed at a random depth, requiring "
                     "the solver to track inheritance order across all levels.")
    config_cls = CaseStackingRealizationConfig

    def generate_entry(self):
        maxp = self.config.max_possessors
        d = random.randint(1, maxp)
        n = 1 + d
        j = random.randint(1, n)
        classes = [random.choice(_CLASSES) for _ in range(n)]
        own_class = classes[j - 1]
        own_case = random.choice(_OWNCASES)
        tail = random.choice(_TAIL_V + _TAIL_C)
        left_poss = list(classes[: j - 1])
        ans = _realized(own_case, own_class, tail, left_poss)

        assert isinstance(ans, str) and len(ans) >= 1, ans
        assert ans == _realized(own_case, own_class, tail, left_poss)

        metadata = {
            "n": int(n),
            "j": int(j),
            "classes": [str(c) for c in classes],
            "query_class": own_class,
            "query_case": own_case,
            "query_tail": tail,
        }
        return Entry(metadata=metadata, answer=ans)

    def render_prompt(self, metadata):
        n = int(metadata["n"])
        j = int(metadata["j"])
        classes = metadata["classes"]
        chain = ", ".join(f"N{k}:{classes[k - 1]}" for k in range(1, n + 1))
        pos_rel = ", ".join(
            f"N{k} possesses N{k + 1}" for k in range(1, n)
        )
        exp_lines = "\n".join(
            f"Class {c}: NOM={_EXP[c]['NOM']}, GEN={_EXP[c]['GEN']}, "
            f"ERG={_EXP[c]['ERG']}, ACC={_EXP[c]['ACC']}, DAT={_EXP[c]['DAT']}"
            for c in _CLASSES
        )
        return (
            "Consider a possessive chain where each nominal possesses the next one "
            f"({pos_rel}). Form a chain of N objects, each with a nominal class; "
            f"the chain classes are: {chain}.\n\n"
            "We ask about the suffix string realized on "
            f"N{j}, which has class {metadata['query_class']} and own clause case "
            f"{metadata['query_case']}, and whose stem ends in the "
            f"{'vowel' if metadata['query_tail'] in _VOWELS else 'consonant'} '{metadata['query_tail']}'.\n\n"
            "Case exponents by class:\n"
            f"{exp_lines}\n\n"
            "Inheritance: a nominal realizes, in left-to-right order, its own case "
            "exponent followed by the GEN exponent of every possessor to its left in "
            "the chain.\n"
            "Boundary & suffix-fusion: between adjacent units (the stem, then each "
            "stacked exponent), if the earlier unit ends in a vowel and the next "
            "exponent begins with a vowel, the next exponent's leading vowel is "
            "dropped; if the earlier unit ends in a consonant and the next exponent "
            "begins with a vowel, a linking 'j' is inserted; otherwise the next "
            "exponent attaches unchanged.\n\n"
            f"What suffix string is realized on N{j}? "
            "The answer is the concatenated suffix exponents only (for example 'maer' "
            "for a hypothetical ACC followed by two stacked GENs), not the stem."
        )


if __name__ == "__main__":
    t = CaseStackingRealization()
    ex = t.generate_example()
    print(ex.prompt)
    print("ANSWER:", ex.answer)

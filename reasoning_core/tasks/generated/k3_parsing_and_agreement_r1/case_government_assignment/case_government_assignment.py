import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

CASES = ["NOM", "ACC", "DAT", "GEN", "ABS", "ERG"]

SUBJ_NOUNS = ["weaver", "farmer", "juggler", "baker", "captain", "scout", "miner", "hunter"]
OBJ_NOUNS = ["bread", "stone", "vessel", "ticket", "mirror", "bundle", "lantern", "anchor"]
ANIM_OBJ = ["guest", "sentry", "bride", "herald", "ward", "envoy"]
IO_NOUNS = ["miller", "apprentice", "host", "courier", "servant"]
PLACE_NOUNS = ["harbor", "market", "shrine", "fort", "mill", "bridge"]

VERBS_TRANS = ["follows", "carries", "reveals", "fetches", "measures", "lifts", "buries", "holds"]
VERBS_QUIRKY_OBJ = ["needs", "grips", "spares", "flatters"]
VERBS_QUIRKY_SUBJ = ["pleases", "eludes", "exports", "invites"]
VERBS_DITRANS = ["gives", "sends", "offers", "passes", "lends", "feeds"]
VERBS_ERG = ["strikes", "opens", "shatters", "breaks"]

PREPS = [("toward", "GEN"), ("beside", "DAT"), ("inside", "ACC"), ("despite", "GEN"), ("above", "DAT")]


def _case_word(c):
    return {"NOM": "nominative", "ACC": "accusative", "DAT": "dative",
            "GEN": "genitive", "ABS": "absolutive", "ERG": "ergative"}[c]


def _quirk():
    return random.choice(["DAT", "GEN"])


def _f_intrans():
    subj = random.choice(SUBJ_NOUNS)
    verb = random.choice(VERBS_ERG)
    clause = f"the {subj} {verb}"
    rules = ["An intransitive verb assigns nominative to its sole argument (the subject)."]
    nps = [(f"the {subj}", "the subject")]
    return dict(clause=clause, rules=rules, nps=nps, cases=["NOM"])


def _f_intrans_quirky():
    subj = random.choice(SUBJ_NOUNS)
    verb = random.choice(VERBS_QUIRKY_SUBJ)
    q = _quirk()
    clause = f"the {subj} {verb}"
    rules = [f"The verb \"{verb}\" is quirky: it assigns {_case_word(q)} to its sole argument (the subject)."]
    nps = [(f"the {subj}", "the subject")]
    return dict(clause=clause, rules=rules, nps=nps, cases=[q])


def _f_trans():
    subj = random.choice(SUBJ_NOUNS)
    obj = random.choice(OBJ_NOUNS)
    verb = random.choice(VERBS_TRANS)
    clause = f"the {subj} {verb} the {obj}"
    rules = ["The subject of a finite transitive verb bears nominative case.",
             "A direct object of an accusative verb bears accusative case."]
    nps = [(f"the {subj}", "the subject"), (f"the {obj}", "the direct object")]
    return dict(clause=clause, rules=rules, nps=nps, cases=["NOM", "ACC"])


def _f_quirky_obj():
    subj = random.choice(SUBJ_NOUNS)
    obj = random.choice(OBJ_NOUNS)
    verb = random.choice(VERBS_QUIRKY_OBJ)
    q = _quirk()
    clause = f"the {subj} {verb} the {obj}"
    rules = ["The subject of a finite verb bears nominative case.",
             f"The verb \"{verb}\" takes an object bearing quirky {_case_word(q)} case."]
    nps = [(f"the {subj}", "the subject"), (f"the {obj}", "the direct object")]
    return dict(clause=clause, rules=rules, nps=nps, cases=["NOM", q])


def _f_quirky_subj():
    subj = random.choice(SUBJ_NOUNS)
    obj = random.choice(OBJ_NOUNS)
    verb = random.choice(VERBS_QUIRKY_SUBJ)
    q = _quirk()
    clause = f"the {subj} {verb} the {obj}"
    rules = [f"The verb \"{verb}\" is quirky: its subject bears {_case_word(q)} case.",
             "A direct object of such a verb bears accusative case."]
    nps = [(f"the {subj}", "the subject"), (f"the {obj}", "the direct object")]
    return dict(clause=clause, rules=rules, nps=nps, cases=[q, "ACC"])


def _f_ergative():
    subj = random.choice(SUBJ_NOUNS)
    obj = random.choice(OBJ_NOUNS)
    verb = random.choice(VERBS_ERG)
    clause = f"the {subj} {verb} the {obj}"
    rules = ["In perfective aspect this single transitive pattern is ergative.",
             "The transitive subject bears ergative case.",
             "The transitive object bears absolutive case."]
    nps = [(f"the {subj}", "the subject"), (f"the {obj}", "the direct object")]
    return dict(clause=clause, rules=rules, nps=nps, cases=["ERG", "ABS"])


def _f_dom():
    subj = random.choice(SUBJ_NOUNS)
    obj = random.choice(ANIM_OBJ)
    clause = f"the {subj} sees the {obj}"
    rules = ["The subject of a finite transitive verb bears nominative case.",
             "A direct object that is animate is differentially marked and bears dative case."]
    nps = [(f"the {subj}", "the subject"), (f"the {obj}", "the animate direct object")]
    return dict(clause=clause, rules=rules, nps=nps, cases=["NOM", "DAT"])


def _f_ditrans():
    subj = random.choice(SUBJ_NOUNS)
    io = random.choice(IO_NOUNS)
    obj = random.choice(OBJ_NOUNS)
    verb = random.choice(VERBS_DITRANS)
    clause = f"the {subj} {verb} the {obj} to the {io}"
    rules = ["The subject of a finite verb bears nominative case.",
             "A direct object bears accusative case.",
             "An indirect object bears dative case."]
    nps = [(f"the {subj}", "the subject"), (f"the {obj}", "the direct object"),
           (f"the {io}", "the indirect object")]
    return dict(clause=clause, rules=rules, nps=nps, cases=["NOM", "ACC", "DAT"])


def _f_adpos():
    subj = random.choice(SUBJ_NOUNS)
    obj = random.choice(OBJ_NOUNS)
    verb = random.choice(VERBS_TRANS)
    prep, pc = random.choice(PREPS)
    place = random.choice(PLACE_NOUNS)
    clause = f"the {subj} {verb} the {obj} {prep} the {place}"
    rules = ["The subject of a finite transitive verb bears nominative case.",
             "A direct object bears accusative case.",
             f"The preposition \"{prep}\" governs {_case_word(pc)} on its object."]
    nps = [(f"the {subj}", "the subject"), (f"the {obj}", "the direct object"),
           (f"the {place}", f"the object of \"{prep}\"")]
    return dict(clause=clause, rules=rules, nps=nps, cases=["NOM", "ACC", pc])


def _f_quirky_ditrans():
    subj = random.choice(SUBJ_NOUNS)
    io = random.choice(IO_NOUNS)
    obj = random.choice(OBJ_NOUNS)
    verb = random.choice(VERBS_QUIRKY_OBJ)
    q = _quirk()
    clause = f"the {subj} {verb} the {obj} to the {io}"
    rules = [f"The verb \"{verb}\" is quirky: its subject bears {_case_word(q)} case.",
             "A direct object bears accusative case.",
             "An indirect object bears dative case."]
    nps = [(f"the {subj}", "the subject"), (f"the {obj}", "the direct object"),
           (f"the {io}", "the indirect object")]
    return dict(clause=clause, rules=rules, nps=nps, cases=[q, "ACC", "DAT"])


def _f_adpos_ditrans():
    subj = random.choice(SUBJ_NOUNS)
    io = random.choice(IO_NOUNS)
    obj = random.choice(OBJ_NOUNS)
    verb = random.choice(VERBS_DITRANS)
    prep, pc = random.choice(PREPS)
    place = random.choice(PLACE_NOUNS)
    clause = f"the {subj} {verb} the {obj} to the {io} {prep} the {place}"
    rules = ["The subject of a finite verb bears nominative case.",
             "A direct object bears accusative case.",
             "An indirect object bears dative case.",
             f"The preposition \"{prep}\" governs {_case_word(pc)} on its object."]
    nps = [(f"the {subj}", "the subject"), (f"the {obj}", "the direct object"),
           (f"the {io}", "the indirect object"), (f"the {place}", f"the object of \"{prep}\"")]
    return dict(clause=clause, rules=rules, nps=nps, cases=["NOM", "ACC", "DAT", pc])


FRAMES = {
    1: [_f_intrans, _f_intrans_quirky],
    2: [_f_trans, _f_quirky_obj, _f_quirky_subj, _f_ergative, _f_dom],
    3: [_f_ditrans, _f_adpos, _f_quirky_ditrans],
    4: [_f_adpos_ditrans],
}


def _wrong_case(correct):
    pool = [c for c in CASES if c != correct]
    return random.choice(pool)


@dataclass
class CaseConfig(Config):
    level: int = 0
    seed: int = None
    np_count: int = 1

    def apply_difficulty(self, level):
        self.np_count = min(4, 1 + (level + 1) // 2)


class CaseGovernmentAssignment(Task):
    summary = ("Select the single correct full case assignment for nominals from lexical frames "
               "and clause structure: structural nominative/accusative, quirky subject/object case, "
               "ditransitive datives, adposition government, aspect-split ergativity, differential "
               "object marking; the answer is the letter of the one correct candidate among "
               "distractors that differ in a single NP's case.")
    design_choice = ("Instances present a clause plus a set of candidate case assignments (one per "
                     "NP), and the solver must select the single correct assignment from a small set "
                     "of alternatives, with distractors differing in one NP's case.")
    config_cls = CaseConfig
    task_version = 2

    def generate_entry(self):
        np_count = self.config.np_count
        frame = random.choice(FRAMES[np_count])()
        correct = list(frame["cases"])

        distractors = []
        for j in range(len(correct)):
            d = list(correct)
            d[j] = _wrong_case(correct[j])
            distractors.append(d)

        candidates = [list(correct)] + [list(d) for d in distractors]
        random.shuffle(candidates)

        ctuple = tuple(correct)
        for c in candidates:
            diffs = sum(1 for a, b in zip(c, correct) if a != b)
            assert (diffs == 0) == (c == list(correct))
        assert candidates.count(list(correct)) == 1

        idx = next(i for i, c in enumerate(candidates) if tuple(c) == ctuple)
        letter = chr(ord("A") + idx)

        metadata = {
            "clause": frame["clause"],
            "rules": frame["rules"],
            "nps": [list(x) for x in frame["nps"]],
            "cases": correct,
            "candidates": candidates,
            "n_candidates": len(candidates),
        }
        return Entry(metadata=metadata, answer=letter)

    def render_prompt(self, metadata):
        lines = ["In this constructed language, assign grammatical case to each noun phrase.",
                 "",
                 f"Clause:  {metadata['clause']}",
                 "",
                 "Grammar notes (the rules that fix the cases):"]
        for r in metadata["rules"]:
            lines.append(f"  \u2022 {r}")
        lines.append("")
        lines.append("Arguments, each taking exactly one case:")
        for i, (ph, role) in enumerate(metadata["nps"], 1):
            lines.append(f"  {i}. \"{ph}\" \u2014 {role}")
        lines.append("")
        lines.append("Candidate assignments, each listing one case per argument in the order above:")
        for l, cand in zip("ABCDEFGH", metadata["candidates"]):
            lines.append(f"  {l}. {', '.join(cand)}")
        last = chr(ord("A") + metadata["n_candidates"] - 1)
        lines.append("")
        lines.append(f"Which candidate (A\u2013{last}) assigns the correct case to every argument? "
                     "Answer with the single letter.")
        return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'case_government_assignment (draw 2 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_parsing_and_agreement_r1/case_government_assignment',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 525660630,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

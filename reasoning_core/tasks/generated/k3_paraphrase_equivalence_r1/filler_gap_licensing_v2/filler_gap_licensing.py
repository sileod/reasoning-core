import random

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'filler_gap_licensing (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_paraphrase_equivalence_r1/filler_gap_licensing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
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


# ---------------------------------------------------------------------------
# Closed vocabularies (kept small so every rendered sentence is grammatical)
# ---------------------------------------------------------------------------
OBJECTS = ["report", "memo", "budget", "contract", "invoice", "agenda"]
MATRIX_SUBJ = ["the analyst", "the auditor", "the counsel", "the intern",
               "the manager", "the deputy"]
EMBED_SUBJ = ["the clerk", "the deputy", "the counsel", "the intern"]
TRANS_VERB = ["review", "file", "read", "retain", "archive", "sign"]
EMBED_VERB = ["reviewed", "scrutinized", "endorsed", "sketched"]
CNP_HEAD = ["the claim", "the rumor", "the fact", "the idea"]
CNP_VERB = ["reject", "dismiss", "challenge", "deny"]
INTRANS_VERB = ["resign", "withdraw", "depart", "recuse", "abstain"]
CSC_OTHER = ["the invoice", "the agenda", "the notice", "the dossier"]

ISLAND_LABEL = {
    "cnpc": "complex NP island",
    "subject": "subject island",
    "adjunct": "adjunct island",
    "wh": "wh-island",
    "csc": "coordinate structure constraint",
}


def _fillers(n):
    return ["which " + o for o in random.sample(OBJECTS, n)]


def _clean(fillers):
    f, subj, verb = fillers[0], random.choice(MATRIX_SUBJ), random.choice(TRANS_VERB)
    return ("%s did %s %s?" % (f, subj, verb)), "linked", [f]


def _cnpc(fillers):
    f, subj = fillers[0], random.choice(MATRIX_SUBJ)
    head, verb = random.choice(CNP_HEAD), random.choice(CNP_VERB)
    esubj, everb = random.choice(EMBED_SUBJ), random.choice(EMBED_VERB)
    return ("%s did %s %s %s that %s %s?" % (f, subj, verb, head, esubj, everb)), "island", ["cnpc"]


def _subject(fillers):
    f = fillers[0]
    esubj, everb, msubj = random.choice(EMBED_SUBJ), random.choice(EMBED_VERB), random.choice(MATRIX_SUBJ)
    return ("%s did the claim that %s %s surprise %s?" % (f, esubj, everb, msubj)), "island", ["subject"]


def _adjunct(fillers):
    f, subj = fillers[0], random.choice(MATRIX_SUBJ)
    esubj, everb, iverb = random.choice(EMBED_SUBJ), random.choice(EMBED_VERB), random.choice(INTRANS_VERB)
    return ("%s did %s %s because %s %s?" % (f, subj, iverb, esubj, everb)), "island", ["adjunct"]


def _wh(fillers):
    f, subj = fillers[0], random.choice(MATRIX_SUBJ)
    esubj, everb, wverb = random.choice(EMBED_SUBJ), random.choice(EMBED_VERB), random.choice(["wonder", "inquire", "ask"])
    return ("%s did %s %s whether %s %s?" % (f, subj, wverb, esubj, everb)), "island", ["wh"]


def _csc(fillers):
    f = fillers[0]
    other = random.choice(CSC_OTHER)
    return ("%s did the analyst review and then catalog %s?" % (f, other)), "island", ["csc"]


def _parasitic(fillers):
    f = fillers[0]
    return ("%s did the analyst file without reviewing?" % f), "licensed", [f]


def _multi(fillers):
    f1, f2 = fillers[0], fillers[1]
    s1, s2 = random.choice(MATRIX_SUBJ), random.choice(MATRIX_SUBJ)
    v1, v2 = random.choice(TRANS_VERB), random.choice(TRANS_VERB)
    while s1 == s2:
        s2 = random.choice(MATRIX_SUBJ)
    return ("%s did %s %s, and %s did %s %s?" % (f1, s1, v1, f2, s2, v2)), "linked", [f1, f2]


_GEN = {
    "clean": _clean,
    "cnpc": _cnpc,
    "subject": _subject,
    "adjunct": _adjunct,
    "wh": _wh,
    "csc": _csc,
    "parasitic": _parasitic,
    "multi": _multi,
}


class FillerGapLicensingV2Config(Config):
    n_fillers: int = 1
    allow_multi: bool = False
    allow_parasitic: bool = False
    island_types: int = 5

    def apply_difficulty(self, level):
        self.allow_multi = level >= 2
        self.allow_parasitic = level >= 4
        self.island_types = 1 + level if level < 5 else 5


class FillerGapLicensingV2Task(Task):
    task_name = "filler_gap_licensing_v2"
    summary = "Trace filler-gap dependencies: judge extractions across complex-NP, subject, adjunct, wh-, and coordinate islands, order multiple fillers by superiority, license parasitic gaps; answer the verdict and violated constraint."
    design_choice = "Present a sentence containing multiple wh-fillers and gaps, requiring the solver to output the ordered list of fillers that can be successfully linked, and the specific island constraint violated if any."
    config_cls = FillerGapLicensingV2Config

    def generate_entry(self):
        cfg = self.config
        fillers = _fillers(cfg.n_fillers)

        viable = ["clean", "cnpc", "subject", "adjunct", "wh", "csc"]
        if cfg.allow_multi and cfg.n_fillers >= 2:
            viable.append("multi")
        if cfg.allow_parasitic and cfg.n_fillers >= 1:
            viable.append("parasitic")

        ctype = random.choice(viable)
        if ctype in ("clean", "multi", "parasitic"):
            label = "noisland"
        else:
            label = "island"

        sentence, verdict, items = _GEN[ctype](fillers)

        if verdict == "island":
            constraint = ISLAND_LABEL[items[0]]
            answer = "island: " + constraint
        elif verdict == "licensed":
            answer = "licensed: " + items[0]
        else:
            answer = "linked: " + "; ".join(items)

        metadata = {
            "fillers": fillers,
            "case": ctype,
            "verdict": verdict,
            "answer": answer,
            "prompt": sentence,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return ("For each wh-phrase, decide whether its gap can be extracted across "
                "the surrounding structure. With multiple wh-phrases, order the "
                "successfully linked fillers by superiority (left to right). If an "
                "extraction is blocked, name the violated island constraint. "
                "Answer in the form 'linked: <filler>; <filler>; ...' or "
                "'island: <constraint>' or 'licensed: <filler>'. "
                "Given the question: %s" % metadata["prompt"])

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        if answer.strip().lower() == entry.answer.strip().lower():
            return 1.0
        return 0.0

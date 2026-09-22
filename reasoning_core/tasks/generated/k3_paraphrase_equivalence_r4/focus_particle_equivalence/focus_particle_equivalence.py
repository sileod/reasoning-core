import random

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'focus_particle_equivalence (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_paraphrase_equivalence_r4/focus_particle_equivalence',
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


PEOPLE = ["Ada", "Bo", "Cy", "Dee", "Ed", "Flo", "Gus", "Ida", "Jun"]
# (base verb phrase, past verb phrase)
PREDS = [("come to the meeting", "came to the meeting"),
         ("submit the form", "submitted the form"),
         ("pass the exam", "passed the exam"),
         ("attend the workshop", "attended the workshop"),
         ("sign the petition", "signed the petition"),
         ("finish the puzzle", "finished the puzzle")]


def _names(n):
    return random.sample(PEOPLE, n)


def _fmt(kind):
    return {"only": "Only %s %s",
            "cleft": "It is %s who %s",
            "pseudo": "The ones who %s are %s",
            "even": "Even %s %s",
            "also": "%s also %s",
            "negonly": "Only %s did not %s",
            "negpseudo": "The ones who did not %s are %s",
            "except": "Everyone except %s %s"}[kind]# (forced-present set, excluded set) encoding a form's truth conditions over
# the domain A, relative to the focal set F.
def _semantics(kind, F, A):
    Fs = set(F)
    As = set(A)
    if kind in ("only", "cleft", "pseudo"):
        return (frozenset(Fs), frozenset(As - Fs))
    if kind in ("negonly", "negpseudo", "except"):
        return (frozenset(As - Fs), frozenset(Fs))
    return (frozenset({next(iter(Fs))}), frozenset())


def _indiv(listed):
    return " and ".join(listed) if len(listed) > 1 else listed[0]


def build_versions(A, pred_base, pred_past):
    kind_pool = ["only", "cleft", "pseudo", "even", "also",
                 "negonly", "negpseudo", "except"]
    selected = random.sample(kind_pool, 5)
    F = random.sample(A, random.choice([1, 1, 2]))
    versions = []
    for kind in selected:
        if kind in ("even", "also"):
            f = [random.choice(F)]
        else:
            f = list(F)
        target = _indiv(f)
        if kind in ("negonly",):
            sentence = _fmt(kind) % (target, pred_base)
        elif kind == "negpseudo":
            sentence = _fmt(kind) % (pred_base, target)
        elif kind == "pseudo":
            sentence = _fmt(kind) % (pred_past, target)
        else:
            sentence = _fmt(kind) % (target, pred_past)
        versions.append((kind, sentence, _semantics(kind, f, A)))
    return versions


class FocusParticleEquivalenceV1Config(Config):
    n_people: int = 5

    def apply_difficulty(self, level):
        self.n_people = 5 + (level if level < 3 else 3)


class FocusParticleEquivalence(Task):
    task_name = "focus_particle_equivalence"
    summary = "Focus particles (only, even, also) in shifted positions plus clefts and pseudo-clefts, evaluated over a given situation model; compute each form's excluded alternatives; answer which versions are truth-conditionally identical."
    design_choice = "Answer as a canonical set of version indices whose truth conditions match the reference version, e.g., \"1,3,4\""
    config_cls = FocusParticleEquivalenceV1Config

    def generate_entry(self):
        A = _names(self.config.n_people)
        pred_base, pred_past = random.choice(PREDS)
        versions = build_versions(A, pred_base, pred_past)
        ref = versions[0][2]
        matching = [str(i + 1) for i, v in enumerate(versions) if v[2] == ref]
        answer = ",".join(matching)
        metadata = {
            "domain": A,
            "predicate": pred_past,
            "sentences": [v[1] for v in versions],
            "semantics": [[sorted(r), sorted(e)] for (r, e) in [v[2] for v in versions]],
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = [
            "Situation model: a set of people {%s} and the property '%s'."
            % (", ".join(metadata["domain"]), metadata["predicate"]),
            ("Each version below asserts something about who has the property. "
             "For focus-particle and cleft constructions, work out, for the "
             "focused constituent, which alternatives the form EXCLUDES (forces "
             "to lack the property) and which it forces to have the property. "
             "Two versions are truth-conditionally identical exactly when they "
             "force the same excluded alternatives and the same present "
             "alternatives."),
        ]
        for i, s in enumerate(metadata["sentences"], 1):
            lines.append("%d. %s" % (i, s))
        lines.append(
            "Version 1 is the reference. List, in increasing order and separated "
            "by commas (always including version 1 itself), every version whose "
            "truth conditions are identical to version 1's.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        gold = entry.answer
        if "".join(answer.split()) == gold:
            return 1.0
        try:
            gotset = set(int(x) for x in answer.split(",") if x.strip())
        except ValueError:
            return 0.0
        goldset = set(int(x) for x in gold.split(","))
        if not gotset:
            return 0.0
        return 1.0 if gotset == goldset else 0.0

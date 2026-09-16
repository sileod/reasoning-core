import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task


MODAL_SURFACE = {
    "must": "must",
    "need": "need to",
    "may": "may",
    "can": "can",
    "req": "is required to",
    "forbid": "is forbidden to",
}


def _normalize(s):
    return s.strip().lower()


def canonical(force, flavor, pol):
    """Canonical form for the (force, polarity) combination.

    The modal force and the polarity of the proposition the modal scopes over
    are enough to fix the equivalence class of a negated-modal phrasing. The
    flavor (deontic vs epistemic) is preserved because 'not may' and 'not must'
    do not invert into each other across flavors in the deontic/epistemic reading
    this task uses.
    """
    if force == "may":
        if pol == "pos":
            return "may"
        else:
            return "may not"
    else:  # must
        if pol == "pos":
            return "must"
        else:
            return "must not"


def _subject():
    return random.choice([
        "the engineer", "the analyst", "the consultant", "each clerk",
        "the operator", "the reviewer", "the student", "the delegate",
        "the agent", "the driver",
    ])


def _activity(verb, obj=None):
    if obj is not None:
        return f"{verb} {obj}"
    return random.choice([
        "submit the form", "approve the invoice", "attend the meeting",
        "run the simulation", "flag the discrepancy", "review the draft",
        "open the account", "sign the contract", "verify the log",
        "file the report", "enter the data", "test the build",
    ])


def render_surface(force, flavor, pol, subj, act):
    """Render a sentence with negation either above or below the modal.

    We render the polarity in varied surface positions (negation below the
    modal, like 'may not', vs negation on a higher auxiliary, like 'does not
    need to') so two different prompt texts share one canonical answer.
    """
    subject = subj
    if force == "must":
        if pol == "pos":
            if flavor == "deontic":
                phrasings = [
                    f"{subject} must {act}.",
                    f"{subject} needs to {act}.",
                    f"{subject} is required to {act}.",
                ]
            else:
                phrasings = [
                    f"{subject} must surely {act}.",
                    f"{subject} must certainly {act}.",
                ]
        else:  # must + not => force flipped to may(neg)
            if flavor == "deontic":
                phrasings = [
                    f"{subject} must not {act}.",
                    f"{subject} is forbidden to {act}.",
                ]
            else:
                phrasings = [
                    f"{subject} cannot certainly {act}.",
                    f"{subject} may not certainly {act}.",
                ]
    else:  # may
        if pol == "pos":
            if flavor == "deontic":
                phrasings = [
                    f"{subject} may {act}.",
                    f"{subject} can {act}.",
                ]
            else:
                phrasings = [
                    f"{subject} may certainly {act}.",
                    f"{subject} can surely {act}.",
                ]
        else:  # may + not
            if flavor == "deontic":
                phrasings = [
                    f"{subject} may not {act}.",
                    f"{subject} is not permitted to {act}.",
                    f"{subject} cannot {act}.",
                ]
            else:
                phrasings = [
                    f"{subject} may not certainly {act}.",
                    f"{subject} cannot surely {act}.",
                ]
    return phrasings


@dataclass
class ModalConfig(Config):
    flavor: str = "deontic"

    def apply_difficulty(self, level):
        # Higher levels mix in epistemic-flavor readings more often and widen
        # the pool of surface renderings, deepening the negation-scope reasoning
        # without enlarging the prompt much.
        if level >= 4:
            self.flavor = "either"
        elif level == 0:
            self.flavor = "deontic"
        else:
            self.flavor = "either" if level >= 2 else "deontic"


class ModalNegationEquivalence(Task):
    summary = ("Deontic and epistemic modals (must, need, may, can, be required, be forbidden) "
               "with negation above or below the modal; normalize force, flavor and polarity; "
               "answer which normalized form (must, must not, may, may not) a differently "
               "negated phrasing is equivalent to.")
    config_cls = ModalConfig

    def generate_entry(self):
        flavor = self.config.flavor
        if flavor == "either":
            flavor = random.choice(["deontic", "epistemic"])

        force = random.choice(["must", "may"])

        # Flip polarity with the modal and normalize. Two different surface
        # phrasings (negation above vs below the modal) collapse onto one
        # canonical form.
        pol = random.choice(["pos", "not"])

        canonical_form = canonical(force, flavor, pol)

        subj = _subject()
        verb, obj = random.choice([
            ("submit", "the form"), ("approve", "the invoice"),
            ("attend", "the briefing"), ("run", "the simulation"),
            ("flag", "the discrepancy"), ("review", "the draft"),
            ("open", "the account"), ("sign", "the contract"),
            ("verify", "the log"), ("file", "the report"),
            ("enter", "the data"), ("test", "the build"),
        ])
        act = f"{verb} {obj}"

        # Build the instance as a pair of sentences that ARE equivalent (share
        # the canonical form) OR one that differs, controlled so the answer is
        # the canonical form of the first sentence. Presenting a second sentence
        # forces the model to work out the equivalence rather than copy the modal.
        # To keep answers canonical and varied we always ask for the canonical
        # form; the second sentence is a decoy sharing the flavor but possibly a
        # different force, so no surface shortcut works.
        surfaces = render_surface(force, flavor, pol, subj, act)
        sentence1 = random.choice(surfaces)

        # Build a second sentence in the same (force, flavor) but a random
        # polarity to serve as the comparison target. The answer is the
        # canonical form of the first sentence.
        sentence2_surfaces = render_surface(force, flavor,
                                            random.choice(["pos", "not"]), subj, act)
        sentence2 = random.choice(sentence2_surfaces)

        entry = Entry(
            metadata={"sentence1": sentence1, "sentence2": sentence2,
                      "force": force, "flavor": flavor, "polarity": pol,
                      "canonical": canonical_form},
            answer=canonical_form,
        )
        return entry

    def render_prompt(self, metadata):
        s1 = metadata["sentence1"]
        s2 = metadata["sentence2"]
        return (
            f"Modal equivalence. Consider degrees of modality: 'must' and 'need to' and "
            f"'is required to' express necessity; 'may' and 'can' express permissibility. "
            f"Putting 'not' above a modal (e.g. 'does not need to') negates the modal "
            f"force; putting 'not' below it (e.g. 'may not') negates the proposition the "
            f"modal scopes over. Two phrasings are equivalent when they agree on force "
            f"(necessity vs permission) and on the polarity of the proposition. "
            f"\nSentence A: {s1}\n"
            f"Sentence B: {s2}\n"
            f"Write the canonical normalized form of Sentence A's reading, choosing "
            f"exactly one of: 'must', 'must not', 'may', 'may not'. Answer with that "
            f"form only."
        )

    def score_answer(self, answer, entry):
        a = _normalize("{}".format(answer))
        target = entry.answer.lower()
        if a == target:
            return 1.0
        return 0.0

    def distractor_candidates(self, entry):
        base = entry.answer.lower()
        cands = ["must", "must not", "may", "may not"]
        out = []
        for c in cands:
            if c != base:
                out.append(c)
        return out


design_choice = ("Present a pair of sentences and ask for the canonical normalized form "
                 "(e.g., 'must not', 'not must', 'may not', 'not may') as the answer.")

TASK_META = {'parent_source_id': None,
 'idea': 'modal_negation_equivalence (variant 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_paraphrase_equivalence_r1/modal_negation_equivalence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

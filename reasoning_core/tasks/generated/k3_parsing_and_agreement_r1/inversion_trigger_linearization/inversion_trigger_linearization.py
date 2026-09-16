import random

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'inversion_trigger_linearization (draw 2 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_parsing_and_agreement_r1/inversion_trigger_linearization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1705404348,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class InversionTriggerLinearizationV2Config(Config):
    dense: float = 0.5
    heavy: float = 0.2

    def apply_difficulty(self, level):
        self.dense = min(0.5 + 0.08 * level, 0.9)
        self.heavy = min(0.2 + 0.1 * level, 0.8)


SUBJ = ["the chef", "the doctor", "the engineer", "the gardener", "the lawyer",
        "the pilot", "the professor", "the sergeant", "the student", "the tailor"]


def _verbs():
    return ["sees", "reads", "writes", "fixes", "draws", "opens", "builds",
            "cooks", "paints", "sings", "tests", "moves"]


def _objects():
    return ["the report", "the window", "the manuscript", "the engine",
            "the diagram", "the letter", "the garden", "the hallway",
            "the kitchen", "the bridge"]


class InversionTriggerLinearization(Task):
    summary = ("Reserialize clauses around order triggers: fronted negatives "
               "and only/so-phrases with auxiliary inversion and do-support, "
               "verb-second after topicalization, extraposition of heavy "
               "phrases; answer the resulting sentence.")
    design_choice = ("Provide a topicalized object with verb-second inversion "
                     "and ask for the full reordered sentence, where the answer "
                     "is the base SVO order with the topic moved to subject "
                     "position.")
    config_cls = InversionTriggerLinearizationV2Config

    def generate_entry(self):
        cfg = self.config
        verb_inflected = random.choice(_verbs())
        bare = verb_inflected.rstrip("s")
        subject = random.choice(SUBJ)
        obj = random.choice(_objects())

        topicalized = f"Only {obj} does {subject} {bare}."
        base = f"{subject} {verb_inflected} {obj}."

        return Entry(metadata={
            "subject": subject,
            "verb": verb_inflected,
            "object": obj,
            "topicalized": topicalized,
            "base": base,
        }, answer=base)

    def render_prompt(self, metadata):
        return (
            f"Rewrite the following sentence into its natural base SVO "
            f"word order (subject, then verb, then object), with no "
            f"inversion and no fronted topic:\n\n"
            f"{metadata['topicalized']}\n\n"
            f"Answer with the full reordered sentence."
        )

    def score_answer(self, answer, entry):
        return 1.0 if answer == entry.answer else 0.0

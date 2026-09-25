import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'switch_reference_chains (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_parsing_and_agreement_r4/switch_reference_chains',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class SwitchRefConfig(Config):
    n_clauses: int = 3
    n_entities: int = 2

    def apply_difficulty(self, level):
        self.n_clauses = 3 + int(stochastic_rounding(level))
        self.n_entities = 2


NAMES = ["Alice", "Ben", "Cora", "Dan", "Eve", "Finn"]
VERBS = [
    "forgot the tickets", "packed a bag", "closed the door",
    "left the keys", "locked the window", "bought a snack",
]


class SwitchReferenceChains(Task):
    summary = "Assign same-subject or different-subject linkers across clause chains with omitted subjects, coordinated subjects and designated comparison pivots; answers give the linker sequence."
    design_choice = "Use either a fixed set of 3 pronouns (he/she/it) or 2 names per chain, forcing subject-tracking without lexical overlap."
    config_cls = SwitchRefConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n_clauses
        ne = self.config.n_entities
        chains = [(random.randrange(ne), random.randrange(ne)) for _ in range(n)]
        chain_names = random.sample(NAMES, ne)
        verbs = [random.choice(VERBS) for _ in range(n)]
        answer = compute_answer(chains)
        metadata = {
            "n_clauses": n,
            "n_entities": ne,
            "entities": chain_names,
            "clause_roles": [
                {"subject": chain_names[s], "verb": verbs[i]}
                for i, (s, o) in enumerate(chains)
            ],
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        a, b = metadata["entities"]
        roles = metadata["clause_roles"]
        body = "; ".join([f"{r['subject']} {r['verb']}" for r in roles]) + "."
        n_gaps = len(roles) - 1
        return (
            f"A short story about {a} and {b} is written in a style, common in many "
            f"languages, where predicate subjects are omitted and a linker marks whether "
            f"each clause's subject is the same person as the previous clause's subject "
            f"('same-subject') or a different person ('different-subject'). You must "
            f"recover those linkers. Note that the very first clause names its subject "
            f"explicitly.\n\n"
            f"Story: {body}\n\n"
            f"Give the {n_gaps} linkers as a comma-separated list in story order, one "
            f"for each clause after the first, using only the words same-subject or "
            f"different-subject. Example (for two gaps): different-subject,same-subject"
        )

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer == gold else 0.0


def compute_answer(chains):
    seq = []
    for i in range(1, len(chains)):
        pre_s, _ = chains[i - 1]
        cur_s, _ = chains[i]
        seq.append("same-subject" if cur_s == pre_s else "different-subject")
    return ",".join(seq)

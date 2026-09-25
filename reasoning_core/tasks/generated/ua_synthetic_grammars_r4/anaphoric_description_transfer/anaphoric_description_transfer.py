import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'anaphoric_description_transfer (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_synthetic_grammars_r4/anaphoric_description_transfer',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class AnaphoricDescriptionTransferConfig(Config):
    n_entities: int = 6
    chain_len: int = 1

    def apply_difficulty(self, level):
        self.n_entities = 5 + level
        self.chain_len = 1 + (level >= 2) + (level >= 5)


_RELATIONS = [
    ("owner", "owns"),
    ("manager", "manages"),
    ("supervisor", "supervises"),
    ("landlord", "lets to"),
    ("guardian", "guards"),
    ("trainer", "trains"),
    ("mechanic", "services"),
]

_NAMES = [
    "Ada", "Ben", "Chris", "Dana", "Eli", "Faye", "Gina", "Hank",
    "Iris", "Jude", "Kara", "Leo", "Mina", "Noah", "Owen", "Paula",
    "Quinn", "Rex", "Sara", "Tom", "Uma", "Vera", "Walt", "Xena",
    "Yuri", "Zoe",
]


def resolve_chain(universe, rels, binder):
    """Apply the chain to a binder. 'rels' is ordered deepest-first: the
    first relation is applied to the binder, the last yields the denotation
    (mirroring 'the owner of the paycheck of the manager')."""
    cur = binder
    for rel in rels:
        mapping = universe.get(cur)
        if mapping is None or rel not in mapping:
            return None
        cur = mapping[rel]
    return cur


def describe(rels):
    return "the " + " of the ".join(rels[::-1]) + " of"


class AnaphoricDescriptionTransfer(Task):
    summary = ("Recover relational descriptions behind paycheck anaphora and "
               "reinstantiate them under new binders; vary nested possessors, "
               "relation chains, and binder switches, returning the newly "
               "denoted entity.")
    design_choice = ("Answer is the entity identifier from a fixed universe, "
                     "chosen by resolving a chain like 'the owner of the "
                     "paycheck of the manager' under a new binder that swaps "
                     "the outer possessor.")
    config_cls = AnaphoricDescriptionTransferConfig

    def generate_entry(self):
        cfg = self.config
        names = random.sample(_NAMES, cfg.n_entities)

        while True:
            new_binder, outer_old = random.sample(names, 2)
            others = [x for x in names if x not in (new_binder, outer_old)]
            answer_new = random.choice(others)
            others2 = [x for x in others if x != answer_new]
            answer_old = random.choice(others2)

            chain_len = cfg.chain_len
            rels = [random.choice(_RELATIONS)[0] for _ in range(chain_len)]
            universe = {}

            def lay_path(start, end, used):
                nodes = [start]
                pool = [x for x in names if x not in used and x not in (start, end)]
                if chain_len > 1:
                    if len(pool) < chain_len - 1:
                        return None, used
                    nodes.extend(random.sample(pool, chain_len - 1))
                nodes.append(end)
                for i in range(chain_len):
                    universe.setdefault(nodes[i], {})[rels[i]] = nodes[i + 1]
                return nodes, used | set(nodes)

            pn, sn = lay_path(new_binder, answer_new, set())
            if pn is None:
                continue
            po, _ = lay_path(outer_old, answer_old, sn | {new_binder})
            if po is None:
                continue

            if resolve_chain(universe, rels, new_binder) != answer_new:
                continue
            if resolve_chain(universe, rels, outer_old) != answer_old:
                continue
            break

        facts = []
        for subj in sorted(universe):
            for rel in sorted(universe[subj]):
                facts.append(f"the {rel} of {subj} is {universe[subj][rel]}")

        return Entry(
            metadata={
                "universe": universe,
                "rels": rels,
                "new_binder": new_binder,
                "outer_old": outer_old,
                "answer_old": answer_old,
                "answer": answer_new,
                "facts": facts,
            },
            answer=str(answer_new),
        )

    def render_prompt(self, metadata):
        facts = "\n".join(metadata["facts"])
        desc_str = describe(metadata["rels"])
        new_b = metadata["new_binder"]
        outer = metadata["outer_old"]
        a_old = metadata["answer_old"]
        return (
            "Here are facts about a cast of people:\n"
            f"{facts}\n"
            f'Reading a description like "{desc_str} (the <binder>)" means: '
            "resolve the chain deepest-first from the binder.\n"
            f"With {outer} as the binder, that description denotes {a_old}.\n"
            f"Now the outer possessor is switched: {new_b} becomes the "
            f"binder instead of {outer}.\n"
            f"Under the new binder {new_b}, whom does the description "
            "denote? Answer with exactly one name."
        )

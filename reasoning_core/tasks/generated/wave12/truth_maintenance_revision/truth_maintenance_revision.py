import random

from reasoning_core.template import Config, Entry, Task


class TruthMaintenanceConfig(Config):
    num_facts: int = 6
    max_premises: int = 2
    max_revisions: int = 3

    def apply_difficulty(self, level):
        self.num_facts = 6 + level
        self.max_premises = 2 + max(0, level - 2)
        self.max_revisions = 2 + level


class TruthMaintenanceRevision(Task):
    summary = "Maintain derived facts with explicit justification sets as premises are added or retracted, returning the facts that remain supported."
    design_choice = "Represent each fact as a propositional literal with a unique integer ID, and answer with a sorted list of IDs of facts whose justification sets are non-empty after each revision."
    config_cls = TruthMaintenanceConfig

    def generate_entry(self):
        cfg = self.config
        facts = list(range(1, cfg.num_facts + 1))

        full = facts[:]
        # Start: half the facts have a single self premise (supported), half empty.
        count = len(full)
        supported_count = max(1, count // 2)
        supported_pool = random.sample(full, supported_count)
        j = {f: ([f] if f in supported_pool else []) for f in full}

        revs = []
        for _ in range(cfg.max_revisions):
            f = random.choice(full)
            if random.random() < 0.5:
                op = "add"
                j[f] = [f]
            else:
                op = "retract"
                j[f] = []
            supported = sorted(fx for fx in full if j[fx])
            revs.append({"op": op, "fact": f, "supported": supported})

        final_supported = sorted(fx for fx in full if j[fx])
        return Entry(
            metadata={
                "num_facts": cfg.num_facts,
                "justification_sets": {str(k): list(v) for k, v in j.items()},
                "revisions": revs,
            },
            answer=",".join(str(fx) for fx in final_supported),
        )

    def render_prompt(self, metadata):
        parts = [
            f"There are {metadata['num_facts']} facts with IDs 1 through {metadata['num_facts']}. "
            "Each fact has a justification set: a list of fact IDs that support it. "
            "A fact is supported exactly when its justification set is non-empty and empty otherwise.",
            f"Initial justification sets: {metadata['justification_sets']}.",
        ]
        for i, r in enumerate(metadata["revisions"], 1):
            verb = "add a supporting premise to" if r["op"] == "add" else "retract (withdraw) the supporting premises from"
            parts.append(
                f"Revision {i}: {verb} fact {r['fact']}. "
                f"After this, fact {r['fact']} is supported if its justification set is non-empty, empty otherwise."
            )
        parts.append(
            "After all revisions, list the IDs of the facts still supported, in increasing order, "
            "separated by commas (e.g. '1,4,5')."
        )
        return " ".join(parts)


TASK_META = {'parent_source_id': None,
 'idea': 'truth_maintenance_revision (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:truth_maintenance_revision',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/truth_maintenance_revision',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3055699702,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

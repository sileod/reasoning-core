import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'epoch_retirement_safety (variant 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_algorithms_and_data_structures_r4/epoch_retirement_safety',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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


@dataclass
class EpochRetirementConfig(Config):
    grace: int = 1
    n_objs: int = 4
    n_readers: int = 3
    max_epoch: int = 6

    def apply_difficulty(self, level):
        self.grace = 1 + level
        self.n_objs = 4 + level
        self.n_readers = 3 + level
        self.max_epoch = 6 + 2 * level


class EpochRetirementSafety(Task):
    summary = ("Track active readers, announced epochs, quiescent transitions, and object "
               "retirements under stated grace-period rules; determine which retired objects "
               "are reclaimable or which readers still block them.")
    config_cls = EpochRetirementConfig
    design_choice = ("Give a static snapshot of per-reader epochs, object retirement epochs, "
                     "and grace period length; ask which objects are safe to free by comparing "
                     "each object's retirement epoch against the oldest active reader epoch plus "
                     "the grace offset.")

    def generate_entry(self):
        n = self.config.n_readers
        m = self.config.n_objs
        max_epoch = self.config.max_epoch
        grace = self.config.grace

        readers = {}
        for i in range(n):
            readers[f"r{i}"] = random.randint(0, max_epoch)

        retired = {}
        for i in range(m):
            retired[f"o{i}"] = random.randint(0, max_epoch)

        oldest = min(readers.values())
        threshold = oldest + grace
        safe_list = sorted(o for o, e in retired.items() if e < threshold)
        blocked_list = sorted(o for o, e in retired.items() if e >= threshold)

        assert len(safe_list) + len(blocked_list) == m

        mode = random.random()

        if mode < 0.4:
            answer = " ".join(safe_list) if safe_list else "none"
            specific = None
            ask = "safe"
        elif mode < 0.8:
            answer = " ".join(blocked_list) if blocked_list else "none"
            specific = None
            ask = "blocked"
        else:
            for _ in range(200):
                if safe_list and blocked_list:
                    break
                readers = {}
                for i in range(n):
                    readers[f"r{i}"] = random.randint(0, max_epoch)
                retired = {}
                for i in range(m):
                    retired[f"o{i}"] = random.randint(0, max_epoch)
                oldest = min(readers.values())
                threshold = oldest + grace
                safe_list = sorted(o for o, e in retired.items() if e < threshold)
                blocked_list = sorted(o for o, e in retired.items() if e >= threshold)
            assert safe_list and blocked_list, "could not build a balanced yes/no instance"
            specific = random.choice(random.choice([safe_list, blocked_list]))
            answer = "yes" if specific in safe_list else "no"
            ask = "yesno"

        metadata = {
            "readers": readers,
            "retired": retired,
            "grace": grace,
            "oldest_reader": oldest,
            "threshold": threshold,
            "safe": safe_list,
            "blocked": blocked_list,
            "specific": specific,
            "ask": ask,
            "target_answer": answer,
        }
        return Entry(metadata=metadata, answer=str(answer))

    def render_prompt(self, metadata):
        grace = metadata["grace"]
        oldest = metadata["oldest_reader"]
        reader_lines = ", ".join(f"{k}:{v}" for k, v in sorted(metadata["readers"].items()))
        retire_lines = ", ".join(f"{k}:{v}" for k, v in sorted(metadata["retired"].items()))

        if metadata["ask"] != "yesno":
            target = "safe to free now (reclaimable)" if metadata["ask"] == "safe" else "still blocking (not yet safe to free)"
            lines = (
                f"In epoch-based memory reclamation, every active reader records the epoch at "
                f"which it began, and an object is retired at the epoch when it is no longer "
                f"referenced. An object retired at epoch E is reclaimable exactly when "
                f"E < oldest_active_reader_epoch + grace.\n"
                f"The grace period is {grace}.\n"
                f"Active reader epochs: {reader_lines}.\n"
                f"Objects retired at these epochs: {retire_lines}.\n"
                f"Here oldest_active_reader_epoch = {oldest}, so the threshold is {metadata['threshold']}.\n"
                f"List every object that is {target}. Write the object names separated "
                f"by single spaces in lexicographic order, or write the single word 'none' if "
                f"no object qualifies."
            )
            return lines
        else:
            lines = (
                f"In epoch-based memory reclamation, every active reader records the epoch at "
                f"which it began, and an object is retired at the epoch when it is no longer "
                f"referenced. An object retired at epoch E is reclaimable exactly when "
                f"E < oldest_active_reader_epoch + grace.\n"
                f"The grace period is {grace}.\n"
                f"Active reader epochs: {reader_lines}.\n"
                f"Objects retired at these epochs: {retire_lines}.\n"
                f"Here oldest_active_reader_epoch = {oldest}, so the threshold is {metadata['threshold']}.\n"
                f"Is the object {metadata['specific']} (retired at epoch "
                f"{metadata['retired'][metadata['specific']]}) safe to free now? "
                f"Answer with the single word 'yes' or 'no'."
            )
            return lines

    def score_answer(self, answer, entry):
        import re
        ans = str(answer).strip()
        metadata = entry.metadata
        if metadata["ask"] != "yesno":
            gold = metadata["safe"] if metadata["ask"] == "safe" else metadata["blocked"]
            if ans.lower() == "none":
                return 1.0 if not gold else 0.0
            tokens = [t for t in re.split(r"\s+", ans) if t]
            if not tokens:
                return 0.0
            return 1.0 if sorted(tokens) == gold else 0.0
        else:
            return 1.0 if ans.lower() == metadata["target_answer"] else 0.0

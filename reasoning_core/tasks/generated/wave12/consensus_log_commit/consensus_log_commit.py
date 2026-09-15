import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class ConsensusLogCommitConfig(Config):
    cluster_size: int = 3
    max_index: int = 6

    def apply_difficulty(self, level):
        sizes = [3, 3, 5, 5, 7, 7, 7]
        self.cluster_size = sizes[min(level, len(sizes) - 1)]
        self.max_index = 4 + level


class ConsensusLogCommit(Task):
    summary = "Track replicated log terms, indexes, acknowledgements, and majority rules in a simplified consensus protocol, returning committed entries or commit index."
    design_choice = "Instances present a fixed cluster size (3, 5, or 7) and a set of log entries per node; the answer is the highest index committed by majority, given as an integer."
    config_cls = ConsensusLogCommitConfig

    def generate_entry(self):
        n = self.config.cluster_size
        majority = n // 2 + 1
        max_index = self.config.max_index

        while True:
            positions = sorted(random.randint(1, max_index) for _ in range(n))
            commit = majority_commit_index(n, majority, positions)
            if 1 <= commit <= max_index:
                break

        node_entries = {f"node{i}": positions[i] for i in range(n)}
        metadata = {
            "cluster_size": n,
            "majority": majority,
            "max_index": max_index,
            "node_entries": node_entries,
            "answer": str(commit),
        }
        return Entry(metadata=metadata, answer=str(commit))

    def render_prompt(self, metadata):
        n = metadata["cluster_size"]
        majority = metadata["majority"]
        lines = "\n".join(
            f"node {i} has committed logs up to and including index {metadata['node_entries'][f'node{i}']}"
            for i in range(n)
        )
        return (
            f"In a replicated consensus log with {n} nodes, each node tracks the highest log index it has "
            f"acknowledged. A log entry at index k is committed once it has been acknowledged by at least "
            f"{majority} nodes (a strict majority of {n}). The committed index is the highest index k such "
            f"that at least {majority} nodes have acknowledged every entry from index 1 up to and including "
            f"index k. Given:\n{lines}\n"
            f"What is the highest committed log index? The answer is one integer."
        )

    def score_answer(self, answer, entry):
        return _score_integer(answer, entry["answer"])


def majority_commit_index(n, majority, positions):
    sorted_desc = sorted(positions, reverse=True)
    return sorted_desc[majority - 1]


def _score_integer(answer, expected):
    try:
        return 1.0 if int(str(answer).strip()) == int(expected) else 0.0
    except (TypeError, ValueError):
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'consensus_log_commit (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:consensus_log_commit',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/consensus_log_commit',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 4126195972,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

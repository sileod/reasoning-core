import random
from dataclasses import dataclass
from itertools import product

from reasoning_core.template import Config, Entry, Task


_MAX_ATTEMPTS = 400


@dataclass
class ComparatorNetworkConfig(Config):
    wires: int = 3
    comparators: int = 5

    def apply_difficulty(self, level):
        self.wires = 3 if level == 0 else 4
        self.comparators = 5 + 2 * level


def _make_sorted(network, wires):
    out = list(range(wires))
    for (a, b) in network:
        if out[a] > out[b]:
            out[a], out[b] = out[b], out[a]
    return out


def _sorts_all(network, wires):
    for word in product((0, 1), repeat=wires):
        out = list(word)
        for (a, b) in network:
            if out[a] > out[b]:
                out[a], out[b] = out[b], out[a]
        if out != sorted(word):
            return False, word
    return True, None


def _random_network(wires, size):
    network = []
    for _ in range(size):
        a = random.randrange(wires)
        b = random.randrange(wires)
        if a == b:
            b = (a + 1) % wires
        if a > b:
            a, b = b, a
        network.append((a, b))
    return network


class ComparatorZeroOneVerification(Task):
    summary = "Comparator networks on few wires: generate a random comparator network and ask whether it sorts all 2^n binary inputs per the zero-one principle, with balanced YES/NO verdicts and randomized wire (3-4) and comparator counts per instance."
    design_choice = "Ask for a yes/no verdict on whether the network sorts all 2^n binary inputs, with the network size and wire count randomized per instance."
    config_cls = ComparatorNetworkConfig

    def generate_entry(self):
        wires = self.config.wires
        size = self.config.comparators

        target_sorts = random.random() < 0.5
        network = _random_network(wires, size)
        for _ in range(_MAX_ATTEMPTS):
            verdict = _sorts_all(network, wires)[0]
            if verdict == target_sorts:
                break
            network = _random_network(wires, size)
        else:
            verdict = _sorts_all(network, wires)[0]

        answer = "YES" if verdict else "NO"
        return Entry(metadata={
            "wires": wires,
            "network": network,
            "answer": answer,
        }, answer=answer)

    def render_prompt(self, metadata):
        wires = metadata["wires"]
        comps = ", ".join(f"({a},{b})" for (a, b) in metadata["network"])
        return (
            f"A comparator network has {wires} wires carrying 0/1 values. "
            f"Its comparators, applied in order, are: {comps}. "
            f"A comparator (a,b) replaces the values on its two wires such that "
            f"afterward the smaller sits on wire a and the larger on wire b. "
            f"By the zero-one principle, the network sorts all inputs iff it sorts "
            f"every length-{wires} binary word. Does this network sort all of its binary "
            f"inputs? Make your verdict the single word YES or NO, and write nothing else."
        )

    def score_answer(self, answer, entry):
        canonical = entry["answer"]
        a = str(answer).strip().upper()
        return 1.0 if a == canonical else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'comparator_network_zero_one_verification (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_latent_structure_reconstruction_r4/comparator_network_zero_one_verification',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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

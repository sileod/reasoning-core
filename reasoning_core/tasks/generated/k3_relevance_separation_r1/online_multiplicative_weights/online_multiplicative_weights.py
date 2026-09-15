"""Online multiplicative weights task: track binary-loss experts."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'online_multiplicative_weights (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relevance_separation_r1/online_multiplicative_weights',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


@dataclass
class OnlineMWConfig(Config):
    n_experts: int = 4
    n_rounds: int = 6

    def apply_difficulty(self, level):
        self.n_experts = 4 + min(level, 3)
        self.n_rounds = 6 + min(level * 2, 8)


class OnlineMultiplicativeWeights(Task):
    summary = "Maintain expert weights under multiplicative updates for a sequence of binary loss vectors (one per-expert 0/1 loss per round, exactly one loser per round), output the final weight vector as a fraction list over a common denominator."

    design_choice = "Loss vectors are binary (0/1) per expert per round, with exactly one expert incurring loss 1 each round; answer is the final weight vector as a fraction list."

    config_cls = OnlineMWConfig

    def generate_entry(self):
        n = self.config.n_experts
        t = self.config.n_rounds

        losses = []
        for _ in range(t):
            loser = random.randrange(n)
            losses.append([1 if j == loser else 0 for j in range(n)])

        eta = 0.5
        weights = [1.0] * n
        for k in range(t):
            for j in range(n):
                weights[j] *= (1 - eta) ** losses[k][j]

        total = sum(weights)

        # Answer: final weights as fractions with common denominator 2^t,
        # normalized to a distribution (divide by total).
        denom = 2 ** t
        fracs = []
        for j in range(n):
            numerator = int(round(weights[j] * denom))
            fracs.append(f"{numerator}/{denom}")

        metadata = {
            "n_experts": n,
            "n_rounds": t,
            "losses": losses,
            "eta": eta,
            "final_weights": [float(w) for w in weights],
            "denom": denom,
            "answer_nums": [int(round(w * denom)) for w in weights],
        }
        return Entry(metadata=metadata, answer=", ".join(fracs))

    def render_prompt(self, metadata):
        n = metadata["n_experts"]
        lines = [
            f"There are {n} experts and {metadata['n_rounds']} rounds of online prediction.",
            "Each round, exactly one of the experts incurs loss 1 and all others incur loss 0.",
            "The loss vectors (round by round, expert by expert) are:",
        ]
        for vec in metadata["losses"]:
            lines.append("  " + ", ".join(str(x) for x in vec))
        lines.append(
            f"Using the multiplicative weights algorithm with learning rate eta={metadata['eta']}, "
            "starting from initial weights all 1, multiply each weight by (1-eta)^(its loss) each round."
        )
        lines.append(
            "Give the resulting final weight vector as a list of fractions "
            f"'a1/D, a2/D, ...' over one common denominator D=2^{metadata['n_rounds']}, "
            "one fraction per expert in expert order, e.g. '1/4, 3/4'. "
            "The weights are not normalized."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        try:
            parts = [p.strip() for p in str(answer).split(",")]
            n = entry.metadata["n_experts"]
            if len(parts) != n:
                return 0.0
            denom = entry.metadata["denom"]
            nums = []
            for p in parts:
                a, b = p.split("/")
                num = int(a)
                if int(b) != denom:
                    return 0.0
                nums.append(num)
            return 1.0 if nums == entry.metadata["answer_nums"] else 0.0
        except Exception:
            return 0.0

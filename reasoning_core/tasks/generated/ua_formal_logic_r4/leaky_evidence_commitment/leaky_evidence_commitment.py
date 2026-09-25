import random

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'leaky_evidence_commitment (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r4/leaky_evidence_commitment',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

class LeakyEvidenceConfig(Config):
    start_bias: int = 1
    bound_low: int = -4
    bound_high: int = 4
    leak_rate: float = 0.04
    max_signs: int = 200
    bound_change_chance: float = 0.0
    burst_chance: float = 0.0

    def apply_difficulty(self, level):
        self.leak_rate = 0.04
        self.bound_high = 3 + level
        self.bound_low = -self.bound_high
        self.start_bias = 1 + (level % 3)
        self.max_signs = 100 + 100 * level
        if level >= 3:
            self.burst_chance = 0.05 + 0.01 * level
        if level >= 5:
            self.bound_change_chance = 0.15


class LeakyEvidenceCommitment(Task):
    summary = (
        "Accumulate signed evidence with stated leakage, starting bias, and "
        "absorbing decision bounds; vary interruptions, changing bounds, and "
        "opposing evidence bursts; answer the committed choice and stopping time."
    )
    design_choice = (
        "Present evidence as a stream of +1/-1 signs with leakage rate and "
        "time-varying thresholds; answer the final choice and step count when "
        "bounds are first hit."
    )
    config_cls = LeakyEvidenceConfig
    task_version = 2

    def _simulate(self, leak, start_bias, low, high, max_signs, bound_change_chance,
                  burst_chance):
        """Draw signs and simulate the leaky accumulator; return (committed, t,
        signs, low0, high0, change). change is (step, side, amount) or None."""
        state = start_bias
        cur_low = low
        cur_high = high
        signs = []
        burst_budget = 0
        change = None
        for t in range(1, max_signs + 1):
            state = int(round(state * (1.0 - leak)))
            if burst_budget > 0:
                burst_budget -= 1
                sign = -1 if state >= 0 else 1
            elif (burst_chance
                    and random.random() < burst_chance):
                burst_budget = random.randint(1, 2)
                sign = -1 if state >= 0 else 1
            else:
                sign = random.choice([-1, 1])
            signs.append(sign)
            state += sign

            if (bound_change_chance
                    and random.random() < bound_change_chance and change is None):
                if random.random() < 0.5:
                    amount = random.randint(1, 2)
                    cur_low -= amount
                    change = (t, "lower", amount)
                else:
                    amount = random.randint(1, 2)
                    cur_high += amount
                    change = (t, "upper", amount)

            if state <= cur_low:
                return "lower", t, signs, low, high, change
            if state >= cur_high:
                return "upper", t, signs, low, high, change
        return None, None, signs, low, high, change

    def generate_entry(self):
        cfg = self.config
        leak = cfg.leak_rate
        start_bias = cfg.start_bias
        attempts = 0
        while True:
            attempts += 1
            if attempts > 500:
                raise RuntimeError(
                    "leaky_evidence_commitment: no trajectory hit a bound in "
                    f"{attempts} attempts"
                )
            committed, t, signs, low0, high0, change = self._simulate(
                leak, start_bias, cfg.bound_low, cfg.bound_high, cfg.max_signs,
                cfg.bound_change_chance, cfg.burst_chance,
            )
            if committed is None:
                continue
            break

        assert t >= 1, "step count must be a positive integer"
        metadata = {
            "start_bias": start_bias,
            "leak_rate": leak,
            "low": low0,
            "high": high0,
            "steps": t,
            "hit": committed,
            "signs": signs,
            "change": change,
        }
        return Entry(metadata=metadata, answer=f"{committed} {t}")

    def render_prompt(self, metadata):
        leak_pct = int(round(metadata["leak_rate"] * 100))
        lines = [
            "A signed-evidence accumulator starts at "
            f"{metadata['start_bias']}. It reads signs one at a time, each +1 or -1. "
            f"Before every sign, the value shrinks by {leak_pct}% of its distance from "
            "zero toward zero (rounded to the nearest integer), then the sign is added. "
            f"The initial decision bounds are {metadata['low']} (lower) and "
            f"{metadata['high']} (upper): the moment the value becomes at or below the "
            "lower bound it commits 'lower', and at or above the upper bound it "
            "commits 'upper', and reading stops immediately.",
        ]
        change = metadata.get("change")
        if change is not None:
            step, side, amount = change
            if side == "lower":
                lines.append(
                    f"At step {step} the lower bound widens further down by "
                    f"{amount} (becomes {metadata['low'] - amount})."
                )
            else:
                lines.append(
                    f"At step {step} the upper bound widens further up by "
                    f"{amount} (becomes {metadata['high'] + amount})."
                )
        signs_text = " ".join(f"{s:+d}" for s in metadata["signs"])
        lines.append(
            "The stated leak, starting value, and (possibly widened) decision "
            "bounds apply while reading this sign stream:\n" + signs_text
        )
        lines.append(
            "What is the committed bound ('upper' or 'lower') and the step number "
            "at which it committed? Answer with the bound word and the step count, "
            "space-separated, e.g. 'upper 7'."
        )
        return "\n".join(lines)

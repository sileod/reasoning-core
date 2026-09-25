import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'perceptual_rivalry_adaptation (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_psychometrics_r4/perceptual_rivalry_adaptation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class PerceptualRivalryConfig(Config):
    steps: int = 3

    def apply_difficulty(self, level):
        self.steps = 3 + level


def _clamp(v):
    return min(1.0, max(0.0, v))


def _step(x, y, pulse, w, alpha, r):
    kind, strength = pulse
    if kind == "A":
        x = _clamp(x + strength)
    elif kind == "B":
        y = _clamp(y + strength)
    if x > y:
        y = _clamp(y - w)
    elif y > x:
        x = _clamp(x - w)
    if x >= y:
        x = _clamp(x - alpha)
        y = _clamp(y + r * (1.0 - y))
    else:
        y = _clamp(y - alpha)
        x = _clamp(x + r * (1.0 - x))
    return x, y


def _dominant(x, y, prev):
    if abs(x - y) < 1e-9:
        return prev
    return "A" if x > y else "B"


def _simulate(base_A, base_B, w, alpha, r, pulses, initial_A):
    x, y = base_A, base_B
    prev = "A" if initial_A else "B"
    dominants = []
    for p in pulses:
        x, y = _step(x, y, p, w, alpha, r)
        d = _dominant(x, y, prev)
        dominants.append(d)
        prev = d
    return dominants, x, y


def _parse_answer(answer):
    if not isinstance(answer, str):
        return None
    a = answer.strip().upper()
    if a in ("A", "B"):
        return a
    return None


class PerceptualRivalryAdaptation(Task):
    summary = "Track competing percepts under stated mutual inhibition, dominance adaptation, and recovery rules; vary stimulus pulses, interruptions, and asymmetric strengths; answer the dominant percept or switch count."
    design_choice = "Answer the dominant percept after a fixed number of simulated time steps, given a deterministic sequence of external pulses and recovery intervals."
    config_cls = PerceptualRivalryConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(50):
            n = random.randint(cfg.steps, cfg.steps + 2)
            base_A = random.uniform(0.1, 0.9)
            base_B = random.uniform(0.1, 0.9)
            w = random.uniform(0.05, 0.45)
            alpha = random.uniform(0.03, 0.3)
            r = random.uniform(0.08, 0.45)
            initial_A = random.random() < 0.5
            pulses = []
            for _ in range(n):
                kind = random.choice(("A", "B", "rest"))
                if kind == "rest":
                    pulses.append(("rest", 0.0))
                else:
                    pulses.append((kind, random.uniform(0.1, 0.8)))
            dominants, fx, fy = _simulate(base_A, base_B, w, alpha, r, pulses, initial_A)
            final = dominants[-1]
            if abs(fx - fy) >= 1e-9 and final in ("A", "B"):
                switch_count = sum(1 for i in range(1, len(dominants)) if dominants[i] != dominants[i - 1])
                pulses_str = " ".join("." if k == "rest" else f"{k}{s:.2f}" for k, s in pulses)
                metadata = {
                    "base_A": round(base_A, 3),
                    "base_B": round(base_B, 3),
                    "w": round(w, 3),
                    "alpha": round(alpha, 3),
                    "r": round(r, 3),
                    "initial_A": initial_A,
                    "pulses": pulses_str,
                    "n": n,
                    "final_A": round(fx, 3),
                    "final_B": round(fy, 3),
                    "switch_count": switch_count,
                    "dominant_history": dominants,
                }
                return Entry(metadata=metadata, answer=final)
        raise RuntimeError("could not draw a non-tied rivalry instance")

    def render_prompt(self, metadata):
        rules = ("Two percepts, A and B, compete. Each has an activation in [0, 1]. "
                 "Each simulated time step applies exactly one of three external pulses: "
                 "'A<strength>' adds that strength to A's activation, 'B<strength>' adds it "
                 "to B's, and '.' (rest) adds nothing. Then, in order: (1) mutual inhibition "
                 "subtracts the inhibition strength from whichever percept is currently weaker; "
                 "(2) dominance adaptation subtracts the adaptation rate from the currently "
                 "stronger percept; (3) recovery adds the recovery rate times its remaining "
                 "distance to 1 to the currently weaker percept. Every activation is kept "
                 "inside [0, 1]. The dominant percept at a step is the one with the strictly "
                 "greater activation.")
        asym = ("Symmetric baseline activations" if metadata["base_A"] == metadata["base_B"]
                else "Asymmetric baseline activations")
        body = (f"Baseline activations at step 0: A={metadata['base_A']}, B={metadata['base_B']} "
                f"({asym}). Inhibitions: w={metadata['w']}, adaptation={metadata['alpha']}, "
                f"recovery={metadata['r']}. The deterministic pulse sequence over all "
                f"{metadata['n']} steps is: {metadata['pulses']}.")
        question = ("Simulate the rivalry for the given number of steps. What is the dominant "
                    "percept after the final step? Answer A or B, and nothing else.")
        return f"{rules}\n{body}\n{question}"

    def score_answer(self, answer, entry):
        a = _parse_answer(answer)
        return float(a is not None and a == _parse_answer(entry.answer))

import math
import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


@dataclass
class ProcessDissociationRoutesV2Config(Config):
    level: int = 0
    max_inclusion: int = 14
    max_attempts: int = 5
    serial_prob: float = 0.5

    def apply_difficulty(self, level):
        self.level = level
        self.max_inclusion = 8 + 2 * level
        self.max_attempts = 2 + level


def _serial_prob(a, c, n):
    p_a = Fraction(a, 100)
    p_c = Fraction(c, 100)
    return (1 - p_c) * (1 - (1 - p_a) ** n)


def _parallel_prob(a, c, n):
    p_a = Fraction(a, 100)
    p_c = Fraction(c, 100)
    any_ = 1 - (1 - p_a) ** n * (1 - p_c)
    return (1 - (1 - p_a) ** n) / any_


class ProcessDissociationRoutes(Task):
    """Separate controlled recollection from automatic influence using inclusion and exclusion outcomes; vary independent serial or parallel automatic routes and shared components; answer route probabilities or feasibility."""

    summary = "Separate controlled recollection from automatic influence using inclusion and exclusion outcomes; vary independent serial or parallel automatic routes and shared components; answer route probabilities or feasibility."
    design_choice = "Give a small process-dissociation scenario with a stated serial or parallel route structure; solvers answer the probability that a specific automatic route contributes, expressed as a reduced fraction."
    config_cls = ProcessDissociationRoutesV2Config
    task_version = 2
    answer_dims = 2

    def generate_entry(self):
        cfg = self.config
        max_incl = cfg.max_inclusion
        max_n = cfg.max_attempts

        while True:
            route_type = random.choice(["serial", "parallel"])
            n = random.randint(1, max_n)
            a = random.randint(1, max_incl)
            c = random.randint(1, max_incl)

            if route_type == "serial":
                p = _serial_prob(a, c, n)
            else:
                p = _parallel_prob(a, c, n)

            if p <= 0 or p >= 1:
                continue
            if p.denominator < 3 or p.denominator > 4000:
                continue

            answer = f"{p.numerator}/{p.denominator}"
            return Entry(
                metadata={
                    "route_type": route_type,
                    "n": n,
                    "a": a,
                    "c": c,
                    "p_auto": [p.numerator, p.denominator],
                    "answer": answer,
                },
                answer=answer,
            )

    def render_prompt(self, metadata):
        rt = metadata["route_type"]
        n = metadata["n"]
        a = metadata["a"]
        c = metadata["c"]

        if rt == "serial":
            return (
                f"In a process-dissociation task a participant must recognize a target word. "
                f"Controlled recollection succeeds with probability {c}/100; when it fails the "
                f"target can still be recognized through the automatic memory route, which "
                f"triggers with probability {a}/100 on each of {n} independent opportunities. "
                f"The two routes cannot both produce the recognition (serial structure). "
                f"Compute the probability that the automatic memory route is the one that "
                f"produces the recognition of the target. Give your answer as a reduced "
                f"fraction a/b."
            )
        else:
            return (
                f"In a process-dissociation task a participant must recognize a target word. "
                f"The controlled recollection route and the automatic memory route operate in "
                f"parallel and independently; the target is recognized if either route triggers. "
                f"The automatic route triggers with probability {a}/100 on each of {n} "
                f"independent opportunities; the controlled route triggers with probability "
                f"{c}/100 once. Given that the target was recognized, compute the conditional "
                f"probability that the automatic route was the one that produced it. Give your "
                f"answer as a reduced fraction a/b."
            )

    def score_answer(self, answer, entry):
        try:
            num, den = answer.split("/")
            got = Fraction(int(num), int(den))
        except Exception:
            return 0.0
        want = Fraction(entry.metadata["p_auto"][0], entry.metadata["p_auto"][1])
        return 1.0 if got == want else 0.0

    def distractor_candidates(self, entry):
        md = entry.metadata
        a = Fraction(md["a"], 100)
        c = Fraction(md["c"], 100)
        n = md["n"]
        rt = md["route_type"]

        p_none_a = (1 - a) ** n
        cands = set()
        cands.add(a)
        cands.add(c)
        cands.add(a * c)
        cands.add(1 - a)
        cands.add(1 - c)
        cands.add(a * n)
        cands.add(Fraction(a * n, 100))
        if rt == "serial":
            cands.add((1 - c) * (1 - a**n))
            cands.add(p_none_a * c)
        else:
            p_any = 1 - p_none_a * (1 - c)
            cands.add(1 - p_none_a)
            cands.add((1 - p_none_a) * c)
            if p_any > 0:
                cands.add(c / p_any)

        want = Fraction(md["p_auto"][0], md["p_auto"][1])
        out = []
        for f in cands:
            if f <= 0 or f >= 1:
                continue
            if f == want:
                continue
            out.append(f"{f.numerator}/{f.denominator}")
        return out


TASK_META = {'parent_source_id': None,
 'idea': 'process_dissociation_routes (variant 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_psychometrics_r4/process_dissociation_routes',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 382564971,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

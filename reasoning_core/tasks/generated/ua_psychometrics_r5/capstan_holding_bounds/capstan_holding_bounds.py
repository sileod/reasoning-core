import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'capstan_holding_bounds (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_psychometrics_r5/capstan_holding_bounds',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _rand_frac(lo, hi_num, hi_den_limit):
    num = random.randint(lo, hi_num)
    den = random.randint(1, num - 1 if num > 1 else 1)
    return Fraction(num, den)


def _rand_wrap(max_int):
    num = random.randint(2, max_int)
    den = random.randint(1, num - 1)
    return Fraction(num, den)


def _parse_answer(answer):
    s = answer.strip()
    if not (s.startswith("[") and s.endswith("]")):
        raise ValueError("not bracketed")
    inner = s[1:-1].strip()
    lo, hi = inner.split(",")
    return Fraction(lo.strip()), Fraction(hi.strip())


@dataclass
class CapstanConfig(Config):
    num_drums: int = 1
    num_loads: int = 1
    max_int: int = 4

    def apply_difficulty(self, level):
        self.num_drums = 1 + level // 2
        self.num_loads = 1 + (level >= 2) + (level >= 5)
        self.max_int = 4 + 2 * level


class CapstanHoldingBounds(Task):
    summary = "Propagate tension bounds through rough drums with specified wrap factors and possible slip directions; combine suspended loads and driven forces, returning the holding-force interval as an exact rational pair in newtons."
    config_cls = CapstanConfig
    task_version = 2
    design_choice = "Return the holding-force interval as an exact fraction pair [min, max] in newtons, with all tensions and wrap factors given as rational numbers."

    def generate_entry(self):
        cfg = self.config
        while True:
            drums = [_rand_wrap(cfg.max_int) for _ in range(cfg.num_drums)]
            loads = [_rand_frac(1, cfg.max_int, cfg.max_int) for _ in range(cfg.num_loads)]
            driven = random.choice([False, True])
            if driven:
                driven_force = _rand_frac(1, cfg.max_int, cfg.max_int)
            else:
                driven_force = None

            total = sum(loads, Fraction(0))
            if driven_force is not None:
                total = total + driven_force

            product = Fraction(1)
            for r in drums:
                product = product * r

            lo = total / product
            hi = total * product

            if lo <= 0 or hi <= lo:
                continue

            min_str = str(lo)
            max_str = str(hi)

            drum_str = [str(r) for r in drums]
            load_str = [str(w) for w in loads]

            if lo == total and hi == total:
                continue

            answer = f"[{min_str}, {max_str}]"
            return Entry(
                metadata={
                    "wrap_factors": drum_str,
                    "loads": load_str,
                    "driven_force": str(driven_force) if driven_force is not None else None,
                    "total_tension": str(total),
                    "wrap_product": str(product),
                    "min": min_str,
                    "max": max_str,
                },
                answer=answer,
            )

    def render_prompt(self, metadata):
        lines = [
            "A rope runs through the following fixed rough drums in series; each drum is "
            "described by its wrap factor, which is how much friction alone lets the tension "
            "ratio across it grow. Tension can therefore differ across a drum by any factor "
            "between its wrap factor and one over it, before slipping."
        ]
        for i, r in enumerate(metadata["wrap_factors"]):
            lines.append(f"Drum {i+1}: wrap factor {r}.")
        base = []
        for j, w in enumerate(metadata["loads"]):
            base.append(f"a suspended block of {w} N")
        if metadata["driven_force"] is not None:
            base.append(f"an assisting driven hoist of {metadata['driven_force']} N")
        lines.append(
            "At the load end the rope carries " + ", ".join(base) + "."
        )
        lines.append(
            "The holding end is where tension is applied to keep the assembly still. "
            "If the load tends to slip the rope downward the holding tension must be at least "
            "the total end tension divided by the product of all wrap factors; if the holding "
            "force is too large the rope lifts the load, giving an upper bound equal to the "
            "total end tension times the product of all wrap factors."
        )
        lines.append(
            "Return the holding-force interval [min, max] in newtons as an exact pair of "
            "fractions, for example [9/4, 36]. Give min and max as reduced fractions; a whole "
            "number may be written as an integer."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        try:
            lo, hi = _parse_answer(answer)
        except Exception:
            return 0.0
        elo = Fraction(entry.metadata["min"])
        ehi = Fraction(entry.metadata["max"])
        if lo == elo and hi == ehi:
            return 1.0
        return 0.0

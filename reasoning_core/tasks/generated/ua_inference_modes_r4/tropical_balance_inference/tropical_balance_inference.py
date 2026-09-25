import random

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'tropical_balance_inference (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_inference_modes_r4/tropical_balance_inference',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class TropicalBalanceConfig(Config):
    exp_range: int = 1
    val_range: int = 2
    max_ab: int = 1

    def apply_difficulty(self, level):
        self.exp_range = 1 + level
        self.val_range = 2 + level
        self.max_ab = 1 + level


def _parse_tuple(text):
    text = str(text).strip()
    if text[:1] in "([":
        text = text.strip("()[]{} ")
    parts = [p.strip() for p in text.split(",")]
    if len(parts) == 2:
        try:
            return (int(parts[0]), int(parts[1]))
        except ValueError:
            pass
    parts = text.split()
    if len(parts) == 2:
        try:
            return (int(parts[0]), int(parts[1]))
        except ValueError:
            pass
    return None


def _weight(a, b, k, p, q):
    return k + a * p + b * q


class TropicalBalanceInference(Task):
    summary = ("Infer the unique admissible leading-power tuple (a,b) balancing a two-variable "
               "small-parameter trinomial system: equal dominant monomial weights in each "
               "equation, subdominant third monomial, matched cancellation signs, coupled "
               "unknowns.")
    design_choice = ("Represent the answer as a single admissible exponent tuple (a,b) for a "
                     "two-variable system, with all other exponents fixed and balanced.")
    config_cls = TropicalBalanceConfig
    task_version = 2

    def generate_entry(self):
        er = self.config.exp_range
        vr = self.config.val_range
        amax = self.config.max_ab
        for _ in range(4000):
            a = random.randint(0, amax)
            b = random.randint(0, amax)
            res = self._build_system(a, b, er, vr)
            if res is None:
                continue
            eq1, eq2 = res
            return Entry(metadata={"eq1": eq1, "eq2": eq2, "a": a, "b": b},
                         answer="({}, {})".format(a, b))
        raise RuntimeError("tropical_balance: could not build an admissible system")

    def _build_system(self, a, b, er, vr):
        for _ in range(200):
            eq1 = self._sample_equation(a, b, er, vr)
            if eq1 is None:
                continue
            d1x = eq1["p1"] - eq1["p2"]
            d1y = eq1["q1"] - eq1["q2"]
            for _ in range(200):
                eq2 = self._sample_equation(a, b, er, vr)
                if eq2 is None:
                    continue
                d2x = eq2["p1"] - eq2["p2"]
                d2y = eq2["q1"] - eq2["q2"]
                if d1x * d2y - d1y * d2x == 0:
                    continue
                return (eq1, eq2)
        return None

    def _sample_equation(self, a, b, er, vr):
        for _ in range(200):
            p1 = random.randint(-er, er)
            q1 = random.randint(-er, er)
            p2 = random.randint(-er, er)
            q2 = random.randint(-er, er)
            if (p1, q1) == (p2, q2):
                continue
            p3 = random.randint(-er, er)
            q3 = random.randint(-er, er)
            if (p3, q3) == (p1, q1) or (p3, q3) == (p2, q2):
                continue
            k1 = random.randint(-vr, vr)
            k2 = k1 + a * (p1 - p2) + b * (q1 - q2)
            w = k1 + a * p1 + b * q1
            if _weight(a, b, 0, p3, q3) >= w:
                continue
            k3_max = w - (a * p3 + b * q3) - 1
            lo3 = max(-vr, k3_max - 2 * vr)
            hi3 = k3_max
            if lo3 > hi3:
                continue
            k3 = random.randint(lo3, hi3)
            if _weight(a, b, k3, p3, q3) >= w:
                continue
            return {"p1": p1, "q1": q1, "p2": p2, "q2": q2,
                    "p3": p3, "q3": q3, "k1": k1, "k2": k2, "k3": k3}
        return None

    def render_prompt(self, metadata):
        e1 = metadata["eq1"]
        e2 = metadata["eq2"]
        a = metadata["a"]
        b = metadata["b"]

        def mon(e):
            return ("+c*e^{%d}*x^{%d}*y^{%d} -c*e^{%d}*x^{%d}*y^{%d} "
                    "+d*e^{%d}*x^{%d}*y^{%d}"
                    % (e["k1"], e["p1"], e["q1"], e["k2"], e["p2"], e["q2"],
                       e["k3"], e["p3"], e["q3"]))

        s = ("A two-variable polynomial system degenerates through a small parameter "
             "e -> 0, where c and d are nonzero constants with c != d. The first two "
             "monomials of each equation have equal magnitude and opposite sign, so they "
             "cancel whenever they are the dominant (maximal e-weight) terms.\n")
        s += "F1 = " + mon(e1) + "\n"
        s += "F2 = " + mon(e2) + "\n"
        s += ("Give x the e-weight a and y the e-weight b, that is the e-weight of a "
              "monomial c*e^k*x^p*y^q is k + a*p + b*q. Both equations balance (their first "
              "two monomials have equal weight and dominate, the third is strictly "
              "sub-dominant) at exactly one admissible leading-power tuple (a, b) with "
              "a >= 0 and b >= 0 satisfying the two balance equations\n")
        s += ("k1 + a*p1 + b*q1 = k2 + a*p2 + b*q2 (for F1), "
              "k1 + a*p1 + b*q1 = k2 + a*p2 + b*q2 (for F2).\n")
        s += ("Find that tuple (a, b). Answer exactly as (a, b) with two integers, e.g. (3, 2).")
        return s

    def score_answer(self, answer, entry):
        ref = _parse_tuple(entry.answer)
        got = _parse_tuple(answer)
        return 1.0 if got is not None and got == ref else 0.0

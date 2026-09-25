import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'event_time_intervention_sensitivity (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_counterfactual_r5/event_time_intervention_sensitivity',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _final_time(x0, legs, resets):
    x = Fraction(x0)
    T = Fraction(0)
    for (a, s, l), (al, be) in zip(legs, resets):
        tau = (Fraction(l) - x) / (Fraction(a) - Fraction(s))
        x = Fraction(al) * (x + Fraction(a) * tau) + Fraction(be)
        T += tau
    return T


def _analytic_sensitivity(x0, legs, resets):
    x = Fraction(x0)
    dxdx0 = Fraction(1)
    dTdx0 = Fraction(0)
    for (a, s, l), (al, be) in zip(legs, resets):
        dtau_dx = Fraction(-1) / (Fraction(a) - Fraction(s))
        dTdx0 += dtau_dx * dxdx0
        dxat_dx = Fraction(1) + Fraction(a) * dtau_dx
        dxdx0 = Fraction(al) * dxat_dx * dxdx0
    return dTdx0


def _finite_sensitivity(x0, legs, resets, eps=Fraction(1, 10**6)):
    t_plus = _final_time(x0 + eps, legs, resets)
    t_minus = _final_time(x0 - eps, legs, resets)
    return (t_plus - t_minus) / (2 * eps)


@dataclass
class EventTimeConfig(Config):
    max_legs: int = 3

    def apply_difficulty(self, level):
        self.max_legs = stochastic_rounding(2 + level)


class EventTimeInterventionSensitivity(Task):
    summary = ("Perturb the initial level of a piecewise-affine flow with affine guards and "
               "resets; propagate the shift in each event time through every leg and return "
               "the exact rational derivative of the final event time with respect to the "
               "initial state.")
    design_choice = ("Represent terminal quantity as the time of the last event, and return "
                     "sensitivity of that event time to an initial state component.")
    config_cls = EventTimeConfig

    def generate_entry(self):
        for _ in range(2000):
            x0 = random.randint(1, 5)
            legs = []
            resets = []
            x = Fraction(x0)
            nlegs = random.randint(1, self.config.max_legs)
            sensitivity = Fraction(0)
            dxdx0 = Fraction(1)
            rejected = False
            for _k in range(nlegs):
                a = random.randint(5, 8)
                s = random.randint(1, a - 1)
                l = random.randint(int(x) + 1, int(x) + 8)
                al = random.choice([-1, 1, -2, 2])
                be = random.randint(0, 4)
                legs.append((a, s, l))
                resets.append((al, be))
                tau = Fraction(l - x, a - s)
                xat = x + Fraction(a) * tau
                x = Fraction(al) * xat + Fraction(be)
                dtau_dx = Fraction(-1, a - s)
                sensitivity += dtau_dx * dxdx0
                dxat_dx = 1 + Fraction(a) * dtau_dx
                dxdx0 = Fraction(al) * dxat_dx * dxdx0
                if x <= 0 or sensitivity.denominator > 10**6 or x.denominator > 10**6:
                    rejected = True
                    break
            if rejected:
                continue
            t0 = _final_time(x0, legs, resets)
            if t0 <= 0:
                continue
            fd = _finite_sensitivity(x0, legs, resets)
            if float(abs(fd - sensitivity)) > 1e-6:
                continue
            answer = str(sensitivity)
            metadata = {
                "x0": x0,
                "nlegs": nlegs,
                "legs": [[int(a), int(s), int(l)] for a, s, l in legs],
                "resets": [[int(al), int(be)] for al, be in resets],
                "final_time_exact": str(t0),
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("event_time_intervention_sensitivity: no admissible instance")

    def render_prompt(self, metadata):
        x0 = metadata["x0"]
        nlegs = metadata["nlegs"]
        leg_lines = []
        for k, (a, s, l) in enumerate(metadata["legs"], 1):
            al, be = metadata["resets"][k - 1]
            leg_lines.append(
                f"   Leg {k}: level rises at rate {a}; the sensor level starts at {l} and "
                f"rises at rate {s}; when the sensor fires the level resets to "
                f"{al}*(level at that instant) + {be}."
            )
        legs_text = "\n".join(leg_lines)
        return (
            "A vessel is refilled through a sequence of guarded, resetting legs in a "
            "piecewise-affine flow. The level x(t) starts at x0 = " + str(x0) + ".\n"
            + legs_text + "\n"
            "Each leg k runs from the moment the previous sensor fired until this leg's "
            "sensor fires; it lasts tau_k = (l_k - x)/(a_k - s_k) and, when it fires, the "
            "level is reset as above. The final event time T is the absolute time at which "
            f"the last (Leg {nlegs}) sensor fires, i.e. T = tau_1 + ... + tau_{nlegs}.\n"
            "What is the exact one-sided sensitivity dT/dx0, i.e. how much the final "
            "event time moves per unit increase in the initial level x0?\n"
            "Answer as an exact reduced fraction such as 3/5 or -7/2 (it may be "
            "negative, zero, or an integer)."
        )


    def score_answer(self, answer, entry):
        try:
            return 1.0 if _parse_fraction(answer) == _parse_fraction(entry.answer) else 0.0
        except Exception:
            return 0.0


def _parse_fraction(s):
    return Fraction(str(s).strip())

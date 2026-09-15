"""Kaplan-Meier (product-limit) survival estimate at a queried day.

Generate a small cohort followed over an integer-day horizon: some subjects
fail (event) on distinct days, others are censored (withdrawn) on other days.
The task walks the ordered timeline maintaining the at-risk count and answers
the product-limit survival probability at a queried day as a reduced fraction.
"""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


@dataclass
class CensoredSurvivalConfig(Config):
    num_subjects: int = 6
    horizon: int = 12
    event_prob: float = 0.6

    def apply_difficulty(self, level):
        self.num_subjects = 6 + level
        self.horizon = 14 + 3 * level


def _build_instance(cfg):
    num = cfg.num_subjects
    horizon = cfg.horizon
    for _ in range(200):
        k_event = sum(1 for _ in range(num) if random.random() < cfg.event_prob)
        if k_event < 1 or k_event >= num:
            continue
        k_withdraw = num - k_event
        if k_withdraw < 1:
            continue
        days = list(range(1, horizon + 1))
        if len(days) < num:
            continue
        event_days = sorted(random.sample(days, k_event))
        remaining = [d for d in days if d not in set(event_days)]
        if len(remaining) < k_withdraw:
            continue
        withdraw_days = sorted(random.sample(remaining, k_withdraw))
        return event_days, withdraw_days, num
    raise RuntimeError("could not construct survival instance")


def _product_limit(event_days, withdraw_days, num, query_day):
    """Return reduced Fraction survival probability at query_day (product-limit)."""
    n_wd = len(withdraw_days)
    wi = 0
    prod = Fraction(1, 1)
    at_risk = num
    for ei, t in enumerate(event_days):
        while wi < n_wd and withdraw_days[wi] < t:
            wi += 1
        at_risk = num - ei - wi
        if t <= query_day:
            prod *= Fraction(at_risk - 1, at_risk)
    return prod


class CensoredSurvivalEstimate(Task):
    summary = ("Walk an ordered timeline of distinct integer-day events and "
               "withdrawals, maintaining the at-risk count; at each event time "
               "multiply the running estimate by the survived fraction, "
               "answering the product-limit (Kaplan-Meier) survival probability "
               "at a queried day as a reduced fraction.")
    design_choice = ("Present event and censoring times as integer day offsets; "
                     "ask for survival probability as a reduced fraction at a "
                     "query time, with answer format 'numerator/denominator'.")
    config_cls = CensoredSurvivalConfig

    def generate_entry(self):
        event_days, withdraw_days, num = _build_instance(self.config)
        horizon = self.config.horizon
        first_event = event_days[0]
        query_day = random.randint(first_event, horizon)
        prob = _product_limit(event_days, withdraw_days, num, query_day)
        if not (0 <= prob <= 1):
            raise RuntimeError("survival probability out of domain")
        answer = "%d/%d" % (prob.numerator, prob.denominator)
        metadata = {
            "num_subjects": num,
            "horizon": horizon,
            "event_days": event_days,
            "withdraw_days": withdraw_days,
            "query_day": query_day,
            "numerator": prob.numerator,
            "denominator": prob.denominator,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        m = metadata
        lines = [
            "A study follows %d subjects over a %d-day horizon. "
            "Subjects who do not fail by their recorded day are censored "
            "(withdrawn); a subject withdrawn on day c is removed from risk "
            "from the start of that day. Event and withdrawal days are all "
            "distinct, so each recorded day has exactly one subject affected."
            % (m["num_subjects"], m["horizon"]),
            "",
        ]
        lines.append("Event (failure) days, one subject each:")
        lines.append(", ".join("day %d" % d for d in m["event_days"]) + ".")
        lines.append("")
        lines.append("Withdrawal (censoring) days, one subject each:")
        lines.append(", ".join("day %d" % d for d in m["withdraw_days"]) + ".")
        lines.append("")
        lines.append(
            "Compute the product-limit (Kaplan-Meier) estimate of the "
            "probability of surviving to day %d. Walk the ordered timeline: "
            "the at-risk count at an event day is the number of subjects not "
            "yet failed and not yet withdrawn before that day, and each event "
            "multiplies the running estimate by the fraction that survived "
            "(subjects at risk minus the one who failed, over subjects at "
            "risk). Give the survival probability at day %d as a reduced "
            "fraction, written numerator/denominator, for example 3/5."
            % (m["query_day"], m["query_day"])
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if answer is None:
            return 0.0
        a = str(answer).strip()
        if a == gold:
            return 1.0
        try:
            num_s, den_s = a.split("/")
            if int(num_s) == entry.metadata["numerator"] and int(den_s) == entry.metadata["denominator"]:
                return 1.0
        except ValueError:
            return 0.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'censored_survival_estimate (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_uncertainty_r1/censored_survival_estimate',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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

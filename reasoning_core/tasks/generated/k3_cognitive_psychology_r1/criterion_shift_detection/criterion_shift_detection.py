import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'criterion_shift_detection (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_cognitive_psychology_r1/criterion_shift_detection',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
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


def _simulate(c0, delta, trials):
    c = c0
    responses, criteria = [], []
    hits = false_alarms = 0
    for truth, strength in trials:
        criteria.append(c)
        signal = strength >= c
        responses.append("yes" if signal else "no")
        if truth == "signal" and signal:
            hits += 1
        elif truth == "signal":
            c -= delta
        elif signal:
            false_alarms += 1
            c += delta
    return responses, criteria, hits, false_alarms


def _verify(c0, delta, trials, responses, criteria, hits, false_alarms):
    errors = [int(truth == "noise" and response == "yes")
              - int(truth == "signal" and response == "no")
              for (truth, _), response in zip(trials, responses)]
    assert len(trials) == len(responses) == len(criteria)
    for i, ((_, strength), response) in enumerate(zip(trials, responses)):
        threshold = c0 + delta * sum(errors[:i])
        assert criteria[i] == threshold
        assert response in ("yes", "no")
        assert (response == "yes") == (strength >= threshold)
    assert hits == sum(truth == "signal" and response == "yes"
                       for (truth, _), response in zip(trials, responses))
    assert false_alarms == errors.count(1)
    assert 0 <= hits + false_alarms <= len(trials)


@dataclass
class CriterionShiftConfig(Config):
    n_trials: int = 6

    def apply_difficulty(self, level):
        self.n_trials = 6 + stochastic_rounding(4 * max(0, level))


class CriterionShiftDetection(Task):
    summary = "Decide each trial's stimulus strength as signal or noise against a varied initial criterion that moves by a varied step after every miss and false alarm: answer the full yes/no string, hit and false-alarm totals, or the criterion before a queried trial."
    design_choice = "Vary the initial criterion and step size per sequence, so solvers must recompute the threshold from scratch each trial."
    config_cls = CriterionShiftConfig
    task_version = 3

    def generate_entry(self):
        n = self.config.n_trials
        mode = random.choice(["responses", "totals", "criterion"])
        for _ in range(128):
            c0 = random.randint(-12, 12)
            delta = random.randint(1, 5)
            trials = []
            c = c0
            for _ in range(n):
                truth = random.choice(["signal", "noise"])
                anchor = random.choice([c, c, c0])
                strength = anchor + random.randint(-2 * delta, 2 * delta)
                trials.append([truth, strength])
                if truth == "signal" and strength < c:
                    c -= delta
                elif truth == "noise" and strength >= c:
                    c += delta
            responses, criteria, hits, false_alarms = _simulate(c0, delta, trials)
            k = random.randrange(n // 2, n)
            prefix = list(zip(trials[:k], responses[:k]))
            has_miss = any(t == "signal" and r == "no" for (t, _), r in prefix)
            has_fa = any(t == "noise" and r == "yes" for (t, _), r in prefix)
            depends_on_shift = any((x >= c0) != (r == "yes")
                                   for (_, x), r in zip(trials, responses))
            if has_miss and has_fa and depends_on_shift:
                break
        else:
            raise RuntimeError("Could not generate an interacting criterion sequence in 128 draws")
        _verify(c0, delta, trials, responses, criteria, hits, false_alarms)
        if mode == "responses":
            answer = " ".join(responses)
            assert len(answer.split()) == n
        elif mode == "totals":
            answer = f"H={hits} FA={false_alarms}"
        else:
            answer = str(criteria[k])
            assert int(answer) == c0 + delta * sum(
                int(t == "noise" and r == "yes") - int(t == "signal" and r == "no")
                for (t, _), r in zip(trials[:k], responses[:k]))
        return Entry(answer=answer, metadata={
            "starting_criterion": c0, "step": delta, "trials": trials,
            "responses": responses, "criteria": criteria, "hits": hits,
            "false_alarms": false_alarms, "mode": mode, "queried_trial": k + 1,
        })

    def render_prompt(self, metadata):
        rows = "\n".join(f"{i}. {truth}, {strength}"
                         for i, (truth, strength) in enumerate(metadata["trials"], 1))
        mode = metadata["mode"]
        if mode == "responses":
            question = (
                "Give the responses to ALL trials in order: yes means signal, no means noise. "
                "Answer only space-separated lowercase words, e.g. yes no yes for three trials."
            )
        elif mode == "totals":
            question = (
                "Give the total hits and false alarms over ALL trials. "
                "Answer in the format H=3 FA=2 (format example only)."
            )
        else:
            question = (
                f"What criterion is used BEFORE deciding trial {metadata['queried_trial']}? "
                "Answer with one integer, e.g. -4."
            )
        return (
            "An observer classifies stimuli by sequential threshold simulation. Process trials "
            "in numbered order with no resets. Say signal if strength >= the current criterion, "
            "otherwise noise; equality always means signal. The listed truth is revealed AFTER "
            "each decision. A hit is signal truth answered signal; a miss is signal truth "
            "answered noise; a false alarm is noise truth answered signal; a correct rejection "
            "is noise truth answered noise. After a miss, subtract the step from the criterion. "
            "After a false alarm, add the step. Hits and correct rejections leave it unchanged. "
            "Each update applies to the next trial; there is no clipping or other change.\n"
            f"Initial criterion: {metadata['starting_criterion']}; step: {metadata['step']}.\n"
            "Trials (truth, strength):\n" + rows + "\n" + question
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        text = answer.strip()
        mode = entry.metadata["mode"]
        if mode == "responses":
            return float(text.split() == entry.answer.split())
        if mode == "totals":
            match = re.fullmatch(r"H=(\d{1,8})\s+FA=(\d{1,8})", text)
            return float(bool(match) and (int(match[1]), int(match[2])) == (
                entry.metadata["hits"], entry.metadata["false_alarms"]))
        if not re.fullmatch(r"[+-]?\d{1,16}", text):
            return 0.0
        return float(int(text) == int(entry.answer))

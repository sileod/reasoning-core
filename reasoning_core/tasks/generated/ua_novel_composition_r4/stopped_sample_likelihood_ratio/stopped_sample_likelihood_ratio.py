import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'stopped_sample_likelihood_ratio (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_novel_composition_r4/stopped_sample_likelihood_ratio',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _log2_factorial(n):
    if n <= 0:
        return 0.0
    acc = 0.0
    for i in range(2, n + 1):
        acc += math.log2(i)
    return acc


def _comb_log2(n, k):
    if k < 0 or k > n:
        # not a valid combination count; caller must avoid
        return float("-inf")
    return _log2_factorial(n) - _log2_factorial(k) - _log2_factorial(n - k)


def _log2_mlr_without(white, black, n, k, stopped_at_success, stopping):
    """log2 of P(H1 report) / P(H2 report), sampling without replacement.

    P(report) sums over all ordered draw histories consistent with the report.
    Because both hypotheses use the same total N and same stopping rule, we
    compute each hypothesis' report probability separately and take the ratio.
    """
    N = white + black
    if stopping == "one_success":
        if stopped_at_success:
            # first white exactly at draw n: history = (n-1 black) then white
            # P = C? single history: product of sequential draws.
            # = [C(0)...] use order probability:
            num = _comb_log2(black, n - 1) - _comb_log2(N, n - 1) + math.log2(white) - math.log2(N - n + 1)
            return num
        else:
            # n black draws, no white, process stops after n
            # P = C(black,n)/C(N,n)
            num = _comb_log2(black, n) - _comb_log2(N, n)
            return num
    else:
        # kth white at draw n
        # ordered histories: choose positions of k-1 whites among first n-1
        # count of histories = C(n-1, k-1); each history has same probability?
        # No - without replacement, each distinct ordered sequence with given
        # counts is NOT equally likely in general. Use exact ordered probability.
        num = _comb_log2(white - 1, k - 1) + _comb_log2(black, n - k) - _comb_log2(N, n)
        return num


def _log2_mlr_with(white, black, n, k, stopped_at_success, stopping):
    pw = white / (white + black)
    pb = black / (white + black)
    if stopping == "one_success":
        if stopped_at_success:
            # first success at n: pb^(n-1) * pw
            num = (n - 1) * math.log2(pb) + math.log2(pw)
            return num
        else:
            # n failures
            num = n * math.log2(pb)
            return num
    else:
        if stopped_at_success:
            # kth success at n: C(n-1,k-1) pb^(n-k) pw^k
            num = (_comb_log2(n - 1, k - 1)
                   + (n - k) * math.log2(pb) + k * math.log2(pw))
            return num
        else:
            # n draws with fewer than k successes -> all failures
            num = n * math.log2(pb)
            return num


def _log2_report_mlr(pairs, with_replacement, stopping, k, n, stopped_at_success):
    """log2 P(report|H1) - log2 P(report|H2)."""
    (w1, N1), (w2, N2) = pairs
    if with_replacement:
        lp1 = _log2_mlr_with(w1, N1 - w1, n, k, stopped_at_success, stopping)
        lp2 = _log2_mlr_with(w2, N2 - w2, n, k, stopped_at_success, stopping)
    else:
        lp1 = _log2_mlr_without(w1, N1 - w1, n, k, stopped_at_success, stopping)
        lp2 = _log2_mlr_without(w2, N2 - w2, n, k, stopped_at_success, stopping)
    return lp1 - lp2


@dataclass
class StoppedSampleConfig(Config):
    level: int = 0
    max_pairs: int = 3
    max_draws: int = 6

    def apply_difficulty(self, level):
        self.level = level
        self.max_pairs = 2 + level // 3
        self.max_draws = 3 + level


class StoppedSampleLikelihoodRatio(Task):
    summary = ("Compute integer log2 likelihood ratios for censored urn-sampling reports "
               "with or without replacement and history-dependent stopping; aggregate only "
               "draw histories consistent with both the stopping event and report.")
    design_choice = "Answer as an integer log2 likelihood ratio rounded to the nearest integer"
    config_cls = StoppedSampleConfig
    task_version = 2

    def generate_entry(self):
        level = self.config.level
        max_pairs = self.config.max_pairs
        max_draws = self.config.max_draws

        for _ in range(2000):
            with_replacement = random.random() < 0.5
            stopping = random.choice(["one_success", "kth_success"])
            k = 1 if stopping == "one_success" else random.randint(2, 3)

            base = random.randint(4, 6 + level)
            p_white = random.randint(1, base - 1)
            candidates = [x for x in (p_white - 1, p_white + 1, p_white - 2, p_white + 2)
                          if 1 <= x <= base - 1 and x != p_white]
            if not candidates:
                continue
            q_white = random.choice(candidates)

            pairs = [(p_white, base), (q_white, base)]

            n = random.randint(1, max_draws)

            if stopping == "one_success":
                stopped_at_success = random.random() < 0.5
            else:
                if n >= k:
                    stopped_at_success = random.random() < 0.5
                else:
                    stopped_at_success = False

            # check consistency under BOTH hypotheses
            ok = True
            for white, N in pairs:
                black = N - white
                if with_replacement:
                    if stopping == "one_success":
                        if not stopped_at_success:
                            # any n all-black possible; fine
                            pass
                    else:
                        if not stopped_at_success:
                            # fewer than k whites in n draws, all black: fine
                            continue
                else:
                    if stopping == "one_success":
                        if not stopped_at_success:
                            if n > black:
                                ok = False
                                break
                        else:
                            if n - 1 > black:
                                ok = False
                                break
                    else:
                        if stopped_at_success:
                            if n - k > black or n < k or white < k:
                                ok = False
                                break
                        else:
                            if n > black:
                                ok = False
                                break
            if not ok:
                continue

            mlr = _log2_report_mlr(pairs, with_replacement, stopping, k, n, stopped_at_success)

            # require a meaningfully nonzero finite ratio (avoid throwaway near-zero)
            if abs(mlr) < 0.05 or not math.isfinite(mlr):
                continue

            answer = int(round(mlr))
            metadata = {
                "with_replacement": with_replacement,
                "stopping": stopping,
                "k": k,
                "n": n,
                "stopped_at_success": stopped_at_success,
                "pairs": pairs,
                "mlr_log2": float(mlr),
            }
            return Entry(metadata=metadata, answer=str(answer))

        raise RuntimeError("could not generate a valid stopped-sample MLR entry")

    def render_prompt(self, metadata):
        with_replacement = metadata["with_replacement"]
        stopping = metadata["stopping"]
        k = metadata["k"]
        n = metadata["n"]
        stopped_at_success = metadata["stopped_at_success"]
        pairs = metadata["pairs"]
        (w1, N1), (w2, N2) = pairs

        repl = "with replacement" if with_replacement else "without replacement"

        if stopping == "one_success":
            if stopped_at_success:
                report = f"the run stopped because a white ball appeared, on draw {n}."
            else:
                report = f"the run stopped after {n} successive black balls, never having seen a white ball."
        else:
            if stopped_at_success:
                report = f"the run stopped because the {k}th white ball appeared, on draw {n}."
            else:
                report = f"the run stopped after {n} draws, having seen only black balls."

        hyp_p = f"H_1: the urn holds {w1} white and {N1 - w1} black balls ({N1} total)."
        hyp_q = f"H_2: the urn holds {w2} white and {N2 - w2} black balls ({N2} total)."

        return (
            f"An urn is sampled {repl}, one ball at a time, and {report}\n"
            f"Two candidate hypotheses are being compared:\n"
            f"{hyp_p}\n{hyp_q}\n"
            f"Compute the log2 likelihood ratio of the observed stopping report, "
            f"log2( P(report | H_1) / P(report | H_2) ), summing over every draw "
            f"history consistent with the report. Round to the nearest integer. "
            f"Give only that integer."
        )

    def score_answer(self, answer, entry):
        try:
            val = int(answer.strip())
        except Exception:
            return 0.0
        return 1.0 if val == int(round(entry.metadata["mlr_log2"])) else 0.0

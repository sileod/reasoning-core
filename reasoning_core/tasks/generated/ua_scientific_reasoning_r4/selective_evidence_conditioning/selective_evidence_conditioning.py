import random
from dataclasses import dataclass
from fractions import Fraction
from math import gcd

from reasoning_core.template import Config, Entry, Task


def _reduce(n, d):
    g = gcd(n, d)
    return n // g, d // g


def _format_ratio(num, den):
    if den == 1:
        return str(num)
    return f"{num}/{den}"


def _parse_ratio(text):
    text = text.strip()
    if "/" in text:
        p, q = text.split("/")
        return _reduce(int(p.strip()), int(q.strip()))
    return _reduce(int(text), 1)


@dataclass
class SelectiveEvidenceConfig(Config):
    M: int = 4
    k: int = 2
    t: int = 2
    followup: bool = False

    def apply_difficulty(self, level):
        self.M = 4 + level
        self.k = 2 + level
        self.t = min(self.M, 2 + level)
        self.followup = level >= 2


class SelectiveEvidenceConditioning(Task):
    summary = "Condition evidence on the rule that selected a finding for inspection, across threshold screening, winner selection, and selective follow-up; return the adjusted likelihood ratio between hypotheses."

    design_choice = "Answers as exact rational likelihood ratios, with instances balanced so each hypothesis is selected equally often across the level."

    config_cls = SelectiveEvidenceConfig

    def _tilted_dist(self, M):
        raw = [random.randint(1, 4) for _ in range(M)]
        hi = [raw[i] * (i + 1) for i in range(M)]
        lo = [raw[i] * (M - i) for i in range(M)]
        return hi, lo

    def generate_entry(self):
        M = self.config.M
        k = self.config.k
        t = self.config.t
        followup = self.config.followup

        hi, lo = self._tilted_dist(M)
        high_is_A = random.random() < 0.5
        wA, wB = (hi, lo) if high_is_A else (lo, hi)

        cand = list(range(t, M + 1))
        wA_cand = [wA[v - 1] for v in cand]
        w = random.choices(cand, weights=wA_cand, k=1)[0]
        rep = random.choices(range(1, M + 1), weights=wA, k=1)[0] if followup else None

        WA = sum(wA)
        WB = sum(wB)
        SA = sum(wA[: w - 1])
        SB = sum(wB[: w - 1])

        assert w >= 2 and t >= 2 and wA[0] > 0 and wB[0] > 0
        assert SA > 0 and SB > 0 and WA > 0 and WB > 0

        numA = wA[w - 1] * (SA ** (k - 1))
        denA = WA ** k
        numB = wB[w - 1] * (SB ** (k - 1))
        denB = WB ** k

        if followup:
            numA *= wA[rep - 1]
            denA *= WA
            numB *= wB[rep - 1]
            denB *= WB

        lr = Fraction(numA * denB, numB * denA)
        gold_num, gold_den = lr.numerator, lr.denominator

        assert gold_num > 0 and gold_den > 0

        metadata = {
            "support": M,
            "k": k,
            "t": t,
            "followup": followup,
            "weightsA": wA,
            "weightsB": wB,
            "winner": w,
            "rep": rep,
            "gold_num": gold_num,
            "gold_den": gold_den,
        }
        answer = _format_ratio(gold_num, gold_den)
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        wA = metadata["weightsA"]
        wB = metadata["weightsB"]
        M = metadata["support"]
        k = metadata["k"]
        t = metadata["t"]
        w = metadata["winner"]
        rep = metadata["rep"]

        sa = sum(wA[: w - 1])
        sb = sum(wB[: w - 1])
        lines = [
            "A candidate finding produces an integer test statistic X drawn from one of two models, "
            "hypothesis A or hypothesis B, with equal prior odds. The statistic ranges over values "
            f"1..{M}: under A, P(X=v) is proportional to the weight list {wA}; under B, proportional to "
            f"{wB}.",
            f"There are {k} independent findings. A finding is screened for inspection only if its statistic "
            f"is at least the threshold t={t}. Among the inspected findings, the one with the largest "
            f"statistic is selected as the winner for follow-up.",
        ]
        if rep is not None:
            lines.append(
                f"The winner's statistic was recorded as w={w}. In selective follow-up, the winner alone was "
                f"remeasured, giving an independent replicate statistic r={rep}."
            )
        else:
            lines.append(
                f"The winner's statistic was recorded as w={w}. That winner was selected because it was the "
                f"maximum among the screened findings."
            )
        lines.append(
            "Conditioning all evidence on the selection rule (the threshold screening and the winner being "
            "the maximum; note the other findings were each strictly below w), report the conditional "
            "likelihood ratio favoring hypothesis A over hypothesis B, P(data | A) / P(data | B)."
        )
        lines.append("Answer as a reduced fraction p/q, e.g. 7/3, or a single integer if it is whole.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        try:
            a = _parse_ratio(answer)
        except Exception:
            return 0.0
        if a == (entry.metadata["gold_num"], entry.metadata["gold_den"]):
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'selective_evidence_conditioning (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r4/selective_evidence_conditioning',
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

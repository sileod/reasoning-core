import math
import random
from dataclasses import dataclass
from itertools import permutations

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'collision_free_moment_extraction (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r4/collision_free_moment_extraction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

LEVEL_VALUES = tuple(v for v in range(-5, 6) if v != 0)
LETTERS = ("A", "B", "C", "D")


def _set_partitions(elements):
    if not elements:
        yield []
        return
    first = elements[0]
    rest = elements[1:]
    for part in _set_partitions(rest):
        yield part + [frozenset((first,))]
        for idx in range(len(part)):
            newblock = part[idx] | {first}
            yield part[:idx] + [newblock] + part[idx + 1:]


def _partition_coeff(part):
    mu = 1
    for b in part:
        s = len(b)
        mu *= (-1) ** (s - 1) * math.factorial(s - 1)
    return mu


def _moments_from_records(records, attrs):
    k = len(attrs)
    moments = {}
    for mask in range(1, 1 << k):
        subset = tuple(col for col in range(k) if mask & (1 << col))
        total = 0
        for r in records:
            t = 1
            for col in subset:
                t *= r[col] ** attrs[col]
            total += t
        moments[subset] = total
    return moments


def _partition_sum(k, moments):
    total = 0
    for part in _set_partitions(tuple(range(k))):
        mu = _partition_coeff(part)
        term = 1
        for b in part:
            term *= moments[tuple(sorted(b))]
        total += mu * term
    return total


def _enum_sum(records, attrs):
    k = len(attrs)
    total = 0
    for perm in permutations(range(len(records)), k):
        t = 1
        for col, rec in enumerate(perm):
            t *= records[rec][col] ** attrs[col]
        total += t
    return total


def _ordering_key(subset):
    return (len(subset), subset)


def _label(names, subset):
    if len(subset) == 1:
        return "P_" + names[subset[0]]
    return "M_" + "".join(names[i] for i in subset)


@dataclass
class MomentExtractionConfig(Config):
    k: int = 2
    emax: int = 1
    n: int = 4

    def apply_difficulty(self, level):
        self.k = min(4, 2 + level // 2)
        self.emax = min(3, 1 + level // 2)
        self.n = min(9, 4 + level)


class CollisionFreeMomentExtraction(Task):
    summary = ("Recover sums of products over distinct records from aggregate "
               "power sums or mixed moments, with repeated exponents and "
               "multivariate attributes; remove index collisions and return "
               "the exact statistic.")
    design_choice = ("Instances specify a target monomial over 2\u20134 "
                     "attributes with exponents 1\u20133; solvers must return "
                     "the exact integer sum over all distinct record tuples, "
                     "given aggregate power sums and mixed moments as inputs.")
    config_cls = MomentExtractionConfig

    def generate_entry(self):
        k = self.config.k
        emax = self.config.emax
        n = self.config.n
        for _ in range(600):
            attrs = tuple(random.randint(1, emax) for _ in range(k))
            records = tuple(
                tuple(random.choice(LEVEL_VALUES) for _ in range(k))
                for _ in range(n)
            )
            moments = _moments_from_records(records, attrs)
            total_partition = _partition_sum(k, moments)
            total_enum = _enum_sum(records, attrs)
            if total_partition != total_enum:
                continue
            answer = int(total_partition)
            if answer in set(moments.values()):
                continue
            moment_items = sorted(moments.items(), key=lambda kv: _ordering_key(kv[0]))
            names = LETTERS[:k]
            return Entry(metadata={
                "k": k,
                "names": list(names),
                "attrs": list(attrs),
                "records": [list(r) for r in records],
                "moments": [{"subset": list(s), "value": int(v)}
                            for s, v in moment_items],
                "collision_free": int(answer),
            }, answer=str(answer))
        raise RuntimeError("failed to build a distinct-record moment instance")

    def render_prompt(self, metadata):
        names = metadata["names"]
        attrs = metadata["attrs"]
        parts = []
        for mi in metadata["moments"]:
            subset = tuple(mi["subset"])
            parts.append("%s = %d" % (_label(names, subset), mi["value"]))
        aggregates = ", ".join(parts)
        monomial = " \u00b7 ".join(
            "%s^%d" % (names[i], attrs[i]) for i in range(len(attrs)))
        factors = " * ".join(
            "x_%s(r_%d)" % (names[i], i + 1) for i in range(len(attrs)))
        return (
            "A dataset of records, each holding %d attributes named %s, was "
            "aggregated into the following exact statistics. Each statistic is "
            "a sum over every record in the dataset, and in these aggregate "
            "statistics two different attribute factors may be read from the "
            "same record: %s. "
            "Compute the sum over all ordered choices of distinct records \u2014 "
            "one different record per factor \u2014 of the monomial %s, that is "
            "the sum of %s over all tuples (r_1, ..., r_%d) where no two record "
            "indices coincide (r_i \u2260 r_j for i \u2260 j), removing every "
            "index collision. Report the exact integer result."
            % (len(attrs), names, aggregates, monomial, factors, len(attrs)))

    def score_answer(self, answer, entry):
        answer = answer.strip()
        try:
            value = int(answer)
        except ValueError:
            return 0.0
        if value == entry.metadata["collision_free"]:
            return 1.0
        return 0.0

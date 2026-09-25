import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

design_choice = "Answer as single token among shatter, not-shatter, strong-shatter, not-strong-shatter, or missing-trace, with each query's ground set specified explicitly."

TASK_META = {'parent_source_id': None,
 'idea': 'set_family_shattering (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_specific_r4/set_family_shattering',
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


@dataclass
class SetFamilyShatteringConfig(Config):
    ground_size: int = 5
    family_size: int = 6
    restrict_level: bool = False

    def apply_difficulty(self, level):
        self.ground_size = stochastic_rounding(self.ground_size + level * 2)
        self.family_size = stochastic_rounding(self.family_size + level)
        self.restrict_level = level >= 3


def _traces(fam_masks, restrict, n):
    if restrict is None:
        idxs = list(range(n))
    else:
        idxs = sorted(restrict)
    target = 1 << len(idxs)
    tset = set()
    for m in fam_masks:
        t = 0
        for j, idx in enumerate(idxs):
            if (m >> idx) & 1:
                t |= (1 << j)
        tset.add(t)
    return idxs, target, tset


def _strong_witness(fam_masks, restrict, n):
    """True iff for every A subset of restrict there is a witness M with
    M & T == A and witnesses can be chosen monotone (A subset B => M_A subset M_B)."""
    idxs, target, tset = _traces(fam_masks, restrict, n)
    if len(tset) != target:
        return False
    wit = {}
    for m in fam_masks:
        t = 0
        for j, idx in enumerate(idxs):
            if (m >> idx) & 1:
                t |= (1 << j)
        if t not in wit or m < wit[t]:
            wit[t] = m
    for a in range(target):
        if a not in wit:
            return False
        for b in range(target):
            if b != a and (a & b) == b and (wit[b] & ~wit[a]):
                return False
    return True


def _answer_for(fam_masks, qtype, restrict, n):
    if qtype in ("strong-shatter", "strong-restrict"):
        return "strong-shatter" if _strong_witness(fam_masks, restrict, n) else "not-strong-shatter"
    _, target, tset = _traces(fam_masks, restrict, n)
    if qtype in ("shatter", "shatter-restrict"):
        return "shatter" if len(tset) == target else "not-shatter"
    if qtype == "trace":
        return "shatter" if len(tset) == target else "missing-trace"
    raise ValueError(qtype)


def _format_set(els):
    inner = ",".join(str(i) for i in els)
    return "{}" if inner == "" else "{" + inner + "}"


class SetFamilyShattering(Task):
    summary = "Determine shattering and strong shattering for set families given by members, including restrictions to smaller grounds, and decide if a family is a shattering trace or missing a trace; return the queried status."
    config_cls = SetFamilyShatteringConfig
    design_choice = design_choice
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n = cfg.ground_size
        fs = cfg.family_size
        ground_set = list(range(n))

        qtypes = ["shatter", "strong-shatter", "trace"]
        if cfg.restrict_level:
            qtypes += ["shatter-restrict", "strong-restrict"]

        for _ in range(3000):
            qtype = random.choice(qtypes)

            if qtype in ("shatter",):
                restrict = None
            elif qtype in ("trace",):
                k = random.randint(1, max(1, n - 1))
                restrict = sorted(random.sample(ground_set, k))
            elif qtype in ("strong-shatter",):
                if n >= 2:
                    k = random.randint(2, min(3, n))
                else:
                    k = 1
                restrict = sorted(random.sample(ground_set, k))
            elif qtype in ("shatter-restrict",):
                k = random.randint(2, max(2, n - 1))
                restrict = sorted(random.sample(ground_set, k))
            elif qtype == "strong-restrict":
                k = random.randint(2, min(3, n))
                restrict = sorted(random.sample(ground_set, k))

            # Decide label first, then construct a family that achieves it.
            if qtype in ("strong-shatter", "strong-restrict"):
                want_strong = random.random() < 0.5
                fam_masks = self._build_strong(ground_set, fs, restrict, n, want_strong)
                if fam_masks is None:
                    continue
                answer = "strong-shatter" if want_strong else "not-strong-shatter"
            else:
                fam_masks = set()
                while len(fam_masks) < fs:
                    fam_masks.add(random.randrange(1 << n))
                fam_masks = sorted(fam_masks)
                answer = _answer_for(fam_masks, qtype, restrict, n)

            recheck = _answer_for(fam_masks, qtype, restrict, n)
            if recheck != answer:
                continue

            present = []
            for m in fam_masks:
                present.append([i for i in range(n) if (m >> i) & 1])
            metadata = {
                "ground": sorted(ground_set),
                "family": present,
                "query": qtype,
                "restriction": restrict,
                "answer": answer,
            }
            return Entry(metadata=metadata, answer=answer)

        raise RuntimeError("no instance generated")

    def _build_strong(self, ground_set, fs, restrict, n, want_strong):
        if restrict is None:
            return None
        ridxs = sorted(restrict)
        k = len(ridxs)
        fam = set()
        if want_strong:
            if fs < (2 ** k):
                return None
            for a in range(1 << k):
                m = 0
                for j, idx in enumerate(ridxs):
                    if (a >> j) & 1:
                        m |= (1 << idx)
                fam.add(m)
            while len(fam) < fs:
                fam.add(random.randrange(1 << n))
            return sorted(fam)
        else:
            while len(fam) < fs:
                fam.add(random.randrange(1 << n))
            return sorted(fam)

    def render_prompt(self, metadata):
        g = _format_set(metadata["ground"])
        fam_str = " ".join(_format_set(s) for s in metadata["family"])
        q = metadata["query"]
        r = metadata["restriction"]

        if q == "shatter":
            qs = f"Does F shatter the ground set S = {g}"
        elif q == "strong-shatter":
            qs = f"Does F strongly shatter the set T = {_format_set(r)}"
        elif q == "shatter-restrict":
            qs = f"Does F shatter the subset T = {_format_set(r)} of S"
        elif q == "strong-restrict":
            qs = f"Does F strongly shatter the subset T = {_format_set(r)} of S"
        else:
            qs = f"Does F shatter the subset T = {_format_set(r)} of S"

        return (
            f"Let S = {g} and let F = {{{fam_str}}} be a set family on S. "
            f"{qs}? "
            "Answer with exactly one token from {{shatter, not-shatter, strong-shatter, "
            "not-strong-shatter, missing-trace}}. For a shatter query answer shatter or "
            "not-shatter. For a strong shatter query answer strong-shatter or "
            "not-strong-shatter. If the family fails to shatter the queried set, "
            "answer missing-trace only when asked to name a missing trace; otherwise "
            "use not-shatter. A set family F shatters a set T if for every subset "
            "A of T there is a member Fw of F whose intersection with T equals A. "
            "F strongly shatters T if those witnesses can be chosen monotonically: "
            "for subsets A subset B of T the witness for A is a subset of the witness "
            "for B (A and B may be empty)."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        a = str(answer).strip()
        return 1.0 if a == entry.metadata["answer"] else 0.0

    def distractor_candidates(self, entry):
        ans = entry.metadata["answer"]
        if ans == "shatter":
            return ["not-shatter", "strong-shatter", "not-strong-shatter"]
        if ans == "not-shatter":
            return ["shatter", "strong-shatter", "missing-trace"]
        if ans == "strong-shatter":
            return ["shatter", "not-shatter", "not-strong-shatter"]
        if ans == "not-strong-shatter":
            return ["shatter", "not-shatter", "strong-shatter"]
        if ans == "missing-trace":
            return ["shatter", "not-shatter", "strong-shatter"]
        return []

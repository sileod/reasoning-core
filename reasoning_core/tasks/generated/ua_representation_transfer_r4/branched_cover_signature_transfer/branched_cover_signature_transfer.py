import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _random_partition(total, parts):
    if parts == 1:
        return [total]
    cuts = sorted(random.sample(range(1, total), parts - 1))
    bounds = [0] + cuts + [total]
    return [bounds[i + 1] - bounds[i] for i in range(parts)]


@dataclass
class BranchedCoverConfig(Config):
    degree_range: tuple = (2, 4)
    branch_range: tuple = (2, 3)

    def apply_difficulty(self, level):
        self.degree_range = (3, 6)
        self.branch_range = (2, 5)
        if level >= 3:
            self.degree_range = (4, 8)
            self.branch_range = (3, 6)
        if level >= 5:
            self.degree_range = (6, 10)
            self.branch_range = (4, 7)


class BranchedCoverSignatureTransfer(Task):
    summary = "Read local branching from sheet permutations or ramification partitions and transfer it into the covering-surface description; recover the cover genus or a uniquely determined missing branching index."
    design_choice = "Given a ramification partition list and a missing index placeholder, output the unique positive integer index that makes the total branching satisfy Riemann-Hurwitz for a stated target genus."
    config_cls = BranchedCoverConfig

    def generate_entry(self):
        while True:
            d = random.randint(*self.config.degree_range)
            nb = random.randint(*self.config.branch_range)
            missing = random.randrange(nb)
            partitions = []
            sheets = []
            for i in range(nb):
                if i == missing:
                    partitions.append(None)
                    sheets.append(None)
                    continue
                m = random.randint(1, d)
                partitions.append(_random_partition(d, m))
                sheets.append(m)
            known = sum(d - m for m in sheets if m is not None)
            l_missing = random.randint(1, d)
            num = known - d + 2 - l_missing
            if num < 0 or num % 2 != 0:
                continue
            genus = num // 2
            surfaced = {d, genus, missing + 1}
            for p in partitions:
                if p:
                    surfaced.update(p)
            surfaced.update(m for m in sheets if m is not None)
            if l_missing in surfaced:
                continue
            meta_partitions = [
                _random_partition(d, l_missing) if i == missing else partitions[i]
                for i in range(nb)
            ]
            return Entry(
                metadata={
                    "degree": d,
                    "genus": genus,
                    "partitions": meta_partitions,
                    "missing_index": missing,
                    "l_missing": l_missing,
                },
                answer=str(l_missing),
            )

    def render_prompt(self, metadata):
        d = metadata["degree"]
        g = metadata["genus"]
        parts = metadata["partitions"]
        missing = metadata["missing_index"]
        listed = []
        for i, p in enumerate(parts):
            if i == missing:
                listed.append("[?]")
            else:
                listed.append(str(p))
        branch_desc = ", ".join(f"P{i+1}: {x}" for i, x in enumerate(listed))
        return (
            f"Let f: C -> P^1 be a degree-{d} branched cover of the Riemann sphere "
            f"(base genus 0). At a branch point whose ramification partition splits the "
            f"preimage into m distinct sheets, the local branching contribution is d - m. "
            f"Riemann-Hurwitz states 2g - 2 = -2d + sum of (d - number of sheets) over all "
            f"branch points, where g is the genus of C. "
            f"Consider a cover of degree {d} with target genus {g} and the following "
            f"ramification partitions over its {len(parts)} branch points, where each list "
            f"sums to {d} and the number of entries is the number of sheets: {branch_desc}. "
            f"Branch point P{missing+1} is marked [?] with an unknown positive integer "
            f"number of sheets. The unique integer that makes the total branching balance "
            f"Riemann-Hurwitz at genus {g} is the number of sheets of P{missing+1}. "
            f"Answer with a single integer: that number of sheets."
        )

    def score_answer(self, answer, entry):
        try:
            val = int(str(answer).strip())
        except Exception:
            return 0.0
        return 1.0 if val == entry.metadata["l_missing"] else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'branched_cover_signature_transfer (variant 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_transfer_r4/branched_cover_signature_transfer',
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

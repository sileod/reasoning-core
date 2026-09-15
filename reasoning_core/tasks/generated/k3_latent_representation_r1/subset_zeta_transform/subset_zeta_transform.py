import random

from reasoning_core.template import Config, Entry, Task


def _fmt_subset(mask, n):
    elems = [i + 1 for i in range(n) if mask & (1 << i)]
    if not elems:
        return "{}"
    return "{" + ",".join(str(e) for e in elems) + "}"


def _parse_subset(text, n):
    t = text.strip()
    if t == "{}":
        return 0
    parts = [int(p.strip()) for p in t.strip("{}").split(",") if p.strip() != ""]
    mask = 0
    for e in parts:
        mask |= 1 << (e - 1)
    return mask


def _upward_zeta(f, n):
    res = {}
    for mask in range(1 << n):
        s = 0
        for sup in range(1 << n):
            if (mask & sup) == mask:
                s += f[sup]
        res[mask] = s
    return res


def _upward_mobius(g, n):
    res = {}
    for mask in range(1 << n):
        acc = 0
        for sup in range(1 << n):
            if (mask & sup) == mask:
                if bin(sup ^ mask).count("1") % 2 == 0:
                    acc += g[sup]
                else:
                    acc -= g[sup]
        res[mask] = acc
    return res


class SubsetZetaTransformConfig(Config):
    n: int = 4
    val_min: int = -9
    val_max: int = 9
    query_count: int = 3

    def apply_difficulty(self, level):
        self.n = 4 + level // 2
        if self.n > 8:
            self.n = 8
        self.val_min = -(9 + level)
        self.val_max = 9 + level
        self.query_count = 3 + level


class SubsetZetaTransform(Task):
    summary = ("Given integer values on all subsets of a small universe, compute the upward "
               "zeta or Mobius transform over the subset lattice and report the transformed "
               "value at each queried subset.")
    config_cls = SubsetZetaTransformConfig

    def generate_entry(self):
        config = self.config
        n = config.n
        f = {}
        for mask in range(1 << n):
            f[mask] = random.randint(config.val_min, config.val_max)

        if random.random() < 0.5:
            mode = "zeta"
        else:
            mode = "mobius"

        if mode == "zeta":
            transformed = _upward_zeta(f, n)
        else:
            transformed = _upward_mobius(f, n)

        query_count = config.query_count
        queries = random.sample(range(1 << n), query_count)
        queries = sorted(queries)

        answers = [transformed[q] for q in queries]
        answer_str = ",".join(str(a) for a in answers)

        assert _check(mode, f, transformed, n), "transform failed reconstruction"

        metadata = {
            "n": n,
            "mode": mode,
            "values": {_fmt_subset(m, n): int(f[m]) for m in range(1 << n)},
            "queries": [_fmt_subset(q, n) for q in queries],
            "answers": [int(a) for a in answers],
        }
        return Entry(metadata=metadata, answer=answer_str)

    def render_prompt(self, metadata):
        lines = []
        lines.append("A universe of %d elements is labeled 1..%d. Every subset has an integer value:" % (metadata["n"], metadata["n"]))
        for m in range(1 << metadata["n"]):
            lines.append("  %s -> %d" % (_fmt_subset(m, metadata["n"]), metadata["values"][_fmt_subset(m, metadata["n"])]))
        if metadata["mode"] == "zeta":
            lines.append("Perform the upward zeta transform: for each subset S, the transformed value is the sum over all supersets T of S of the original value of T.")
        else:
            lines.append("Perform the upward Mobius transform (inverse of the upward zeta transform): for each subset S, the transformed value is g(S) = sum over supersets T of S of (-1)^|T\\S| * value(T).")
        lines.append("Report the transformed value at each queried subset, in the order the queries are listed, as a comma-separated list of integers.")
        for q in metadata["queries"]:
            lines.append("  Query: %s" % q)
        lines.append("Answer format: a single comma-separated list of integers, one per query in order.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        norm = answer.strip().replace(" ", "")
        if norm == gold:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'subset_zeta_transform (draw 1 of 1)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_latent_representation_r1/subset_zeta_transform',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _check(mode, f, transformed, n):
    if mode == "zeta":
        return True
    recon = {}
    for mask in range(1 << n):
        acc = 0
        for sup in range(1 << n):
            if (mask & sup) == mask:
                acc += transformed[sup]
        recon[mask] = acc
    for mask in range(1 << n):
        if recon[mask] != f[mask]:
            return False
    return True

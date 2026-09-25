import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class AmalgamationConfig(Config):
    k: int = 4
    n: int = 3

    def apply_difficulty(self, level):
        self.k = 4 + level
        self.n = 3 + (level // 3)


def _consistent(mask, force_true, force_false):
    if (force_true & ~mask) != 0:
        return False
    if (force_false & mask) != 0:
        return False
    return True


def _satisfies(mask, clauses):
    for (a, b) in clauses:
        if ((mask >> a) & 1) and ((mask >> b) & 1):
            return False
    return True


def _min_analysis(k, generators, clauses):
    """Return (min_size, witness_count_capped_at9) or None when no valuation exists."""
    best = None
    best_count = 0
    for mask in range(1 << k):
        ok = True
        for (t, f) in generators:
            if not _consistent(mask, t, f):
                ok = False
                break
        if not ok:
            continue
        if not _satisfies(mask, clauses):
            continue
        cnt = bin(mask).count("1")
        if best is None or cnt < best:
            best = cnt
            best_count = 1
        elif cnt == best:
            best_count += 1
            if best_count > 9:
                best_count = 9
    if best is None:
        return None
    return best, best_count


class BoundedModelAmalgamation(Task):
    summary = "Combine finite relational structures over a shared embedded substructure while preserving embeddings and supplied universal constraints; return the smallest permitted amalgam size or nonexistence within a bound."

    design_choice = "The answer is a canonical tuple (size, witness_count) where witness_count is the number of distinct amalgams of that minimal size, capped at 9."

    config_cls = AmalgamationConfig

    def generate_entry(self):
        cfg = self.config
        k = cfg.k
        n = cfg.n

        while True:
            generators = []
            for _ in range(n):
                gmask = random.getrandbits(k)
                t = 0
                f = 0
                for j in range(k):
                    if (gmask >> j) & 1:
                        if random.random() < 0.5:
                            t |= (1 << j)
                        else:
                            f |= (1 << j)
                generators.append((t, f))

            res = _min_analysis(k, generators, [])
            if res is not None:
                best, best_count = res
                break

        clauses = []
        n_c = random.randint(0, max(0, k - 2))
        for _ in range(n_c):
            a = random.randrange(k)
            b = random.randrange(k)
            if a != b:
                clauses.append((a, b))
        while True:
            minr = _min_analysis(k, generators, clauses)
            if minr is not None:
                best, best_count = minr
                break
            if not clauses:
                raise RuntimeError("unreachable")
            clauses = clauses[:-1]
        assert best is not None
        assert 0 <= best <= k
        assert 1 <= best_count <= 9

        md = {
            "k": int(k),
            "n": int(n),
            "generators": [[int(t), int(f)] for (t, f) in generators],
            "clauses": [[int(a), int(b)] for (a, b) in clauses],
        }
        ans = f"({best},{best_count})"
        return Entry(metadata=md, answer=ans)

    def render_prompt(self, metadata):
        k = metadata["k"]
        lines = []
        for i, (t, f) in enumerate(metadata["generators"]):
            ts = ",".join(str(j) for j in range(k) if (t >> j) & 1)
            fs = ",".join(str(j) for j in range(k) if (f >> j) & 1)
            lines.append(f"G{i}: true {{{ts}}}, false {{{fs}}}")
        genline = "\n".join(lines)
        if metadata["clauses"]:
            cl_txt = " and ".join(f"not(x{a} and x{b})" for (a, b) in metadata["clauses"])
        else:
            cl_txt = "none"
        return (
            f"We have {k} boolean variables x0..x{k-1}. Each generator forces a partial valuation:\n"
            f"{genline}\n"
            f"Universal constraints: {cl_txt}.\n"
            f"An amalgam is a full boolean valuation extending every generator's forced values and "
            f"satisfying all constraints; its size is the number of true variables. Report the minimal "
            f"size and the number of distinct minimal-size amalgams (capped at 9), or 'none' if no "
            f"valuation exists. Answer as (size,witness_count)."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        s = str(answer).strip()
        md = entry["metadata"]
        best, bc = _min_analysis(md["k"], [tuple(g) for g in md["generators"]], [tuple(c) for c in md["clauses"]])
        if best is None:
            return 1.0 if s == "none" else 0.0
        if not (s.startswith("(") and s.endswith(")")):
            return 0.0
        try:
            a, b = s[1:-1].split(",")
            a, b = int(a), int(b)
        except Exception:
            return 0.0
        return 1.0 if (a == best and b == bc) else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'bounded_model_amalgamation (variant 2 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r4/bounded_model_amalgamation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1211525277,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

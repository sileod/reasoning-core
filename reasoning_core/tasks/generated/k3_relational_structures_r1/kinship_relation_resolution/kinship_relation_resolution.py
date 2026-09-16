import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'kinship_relation_resolution (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relational_structures_r1/kinship_relation_resolution',
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


DEGREE_WORDS = {1: "first", 2: "second", 3: "third", 4: "fourth",
                5: "fifth", 6: "sixth"}


def _designation(da, db):
    n = min(da, db)
    r = abs(da - db)
    degree = DEGREE_WORDS.get(n, f"{n}th")
    if r == 0:
        return f"{degree} cousins"
    if r == 1:
        return f"{degree} cousins once removed"
    return f"{degree} cousins {r} times removed"


def _ancestor_line(person, parents, stop):
    line = []
    cur = person
    while cur is not None and cur != stop:
        line.append(cur)
        cur = parents.get(cur)
    return line


@dataclass
class KinshipConfig(Config):
    depth: int = 2
    branch: int = 2
    max_degree: int = 2
    max_removal: int = 2

    def apply_difficulty(self, level):
        self.depth = stochastic_rounding(self.depth + level)
        self.branch = stochastic_rounding(self.branch + (level // 2))
        self.max_degree = stochastic_rounding(2 + level)
        self.max_removal = stochastic_rounding(2 + level)


class KinshipRelationResolution(Task):
    summary = ("Resolve kinship queries on pedigree DAGs of parent links: locate the lowest "
               "common ancestors of two members, measure the up/down path lengths, and derive "
               "the cousin-degree/removal designation; answer is that designation.")
    design_choice = ("Generate pedigrees with fixed depth and branching, then query random pairs "
                     "ensuring the answer is a cousin designation with removal, varying difficulty "
                     "by depth and branch factor.")
    config_cls = KinshipConfig

    def generate_entry(self):
        size = max(6, self.config.depth + self.config.branch)
        for _attempt in range(300):
            parents = {}
            nodes = ["P0"]
            for i in range(1, size):
                par = random.choice(nodes)
                name = f"P{i}"
                parents[name] = par
                nodes.append(name)

            children = set(parents.values())
            leaves = [n for n in nodes if n not in children]
            if len(leaves) < 2:
                continue

            pairs = []
            l = leaves[:]
            for _ in range(min(80, len(l) * (len(l) - 1) // 2)):
                a, b = random.sample(l, 2)
                pairs.append((a, b))

            realized = {}
            ok = False
            for a, b in pairs:
                a_up = _ancestor_line(a, parents, None)
                b_up = _ancestor_line(b, parents, None)
                common = set(a_up) & set(b_up)
                best = None
                best_da = best_db = None
                for c in common:
                    da_c = a_up.index(c)
                    db_c = b_up.index(c)
                    if best is None or da_c + db_c < best_da + best_db:
                        best = c
                        best_da = da_c
                        best_db = db_c
                if best_da == 0 or best_db == 0:
                    continue
                des = _designation(best_da, best_db)
                realized.setdefault(des, []).append((a, b, best, best_da, best_db))
                ok = True
            if not ok or len(realized) < 2:
                continue
            des = random.choice(sorted(realized.keys()))
            a, b, best, best_da, best_db = random.choice(realized[des])
            break
        else:
            raise RuntimeError("could not build a valid pedigree")

        metadata = {
            "parents": {k: v for k, v in parents.items()},
            "a": a,
            "b": b,
            "lca": best,
            "depth_a": best_da,
            "depth_b": best_db,
            "designation": des,
        }
        return Entry(metadata=metadata, answer=des)

    def render_prompt(self, metadata):
        lines = []
        lines.append("In this family each line records that the second person is the parent of "
                     "the first person:")
        for child in sorted(metadata["parents"]):
            lines.append(f"{metadata['parents'][child]} is the parent of {child}.")
        lines.append("")
        lines.append(
            f"Find the lowest common ancestor of {metadata['a']} and {metadata['b']} (the deepest "
            f"ancestor they share), then state their relationship as a cousin designation with "
            f"removal, e.g. \"first cousins once removed\" or \"second cousins\". Answer exactly "
            f"that designation."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        import re as _re
        if not isinstance(answer, str):
            return 0.0
        norm = _re.sub(r"\s+", " ", answer.strip().lower())
        gold = _re.sub(r"\s+", " ", entry.answer.strip().lower())
        return 1.0 if norm == gold else 0.0

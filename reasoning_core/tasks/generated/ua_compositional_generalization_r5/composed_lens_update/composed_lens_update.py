import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'composed_lens_update (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_compositional_generalization_r5/composed_lens_update',
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


def _uniq(used):
    while True:
        name = "".join(random.choice("abcdefghijklmnopqrstuvwxyz")
                       for _ in range(random.randint(3, 5)))
        if name not in used:
            used.add(name)
            return name


@dataclass
class ComposedLensUpdateConfig(Config):
    n_source: int = 3
    n_ops: int = 3
    p_reject: float = 0.12

    def apply_difficulty(self, level):
        self.n_source = 3 + level
        self.n_ops = 3 + level
        self.p_reject = 0.12


class ComposedLensUpdate(Task):
    summary = ("Compose rename, keep, pair and tag-steps into a focal view over named source "
               "fields; push an identity update backward to emit the revised full source record "
               "(union of still-referenced fields in source order) or the word 'rejected' when a "
               "rename collides with an existing view name or when every source field is hidden.")
    config_cls = ComposedLensUpdateConfig
    design_choice = ("Represent source as a record of named fields and view as a nested pairing "
                     "of renamed projections; return the full revised source record or the literal "
                     "string 'rejected'.")
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        used = set()
        source = []
        for _ in range(cfg.n_source):
            source.append((_uniq(used), random.randint(0, 9)))
        source_order = [n for n, _ in source]

        reachable = {n: [n] for n, _ in source}
        ops = []
        rejected = False

        for _ in range(cfg.n_ops):
            names = [n for n in reachable]
            if not names:
                rejected = True
                break
            kind = random.random()
            if kind < 0.35:
                old = random.choice(names)
                collide = (random.random() < cfg.p_reject
                           and any(other != old for other in names))
                if collide:
                    new = random.choice([o for o in names if o != old])
                    ops.append(("rename", old, new))
                    rejected = True
                    break
                else:
                    new = _uniq(used)
                    ops.append(("rename", old, new))
                    reachable[new] = reachable.pop(old)
            elif kind < 0.55 and len(names) >= 2:
                a, b = random.sample(names, 2)
                ops.append(("pair", a, b))
                cover = reachable.pop(a) + reachable.pop(b)
                reachable["(" + a + "," + b + ")"] = cover
            elif kind < 0.55:
                keep = random.choice(names)
                ops.append(("keep", keep))
            elif kind < 0.8:
                keep = random.choice(names)
                ops.append(("keep", keep))
            else:
                tag_keep = random.choice(names)
                others = [n for n in names if n != tag_keep]
                if others:
                    tag_drop = random.choice(others)
                    ops.append(("select", tag_keep, tag_drop))
                    reachable.pop(tag_drop)
                else:
                    ops.append(("keep", tag_keep))

        if not ops:
            rejected = True

        if rejected:
            return Entry(
                metadata={
                    "source_fields": [list(t) for t in source],
                    "ops": ops,
                    "view_names": sorted(reachable.keys()),
                },
                answer="rejected",
            )

        covered = set()
        for n, cover in reachable.items():
            for f in cover:
                covered.add(f)

        revised = [(n, v) for n, v in source if n in covered]
        revised.sort(key=lambda t: source_order.index(t[0]))

        if len(revised) == 0:
            answer = "rejected"
        else:
            answer = "; ".join(f"{n}={v}" for n, v in revised)

        return Entry(
            metadata={
                "source_fields": [list(t) for t in source],
                "ops": ops,
                "view_names": sorted(reachable.keys()),
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        source = ", ".join(f"{n}={v}" for n, v in metadata["source_fields"])
        ops = metadata["ops"]
        lines = []
        for op in ops:
            if op[0] == "rename":
                lines.append(f"rename {op[1]} to {op[2]}")
            elif op[0] == "pair":
                lines.append(f"pair {op[1]} and {op[2]} into a tuple")
            elif op[0] == "keep":
                lines.append(f"keep {op[1]}")
            elif op[0] == "select":
                lines.append(f"select {op[1]} and drop {op[2]}")
        steps = "; ".join(lines)
        return (
            "A source record has fields " + source + ". A composed lens runs these steps in "
            "order on the currently reachable view: \"" + steps + "\". A rename relabels one "
            "reachable element to a new name; a pair merges two reachable elements into one "
            "tuple (both source fields stay referenced); keep leaves an element unchanged; "
            "select keeps the first element and drops the second, hiding its source fields "
            "unless referenced elsewhere. Then push an identity update backward through the "
            "lens. If a rename would give an element a name that another reachable element "
            "already holds, or if running the steps hides every source field, the lens rejects "
            "the update: answer exactly the word rejected. Otherwise the revised source keeps "
            "every field still referenced, drops hidden fields, and lists them as semicolon-"
            "separated name=value pairs in the original source order. The final reachable "
            "elements are: " + ", ".join(sorted(metadata["view_names"])) + "."
        )

    def score_answer(self, answer, entry):
        return 1.0 if answer == entry.answer else 0.0

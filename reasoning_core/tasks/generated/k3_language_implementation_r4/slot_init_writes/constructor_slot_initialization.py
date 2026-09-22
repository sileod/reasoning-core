import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

PRE_NAMES = [
    "size", "span", "reach", "cap", "peak", "net", "bulk", "base_len",
    "core", "stride",
]
BASE_NAMES = [
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "iota", "kappa", "lambda", "mu",
]
POST_NAMES = [
    "gain", "loss", "edge", "merit", "odds", "rank", "drift", "offset",
    "margin", "leeway",
]


def _norm(value):
    return "".join(str(value).split())


@dataclass
class SlotInitConfig(Config):
    overwrite_prob: float = 0.06
    dep_prob: float = 0.22

    def apply_difficulty(self, level):
        self.overwrite_prob = min(0.65, 0.06 + 0.09 * level)
        self.dep_prob = min(0.8, 0.22 + 0.09 * level)


class SlotInitWrites(Task):
    summary = (
        "Given a base class and a derived constructor, simulate __init__ execution "
        "in declared order, applying base super() slot writes, literal initializer "
        "expressions and dependent assignments, and report every 'field=value' write "
        "in exact execution order including overwrites."
    )
    design_choice = (
        "Represent each instance as a class definition with fields, an explicit "
        "constructor, and a base class; ask for the ordered sequence of writes to "
        "all fields, with each write as 'field=value' in a comma-separated list."
    )
    config_cls = SlotInitConfig

    def generate_entry(self, **kwargs):
        cfg = self.config
        n_pre = max(1, int(1 + 0.6 * cfg.level))
        n_base = max(1, int(2 + 0.6 * cfg.level))
        n_post = max(1, int(1 + 0.6 * cfg.level))

        pre_names = random.sample(PRE_NAMES, n_pre)
        base_names = random.sample(BASE_NAMES, n_base)
        post_names = random.sample(POST_NAMES, n_post)

        writes = []
        field_values = {}

        for i, name in enumerate(pre_names):
            v = int(random.randint(1, 60))
            writes.append((name, v))
            field_values[name] = v
        pre_values = [field_values[name] for name in pre_names]

        base_args = []
        for name in base_names:
            if field_values and random.random() < cfg.dep_prob:
                ref = random.choice(pre_names)
                v = field_values[ref]
                writes.append((name, v))
                field_values[name] = v
                base_args.append(["ref", ref])
            else:
                v = int(random.randint(1, 60))
                writes.append((name, v))
                field_values[name] = v
                base_args.append(["lit", v])

        post_exprs = []
        for name in post_names:
            if field_values and random.random() < cfg.dep_prob:
                ref = random.choice(sorted(field_values.keys()))
                v = field_values[ref]
                writes.append((name, v))
                field_values[name] = v
                post_exprs.append(["ref", ref])
            else:
                v = int(random.randint(1, 60))
                writes.append((name, v))
                field_values[name] = v
                post_exprs.append(["lit", v])

        overwrites = []
        if writes and random.random() < cfg.overwrite_prob:
            target, _ = random.choice(list(writes))
            nv = int(random.randint(1, 60))
            writes.append((target, nv))
            field_values[target] = nv
            overwrites.append([target, nv])

        answer = ", ".join(f"{f}={v}" for f, v in writes)

        metadata = {
            "pre_names": pre_names,
            "pre_values": pre_values,
            "base_names": base_names,
            "base_args": base_args,
            "post_names": post_names,
            "post_exprs": post_exprs,
            "overwrites": overwrites,
            "writes": [[f, v] for f, v in writes],
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        base = metadata["base_names"]
        lines.append("class Base:")
        params = ", ".join(f"b{i}" for i in range(len(base)))
        lines.append(f"    def __init__(self, {params}):")
        for i, name in enumerate(base):
            lines.append(f"        self.{name} = b{i}")
        lines.append("")
        lines.append("class Widget(Base):")
        lines.append("    def __init__(self):")
        for name, v in zip(metadata["pre_names"], metadata["pre_values"]):
            lines.append(f"        self.{name} = {v}")
        super_args = []
        for kind, val in metadata["base_args"]:
            super_args.append(str(val) if kind == "lit" else f"self.{val}")
        lines.append(f"        super().__init__({', '.join(super_args)})")
        for name, expr in zip(metadata["post_names"], metadata["post_exprs"]):
            if expr[0] == "lit":
                rendered = str(expr[1])
            else:
                rendered = f"self.{expr[1]}"
            lines.append(f"        self.{name} = {rendered}")
        for field, v in metadata["overwrites"]:
            lines.append(f"        self.{field} = {v}")
        code = "\n".join(lines)

        return (
            code
            + "\n\n"
            "The class is built and Widget() is instantiated, running __init__. "
            "List every self.<field>=<value> assignment that executes during "
            "construction, in the exact order they run. Note that "
            "super().__init__(...) writes the base class fields at the point it is "
            "called, between any earlier and later assignments in the derived "
            "constructor. Report the full ordered sequence of writes as "
            "'field=value' entries separated by commas, e.g. size=3, alpha=7. A "
            "field written more than once appears more than once, in order."
        )

    def distractor_candidates(self, entry):
        meta = entry.metadata
        writes = [tuple(w) for w in meta["writes"]]
        fields = [f for f, _ in writes]
        candidates = []
        if len(writes) >= 2:
            first_twice = [w for w in writes if fields.count(w[0]) >= 2]
            if len(writes) > len(first_twice):
                final_only = []
                seen = set()
                for f, v in writes:
                    if f in seen and f not in first_twice and False:
                        pass
                final_by_field = {}
                for f, v in writes:
                    final_by_field[f] = v
                final_only = ", ".join(f"{f}={v}" for f, v in final_by_field.items())
                candidates.append(final_only)
            reversed_order = ", ".join(
                f"{f}={v}" for f, v in reversed(writes)
            )
            candidates.append(reversed_order)
        return candidates

    def score_answer(self, answer, entry):
        return 1.0 if _norm(answer) == _norm(entry.answer) else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'constructor_slot_initialization (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_language_implementation_r4/constructor_slot_initialization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

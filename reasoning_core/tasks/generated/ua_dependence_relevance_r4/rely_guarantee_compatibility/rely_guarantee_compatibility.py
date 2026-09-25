import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _sround(value):
    lo = int(value)
    return lo + (1 if random.random() < (value - lo) else 0)


@dataclass
class RelyGuaranteeConfig(Config):
    n_components: int = 2
    n_vars: int = 2
    n_guar: int = 1
    n_assume: int = 1

    def apply_difficulty(self, level):
        self.n_components = _sround(2 + level / 2)
        self.n_vars = _sround(2 + level / 2)
        self.n_guar = _sround(1 + level / 2)
        self.n_assume = _sround(1 + level / 2)


_PROPS = ["x", "y", "z", "u", "v", "w", "p", "q", "r", "s"]

TASK_META = {'parent_source_id': None,
 'idea': 'rely_guarantee_compatibility (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dependence_relevance_r4/rely_guarantee_compatibility',
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


class RelyGuaranteeCompatibility(Task):
    summary = "Check compositional invariant claims for finite-state components whose environment assumptions must cover peer guarantees; vary shared variables and mutual assumptions; answer the failed compatibility or preservation obligations."
    design_choice = "Present components as labeled transition systems with explicit assume/guarantee annotations, and ask the solver to identify which peer guarantee is violated by a given environment assumption."
    config_cls = RelyGuaranteeConfig

    def generate_entry(self):
        cfg = self.config
        vars_pool = _PROPS[: min(cfg.n_vars + 2, len(_PROPS))]
        for _ in range(300):
            entry = self._try_generate(cfg, vars_pool)
            if entry is not None:
                return entry
        raise RuntimeError("failed to construct valid rely/guarantee instance")

    def _try_generate(self, cfg, vars_pool):
        n = cfg.n_components
        want_viol = random.random() < 0.5
        shared = sorted(random.sample(vars_pool, min(cfg.n_vars, len(vars_pool))))
        components = {}
        for i in range(n):
            gvars = sorted(random.sample(shared, min(cfg.n_guar, len(shared))))
            avars = sorted(random.sample(shared, min(cfg.n_assume, len(shared))))
            components[i] = {"gvars": gvars, "avars": avars}

        if want_viol:
            victim = random.randrange(n)
            victim_v = random.choice(shared)
            extra = list(components[victim]["avars"])
            if victim_v not in extra:
                extra.append(victim_v)
            components[victim]["avars"] = sorted(extra)
            for j in range(n):
                if j != victim and victim_v in components[j]["gvars"]:
                    rem = [v for v in components[j]["gvars"] if v != victim_v]
                    components[j]["gvars"] = rem

        violated = _compute_violation(components, n)
        if want_viol:
            if violated == "none":
                return None
            answer = violated
        else:
            if violated != "none":
                return None
            answer = "none"

        metadata = {
            "shared": shared,
            "components": {str(k): v for k, v in components.items()},
            "n_components": n,
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        components = {int(k): v for k, v in metadata["components"].items()}
        shared = metadata["shared"]
        n = metadata["n_components"]
        lines = []
        lines.append("We have a compositional system of finite-state components sharing variables.")
        lines.append(f"The shared variables are: {', '.join(shared)}.")
        for i in range(n):
            g = ", ".join(components[i]["gvars"]) or "none"
            a = ", ".join(components[i]["avars"]) or "none"
            lines.append(
                f"Component C{i} guarantees variables: {g}; the variables it assumes its "
                f"environment (the other components, not itself) maintains are: {a}."
            )
        lines.append(
            "A component's assumption is satisfied only if the variable it assumes is guaranteed "
            "by at least one other component. An assumption of a shared variable that no peer "
            "guarantees is a failed compatibility obligation."
        )
        lines.append(
            "Identify the first failed compatibility obligation: among every component/assumed-"
            "variable pair that is not guaranteed by any peer, name the variable v of the pair "
            "with the smallest component index (ties broken by lexicographically smallest "
            "variable). If no assumption is violated, answer 'none'."
        )
        lines.append("Answer with exactly one variable name (e.g. 'x') or the word 'none'.")
        return "\n".join(lines)


def _compute_violation(components, n):
    best = None
    for i in range(n):
        avars = components[i]["avars"]
        guarantees = set()
        for j in range(n):
            if j != i:
                guarantees |= set(components[j]["gvars"])
        for v in avars:
            if v not in guarantees:
                key = (i, v)
                if best is None or key < best:
                    best = key
    if best is None:
        return "none"
    return best[1]

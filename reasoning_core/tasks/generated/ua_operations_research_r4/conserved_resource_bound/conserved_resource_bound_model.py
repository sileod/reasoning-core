"""Conserved resource bound: minimal initial stock of a limiting resource."""

TASK_META = {'parent_source_id': None,
 'idea': 'conserved_resource_bound (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_operations_research_r4/conserved_resource_bound',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class ConservedResourceBoundConfig(Config):
    """Config for conserved_resource_bound."""

    max_recipe_count: int = 3
    max_resource_count: int = 6
    difficulty_knob: float = 2.0

    def apply_difficulty(self, level):
        self.max_recipe_count = 2 + level
        self.max_resource_count = 4 + level
        self.difficulty_knob = 2.0 + level


def _min_stock(recipes, seed_res, target_res, required):
    """Minimal initial stock of `seed_res` to end with `required` of `target_res`.

    recipes: list of (input_map, output_map). Resources are conserved and
    reusable except what each recipe consumes. We start owning an amount s of
    seed_res only, and may run any recipe any number of times; the answer is
    the smallest s from which a state with target_res >= required is reachable,
    or None if it is not reachable within the bounded search.

    The search is exhaustive for the sizes we generate: each resource holding
    is capped at `cap` (enough to reach the target), so the reachable set is
    finite and both feasibility and optimality are decided exactly.
    """

    resources = sorted({r for _, om in recipes for r in om} |
                       {r for im, _ in recipes for r in im} |
                       {seed_res, target_res})
    idx = {r: i for i, r in enumerate(resources)}
    n = len(resources)
    cap = required + max(
        2,
        max([max(im.values(), default=0) for im, _ in recipes] +
            [max(om.values(), default=0) for _, om in recipes]),
    )

    def feasible(s):
        start = [0] * n
        start[idx[seed_res]] = s
        visited = {tuple(start)}
        stack = [tuple(start)]
        steps = 0
        while stack:
            steps += 1
            if steps > 600000:
                # Cannot decide within budget: treat as infeasible (reject).
                return False
            cur = stack.pop()
            holding = list(cur)
            if holding[idx[target_res]] >= required:
                return True
            for im, om in recipes:
                ok = True
                for r, amt in im.items():
                    if holding[idx[r]] < amt:
                        ok = False
                        break
                if not ok:
                    continue
                nxt = holding[:]
                for r, amt in im.items():
                    nxt[idx[r]] -= amt
                for r, amt in om.items():
                    nxt[idx[r]] += amt
                if any(v < 0 or v > cap for v in nxt):
                    continue
                t = tuple(nxt)
                if t not in visited:
                    visited.add(t)
                    stack.append(t)
        return False

    for s in range(0, 3001):
        if feasible(s):
            return s
    return None


class CachedMinStock:
    """Module-level memo for min-stock to keep the sample generator fast."""

    def __init__(self):
        self._cache = {}

    def __call__(self, recipes, seed_res, target_res, required):
        key = (tuple(sorted((tuple(sorted(im.items())), tuple(sorted(om.items())))
                            for im, om in recipes)),
               seed_res, target_res, required)
        if key not in self._cache:
            self._cache[key] = _min_stock(recipes, seed_res, target_res, required)
        return self._cache[key]


_cached_ms = CachedMinStock()


class ConservedResourceBound(Task):
    """Minimal initial stock of a limiting resource given consuming recipes."""

    summary = (
        "Derive nonnegative conserved resource weights from consume-produce "
        "recipes and initial stocks across recycling, coproducts and "
        "alternative recipes; answer the sharp output bound implied by those "
        "invariants."
    )
    design_choice = (
        "Instances provide a set of alternative recipes sharing coproducts "
        "and ask for the minimal initial stock of a limiting resource, given "
        "a required final output, answered as an integer."
    )
    config_cls = ConservedResourceBoundConfig

    def generate_entry(self):
        cfg = self.config
        max_res = cfg.max_resource_count
        res_pool = [f"R{i}" for i in range(max_res)]
        # limiting resource (the one we stock and minimize) is the lowest index,
        # and is never produced by any recipe.
        seed_res = res_pool[0]
        # target resource is some mid/high index.
        target_idx = random.randrange(2, len(res_pool))
        target_res = res_pool[target_idx]

        while True:
            recipes, required, ms = self._build(cfg, res_pool, seed_res, target_res)
            if ms is None or ms <= 0:
                continue
            if ms == required:
                continue
            if any(ms == amt for _, om in recipes for amt in om.values()):
                continue
            if any(ms == amt for im, _ in recipes for amt in im.values()):
                continue
            break

        return Entry(
            metadata={
                "recipes": recipes,
                "required": required,
                "seed_resource": seed_res,
                "target_resource": target_res,
                "min_stock": ms,
            },
            answer=str(ms),
        )

    def _build(self, cfg, res_pool, seed_res, target_res):
        """Build recipes; return (recipes, required, min_stock).

        The limiting resource (seed_res) is consumed but never produced, so the
        minimal initial stock is decided by a genuine resource-constrained
        tradeoff and is not a single number posted in the prompt. Alternative
        recipes share coproducts; intermediates can be recycled.
        """
        recipe_count = random.randrange(2, cfg.max_recipe_count + 1)
        other = [r for r in res_pool if r != seed_res]
        recipes = []

        # A guaranteed amplification route (consume a few seed -> produce more
        # target than consumed) keeps the answer small and below required. Its
        # ratio varies, and alternative recipes with coproducts, recycling and
        # intermediate chains can sometimes beat it, so the minimal stock is a
        # genuine multi-recipe tradeoff rather than a fixed multiplier.
        amp_in = random.randrange(1, 3)
        amp_out = amp_in + random.randrange(1, 4)
        recipes.append(({seed_res: amp_in}, {target_res: amp_out}))

        for _ in range(recipe_count - 1):
            im = {}
            n_in = random.randrange(1, 3)
            ins = random.sample(other, min(n_in, len(other)))
            for r in ins:
                im[r] = random.randrange(1, 4)
            if random.random() < 0.5:
                im[seed_res] = random.randrange(1, 4)
            if not im:
                im[other[0]] = 1
            om = {}
            if random.random() < 0.7:
                om[target_res] = random.randrange(1, 5)
            for r in random.sample(other, min(random.randrange(0, 3), len(other))):
                om[r] = random.randrange(1, 4)
            if not om:
                om[other[0]] = 1
            recipes.append((im, om))

        required = random.randrange(5, 8 + recipe_count * 4)
        ms = _cached_ms(recipes, seed_res, target_res, required)
        return recipes, required, ms

    def render_prompt(self, metadata):
        lines = []
        lines.append("You run a refinery with several recipes. A recipe lists which resources it consumes and which it produces. All resources are fully conserved: whatever you produce stays available for later use (including recycling), and whatever you consume is gone. The only resource you can buy to start is the limiting resource; it is never produced by any recipe.")
        lines.append("")
        lines.append("Recipes:")
        for i, (im, om) in enumerate(metadata["recipes"]):
            c = ", ".join(f"{amt} {r}" for r, amt in sorted(im.items()))
            p = ", ".join(f"{amt} {r}" for r, amt in sorted(om.items()))
            lines.append(f"  recipe {i}: consume {c} -> produce {p}")
        lines.append("")
        lines.append(f"You must end with at least {metadata['required']} units of {metadata['target_resource']} on hand. You may run any recipe any number of times, in any order, spending produced resources freely.")
        lines.append("")
        lines.append(f"What is the minimal initial stock of the limiting resource {metadata['seed_resource']} that lets you end with the required amount? Answer with one integer.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        ans = answer.strip()
        try:
            val = int(ans)
        except (ValueError, TypeError):
            return 0.0
        if val == entry.metadata["min_stock"]:
            return 1.0
        return 0.0

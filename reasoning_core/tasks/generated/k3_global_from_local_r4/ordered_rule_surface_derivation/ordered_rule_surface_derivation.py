import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

_SEG_POOL = list("pbtkdgszfvmnrl")


def _apply_rule(string, rule):
    s = list(string)
    n = len(s)
    out = list(s)
    target = rule["target"]
    left = rule["left"]
    right = rule["right"]
    for i in range(n):
        if s[i] != target:
            continue
        if i < len(left):
            continue
        ok = True
        for k in range(len(left)):
            if s[i - 1 - k] != left[len(left) - 1 - k]:
                ok = False
                break
        if not ok:
            continue
        if n - 1 - i < len(right):
            continue
        for k in range(len(right)):
            if s[i + 1 + k] != right[k]:
                ok = False
                break
        if ok:
            out[i] = rule["repl"]
    return "".join(out)


def _derive(string, rules):
    for rule in rules:
        string = _apply_rule(string, rule)
    return string


def _render_context(ctx):
    return "".join(ctx) if ctx else "\u2205"


def _render_rule(rule):
    return "{} -> {} / {} _ {}".format(
        rule["target"], rule["repl"],
        _render_context(rule["left"]), _render_context(rule["right"]))


def _random_underline(length, inventory):
    return "".join(random.choice(inventory) for _ in range(length))


def _make_rule_at(s, pos, inventory, max_ctx):
    seg = s[pos]
    others = [x for x in inventory if x != seg]
    repl = random.choice(others)
    n = len(s)
    l = random.randint(0, min(max_ctx, pos))
    r = random.randint(0, min(max_ctx, n - 1 - pos))
    left = list(s[pos - l:pos])
    right = list(s[pos + 1:pos + 1 + r])
    return {"target": seg, "repl": repl, "left": left, "right": right}


def _build_derive(underline, inventory, n_rules, max_ctx):
    s = list(underline)
    rules = []
    for _ in range(n_rules):
        pos = random.randrange(len(s))
        rule = _make_rule_at(s, pos, inventory, max_ctx)
        rules.append(rule)
        s = _apply_rule(s, rule)
    return rules, "".join(s)


def _build_feeding(underline, inventory, max_ctx):
    s = list(underline)
    pos = random.randrange(len(s))
    x = s[pos]
    y = random.choice([c for c in inventory if c != x])
    r1 = _make_rule_at(s, pos, inventory, max_ctx)
    r1["target"] = x
    r1["repl"] = y
    s1 = _apply_rule(s, r1)
    z = random.choice([c for c in inventory if c != y])
    r2 = {"target": y, "repl": z, "left": [], "right": []}
    pp = pos
    l2 = random.randint(0, min(max_ctx, pp))
    r2w = random.randint(0, min(max_ctx, len(s1) - 1 - pp))
    r2["left"] = list(s1[pp - l2:pp])
    r2["right"] = list(s1[pp + 1:pp + 1 + r2w])
    return r1, r2


def _build_commute(underline, inventory, max_ctx):
    s = list(underline)
    idxs = list(range(len(s)))
    random.shuffle(idxs)
    i, j = idxs[0], idxs[1]
    x1 = s[i]
    x2 = s[j]
    while x1 == x2:
        x2 = random.choice(inventory)
    y1 = random.choice([c for c in inventory if c not in (x1, x2)])
    y2 = random.choice([c for c in inventory if c not in (x1, x2, y1)])
    r1 = _make_rule_at(s, i, inventory, max_ctx)
    r1["target"] = x1
    r1["repl"] = y1
    r2 = _make_rule_at(s, j, inventory, max_ctx)
    r2["target"] = x2
    r2["repl"] = y2
    return r1, r2


def _make_reorder(inventory, min_len, max_len, max_ctx, desired):
    for _ in range(60):
        underline = _random_underline(random.randint(min_len, max_len), inventory)
        if desired == "change":
            r1, r2 = _build_feeding(underline, inventory, max_ctx)
            s1 = _derive(underline, [r1, r2])
            s2 = _derive(underline, [r2, r1])
            if s1 != s2:
                return underline, r1, r2, "Yes"
        else:
            r1, r2 = _build_commute(underline, inventory, max_ctx)
            s1 = _derive(underline, [r1, r2])
            s2 = _derive(underline, [r2, r1])
            if s1 == s2:
                return underline, r1, r2, "No"
    raise RuntimeError("failed to build reorder instance")


@dataclass
class OrderedRuleSurfaceDerivationV1Config(Config):
    inventory_size: int = 4
    n_rules: int = 1
    string_len_min: int = 4
    string_len_max: int = 5
    max_ctx: int = 1
    mode_derive_prob: float = 0.5

    def apply_difficulty(self, level):
        self.inventory_size = 4 + level
        self.n_rules = 1 + int(round(level * 0.7))
        self.string_len_min = 4
        self.string_len_max = 5 + level
        self.max_ctx = 1 + int(level >= 3)
        self.mode_derive_prob = 0.5


class OrderedRuleSurfaceDerivation(Task):
    summary = ("Invented segment inventories with ordered context-sensitive rewrite "
               "rules: derive surface strings from underlying forms, and compare "
               "swapped rule orders for feeding/bleeding; answer the surface string "
               "or whether reordering changes it.")
    design_choice = ("Rule notation: use explicit formal rewrite rules (A\u2192B / X_Y) "
                     "with segment symbols, requiring solvers to apply them stepwise to "
                     "underlying strings.")
    config_cls = OrderedRuleSurfaceDerivationV1Config
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        inventory = random.sample(_SEG_POOL, cfg.inventory_size)
        mode = "derive" if random.random() < cfg.mode_derive_prob else "reorder"
        if mode == "derive":
            underline = _random_underline(
                random.randint(cfg.string_len_min, cfg.string_len_max), inventory)
            rules, surface = _build_derive(underline, inventory, cfg.n_rules, cfg.max_ctx)
            if surface == underline:
                rules, surface = _build_derive(underline, inventory, cfg.n_rules, cfg.max_ctx)
            answer = surface
            payload = {"inventory": list(inventory), "underlying": underline,
                       "rules": rules, "mode": mode}
        else:
            desired = random.choice(["change", "nochange"])
            underline, r1, r2, answer = _make_reorder(
                inventory, cfg.string_len_min, cfg.string_len_max, cfg.max_ctx, desired)
            payload = {"inventory": list(inventory), "underlying": underline,
                       "rules": [r1, r2], "mode": mode}
        return Entry(metadata=payload, answer=answer)

    def render_prompt(self, metadata):
        inv = ", ".join(metadata["inventory"])
        lines = [f"The only segments of a language are: {inv}.",
                 f"Underlying form: {metadata['underlying']}"]
        if metadata["mode"] == "derive":
            lines.append("Ordered rewrite rules, applied in the order listed. Each rule "
                         "rewrites every matching occurrence at once, using the string as "
                         "it is when that rule starts; \u2205 means that side is "
                         "unconstrained; 'A -> B / X _ Y' rewrites A to B when it occurs "
                         "after X and before Y:")
            lines += ["R{}. {}".format(i + 1, _render_rule(r))
                      for i, r in enumerate(metadata["rules"])]
            lines.append("Compute the surface form obtained after applying all rules "
                         "to the underlying form. The answer is the surface string "
                         "of segments.")
        else:
            lines.append("Rewrite rules, applied with the same semantics as above "
                         "(each rule rewrites every matching occurrence at once):")
            lines += ["R1. {}".format(_render_rule(metadata["rules"][0])),
                      "R2. {}".format(_render_rule(metadata["rules"][1]))]
            lines.append("Compare the surface string when the rules are applied in the "
                         "order R1 then R2 versus the order R2 then R1. Does the order "
                         "of the two rules change the final surface string? The answer "
                         "is Yes or No.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        mode = entry.metadata.get("mode")
        ans = str(answer).strip()
        if mode == "derive":
            return 1.0 if ans == str(entry.answer) else 0.0
        gold = str(entry.answer).strip()
        if ans.lower() in ("yes", "no"):
            return 1.0 if ans.lower() == gold.lower() else 0.0
        return 0.0

    def distractor_candidates(self, entry):
        mode = entry.metadata.get("mode")
        if mode == "derive":
            yield entry.metadata.get("underlying", "")
        else:
            gold = str(entry.answer)
            yield "No" if gold.lower() == "yes" else "Yes"


TASK_META = {'parent_source_id': None,
 'idea': 'ordered_rule_surface_derivation (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_global_from_local_r4/ordered_rule_surface_derivation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

import random
import re
import string
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Reward, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'stratified_datalog_evaluation (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_invariants_r1/stratified_datalog_evaluation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class StratifiedDatalogConfig(Config):
    num_predicates: int = 2
    num_rules: int = 3
    domain_size: int = 3

    def apply_difficulty(self, level):
        self.num_predicates = stochastic_rounding(self.num_predicates + level // 2)
        self.num_rules = stochastic_rounding(self.num_rules + level)
        self.domain_size = stochastic_rounding(self.domain_size + level)


GROUND_FACTS = list(range(10))
VAR = string.ascii_lowercase
_ATOM_RE = re.compile(r"([a-zA-Z]\w*)\(([^()]*)\)")


def _cget(config, name, default):
    if isinstance(config, dict):
        return config.get(name, default)
    return getattr(config, name)


def atom_str(pred, args):
    return "%s(%s)" % (pred, ",".join(str(a) for a in args))


def parse_answer(answer, pred, arity):
    s = answer.strip()
    if not s.startswith("[") or not s.endswith("]"):
        return None
    inner = s[1:-1].strip()
    if not inner:
        return []
    atoms = []
    for m in _ATOM_RE.finditer(inner):
        name = m.group(1)
        args_text = m.group(2).strip()
        try:
            args = tuple(int(x.strip()) for x in args_text.split(",")) if args_text else ()
        except ValueError:
            return None
        if name != pred or len(args) != arity:
            return None
        atoms.append(args)
    return atoms


def saturate_stratum(rules, arities, dom_vals, derived, stratum, s):
    """Saturate all rules whose head stratum == s to a fixed point."""
    changed = True
    guard = 0
    while changed and guard < 100:
        changed = False
        guard += 1
        for head, head_vars, body in rules:
            if stratum[head] != s:
                continue
            new_facts = _saturate_rule(head, head_vars, body, arities, dom_vals, derived)
            before = len(derived[head])
            derived[head] |= new_facts
            if len(derived[head]) > before:
                changed = True


def _saturate_rule(head, head_vars, body, arities, dom_vals, derived):
    """All head facts derivable from one application of `rule` given current `derived`."""
    out = set()
    var_names = []
    for v in head_vars:
        if v not in var_names:
            var_names.append(v)
    for idx, v, neg in body:
        for a in v:
            if a not in var_names:
                var_names.append(a)
    if len(var_names) > 6:
        return out
    for assign in _enumerate_assignments(var_names, dom_vals):
        ok = True
        for idx, v, neg in body:
            args = tuple(assign[a] for a in v)
            holds = args in derived[idx]
            if neg:
                holds = not holds
            if not holds:
                ok = False
                break
        if ok:
            out.add(tuple(assign[a] for a in head_vars))
    return out


def _enumerate_assignments(var_names, dom_vals):
    if not var_names:
        return [{}]
    results = [{}]
    for v in var_names:
        new_results = []
        for a in results:
            for d in dom_vals:
                na = dict(a)
                na[v] = d
                new_results.append(na)
        results = new_results
    return results


class StratifiedDatalogEvaluation(Task):
    summary = (
        "Evaluate stratified Datalog with negation by ordering strata along negative "
        "dependencies and saturating each to a fixed point; given a queried predicate, "
        "return every derived ground fact as a canonical sorted list."
    )
    design_choice = (
        "Answer form: return the full set of derived facts for a queried predicate as a "
        "canonical sorted list of ground atoms."
    )
    config_cls = StratifiedDatalogConfig

    def generate_entry(self):
        cfg = self.config
        num_pred = max(2, _cget(cfg, "num_predicates", 2))
        num_rules = max(2, _cget(cfg, "num_rules", 3))
        dom = max(2, _cget(cfg, "domain_size", 3))
        dom_vals = GROUND_FACTS[:dom]

        pred_names = ["p%d" % i for i in range(num_pred)]
        arities = [random.choice([1, 2]) for _ in range(num_pred)]

        facts = []
        for i in range(num_pred):
            nf = random.randint(1, max(2, dom // 2))
            if arities[i] == 1:
                fs = random.sample(dom_vals, min(nf, len(dom_vals)))
                facts.append([(v,) for v in fs])
            else:
                pairs = [(a, b) for a in dom_vals for b in dom_vals]
                random.shuffle(pairs)
                take = min(nf, len(pairs))
                facts.append(pairs[:take])

        # Random stratum assignment, then generate rules respecting stratification.
        stratum = [random.randint(0, 1) for _ in range(num_pred)]

        def gen_rule():
            head = random.randint(0, num_pred - 1)
            h_arity = arities[head]
            head_vars = list(VAR[:h_arity])
            nbody = random.randint(1, 2)
            body = []
            for _ in range(nbody):
                idx = random.randint(0, num_pred - 1)
                arity = arities[idx]
                neg = random.random() < 0.3
                v = list(VAR[:arity])
                body.append((idx, tuple(v), neg))
            return (head, tuple(head_vars), body)

        rules = []
        attempts = 0
        while len(rules) < num_rules and attempts < 400:
            attempts += 1
            rule = gen_rule()
            head, head_vars, body = rule
            valid = True
            for idx, _, neg in body:
                if neg and stratum[idx] >= stratum[head]:
                    valid = False
                    break
                if not neg and stratum[idx] > stratum[head]:
                    valid = False
                    break
            if not valid:
                continue
            rules.append(rule)

        # Evaluate: derive with stratification.
        derived = [set(f) for f in facts]
        for s in sorted(set(stratum)):
            saturate_stratum(rules, arities, dom_vals, derived, stratum, s)

        q = random.randint(0, num_pred - 1)
        result = sorted(derived[q])
        answer = "[" + ", ".join(atom_str(pred_names[q], args) for args in result) + "]"
        if not result:
            answer = "[]"

        # Independent recheck of the queried predicate.
        recheck = [set(f) for f in facts]
        for s in sorted(set(stratum)):
            saturate_stratum(rules, arities, dom_vals, recheck, stratum, s)
        assert recheck[q] == derived[q], "verifier mismatch"

        lines = []
        for i in range(num_pred):
            fs = sorted(facts[i])
            if fs:
                lines.append("  " + ", ".join(atom_str(pred_names[i], a) for a in fs) + ".")
        rule_lines = []
        for head, head_vars, body in rules:
            head_atom = atom_str(pred_names[head], head_vars)
            body_parts = []
            for idx, v, neg in body:
                a = atom_str(pred_names[idx], v)
                if neg:
                    a = "not " + a
                body_parts.append(a)
            rule_lines.append("  " + head_atom + " :- " + ", ".join(body_parts) + ".")
        prompt = (
            "The following is a stratified Datalog program with negation.\n"
            "Facts:\n" + "\n".join(lines) +
            "\nRules:\n" + "\n".join(rule_lines) +
            "\nEvaluate this program under stratified Datalog semantics: order the strata "
            "along negative dependencies and saturate each stratum to a fixed point, using "
            "already-computed facts of lower strata when a negated literal appears. "
            "Determine every ground fact derivable for predicate %s.\n"
            "Answer as a canonical sorted list of ground atoms with arguments in "
            "ascending numeric order, e.g. [p(0), p(2)] or [] if none are derivable." % pred_names[q]
        )

        metadata = {
            "pred_names": pred_names,
            "arities": arities,
            "facts": [sorted(f) for f in facts],
            "rules": [[head, list(head_vars), [[idx, list(v), neg] for idx, v, neg in body]]
                      for head, head_vars, body in rules],
            "stratum": stratum,
            "query": pred_names[q],
            "result": result,
            "prompt": prompt,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return metadata["prompt"]

    def score_answer(self, answer, entry):
        q = entry.metadata["query"]
        qidx = entry.metadata["pred_names"].index(q)
        arity = entry.metadata["arities"][qidx]
        gold = [tuple(a) for a in entry.metadata["result"]]
        parsed = parse_answer(answer, q, arity)
        if parsed is None:
            return Reward(0.0, "unparseable")
        if sorted(tuple(a) for a in parsed) == sorted(gold):
            return Reward(1.0, "exact")
        return Reward(0.0, "mismatch")

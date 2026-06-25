"""Metamath set.mm proof-tree tasks.

The generator downloads set.mm into appdirs, mines small assertions as inference
rules, builds fresh uncompressed proof trees by substitution, and checks them
with a small Metamath stack verifier.
"""

from __future__ import annotations

import itertools
import random
import re
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from urllib.request import urlretrieve

from appdirs import AppDirs
from easydict import EasyDict as edict

from reasoning_core.template import Config, Problem, Task


_SET_MM_URL = "https://raw.githubusercontent.com/metamath/set.mm/develop/set.mm"
_TYPECODES = {"|-", "wff", "class", "set"}
_VARS = {
    "wff": ("ph", "ps", "ch", "th", "ta", "et", "ze", "si"),
    "class": ("A", "B", "C", "D", "E", "F", "G", "H"),
    "set": ("x", "y", "z", "w", "v", "u", "t", "s"),
}
_MATH_TOKENS = {
    "=", "e.", "C_", "<", "<_", ">", ">_", "+", "-", "x.", "/", "0", "1", "2",
    "RR", "CC", "NN", "ZZ", "QQ", "dom", "ran", "Fun", "Rel", "Ord", "On", "U.",
    "|^|", "i^i", "X.", "sSet", "Top", "Grp", "Mgm", "Ring", "Field",
    "Abel", "CMnd", "Mnd", "sin", "cos", "tan", "exp", "log", "`",
}
_STRUCTURAL_MATH_TOKENS = _MATH_TOKENS - {"="}
_PURE_WFF = {"ph", "ps", "ch", "th", "ta", "et", "ze", "si"}
_KEEP_HEADS = {"e.", "=", "=/=", "<", "<_", ">", ">_", "C_"}
_KEEP_CONSTS = {"RR", "CC", "NN", "ZZ", "QQ", "Abel", "CMnd", "Mnd", "Grp", "Ring", "Field"}
_BINOPS = {
    "->": "=>",
    "<->": "<=>",
    "/\\": "∧",
    "\\/": "∨",
    "=": "=",
    "=/=": "≠",
    "e.": "∈",
    "C_": "⊆",
    "C.": "⊂",
    "<": "<",
    "<_": "≤",
    ">": ">",
    ">_": "≥",
    "+": "+",
    "-": "-",
    "x.": "·",
    "/": "/",
    "^": "^",
}
_PREFIX_APP = {
    "*": "conjugate",
    "sin": "sin",
    "cos": "cos",
    "tan": "tan",
    "exp": "exp",
    "log": "log",
    "sqrt": "sqrt",
    "-u": "-",
}
_PRECEDENCE = [
    ("->", "<->"),
    ("/\\", "\\/"),
    ("=", "=/=", "e.", "C_", "C.", "<", "<_", ">", ">_"),
    ("+", "-"),
    ("x.", "/"),
    ("^",),
]


@dataclass(frozen=True)
class MMRule:
    label: str
    conclusion: tuple[str, ...]
    floating: tuple[tuple[str, str, str], ...]  # label, typecode, variable
    essential: tuple[tuple[str, ...], ...]
    dv: frozenset[tuple[str, str]]


@dataclass(frozen=True)
class MMTree:
    target: tuple[str, ...]
    leaves: tuple[tuple[str, ...], ...]
    proof: tuple[str, ...]
    used: frozenset[str]


@dataclass
class MetamathConfig(Config):
    proof_depth: int = 2
    n_rules: int = 5
    n_options: int = 4
    max_premises: int = 6
    formula_len_cap: int = 18

    def update(self, c=1):
        self.proof_depth += c
        self.n_rules += c
        self.max_premises += c
        self.formula_len_cap += 2 * c


def _metamath_dir():
    return Path(AppDirs("reasoning_core").user_data_dir) / "metamath"


def ensure_set_mm():
    """Download set.mm once into appdirs and return its path."""
    base = _metamath_dir()
    path = base / "set.mm"
    if not path.exists() or path.stat().st_size < 1_000_000:
        base.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        urlretrieve(_SET_MM_URL, tmp)
        tmp.replace(path)
    return path


def _tokens(text):
    text = re.sub(r"\$\((?:.|\n)*?\$\)", " ", text)
    return re.findall(r"\S+", text)


def _pairs(xs):
    return {tuple(sorted(p)) for p in itertools.combinations(xs, 2)}


def _vars_in(expr, active_vars):
    return {t for t in expr if t in active_vars}


@lru_cache(maxsize=1)
def _database():
    toks = _tokens(ensure_set_mm().read_text(encoding="utf-8", errors="ignore"))
    frames = [edict(vars=set(), f={}, f_order=[], e=[], dv=set())]
    labels, rules, var_type, var_flabel = {}, {}, {}, {}
    constants, i = set(), 0

    def active_vars():
        out = set()
        for fr in frames:
            out |= fr.vars
        return out

    def active_floating(mandatory):
        out = []
        for fr in frames:
            for var in fr.f_order:
                if var in mandatory:
                    out.append(fr.f[var])
        return out

    def active_e():
        out = []
        for fr in frames:
            out.extend(fr.e)
        return out

    def active_dv():
        out = set()
        for fr in frames:
            out |= fr.dv
        return out

    def read_until(stop):
        nonlocal i
        out = []
        while i < len(toks) and toks[i] != stop:
            out.append(toks[i])
            i += 1
        i += 1
        return out

    while i < len(toks):
        tok = toks[i]
        i += 1
        if tok == "${":
            frames.append(edict(vars=set(), f={}, f_order=[], e=[], dv=set()))
        elif tok == "$}":
            frames.pop()
        elif tok == "$c":
            constants |= set(read_until("$."))
        elif tok == "$v":
            frames[-1].vars |= set(read_until("$."))
        elif tok == "$d":
            frames[-1].dv |= _pairs(read_until("$."))
        elif tok == "$[":
            read_until("$]")
        elif i < len(toks) and toks[i] in {"$f", "$e", "$a", "$p"}:
            label, kind = tok, toks[i]
            i += 1
            if kind == "$p":
                stmt = []
                while toks[i] != "$=":
                    stmt.append(toks[i])
                    i += 1
                i += 1
                read_until("$.")
                stmt = tuple(stmt)
            else:
                stmt = tuple(read_until("$."))
            labels[label] = tuple(stmt)
            if kind == "$f" and len(stmt) == 2:
                typecode, var = stmt
                frames[-1].f[var] = (label, typecode, var)
                frames[-1].f_order.append(var)
                var_type[var], var_flabel[var] = typecode, label
            elif kind == "$e":
                frames[-1].e.append((label, tuple(stmt)))
            elif kind in {"$a", "$p"} and stmt:
                avars = _vars_in(stmt, active_vars())
                essentials = tuple(e for _, e in active_e())
                mandatory = set(avars)
                for e in essentials:
                    mandatory |= _vars_in(e, active_vars())
                floating = tuple(active_floating(mandatory))
                rule = MMRule(
                    label=label,
                    conclusion=tuple(stmt),
                    floating=floating,
                    essential=essentials,
                    dv=frozenset(p for p in active_dv() if p[0] in mandatory and p[1] in mandatory),
                )
                rules[label] = rule
    return edict(labels=labels, rules=rules, var_type=var_type, var_flabel=var_flabel, constants=constants)


def _rule_catalog(max_len=18):
    db = _database()
    out = []
    for r in db.rules.values():
        if not (1 <= len(r.essential) <= 3 and len(r.conclusion) <= max_len):
            continue
        if r.conclusion[0] != "|-" or any(len(h) > max_len for h in r.essential):
            continue
        if all(v in _VARS.get(t, ()) for _, t, v in r.floating):
            out.append(r)
    return out


def _math_rule_catalog(max_len=18):
    return [r for r in _rule_catalog(max_len) if _keep_rule(r)]


def _balanced(xs):
    depth = 0
    for tok in xs:
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def _strip_outer(xs):
    xs = list(xs)
    while len(xs) >= 2 and xs[0] == "(" and xs[-1] == ")" and _balanced(xs[1:-1]):
        xs = xs[1:-1]
    return xs


def _find_top_level_binary(xs):
    for ops in _PRECEDENCE:
        depth = 0
        for i, tok in enumerate(xs):
            if tok == "(":
                depth += 1
            elif tok == ")":
                depth -= 1
            elif depth == 0 and tok in ops:
                return i, tok
    return None


def render_expr(expr):
    xs = _strip_outer(list(expr))
    if xs and xs[0] == "|-":
        return render_expr(xs[1:])
    xs = _strip_outer(xs)
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    if len(xs) == 2 and xs[0] in _PREFIX_APP:
        arg = render_expr([xs[1]])
        return f"{_PREFIX_APP[xs[0]]}{arg}" if xs[0] == "-u" and arg is not None else (
            f"{_PREFIX_APP[xs[0]]}({arg})" if arg is not None else None
        )
    if len(xs) == 3 and xs[1] == "`":
        arg = render_expr([xs[2]])
        if arg is None:
            return None
        return f"{_PREFIX_APP.get(xs[0], xs[0])}({arg})"
    split = _find_top_level_binary(xs)
    if split:
        i, op = split
        left, right = render_expr(xs[:i]), render_expr(xs[i + 1:])
        if left is None or right is None:
            return None
        text = f"{left} {_BINOPS[op]} {right}"
        if op in {"->", "<->", "/\\", "\\/"}:
            return f"({text})"
        return text
    return None


def _math_score(expr):
    return len(set(expr) & _MATH_TOKENS)


def _has_math_atom(expr):
    return bool(set(expr) & _KEEP_HEADS)


def _wff_only(expr):
    return set(expr) <= _PURE_WFF | {"|-", "(", ")", "->", "<->", "/\\", "\\/"}


def _keep_rule(rule):
    exprs = [rule.conclusion, *rule.essential]
    rendered = [render_expr(e) for e in exprs]
    return (
        1 <= len(rule.essential) <= 3
        and all(r is not None and len(r) <= 120 for r in rendered)
        and (any(_has_math_atom(e) for e in exprs) or bool(set().union(*map(set, exprs)) & _KEEP_CONSTS))
        and sum(tok in _KEEP_HEADS for e in exprs for tok in e) >= 2
        and sum(_math_score(e) for e in exprs) >= 2
        and not all(_wff_only(e) for e in exprs)
    )


def _count_math_atoms(text):
    return sum(text.count(tok) for tok in ("∈", "=", "≠", "<", "≤", ">", "≥", "⊆", "⊂"))


def _target_is_wff_implication(text):
    return bool(re.fullmatch(r"\(?[a-z]{2} => [a-z]{2}\)?", text.strip()))


def _display(text):
    if text is None:
        return None
    xs = text.strip()
    while xs.startswith("(") and xs.endswith(")") and _balanced(re.findall(r"\(|\)|[^()\s]+", xs[1:-1])):
        xs = xs[1:-1].strip()
    return xs


def _subst_expr(expr, subst):
    out = []
    for tok in expr:
        out.extend(subst.get(tok, (tok,)))
    return tuple(out)


def _fresh_subst(rule):
    used = defaultdict(int)
    subst = {}
    for _, typecode, var in rule.floating:
        pool = _VARS.get(typecode, (var,))
        subst[var] = (pool[used[typecode] % len(pool)],)
        used[typecode] += 1
    for a, b in rule.dv:
        if subst.get(a) == subst.get(b):
            return None
    return subst


def _head(expr):
    body = expr[1:] if expr and expr[0] in _TYPECODES else expr
    return next((t for t in body if t not in {"(", ")"} and t not in _database().var_type), "")


def _match_pattern(pattern, target, subst=None):
    db = _database()
    subst = dict(subst or {})

    def rec(pi, ti):
        if pi == len(pattern) and ti == len(target):
            return subst
        if pi >= len(pattern) or ti > len(target):
            return None
        tok = pattern[pi]
        if tok in db.var_type:
            old = subst.get(tok)
            if old is not None:
                return rec(pi + 1, ti + len(old)) if tuple(target[ti:ti + len(old)]) == old else None
            max_end = len(target) - (len(pattern) - pi - 1)
            for end in range(ti + 1, max_end + 1):
                subst[tok] = tuple(target[ti:end])
                got = rec(pi + 1, end)
                if got is not None:
                    return got
            subst.pop(tok, None)
            return None
        if ti < len(target) and tok == target[ti]:
            return rec(pi + 1, ti + 1)
        return None

    return rec(0, 0)


def _match_variable_only(pattern, target):
    db = _database()
    if len(pattern) != len(target):
        return None
    subst = {}
    for p, t in zip(pattern, target):
        if p in db.var_type:
            if t not in db.var_type or db.var_type[t] != db.var_type[p]:
                return None
            if p in subst and subst[p] != (t,):
                return None
            subst[p] = (t,)
        elif p != t:
            return None
    return subst


def _rules_matching_variable_only(target, rules):
    random.shuffle(rules)
    return [r for r in rules if _match_variable_only(r.conclusion, target) is not None]


def _local_f_label(var):
    return _database().var_flabel[var]


def _build_tree(rule, rules, depth, leaf_prob=0.45, target=None):
    subst = _match_variable_only(rule.conclusion, target) if target is not None else _fresh_subst(rule)
    if subst is None:
        return None
    used_by_type = defaultdict(set)
    for _, typecode, var in rule.floating:
        if var in subst:
            used_by_type[typecode].add(subst[var][0])
    for _, typecode, var in rule.floating:
        if var in subst:
            continue
        pool = [v for v in _VARS.get(typecode, (var,)) if v not in used_by_type[typecode]]
        if not pool:
            pool = list(_VARS.get(typecode, (var,)))
        subst[var] = (pool[0],)
        used_by_type[typecode].add(pool[0])
    for a, b in rule.dv:
        if subst.get(a) == subst.get(b):
            return None
    target = _subst_expr(rule.conclusion, subst)
    leaves, proof, used = [], [], {rule.label}
    proof.extend(_local_f_label(v[0]) for _, _, v0 in rule.floating if (v := subst[v0]) and v[0] in _database().var_flabel)
    for hyp in rule.essential:
        shyp = _subst_expr(hyp, subst)
        child = None
        if depth > 0 and random.random() >= leaf_prob:
            matches = [
                r for r in _rules_matching_variable_only(shyp, list(rules))
                if r.label != rule.label or random.random() < 0.35
            ]
            if matches:
                child = _build_tree(random.choice(matches), rules, depth - 1, leaf_prob, target=shyp)
        if child is None:
            leaves.append(shyp)
            proof.append("__LEAF__")
        else:
            leaves.extend(child.leaves)
            proof.extend(child.proof)
            used |= set(child.used)
    proof.append(rule.label)
    return MMTree(target, tuple(leaves), tuple(proof), frozenset(used))


def _verify(proof, target, premises, allowed_rules):
    db = _database()
    labels = {k: db.labels[k] for k in db.var_flabel.values() if k in db.labels}
    rules = {k: db.rules[k] for k in allowed_rules if k in db.rules}
    for i, p in enumerate(premises, 1):
        labels[f"prem{i}"] = tuple(p)
    stack = []
    for label in proof:
        if label in labels:
            stack.append(labels[label])
            continue
        rule = rules[label]
        subst = {}
        mandatory = list(rule.floating) + [(None, None, None)] * len(rule.essential)
        hyps = [tuple((t, v)) for _, t, v in rule.floating] + list(rule.essential)
        if len(stack) < len(hyps):
            return False
        args = stack[-len(hyps):] if hyps else []
        if hyps:
            del stack[-len(hyps):]
        for (_, t, v), arg in zip(mandatory[:len(rule.floating)], args[:len(rule.floating)]):
            if not arg or arg[0] != t:
                return False
            subst[v] = tuple(arg[1:])
        for hyp, arg in zip(rule.essential, args[len(rule.floating):]):
            if _subst_expr(hyp, subst) != tuple(arg):
                return False
        for a, b in rule.dv:
            va, vb = subst.get(a, ()), subst.get(b, ())
            if va == vb or set(va) & set(vb):
                return False
        stack.append(_subst_expr(rule.conclusion, subst))
    return stack == [tuple(target)]


def _tree_with_premise_labels(tree):
    mapping, premises = {}, []
    for leaf in tree.leaves:
        if leaf not in mapping:
            mapping[leaf] = f"prem{len(mapping) + 1}"
            premises.append(leaf)
    proof, leaf_iter = [], iter(tree.leaves)
    for label in tree.proof:
        if label == "__LEAF__":
            proof.append(mapping[next(leaf_iter)])
        else:
            proof.append(label)
    return tuple(premises), tuple(proof)


def _closure(premises, rules, cap=18, rounds=5):
    known = set(map(tuple, premises))
    rules = list(rules)
    for _ in range(rounds):
        before = len(known)
        for r in rules:
            if not r.essential:
                continue
            pools = [list(known) for _ in r.essential]
            for args in itertools.product(*pools):
                subst = {}
                ok = True
                for hyp, arg in zip(r.essential, args):
                    subst = _match_pattern(hyp, arg, subst)
                    if subst is None:
                        ok = False
                        break
                if not ok:
                    continue
                conc = _subst_expr(r.conclusion, subst)
                if len(conc) <= cap:
                    known.add(conc)
        if len(known) == before:
            break
    return known


def _fmt(expr):
    return _display(render_expr(expr))


def _rule_schema(label):
    rule = _database().rules[label]
    lhs = "; ".join(_fmt(h) for h in rule.essential)
    return f"{label}: {lhs} ==> {_fmt(rule.conclusion)}"


def _keep_instance(inst):
    rendered_premises = [_fmt(p) for p in inst.premises]
    rendered_target = _fmt(inst.tree.target)
    rendered_rules = [_rule_schema(label) for label in inst.rules]
    if rendered_target is None or any(p is None for p in rendered_premises + rendered_rules):
        return False
    text = "\n".join([rendered_target, *rendered_premises])
    return (
        len(inst.premises) >= 2
        and len(inst.tree.used) >= 2
        and _count_math_atoms(text) >= 3
        and not _target_is_wff_implication(rendered_target)
    )


def _sample_instance(config):
    rules = _math_rule_catalog(int(config.formula_len_cap))
    if not rules:
        raise RuntimeError("No small Metamath rules mined from set.mm")
    for _ in range(200):
        root = random.choice(rules)
        tree = _build_tree(root, rules, int(config.proof_depth))
        if (
            not tree or len(tree.used) < 2 or len(tree.used) > int(config.n_rules)
            or not tree.leaves or len(set(tree.leaves)) > int(config.max_premises)
        ):
            continue
        premises, proof = _tree_with_premise_labels(tree)
        if not _verify(proof, tree.target, premises, tree.used):
            continue
        displayed = sorted(tree.used)
        inst = edict(tree=tree, premises=premises, proof=proof, rules=displayed)
        if _keep_instance(inst):
            return inst
    raise RuntimeError("failed to generate a verified Metamath proof tree")


def _negative_target(inst, config):
    closure = _closure(inst.premises, [_database().rules[l] for l in inst.rules], int(config.formula_len_cap))
    vars_ = sorted({t for f in list(inst.premises) + [inst.tree.target] for t in f if t in _database().var_type})
    for _ in range(80):
        repl = {v: random.choice(_VARS.get(_database().var_type[v], (v,))) for v in vars_}
        cand = tuple(repl.get(t, t) for t in inst.tree.target)
        if cand != inst.tree.target and len(cand) <= int(config.formula_len_cap) and _head(cand) == _head(inst.tree.target):
            if cand not in closure:
                return cand
    for r in _math_rule_catalog(int(config.formula_len_cap)):
        subst = _fresh_subst(r)
        if subst:
            cand = _subst_expr(r.conclusion, subst)
            if _head(cand) == _head(inst.tree.target) and cand not in closure:
                return cand
    return None


def _abc(i):
    return chr(ord("A") + i)


class MetamathEntailment(Task):
    """True/False bounded derivability from displayed set.mm-derived rules."""

    def __init__(self, config=None, **kwargs):
        config = config or MetamathConfig()
        for k, v in kwargs.items():
            setattr(config, k, v)
        super().__init__(config=config, timeout=120)
        self._want_positive = True

    def generate(self):
        for _ in range(50):
            inst = _sample_instance(self.config)
            positive = self._want_positive
            target = inst.tree.target
            if not positive:
                target = _negative_target(inst, self.config)
                if target is None or _fmt(target) is None:
                    continue
            self._want_positive = not self._want_positive
            return Problem(
                edict(
                    premises=[_fmt(p) for p in inst.premises],
                    raw_premises=[list(p) for p in inst.premises],
                    rules=inst.rules,
                    rule_schemas=[_rule_schema(r) for r in inst.rules],
                    conjecture=_fmt(target),
                    raw_conjecture=list(target),
                    positive=positive,
                    proof=list(inst.proof) if positive else [],
                    source="set.mm",
                ),
                "True" if positive else "False",
            )
        raise RuntimeError("failed to generate Metamath entailment task")

    def prompt(self, metadata):
        premises = "\n".join(f"{i + 1}. {p}" for i, p in enumerate(metadata.premises))
        rules = "\n".join(f"{_abc(i)}. {r}" for i, r in enumerate(metadata.rule_schemas))
        return (
            "Using only these displayed Metamath premises and rules, does the conjecture follow?\n"
            "The answer is True or False.\n\n"
            f"Premises:\n{premises}\n\n"
            f"Allowed rules:\n{rules}\n\n"
            f"Conjecture: {metadata.conjecture}"
        )


class MetamathCoreSelect(Task):
    """Select the minimal sufficient displayed rule subset for a Metamath proof."""

    def __init__(self, config=None, **kwargs):
        config = config or MetamathConfig()
        for k, v in kwargs.items():
            setattr(config, k, v)
        super().__init__(config=config, timeout=120)

    def generate(self):
        labels = [r.label for r in _math_rule_catalog(int(self.config.formula_len_cap))]
        for _ in range(80):
            inst = _sample_instance(self.config)
            core = tuple(sorted(inst.tree.used))
            if inst.tree.target in _closure(inst.premises, [_database().rules[l] for l in core if l in _database().rules], int(self.config.formula_len_cap)):
                pass
            else:
                continue
            if any(inst.tree.target in _closure(inst.premises, [_database().rules[l] for l in core if l != miss], int(self.config.formula_len_cap)) for miss in core):
                continue
            wrong = set()
            if len(core) > 1:
                wrong.add(tuple(x for x in core if x != random.choice(core)))
            else:
                wrong.add(tuple())
            near = [l for l in labels if l not in core]
            random.shuffle(near)
            for label in near:
                cand = tuple(sorted((set(core) - {random.choice(core)}) | {label}))
                if cand != core and cand not in wrong and inst.tree.target not in _closure(inst.premises, [_database().rules[l] for l in cand], int(self.config.formula_len_cap)):
                    wrong.add(cand)
                if len(wrong) >= int(self.config.n_options) - 1:
                    break
            if len(wrong) < int(self.config.n_options) - 1:
                continue
            options = [core] + list(wrong)[: int(self.config.n_options) - 1]
            if len(set(options)) != int(self.config.n_options):
                continue
            random.shuffle(options)
            answer = _abc(options.index(core))
            return Problem(
                edict(
                    premises=[_fmt(p) for p in inst.premises],
                    raw_premises=[list(p) for p in inst.premises],
                    conjecture=_fmt(inst.tree.target),
                    raw_conjecture=list(inst.tree.target),
                    rule_schemas=[_rule_schema(r) for r in sorted(set().union(*map(set, options)))],
                    options=[list(o) for o in options],
                    proof=list(inst.proof),
                    source="set.mm",
                ),
                answer,
            )
        raise RuntimeError("failed to generate Metamath core-selection task")

    def prompt(self, metadata):
        premises = "\n".join(f"{i + 1}. {p}" for i, p in enumerate(metadata.premises))
        rules = "\n".join(f"- {r}" for r in metadata.rule_schemas)
        options = "\n".join(f"{_abc(i)}. [{', '.join(o)}]" for i, o in enumerate(metadata.options))
        return (
            "Which option is the minimal sufficient set of Metamath rules for the conjecture?\n"
            "The answer is A, B, C, or D.\n\n"
            f"Premises:\n{premises}\n\n"
            f"Rule catalog:\n{rules}\n\n"
            f"Conjecture: {metadata.conjecture}\n\n"
            f"Options:\n{options}"
        )

    def score_answer(self, answer, entry):
        m = re.search(r"[A-D]", str(answer).upper())
        return float(bool(m) and m.group(0) == entry.answer)

# multistep_nli v1
from collections import Counter, defaultdict
from dataclasses import dataclass
import itertools
import random
from typing import Optional

from easydict import EasyDict as edict

from reasoning_core.template import Config, Problem, Task


@dataclass(frozen=True)
class Atom:
    pred: str
    args: tuple
    sign: bool = True


@dataclass(frozen=True)
class PredSig:
    name: str
    arg_types: tuple
    verbalizers: tuple = ()


@dataclass(frozen=True)
class Rule:
    body: tuple
    head: Atom
    name: str = ""
    shape: str = ""


@dataclass(frozen=True)
class Denial:
    body: tuple


@dataclass
class Derivation:
    atom: Atom
    depth: int
    rule: Optional[object]
    parents: tuple


@dataclass
class Theory:
    facts: list
    rules: list
    denials: list
    pred_sigs: dict
    entities: dict
    domain_pack: str = "generic"


@dataclass
class ChaseResult:
    closure: set
    derivations: dict
    inconsistent: bool = False


@dataclass
class MultistepCase:
    theory: Theory
    res: ChaseResult
    label: str
    hyp: Atom
    target: Optional[Atom]
    derivation: Optional[Derivation]
    support_atoms: set
    lines: list
    source: dict
    surf: list
    live_rule_rate: float
    proof_rule_rate: float

SUPPORTED_DOMAIN_PACKS = ("surface", "abstract", "spatial", "kinship")

@dataclass
class MultistepNLIConfig(Config):
    n_entities: int = 4
    n_unary_preds: int = 6
    n_binary_preds: int = 3
    n_facts: int = 4
    n_rules: int = 4
    max_depth: int = 3
    min_target_depth: int = 2
    max_target_depth: int = 3
    n_distractors: int = 1
    neutral_rate: float = 0.33
    contradiction_rate: float = 0.33
    max_bin_size: int = 8
    domain_packs: tuple = SUPPORTED_DOMAIN_PACKS
    min_target_support_size: int = 2
    max_target_support_size: Optional[int] = 3
    
    def update(self, c):
        self.max_depth += int(c) // 2
        self.n_rules += c
        self.n_distractors += 2 * c
        self.n_unary_preds += c
        self.n_binary_preds += c
        self.min_target_support_size = min(5, self.min_target_support_size + max(1, int(c)) / 3)
        self.max_target_depth = min(int(self.max_depth), int(self.max_target_depth) + max(1, int(c) // 2))


@dataclass
class MultistepAbductionConfig(MultistepNLIConfig):
    n_candidates: int = 6
    n_missing_facts: int = 1
    max_abduction_size: int = 1
    require_unique: bool = True


NAMES = ("alice", "bruno", "clara", "david", "elena", "farah", "george", "hannah")
OBJECTS = ("box", "key", "lamp", "map", "coin", "vase", "book", "ring")
PLACES = ("atrium", "lab", "office", "vault", "garden", "studio", "hall", "archive")

GEN_UNARY = (
    "approved", "careful", "trained", "trusted", "active", "verified", "alert",
    "eligible", "quiet", "skilled", "reliable", "flagged", "cleared", "busy",
)
GEN_BINARY = (
    "helps", "trusts", "advises", "checks", "visits", "guards", "reports_to",
    "contacts", "observes", "supports", "follows", "reviews",
)
SP_UNARY = ("marked", "fixed", "visible", "blocked", "safe", "fragile", "lit", "sealed")
ABS_UNARY = tuple(f"p{i}" for i in range(24))
ABS_BINARY = tuple(f"r{i}" for i in range(24))
TAG_WORDS = (
    "alpha", "bravo", "charlie", "delta", "echo", "foxtrot",
    "gamma", "kappa", "lambda", "omega", "sigma", "zeta",
)
REL_WORDS = (
    "alpha-linked", "beta-linked", "gamma-linked", "delta-related",
    "omega-connected", "sigma-associated", "kappa-linked", "zeta-related",
)



def is_var(x):
    return isinstance(x, str) and x.startswith("?")


def opposite(a):
    return Atom(a.pred, a.args, not a.sign)


def _subst(atom, env):
    return Atom(atom.pred, tuple(env.get(x, x) for x in atom.args), atom.sign)


def _match(pattern, fact, env):
    if pattern.pred != fact.pred or pattern.sign != fact.sign or len(pattern.args) != len(fact.args):
        return None
    env = dict(env)
    for p, v in zip(pattern.args, fact.args):
        if is_var(p):
            if p in env and env[p] != v:
                return None
            env[p] = v
        elif p != v:
            return None
    return env


def _rule_instances(rule, closure):
    index = defaultdict(list)
    for fact in closure:
        index[(fact.pred, fact.sign)].append(fact)

    atoms = [b for b in rule.body if isinstance(b, Atom)]
    checks = [b for b in rule.body if not isinstance(b, Atom)]

    def rec(i, env, parents):
        if i == len(atoms):
            for chk in checks:
                if chk[0] == "!=" and env.get(chk[1]) == env.get(chk[2]):
                    return
            head = _subst(rule.head, env)
            if any(is_var(a) for a in head.args):
                return
            yield head, parents
            return
        pat = atoms[i]
        for fact in index.get((pat.pred, pat.sign), ()):
            env2 = _match(pat, fact, env)
            if env2 is not None:
                yield from rec(i + 1, env2, parents + (fact,))

    yield from rec(0, {}, ())


def chase(theory, max_depth=None):
    closure = set(theory.facts)
    deriv = {a: Derivation(a, 0, None, ()) for a in closure}

    def denial_hit():
        for p in list(closure):
            if opposite(p) in closure:
                return True
        for d in theory.denials:
            dummy = Rule(d.body, Atom("__false__", ()))
            if next(_rule_instances(dummy, closure), None):
                return True
        return False

    if denial_hit():
        return ChaseResult(closure, deriv, True)

    changed = True
    while changed:
        changed = False
        for rule in theory.rules:
            for head, parents in _rule_instances(rule, closure):
                depth = 1 + max(deriv[p].depth for p in parents) if parents else 1
                if max_depth is not None and depth > max_depth:
                    continue
                old = deriv.get(head)
                if old is None or depth < old.depth:
                    closure.add(head)
                    deriv[head] = Derivation(head, depth, rule, parents)
                    changed = True
        if denial_hit():
            return ChaseResult(closure, deriv, True)
    return ChaseResult(closure, deriv, False)


def _sigs(names, arity, typ="person"):
    return {p: PredSig(p, (typ,) * arity, (p.replace("_", " "),)) for p in names}


def _domain_pack(name, cfg):
    n = min(max(3, cfg.n_entities), 7)
    if name in {"abstract", "surface"}:
        ents = {"entity": tuple(x.title() for x in NAMES[:n])}
        unary = ABS_UNARY[: cfg.n_unary_preds]
        binary = ABS_BINARY[: cfg.n_binary_preds]
        return ents, {**_sigs(unary, 1, "entity"), **_sigs(binary, 2, "entity")}, [], []
    if name == "spatial":
        ents = {"item": OBJECTS[:n], "place": PLACES[: max(3, n // 2)]}
        unary = SP_UNARY[: cfg.n_unary_preds]
        binary = ("left_of", "right_of", "above", "below", "inside", "contains", "disjoint")
        sigs = {**_sigs(unary, 1, "item"), **_sigs(binary[: cfg.n_binary_preds + 4], 2, "item")}
        bg = [
            Rule((Atom("left_of", ("?x", "?y")),), Atom("right_of", ("?y", "?x")), "spatial", "converse"),
            Rule((Atom("above", ("?x", "?y")),), Atom("below", ("?y", "?x")), "spatial", "converse"),
            Rule((Atom("inside", ("?x", "?y")),), Atom("contains", ("?y", "?x")), "spatial", "converse"),
            Rule((Atom("inside", ("?x", "?y")), Atom("inside", ("?y", "?z"))), Atom("inside", ("?x", "?z")), "spatial", "composition"),
            Rule((Atom("left_of", ("?x", "?y")), Atom("left_of", ("?y", "?z"))), Atom("left_of", ("?x", "?z")), "spatial", "composition"),
            Rule((Atom("above", ("?x", "?y")), Atom("above", ("?y", "?z"))), Atom("above", ("?x", "?z")), "spatial", "composition"),
            Rule((Atom("disjoint", ("?x", "?y")),), Atom("disjoint", ("?y", "?x")), "spatial", "converse"),
        ]
        irreflexive = ("left_of", "right_of", "above", "below", "inside", "contains", "disjoint")
        asymmetric = ("left_of", "right_of", "above", "below", "inside", "contains")
        denials = [Denial((Atom(p, ("?x", "?x")),)) for p in irreflexive]
        denials += [Denial((Atom(p, ("?x", "?y")), Atom(p, ("?y", "?x")))) for p in asymmetric]
        return ents, sigs, bg, denials
    ents = {"person": NAMES[:n]}
    if name == "kinship":
        unary = ("adult", "minor", "kind", "patient", "careful", "trusted", "female", "male")
        binary = ("parent", "ancestor", "sibling", "spouse", "aunt_or_uncle", "helps", "trusts")
        sigs = {**_sigs(unary[: cfg.n_unary_preds], 1), **_sigs(binary[: cfg.n_binary_preds + 5], 2)}
        bg = [
            Rule((Atom("parent", ("?x", "?y")),), Atom("ancestor", ("?x", "?y")), "kin", "bridge"),
            Rule((Atom("parent", ("?x", "?y")), Atom("ancestor", ("?y", "?z"))), Atom("ancestor", ("?x", "?z")), "kin", "composition"),
            Rule((Atom("parent", ("?p", "?x")), Atom("parent", ("?p", "?y")), ("!=", "?x", "?y")), Atom("sibling", ("?x", "?y")), "kin", "sibling"),
            Rule((Atom("sibling", ("?x", "?y")),), Atom("sibling", ("?y", "?x")), "kin", "converse"),
            Rule((Atom("spouse", ("?x", "?y")),), Atom("spouse", ("?y", "?x")), "kin", "converse"),
            Rule((Atom("parent", ("?x", "?y")), Atom("sibling", ("?x", "?z"))), Atom("aunt_or_uncle", ("?z", "?y")), "kin", "bridge"),
        ]
        denials = [
            Denial((Atom("male", ("?x",)), Atom("female", ("?x",)))),
            Denial((Atom("adult", ("?x",)), Atom("minor", ("?x",)))),
        ]
        irreflexive = ("parent", "ancestor", "sibling", "spouse", "aunt_or_uncle")
        asymmetric = ("parent", "ancestor")
        denials += [Denial((Atom(p, ("?x", "?x")),)) for p in irreflexive]
        denials += [Denial((Atom(p, ("?x", "?y")), Atom(p, ("?y", "?x")))) for p in asymmetric]
        return ents, sigs, bg, denials
    unary = GEN_UNARY[: cfg.n_unary_preds]
    binary = GEN_BINARY[: cfg.n_binary_preds]
    return ents, {**_sigs(unary, 1), **_sigs(binary, 2)}, [], []


def _vars_for(sig):
    return tuple(f"?{chr(120 + i)}" for i in range(len(sig.arg_types)))


def _random_atom(sigs, entities, arity=None, ground=False, sign=None, pred=None):
    choices = [s for s in sigs.values() if arity is None or len(s.arg_types) == arity]
    sig = sigs[pred] if pred else random.choice(choices)
    args = []
    for i, typ in enumerate(sig.arg_types):
        args.append(random.choice(entities[typ]) if ground else f"?{chr(120 + i)}")
    return Atom(sig.name, tuple(args), random.choice([True, False]) if sign is None else sign)


def _fresh_fact(theory, used):
    for _ in range(100):
        a = _random_atom(theory.pred_sigs, theory.entities, ground=True, sign=random.random() > 0.18)
        if len(a.args) == 2 and a.args[0] == a.args[1]:
            continue
        if a not in used and opposite(a) not in used:
            used.add(a)
            return a
    return None


def _sample_rule(sigs):
    unaries = [s for s in sigs.values() if len(s.arg_types) == 1]
    binaries = [s for s in sigs.values() if len(s.arg_types) == 2]
    shapes = []
    if len(unaries) >= 2:
        shapes.append("u_imp")
    if len(unaries) >= 3:
        shapes += ["u_and", "signed"]
    if binaries and len(unaries) >= 2:
        shapes += ["rel_y", "rel_x"]
    if len(binaries) >= 2:
        shapes.append("converse")
    if len(binaries) >= 3:
        shapes.append("composition")
    if not shapes:
        raise ValueError("not enough predicates to sample a rule")
    shape = random.choice(shapes)
    neg_head = shape == "signed" or random.random() < 0.15
    if shape == "u_imp":
        if len(unaries) < 2:
            raise ValueError("need at least two unary predicates")
        a, b = random.sample(unaries, 2)
        return Rule((Atom(a.name, ("?x",)),), Atom(b.name, ("?x",), not neg_head), shape=shape)
    if shape in ("u_and", "signed"):
        if len(unaries) < 3:
            raise ValueError("need at least three unary predicates")
        a, b, c = random.sample(unaries, 3)
        return Rule((Atom(a.name, ("?x",)), Atom(b.name, ("?x",))), Atom(c.name, ("?x",), not neg_head), shape=shape)
    if shape == "rel_y":
        r = random.choice(binaries); a, b = random.sample(unaries, 2)
        return Rule((Atom(r.name, ("?x", "?y")), Atom(a.name, ("?y",))), Atom(b.name, ("?x",), not neg_head), shape=shape)
    if shape == "rel_x":
        r = random.choice(binaries); a, b = random.sample(unaries, 2)
        return Rule((Atom(r.name, ("?x", "?y")), Atom(a.name, ("?x",))), Atom(b.name, ("?y",), not neg_head), shape=shape)
    if shape == "converse":
        r, s = random.sample(binaries, 2)
        return Rule((Atom(r.name, ("?x", "?y")),), Atom(s.name, ("?y", "?x"), not neg_head), shape=shape)
    if shape == "composition":
        r, s, t = random.sample(binaries, 3)
        return Rule((Atom(r.name, ("?x", "?y")), Atom(s.name, ("?y", "?z"))), Atom(t.name, ("?x", "?z"), not neg_head), shape=shape)
    raise AssertionError(f"unknown rule shape: {shape}")


def _bad_rule(rule):
    if any(isinstance(b, Atom) and b == rule.head for b in rule.body):
        return True
    conflicts = {frozenset(("male", "female")), frozenset(("adult", "minor"))}
    positive = defaultdict(set)
    for b in rule.body:
        if isinstance(b, Atom) and b.sign:
            positive[b.args].add(b.pred)
    return any(pair <= preds for preds in positive.values() for pair in conflicts)


def _plant_backbone(theory, sigs, entities):
    unaries = [s for s in sigs.values() if len(s.arg_types) == 1]
    binaries = [s for s in sigs.values() if len(s.arg_types) == 2]
    options = ["unary"]
    if len(unaries) >= 2 and binaries:
        options.append("bridge")
    if unaries and len(binaries) >= 3:
        options.append("composition")
    if len(unaries) >= 4:
        options.append("conjunctive")
    kind = random.choice(options)

    if kind == "bridge":
        r = random.choice(binaries)
        a, b, c = random.sample(unaries, 3 if len(unaries) >= 3 else 2) if len(unaries) >= 3 else (*random.sample(unaries, 2), None)
        x, y = [random.choice(entities[t]) for t in r.arg_types]
        if x == y:
            y = random.choice([e for e in entities[r.arg_types[1]] if e != x] or entities[r.arg_types[1]])
        theory.facts += [Atom(r.name, (x, y)), Atom(a.name, (y,))]
        theory.rules.append(Rule((Atom(r.name, ("?x", "?y")), Atom(a.name, ("?y",))), Atom(b.name, ("?x",)), "backbone", "rel_y"))
        if c:
            theory.rules.append(Rule((Atom(b.name, ("?x",)),), Atom(c.name, ("?x",)), "backbone", "u_imp"))
        return {"kind": kind, "entities": (x, y), "unaries": tuple(s.name for s in (a, b) + ((c,) if c else ())), "binaries": (r.name,)}

    if kind == "composition":
        r, s, t = random.sample(binaries, 3)
        a = random.choice(unaries)
        x = random.choice(entities[r.arg_types[0]])
        y = random.choice(entities[r.arg_types[1]])
        z = random.choice(entities[s.arg_types[1]])
        if x == y:
            y = random.choice([e for e in entities[r.arg_types[1]] if e != x] or entities[r.arg_types[1]])
        if y == z:
            z = random.choice([e for e in entities[s.arg_types[1]] if e != y] or entities[s.arg_types[1]])
        theory.facts += [Atom(r.name, (x, y)), Atom(s.name, (y, z))]
        theory.rules += [
            Rule((Atom(r.name, ("?x", "?y")), Atom(s.name, ("?y", "?z"))), Atom(t.name, ("?x", "?z")), "backbone", "composition"),
            Rule((Atom(t.name, ("?x", "?z")),), Atom(a.name, ("?x",)), "backbone", "rel_to_unary"),
        ]
        return {"kind": kind, "entities": (x, y, z), "unaries": (a.name,), "binaries": (r.name, s.name, t.name)}

    if kind == "conjunctive":
        a, b, c, d = random.sample(unaries, 4)
        x = random.choice(entities[a.arg_types[0]])
        theory.facts += [Atom(a.name, (x,)), Atom(b.name, (x,))]
        theory.rules += [
            Rule((Atom(a.name, ("?x",)), Atom(b.name, ("?x",))), Atom(c.name, ("?x",)), "backbone", "u_and"),
            Rule((Atom(c.name, ("?x",)),), Atom(d.name, ("?x",)), "backbone", "u_imp"),
        ]
        return {"kind": kind, "entities": (x,), "unaries": tuple(s.name for s in (a, b, c, d)), "binaries": ()}

    if len(unaries) >= 4:
        chain = random.sample(unaries, random.randint(3, min(5, len(unaries))))
        ent = random.choice(entities[chain[0].arg_types[0]])
        theory.facts.append(Atom(chain[0].name, (ent,)))
        for i, (a, b) in enumerate(zip(chain, chain[1:])):
            sign = True if i + 2 < len(chain) else random.random() > 0.25
            theory.rules.append(Rule((Atom(a.name, ("?x",)),), Atom(b.name, ("?x",), sign), "backbone", "u_imp"))
        return {"kind": "unary", "entities": (ent,), "unaries": tuple(s.name for s in chain), "binaries": ()}
    return None


def _add_near_misses(theory, sigs, entities, backbone, n=4):
    if not backbone:
        return
    unaries = [s.name for s in sigs.values() if len(s.arg_types) == 1]
    binaries = [s.name for s in sigs.values() if len(s.arg_types) == 2]
    es = list(next(iter(entities.values())))
    ents = tuple(backbone.get("entities", ()))
    us = tuple(backbone.get("unaries", ()))
    bs = tuple(backbone.get("binaries", ()))
    seen = set(theory.facts)
    def add_fact(a):
        if a in seen or opposite(a) in seen:
            return False
        theory.facts.append(a)
        seen.add(a)
        return True
    added = 0
    while added < n:
        kind = random.choice(["wrong_entity", "wrong_pred", "polarity", "near_rule"])
        if kind == "wrong_entity" and bs and us and len(ents) >= 2:
            x, y = ents[0], ents[1]
            other = random.choice([e for e in es if e not in {x, y}] or es)
            ok = add_fact(Atom(bs[0], (x, other)))
            ok = add_fact(Atom(us[0], (other,), random.random() > 0.35)) or ok
        elif kind == "wrong_pred" and len(bs) >= 1 and len(binaries) >= 2 and len(ents) >= 2:
            alt = random.choice([b for b in binaries if b not in bs] or binaries)
            ok = add_fact(Atom(alt, (ents[0], ents[1])))
        elif kind == "polarity" and us and ents:
            ok = add_fact(Atom(us[0], (random.choice(ents),), False))
        elif kind == "near_rule" and us:
            a = random.choice(us)
            b = random.choice([u for u in unaries if u not in us] or unaries)
            c = random.choice([u for u in unaries if u != b] or unaries)
            rule = Rule((Atom(a, ("?x",)), Atom(b, ("?x",))), Atom(c, ("?x",)), "near_miss", "u_and")
            ok = rule not in theory.rules and not _bad_rule(rule)
            if ok:
                theory.rules.append(rule)
        else:
            continue
        added += int(ok)


def sample_theory(cfg):
    pack = random.choice(tuple(cfg.domain_packs))
    entities, sigs, bg, denials = _domain_pack(pack, cfg)
    theory = Theory([], [], denials, sigs, entities, pack)
    used = set()
    backbone = None
    if pack in {"abstract", "surface"}:
        backbone = _plant_backbone(theory, sigs, entities)
        _add_near_misses(theory, sigs, entities, backbone, cfg.n_distractors)
    elif pack == "spatial":
        es = entities["item"]
        a, b, c = random.sample(es, min(3, len(es)))
        rel = random.choice(["left_of", "above", "inside"])
        theory.facts += [Atom(rel, (a, b)), Atom(rel, (b, c))]
    elif pack == "kinship":
        es = entities["person"]
        a, b, c = random.sample(es, min(3, len(es)))
        theory.facts += [Atom("parent", (a, b)), Atom("parent", (b, c))]
    used.update(theory.facts)
    for _ in range(cfg.n_facts):
        if f := _fresh_fact(theory, used):
            theory.facts.append(f)
    theory.rules = list(bg) + theory.rules
    if pack in {"abstract", "surface"}:
        used_rules = set(theory.rules)
        for _ in range(cfg.n_rules):
            for _ in range(20):
                rule = _sample_rule(sigs)
                if rule not in used_rules and not _bad_rule(rule):
                    theory.rules.append(rule)
                    used_rules.add(rule)
                    break
    return theory


def support_atoms(atom, deriv):
    d = deriv[atom]
    if d.rule is None:
        return {atom}
    out = set()
    for p in d.parents:
        out |= support_atoms(p, deriv)
    return out


def support_sources(atom, deriv, source):
    d = deriv[atom]
    if d.rule is None:
        return {source[atom]} if atom in source else set()
    out = {source[d.rule]} if d.rule in source else set()
    for p in d.parents:
        out |= support_sources(p, deriv, source)
    return out


def _all_ground_atoms(theory, signs=(True, False)):
    for sig in theory.pred_sigs.values():
        pools = [theory.entities[t] for t in sig.arg_types]
        for args in itertools.product(*pools):
            if len(args) == 2 and args[0] == args[1]:
                continue
            for sign in signs:
                yield Atom(sig.name, tuple(args), sign)


def close_with(theory, extra):
    t = Theory(list(theory.facts) + list(extra), theory.rules, theory.denials, theory.pred_sigs, theory.entities, theory.domain_pack)
    return chase(t, max_depth=None)


def choose_example(theory, res, cfg, label_signs=None, label_depths=None):
    label_signs = label_signs or Counter()
    label_depths = label_depths or Counter()
    derived = [a for a in res.closure if res.derivations[a].depth > 0]
    non_direct = [a for a in derived if opposite(a) not in theory.facts and a not in theory.facts]
    target_depths = tuple(range(cfg.min_target_depth, min(cfg.max_target_depth, cfg.max_depth) + 1))
    depth_ok = lambda a: res.derivations[a].depth in target_depths
    def support_size_ok(a):
        n = len(support_atoms(a, res.derivations))
        if n < cfg.min_target_support_size:
            return False
        if cfg.max_target_support_size is not None and n > cfg.max_target_support_size:
            return False
        return True
    def prefer_support_range(pool, target=lambda x: x):
        preferred = [h for h in pool if support_size_ok(target(h))]
        return preferred or pool
    r = random.random()
    wants = "neutral" if r < cfg.neutral_rate else "contradiction" if r < cfg.neutral_rate + cfg.contradiction_rate else "entailment"
    labels = [wants, "entailment", "contradiction", "neutral"]
    seen = set()
    def balanced(label, pool):
        want = True if label_signs[(label, True)] <= label_signs[(label, False)] else False
        same = [h for h in pool if h.sign == want]
        return same or pool
    def choose_by_depth(label, pool, target=lambda x: x):
        by_depth = defaultdict(list)
        for h in pool:
            by_depth[res.derivations[target(h)].depth].append(h)
        available = [d for d in target_depths if by_depth[d]]
        if not available:
            return None
        min_fill = min(label_depths[(label, d)] for d in available)
        least = [d for d in available if label_depths[(label, d)] == min_fill]
        d = random.choices(least, weights=[d * d for d in least])[0]
        return random.choice(by_depth[d])

    for label in [x for x in labels if not (x in seen or seen.add(x))]:
        if label == "entailment":
            pool = prefer_support_range(balanced(label, [a for a in non_direct if depth_ok(a)]))
            if pool:
                h = choose_by_depth(label, pool)
                if h is None:
                    continue
                return label, h, res.derivations[h], support_atoms(h, res.derivations)
        if label == "contradiction":
            pool = prefer_support_range(
                balanced(label, [opposite(a) for a in non_direct if opposite(a) not in theory.facts and depth_ok(a)]),
                opposite,
            )
            if pool:
                h = choose_by_depth(label, pool, opposite)
                if h is None:
                    continue
                d = res.derivations[opposite(h)]
                return label, h, d, support_atoms(opposite(h), res.derivations)
        if label == "neutral":
            closure = res.closure
            near_preds = Counter(a.pred for a in derived or closure)
            pool = sorted(
                [a for a in _all_ground_atoms(theory) if a not in closure and opposite(a) not in closure],
                key=lambda a: -near_preds[a.pred],
            )
            pool = balanced(label, pool)
            near, rest = pool[: min(30, len(pool))], pool[min(30, len(pool)) :]
            random.shuffle(near)
            pool = near + rest
            for h in pool[:80]:
                if not close_with(theory, [h]).inconsistent and not close_with(theory, [opposite(h)]).inconsistent:
                    return label, h, None, set()
    return None


def pred_words(pred):
    return pred.replace("_", " ")


def tag_word(pred):
    return TAG_WORDS[int(pred[1:]) % len(TAG_WORDS)] if pred.startswith("p") and pred[1:].isdigit() else pred_words(pred)


def rel_word(pred):
    return REL_WORDS[int(pred[1:]) % len(REL_WORDS)] if pred.startswith("r") and pred[1:].isdigit() else pred_words(pred)


def atom_text(a, pack="surface"):
    if pack in {"surface", "abstract"} and a.pred.startswith("p"):
        t = tag_word(a.pred)
        return f"{a.args[0]} is {'not ' if not a.sign else ''}{t} tagged"
    if pack in {"surface", "abstract"} and a.pred.startswith("r"):
        r = rel_word(a.pred)
        if a.sign:
            return f"{a.args[0]} is {r} to {a.args[1]}"
        return f"{a.args[0]} is not {r} to {a.args[1]}"
    p = pred_words(a.pred)
    neg = "not " if not a.sign else ""
    if len(a.args) == 1:
        return f"{a.args[0]} is {neg}{p}"
    if a.sign:
        return f"{a.args[0]} {p} {a.args[1]}"
    return f"{a.args[0]} does not {p} {a.args[1]}"


def _lit_schema(a, names=None, pack="surface"):
    names = names or {"?x": "x", "?y": "y", "?z": "z", "?p": "p"}
    args = [names.get(x, x) for x in a.args]
    if pack in {"surface", "abstract"} and a.pred.startswith("p"):
        return f"{args[0]} is {'not ' if not a.sign else ''}{tag_word(a.pred)} tagged"
    if pack in {"surface", "abstract"} and a.pred.startswith("r"):
        return f"{args[0]} is {'not ' if not a.sign else ''}{rel_word(a.pred)} to {args[1]}"
    p = pred_words(a.pred)
    if len(a.args) == 1:
        return f"{args[0]} is {'not ' if not a.sign else ''}{p}"
    if a.sign:
        return f"{args[0]} {p} {args[1]}"
    return f"{args[0]} does not {p} {args[1]}"


def rule_text(rule, rid=None, pack="surface"):
    atoms = [b for b in rule.body if isinstance(b, Atom)]
    checks = [b for b in rule.body if not isinstance(b, Atom)]
    names = {"?x": "x", "?y": "y", "?z": "z", "?p": "p"}
    parts = [_lit_schema(a, names, pack) for a in atoms]
    parts += [f"{c[1][1:]} is different from {c[2][1:]}" for c in checks if c[0] == "!="]
    body = " and ".join(parts)
    head = _lit_schema(rule.head, names, pack)
    vars_ = sorted({v[1:] for a in atoms + [rule.head] for v in a.args if is_var(v)} | {v[1:] for c in checks for v in c[1:] if is_var(v)})
    q = ", ".join(vars_)
    templates = [
        f"For all {q}, if {body}, then {head}.",
        f"Whenever {body}, {head}.",
        f"From {body}, it follows that {head}.",
    ]
    if len(atoms) == 1 and len(atoms[0].args) == 1 and len(rule.head.args) == 1:
        if pack in {"surface", "abstract"}:
            a = ("not " if not atoms[0].sign else "") + tag_word(atoms[0].pred)
            h = ("not " if not rule.head.sign else "") + tag_word(rule.head.pred)
            templates += [
                f"Anyone who is {a} tagged is {h} tagged.",
                f"Every {a}-tagged person is {h} tagged.",
                f"If a person is {a} tagged, then that person is {h} tagged.",
            ]
        else:
            a = ("not " if not atoms[0].sign else "") + pred_words(atoms[0].pred)
            h = ("not " if not rule.head.sign else "") + pred_words(rule.head.pred)
            templates += [f"All things that are {a} are {h}.", f"Every {a} entity is {h}.", f"Being {a} implies being {h}."]
    elif len(atoms) == 2 and all(len(a.args) == 1 and a.args == ("?x",) for a in atoms) and rule.head.args == ("?x",):
        a = tag_word(atoms[0].pred) if pack in {"surface", "abstract"} else pred_words(atoms[0].pred)
        b = tag_word(atoms[1].pred) if pack in {"surface", "abstract"} else pred_words(atoms[1].pred)
        h = ("not " if not rule.head.sign else "") + (tag_word(rule.head.pred) if pack in {"surface", "abstract"} else pred_words(rule.head.pred))
        tagged = " tagged" if pack in {"surface", "abstract"} else ""
        templates += [
            f"Anyone who is {a}{tagged} and {b}{tagged} is {h}{tagged}.",
            f"Every {a}-tagged person who is {b}{tagged} is {h}{tagged}." if pack in {"surface", "abstract"} else f"Every {a} entity that is also {b} is {h}.",
            f"If a person is {a}{tagged} and {b}{tagged}, then that person is {h}{tagged}.",
        ]
    elif len(atoms) == 2 and len(atoms[0].args) == 2 and atoms[1].args == ("?y",) and rule.head.args == ("?x",):
        r = rel_word(atoms[0].pred) if pack in {"surface", "abstract"} else pred_words(atoms[0].pred)
        a = tag_word(atoms[1].pred) if pack in {"surface", "abstract"} else pred_words(atoms[1].pred)
        h = ("not " if not rule.head.sign else "") + (tag_word(rule.head.pred) if pack in {"surface", "abstract"} else pred_words(rule.head.pred))
        tagged = " tagged" if pack in {"surface", "abstract"} else ""
        templates += [
            f"Anyone {r} to a {a}-tagged person is {h}{tagged}.",
            f"If a person is {r} to someone {a}{tagged}, then that person is {h}{tagged}.",
            f"A person is {h}{tagged} when they are {r} to a {a}-tagged person.",
        ]
    elif len(atoms) == 2 and len(atoms[0].args) == 2 and atoms[1].args == ("?x",) and rule.head.args == ("?y",):
        r = rel_word(atoms[0].pred) if pack in {"surface", "abstract"} else pred_words(atoms[0].pred)
        a = tag_word(atoms[1].pred) if pack in {"surface", "abstract"} else pred_words(atoms[1].pred)
        h = ("not " if not rule.head.sign else "") + (tag_word(rule.head.pred) if pack in {"surface", "abstract"} else pred_words(rule.head.pred))
        tagged = " tagged" if pack in {"surface", "abstract"} else ""
        templates += [
            f"Anyone {r} from a {a}-tagged person is {h}{tagged}.",
            f"If a {a}-tagged person is {r} to someone, then that other person is {h}{tagged}.",
            f"People reached by a {r} relation from a {a}-tagged person are {h}{tagged}.",
        ]
    elif len(atoms) == 2 and all(len(a.args) == 2 for a in atoms) and rule.head.args == ("?x", "?z"):
        r = rel_word(atoms[0].pred) if pack in {"surface", "abstract"} else pred_words(atoms[0].pred)
        s = rel_word(atoms[1].pred) if pack in {"surface", "abstract"} else pred_words(atoms[1].pred)
        h = rel_word(rule.head.pred) if pack in {"surface", "abstract"} else pred_words(rule.head.pred)
        templates += [
            f"If one person is {r} to a second person, and the second is {s} to a third, then the first is {h} to the third.",
            f"Anyone {r} to someone who is {s} to a third person is {h} to that third person.",
            f"{r.title()} relations followed by {s} relations imply {h} relations.",
        ]
    elif len(atoms) == 1 and len(atoms[0].args) == 2 and len(rule.head.args) == 2 and rule.head.args == ("?y", "?x"):
        r = rel_word(atoms[0].pred) if pack in {"surface", "abstract"} else pred_words(atoms[0].pred)
        h = rel_word(rule.head.pred) if pack in {"surface", "abstract"} else pred_words(rule.head.pred)
        templates += [
            f"If one person is {r} to another, then the second is {h} to the first.",
            f"Every {r} relation creates a {h} relation in the reverse direction.",
        ]
    if rid is None:
        rid = random.randrange(len(templates))
    return templates[rid % len(templates)], (rule.shape, rid % len(templates), "if" if rid % 3 == 0 else "whenever", "normal")


def render(theory):
    lines, source = [], {}
    for a in theory.facts:
        source[a] = len(lines)
        lines.append(atom_text(a, theory.domain_pack) + ".")
    surf = []
    for r in theory.rules:
        txt, key = rule_text(r, pack=theory.domain_pack)
        source[r] = len(lines)
        surf.append((*key, theory.domain_pack))
        lines.append(txt)
    return lines, source, surf


def trace_for(target, deriv, source, pack="surface"):
    if target is None:
        return ""
    lines, seen = [], {}

    def rec(a):
        if a in seen:
            return seen[a]
        d = deriv[a]
        parent_ids = [rec(p) for p in d.parents]
        idx = len(lines) + 1
        seen[a] = idx
        if d.rule is None:
            ctx = f"P{source.get(a, '?')}"
        else:
            ctx = ";".join([f"P{source.get(d.rule, '?')}"] + [str(i) for i in parent_ids])
        lines.append(f"{idx}. [{ctx}] {atom_text(a, pack)}")
        return idx

    rec(target)
    return "\n".join(lines)


def derivation_rules(atom, deriv):
    if atom is None:
        return set()
    d = deriv[atom]
    if d.rule is None:
        return set()
    out = {d.rule}
    for p in d.parents:
        out |= derivation_rules(p, deriv)
    return out


def participating_rules(deriv):
    return {d.rule for d in deriv.values() if d.rule is not None}


def bin_key(label, hyp, d, support, theory, target=None, deriv=None):
    depth = 0 if d is None else d.depth
    support_size = len(support)
    uses_binary = any(len(a.args) == 2 for a in support | {hyp})
    rules = derivation_rules(target, deriv) if target is not None and deriv is not None else set()
    uses_signed = any(not r.head.sign for r in rules)
    uses_comp = any("composition" in r.shape for r in rules)
    return (label, min(depth, 4), min(support_size, 4), uses_binary, uses_signed, uses_comp, theory.domain_pack)


def target_for(label, hyp):
    return opposite(hyp) if label == "contradiction" else hyp if label == "entailment" else None


def indexed_premise(lines):
    return "\n".join(f"[{i}] {x}" for i, x in enumerate(lines))


def format_candidate_list(candidates, pack):
    return "\n".join(f"[{i}] {atom_text(a, pack)}." for i, a in enumerate(candidates))


def case_metadata(case, key=None):
    d = case.derivation
    return edict(
        premise=case.lines,
        hypothesis=atom_text(case.hyp, case.theory.domain_pack) + ".",
        label=case.label,
        domain_pack=case.theory.domain_pack,
        depth=None if d is None else d.depth,
        hypothesis_sign=case.hyp.sign,
        support_indices=[] if case.target is None else sorted(support_sources(case.target, case.res.derivations, case.source)),
        live_rule_rate=case.live_rule_rate,
        proof_rule_rate=case.proof_rule_rate,
        bin_key=repr(key) if key is not None else "",
        surface_bins=[repr(x) for x in case.surf],
        cot=trace_for(case.target, case.res.derivations, case.source, case.theory.domain_pack),
    )


def generate_case(cfg, allowed_labels=("entailment", "contradiction", "neutral"), state=None):
    state = state or {}
    bins = state.setdefault("bins", Counter())
    label_counts = state.setdefault("label_counts", Counter())
    label_signs = state.setdefault("label_signs", Counter())
    label_depths = state.setdefault("label_depths", Counter())
    surface = state.setdefault("surface", Counter())
    allowed_labels = set(allowed_labels)
    for _ in range(500):
        theory = sample_theory(cfg)
        res = chase(theory, max_depth=None)
        if res.inconsistent:
            continue
        choice = choose_example(theory, res, cfg, label_signs, label_depths)
        if not choice:
            continue
        label, hyp, derivation, support = choice
        if label not in allowed_labels:
            continue
        ls_key = (label, hyp.sign)
        other = label_signs[(label, not hyp.sign)]
        if label_signs[ls_key] > other + 6 and random.random() > 0.2:
            continue
        lines, source, surf = render(theory)
        if surf and surface:
            ordered = sorted(surface.values())
            median = ordered[len(ordered) // 2]
            overused = any(surface[x] > max(4, median * 2) for x in surf)
            if overused and random.random() < 0.85:
                continue
        target = target_for(label, hyp)
        d = None if target is None else res.derivations[target]
        used_rules = derivation_rules(target, res.derivations) if target is not None else set()
        live_rule_rate = len(participating_rules(res.derivations)) / max(1, len(theory.rules))
        proof_rule_rate = len(used_rules) / max(1, len(theory.rules))
        if live_rule_rate < 0.25:
            continue
        if label != "neutral" and proof_rule_rate < 0.10:
            continue
        key = bin_key(label, hyp, d, support, theory, target, res.derivations)
        min_label = min([label_counts[x] for x in allowed_labels] or [0])
        label_needs_examples = label_counts[label] <= min_label + 3
        if bins[key] >= cfg.max_bin_size and not label_needs_examples and random.random() > 0.2:
            continue
        bins[key] += 1
        label_counts[label] += 1
        label_signs[ls_key] += 1
        if d is not None:
            label_depths[(label, d.depth)] += 1
        surface.update(surf)
        return MultistepCase(theory, res, label, hyp, target, d, support, lines, source, surf, live_rule_rate, proof_rule_rate), key
    return None, None


def near_miss_abducibles(theory, removed, n):
    out, seen = [], set(removed)
    seen |= set(theory.facts)
    ents = list(next(iter(theory.entities.values())))
    unaries = [s.name for s in theory.pred_sigs.values() if len(s.arg_types) == 1]
    binaries = [s.name for s in theory.pred_sigs.values() if len(s.arg_types) == 2]
    def add(a):
        if a in seen:
            return
        seen.add(a)
        out.append(a)
    for a in removed:
        add(opposite(a))
        if len(a.args) == 1:
            others = [e for e in ents if e != a.args[0]]
            preds = [p for p in unaries if p != a.pred]
            if others:
                add(Atom(a.pred, (random.choice(others),), a.sign))
            if preds:
                add(Atom(random.choice(preds), a.args, a.sign))
        elif len(a.args) == 2:
            preds = [p for p in binaries if p != a.pred]
            others = [e for e in ents if e not in a.args] or ents
            add(Atom(a.pred, (a.args[1], a.args[0]), a.sign))
            if preds:
                add(Atom(random.choice(preds), a.args, a.sign))
            add(Atom(a.pred, (a.args[0], random.choice(others)), a.sign))
    random.shuffle(out)
    return out[:n]


def minimal_abductions(theory, candidates, target, max_k=2):
    for k in range(1, max_k + 1):
        out = []
        for ids in itertools.combinations(range(len(candidates)), k):
            res = close_with(theory, [candidates[i] for i in ids])
            if not res.inconsistent and target in res.closure:
                out.append(ids)
        if out:
            return out
    return []


def necessary_indices(case):
    if case.target is None:
        return []
    # Any globally necessary premise must occur in every proof, including this one.
    support = sorted(support_sources(case.target, case.res.derivations, case.source))
    nec = []
    for i in support:
        keep = lambda x: case.source.get(x) != i
        sub = Theory(
            [a for a in case.theory.facts if keep(a)],
            [r for r in case.theory.rules if keep(r)],
            case.theory.denials,
            case.theory.pred_sigs,
            case.theory.entities,
            case.theory.domain_pack,
        )
        if case.target not in chase(sub, max_depth=None).closure:
            nec.append(i)
    return nec


def parse_indices(s):
    try:
        return {int(x.strip()) for x in str(s).strip().strip("[]").split(",") if x.strip()}
    except ValueError:
        return set()


def make_direct_abduction_case(cfg):
    entities, sigs, _, _ = _domain_pack("surface", cfg)
    es = list(entities["entity"])
    x, y = random.sample(es, 2)
    unaries = [s.name for s in sigs.values() if len(s.arg_types) == 1]
    binaries = [s.name for s in sigs.values() if len(s.arg_types) == 2]
    label = random.choice(["entailment", "contradiction"])
    shape = random.choice(["unary", "bridge", "conjunctive"])
    facts, rules, removed = [], [], []

    if shape == "bridge" and binaries and len(unaries) >= 3:
        r = random.choice(binaries)
        a, b, c = random.sample(unaries, 3)
        removed = [Atom(a, (y,))]
        facts = [Atom(r, (x, y)), Atom(random.choice(unaries), (random.choice(es),))]
        rules = [
            Rule((Atom(r, ("?x", "?y")), Atom(a, ("?y",))), Atom(b, ("?x",)), "abduction", "rel_y"),
            Rule((Atom(b, ("?x",)),), Atom(c, ("?x",), label == "entailment"), "abduction", "u_imp"),
        ]
        hyp = Atom(c, (x,), True)
    elif shape == "conjunctive" and len(unaries) >= 4:
        a, b, c, d = random.sample(unaries, 4)
        removed = [Atom(a, (x,))]
        facts = [Atom(b, (x,)), Atom(a, (y,)), Atom(random.choice(unaries), (random.choice(es),))]
        rules = [
            Rule((Atom(a, ("?x",)), Atom(b, ("?x",))), Atom(c, ("?x",)), "abduction", "u_and"),
            Rule((Atom(c, ("?x",)),), Atom(d, ("?x",), label == "entailment"), "abduction", "u_imp"),
        ]
        hyp = Atom(d, (x,), True)
    else:
        a, b, c = random.sample(unaries, 3)
        removed = [Atom(a, (x,))]
        facts = [Atom(a, (y,)), Atom(random.choice(unaries), (random.choice(es),))]
        rules = [
            Rule((Atom(a, ("?x",)),), Atom(b, ("?x",)), "abduction", "u_imp"),
            Rule((Atom(b, ("?x",)),), Atom(c, ("?x",), label == "entailment"), "abduction", "u_imp"),
        ]
        hyp = Atom(c, (x,), True)

    target = target_for(label, hyp)
    clean_facts, seen = [], set()
    for fact in facts:
        if fact not in seen and opposite(fact) not in seen:
            clean_facts.append(fact)
            seen.add(fact)
    facts = clean_facts
    theory = Theory(facts, rules, [], sigs, entities, "surface")
    if target in chase(theory, None).closure:
        return None
    if target not in close_with(theory, removed).closure:
        return None

    candidates = removed + near_miss_abducibles(theory, removed, cfg.n_candidates * 3)
    filtered = []
    for cand in candidates:
        if cand in filtered:
            continue
        cres = close_with(theory, [cand])
        if cand in removed or (not cres.inconsistent and target not in cres.closure):
            filtered.append(cand)
        if len(filtered) >= cfg.n_candidates:
            break
    random.shuffle(filtered)
    sols = minimal_abductions(theory, filtered, target, cfg.max_abduction_size)
    if not sols or (cfg.require_unique and len(sols) != 1):
        return None
    lines, _, _ = render(theory)
    return edict(theory=theory, label=label, hyp=hyp, target=target, lines=lines,
                 candidates=filtered, answer=list(sols[0]), domain_pack="surface")


class MultistepNLI(Task):
    def __init__(self, config=MultistepNLIConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio = 1 / 3
        self._case_state = {}

    def generate(self):
        case, key = generate_case(self.config, state=self._case_state)
        if case:
            return Problem(case_metadata(case, key), case.label)
        raise RuntimeError("could not generate a consistent multistep_nli example")

    def prompt(self, meta):
        prem = "\n".join(meta.premise)
        return (
            f"Premise:\n{prem}\n\n"
            f"Hypothesis:\n{meta.hypothesis}\n\n"
            "If the Premise entails the Hypothesis, the label is 'entailment'.\n"
            "If the Premise contradicts the Hypothesis, the label is 'contradiction'.\n"
            "If neither, the label is 'neutral'.\n"
            "The answer is exactly one word: neutral, contradiction, or entailment."
        )

    def score_answer(self, answer, entry):
        return float(str(answer).strip().lower() == str(entry.answer).strip().lower())

    def balancing_key(self, problem):
        return problem.answer


class MultistepEvidenceRetrieval(Task):
    def __init__(self, config=MultistepNLIConfig()):
        super().__init__(config=config)
        self._case_state = {}

    def generate(self):
        for _ in range(200):
            case, key = generate_case(self.config, ("entailment", "contradiction"), self._case_state)
            if not case:
                continue
            nec = necessary_indices(case)
            if not nec:
                continue
            meta = case_metadata(case, key)
            meta.necessary_indices = nec
            meta.valid_supports = [nec]
            meta.support_indices = nec
            answer = "[" + ", ".join(str(i) for i in nec) + "]"
            return Problem(meta, answer)
        raise RuntimeError("could not generate a unique-support multistep_evidence_retrieval example")

    def prompt(self, meta):
        verb = "entail" if meta.label == "entailment" else "contradict"
        return (
            f"Premise:\n{indexed_premise(meta.premise)}\n\n"
            f"Hypothesis:\n{meta.hypothesis}\n\n"
            f"Which premise statements are necessary to {verb} the hypothesis, "
            "meaning removing any one of them breaks that result?\n"
            "The answer is a list of indices, e.g. [0, 1]."
        )

    def score_answer(self, answer, entry):
        pred = parse_indices(answer)
        valid = [set(x) for x in entry.metadata.get("valid_supports", [])]
        return float(any(pred == x for x in valid))


class MultistepAbduction(Task):
    def __init__(self, config=MultistepAbductionConfig()):
        super().__init__(config=config)
        self._case_state = {}

    def generate(self):
        for _ in range(100):
            abd = make_direct_abduction_case(self.config)
            if not abd:
                continue
            meta = edict(
                premise=abd.lines,
                hypothesis=atom_text(abd.hyp, abd.domain_pack) + ".",
                candidates=[atom_text(a, abd.domain_pack) + "." for a in abd.candidates],
                label=abd.label,
                domain_pack=abd.domain_pack,
            )
            answer = "[" + ", ".join(str(i) for i in abd.answer) + "]"
            return Problem(meta, answer)
        raise RuntimeError("could not generate a consistent multistep_abduction example")

    def prompt(self, meta):
        mode = "entail the hypothesis" if meta.label == "entailment" else "contradict the hypothesis"
        return (
            f"Premise:\n{indexed_premise(meta.premise)}\n\n"
            f"Hypothesis:\n{meta.hypothesis}\n\n"
            f"Candidate additional facts:\n{indexed_premise(meta.candidates)}\n\n"
            f"Which candidate facts, if added to the premise, make the premise {mode}?\n"
            "Return the smallest list of candidate indices, e.g. [0, 2]."
        )

    def score_answer(self, answer, entry):
        parse = lambda s: {x.strip() for x in str(s).strip().strip("[]").split(",") if x.strip()}
        return float(parse(answer) == parse(entry.answer))

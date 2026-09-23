"""Convert first-order formulas to clause form (NNF, prenex, Skolemization, CNF)."""

import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'prenex_skolem_clause_form (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_operations_research_r4/prenex_skolem_clause_form',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 368817805,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

PRED_POOL = ["P", "Q", "R", "H", "G"]
FUN_POOL = ["f", "g", "h"]
VAR_POOL = ["x", "y", "z", "w", "u", "v", "t", "r", "s", "q"]


@dataclass
class PrenexSkolemClauseFormV3Config(Config):
    n_quantifiers: int = 2
    atoms: int = 3
    depth: int = 2
    arity: int = 1
    use_functions: bool = False

    def apply_difficulty(self, level):
        self.n_quantifiers = 2 + level
        self.atoms = 3 + (level // 2)
        self.depth = 2 + (level // 2)
        self.arity = 1 + (level // 3)
        self.use_functions = level >= 2


# ---------------------------------------------------------------- terms -----

def render_term(t):
    if isinstance(t, str):
        return t
    return t[1] + "(" + ",".join(render_term(a) for a in t[2]) + ")"


def render_atom(a):
    pred, terms = a
    if not terms:
        return pred
    return pred + "(" + ",".join(render_term(x) for x in terms) + ")"


def free_vars_of_term(t, out):
    if isinstance(t, str):
        out.add(t)
    else:
        for a in t[2]:
            free_vars_of_term(a, out)


def free_vars_of_atom(a, out):
    for x in a[1]:
        free_vars_of_term(x, out)


def subst_term(t, var, repl):
    if isinstance(t, str):
        return repl if t == var else t
    return ('fun', t[1], tuple(subst_term(a, var, repl) for a in t[2]))


def subst_atom(a, var, repl):
    return (a[0], tuple(subst_term(x, var, repl) for x in a[1]))


# ------------------------------------------------------------- formulas -----
# node encodings:
#   ('atom', pred, (terms...))
#   ('not', f)
#   ('and', f1, f2)
#   ('or', f1, f2)
#   ('imp', f1, f2)
#   ('forall', var, body)
#   ('exists', var, body)


def render_formula(n):
    t = n[0]
    if t == 'atom':
        return render_atom((n[1], n[2]))
    if t == 'not':
        return "not(" + render_formula(n[1]) + ")"
    if t == 'and':
        return "(" + render_formula(n[1]) + " and " + render_formula(n[2]) + ")"
    if t == 'or':
        return "(" + render_formula(n[1]) + " or " + render_formula(n[2]) + ")"
    if t == 'imp':
        return "(" + render_formula(n[1]) + " -> " + render_formula(n[2]) + ")"
    if t == 'forall':
        return "forall " + n[1] + ".(" + render_formula(n[2]) + ")"
    if t == 'exists':
        return "exists " + n[1] + ".(" + render_formula(n[2]) + ")"
    raise ValueError(t)


def free_vars(n, bound, out):
    t = n[0]
    if t == 'atom':
        free_vars_of_atom((n[1], n[2]), out)
    elif t == 'not':
        free_vars(n[1], bound, out)
    elif t in ('and', 'or', 'imp'):
        free_vars(n[1], bound, out)
        free_vars(n[2], bound, out)
    elif t in ('forall', 'exists'):
        if n[1] not in bound:
            nb = bound | {n[1]}
        else:
            nb = bound
        free_vars(n[2], nb, out)


# ------------------------------------------------------------ NNF / prenex --

def to_nnf(n):
    t = n[0]
    if t == 'atom':
        return n
    if t == 'not':
        return neg_nnf(n[1])
    if t == 'and':
        return ('and', to_nnf(n[1]), to_nnf(n[2]))
    if t == 'or':
        return ('or', to_nnf(n[1]), to_nnf(n[2]))
    if t == 'imp':
        return ('or', to_nnf(('not', n[1])), to_nnf(n[2]))
    if t == 'forall':
        return ('forall', n[1], to_nnf(n[2]))
    if t == 'exists':
        return ('exists', n[1], to_nnf(n[2]))
    raise ValueError(t)


def neg_nnf(n):
    t = n[0]
    if t == 'atom':
        return ('not', n)
    if t == 'not':
        return to_nnf(n[1])
    if t == 'and':
        return ('or', neg_nnf(n[1]), neg_nnf(n[2]))
    if t == 'or':
        return ('and', neg_nnf(n[1]), neg_nnf(n[2]))
    if t == 'imp':
        # not(p -> q) = p and not q
        return ('and', to_nnf(n[1]), neg_nnf(n[2]))
    if t == 'forall':
        return ('exists', n[1], neg_nnf(n[2]))
    if t == 'exists':
        return ('forall', n[1], neg_nnf(n[2]))
    raise ValueError(t)


def prenex(n):
    """Return (prefix_list, matrix). prefix_list items are (type, var)."""
    t = n[0]
    if t == 'atom':
        return [], n
    if t == 'not':
        p, m = prenex(n[1])
        return p, ('not', m)
    if t == 'and':
        p1, m1 = prenex(n[1])
        p2, m2 = prenex(n[2])
        return p1 + p2, ('and', m1, m2)
    if t == 'or':
        p1, m1 = prenex(n[1])
        p2, m2 = prenex(n[2])
        return p1 + p2, ('or', m1, m2)
    if t == 'imp':
        p1, m1 = prenex(n[1])
        p2, m2 = prenex(n[2])
        return p1 + p2, ('imp', m1, m2)
    if t == 'forall':
        p, m = prenex(n[2])
        return [('forall', n[1])] + p, m
    if t == 'exists':
        p, m = prenex(n[2])
        return [('exists', n[1])] + p, m
    raise ValueError(t)


# ------------------------------------------------------------- skolemize ----

def skolemize(prefix, matrix):
    """Replace each exists var by a skolem term over preceding forall vars."""
    matrix_out = matrix
    all_term = {}
    n_exist = 0
    forall_seen = []
    for typ, var in prefix:
        if typ == 'forall':
            forall_seen.append(var)
        else:
            args = tuple(forall_seen)
            if args:
                term = ('fun', "sk%d" % n_exist, args)
            else:
                term = "sk%d" % n_exist
            n_exist += 1
            matrix_out = subst_formula(matrix_out, var, term)
            all_term[var] = term
    return matrix_out, all_term


def subst_formula(n, var, repl):
    t = n[0]
    if t == 'atom':
        return ('atom', n[1], tuple(subst_term(x, var, repl) for x in n[2]))
    if t == 'not':
        return ('not', subst_formula(n[1], var, repl))
    if t in ('and', 'or', 'imp'):
        return (t, subst_formula(n[1], var, repl), subst_formula(n[2], var, repl))
    if t in ('forall', 'exists'):
        if n[1] == var:
            return n
        return (t, n[1], subst_formula(n[2], var, repl))
    raise ValueError(t)


# ------------------------------------------------------------------- CNF ----

def cnf_clauses(n):
    """Return list of clauses; each clause is a set of frozenset-literal."""
    t = n[0]
    if t == 'atom':
        return [frozenset([('atom', n[1], n[2])])]
    if t == 'not':
        c = cnf_clauses_neg(n[1])
        return c
    if t == 'and':
        return cnf_clauses(n[1]) + cnf_clauses(n[2])
    if t == 'or':
        return distribute(cnf_clauses(n[1]), cnf_clauses(n[2]))
    if t == 'imp':
        return cnf_clauses(('or', ('not', n[1]), n[2]))
    raise ValueError(t)


def cnf_clauses_neg(n):
    """CNF clauses for a negated NNF node (only push negation to atoms)."""
    t = n[0]
    if t == 'atom':
        return [frozenset([('neg', n[1], n[2])])]
    if t == 'and':
        return distribute(cnf_clauses_neg(n[1]), cnf_clauses_neg(n[2]))
    if t == 'or':
        return cnf_clauses_neg(n[1]) + cnf_clauses_neg(n[2])
    raise ValueError(t)


def distribute(l1, l2):
    return [frozenset(c1 | c2) for c1 in l1 for c2 in l2]


def render_literal(lit):
    if lit[0] == 'neg':
        return "not " + render_atom((lit[1], lit[2]))
    return render_atom((lit[1], lit[2]))


def render_clause_set(clauses):
    rendered = []
    for cl in clauses:
        lits = sorted(render_literal(l) for l in cl)
        rendered.append("{" + ", ".join(lits) + "}")
    return "; ".join(sorted(rendered))


# ------------------------------------------------------------- generation ---

def pick_var(used, idx):
    name = VAR_POOL[idx % len(VAR_POOL)]
    if idx >= len(VAR_POOL):
        name = "v%d" % idx
    if name in used:
        k = 0
        while ("%s%d" % (name, k)) in used:
            k += 1
        name = "%s%d" % (name, k)
    return name


def make_term(vars_in_scope, arity, use_functions):
    r = random.random()
    if vars_in_scope and (r < 0.6 or not use_functions):
        return random.choice(vars_in_scope)
    nargs = random.randint(1, max(1, arity))
    fname = random.choice(FUN_POOL)
    args = [random.choice(vars_in_scope) for _ in range(nargs)]
    return ('fun', fname, tuple(args))


def make_atom(vars_in_scope, arity, use_functions):
    pred = random.choice(PRED_POOL)
    na = random.randint(0, arity)
    terms = [make_term(vars_in_scope, arity, use_functions) for _ in range(na)]
    return ('atom', pred, tuple(terms))


def make_formula_node(scope, arity, use_functions, depth, atoms_remaining):
    """Build a formula node respecting depth/leaf budget. Returns (node, leaves_used)."""
    if atoms_remaining <= 1 or depth <= 0:
        return make_atom(scope, arity, use_functions), 1
    r = random.random()
    if r < 0.28:
        a1, l1 = make_formula_node(scope, arity, use_functions, depth - 1, atoms_remaining - 1)
        return ('not', a1), l1
    if r < 0.56:
        a1, l1 = make_formula_node(scope, arity, use_functions, depth - 1, atoms_remaining - 1)
        a2, l2 = make_formula_node(scope, arity, use_functions, depth - 1, atoms_remaining - 1 - l1)
        return ('and', a1, a2), l1 + l2
    if r < 0.84:
        a1, l1 = make_formula_node(scope, arity, use_functions, depth - 1, atoms_remaining - 1)
        a2, l2 = make_formula_node(scope, arity, use_functions, depth - 1, atoms_remaining - 1 - l1)
        return ('or', a1, a2), l1 + l2
    a1, l1 = make_formula_node(scope, arity, use_functions, depth - 1, atoms_remaining - 1)
    a2, l2 = make_formula_node(scope, arity, use_functions, depth - 1, atoms_remaining - 1 - l1)
    return ('imp', a1, a2), l1 + l2


def make_body(scope, arity, use_functions, depth, atoms):
    node, leaves = make_formula_node(scope, arity, use_functions, depth, atoms)
    return node


def build_instance(config):
    scope = []
    scope_set = set()
    used = set()
    n_q = config.n_quantifiers
    kinds = []
    for i in range(n_q):
        kinds.append('forall' if random.random() < 0.5 else 'exists')
    if 'exists' not in kinds:
        kinds[random.randrange(n_q)] = 'exists'
    if 'forall' not in kinds:
        kinds[random.randrange(n_q)] = 'forall'
    quant = []
    for k in kinds:
        v = pick_var(used, len(quant))
        used.add(v)
        scope.append(v)
        scope_set.add(v)
        quant.append((k, v))
    if random.random() < 0.3:
        fv = pick_var(used, 100 + len(quant))
        used.add(fv)
        scope.append(fv)
        scope_set.add(fv)
    scope = sorted(scope)
    body = make_body(scope, config.arity, config.use_functions, config.depth, config.atoms)
    return quant, body, used


def make_formula(quant, body):
    node = body
    for typ, var in reversed(quant):
        node = (typ, var, node)
    return node


# ------------------------------------------------------------- scoring ------

def _norm(s):
    return re.sub(r"\s+", "", s.strip())


class PrenexSkolemClauseForm(Task):
    summary = ("Convert first-order formulas to clause form via negation normal form, prenex "
               "rearrangement, arity-correct Skolemization and distribution; answer the final "
               "clause set or the Skolem term replacing a named existence-bound variable.")
    config_cls = PrenexSkolemClauseFormV3Config

    def generate_entry(self):
        c = self.config
        for _ in range(20):
            quant, body, used = build_instance(c)
            formula = make_formula(quant, body)
            nnf_node = to_nnf(formula)
            prefix, matrix = prenex(nnf_node)
            matrix_s, all_term = skolemize(prefix, matrix)
            clauses = cnf_clauses(matrix_s)
            clauses = [cl for cl in clauses if len(cl) > 0]
            if not clauses:
                continue
            if len(clauses) > 16:
                continue
            exists_pos = [i for i, (typ, _v) in enumerate(prefix) if typ == 'exists']
            if not exists_pos:
                continue
            # guarantee-clause form valid: every clause uses only skolem terms
            exits = [v for _t, v in prefix if _t == 'exists']
            if not exits:
                continue
            mode = 'skolem' if random.random() < 0.5 else 'clauses'
            if mode == 'skolem':
                i = random.choice(exists_pos)
                target_var = prefix[i][1]
                answer = render_term(all_term[target_var])
            else:
                answer = render_clause_set(clauses)
            s_answer = answer
            # sanity: answer must not be empty
            if not s_answer:
                continue
            prompt = render_formula(formula)
            metadata = {
                "formula": prompt,
                "mode": mode,
                "answer": s_answer,
                "clauses": [list(cl) for cl in clauses][:16],
                "target_var": None if mode == 'clauses' else target_var,
                "target_skolem_term": {} if mode == 'clauses' else {target_var: render_term(all_term[target_var])},
                "name_phrase": ("the variable " + target_var) if mode == 'skolem' else None,
            }
            return Entry(metadata=metadata, answer=s_answer)
        raise RuntimeError("could not build valid instance")

    def render_prompt(self, metadata):
        if metadata["mode"] == "skolem":
            return (
                "Convert the following first-order formula to clause form by pushing negations to "
                "negation normal form, pulling quantifiers out into a prenex, replacing each "
                "existential by a Skolem term that depends on the universal variables in scope, "
                "and distributing to conjunctive normal form.\n"
                "Formula: " + metadata["formula"] + "\n"
                "Give the exact Skolem term that replaces the existential variable bound in the "
                "prenex as this variable: " + metadata["name_phrase"] + ".\n"
                "Write the term exactly as rendered, e.g. f(x) or sk2(y,z) or a plain constant "
                "such as sk1. Answer with the term and nothing else."
            )
        return (
            "Convert the following first-order formula to clause form by pushing negations to "
            "negation normal form, pulling quantifiers out into a prenex, replacing each "
            "existential by a Skolem term that depends on the universal variables in scope, and "
            "distributing to conjunctive normal form.\n"
            "Formula: " + metadata["formula"] + "\n"
            "Write the final clause set as a semicolon-separated list of clauses, each clause a "
            "brace-enclosed comma-separated set of literals such as {not P(a), Q(b)}; {R(x)}. Use "
            "the predicate, function and Skolem function names exactly as introduced. Answer with "
            "the clause set and nothing else."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if _norm(answer) == _norm(entry.answer) else 0.0

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'nominal_equation_solving (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P012',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r4/nominal_equation_solving',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1333628617,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


# ---------------------------------------------------------------------------
# Nominal terms
#   ('at',  name)           atom constant  a,b,c,...
#   ('var', name)           unification variable  X,Y,Z,...
#   ('sus', perm, varname)  suspended permutation  swap(...).X
#   ('bind', atomname, t)   binder  [a].t
#   ('app', sym, (t0,..))   application f(t0,..)
# A permutation is a dict {atom: image} over its support; atoms outside the
# support are fixed.  Composition comp(p1, p2) applies p2 first then p1.
# ---------------------------------------------------------------------------


def sw_atom(perm, a):
    return perm.get(a, a)


def comp(p1, p2):
    keys = set(p1) | set(p2)
    return {a: p1.get(p2.get(a, a), p2.get(a, a)) for a in keys}


def inv(perm):
    return {v: k for k, v in perm.items()}


def perm_apply(perm, t):
    if t[0] == 'at':
        return ('at', sw_atom(perm, t[1]))
    if t[0] == 'var':
        return t
    if t[0] == 'sus':
        return ('sus', comp(perm, t[1]), t[2])
    if t[0] == 'bind':
        return ('bind', sw_atom(perm, t[1]), perm_apply(perm, t[2]))
    return ('app', t[1], tuple(perm_apply(perm, c) for c in t[2]))


def term_vars(t, acc):
    if t[0] == 'var':
        acc.add(t[1])
    elif t[0] == 'sus':
        acc.add(t[2])
    elif t[0] == 'bind':
        term_vars(t[2], acc)
    elif t[0] == 'app':
        for c in t[2]:
            term_vars(c, acc)
    return acc


def occurs(var, t):
    return var in term_vars(t, set())


def free_atoms(t, acc):
    if t[0] == 'at':
        acc.add(t[1])
    elif t[0] == 'bind':
        free_atoms(t[2], acc)
    elif t[0] == 'app':
        for c in t[2]:
            free_atoms(c, acc)
    return acc


def subst_term(t, sigma):
    if t[0] == 'var':
        if t[1] in sigma:
            return subst_term(sigma[t[1]], sigma)
        return t
    if t[0] == 'sus':
        if t[2] in sigma:
            return subst_term(perm_apply(t[1], sigma[t[2]]), sigma)
        return t
    if t[0] == 'bind':
        return ('bind', t[1], subst_term(t[2], sigma))
    if t[0] == 'app':
        return ('app', t[1], tuple(subst_term(c, sigma) for c in t[2]))
    return t


def render(t):
    if t[0] == 'at':
        return t[1]
    if t[0] == 'var':
        return t[1]
    if t[0] == 'sus':
        if not t[1]:
            return t[2]
        swaps = ",".join(sorted(f"{a}<->{b}" for a, b in t[1].items() if a != b))
        return f"swap({swaps}).{t[2]}"
    if t[0] == 'bind':
        return f"[{t[1]}].{render(t[2])}"
    return f"{t[1]}({','.join(render(c) for c in t[2])})"


def perm_nontriv(perm):
    return any(a != b for a, b in perm.items())


# ---------------------------------------------------------------------------
# Nominal unification (Urban--Pitts--Gabbay fragment).
# Returns (sigma, fresh) on success, else None for inconsistency.
#   sigma : {var: term}   principal substitution
#   fresh : set of frozenset({'hf', atom, var}) residual freshness conditions
# ---------------------------------------------------------------------------


def _solve_sus(perm, var, t, sigma, fresh):
    """Solve perm*var == t with var not occurring in t."""
    pinv = inv(perm)
    img = perm_apply(pinv, t)
    if perm_nontriv(perm):
        for a in set(perm):
            if a in free_atoms(img, set()):
                fresh.add((a, var))
    sigma[var] = img
    return ('ok', [])


def _solve_var_at(var, perm, a, sigma, fresh):
    """perm*var == a (atom)."""
    val = sw_atom(inv(perm), a)
    sigma[var] = ('at', val)
    return ('ok', [])


def _binder_binders(a, t, b, u, sigma, fresh):
    """[a].t == [b].u with possibly distinct binders, alpha-renaming."""
    if a == b:
        return ('ok', [(t, u)])
    perm = {a: b, b: a}
    tn = perm_apply(perm, t)
    if a in free_atoms(t, set()):
        return ('fail', None)
    v = _top_var(t)
    if v is not None:
        fresh.add((a, v))
    return ('ok', [(tn, u)])


def _top_var(t):
    if t[0] == 'var':
        return t[1]
    if t[0] == 'sus':
        return t[2]
    return None


def unify_eq(s, t, sigma, fresh):
    if s == t:
        return ('ok', [])
    hs, ht = s[0], t[0]
    if hs == 'at' and ht == 'at':
        return ('fail', None)
    if hs == 'app' and ht == 'app':
        if s[1] != t[1] or len(s[2]) != len(t[2]):
            return ('fail', None)
        return ('ok', list(zip(s[2], t[2])))
    if hs == 'bind' and ht == 'bind':
        return _binder_binders(s[1], s[2], t[1], t[2], sigma, fresh)
    if hs == 'at' and ht == 'sus':
        # a == perm*X
        if occurs(t[2], ('at', s[1])):
            return ('fail', None)
        fresh.add((sw_atom(inv(t[1]), s[1]), t[2]))
        sigma[t[2]] = ('at', sw_atom(inv(t[1]), s[1]))
        return ('ok', [])
    if hs == 'sus' and ht == 'at':
        return _solve_var_at(s[2], s[1], t[1], sigma, fresh)
    if hs == 'sus' and ht == 'at':
        return _solve_var_at(s[2], s[1], t[1], sigma, fresh)
    if hs == 'sus' and ht == 'var':
        # perm*X == Y
        if s[2] == t[1]:
            # X == perm*X: only solvable if perm identity
            if not perm_nontriv(s[1]):
                return ('ok', [])
            return ('fail', None)
        if not perm_nontriv(s[1]):
            sigma[s[2]] = ('var', t[1])
            return ('ok', [])
        sigma[s[2]] = ('sus', s[1], t[1])
        for a in set(s[1]):
            fresh.add((a, t[1]))
        return ('ok', [])
    if hs == 'var' and ht == 'sus':
        return unify_eq(t, s, sigma, fresh)
    if hs == 'sus' and ht in ('app', 'bind'):
        if occurs(s[2], t):
            return ('fail', None)
        return _solve_sus(s[1], s[2], t, sigma, fresh)
    if ht == 'sus' and hs in ('app', 'bind'):
        if occurs(t[2], s):
            return ('fail', None)
        return _solve_sus(t[1], t[2], s, sigma, fresh)
    if hs == 'var' and ht in ('app', 'bind', 'at'):
        if occurs(s[1], t):
            return ('fail', None)
        sigma[s[1]] = t
        return ('ok', [])
    if ht == 'var' and hs in ('app', 'bind', 'at'):
        if occurs(t[1], s):
            return ('fail', None)
        sigma[t[1]] = s
        return ('ok', [])
    return ('fail', None)


def unify(equations):
    sigma = {}
    fresh = set()
    stack = list(equations)
    guard = 0
    while stack and guard < 6000:
        guard += 1
        s, t = stack.pop()
        s = subst_term(s, sigma)
        t = subst_term(t, sigma)
        if s == t:
            continue
        status, extra = unify_eq(s, t, sigma, fresh)
        if status == 'fail':
            return None
        if extra:
            stack.extend(extra)
    return sigma, fresh


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

ATOMS = ['a', 'b', 'c', 'd', 'e']
FUNS = ['f', 'g', 'h']
VNS = ['X', 'Y', 'Z', 'W', 'V', 'U']


def _rand_perm():
    if random.random() < 0.45:
        return {}
    a, b = random.sample(ATOMS, 2)
    return {a: b, b: a}


@dataclass
class NominalEquationConfig(Config):
    depth: int = 2
    var_count: int = 2

    def apply_difficulty(self, level):
        self.depth = 2 + level
        self.var_count = 2 + (level // 2)


class NominalEquationSolving(Task):
    summary = ("Solve equations between nominal terms with atom binders, suspended "
               "permutations, and freshness constraints modulo alpha-equivalence; "
               "return inconsistency or the principal substitution and residual "
               "freshness conditions.")
    config_cls = NominalEquationConfig
    design_choice = ("Generate two nominal terms sharing unification variables and "
                     "permuted suspensions, run nominal unification, and answer with "
                     "the resulting principal substitution and residual freshness "
                     "conditions, or 'inconsistent' when no unifier exists.")

    def generate_entry(self):
        while True:
            res = self._attempt()
            if res is not None:
                kind, left, right, ans = res
                break
        meta = {'kind': kind, 'left': left, 'right': right}
        return Entry(metadata=meta, answer=ans)

    def _attempt(self):
        cfg = self.config
        make_inc = random.random() < 0.3
        if make_inc:
            return self._mk_inconsistent(cfg)
        return self._mk_consistent(cfg)

    def _mk_consistent(self, cfg):
        var_pool = random.sample(VNS, max(2, cfg.var_count))
        used = set(var_pool)
        solver = next(v for v in VNS if v not in used)
        body = self._mk_term(cfg.depth, var_pool)
        # guaranteed to unify:  solver*perm == body
        if random.random() < 0.5:
            left = ('var', solver)
        else:
            left = ('sus', _rand_perm(), solver)
        r = unify([(left, body)])
        if r is None:
            return None
        sigma, fresh = r
        ans = self._answer_string(sigma, fresh)
        return ('solvable', render(left), render(body), ans)

    def _mk_inconsistent(self, cfg):
        var_pool = random.sample(VNS, max(2, cfg.var_count))
        depth = cfg.depth
        sym = random.choice(FUNS)
        # same symbol, different arity -> deterministically inconsistent
        if random.random() < 0.5:
            left = ('app', sym, (self._mk_term(depth, var_pool),))
            right = ('app', sym, (self._mk_term(depth, var_pool),
                                  self._mk_term(depth, var_pool)))
        else:
            left = ('bind', random.choice(ATOMS), self._mk_term(depth, var_pool))
            right = ('at', random.choice(ATOMS))
        r = unify([(left, right)])
        if r is not None:
            return None
        return ('inconsistent', render(left), render(right), 'inconsistent')

    def _mk_term(self, depth, var_pool):
        if depth <= 0:
            k = random.random()
            if k < 0.3:
                return ('at', random.choice(ATOMS))
            if k < 0.7:
                return ('var', random.choice(var_pool))
            return ('sus', _rand_perm(), random.choice(var_pool))
        k = random.random()
        if k < 0.28:
            return ('at', random.choice(ATOMS))
        if k < 0.48:
            return ('var', random.choice(var_pool))
        if k < 0.66:
            return ('sus', _rand_perm(), random.choice(var_pool))
        if k < 0.84:
            return ('bind', random.choice(ATOMS), self._mk_term(depth - 1, var_pool))
        return ('app', random.choice(FUNS),
                tuple(self._mk_term(depth - 1, var_pool)
                      for _ in range(random.randint(1, 2))))

    def _answer_string(self, sigma, fresh):
        sigma_items = sorted((k, render(v)) for k, v in sigma.items())
        sigma_str = ", ".join(f"{k} = {v}" for k, v in sigma_items)
        fresh_pairs = sorted(fresh, key=lambda p: (p[1], p[0]))
        fresh_str = ", ".join(f"{a} # {v}" for a, v in fresh_pairs)
        if not fresh_str:
            fresh_str = "none"
        return f"subst{{{sigma_str}}}; fresh{{{fresh_str}}}"

    def render_prompt(self, metadata):
        return (f"In nominal syntax: a..e are atom constants, X..Z unification "
                f"variables, swap(a<->b).X a suspended permutation, [a].t a binder "
                f"where the binder atom is alpha-renamable, and f(t) an "
                f"application. Two terms are equated modulo alpha-equivalence of "
                f"their binders. Solve the nominal equation:\n"
                f"  {metadata['left']}  ==  {metadata['right']}\n"
                f"If the equation has no unifier (is inconsistent), answer the single "
                f"word  inconsistent.\n"
                f"Otherwise give the principal substitution and the residual "
                f"freshness conditions in exactly this format:\n"
                f"  subst{{X = t, ...}}; fresh{{a # X, ...}}\n"
                f"use  fresh{{none}}  when there are no residual freshness "
                f"conditions. Write only that one line.")

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == entry.answer else 0.0

"""SLD resolution over Horn-clause programs.

Given a definite-clause program and a goal, compute the ordered sequence of
answer substitutions produced by SLD resolution with renaming-apart,
occurs-check unification, and left-to-right, depth-first backtracking through
clause order. The answer is the ordered substitutions (each a substitution
over the goal's answer variables), written in a canonical sorted variable
order. If no derivation succeeds, the answer is exactly "fail".
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'sld_resolution_substitutions (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scope_and_binding_r1/sld_resolution_substitutions',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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

VARIABLES = "UVWXYZ"
CONSTANTS = ["a", "b", "c", "d", "e", "f", "g", "h"]


def _term_vars(term):
    out = set()
    if isinstance(term, str):
        if term in VARIABLES:
            out.add(term)
        return out
    for t in term:
        out |= _term_vars(t)
    return out


def _atom_vars(atom):
    out = set()
    for t in atom[1:]:
        out |= _term_vars(t)
    return out


def _subst_term(term, sigma):
    if isinstance(term, str):
        if term in VARIABLES and term in sigma:
            val = sigma[term]
            if val == term:
                return term
            return _subst_term(val, sigma)
        return term
    return tuple(_subst_term(t, sigma) for t in term)


def _term_str(t):
    if isinstance(t, str):
        return t
    return t[0] + "(" + ",".join(_term_str(x) for x in t[1:]) + ")"


def _atom_str(atom):
    return atom[0] + "(" + ",".join(_term_str(t) for t in atom[1:]) + ")"


class _UnifError(Exception):
    pass


_trail = []


def _unify(t1, t2, env):
    while isinstance(t1, str) and t1 in VARIABLES and t1 in env:
        t1 = env[t1]
    while isinstance(t2, str) and t2 in VARIABLES and t2 in env:
        t2 = env[t2]
    if isinstance(t1, str) and t1 in VARIABLES:
        if isinstance(t2, str) and t2 in VARIABLES and t2 not in env:
            if t1 == t2:
                return
            _trail.append(t1)
            env[t1] = t2
            return
        if _occurs(t1, t2):
            raise _UnifError
        _trail.append(t1)
        env[t1] = t2
        return
    if isinstance(t2, str) and t2 in VARIABLES:
        if _occurs(t2, t1):
            raise _UnifError
        _trail.append(t2)
        env[t2] = t1
        return
    if isinstance(t1, str) or isinstance(t2, str):
        if t1 == t2:
            return
        raise _UnifError
    if len(t1) != len(t2):
        raise _UnifError
    for a, b in zip(t1, t2):
        _unify(a, b, env)


def _occurs(var, term):
    if isinstance(term, str):
        return term == var
    return any(_occurs(var, t) for t in term)


def _mark():
    return len(_trail)


def _undo(mark, env):
    while len(_trail) > mark:
        var = _trail.pop()
        env.pop(var, None)


def _rename_apart(atom, ren):
    def rt(t):
        if isinstance(t, str):
            if t in VARIABLES and t in ren:
                return t + "_" + str(ren[t])
            return t
        return tuple(rt(x) for x in t)
    return (atom[0],) + tuple(rt(t) for t in atom[1:])


def _solve(clauses, goal, answer_vars, max_answers, max_depth):
    _trail.clear()
    answers = []
    done = False

    def dfs(goals, env, depth):
        nonlocal done
        if done:
            return
        if len(answers) >= max_answers:
            done = True
            return
        if depth > max_depth:
            return
        if not goals:
            sub = {}
            for v in answer_vars:
                t = env.get(v, v)
                d = _subst_term(t, env)
                sub[v] = None if (isinstance(d, str) and d in VARIABLES) else d
            answers.append(sub)
            return
        cur = goals[0]
        rest = goals[1:]
        for ci, (head, body) in enumerate(clauses):
            ren = {}
            for k, v in enumerate(sorted(_atom_vars(head))):
                ren[v] = ci * 100000 + depth * 1000 + k
            head_r = _rename_apart(head, ren)
            mark = _mark()
            try:
                _unify(cur, head_r, env)
            except _UnifError:
                _undo(mark, env)
                continue
            bodyr = []
            for b in body:
                rn = {}
                for k, v in enumerate(sorted(_atom_vars(b))):
                    rn[v] = ci * 100000 + depth * 1000 + 500 + k
                bodyr.append(_rename_apart(b, rn))
            dfs(bodyr + rest, env, depth + 1)
            _undo(mark, env)
            if done:
                return

    dfs(goal, {}, 0)
    return answers


def _answer_str(answer_vars, sub):
    parts = []
    for v in answer_vars:
        if v in sub and sub[v] is not None:
            parts.append(f"{v}={_term_str(sub[v])}")
        else:
            parts.append(f"{v}=unbound")
    return "{ " + ", ".join(parts) + " }"


def _program_str(clauses):
    lines = []
    for head, body in clauses:
        if body:
            rhs = ", ".join(_atom_str(b) for b in body)
            lines.append(f"{_atom_str(head)} :- {rhs}.")
        else:
            lines.append(f"{_atom_str(head)}.")
    return "\n".join(lines)


@dataclass
class SLDConfig(Config):
    n_clauses: int = 2
    max_answers: int = 2
    max_depth: int = 4

    def apply_difficulty(self, level):
        self.n_clauses = stochastic_rounding(self.n_clauses + level)
        self.max_answers = stochastic_rounding(self.max_answers + level // 2)
        self.max_depth = stochastic_rounding(self.max_depth + level)


def _gen_term(depth, varpool):
    if depth <= 0:
        return random.choice(CONSTANTS)
    k = random.randint(0, 3)
    if k == 0:
        return random.choice(varpool)
    if k == 1:
        return random.choice(CONSTANTS)
    name = random.choice(["f", "g", "h"])
    n = random.randint(1, 2)
    args = tuple(_gen_term(depth - 1, varpool) for _ in range(n))
    return (name,) + args


class SLDResolution(Task):
    summary = ("Execute SLD resolution over Horn-clause programs with "
               "renaming-apart, occurs-check unification, and depth-first "
               "backtracking through clause order; answers are the ordered "
               "answer substitutions or the first failing goal.")
    config_cls = SLDConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(60):
            entry = self._try_generate(cfg)
            if entry is not None:
                return entry
        raise RuntimeError("could not generate valid SLD instance")

    def _try_generate(self, cfg):
        varpool = list(VARIABLES[:3])
        n_goal_vars = random.choice([1, 1, 2])
        goal_vars = random.sample(varpool, n_goal_vars)
        pred = random.choice(["p", "q"])
        goal = (pred,) + tuple(goal_vars)

        clauses = []
        fact_consts = random.sample(CONSTANTS, 3)
        clauses.append(((pred, fact_consts[0]), []))
        clauses.append(((pred, fact_consts[1]), []))

        if cfg.n_clauses >= 3:
            aux = random.choice(["r", "s"])
            clauses.append(((pred, "V"), [(aux, "V")]))
            clauses.append(((aux, fact_consts[2]), []))
        if cfg.n_clauses >= 5:
            clauses.append(((pred, "W"), [(aux, "W"), (pred, "W")]))

        final_clauses = clauses[: cfg.n_clauses]

        answers = _solve(final_clauses, [goal], goal_vars, cfg.max_answers, cfg.max_depth)
        if not answers:
            return None
        # require not all answers identical (give structural variety)
        unique = {repr(a) for a in answers}
        if len(unique) < 2 and n_goal_vars == 1:
            # for single var require at least 2 distinct answers when possible
            if len(answers) < 2:
                return None

        answer_str = " ; ".join(_answer_str(goal_vars, a) for a in answers)
        return Entry(
            metadata={
                "program": _program_str(final_clauses),
                "goal": _atom_str(goal),
                "goal_vars": goal_vars,
                "answers": [{k: (None if v is None else _term_str(v)) for k, v in a.items()}
                            for a in answers],
            },
            answer=answer_str,
        )

    def render_prompt(self, metadata):
        return (
            "Consider this definite-clause (Horn) logic program:\n"
            f"{metadata['program']}\n"
            f"Goal: {metadata['goal']}\n"
            "Using SLD resolution -- renaming variables apart before each clause "
            "use, occurs-check unification, selecting the leftmost goal, and "
            "depth-first backtracking through clause order as written -- compute the "
            "ordered answer substitutions for the goal variable(s). "
            "Write them in the order found, separated by ' ; '. Each substitution "
            "has the form: { X=c, Y=unbound }, where an unbounded goal variable is "
            "shown as 'unbound'. If no derivation succeeds, answer exactly: fail"
        )

    def score_answer(self, answer, entry):
        return 1.0 if (answer or "").strip() == entry.answer else 0.0

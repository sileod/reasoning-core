import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict

TASK_META = {'parent_source_id': None,
 'idea': 'sequent_proof_search (variant 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_global_from_local_r4/sequent_proof_search',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

ATOMS = 'pqrstuvwxyzabcdefghijklmno'

design_choice = "Use only single-conclusion sequents and answer with an integer leaf count, where leaves are counted after exhaustive invertible and disjunctive branching."


@dataclass
class SequentProofConfig(Config):
    tmax: int = 3
    enrich_frac: float = 0.15
    use_rs_or: float = 0.0

    def apply_difficulty(self, level):
        self.tmax = 3 + level
        self.enrich_frac = round(0.12 + 0.06 * level, 3)
        self.use_rs_or = 0.0 if level < 2 else 0.25


def _mk_atom():
    return ('atom', random.choice(ATOMS))


def _mk_formula(depth):
    if depth <= 0 or random.random() < 0.35:
        return _mk_atom()
    if random.random() < 0.5:
        return ('and', _mk_formula(depth - 1), _mk_formula(depth - 1))
    return ('or', _mk_formula(depth - 1), _mk_formula(depth - 1))


def _render(f):
    if f[0] == 'atom':
        return f[1]
    return f"({_render(f[1])} {f[0]} {_render(f[2])})"


def _build_rs(t, pool):
    if t == 1:
        return ('atom', random.choice(pool))
    a = random.randint(1, t - 1)
    return ('and', _build_rs(a, pool), _build_rs(t - a, pool))


def _collect_atoms(x, out):
    if x[0] == 'atom':
        out.append(x[1])
        return
    _collect_atoms(x[1], out)
    _collect_atoms(x[2], out)


def _leaf_count(ctx, rs):
    kind = rs[0]
    if kind == 'atom':
        name = rs[1]
        if any(c[0] == 'atom' and c[1] == name for c in ctx):
            return 1
        for i in range(len(ctx)):
            f = ctx[i]
            if f[0] == 'and':
                return _leaf_count(ctx[:i] + [f[1], f[2]] + ctx[i + 1:], rs)
            if f[0] == 'or':
                l = _leaf_count(ctx[:i] + [f[1]] + ctx[i + 1:], rs)
                if l is None:
                    return None
                r = _leaf_count(ctx[:i] + [f[2]] + ctx[i + 1:], rs)
                if r is None:
                    return None
                return l + r
        return None
    if kind == 'and':
        l = _leaf_count(ctx, rs[1])
        if l is None:
            return None
        r = _leaf_count(ctx, rs[2])
        if r is None:
            return None
        return l + r
    if kind == 'or':
        return _leaf_count(ctx, rs[1])
    raise ValueError


def _parse_int(s):
    try:
        return int(str(s).strip())
    except (TypeError, ValueError):
        return None


class SequentProofSearch(Task):
    summary = ("Search a single-conclusion propositional sequent calculus (atoms, and, or of a "
               "fully parenthesized ordered sequent Gamma |- A), applying invertible right/left "
               "rules freely and branching on disjunctive and/or rules, and answer the integer "
               "leaf count of the deterministic finished derivation tree.")
    config_cls = SequentProofConfig
    design_choice = design_choice

    def generate_entry(self):
        cfg = self.config
        pool = list(ATOMS[:4 + cfg.tmax])
        while True:
            t = random.randint(1, cfg.tmax)
            rs = _build_rs(t, pool)
            if cfg.use_rs_or > 0.0 and random.random() < cfg.use_rs_or:
                rs = ('or', rs, _mk_formula(1))
            leaves = []
            _collect_atoms(rs, leaves)
            ctx = []
            for g in leaves:
                if random.random() < cfg.enrich_frac:
                    x = random.choice(pool)
                    ctx.append(('or', ('atom', g), ('and', ('atom', g), ('atom', x))))
                else:
                    ctx.append(('atom', g))
            random.shuffle(ctx)
            cnt = _leaf_count(ctx, rs)
            if cnt is not None and cnt >= 1:
                break
        assert _leaf_count(ctx, rs) == cnt
        ctx_str = [_render(c) for c in ctx]
        answer = str(cnt)
        metadata = edict({
            'ctx': ctx_str,
            'rs': _render(rs),
            'leaf_count': cnt,
            '_t': t,
        })
        metadata.payload = {
            'ctx': ctx_str,
            'rs': _render(rs),
        }
        metadata['_answer'] = answer
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return (
            "We work with single-conclusion propositional sequents Gamma |- A, where Gamma is the "
            "ordered left side (a comma-separated list of formulas) and A is the single formula on "
            "the right. Formulas are built from atoms and the connectives and / or, each fully "
            "parenthesized: (X and Y) is the conjunction and (X or Y) the disjunction of X and Y "
            "with X on the left and Y on the right.\n\n"
            "A finished derivation tree is built from a sequent by this deterministic procedure, "
            "reapplied until no rule applies; we want the number of leaves of that tree.\n\n"
            "For a right conjunction A = (X and Y): split into two children Gamma |- X and "
            "Gamma |- Y (both premises are followed).\n"
            "For a right disjunction A = (X or Y): follow only the first premise Gamma |- X (the "
            "right disjunction keeps the first disjunct).\n"
            "If A is an atom p and p is listed in Gamma: this is an axiom leaf; it contributes "
            "exactly one leaf and nothing more is done.\n"
            "Otherwise A is an atom p not present in Gamma: scan Gamma from left to right and, at "
            "the first formula that is a conjunction or disjunction, apply a left rule, then start "
            "again from the left. For a conjunct (X and Y) replace it in place by the two formulas "
            "X, Y (one premise). For a disjunct (X or Y) branch into two children: one with that "
            "formula replaced in place by X, and one with it replaced in place by Y (two premises, "
            "both counted).\n\n"
            f"Sequent: {', '.join(metadata.ctx)} |- {metadata.rs}\n"
            "Count every axiom leaf of the finished tree. The answer is the integer leaf count."
        )

    def score_answer(self, answer, entry):
        got = _parse_int(answer)
        if got is None:
            return 0.0
        return 1.0 if got == entry.metadata.leaf_count else 0.0

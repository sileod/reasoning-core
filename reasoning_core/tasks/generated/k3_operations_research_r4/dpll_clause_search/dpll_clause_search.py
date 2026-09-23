import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'dpll_clause_search (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_operations_research_r4/dpll_clause_search',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 4238614268,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class DPLLClauseSearchConfig(Config):
    num_vars: int = 3
    num_clauses: int = 3
    max_len: int = 2

    def apply_difficulty(self, level):
        self.num_vars = 3 + level
        self.num_clauses = 3 + 2 * level
        self.max_len = 3 if level >= 3 else 2


_VERDICT_SEEN = {}


def _vars(clauses):
    return {abs(l) for c in clauses for l in c}


def _find_pure(clauses, assign):
    for v in sorted(_vars(clauses)):
        if v in assign:
            continue
        pos = any(v in c for c in clauses)
        neg = any(-v in c for c in clauses)
        if pos and not neg:
            return v
        if neg and not pos:
            return -v
    return None


def _propagate(clauses, assign):
    for clause in clauses:
        falsified = True
        un = []
        for lit in clause:
            v = abs(lit)
            if v in assign:
                if assign[v] == (lit > 0):
                    falsified = False
                    break
            else:
                falsified = False
                un.append(lit)
        else:
            if falsified:
                return clause, None
            if len(un) == 1:
                return None, un[0]
    return None, None


def _all_satisfied(clauses, assign):
    return all(
        any(abs(l) in assign and assign[abs(l)] == (l > 0) for l in c)
        for c in clauses
    )


def _complete(clauses, assign):
    for v in sorted(_vars(clauses)):
        assign.setdefault(v, False)


def _dpll_search(clauses, assign, decisions, first_conflict):
    while True:
        conflict, unit = _propagate(clauses, assign)
        if conflict is not None:
            if first_conflict[0] is None:
                first_conflict[0] = tuple(sorted(conflict, key=abs))
            return False
        if unit is not None:
            assign[abs(unit)] = unit > 0
            continue
        pure = _find_pure(clauses, assign)
        if pure is not None:
            assign[abs(pure)] = pure > 0
            continue
        break
    if _all_satisfied(clauses, assign):
        _complete(clauses, assign)
        return True
    unassigned = sorted(v for v in _vars(clauses) if v not in assign)
    var = unassigned[0]
    decisions.append((var, False))
    a2 = dict(assign)
    a2[var] = True
    if _dpll_search(clauses, a2, decisions, first_conflict):
        assign.update(a2)
        return True
    decisions.append((var, True))
    a3 = dict(assign)
    a3[var] = False
    if _dpll_search(clauses, a3, decisions, first_conflict):
        assign.update(a3)
        return True
    return False


def _run(clauses):
    first_conflict = [None]
    decisions = []
    assign = {}
    sat = _dpll_search(clauses, assign, decisions, first_conflict)
    return sat, assign, decisions, first_conflict[0]


def _make_cnf(cfg):
    nvars = cfg.num_vars
    clauses = []
    for _ in range(cfg.num_clauses):
        nlen = random.randint(2, cfg.max_len)
        vs = random.sample(range(1, nvars + 1), min(nlen, nvars))
        seen = set()
        clause = []
        for v in vs:
            if v in seen:
                continue
            seen.add(v)
            clause.append(v if random.random() < 0.5 else -v)
        if clause:
            clauses.append(tuple(sorted(clause, key=abs)))
    used = {abs(l) for c in clauses for l in c}
    missing = [v for v in range(1, nvars + 1) if v not in used]
    for v in missing:
        inserted = False
        for _ in range(30):
            ci = random.randrange(len(clauses))
            cl = list(clauses[ci])
            if not any(abs(l) == v for l in cl):
                cl.append(v if random.random() < 0.5 else -v)
                cl.sort(key=abs)
                clauses[ci] = tuple(cl)
                inserted = True
                break
        if not inserted and clauses:
            clauses.append((v if random.random() < 0.5 else -v,))
    return [c for c in clauses if c]


def _render_lit(l):
    return ("~x" + str(abs(l))) if l < 0 else ("x" + str(abs(l)))


def _render_clauses(clauses):
    return "; ".join("(" + " or ".join(_render_lit(l) for l in c) + ")" for c in clauses)


def _fmt_assignment(assign):
    return ",".join(f"x{v}={'T' if assign[v] else 'F'}" for v in sorted(assign))


def _fmt_decisions(decisions):
    return ",".join(("~x" if neg else "x") + str(v) for v, neg in decisions)


def _fmt_conflict(conflict):
    return ",".join(("~x" if l < 0 else "x") + str(abs(l)) for l in conflict)


def _make_unsat_cnf(cfg):
    n = cfg.num_vars
    clauses = [list(c) for c in _make_cnf(cfg)]
    d = random.randint(1, n)
    c = random.choice([v for v in range(1, n + 1) if v != d])
    ld = d if random.random() < 0.5 else -d
    lc = c if random.random() < 0.5 else -c
    clauses.append([ld])
    clauses.append([-ld, lc])
    clauses.append([-ld, -lc])
    random.shuffle(clauses)
    return [tuple(sorted(cl, key=abs)) for cl in clauses]


def _make_sat_cnf(cfg):
    while True:
        c = _make_cnf(cfg)
        s, _, _, _ = _run(c)
        if s:
            return c


def _gen_verdict(cfg):
    seen = _VERDICT_SEEN.setdefault(cfg.level, [0, 0])
    total = seen[0] + seen[1]
    target = 0 if (total == 0 or seen[0] <= seen[1]) else 1
    if target == 0:
        cl = _make_sat_cnf(cfg)
    else:
        cl = _make_unsat_cnf(cfg)
    seen[target] += 1
    label = "SAT" if target == 0 else "UNSAT"
    md = {"mode": "verdict", "clauses": cl, "nvar": cfg.num_vars, "label": label}
    return Entry(metadata=md, answer=label)


def _gen_assignment(cfg):
    c = _make_sat_cnf(cfg)
    s, assign, _, _ = _run(c)
    ans = _fmt_assignment(assign)
    md = {
        "mode": "assignment",
        "clauses": c,
        "nvar": cfg.num_vars,
        "assignment": [[v, True if assign[v] else False] for v in sorted(assign)],
        "answer": ans,
    }
    return Entry(metadata=md, answer=ans)


def _gen_decision(cfg):
    for _ in range(400):
        c = _make_sat_cnf(cfg)
        s, _, decisions, _ = _run(c)
        if decisions:
            ans = _fmt_decisions(decisions)
            md = {
                "mode": "decision",
                "clauses": c,
                "nvar": cfg.num_vars,
                "decisions": [[v, 1 if neg else 0] for v, neg in decisions],
                "answer": ans,
            }
            return Entry(metadata=md, answer=ans)
    raise RuntimeError("dpll decision generation failed")


def _gen_conflict(cfg):
    c = _make_unsat_cnf(cfg)
    s, _, _, first = _run(c)
    if not s and first is not None:
        ans = _fmt_conflict(first)
        md = {
            "mode": "conflict",
            "clauses": c,
            "nvar": cfg.num_vars,
            "conflict": list(first),
            "answer": ans,
        }
        return Entry(metadata=md, answer=ans)
    c = [(1,), (-1,)]
    s, _, _, first = _run(c)
    ans = _fmt_conflict(first)
    md = {
        "mode": "conflict",
        "clauses": [(1,), (-1,)],
        "nvar": 1,
        "conflict": list(first),
        "answer": ans,
    }
    return Entry(metadata=md, answer=ans)


def _parse_lit(tok):
    m = re.fullmatch(r"\s*(~?)x(\d+)\s*", tok)
    if not m:
        return None
    return (int(m.group(2)), m.group(1) == "~")


def _parse_assignment(answer):
    if not isinstance(answer, str):
        return None
    d = {}
    for tok in answer.split(","):
        m = re.fullmatch(r"\s*x(\d+)\s*=\s*([TF])\s*", tok)
        if not m:
            return None
        d[int(m.group(1))] = m.group(2) == "T"
    return d


def _parse_decision(answer):
    if not isinstance(answer, str):
        return None
    out = []
    if answer.strip() == "":
        return None
    for tok in answer.split(","):
        lit = _parse_lit(tok)
        if lit is None:
            return None
        out.append(lit)
    return out


def _parse_conflict(answer):
    if not isinstance(answer, str):
        return None
    out = set()
    for tok in answer.split(","):
        lit = _parse_lit(tok)
        if lit is None:
            return None
        out.add(lit)
    return out


class DpllClauseSearch(Task):
    summary = "Drive DPLL over small CNF instances: propagate unit clauses, collapse pure literals, branch with backtracking; answer a satisfying assignment, the literals in decision order, an UNSAT verdict, or the first conflicting clause."
    config_cls = DPLLClauseSearchConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        mode = random.choice(("verdict", "assignment", "decision", "conflict"))
        if mode == "verdict":
            return _gen_verdict(cfg)
        if mode == "assignment":
            return _gen_assignment(cfg)
        if mode == "decision":
            return _gen_decision(cfg)
        return _gen_conflict(cfg)

    def render_prompt(self, metadata):
        mode = metadata["mode"]
        vline = f"The variables are x1 through x{metadata['nvar']}."
        cnf = f"The CNF formula is:\n{_render_clauses(metadata['clauses'])}"
        rule = ("Run the DPLL algorithm: repeatedly propagate unit clauses, eliminate pure "
                "literals, and branch on the lowest-index unassigned variable, trying true "
                "before false and backtracking on conflict.")
        if mode == "verdict":
            q = "Decide whether the formula is satisfiable. Answer exactly SAT or UNSAT."
        elif mode == "assignment":
            q = ("The formula is satisfiable. Report the satisfying assignment DPLL produces in "
                 "increasing variable order, as a comma-separated list where each variable is "
                 "x<k>=T or x<k>=F, e.g. 'x1=T,x2=F,x3=T'. A variable not fixed by the search is "
                 "set false.")
        elif mode == "decision":
            q = ("List the literals chosen as branch decisions during the search, in the order "
                 "made (including a backtracked attempt), comma-separated: 'x2' means set x2 "
                 "true and '~x1' means set x1 false, e.g. 'x2,~x1,x3'. Exclude unit-propagation "
                 "and pure-literal assignments.")
        else:
            q = ("The formula is unsatisfiable. Report the first clause that becomes false "
                 "during the search, the conflicting clause, as its literals sorted by variable "
                 "index and comma-separated like '~x1,x3'.")
        return f"{vline}\n{cnf}\n{rule}\n{q}"

    def score_answer(self, answer, entry):
        md = getattr(entry, "metadata", None)
        if md is None:
            try:
                md = entry["metadata"]
            except Exception:
                return 0.0
        mode = md.get("mode")
        if mode == "verdict":
            return float(isinstance(answer, str) and answer.strip().upper() == md["label"])
        if mode == "assignment":
            parsed = _parse_assignment(answer)
            if parsed is None:
                return 0.0
            gold = {v: bool(b) for v, b in md["assignment"]}
            return float(parsed == gold)
        if mode == "decision":
            parsed = _parse_decision(answer)
            if parsed is None:
                return 0.0
            gold = [(v, neg == 1) for v, neg in md["decisions"]]
            return float(parsed == gold)
        if mode == "conflict":
            parsed = _parse_conflict(answer)
            if parsed is None:
                return 0.0
            gold = {(abs(l), l < 0) for l in md["conflict"]}
            return float(parsed == gold)
        return 0.0

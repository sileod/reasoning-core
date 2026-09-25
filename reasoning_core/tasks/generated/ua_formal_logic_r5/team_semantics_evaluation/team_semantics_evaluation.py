import random
import itertools
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

VARNAMES = ["a", "b", "c", "d", "e", "f", "g", "h"]


# ---------------------------------------------------------------------------
# Shared team-semantics helpers. All are module-level so score_answer can call
# none of them and generation stays deterministic under the module RNG.
# ---------------------------------------------------------------------------

def _dedup(rows):
    """Return distinct rows (rows are dicts var->val) preserving a stable order."""
    seen = set()
    out = []
    for r in rows:
        t = tuple(sorted(r.items()))
        if t not in seen:
            seen.add(t)
            out.append(dict(r))
    return out


def _rt(r, names):
    return tuple(r[n] for n in names)


def _sat_dep(rows, xl, yl):
    rows = _dedup(rows)
    for r1 in rows:
        for r2 in rows:
            if all(r1[k] == r2[k] for k in xl) and any(r1[k] != r2[k] for k in yl):
                return False
    return True


def _sat_incl(rows, xl, yl):
    rows = _dedup(rows)
    vals_x = {_rt(r, xl) for r in rows}
    return all(_rt(r, yl) in vals_x for r in rows)


def _sat_ind(rows, xl, yl):
    rows = _dedup(rows)
    xv = {_rt(r, xl) for r in rows}
    yv = {_rt(r, yl) for r in rows}
    pairs = {(_rt(r, xl), _rt(r, yl)) for r in rows}
    return pairs == {(x, y) for x in xv for y in yv}


def _sat_literal(rows, kind, u, w):
    rows = _dedup(rows)
    if kind == "eq":
        return all(r[u] == r[w] for r in rows)
    return all(r[u] != r[w] for r in rows)


def _sat_split(rows, phi, psi, strict):
    rows = _dedup(rows)
    n = len(rows)
    for lmask in range(1, 1 << n):
        L = [rows[i] for i in range(n) if (lmask >> i) & 1]
        if not L or not _sat_literal(L, phi["kind"], phi["u"], phi["w"]):
            continue
        if strict:
            rmask = ((1 << n) - 1) ^ lmask
            if rmask == 0:
                continue
            R = [rows[i] for i in range(n) if (rmask >> i) & 1]
            if _sat_literal(R, psi["kind"], psi["u"], psi["w"]):
                return True
        else:
            for rmask in range(1, 1 << n):
                R = [rows[i] for i in range(n) if (rmask >> i) & 1]
                if not R:
                    continue
                if _sat_literal(R, psi["kind"], psi["u"], psi["w"]) and all(
                    ((lmask >> i) & 1) or ((rmask >> i) & 1) for i in range(n)
                ):
                    return True
    return False


def _sat_exists(rows, inner, x, dom, strict):
    rows = _dedup(rows)
    if not rows:
        return True
    n = len(rows)

    def test(Xrows, lit):
        return _sat_literal(Xrows, lit["kind"], lit["u"], lit["w"])

    if strict:
        for combo in itertools.product(range(dom), repeat=n):
            X = []
            for row, xv in zip(rows, combo):
                r = dict(row)
                r[x] = xv
                X.append(r)
            if test(_dedup(X), inner):
                return True
        return False
    subsets = [s for m in range(1, dom + 1) for s in itertools.combinations(range(dom), m)]
    for combo in itertools.product(subsets, repeat=n):
        Xset = set()
        for row, xs in zip(rows, combo):
            for xv in xs:
                r = dict(row)
                r[x] = xv
                Xset.add(tuple(sorted(r.items())))
        if test([dict(t) for t in Xset], inner):
            return True
    return False


def _fmt_literal(lit):
    op = "=" if lit["kind"] == "eq" else "!="
    return f"({lit['u']}{op}{lit['w']})"


# ---------------------------------------------------------------------------
# Constructors: each takes the config and a target label ('T'/'F' for yes/no)
# and returns (metadata, holds) after verifying the construction, or None if
# the search fails (rare). Construction is target-driven so labels balance and
# the answer is always independently verified against the brute-force solver.
# ---------------------------------------------------------------------------

def _construct_dep(cfg, target):
    dom = cfg.dom
    for _ in range(80):
        nv = random.randint(2, cfg.max_vars)
        space = VARNAMES[:nv]
        k = random.randint(1, min(2, nv - 1))
        xl = random.sample(space, k)
        rem = [v for v in space if v not in xl]
        y = random.choice(rem)
        size = random.randint(1, cfg.max_team)
        if target:
            rows = []
            for _r in range(size):
                row = {v: random.randrange(dom) for v in space}
                row[y] = sum(row[v] for v in xl) % dom
                rows.append(row)
            rows = _dedup(rows)
            if rows and _sat_dep(rows, xl, [y]):
                meta = {"mode": "dep", "team": rows, "xl": xl, "y": y, "dom": dom}
                return meta, True
        else:
            xval = {v: random.randrange(dom) for v in xl}
            y1 = random.randrange(dom)
            y2 = (y1 + 1 + random.randrange(dom - 1)) % dom

            def mk(yv):
                row = {v: random.randrange(dom) for v in space}
                for v in xl:
                    row[v] = xval[v]
                row[y] = yv
                return row

            rows = [mk(y1), mk(y2)]
            while len(rows) < size:
                row = {v: random.randrange(dom) for v in space}
                rows.append(row)
            rows = _dedup(rows)
            if len(rows) >= 2 and not _sat_dep(rows, xl, [y]):
                meta = {"mode": "dep", "team": rows, "xl": xl, "y": y, "dom": dom}
                return meta, False
    return None


def _construct_incl(cfg, target):
    dom = cfg.dom
    for _ in range(80):
        nv = random.randint(2, cfg.max_vars)
        space = VARNAMES[:nv]
        cnt = random.randint(1, min(2, nv - 1))
        xl = random.sample(space, cnt)
        rem = [v for v in space if v not in xl]
        ycnt = random.randint(1, min(2, len(rem)))
        yl = random.sample(rem, ycnt)
        size = random.randint(1, cfg.max_team)
        rows = [{v: random.randrange(dom) for v in space} for _ in range(size)]
        if target:
            yseen = []
            for r in rows:
                t = _rt(r, yl)
                if t not in yseen:
                    yseen.append(t)
            for t in yseen:
                row = {v: random.randrange(dom) for v in space}
                for v, val in zip(xl, t):
                    row[v] = val
                rows.append(row)
            rows = _dedup(rows)
            if rows and _sat_incl(rows, xl, yl):
                meta = {"mode": "incl", "team": rows, "xl": xl, "yl": yl, "dom": dom}
                return meta, True
        else:
            xset = {_rt(r, xl) for r in rows}
            fresh = None
            for _a in range(60):
                t = tuple(random.randrange(dom) for _ in yl)
                if t not in xset:
                    fresh = t
                    break
            if fresh is None:
                continue
            row = {v: random.randrange(dom) for v in space}
            for v, val in zip(yl, fresh):
                row[v] = val
            rows.append(row)
            rows = _dedup(rows)
            if rows and not _sat_incl(rows, xl, yl):
                meta = {"mode": "incl", "team": rows, "xl": xl, "yl": yl, "dom": dom}
                return meta, False
    return None


def _construct_ind(cfg, target):
    dom = cfg.dom
    for _ in range(80):
        nv = random.randint(2, cfg.max_vars)
        space = VARNAMES[:nv]
        try:
            xcnt = random.randint(1, min(2, nv - 1))
            xl = random.sample(space, xcnt)
            rem = [v for v in space if v not in xl]
            ycnt = random.randint(1, min(2, len(rem)))
            yl = random.sample(rem, ycnt)
        except ValueError:
            continue
        others = [v for v in space if v not in xl and v not in yl]
        A = list({tuple(random.randrange(dom) for _ in xl) for _ in range(10)})
        B = list({tuple(random.randrange(dom) for _ in yl) for _ in range(10)})
        if len(A) < 2 or len(B) < 2:
            continue
        A = sorted(A[:2])
        B = sorted(B[:2])
        if target:
            rows = []
            for a in A:
                for b in B:
                    row = {v: random.randrange(dom) for v in others}
                    row.update({v: av for v, av in zip(xl, a)})
                    row.update({v: bv for v, bv in zip(yl, b)})
                    rows.append(row)
            rows = _dedup(rows)
            if _sat_ind(rows, xl, yl):
                meta = {"mode": "ind", "team": rows, "xl": xl, "yl": yl, "dom": dom}
                return meta, True
        else:
            rows = []
            for i, a in enumerate(A):
                for j, b in enumerate(B):
                    if i == len(A) - 1 and j == 0:
                        continue
                    row = {v: random.randrange(dom) for v in others}
                    row.update({v: av for v, av in zip(xl, a)})
                    row.update({v: bv for v, bv in zip(yl, b)})
                    rows.append(row)
            rows = _dedup(rows)
            if len(rows) >= 2 and not _sat_ind(rows, xl, yl):
                meta = {"mode": "ind", "team": rows, "xl": xl, "yl": yl, "dom": dom}
                return meta, False
    return None


def _construct_split(cfg, target):
    dom = cfg.dom
    base = ["u", "v", "p", "q"]
    for _ in range(80):
        strict = random.random() < 0.5
        phi = {"kind": random.choice(["eq", "neq"]), "u": "u", "w": "v"}
        psi = {"kind": random.choice(["eq", "neq"]), "u": "p", "w": "q"}

        def force_false(row, lit):
            u, w = lit["u"], lit["w"]
            if lit["kind"] == "eq":
                row[w] = (row[u] + 1 + random.randrange(dom - 1)) % dom
            else:
                row[w] = row[u]

        def force_true(row, lit):
            u, w = lit["u"], lit["w"]
            if lit["kind"] == "eq":
                row[w] = row[u]
            else:
                row[w] = (row[u] + 1 + random.randrange(dom - 1)) % dom

        if target:
            rows = []
            nl = random.randint(1, 2)
            for _i in range(nl):
                row = {v: random.randrange(dom) for v in base}
                force_true(row, phi)
                rows.append(row)
            nr = random.randint(1, 2)
            for _i in range(nr):
                row = {v: random.randrange(dom) for v in base}
                force_true(row, psi)
                rows.append(row)
            rows = _dedup(rows)
            if len(rows) >= 2 and _sat_split(rows, phi, psi, strict):
                meta = {"mode": "split", "team": rows, "phi": phi, "psi": psi, "dom": dom,
                        "semantics": "strict" if strict else "lax"}
                return meta, True
        else:
            size = random.randint(1, 2)
            rows = []
            for _i in range(size):
                row = {v: random.randrange(dom) for v in base}
                force_false(row, phi)
                force_false(row, psi)
                rows.append(row)
            rows = _dedup(rows)
            if rows and not _sat_split(rows, phi, psi, strict):
                meta = {"mode": "split", "team": rows, "phi": phi, "psi": psi, "dom": dom,
                        "semantics": "strict" if strict else "lax"}
                return meta, False
    return None


def _construct_exists(cfg, target):
    dom = cfg.dom
    base = ["u", "v"]
    for _ in range(80):
        strict = random.random() < 0.5
        x = "x"
        kind = random.choice(["eq", "neq"])
        pair = random.choice([("x", "u"), ("x", "v"), ("u", "v")])
        u, w = pair
        inner = {"kind": kind, "u": u, "w": w}
        size = random.randint(1, min(3, max(cfg.max_team, 1)))
        rows = []
        for _r in range(size):
            row = {v: random.randrange(dom) for v in base}
            rows.append(row)
        rows = _dedup(rows)
        if not rows:
            continue
        holds = _sat_exists(rows, inner, x, dom, strict)
        if holds == target:
            meta = {"mode": "exists", "team": rows, "inner": inner, "x": x, "dom": dom,
                    "semantics": "strict" if strict else "lax"}
            return meta, holds
    return None


_MODES = {
    "dep": _construct_dep,
    "incl": _construct_incl,
    "ind": _construct_ind,
    "split": _construct_split,
    "exists": _construct_exists,
}


@dataclass
class TeamSemanticsConfig(Config):
    max_team: int = 2
    max_vars: int = 2
    dom: int = 2

    def apply_difficulty(self, level):
        self.max_team = max(2, 2 + min(level, 4))
        self.max_vars = 2 + min(level, 3)
        self.dom = 2 if level <= 3 else 3


class TeamSemanticsEvaluation(Task):
    task_name = "team_semantics_evaluation"
    summary = ("Evaluate team-semantics formulas over finite sets of assignments: "
               "dependence, inclusion, and independence atoms plus split disjunction "
               "and quantified team extension under strict or lax semantics; return "
               "Yes/No satisfaction.")
    design_choice = ("Generate formulas with exactly one connective type per instance, "
                     "and vary the team size and variable count to control difficulty "
                     "while keeping the answer binary.")
    config_cls = TeamSemanticsConfig

    def generate_entry(self):
        target = random.random() < 0.5
        modes = list(_MODES)
        random.shuffle(modes)
        for m in modes:
            res = _MODES[m](self.config, target)
            if res is not None:
                meta, holds = res
                answer = "Yes" if holds else "No"
                return Entry(metadata=meta, answer=answer)
        raise RuntimeError("team_semantics_evaluation: could not construct an instance for target")

    def render_prompt(self, metadata):
        mode = metadata["mode"]
        team = _fmt_team(metadata["team"])
        dom = int(metadata["dom"])
        head = (
            "In team semantics a formula is evaluated over a finite team: a set of "
            "assignments (rows) that map each variable to a value in {"
            + ",".join(str(v) for v in range(dom))
            + "}."
        )
        body = _SEMANTIC_TEXT[mode].format(meta=metadata)
        formula = _fmt_formula(mode, metadata)
        semantics = metadata.get("semantics")
        sem_line = (
            f"This problem uses {semantics.upper()} semantics."
            if semantics
            else "This atom has a single semantics (strict and lax coincide)."
        )
        return (
            f"{head}\n\n"
            f"{body}\n\n"
            f"Team rows:\n{team}\n\n"
            f"{sem_line}\n"
            f"Formula: {formula}\n\n"
            f"Determine whether the team is a model of the formula. "
            f"Write Yes for a model, No otherwise."
        )

    def score_answer(self, answer, entry):
        gold = entry["answer"]
        a = str(answer).strip().lower()
        g = str(gold).strip().lower()
        if a not in ("yes", "no"):
            return 0.0
        return 1.0 if a == g else 0.0


def _fmt_team(rows):
    rows = _dedup(rows)
    keys = sorted(rows[0].keys()) if rows else []
    lines = []
    for i, r in enumerate(rows, 1):
        lines.append("  %d. %s" % (i, " ".join("%s=%d" % (k, r[k]) for k in keys)))
    return "\n".join(lines) if lines else "  (empty)"


def _fmt_formula(mode, meta):
    if mode == "dep":
        return "=(" + ",".join(meta["xl"]) + "; " + meta["y"] + ")"
    if mode == "incl":
        return ",".join(meta["xl"]) + " \u2286 " + ",".join(meta["yl"])
    if mode == "ind":
        return ",".join(meta["xl"]) + " \u22a5 " + ",".join(meta["yl"])
    if mode == "split":
        return _fmt_literal(meta["phi"]) + " \u2297 " + _fmt_literal(meta["psi"])
    if mode == "exists":
        return "\u2203" + meta["x"] + " " + _fmt_literal(meta["inner"])
    return ""


_SEMANTIC_TEXT = {
    "dep": ("Write =(X;y) for the dependence atom: it is satisfied exactly when every two "
            "rows that agree on all variables in X also agree on y."),
    "incl": ("Write X\u2286Y for the inclusion atom: it is satisfied exactly when each "
             "row's tuple of Y-values occurs as the X-tuple of some row."),
    "ind": ("Write X\u22a5Y for the independence atom: it is satisfied exactly when every "
            "combination of an X-tuple that occurs and a Y-tuple that occurs appears "
            "together in some row."),
    "split": ("A literal (u=w) is satisfied by a team iff every row has u=w, and (u!=w) "
              "iff every row has u!=w.  The split disjunction phi\u2297psi is satisfied "
              "iff the rows can be shared out into a nonempty left part satisfying phi "
              "and a nonempty right part satisfying psi.  Under STRICT semantics no row "
              "may be in both parts; under LAX semantics a row may be in both parts, and "
              "the two parts together must use up every row."),
    "exists": ("A literal (u=w) is satisfied by a team iff every row has u=w, and (u!=w) "
               "iff every row has u!=w.  The formula \u2203x phi is satisfied iff there is "
               "a team over the base variables plus x, agreeing with the given team on the "
               "base variables, whose rows satisfy phi.  Under STRICT semantics each given "
               "row is extended by exactly one value of x; under LAX semantics a given row "
               "may be extended by one or by several different values of x."),
}


TASK_META = {'parent_source_id': None,
 'idea': 'team_semantics_evaluation (variant 1 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r5/team_semantics_evaluation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2305351643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

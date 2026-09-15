import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'relational_join_execution (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:relational_join_execution',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/relational_join_execution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1718001595,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

L_BASE = ["x", "a", "b"]
R_BASE = ["y", "c", "d"]
JOIN_TYPES = ["inner", "left", "semi", "anti"]


@dataclass
class RelationalJoinConfig(Config):
    level: int = 0
    seed: int = None
    n_l: int = 3
    n_r: int = 3
    key_universe: int = 3
    l_cols: int = 2
    r_cols: int = 2

    def apply_difficulty(self, level):
        self.n_l = 2 + level
        self.n_r = 2 + level
        self.key_universe = max(2, (self.n_l + 1) // 2)
        self.l_cols = 1 + (1 if level >= 3 else 0)
        self.r_cols = 1 + (1 if level >= 4 else 0)


def _build_relation(n, ku, n_val):
    """Return list of rows in column order [key, val1, ..., valn] with a guaranteed repeated key."""
    rows = []
    for _ in range(n):
        k = random.randrange(ku)
        vals = [random.randrange(1, 10) for _ in range(n_val)]
        rows.append([k] + vals)
    keys = [r[0] for r in rows]
    if n > 1 and len(set(keys)) == n:
        rows[-1][0] = rows[0][0]
    return rows


def _join_rows(jtype, L, R):
    """Return list of (lrow, rrow_or_None) pairs in input row order, plus the raw L results
    for semi/anti. Kept as a pure function so both generation and verification share it."""
    if jtype in ("inner", "left"):
        out = []
        for lrow in L:
            matches = [rrow for rrow in R if rrow[0] == lrow[0]]
            for rrow in matches:
                out.append((lrow, rrow))
            if jtype == "left" and not matches:
                out.append((lrow, None))
        return out
    # semi/anti return only L rows, in L order
    out = []
    for lrow in L:
        has = any(rrow[0] == lrow[0] for rrow in R)
        if jtype == "semi" and has:
            out.append((lrow, None))
        elif jtype == "anti" and not has:
            out.append((lrow, None))
    return out


def _selected_projection(eligible):
    k = random.randrange(1, len(eligible) + 1)
    chosen = set(random.sample(eligible, k))
    return [c for c in eligible if c in chosen]


class RelationalJoinExecution(Task):
    summary = ("Execute inner, left, semi, and anti joins on small keyed relations with "
               "repeated keys, then return a specified projection or exact aggregate.")
    design_choice = ("Answer is a canonical join-result table string with rows sorted by "
                     "input row order and keys repeated per occurrence.")
    config_cls = RelationalJoinConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        jtype = random.choice(JOIN_TYPES)
        l_names = L_BASE[:cfg.l_cols + 1]
        r_names = R_BASE[:cfg.r_cols + 1]
        L = _build_relation(cfg.n_l, cfg.key_universe, cfg.l_cols)
        R = _build_relation(cfg.n_r, cfg.key_universe, cfg.r_cols)

        if jtype in ("inner", "left"):
            eligible = l_names + r_names
        else:
            eligible = list(l_names)
        proj = _selected_projection(eligible)

        joined = _join_rows(jtype, L, R)

        # verify the join before producing the answer
        if jtype == "inner":
            assert all(l[0] == r[0] for l, r in joined)
            matched = set((i, j) for i, l in enumerate(L) for j, r in enumerate(R)
                          if r[0] == l[0])
            assert len(joined) == len(matched)
        elif jtype == "left":
            assert len(joined) == sum(
                max(1, sum(1 for r in R if r[0] == l[0])) for l in L)
            for l, r in joined:
                assert (r is not None and l[0] == r[0]) or (
                    r is None and not any(rr[0] == l[0] for rr in R))
        elif jtype == "semi":
            assert len(joined) == sum(
                1 for l in L if any(r[0] == l[0] for r in R))
            assert all(any(r[0] == l[0] for r in R) for l, _ in joined)
        elif jtype == "anti":
            assert len(joined) == sum(
                1 for l in L if not any(r[0] == l[0] for r in R))
            assert all(not any(r[0] == l[0] for r in R) for l, _ in joined)

        header = ", ".join(proj)
        lines = []
        for lrow, rrow in joined:
            cells = []
            for col in proj:
                if col in l_names:
                    cells.append(str(lrow[l_names.index(col)]))
                else:
                    if rrow is None:
                        cells.append("NULL")
                    else:
                        cells.append(str(rrow[r_names.index(col)]))
            lines.append(", ".join(cells))
        answer = header + "\n" + "\n".join(lines)

        metadata = {
            "jtype": jtype,
            "l_cols": l_names,
            "r_cols": r_names,
            "L": L,
            "R": R,
            "projection": proj,
            "answer_rows": len(joined),
            "key_universe": cfg.key_universe,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        jtype = metadata["jtype"]
        l_names = metadata["l_cols"]
        r_names = metadata["r_cols"]
        L = metadata["L"]
        R = metadata["R"]

        if jtype in ("inner", "left"):
            r_desc = ("Relation R has columns " + ", ".join(r_names) +
                      " (key " + r_names[0] + ").")
        else:
            r_desc = "Relation R has columns " + ", ".join(r_names) + "."

        join_verb = {
            "inner": ("Perform an inner join of L and R on the condition that the keys are "
                      "equal, keeping only the L rows that have at least one matching R row."),
            "left": ("Perform a left join of L and R on the condition that the keys are equal, "
                     "keeping every L row; for an L row with no matching R row, put NULL for "
                     "the R columns."),
            "semi": ("Perform a semi join: keep each L row, once, if it has at least one "
                     "matching R row; output only the L columns."),
            "anti": ("Perform an anti join: keep each L row, once, if it has no matching R "
                     "row; output only the L columns."),
        }[jtype]

        def fmt_rel(names, rows):
            head = ", ".join(names)
            body = "\n".join(", ".join(str(v) for v in r) for r in rows)
            return "(" + head + ")\n" + body

        return (
            "Two small relations are given below. Relation L has columns " +
            ", ".join(l_names) + " (key " + l_names[0] + "). " + r_desc + "\n\n" +
            join_verb + "\n\n" +
            "Project the join result onto the columns " + ", ".join(metadata["projection"]) + ".\n\n" +
            "Write the resulting table with a first line listing the projected column names and "
            "one row per output line, values separated by \", \" (a comma then a space), keeping "
            "rows in join order: for inner and left joins, walk the L rows in their given order "
            "and, for each, the matching R rows in their given order; for semi and anti joins, "
            "list the kept L rows in their given order. Represent a missing value as NULL. "
            "Example format:\n\np, q\n1, 2\n3, 4\n\n" +
            "L " + fmt_rel(l_names, L) + "\n\n" +
            "R " + fmt_rel(r_names, R)
        )

    def score_answer(self, answer, entry):
        ref = str(entry["answer"]).strip()
        if answer is None:
            return 0.0
        if str(answer).strip() == ref:
            return 1.0
        return 0.0

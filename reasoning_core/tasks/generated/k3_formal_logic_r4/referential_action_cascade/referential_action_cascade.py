import random
from dataclasses import dataclass

from reasoning_core.template import Config as BaseConfig
from reasoning_core.template import Entry, Task, stochastic_rounding

RESTRICT = "restrict"
CASCADE = "cascade"
SET_NULL = "set-null"
SET_DEFAULT = "set-default"
ACTIONS = [RESTRICT, CASCADE, SET_NULL, SET_DEFAULT]

DEFAULT_SENTINEL = -999999


class FKViolation(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def _children(fks, tab):
    return [fk for fk in fks if fk["parent"] == tab]


def _pk_of(tables, tab):
    for t in tables:
        if t["name"] == tab:
            return t["pk"]
    return "id"


def _referenced_rows(rows, col, val):
    return [r for r in rows if r.get(col) == val]


def _delete_propagate(rows, tables, fks, tab, r):
    for fk in _children(fks, tab):
        child_tab = fk["child"]
        child_pk = _pk_of(tables, child_tab)
        dependents = _referenced_rows(rows[child_tab], fk["fkc"], r[fk["parent_pk"]])
        if fk["action"] == RESTRICT:
            if dependents:
                raise FKViolation(RESTRICT)
        elif fk["action"] == CASCADE:
            for cr in list(dependents):
                rows[child_tab].remove(cr)
                _delete_propagate(rows, tables, fks, child_tab, cr)
        elif fk["action"] == SET_NULL:
            for cr in dependents:
                cr[fk["fkc"]] = None
        else:
            for cr in dependents:
                cr[fk["fkc"]] = fk["default"]


def _update_propagate(rows, tables, fks, tab, oldval, newval):
    for fk in _children(fks, tab):
        child_tab = fk["child"]
        dependents = _referenced_rows(rows[child_tab], fk["fkc"], oldval)
        if fk["action"] == RESTRICT:
            if dependents:
                raise FKViolation(RESTRICT)
        elif fk["action"] == CASCADE:
            for cr in dependents:
                cr[fk["fkc"]] = newval
        elif fk["action"] == SET_NULL:
            for cr in dependents:
                cr[fk["fkc"]] = None
        else:
            for cr in dependents:
                cr[fk["fkc"]] = fk["default"]


def _check_child_fk(rows, tables, fks, child_tab, fkc, val):
    if val is None:
        return
    parent_tab = None
    reason = None
    for fk in fks:
        if fk["child"] == child_tab and fk["fkc"] == fkc:
            parent_tab = fk["parent"]
            reason = fk["action"]
            break
    if parent_tab is None:
        return
    parent_pk = _pk_of(tables, parent_tab)
    if not any(r.get(parent_pk) == val for r in rows[parent_tab]):
        raise FKViolation(reason)


def execute_op(op, rows, tables, fks):
    t = op["t"]
    if t == "insert":
        tab = op["table"]
        row = dict(op["row"])
        fkc = op["fkc"]
        if fkc:
            _check_child_fk(rows, tables, fks, tab, fkc, row.get(fkc))
        rows[tab].append(row)
    elif t == "update":
        tab = op["table"]
        pk = op["pk"]
        target = op["where_pk"]
        rset = [r for r in rows[tab] if r.get(pk) == target]
        if not rset:
            return
        r = rset[0]
        for col, newval in op["sets"]:
            if col == pk:
                _update_propagate(rows, tables, fks, tab, r[col], newval)
                if newval in {x.get(pk) for x in rows[tab] if x is not r}:
                    raise FKViolation(RESTRICT)
                r[col] = newval
            else:
                _check_child_fk(rows, tables, fks, tab, col, newval)
                r[col] = newval
    elif t == "delete":
        tab = op["table"]
        pk = op["pk"]
        target = op["where_pk"]
        rset = [r for r in rows[tab] if r.get(pk) == target]
        if not rset:
            return
        r = rset[0]
        _delete_propagate(rows, tables, fks, tab, r)
        if r in rows[tab]:
            rows[tab].remove(r)


def _referentially_ok(rows, tables, fks):
    for fk in fks:
        parent_ids = {r.get(fk["parent_pk"]) for r in rows[fk["parent"]]
                      if r.get(fk["parent_pk"]) is not None}
        for r in rows[fk["child"]]:
            v = r.get(fk["fkc"])
            if v is not None and v not in parent_ids:
                return False
    return True


def simulate(schema, statements):
    tables = schema["tables"]
    fks = schema["fks"]
    rows = {}
    for t in tables:
        rows[t["name"]] = [dict(r) for r in schema["seed"][t["name"]]]
    for i, op in enumerate(statements):
        try:
            execute_op(op, rows, tables, fks)
        except FKViolation as e:
            return ("reject", i, e.reason)
    return ("ok", None, None)


def _fresh_rows(schema):
    rows = {}
    for t in schema["tables"]:
        rows[t["name"]] = [dict(r) for r in schema["seed"][t["name"]]]
    return rows


def _live_ids(rows, pk):
    return sorted({r.get(pk) for r in rows if r.get(pk) is not None})


def _gen_pk(ids):
    while True:
        v = "nx" + str(random.randrange(10 ** 9))
        if v not in ids:
            return v


def _random_op(rows, tables, fks):
    tab = random.choice(tables)
    name = tab["name"]
    pk = tab["pk"]
    ids = _live_ids(rows[name], pk)
    fkc = None
    parentpk = None
    for fk in fks:
        if fk["child"] == name:
            fkc = fk["fkc"]
            parentpk = fk["parent_pk"]
            break
    kind = random.choice(["insert", "delete", "update_pk", "update_fk"])
    if kind == "insert" or not ids:
        newpk = _gen_pk(ids)
        fkval = None
        if fkc is not None:
            pids = _live_ids(_parent_rows(rows, fks, name), parentpk)
            fkval = random.choice(pids) if pids else None
        row = {pk: newpk}
        if fkc is not None:
            row[fkc] = fkval
        return {"t": "insert", "table": name, "pk": pk, "fkc": fkc, "row": row}
    if kind == "delete":
        val = random.choice(ids)
        return {"t": "delete", "table": name, "pk": pk, "where_pk": val}
    if kind == "update_pk":
        val = random.choice(ids)
        newpk = _gen_pk([x for x in ids if x != val])
        return {"t": "update", "table": name, "pk": pk, "where_pk": val, "sets": [[pk, newpk]]}
    val = random.choice(ids)
    pids = _live_ids(_parent_rows(rows, fks, name), parentpk) if fkc is not None else []
    newval = random.choice(pids) if pids else None
    return {"t": "update", "table": name, "pk": pk, "where_pk": val, "sets": [[fkc, newval]]}


def _parent_name(fks, name):
    for fk in fks:
        if fk["child"] == name:
            return fk["parent"]
    return None


def _parent_rows(rows, fks, name):
    pn = _parent_name(fks, name)
    return rows[pn] if pn else []


def _try_valid(rows, tables, fks, tries=60):
    for _ in range(tries):
        op = _random_op(rows, tables, fks)
        rows2 = {k: [dict(r) for r in v] for k, v in rows.items()}
        try:
            execute_op(op, rows2, tables, fks)
        except FKViolation:
            continue
        if _referentially_ok(rows2, tables, fks):
            return op, rows2
    return None, rows


def _violating_op(fks, tables, rows):
    fk = random.choice(fks)
    name = fk["child"]
    pk = _pk_of(tables, name)
    ids = _live_ids(rows[name], pk)
    newpk = _gen_pk(ids)
    dangling = "__dangling__" + str(random.randrange(10 ** 9))
    row = {pk: newpk, fk["fkc"]: dangling}
    return {"t": "insert", "table": name, "pk": pk, "fkc": fk["fkc"], "row": row}


def _build_schema(config):
    n = config.ntables
    tables = [{"name": f"t{i}", "pk": f"id{i}"} for i in range(n)]
    fks = []
    for i in range(1, n):
        fks.append({
            "name": f"fk{i}",
            "child": f"t{i}",
            "fkc": f"ref{i}",
            "parent": f"t{i-1}",
            "parent_pk": f"id{i-1}",
            "action": random.choice(ACTIONS),
            "default": DEFAULT_SENTINEL - i,
        })
    fks.append({
        "name": "fk_back",
        "child": "t0",
        "fkc": "reflast",
        "parent": f"t{n-1}",
        "parent_pk": f"id{n-1}",
        "action": random.choice(ACTIONS),
        "default": DEFAULT_SENTINEL,
    })
    seed = {}
    for t in tables:
        name = t["name"]
        pk = t["pk"]
        seed[name] = [{pk: f"{name}#{j}"} for j in range(2)]
    for i in range(1, n):
        parent_vals = [r[tables[i - 1]["pk"]] for r in seed[tables[i - 1]["name"]]]
        for r in seed[tables[i]["name"]]:
            r[f"ref{i}"] = random.choice(parent_vals)
    last_vals = [r[tables[n - 1]["pk"]] for r in seed[tables[n - 1]["name"]]]
    for r in seed["t0"]:
        r["reflast"] = random.choice(last_vals)
    return {"tables": tables, "fks": fks, "seed": seed}


def _build_instance(config):
    schema = _build_schema(config)
    rows = _fresh_rows(schema)
    tables = schema["tables"]
    fks = schema["fks"]
    n = config.nstatements
    reject = random.random() < 0.72
    valid_ops = []
    cur = rows
    build_target = n if not reject else n - 1
    guard = 0
    while len(valid_ops) < build_target and guard < 3 * (n + 4):
        op, cur = _try_valid(cur, tables, fks)
        if op is None:
            guard += 1
            continue
        valid_ops.append(op)
        guard = 0
    if not reject:
        return schema, valid_ops
    v = random.randint(0, len(valid_ops)) if valid_ops else 0
    prefix = valid_ops[:v]
    stmts = prefix + [_violating_op(fks, tables, cur)]
    stmts += valid_ops[v:]
    return schema, stmts


def _fmt_stmt(s):
    t = s["t"]
    if t == "insert":
        shown = {k: v for k, v in s["row"].items() if v is not None}
        parts = ", ".join(f"{k}={v}" for k, v in shown.items())
        return f"insert into {s['table']} ({parts})"
    if t == "delete":
        return f"delete from {s['table']} where {s['pk']}={s['where_pk']}"
    if t == "update":
        sets = ", ".join(f"{c}={v}" for c, v in s["sets"])
        return f"update {s['table']} set {sets} where {s['pk']}={s['where_pk']}"
    return str(s)


@dataclass
class Config(BaseConfig):
    ntables: int = 3
    nstatements: int = 5

    def apply_difficulty(self, level):
        self.ntables = stochastic_rounding(3 + (level // 2))
        self.nstatements = stochastic_rounding(5 + level)


class ReferentialActionCascade(Task):
    summary = "Execute inserts, key updates, and deletes under restrict, cascade, set-null, and set-default foreign keys, crossing cycles and deferred checks; answer altered rows, repair bindings, or first rejected statement."
    design_choice = "Answer form: a canonical string listing the first rejected statement's index and the reason code (e.g., '3:restrict') when a constraint violation occurs, otherwise 'accepted'."
    config_cls = Config

    def generate_entry(self):
        schema, stmts = _build_instance(self.config)
        result, idx, reason = simulate(schema, stmts)
        answer = "accepted" if result == "ok" else f"{idx}:{reason}"
        expect, i2, r2 = simulate(schema, stmts)
        ex = "accepted" if expect == "ok" else f"{i2}:{r2}"
        if ex != answer:
            raise RuntimeError("simulator unstable")
        metadata = {
            "tables": schema["tables"],
            "fks": schema["fks"],
            "seed": schema["seed"],
            "statements": stmts,
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        for fk in metadata["fks"]:
            lines.append(
                f"FK {fk['name']}: {fk['child']}.{fk['fkc']} references "
                f"{fk['parent']}.{fk['parent_pk']} on-{fk['action']}"
            )
        lines.append("Initial rows:")
        for t in metadata["tables"]:
            name = t["name"]
            rows_txt = "; ".join(
                ",".join(f"{k}={v}" for k, v in row.items()) for row in metadata["seed"][name]
            )
            lines.append(f"  {name}: {rows_txt}")
        lines.append("Statements (0-indexed, run in order):")
        for i, s in enumerate(metadata["statements"]):
            lines.append(f"  {i}: {_fmt_stmt(s)}")
        lines.append(
            "Execute the statements in order under the foreign-key constraints. "
            "If a statement is rejected as the first referential-integrity violation "
            "at index i by a constraint of action a (restrict, cascade, set-null, "
            "set-default), answer exactly 'i:a' (for example '3:restrict'). If no "
            "statement is rejected, answer exactly 'accepted'."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        if answer.strip() == entry.answer:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'referential_action_cascade (variant 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_logic_r4/referential_action_cascade',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

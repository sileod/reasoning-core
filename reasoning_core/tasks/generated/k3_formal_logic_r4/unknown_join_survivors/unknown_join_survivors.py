import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

_COLS = ["p", "x", "y"]
_OPS = ["=", "!=", "<", "<=", ">", ">="]


def _maybe_int(lo, hi, prob):
    """A small int in [lo, hi], or None (SQL NULL) with probability ``prob``."""
    return None if random.random() < prob else random.randint(lo, hi)


def _compare3(left, op, right):
    """Three-valued comparison; returns True/False/None (None == UNKNOWN)."""
    if left is None or right is None:
        return None
    if op == "=":
        return left == right
    if op == "!=":
        return left != right
    if op == "<":
        return left < right
    if op == "<=":
        return left <= right
    if op == ">":
        return left > right
    if op == ">=":
        return left >= right
    raise ValueError(op)


def _and3(vals):
    if any(v is False for v in vals):
        return False
    if all(v is True for v in vals):
        return True
    return None


def _not3(v):
    if v is None:
        return None
    return not v


def _atom_eval(row, atom):
    row = dict(row)
    if atom[0] == "cmp":
        col, op, other = atom[1], atom[2], atom[3]
        left = row[col]
        right = row[other] if isinstance(other, str) else other
        return _compare3(left, op, right)
    col, is_null = atom[1], atom[2]
    present = row[col] is not None
    return (not present) if is_null else present


def _formula_eval(row, atoms, negated):
    val = _and3([_atom_eval(row, a) for a in atoms])
    return _not3(val) if negated else val


def _bag_join(R, S):
    out = []
    for r in R:
        for s in S:
            if r["p"] is not None and r["p"] == s["p"]:
                out.append({
                    "rpk": r["pk"], "spk": s["pk"],
                    "p": r["p"], "x": r["x"], "y": s["y"],
                })
    return out


def _answer_of(survivors):
    if not survivors:
        return "[]"
    return " ".join("(%s,%s)" % (s["rpk"], s["spk"]) for s in survivors)


def _normalize(text):
    return "".join(str(text).split())


def score_answer_list(answer, reference):
    return 1.0 if _normalize(answer) == _normalize(reference) else 0.0


@dataclass
class UnknownJoinConfig(Config):
    rows_max: int = 3
    domain: int = 2
    value_range: int = 2
    max_atoms: int = 1

    def apply_difficulty(self, level):
        self.rows_max = 3 + (level >= 1) + (level >= 3) + (level >= 5)
        self.domain = 2 + (level >= 1) + (level >= 3)
        self.value_range = 2 + (level >= 2) + (level >= 4)
        self.max_atoms = 1 + (level >= 2) + (level >= 4)


def _gen_table(prefix, count, domain, value_range):
    rows = []
    for i in range(count):
        p = _maybe_int(1, domain, 0.15)
        v = _maybe_int(0, value_range - 1, 0.2)
        rows.append({"pk": "%s%d" % (prefix, i), "p": p,
                     "x": v if prefix == "r" else None,
                     "y": v if prefix == "s" else None})
    return rows


def _gen_atoms(max_atoms, value_range):
    count = random.randint(1, max_atoms)
    atoms = []
    for _ in range(count):
        col = random.choice(_COLS)
        if random.random() < 0.5:
            other = random.choice(_COLS)
        else:
            other = random.choice([None, random.randint(0, value_range - 1)])
        atoms.append(("cmp", col, random.choice(_OPS), other))
    return atoms


def _render_atom(atom):
    if atom[0] == "cmp":
        _, col, op, other = atom
        return "%s %s %s" % (col, op, other)
    raise ValueError(atom)


def _render_formula(atoms, negated):
    body = " AND ".join(_render_atom(a) for a in atoms)
    return "NOT ( %s )" % body if negated else body


def _render_tables(R, S):
    lines = ["Table R (row key, join value p, value x):"]
    for r in R:
        lines.append("  %s: p=%s, x=%s" % (r["pk"], r["p"], r["x"]))
    lines.append("Table S (row key, join value p, value y):")
    for s in S:
        lines.append("  %s: p=%s, y=%s" % (s["pk"], s["p"], s["y"]))
    return "\n".join(lines)


def _render_prompt(metadata):
    m = metadata
    lines = [
        "Evaluate a bag natural join followed by a selection over two small tables.",
        "",
        _render_tables(m["R"], m["S"]),
        "",
        "Join R and S on attribute p (rows match when their p values are equal; "
        "NULL never matches). A matched row carries p, x (from R) and y (from S). "
        "This is a bag join: every matching (R,S) pair is its own output row.",
        "",
        "Then apply the selection predicate:",
        "  " + _render_formula(m["atoms"], m["negated"]),
        "",
        "The predicate uses SQL three-valued logic: a comparison involving NULL "
        "yields UNKNOWN, and NOT UNKNOWN is UNKNOWN. A row survives only when the "
        "predicate evaluates to TRUE.",
        "",
        "Answer the keys of the surviving joined rows as an ordered list, one "
        "(Rkey,Skey) per survivor in join order (R rows top to bottom, then S rows "
        "top to bottom within each R row), duplicates repeated, separated by spaces. "
        "If the list would be empty, output the two characters [ ] instead.",
    ]
    return "\n".join(lines)


class UnknownJoinSurvivors(Task):
    summary = ("Evaluate bag natural joins over small tables with NULL values, then "
               "selections whose possibly-negated predicates exercise NULL/UNKNOWN "
               "three-valued logic, answering survivors as an ordered list of original "
               "row keys with duplicates repeated for provenance.")
    design_choice = ("Answer as ordered list of original row keys surviving the join, "
                     "with duplicate keys repeated to preserve provenance.")
    config_cls = UnknownJoinConfig
    task_version = 2

    def generate_entry(self):
        survivors = None
        for _ in range(40):
            m = random.randint(2, self.config.rows_max)
            n = random.randint(2, self.config.rows_max)
            R = _gen_table("r", m, self.config.domain, self.config.value_range)
            S = _gen_table("s", n, self.config.domain, self.config.value_range)
            joined = _bag_join(R, S)
            atoms = _gen_atoms(self.config.max_atoms, self.config.value_range)
            negated = random.random() < 0.5
            survivors = [j for j in joined
                         if _formula_eval(j, atoms, negated) is True]
            if survivors:
                break
        answer = _answer_of(survivors)
        metadata = {
            "R": R, "S": S, "atoms": atoms, "negated": negated,
            "survivors": [[s["rpk"], s["spk"]] for s in survivors],
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return _render_prompt(metadata)

    def score_answer(self, answer, entry):
        return score_answer_list(answer, entry.answer)


TASK_META = {'parent_source_id': None,
 'idea': 'unknown_join_survivors (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_logic_r4/unknown_join_survivors',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

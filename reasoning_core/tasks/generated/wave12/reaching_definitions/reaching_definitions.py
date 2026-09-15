import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class ReachingDefinitionsConfig(Config):
    n_lines: int = 3
    depth: int = 1
    body_max: int = 2

    def apply_difficulty(self, level):
        self.n_lines = 3 + level
        self.depth = 1 + level // 2
        self.body_max = 2 + (1 if level >= 4 else 0)


VARIABLES = ["x", "y", "z"]


def _expr(var):
    r = random.random()
    if r < 0.4:
        return str(random.randint(0, 9))
    if r < 0.8:
        return f"{var} + {random.randint(1, 9)}"
    return random.choice(["a", "b", "c"])


def _cond():
    return random.choice(["c1", "c2", "c3", "c4"])


def _gen_seq(depth, body_max, count, label_counter):
    """Generate a list of statements. Returns (ast_list, label_counter)."""
    ast = []
    n = count
    for _ in range(n):
        r = random.random()
        if depth > 0 and r < 0.30:
            sub = random.randint(1, body_max)
            if random.random() < 0.5:
                thens, label_counter = _gen_seq(depth - 1, body_max, sub, label_counter)
                elses, label_counter = _gen_seq(depth - 1, body_max, random.randint(1, body_max), label_counter)
                ast.append({"k": "i", "cond": _cond(), "then": thens, "else": elses})
            else:
                body, label_counter = _gen_seq(depth - 1, body_max, sub, label_counter)
                ast.append({"k": "w", "cond": _cond(), "body": body})
        else:
            var = random.choice(VARIABLES)
            ast.append({"k": "a", "label": label_counter, "var": var, "expr": _expr(var)})
            label_counter += 1
    return ast, label_counter


def _assignments(ast):
    for s in ast:
        if s["k"] == "a":
            yield s["label"], s["var"]
        elif s["k"] == "i":
            yield from _assignments(s["then"])
            yield from _assignments(s["else"])
        else:
            yield from _assignments(s["body"])


def _build_nodes(ast):
    """Convert a statement AST into a CFG node list. Returns nodes and exit index."""
    nodes = []

    def new_node(nkind, gen=(), kill=()):
        idx = len(nodes)
        nodes.append({"kind": nkind, "succ": [], "gen": set(gen), "kill": set(kill)})
        return idx

    def build(seq):
        # returns entry, exit
        if not seq:
            e = new_node("nop")
            return e, e
        entry = None
        prev_exit = None
        tail_exit = None
        for s in seq:
            e, x = build_stmt(s)
            if entry is None:
                entry = e
            else:
                nodes[prev_exit]["succ"].append(e)
            prev_exit = x
            tail_exit = x
        return entry, tail_exit

    def build_stmt(s):
        if s["k"] == "a":
            e = new_node("assign", gen=(s["label"],), kill=kill_for(s["var"]))
            return e, e
        if s["k"] == "i":
            cond = new_node("cond")
            te, tx = build(s["then"])
            ee, ex = build(s["else"])
            merge = new_node("merge")
            nodes[cond]["succ"].extend([te, ee])
            nodes[tx]["succ"].append(merge)
            nodes[ex]["succ"].append(merge)
            return cond, merge
        # k == 'w'
        head = new_node("cond")
        be, bx = build(s["body"])
        merge = new_node("merge")
        nodes[head]["succ"].extend([be, merge])
        nodes[bx]["succ"].append(head)
        return head, merge

    var_to_labels = {}
    for lab, var in _assignments(ast):
        var_to_labels.setdefault(var, []).append(lab)

    def kill_for(var):
        return var_to_labels.get(var, []) if var is not None else []

    entry, exit = build(ast)
    return nodes, entry, exit


def _dataflow(nodes):
    n = len(nodes)
    IN = [set() for _ in range(n)]
    OUT = [set() for _ in range(n)]
    preds = [[] for _ in range(n)]
    for j, nd in enumerate(nodes):
        for s in nd["succ"]:
            preds[s].append(j)
    changed = True
    while changed:
        changed = False
        for i in range(n):
            newin = set()
            for p in preds[i]:
                newin |= OUT[p]
            nd = nodes[i]
            newout = (newin - nd["kill"]) | nd["gen"]
            if newin != IN[i] or newout != OUT[i]:
                IN[i] = newin
                OUT[i] = newout
                changed = True
    return IN, OUT


def _solve(ast):
    nodes, entry, exit = _build_nodes(ast)
    IN, OUT = _dataflow(nodes)
    return sorted(IN[exit]), nodes, IN, OUT, exit


def _fmt_node(ast, ind, out):
    for s in ast:
        if s["k"] == "a":
            out.append(" " * ind + f"L{s['label']}: {s['var']} = {s['expr']}")
        elif s["k"] == "i":
            out.append(" " * ind + f"if ({s['cond']}):")
            _fmt_node(s["then"], ind + 2, out)
            out.append(" " * ind + "else:")
            _fmt_node(s["else"], ind + 2, out)
        else:
            out.append(" " * ind + f"while ({s['cond']}):")
            _fmt_node(s["body"], ind + 2, out)


def _render_program(ast):
    out = []
    _fmt_node(ast, 0, out)
    return "\n".join(out)


def _answer_str(labels):
    if not labels:
        return "none"
    return ", ".join("L%d" % l for l in labels)


def _parse_answer(answer):
    if answer is None:
        return None
    s = str(answer).strip()
    if s.lower() == "none":
        return []
    import re
    return sorted(int(m) for m in re.findall(r"[Ll](\d+)", s))


class ReachingDefinitions(Task):
    summary = ("Propagate reaching-definition sets through branched control flow and loops, returning the "
               "sorted set of labeled assignments that can reach a queried program point.")
    config_cls = ReachingDefinitionsConfig
    design_choice = ("Instance format: a small imperative program with branches/loops and a query point; "
                     "answer is a canonical sorted set of assignment labels like {a=1, b=2} as a "
                     "comma-separated string.")

    def generate_entry(self):
        cfg = self.config
        label_counter = 0
        ast = None
        answer = None
        for _ in range(200):
            ast, label_counter = _gen_seq(cfg.depth, cfg.body_max, cfg.n_lines, 0)
            total = sum(1 for _ in _assignments(ast))
            if total < 2:
                continue
            labels, nodes, IN, OUT, exit = _solve(ast)
            # self-check: the fixed-point equations must hold exactly.
            ok = all(OUT[i] == (IN[i] - nodes[i]["kill"]) | nodes[i]["gen"] for i in range(len(nodes)))
            if not ok:
                continue
            answer = labels
            break
        if answer is None:
            raise RuntimeError("reaching_definitions: failed to generate a valid instance")

        metadata = {
            "ast": ast,
            "variables": list(VARIABLES),
            "answer_labels": answer,
        }
        return Entry(metadata=metadata, answer=_answer_str(answer))

    def render_prompt(self, metadata):
        program = _render_program(metadata["ast"])
        return (
            "Below is a small imperative program. Each assignment statement carries a unique label "
            "(L0, L1, ...).\n\n"
            f"{program}\n\n"
            "A labeled assignment's definition reaches the end of the program if there is a path through "
            "the control flow (following branches and the body of while-loops, possibly zero or more times) "
            "from that assignment to the final point on which the assigned variable is not overwritten by "
            "another assignment. List every label whose definition reaches the end of the program.\n\n"
            "Answer format: the labels in ascending order, comma-separated with no spaces, for example "
            "L0,L1,L4. If no assignment reaches the end, write exactly: none"
        )

    def score_answer(self, answer, entry):
        got = _parse_answer(answer)
        if got is None:
            return 0.0
        golden = [int(l) for l in entry.metadata["answer_labels"]]
        return 1.0 if got == golden else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'reaching_definitions (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:reaching_definitions',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/reaching_definitions',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2640394,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

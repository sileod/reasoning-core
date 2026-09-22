import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'phi_sensitive_ssa_evaluation (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_language_implementation_r4/phi_sensitive_ssa_evaluation',
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


def _expr_str(e):
    if isinstance(e, int):
        return str(e)
    op, a, b = e
    sym = {"add": "+", "sub": "-", "mul": "*"}[op]
    return "(" + a + " " + sym + " " + b + ")"


def _apply(op, x, c):
    o, a, b = op
    va, vb = {"x": x, "c": c}[a], {"x": x, "c": c}[b]
    return {"add": va + vb, "sub": va - vb, "mul": va * vb}[o]


def _fresh(used):
    i = 0
    while True:
        t = "t%d" % i
        i += 1
        if t not in used:
            used.add(t)
            return t


@dataclass
class PhiConfig(Config):
    level: int = 0

    def apply_difficulty(self, level):
        self.level = level


class PhiSensitiveSSA(Task):
    summary = "Execute arithmetic SSA programs with branches, loops, and predecessor-selected phi nodes until halt; report a queried value, the phi edge taken at a step, or the first invalid operation."
    design_choice = "Queried value is the final value of a named variable, while phi-edge and invalid-op queries are separate instance types."
    config_cls = PhiConfig

    def _modes(self, level):
        if level <= 1:
            return ["value"]
        if level <= 3:
            return ["value", "value", "phi"]
        return ["value", "value", "value", "value", "phi", "invalid"]

    def generate_entry(self):
        level = self.config.level
        mode = random.choice(self._modes(level))
        for _ in range(40):
            e = self._build(mode, level)
            if e is not None:
                return e
        raise RuntimeError("failed to build instance")

    def _build(self, mode, level):
        BOUND = random.randint(2, 3 + level)
        INIT_X = random.randint(-3, 3)
        INIT_C = 0
        STEP = random.randint(1, 2)
        XOP = random.choice(
            [("add", "x", "x"), ("sub", "x", "c"), ("add", "x", "c"),
             ("mul", "x", "c"), ("add", "c", "x"), ("sub", "c", "x")])

        ntemp = 1 + level // 3
        used = {"x", "c"}
        temps = []
        for ti in range(ntemp):
            t = "t%d" % ti
            if random.random() < 0.5:
                e = random.randint(-2, 4)
            else:
                a = random.choice(sorted(used))
                b = random.choice(sorted(used))
                op = random.choice(["add", "sub", "mul"])
                e = (op, a, b)
            temps.append((t, e))
            used.add(t)
        qvar = random.choice([v for v, _ in temps] + ["x"])

        # Faithful simulation. Canonical order per body visit:
        #   header: phi merges x; if c < BOUND run body else exit.
        #   body: x = XOP(x,c); c = c + STEP; temps use new x and c.
        x = INIT_X
        c = INIT_C
        invalid = None
        phi_edges = []
        tempenv = {}
        iterations = 0
        maxiter = 100
        while c < BOUND and iterations < maxiter:
            if iterations == 0:
                phi_edges.append("b0")
                x = INIT_X
            else:
                phi_edges.append("bB")
            iterations += 1
            nx = _apply(XOP, x, c)
            nc = c + STEP
            if nx > 40 or nx < -40:
                if invalid is None:
                    invalid = "x"
            tempenv = {"x": nx, "c": nc}
            for t, e in temps:
                if isinstance(e, int):
                    val = e
                else:
                    val = _eval_expr(e, tempenv)
                if val > 40 or val < -40:
                    if invalid is None:
                        invalid = t
                tempenv[t] = val
            c = nc
            x = nx
        final_x = x

        rendered = self._render(BOUND, INIT_X, INIT_C, STEP, XOP, temps)

        if mode == "value":
            if invalid is not None:
                return None
            qval = final_x if qvar == "x" else tempenv.get(qvar)
            if qval is None or not (-20 <= qval <= 20):
                return None
            return Entry(
                metadata={"program": rendered, "mode": "value",
                          "query": qvar, "answer": qval, "level": self.config.level},
                answer=str(qval))
        if mode == "phi":
            if invalid is not None or iterations == 0:
                return None
            k = random.randint(1, iterations)
            ans = phi_edges[k - 1]
            return Entry(
                metadata={"program": rendered, "mode": "phi", "block": "bH",
                          "step": k, "answer": ans, "level": self.config.level},
                answer=ans)
        # mode == invalid
        if invalid is None:
            return None
        ans = invalid
        return Entry(
            metadata={"program": rendered, "mode": "invalid", "answer": ans,
                      "level": self.config.level},
            answer=ans)

    def _render(self, BOUND, INIT_X, INIT_C, STEP, XOP, temps):
        tlines = "; ".join(t + " = " + _expr_str(e) for t, e in temps)
        op = _apply_str(XOP)
        body = ("bB: [ x = " + op + "; c = c + " + str(STEP)
                + (("; " + tlines) if tlines else "") + " ] -> bH")
        return (
            "b0: [ c = " + str(INIT_C) + "; x = " + str(INIT_X) + " ] -> bH\n"
            "bH: [ phi x [ b0, bB ] ] -> if c < " + str(BOUND) + " then bB else bE\n"
            + body + "\n"
            "bE: [ ] -> halt"
        )

    def render_prompt(self, metadata):
        m = metadata
        head = ("This is an arithmetic SSA program (single static assignment) with a loop "
                "and a predecessor-selected phi node. 'v = expr' assigns a variable using "
                "earlier variables; 'phi x [ b0, bB ]' makes x take the value that the "
                "predecessor block actually taken beforehand produced. A block 'bN: [ ... ] "
                "-> if cond then A else B' branches, '-> T' jumps, '-> halt' stops.\n\n"
                + m["program"])
        if m["mode"] == "value":
            return head + (f"\n\nExecute the program until it halts. What is the final value "
                           f"of variable {m['query']}? Answer one integer.")
        if m["mode"] == "phi":
            return head + (f"\n\nExecute the program until it halts. On the {_ord(m['step'])} "
                           f"execution of the phi node in block {m['block']}, which "
                           f"predecessor block's edge is selected? Answer with the block "
                           f"identifier ('b0' or 'bB').")
        return head + (f"\n\nExecute the program until it halts. Which variable first takes a "
                       f"value outside [-40, 40] (this makes the program invalid)? Answer "
                       f"with the variable's name, or 'none' if no variable overflows.")

    def score_answer(self, answer, entry):
        gold = entry.answer
        if isinstance(answer, str):
            answer = answer.strip()
        else:
            answer = str(answer)
        return 1.0 if answer == gold else 0.0


def _ord(n):
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(n, "%dth" % n)


def _apply_str(op):
    o, a, b = op
    sym = {"add": "+", "sub": "-", "mul": "*"}[o]
    return "(" + a + " " + sym + " " + b + ")"


def _eval_expr(e, env):
    if isinstance(e, int):
        return e
    op, a, b = e
    va, vb = env[a], env[b]
    return {"add": va + vb, "sub": va - vb, "mul": va * vb}[op]

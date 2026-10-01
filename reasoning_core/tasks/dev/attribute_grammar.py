"""Evaluate an attribute grammar with two inherited attributes (an offset and a scoped symbol table).

Reworked from the generated attribute_grammar_evaluation (ext #4 on v8_tiny). That version had
depth 2 at levels 0-1 (one env over one leaf), a Boolean mode that a coin flip half-solves, and a
single inherited attribute. Here trees grow with the level, `let` adds a scoped environment with
shadowing (a classic inherited symbol table), and the question may target a marked inner node,
whose inherited attributes must be pushed down from the root before its value can be built up.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Entry, edict, stochastic_rounding as sround

ARITH, STRING = "integer", "string"
VARS = "xyz"
BOUND = 10_000


@dataclass
class AttributeGrammarConfig(Config):
    depth: int = 3
    min_nodes: int = 3
    max_nodes: int = 7

    def apply_difficulty(self, level):
        self.depth = 3 + sround(0.6 * level)
        self.min_nodes = 3 + 2 * level
        self.max_nodes = 7 + 3 * level


def _build(mode, depth, scope):
    """A random tree; `scope` lists the variable names bound above this node."""
    r = random.random()
    if depth <= 1 or r < 0.06:
        if scope and random.random() < 0.45:
            return ["var", random.choice(scope)]
        return ["num", random.randint(-9, 9)] if mode == ARITH else ["sym", random.choice("abcd")]
    if r < 0.32:
        return ["env", random.choice([-3, -2, -1, 1, 2, 3]), _build(mode, depth - 1, scope)]
    if r < 0.52:
        name = random.choice(VARS)
        return ["let", name, _build(mode, depth - 1, scope), _build(mode, depth - 1, scope + [name])]
    if mode == STRING:
        if r < 0.62:
            return ["rep", random.randint(2, 3), _build(mode, depth - 1, scope)]
        return ["cat", _build(mode, depth - 1, scope), _build(mode, depth - 1, scope)]
    op = random.choices(["add", "sub", "mul"], [3, 3, 1])[0]
    return [op, _build(mode, depth - 1, scope), _build(mode, depth - 1, scope)]


def _eval(node, ctx, env, out):
    """Synthesized value of node; records every node's value in `out` keyed by id(node)."""
    op = node[0]
    if op == "num":
        v = node[1] + ctx
    elif op == "sym":
        v = node[1] * (1 + abs(ctx) % 3)
    elif op == "var":
        v = env[node[1]]
    elif op == "env":
        v = _eval(node[2], ctx + node[1], env, out)
    elif op == "let":
        v = _eval(node[3], ctx, {**env, node[1]: _eval(node[2], ctx, env, out)}, out)
    elif op == "rep":
        v = _eval(node[2], ctx, env, out) * node[1]
    else:
        a, b = _eval(node[1], ctx, env, out), _eval(node[2], ctx, env, out)
        v = {"add": a + b, "sub": a - b if isinstance(a, int) else None, "mul": a * b if isinstance(a, int) else None,
             "cat": a + b}[op]
    if isinstance(v, int) and abs(v) > BOUND or isinstance(v, str) and len(v) > 40:
        raise OverflowError
    out[id(node)] = v
    return v


def _nodes(node):
    yield node
    for child in node[1:]:
        if isinstance(child, list):
            yield from _nodes(child)


def _render(node, mark):
    op = node[0]
    tag = "[Q]" if node is mark else ""
    if op == "num":
        s = f"N({node[1]})"
    elif op == "sym":
        s = f"S('{node[1]}')"
    elif op == "var":
        s = f"V({node[1]})"
    elif op in ("env", "rep"):
        s = f"{op}({node[1]}, {_render(node[2], mark)})"
    elif op == "let":
        s = f"let({node[1]}, {_render(node[2], mark)}, {_render(node[3], mark)})"
    else:
        s = f"{op}({_render(node[1], mark)}, {_render(node[2], mark)})"
    return tag + s


RULES = {
    ARITH: "- N(v): a leaf whose value is v + ctx.\n"
           "- add/sub/mul(L, R): both children inherit ctx and env; the value is L + R, L - R or L * R.\n",
    STRING: "- S('c'): a leaf whose value is the character c repeated (1 + |ctx| mod 3) times.\n"
            "- cat(L, R): both children inherit ctx and env; the value is the concatenation L R.\n"
            "- rep(k, T): the value of T repeated k times.\n",
}


class AttributeGrammar(DevTask):
    summary = ("Evaluate a parse tree under an attribute grammar with two inherited attributes, an "
               "integer offset and a scoped variable environment with shadowing, over integer or string "
               "values; report the synthesized value of the root or of a marked inner node.")
    config_cls = AttributeGrammarConfig
    task_version = 1

    def generate_entry(self):
        cfg = self.config
        mode = random.choices([ARITH, STRING], [3, 1])[0]
        tree = _build(mode, cfg.depth, [])
        nodes = list(_nodes(tree))
        if not cfg.min_nodes <= len(nodes) <= cfg.max_nodes or not any(n[0] in ("env", "let") for n in nodes):
            return None
        values = {}
        try:
            _eval(tree, 0, {}, values)
        except OverflowError:
            return None
        if any(v is None for v in values.values()):
            return None
        inner = [n for n in nodes[1:] if n[0] not in ("num", "sym", "var")]
        mark = random.choice(inner) if inner and random.random() < 0.5 else None
        value = values[id(mark if mark is not None else tree)]
        return Entry(metadata=edict(mode=mode, tree=_render(tree, mark), marked=mark is not None),
                     answer=str(value))

    def render_prompt(self, m):
        target = "the node marked [Q]" if m.marked else "the root"
        return (f"A parse tree is evaluated with an attribute grammar over {m.mode} values. Two attributes are "
                "inherited (passed down): ctx, an integer that is 0 at the root, and env, a mapping from "
                "variable names to values that is empty at the root. One attribute is synthesized (passed up): "
                "the node's value. Rules:\n"
                + RULES[m.mode] +
                "- env(k, T): T inherits ctx + k; the value is T's value.\n"
                "- let(x, E, T): E is evaluated with the current ctx and env; T inherits the current ctx and "
                "env extended with x bound to E's value (an inner let of the same name shadows the outer one); "
                "the value is T's value.\n"
                "- V(x): the value bound to x in the inherited env (ctx does not apply).\n\n"
                f"Tree:\n    {m.tree}\n\n"
                f"What is the synthesized value of {target}? Give only the value"
                + (", without quotes." if m.mode == STRING else "."))

    def score_answer(self, answer, entry):
        return float(str(answer).strip().strip("'\"") == entry.answer)

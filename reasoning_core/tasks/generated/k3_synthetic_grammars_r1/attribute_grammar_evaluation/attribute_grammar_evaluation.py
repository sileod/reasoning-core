import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

ARITH = "arith"
BOOL = "bool"
STRING = "string"
MODES = (ARITH, BOOL, STRING)


def _leaf(mode):
    if mode == ARITH:
        return ["num", random.randint(-9, 9)]
    if mode == BOOL:
        return ["cmp", random.randint(-6, 6)]
    return ["sym", random.choice("abcdxy")]


def _build(mode, depth, env_range):
    if depth <= 1:
        return _leaf(mode)
    r = random.random()
    if mode == STRING and r < 0.18:
        return ["rep", random.randint(1, 3), _build(mode, depth - 1, env_range)]
    if r < 0.42:
        return ["env", random.randint(-env_range, env_range), _build(mode, depth - 1, env_range)]
    if mode == ARITH:
        op = random.choice(["add", "mul", "sub"])
        return [op, _build(mode, depth - 1, env_range), _build(mode, depth - 1, env_range)]
    if mode == BOOL:
        if random.random() < 0.3:
            return ["not", _build(mode, depth - 1, env_range)]
        op = random.choice(["and", "or"])
        return [op, _build(mode, depth - 1, env_range), _build(mode, depth - 1, env_range)]
    return ["cat", _build(mode, depth - 1, env_range), _build(mode, depth - 1, env_range)]


def _count_env(node):
    if node[0] == "env":
        return 1 + _count_env(node[2])
    if node[0] == "rep":
        return _count_env(node[2])
    if node[0] == "not":
        return _count_env(node[1])
    if node[0] in ("num", "cmp", "sym"):
        return 0
    return _count_env(node[1]) + _count_env(node[2])


def _evaluate(node, mode, ctx):
    op = node[0]
    if op == "num":
        return node[1] + ctx
    if op == "cmp":
        return node[1] > ctx
    if op == "sym":
        return node[1] * (1 + abs(ctx) % 3)
    if op == "env":
        return _evaluate(node[2], mode, ctx + node[1])
    if op == "rep":
        return _evaluate(node[2], mode, ctx) * node[1]
    if op == "add":
        return _evaluate(node[1], mode, ctx) + _evaluate(node[2], mode, ctx)
    if op == "mul":
        return _evaluate(node[1], mode, ctx) * _evaluate(node[2], mode, ctx)
    if op == "sub":
        return _evaluate(node[1], mode, ctx) - _evaluate(node[2], mode, ctx)
    if op == "and":
        return _evaluate(node[1], mode, ctx) and _evaluate(node[2], mode, ctx)
    if op == "or":
        return _evaluate(node[1], mode, ctx) or _evaluate(node[2], mode, ctx)
    if op == "not":
        return not _evaluate(node[1], mode, ctx)
    if op == "cat":
        return _evaluate(node[1], mode, ctx) + _evaluate(node[2], mode, ctx)
    raise ValueError(op)


def _render_node(node, mode):
    op = node[0]
    if op == "num":
        return f"N({node[1]})"
    if op == "cmp":
        return f"C({node[1]})"
    if op == "sym":
        return f"S('{node[1]}')"
    if op == "env":
        return f"env({node[1]}, {_render_node(node[2], mode)})"
    if op == "rep":
        return f"rep({node[1]}, {_render_node(node[2], mode)})"
    if op == "not":
        return f"not({_render_node(node[1], mode)})"
    return f"{op}({_render_node(node[1], mode)}, {_render_node(node[2], mode)})"


def _format_answer(value, mode):
    if mode == BOOL:
        return "true" if value else "false"
    return str(value)


def score_answer(answer, entry):
    mode = entry.metadata["mode"]
    gold = entry.answer
    if not isinstance(answer, str):
        return 0.0
    a = answer.strip()
    if mode == BOOL:
        return 1.0 if a.lower() in (gold, ("true" if gold == "true" else "false")) else 0.0
    if mode == ARITH:
        try:
            return 1.0 if int(a) == int(gold) else 0.0
        except ValueError:
            return 0.0
    return 1.0 if a == gold else 0.0


@dataclass
class AttributeGrammarConfig(Config):
    depth: int = 2
    env_range: int = 2

    def apply_difficulty(self, level):
        self.depth = 2 + (level * 7) // 10
        self.env_range = 2 + level


class AttributeGrammarEvaluation(Task):
    summary = (
        "Decorate a random parse tree with a small attribute grammar of synthesized and "
        "inherited equations over arithmetic, Boolean, and string domains (per-instance "
        "domain), where inherited context folds from the root into leaf bases; compute the "
        "root's synthesized value and report it as an integer, true/false, or exact string."
    )
    config_cls = AttributeGrammarConfig
    task_version = 2

    def generate_entry(self):
        depth = self.config.depth
        env_range = self.config.env_range
        for _ in range(200):
            mode = random.choice(MODES)
            if mode == STRING and random.random() < 0.5:
                mode = random.choice((ARITH, BOOL))
            node = _build(mode, depth, env_range)
            if _count_env(node) == 0:
                continue
            value = _evaluate(node, mode, 0)
            if mode == ARITH and not isinstance(value, int):
                continue
            if mode == STRING and not isinstance(value, str):
                continue
            return Entry(
                metadata={
                    "mode": mode,
                    "tree": node,
                    "value": value,
                },
                answer=_format_answer(value, mode),
            )
        raise RuntimeError("failed to generate attribute grammar instance")

    def render_prompt(self, metadata):
        mode = metadata["mode"]
        body = {
            ARITH: (
                "An arithmetic expression is built from the following parse tree. Each node "
                "carries two attributes. Inherited 'ctx' starts at 0 at the root and flows "
                "down the tree; synthesized value flows up. The rules for this grammar are:\n"
                "- N(v): a leaf emitting v + ctx\n"
                "- env(k, T): the child T runs with ctx += k and contributes its value\n"
                "- add/mul/sub(L, R): both children inherit the same ctx; the node value is "
                "L + R, L * R, or L - R respectively.\n"
                "Evaluate the grammar and report the root's synthesized value."
            ),
            BOOL: (
                "A Boolean expression is built from the following parse tree. Inherited 'ctx' "
                "starts at 0 at the root and flows down; synthesized value flows up. Rules:\n"
                "- C(v): a leaf emitting (v > ctx)\n"
                "- env(k, T): the child T runs with ctx += k and contributes its value\n"
                "- and/or(L, R): both children inherit the same ctx; the node value is the "
                "logical AND or OR.\n"
                "- not(T): logical NOT of the child.\n"
                "Evaluate the grammar and report the root's value as exactly 'true' or 'false'."
            ),
            STRING: (
                "A string is built from the following parse tree. Inherited 'ctx' starts at 0 "
                "at the root and flows down; synthesized value flows up. Rules:\n"
                "- S('c'): a leaf emitting the character 'c' repeated (1 + |ctx| mod 3) times\n"
                "- env(k, T): the child T runs with ctx += k and contributes its value\n"
                "- cat(L, R): concatenation, both children inherit the same ctx.\n"
                "- rep(k, T): the child's string repeated k times.\n"
                "Evaluate the grammar and report the root's exact resulting string."
            ),
        }[mode]
        return (
            f"{body}\n\n"
            f"Parse tree:\n\n"
            f"    {_render_node(metadata['tree'], mode)}\n\n"
            f"What is the root's synthesized value? Give only the answer, nothing else."
        )


TASK_META = {'parent_source_id': None,
 'idea': 'attribute_grammar_evaluation (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_synthetic_grammars_r1/attribute_grammar_evaluation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1140349348,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

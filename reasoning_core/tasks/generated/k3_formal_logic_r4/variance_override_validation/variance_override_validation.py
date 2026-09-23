import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {
    'parent_source_id': None,
    'idea': 'variance_override_validation (variant 1 of 3)',
    'hypothesis': 'P007',
    'changes': 'new task in '
               'reasoning_core/tasks/generated/k3_formal_logic_r4/variance_override_validation',
    'generation': {
        'provider_name': 'albert',
        'model_name': 'deepseek-v4-flash',
        'harness_name': 'opencode',
        'harness_version': '1.18.32',
        'agent_name': 'task-search-worker',
        'settings': {
            'variant': None,
            'requested_seed': 1139467751,
            'seed_forwarded': True,
            'temperature': None,
            'top_p': None,
            'pure': True,
            'max_steps': 56,
            'timeout_seconds': 1800,
            'sandbox': {'name': 'bubblewrap',
                        'version': 'bubblewrap 0.8.0'}}}}

ATOMS = ['Int', 'Bool', 'String', 'Float']

_POL_LABEL = {'C': 'covariant', 'K': 'contravariant', 'I': 'invariant'}


def _combine(pols):
    c = any(p == 'C' for p in pols)
    k = any(p == 'K' for p in pols)
    i = any(p == 'I' for p in pols)
    if i or (c and k):
        return 'I'
    if c:
        return 'C'
    if k:
        return 'K'
    return None


@dataclass
class VarianceOverrideConfig(Config):
    depth: int = 2
    alias_count: int = 1

    def apply_difficulty(self, level):
        self.depth = 2 + level
        self.alias_count = 1 + (level // 2)


class VarianceOverrideValidation(Task):
    summary = ("Track positive, negative, and invariant polarity through nested generic "
               "constructors, function arrows, and aliases; report a queried parameter's "
               "allowed polarity or the first occurrence that breaks an override.")
    config_cls = VarianceOverrideConfig
    design_choice = ("Represent each type constructor as a fixed set of polarity rules "
                     "(e.g., covariant, contravariant, invariant) and ask for the polarity "
                     "of a specific parameter index after expanding aliases and following "
                     "arrows.")

    def generate_entry(self):
        cfg = self.config
        tree = self._make_type(cfg.depth + 1)
        pos = self._random_position(tree)

        pols = self._trace(tree, pos)
        combined = _combine(pols)
        ans = _POL_LABEL.get(combined, 'covariant')

        rendered, aliases = self._render(tree, {}, {})
        aliases = dict(sorted(aliases.items()))

        ctx = {
            'aliases': aliases,
            'base': rendered,
            'position': tuple(pos),
            'polarity': ans,
        }
        return Entry(metadata=ctx, answer=ans)

    def _make_type(self, depth):
        if depth <= 0:
            return random.choice(ATOMS)
        k = random.random()
        if k < 0.42:
            return (random.choice(['List', 'Set', 'Seq']),
                    self._make_type(depth - 1))
        if k < 0.67:
            return ('Dict', random.choice(ATOMS), self._make_type(depth - 1))
        return ('->', self._make_type(depth - 1), self._make_type(depth - 1))

    def _random_position(self, tree):
        pos = []
        node = tree
        guard = 0
        while isinstance(node, tuple) and guard < 30:
            if node[0] == '->':
                idx = 1 if random.random() < 0.5 else 2
            elif node[0] == 'Dict':
                idx = 1 if random.random() < 0.5 else 2
            else:
                idx = 1
            pos.append(idx)
            node = node[idx]
            guard += 1
            if isinstance(node, tuple) and random.random() < 0.55:
                continue
            break
        return tuple(pos)

    def _render(self, tree, aliases, bound, is_root=True):
        if isinstance(tree, str):
            return tree, aliases
        key = self._render_full_key(tree)
        if not is_root and key in bound:
            return bound[key], aliases
        if not is_root:
            inner, aliases = self._render_plain(tree, aliases)
            name = f"A{len(bound)}"
            bound[key] = name
            aliases[name] = inner
            return name, aliases
        new_parts = []
        for child in tree[1:]:
            part, aliases = self._render(child, aliases, bound, is_root=False)
            new_parts.append(part)
        if tree[0] == 'Dict':
            s = f"Dict<{new_parts[0]},{new_parts[1]}>"
        elif tree[0] == '->':
            s = f"({new_parts[0]} -> {new_parts[1]})"
        else:
            s = f"{tree[0]}<{new_parts[0]}>"
        return s, aliases

    def _render_plain(self, tree, aliases):
        if isinstance(tree, str):
            return tree, aliases
        new_parts = []
        for child in tree[1:]:
            part, aliases = self._render_plain(child, aliases)
            new_parts.append(part)
        if tree[0] == 'Dict':
            s = f"Dict<{new_parts[0]},{new_parts[1]}>"
        elif tree[0] == '->':
            s = f"({new_parts[0]} -> {new_parts[1]})"
        else:
            s = f"{tree[0]}<{new_parts[0]}>"
        return s, aliases

    def _render_full_key(self, tree):
        if isinstance(tree, str):
            return tree
        return "(" + "|".join(self._render_full_key(c) for c in tree) + ")"

    def _trace(self, tree, pos):
        pols = []
        node = tree
        for step in pos:
            if not isinstance(node, tuple):
                break
            idx = int(step)
            ctor = node[0]
            if ctor in ('List', 'Set', 'Seq'):
                p = 'C'
            elif ctor == 'Dict':
                p = 'I' if idx == 1 else 'C'
            elif ctor == '->':
                p = 'K' if idx == 1 else 'C'
            else:
                p = 'C'
            pols.append(p)
            node = node[idx]
        return pols

    def render_prompt(self, metadata):
        alias_str = ""
        if metadata['aliases']:
            lines = [f"{n} = {b}" for n, b in metadata['aliases'].items()]
            alias_str = "Aliases:\n" + "\n".join(lines) + "\n\n"
        pos = metadata['position']
        pos_str = ".".join(str(i) for i in pos)
        return (f"{alias_str}"
                f"We define variance rules: List, Set and Seq keep their parameter "
                f"covariant; Dict keeps its key invariant and its value covariant; in a "
                f"function A -> B, A is contravariant and B is covariant. Combining "
                f"polarities on one position: any invariant makes it invariant, and a mix "
                f"of covariant and contravariant is invariant.\n"
                f"Consider the type {metadata['base']}. Follow the 0-indexed child path "
                f"{pos_str} from the root, expanding any named alias you meet as the type "
                f"it stands for. Report the effectively allowed polarity at the reached "
                f"parameter using exactly one of the words covariant, contravariant, or "
                f"invariant; write only that single word.")

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        answer = answer.strip().lower()
        return 1.0 if answer == gold else 0.0

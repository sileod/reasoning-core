import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'synchronous_tuple_derivation (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_parsing_and_agreement_r4/synchronous_tuple_derivation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_SYMBOLS = ["a", "b", "c", "d", "e", "f", "g", "h", "x", "y", "z"]

design_choice = "The derivation includes nested parentheses that group components; the requested output is a specific component referenced by its original index after multiple wrapping and interleaving steps."


def _render(components):
    return "(" + ", ".join(components) + ")"


def _interleave(a, b):
    out = []
    for i in range(max(len(a), len(b))):
        if i < len(a):
            out.append(a[i])
        if i < len(b):
            out.append(b[i])
    return out


def _wrap(comp, marker):
    return marker + comp + marker


@dataclass
class SyncTupleConfig(Config):
    init_components: int = 4
    wrap_steps: int = 0
    interleave: bool = False

    def apply_difficulty(self, level):
        self.init_components = stochastic_rounding(4 + level)
        self.wrap_steps = 2 + level
        self.interleave = level >= 2


def _make_step(cur, cfg):
    markers = ["[", "{", "<", "|"]
    action = random.random()
    if cfg.interleave and action < 0.35 and len(cur) >= 4 and len(cur) % 2 == 0:
        mid = len(cur) // 2
        return _interleave(cur[:mid], cur[mid:]), ("interleave",)
    if action < 0.75:
        idx = random.randrange(len(cur))
        marker = markers[random.randrange(len(markers))]
        nxt = list(cur)
        nxt[idx] = _wrap(nxt[idx], marker)
        return nxt, ("wrap", idx, marker)
    pos = random.randrange(len(cur) + 1)
    new = random.choice(_SYMBOLS)
    nxt = list(cur)
    nxt.insert(pos, new)
    return nxt, ("insert", pos, new)


class SyncTupleDerivationV2(Task):
    task_name = "sync_tuple_derivation"
    summary = "Execute supplied derivations whose productions transform tuples of strings by permuting, interleaving, or wrapping components; track linked occurrences through nesting and return the requested output component."
    design_choice = "The derivation includes nested parentheses that group components; the requested output is a specific component referenced by its original index after multiple wrapping and interleaving steps."
    config_cls = SyncTupleConfig

    def generate_entry(self):
        cfg = self.config
        n = max(2, cfg.init_components)
        for _ in range(200):
            components = [random.choice(_SYMBOLS) for _ in range(n)]
            cur = list(components)
            steps = []
            for _ in range(cfg.wrap_steps):
                cur, desc = _make_step(cur, cfg)
                steps.append(desc)
            if len(cur) >= 1:
                break
        else:
            raise RuntimeError("could not build derivation")
        query_index = random.randrange(n)
        answer = components[query_index]
        assert isinstance(answer, str) and answer in _SYMBOLS
        return Entry(
            metadata={
                "components": components,
                "query_index": query_index,
                "steps": steps,
            },
            answer=str(answer),
        )

    def render_prompt(self, metadata):
        components = metadata["components"]
        idx = metadata["query_index"]
        steps = metadata["steps"]
        lines = [
            f"We start with the tuple of components {_render(components)}. "
            "Perform these synchronous derivation steps, tracking the position of every component as it moves or changes, in order:"
        ]
        for i, desc in enumerate(steps, 1):
            if desc[0] == "interleave":
                lines.append(f"{i}. Interleave the first half of the current tuple with the second half, taking one component from each in alternation beginning with the first half.")
            elif desc[0] == "wrap":
                lines.append(f"{i}. Enclose the component at position {desc[1]} of the current tuple by placing the two markers {desc[2]} immediately around its text.")
            else:
                lines.append(f"{i}. Insert the new component {desc[2]} at position {desc[1]} of the current tuple, shifting later components one position right.")
        lines.append(
            f"After all steps, what is the text of the component that originated at index "
            f"{idx} of the initial tuple, with any wrapping markers removed? "
            f"Give a single string with no parentheses or punctuation:"
        )
        return "\n".join(lines)

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'layered_interval_exposure (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r4/layered_interval_exposure',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class LayerExposureConfig(Config):
    n_layers: int = 3
    span: int = 10
    n_ops: int = 2

    def apply_difficulty(self, level):
        self.n_layers = 2 + level
        self.span = 6 + 2 * level
        self.n_ops = 1 + level


class LayeredIntervalExposure(Task):
    summary = "Maintain visible values beneath prioritized interval layers through activation, removal, and priority changes; reveal covered layers when higher ones disappear and return maximal constant visible spans."
    design_choice = "Answer is a canonical list of disjoint maximal spans, each as [start,end] inclusive, ordered ascending, with the underlying layer id appended when the visible value is constant over that span."
    config_cls = LayerExposureConfig

    def generate_entry(self):
        n = self.config.n_layers
        span = self.config.span
        n_ops = self.config.n_ops
        layers = []
        for i in range(n):
            lo = random.randint(0, span - 2)
            hi = random.randint(lo + 1, span - 1)
            prio = random.randint(1, 10)
            active = True
            layers.append({"id": i, "lo": lo, "hi": hi, "prio": prio, "active": active})
        ops = []
        for _ in range(n_ops):
            kind = random.choice(["remove", "activate", "prioritize"])
            layers_available = [l for l in layers if l["active"]]
            layers_inactive = [l for l in layers if not l["active"]]
            if kind == "remove":
                if len(layers_available) <= 1:
                    kind = "activate"
                else:
                    l = random.choice(layers_available)
                    ops.append({"kind": "remove", "id": l["id"]})
                    l["active"] = False
                    continue
            if kind == "activate":
                if not layers_inactive:
                    continue
                l = random.choice(layers_inactive)
                ops.append({"kind": "activate", "id": l["id"]})
                l["active"] = True
            else:
                l = random.choice(layers_available)
                new_prio = random.randint(1, 10)
                ops.append({"kind": "prioritize", "id": l["id"], "prio": new_prio})
                l["prio"] = new_prio

        init_layers = [{"id": l["id"], "lo": l["lo"], "hi": l["hi"], "prio": l["prio"]} for l in layers]
        visible = self._compute_visible(layers, span)
        metadata = {
            "layers": init_layers,
            "ops": ops,
            "span": span,
            "visible": visible,
            "answer": self._render_answer(visible),
        }
        answer = metadata["answer"]
        return Entry(metadata=metadata, answer=answer)

    def _compute_visible(self, layers, span):
        visible = [None] * span
        for pos in range(span):
            best = None
            best_prio = None
            for l in layers:
                if not l["active"]:
                    continue
                if l["lo"] <= pos <= l["hi"]:
                    if best is None or l["prio"] > best_prio:
                        best = l["id"]
                        best_prio = l["prio"]
            visible[pos] = best
        return visible

    def _render_answer(self, visible):
        spans = []
        i = 0
        n = len(visible)
        while i < n:
            if visible[i] is None:
                i += 1
                continue
            j = i
            while j + 1 < n and visible[j + 1] == visible[i]:
                j += 1
            spans.append([i, j, visible[i]])
            i = j + 1
        if not spans:
            return "none"
        return ";".join(f"[{s[0]},{s[1]}]:{s[2]}" for s in spans)

    def render_prompt(self, metadata):
        lines = []
        lines.append("We maintain a line of positions 0..%(span)d. There are %(n)d interval layers. layer X is [lo,hi] inclusive and has priority P; a higher priority covers a lower one. The visible value at a position is the id of the highest-priority active layer covering it, or empty if none." % {"span": metadata["span"], "n": len(metadata["layers"])})
        for l in sorted(metadata["layers"], key=lambda x: x["id"]):
            lines.append(f"layer {l['id']} is [{l['lo']},{l['hi']}] at priority {l['prio']}.")
        for op in metadata["ops"]:
            if op["kind"] == "remove":
                lines.append(f"remove layer {op['id']}.")
            elif op["kind"] == "activate":
                lines.append(f"activate layer {op['id']}.")
            else:
                lines.append(f"layer {op['id']} changes priority to {op['prio']}.")
        lines.append("After the operations, the final visible value across the line is grouped into maximal constant spans where the visible value is that of a single layer. Report those spans in ascending order, each as [start,end] followed by the layer id, segments separated by ';'. If the whole line is empty, answer exactly 'none'.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        return 1.0 if answer == entry.answer else 0.0

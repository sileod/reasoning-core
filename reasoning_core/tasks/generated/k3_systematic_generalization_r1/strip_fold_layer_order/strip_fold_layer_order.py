import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class StripFoldConfig(Config):
    segments: int = 4
    folds: int = 1

    def apply_difficulty(self, level):
        self.segments = stochastic_rounding(4 + level * 2)
        self.folds = stochastic_rounding(1 + level)


class StripFoldLayerOrder(Task):
    summary = "Apply a signed mountain/valley fold sequence to a strip of labeled segments, maintaining orientation and layer order, and return the top-to-bottom segment order in a queried stack."
    design_choice = "Represent the strip as a list of segment labels, apply folds by reversing and flipping sublists, and output the final top-to-bottom labels as a comma-separated string."
    config_cls = StripFoldConfig

    def generate_entry(self):
        n = self.config.segments
        f = self.config.folds
        labels = list(range(1, n + 1))
        random.shuffle(labels)
        strip = [[lab] for lab in labels]

        folds = []
        for _ in range(f):
            if len(strip) < 2:
                break
            cut = random.randint(1, len(strip) - 1)
            direction = random.choice(["mountain", "valley"])
            folds.append({"fold": len(folds) + 1, "cut": cut, "direction": direction})
            left = strip[:cut]
            right = strip[cut:]
            if direction == "valley":
                # top part folds onto bottom part; the folded-on-top block is reversed
                top = [list(reversed(seg)) for seg in reversed(left)] + right
            else:
                # bottom part folds onto top part; the folded-on-top block is reversed
                top = [list(reversed(seg)) for seg in reversed(right)] + left
            strip = top

        top_to_bottom = [seg[0] for seg in strip]
        for seg in strip:
            assert len(set(seg)) == len(seg), "segment identity repeated"
        assert [lab for seg in strip for lab in seg].__len__() == n

        all_labs = [lab for seg in strip for lab in seg]
        assert sorted(all_labs) == sorted(labels), "lost a segment"

        answer = ",".join(str(lab) for lab in top_to_bottom)
        metadata = {
            "labels": labels,
            "folds": folds,
            "top_to_bottom": top_to_bottom,
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        labels = metadata["labels"]
        folds = metadata["folds"]
        lines = [
            "We have a one-dimensional strip of labeled segments placed side by side, "
            "flat at the bottom of a single stack, with layer order equal to the listed order "
            "(the first listed segment is on top)."
        ]
        lines.append("Initial segment order (top to bottom): " + ", ".join(str(l) for l in labels) + ".")
        lines.append("Now apply folds, in order. A fold at cut position c divides the current "
                     "strip (counting segments from the top) into a top part and a bottom part. "
                     "Applying a mountain fold folds the bottom part up onto the top part; applying "
                     "a valley fold folds the top part down onto the bottom part. The block that is "
                     "folded on top is turned over, which reverses the order of its segments and "
                     "mirrors the layers within each of its segments, so that it lands on top in "
                     "that reversed order.")
        for fold in folds:
            lines.append(f"Fold {fold['fold']}: {fold['direction']} fold at cut position "
                         f"{fold['cut']} (counting segments from the top).")
        lines.append("After all folds, report the segment labels from top to bottom. "
                     "Answer with a comma-separated list of integers, no spaces.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        expected = entry.answer
        normalized = "".join(str(answer).split()).strip()
        if normalized == expected:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'strip_fold_layer_order (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_systematic_generalization_r1/strip_fold_layer_order',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

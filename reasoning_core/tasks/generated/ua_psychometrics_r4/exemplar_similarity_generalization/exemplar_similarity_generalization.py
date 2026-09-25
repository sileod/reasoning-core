import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding as sround

TASK_META = {'parent_source_id': None,
 'idea': 'exemplar_similarity_generalization (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_psychometrics_r4/exemplar_similarity_generalization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class ExemplarSimGenConfig(Config):
    n_dims: int = 3
    n_missing: int = 0
    n_per_cat: int = 2
    val_max: int = 3
    min_weight: float = 0.5
    weight_span: float = 1.0
    margin: float = 0.15
    max_attempts: int = 200

    def apply_difficulty(self, level):
        self.n_dims = sround(3 + 0.8 * level)
        self.n_per_cat = sround(2 + 0.5 * level)
        self.n_missing = min(sround(0.6 * level), self.n_dims - 2)
        self.val_max = sround(3 + 0.7 * level)
        self.weight_span = 1.0 + 0.25 * level


def _contribution(kernel, weight, diff, val_max):
    if kernel == "linear":
        return weight * max(0.0, 1.0 - abs(diff) / float(val_max))
    return weight * (0.5 ** abs(diff))


def _category_scores(weights, exemplars, stimulus, missing, kernel, val_max):
    sums = {"A": 0.0, "B": 0.0}
    for label, values in exemplars:
        total = 0.0
        for d, w in enumerate(weights):
            if d in missing:
                continue
            total += _contribution(kernel, w, values[d] - stimulus[d], val_max)
        sums[label] += total
    return sums


class ExemplarSimilarityGeneralization(Task):
    summary = ("Classify a novel stimulus by summed feature-weighted similarity to remembered "
               "exemplars under two fixed labels; vary feature weights, missing dimensions, "
               "exemplar counts, and linear/exponential similarity kernels; answer the winning "
               "category A or B.")
    config_cls = ExemplarSimGenConfig

    def generate_entry(self):
        cfg = self.config
        kernel = random.choice(["linear", "exponential"])
        for _ in range(cfg.max_attempts):
            weights = [round(random.uniform(cfg.min_weight,
                                            cfg.min_weight + cfg.weight_span), 1)
                       for _ in range(cfg.n_dims)]
            novel = [random.randint(0, cfg.val_max) for _ in range(cfg.n_dims)]
            missing = set(sorted(random.sample(range(cfg.n_dims), cfg.n_missing)))
            exemplars = []
            for label in ("A", "B"):
                for _ in range(cfg.n_per_cat):
                    exemplars.append((label,
                                      [random.randint(0, cfg.val_max)
                                       for _ in range(cfg.n_dims)]))
            random.shuffle(exemplars)
            sums = _category_scores(weights, exemplars, novel, missing, kernel, cfg.val_max)
            for s in sums.values():
                assert s >= 0.0, f"similarity sum must be non-negative, got {s}"
            if abs(sums["A"] - sums["B"]) >= cfg.margin:
                answer = "A" if sums["A"] > sums["B"] else "B"
                stim = [None if d in missing else v for d, v in enumerate(novel)]
                metadata = {
                    "weights": weights,
                    "kernel": kernel,
                    "val_max": cfg.val_max,
                    "exemplars": [{"label": lbl, "values": vals} for lbl, vals in exemplars],
                    "stimulus": stim,
                    "sumA": round(sums["A"], 4),
                    "sumB": round(sums["B"], 4),
                }
                return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("exemplar_similarity_generalization: no instance with a "
                           "sufficient margin after bounded attempts")

    def render_prompt(self, metadata):
        dims = range(len(metadata["weights"]))
        whdr = "  ".join(f"d{d}" for d in dims)
        wrow = "  ".join(f"{w:g}" for w in metadata["weights"])
        lines = [
            "Remembered exemplars:",
            f"dim     {whdr}",
        ]
        for ex in metadata["exemplars"]:
            vals = "  ".join(f"{v}" for v in ex["values"])
            lines.append(f"label {ex['label']}   {vals}")
        lines.append("")
        lines.append("Feature weights (one per dimension, applied to every exemplar):")
        lines.append(f"        {wrow}")
        lines.append("")
        lines.append("Novel stimulus "
                     "(a '?' marks a dimension whose value was not observed, so it is skipped):")
        svals = "  ".join("?" if v is None else str(v) for v in metadata["stimulus"])
        lines.append(f"        {svals}")
        lines.append("")
        kernel_desc = {
            "linear": ("For an observed dimension d with exemplar value m and stimulus value x, "
                       "its similarity contribution is weight_d * max(0, 1 - |x - m| / "
                       f"{metadata['val_max']})."),
            "exponential": ("For an observed dimension d with exemplar value m and stimulus value "
                            "x, its similarity contribution is weight_d * 0.5^|x - m|."),
        }[metadata["kernel"]]
        lines.append(f"Similarity kernel: {kernel_desc}")
        lines.append("Sum an exemplar's contributions over observed dimensions to get its "
                     "similarity to the stimulus.")
        lines.append("Category score = the summed similarity of ALL exemplars of that category.")
        lines.append("Classify the stimulus into the category with the higher summed score; on a "
                     "tie, choose A.")
        lines.append("Give only the winning category label.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        ref = str(entry["answer"]).strip()
        if answer is None:
            return 0.0
        ans = str(answer).strip()
        if ans == ref:
            return 1.0
        return 0.0

    def balancing_key(self, problem):
        return str(problem.answer)

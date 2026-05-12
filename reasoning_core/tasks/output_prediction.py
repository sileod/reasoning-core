import random
import re
from dataclasses import dataclass
from typing import Any

from easydict import EasyDict as edict
from nltk.metrics.distance import edit_distance

from reasoning_core.template import Task, Problem, Config

from ._gramforge_helpers.grammars import pygram_grammar
from ._gramforge_helpers.prerequisites import (
    Fuzzer, TrivialityFilter, run_sandboxed, ASTMetrics,
)
from ._gramforge_helpers.pygram_adapter import (
    add_entry_call_str, PYGRAM_TRIVIALITY_POLICY,
)


# ── Config with disjoint per-level ranges ────────────────────────────────────
def _level_complexity_score(metrics, code, num_output_lines, num_output_chars):
    """Combined complexity score; higher = harder."""
    return (
        metrics.ast_height * 1.0
        + metrics.num_loops * 3.0
        + metrics.num_conditionals * 1.5
        + metrics.nesting_depth * 2.0
        + code.count("print(") * 1.0
        + num_output_lines * 0.5
        + min(num_output_chars / 20.0, 5.0)
    )

# Per-level required score band (disjoint)
_level_score_bands = {
    0: (0, 12),
    1: (12, 20),
    2: (20, 30),
    3: (30, 50),
}

@dataclass
class OutputPredictionConfig(Config):
    timeout: float = 3.0

    # Disjoint depth bands — set the fuzzer's generation envelope.
    _depth_ranges: tuple = ((5, 8), (8, 11), (11, 13), (13, 16))

    # Per-level complexity score band; a record qualifies if its
    # combined complexity score lies in this range.
    _score_bands: tuple = ((0, 12), (12, 20), (20, 25), (25, 50))

    # Absolute output caps (anti-pathology, not difficulty knobs)
    _min_output_chars_per_level: tuple = (1, 5, 15, 30)
    _max_output_chars_per_level: tuple = (60, 150, 300, 500)
    _max_output_lines_per_level: tuple = (4, 8, 14, 25)

    min_depth: Any = 6
    max_depth: Any = 9
    score_min: Any = 0
    score_max: Any = 12
    min_output_chars: Any = 1
    max_output_chars: Any = 60
    max_output_lines: Any = 4

    def update(self, c):
        idx = max(0, min(self.level, len(self._depth_ranges) - 1))
        self.min_depth, self.max_depth = self._depth_ranges[idx]
        self.score_min, self.score_max = self._score_bands[idx]
        self.min_output_chars = self._min_output_chars_per_level[idx]
        self.max_output_chars = self._max_output_chars_per_level[idx]
        self.max_output_lines = self._max_output_lines_per_level[idx]



# ── Output suitability (config-driven) ───────────────────────────────────────

def _is_suitable_output(stdout: str, cfg) -> bool:
    s = stdout.strip()
    if not s:
        return False
    n_lines = len(s.splitlines())
    if n_lines < cfg.min_output_lines or n_lines > cfg.max_output_lines:
        return False
    n_chars = len(s)
    if n_chars < cfg.min_output_chars or n_chars > cfg.max_output_chars:
        return False
    return True


def _has_min_structure(metrics, code: str, cfg) -> bool:
    if metrics.num_loops < cfg.min_loops:
        return False
    if code.count("print(") < cfg.min_total_prints:
        return False
    return True


# ── Scoring helper (self-free) ────────────────────────────────────────────────

def _prepr(s) -> str:
    s = str(s).strip()
    s = re.sub(r'\s+', ' ', s)
    s = s.replace('"', '').replace("'", '')
    return s


# ── Task ──────────────────────────────────────────────────────────────────────

class OutputPrediction(Task):
    task_name = "output_prediction"
    balancing_key_ratio = 0.2

    def __init__(self, config=None):
        super().__init__(
            config=config if config is not None else OutputPredictionConfig()
        )
        self._fuzzer = Fuzzer(
            grammar_fn=pygram_grammar,
            min_depth=self.config.min_depth,
            max_depth=self.config.max_depth,
        )
        self._triviality = TrivialityFilter(PYGRAM_TRIVIALITY_POLICY)

    def _refresh_fuzzer(self):
        if (self._fuzzer.min_depth != self.config.min_depth
                or self._fuzzer.max_depth != self.config.max_depth):
            self._fuzzer = Fuzzer(
                grammar_fn=pygram_grammar,
                min_depth=self.config.min_depth,
                max_depth=self.config.max_depth,
            )

    def _level_complexity_score(metrics, code, num_output_lines, num_output_chars):
        return (
            metrics.ast_height * 1.0
            + metrics.num_loops * 3.0
            + metrics.num_conditionals * 1.5
            + metrics.nesting_depth * 2.0
            + code.count("print(") * 1.0
            + num_output_lines * 0.5
            + min(num_output_chars / 20.0, 5.0)
        )


    def generate(self) -> Problem:
        self._refresh_fuzzer()
        rng = random.Random()
        cfg = self.config

        max_attempts = 100 + 80 * cfg.level

        for _ in range(max_attempts):
            try:
                node = self._fuzzer.sample(1, seed=rng.randint(0, 2**31))[0]
                raw_code = node @ 'py'
            except Exception:
                continue

            if self._triviality.is_trivial(raw_code):
                continue

            prepared = add_entry_call_str(raw_code, rng)
            result = run_sandboxed(prepared, timeout=cfg.timeout)
            if not result.success:
                continue

            stdout = result.stdout.strip()
            if not stdout:
                continue
            n_lines = len(stdout.splitlines())
            n_chars = len(stdout)

            # Cheap absolute caps
            if n_chars < cfg.min_output_chars:
                continue
            if n_chars > cfg.max_output_chars:
                continue
            if n_lines > cfg.max_output_lines:
                continue

            # Combined complexity score
            metrics = ASTMetrics.from_code(raw_code)
            score = _level_complexity_score(metrics, raw_code, n_lines, n_chars)

            if not (cfg.score_min <= score < cfg.score_max):
                continue

            metadata = edict(
                code=prepared,
                correct_output=stdout,
                num_output_lines=n_lines,
                num_output_chars=n_chars,
                complexity_score=score,
                grammar='pygram',
                metrics=metrics.to_dict(),
                elapsed_ms=result.elapsed_ms,
            )
            return Problem(metadata=metadata, answer=stdout)

        raise RuntimeError(
            f"OutputPrediction: failed after {max_attempts} attempts at level {cfg.level}"
        )


    def prompt(self, metadata) -> str:
        return (
            f"Predict the exact output printed to stdout by the following "
            f"Python program.\n\n"
            f"```python\n{metadata.code}\n```\n\n"
            f"Return only the printed output string, with no extra commentary."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0
        reference = entry['answer']
        a = _prepr(answer)
        r = _prepr(reference)
        dist = edit_distance(a, r)
        return 1 / (1 + dist / (len(r) ** 0.5 + 1))

    def balancing_key(self, problem):
        out = str(problem.answer)
        n = len(out)
        if n <= 2:
            return 'short'
        if n <= 8:
            return 'medium'
        return 'long'

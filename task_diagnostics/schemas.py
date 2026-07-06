"""schemas.py — canonical contracts for the task-diagnostics pipeline.

One row schema (TaskRow) is the single source of truth. Zero-shot predictions, influence results and
reports all DERIVE from immutable cached rows. HF-datasets/Parquet is only the storage/interchange
layer; the internal contract is TaskRow, not "whatever the HF repo exposes today".
"""
from __future__ import annotations
import ast
import hashlib
import json
from dataclasses import asdict, dataclass


def canonical_json(obj) -> str:
    """Stable JSON string for metadata/config, whether given a dict, a JSON string, or a Python-repr
    string (reasoning_core's Problem.to_dict emits metadata as a repr, not JSON)."""
    if isinstance(obj, str):
        s = obj.strip()
        if not s:
            return "{}"
        for parse in (json.loads, ast.literal_eval):
            try:
                obj = parse(s); break
            except Exception:
                continue
        else:
            return s  # already a plain string we can't structure — keep as-is
    return json.dumps(obj, sort_keys=True, default=str, ensure_ascii=False)


@dataclass(frozen=True)
class TaskRow:
    """One immutable task example. HF-like; metadata/config are canonical JSON strings."""
    task: str
    level: int
    prompt: str
    answer: str
    metadata: str          # canonical JSON string
    mode: str              # "instruct" default (hub-data annotation)
    task_version: str
    behavior_hash: str
    config: str            # canonical JSON string
    prompt_tokens: int
    answer_tokens: int
    gen_time_s: float
    row_hash: str

    def to_dict(self) -> dict:
        return asdict(self)

    def to_series(self):
        """pandas.Series for reasoning_core.score_answer (metadata parsed back to a dict)."""
        import pandas as pd
        d = asdict(self)
        try:
            d["metadata"] = json.loads(self.metadata)
        except Exception:
            pass
        return pd.Series(d)

    def to_problem(self):
        from reasoning_core.template import Problem
        try:
            md = json.loads(self.metadata)
        except Exception:
            md = {}
        return Problem.from_dict({"prompt": self.prompt, "answer": self.answer,
                                  "metadata": md, "task": self.task})

    @staticmethod
    def compute_hash(task, level, prompt, answer, metadata) -> str:
        h = hashlib.sha1(f"{task}\x00{level}\x00{prompt}\x00{answer}\x00{metadata}".encode())
        return h.hexdigest()[:16]


@dataclass(frozen=True)
class CacheManifest:
    cache_id: str
    source: str                       # "fresh" | "hf"
    tasks: tuple
    levels: tuple
    n_per_task: int
    mode: str
    generator_version: str
    behavior_hashes: dict             # task -> behavior_hash
    tokenizer: str
    repo: str | None = None
    revision: str | None = None
    n_rows: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ExperimentSpec:
    """A comparable configuration. Reports aggregate ONLY rows sharing a spec (unless told otherwise)."""
    model: str
    seed: int
    train_steps: int
    main_data: str
    legs: tuple
    aux_cache_id: str
    scoring: str = "pct_reduction"

    def hash(self) -> str:
        return hashlib.sha1(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()[:12]

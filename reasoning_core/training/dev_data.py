"""Versioned local/Hugging Face streaming recipes for the dev pipeline."""

import gc
import time
from dataclasses import dataclass
from pathlib import Path

from datasets import interleave_datasets, load_dataset


FORMATTERS = ("sft_qa_v1", "influence_legacy_v1", "text_v1")


@dataclass(frozen=True)
class StreamSpec:
    source: str
    formatter: str
    split: str = "train"
    config: str | None = None
    cycle: bool = False

    def __post_init__(self):
        if self.formatter not in FORMATTERS:
            raise ValueError(f"Unknown formatter {self.formatter!r}; choose from {FORMATTERS}")


def format_row(row, eos_token, formatter):
    if formatter == "text_v1":
        return {"prompt": "", "completion": row["text"] + eos_token}
    prompt, answer = row["prompt"], row["answer"]
    if formatter == "sft_qa_v1":
        return {"prompt": f"Q: {prompt}\nA:", "completion": f" {answer}{eos_token}"}
    return {"prompt": f"{prompt}\n", "completion": f"{answer}{eos_token}"}


def load_stream(spec, tokenizer, max_length=None, chars_per_token=4.0):
    """Load a replayable local or HF stream and apply a versioned formatter."""
    max_chars = max_length * chars_per_token if max_length else None
    raw = _raw_stream(spec)

    def format_example(row, index):
        return {
            **format_row(row, tokenizer.eos_token, spec.formatter),
            "_source": spec.source,
            "_source_index": index,
        }

    stream = raw.map(format_example, with_indices=True, remove_columns=raw.column_names)
    if max_chars:
        stream = stream.filter(
            lambda row: len(row["prompt"]) + len(row["completion"]) <= max_chars
        )
    return stream.repeat(None) if spec.cycle else stream


def mix_streams(main, aux=None, aux_ratio=0.0, seed=42, shuffle_buffer=100):
    parts = [stream for stream in (main, aux) if stream is not None]
    if len(parts) == 2:
        p_main = 1 / (1 + aux_ratio)
        stream = interleave_datasets(
            parts, probabilities=[p_main, 1 - p_main],
            seed=seed, stopping_strategy="first_exhausted",
        )
    else:
        stream = parts[0]
    return stream.shuffle(seed=seed, buffer_size=shuffle_buffer) if shuffle_buffer else stream


def steps_for_token_budget(token_budget, aux_ratio, max_length, effective_batch_size):
    total = token_budget * (1 + aux_ratio)
    return max(1, int(total // (max_length * effective_batch_size)))


def replay_after(stream_factory, consumed):
    """Recreate and skip, matching Trainer's deterministic iterable resume strategy."""
    return stream_factory().skip(consumed)


def settle_remote_streams(seconds=1):
    """Let native HF/Arrow readers finish teardown before interpreter shutdown."""
    gc.collect()
    time.sleep(seconds)


def _raw_stream(spec):
    path = Path(spec.source).expanduser()
    if path.exists():
        suffix = path.suffix.lower()
        if suffix not in {".json", ".jsonl", ".parquet"}:
            raise ValueError(f"Local stream must be JSONL/JSON/Parquet, got {path}")
        loader = "parquet" if suffix == ".parquet" else "json"
        return load_dataset(loader, data_files=str(path), split=spec.split, streaming=True)
    return load_dataset(spec.source, spec.config, split=spec.split, streaming=True)

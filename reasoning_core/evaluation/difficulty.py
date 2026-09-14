"""Cheap generation headroom checks, shared by landing and ladder tuning.

Repetition is only a smoke test for variety, not evidence of structural diversity.
No model calls, balancing, deduplication, or length rejection sampling belong here.
"""
import json
import time


def check_headroom(task, *, levels=(0, 6), samples=16, max_prompt_tokens=2048,
                   max_mean_seconds=1.0, timeout_seconds=3, min_unique_ratio=0.75):
    """Return per-level measurements; raise ValueError on an unusable endpoint.

    Call inside the validation subprocess for an outer deadline as well as the
    generator's per-example timeout. The task's configuration is advanced in place.
    """
    measurements = []
    for level in levels:
        keys, prompts, costs, lengths = set(), set(), [], []
        for _ in range(samples):
            started = time.monotonic()
            try:
                entry = task.generate_example(level=level, max_tokens=0,
                                              timeout=timeout_seconds)
                elapsed = time.monotonic() - started
                json.dumps(entry.to_dict())
                if task.score_answer(entry.answer, entry) != 1:
                    raise ValueError("reference answer does not score 1")
                tokens = len(task.tokenizer.encode(entry.prompt))
                if tokens > max_prompt_tokens:
                    raise ValueError(f"prompt has {tokens} tokens; ceiling {max_prompt_tokens}")
                if elapsed > timeout_seconds:
                    raise ValueError(f"generation took {elapsed:.2f}s; ceiling {timeout_seconds}s")
                prompts.add(entry.prompt)
                keys.add(task.deduplication_key(entry))
            except Exception as error:
                raise ValueError(f"headroom level {level}: {error}") from error
            costs.append(elapsed)
            lengths.append(tokens)
        mean = sum(costs) / samples
        unique = min(len(keys), len(prompts)) / samples
        if mean > max_mean_seconds:
            raise ValueError(f"headroom level {level}: generation averages {mean:.2f}s; "
                             f"ceiling {max_mean_seconds}s")
        if unique < min_unique_ratio:
            raise ValueError(f"headroom level {level}: instance pool is too repetitive "
                             f"({unique:.0%} unique across {samples} raw draws)")
        measurements.append(dict(level=level, samples=samples, unique_ratio=unique,
                                 mean_seconds=mean, max_prompt_tokens=max(lengths)))
    return measurements

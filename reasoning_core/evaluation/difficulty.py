"""Cheap generation headroom checks and ladder verdicts, shared by landing and ladder tuning.

Repetition is only a smoke test for variety, not evidence of structural diversity.
No model calls, balancing, deduplication, or length rejection sampling belong here.
"""
import json
import time

# What a ladder should do: start solvable, end hard, and fall in between. The bands are wide
# because the probe is a few samples per cell: a verdict says which ladders are worth a look,
# not what to change.
EASY_FLOOR = 0.60     # the bottom level should be mostly solvable
HARD_CEIL = 0.30      # the top level should mostly not be
MIN_SPAN = 0.25       # below this the knob is not moving difficulty
MIN_N = 5             # a solve rate over 3 samples has a standard error near 0.3


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


def curve(cache, model, min_n=MIN_N):
    """{task: (points, holes)} for one model, from the probe cache.

    `holes` are probed levels whose cell cannot be trusted, and a curve with holes is not
    diagnosed at all. The dropped cells are the HARD ones -- format failures and short batches
    cluster at the top of the ladder -- so dropping them per cell truncates the curve from the
    top and makes a falling task look flat. graph_pathfinding measured 53/53/25/0 and was
    diagnosed "flat" off the two surviving cells, which would have bought a patch it did not need.
    """
    points, holes = {}, {}
    for key, cell in cache.items():
        parts = key.split("|")
        if len(parts) != 3 or parts[2] != model:
            continue
        task, level = parts[0], int(parts[1])
        if cell.get("status") != "ok":
            why = cell.get("status")
        elif cell.get("format_ok", 1.0) < 0.5:
            why = f"format {cell['format_ok']:.0%}"
        elif cell.get("n", 0) < min_n:
            why = f"n={cell.get('n', 0)}"
        else:
            why = None
        if why:
            holes.setdefault(task, {})[level] = why
        else:
            points.setdefault(task, {})[level] = cell["solve_rate"]
    return {t: (dict(sorted(points.get(t, {}).items())), dict(sorted(holes.get(t, {}).items())))
            for t in set(points) | set(holes)}


def diagnose(points):
    """What is wrong with this ladder, or None if nothing is."""
    rates = list(points.values())
    lo, hi = rates[0], rates[-1]
    if hi > lo + MIN_SPAN:
        return ("inverted", "solve rate RISES with level: the knob is making problems easier")
    if min(rates) >= EASY_FLOOR:
        return ("too-easy", f"solved at every level (min {min(rates):.0%}): the top rung is not hard")
    if max(rates) <= HARD_CEIL:
        return ("too-hard", f"unsolved at every level (max {max(rates):.0%}): the bottom rung is not easy")
    if lo - hi < MIN_SPAN:
        return ("flat", f"spans only {lo - hi:+.0%} across the range: the knob adds size, not difficulty")
    return None

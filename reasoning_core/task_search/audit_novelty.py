"""Run the wave critic against tasks the library already ships.

audit_shipped makes this argument about the contract gate; this is the same argument
about the novelty gate. A gate can be strict, or it can be wrong, and a run of rejections
alone cannot tell those apart. The library is the calibration: every shipped task was once
a candidate, so a critic that will not let them back in is not measuring novelty against
the catalog, it is measuring against a standard the catalog does not meet.

The held-out entries are removed from the catalog by name before review, or each candidate
would be its own nearest neighbour and the answer would be a tautology. They are removed
together and reviewed together, which is also the fairest arrangement available: the
critic compares candidates against each other as well as against the catalog, so the
held-out set stays visible as competition rather than vanishing.

    python -m reasoning_core.task_search.audit_novelty --count 30
"""
import argparse
import os
import random
from pathlib import Path

from .wave_proposer import (CRITIC_API_KEY_ENV, CRITIC_ENDPOINT, CRITIC_MAX_BATCH,
                            CRITIC_MODEL, CRITIC_SAMPLES, ChatClient, _critic_votes,
                            build_catalog)

SHIPPED = ("gallery", "task")


def sample(catalog, *, count, seed, sources=SHIPPED):
    shipped = [entry for entry in catalog if entry.source in sources]
    if len(shipped) <= count:
        return shipped
    return random.Random(seed).sample(shipped, count)


def verdicts(votes, held_out):
    """The wave's own accept rule, applied to each held-out entry.

    Kept in step with propose_wave by hand rather than shared: the wave also assigns ids,
    grows the catalog and writes exclusions, and none of that belongs in an audit.
    """
    for entry, ballots in zip(held_out, votes):
        cast = [ballot for ballot in ballots if ballot and ballot["neighbors_valid"]]
        in_favour = [ballot for ballot in cast if ballot["passes"]]
        if not cast:
            yield entry, None, f"0/{len(ballots)} usable ballots", None
            continue
        tally = f"{len(in_favour)}/{len(cast)}"
        losing = next((other for other in cast if not other["passes"]), None)
        shown = losing if losing is not None else in_favour[0]
        yield entry, len(in_favour) * 2 > len(cast), tally, shown


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--count", type=int, default=30)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--model", default=CRITIC_MODEL)
    parser.add_argument("--endpoint", default=CRITIC_ENDPOINT)
    parser.add_argument("--api-key-env", default=CRITIC_API_KEY_ENV)
    parser.add_argument("--samples", type=int, default=CRITIC_SAMPLES)
    parser.add_argument("--timeout-seconds", type=int, default=2400)
    arguments = parser.parse_args(argv)

    catalog = build_catalog(Path(arguments.repo_root).resolve())
    held_out = sample(catalog, count=arguments.count, seed=arguments.seed)
    names = {entry.name for entry in held_out}
    remaining = tuple(entry for entry in catalog if entry.name not in names)
    print(f"{len(held_out)} shipped tasks reviewed against {len(remaining)} catalog"
          f" entries, {arguments.samples} samples each")

    critic = ChatClient(model=arguments.model, endpoint=arguments.endpoint,
                        api_key=os.environ.get(arguments.api_key_env),
                        timeout=arguments.timeout_seconds)
    votes = _critic_votes(
        critic, [{"name": entry.name, "summary": entry.summary} for entry in held_out],
        list(remaining),
        samples=arguments.samples, round_index=1, wave_name="audit-novelty",
        max_batch=CRITIC_MAX_BATCH)

    readmitted = 0
    for entry, passed, tally, ballot in verdicts(votes, held_out):
        readmitted += bool(passed)
        mark = "novel " if passed else ("REJECT" if passed is False else "unusable")
        # Why it failed, not just that it did: a rejection that names no overlap and
        # scores 2 on novelty is the gate disliking the task, not finding a duplicate,
        # and those are different problems with different fixes.
        scores = (ballot or {}).get("scores") or {}
        graded = " ".join(f"{key[:4]}={scores.get(key, '-')}"
                          for key in ("novelty", "sft_value", "feasibility", "clarity"))
        collided = next((n.get("id") for n in (ballot or {}).get("neighbors") or []
                         if n.get("relationship") in ("same_operation", "variant")), "")
        print(f"  {mark} {tally:>5}  {entry.name:<42} "
              f"{(ballot or {}).get('verdict', '-'):<10} {graded}  {collided}")
    print(f"\n{readmitted}/{len(held_out)} shipped tasks would be accepted as new today")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

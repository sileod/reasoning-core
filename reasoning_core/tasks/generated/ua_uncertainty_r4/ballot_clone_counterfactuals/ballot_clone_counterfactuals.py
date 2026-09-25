import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class BallotCloneConfig(Config):
    k: int = 3
    voters: int = 3
    blocks: int = 1

    def apply_difficulty(self, level):
        self.k = min(5, 3 + level // 2)
        self.voters = min(6, 3 + level // 2)
        self.blocks = 1 if level < 2 else 2


def _irv_winner(ballots, candidates):
    rem = list(candidates)
    while len(rem) > 1:
        counts = {c: 0 for c in rem}
        for b in ballots:
            for c in b:
                if c in rem:
                    counts[c] += 1
                    break
        mn = min(counts.values())
        to_elim = sorted(c for c in rem if counts[c] == mn)[0]
        rem.remove(to_elim)
    return rem[0]


def _collapse(label, clonable):
    for base in clonable:
        if label in (base + "1", base + "2"):
            return base
    return label


def _build_ballot(base_ranking, clonable, pattern, vi):
    actual = []
    for c in base_ranking:
        if c in clonable:
            idx = clonable.index(c)
            bit = pattern[vi * len(clonable) + idx]
            c1, c2 = c + "1", c + "2"
            actual += ([c1, c2] if bit == 0 else [c2, c1])
        else:
            actual.append(c)
    return actual


class BallotCloneCounterfactuals(Task):
    summary = ("Replace candidates with contiguous clone blocks in ranked ballots under "
               "stated elimination or scoring rules; range over internal clone orders and "
               "determine which original candidates can win after collapsing clone identities.")
    design_choice = ("output the set of surviving original candidate labels as a sorted "
                     "hyphen-joined string, e.g., 'A-B' or 'NONE'.")
    config_cls = BallotCloneConfig

    def generate_entry(self):
        cfg = self.config
        k, V = cfg.k, cfg.voters
        orig_labels = [chr(65 + i) for i in range(k)]
        clonable = random.sample(orig_labels, cfg.blocks)
        base_ballots = [random.sample(orig_labels, k) for _ in range(V)]

        candidates = []
        for c in orig_labels:
            if c in clonable:
                candidates += [c + "1", c + "2"]
            else:
                candidates.append(c)

        winners = set()
        for pattern in itertools.product((0, 1), repeat=V * len(clonable)):
            ballots = [_build_ballot(base, clonable, pattern, vi)
                       for vi, base in enumerate(base_ballots)]
            win = _irv_winner(ballots, candidates)
            winners.add(_collapse(win, clonable))

        winners = set(winners)
        assert 1 <= len(winners) <= k
        assert winners.issubset(set(orig_labels))

        answer = "-".join(sorted(winners))
        metadata = {
            "originals": list(orig_labels),
            "clonable": list(clonable),
            "ballots": [list(b) for b in base_ballots],
            "winners": sorted(winners),
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        m = metadata
        clonable = m["clonable"]
        candidates_txt = ", ".join(
            (c + "1," + c + "2" if c in clonable else c) for c in m["originals"]
        )
        block_lines = []
        for bc in clonable:
            block_lines.append(f"- {bc} is a clone block with two clones {bc}1 and {bc}2")
        ballot_text = ", ".join("(" + " > ".join(b) + ")" for b in m["ballots"])
        return (
            "An election uses instant-runoff voting (IRV): repeatedly eliminate the "
            "candidate with the fewest first-choice votes among those still running, "
            "retallying each eliminated candidate's second (then third, ...) choice on "
            "that ballot; ties for fewest first-choice votes are broken by eliminating "
            "the alphabetically earliest label. Stop when one candidate remains.\n"
            f"The candidates are {candidates_txt} over original identities "
            f"{', '.join(m['originals'])}.\n"
            + "\n".join(block_lines)
            + "\nIn every ballot, the two clones of a clone block are placed in two "
            "adjacent ranks, but the internal order of the two clones within a block may "
            "differ from voter to voter. We range over every possible assignment of "
            "internal clone orders across voters and blocks.\n"
            f"The ballots (each voter's full ranking, highest rank first) are "
            f"{ballot_text}.\n"
            "After a clone is elected we collapse its identity to its original. "
            "Determine the set of ORIGINAL candidate labels that can end up as the "
            "winner under some assignment of the internal clone orders. Answer as the "
            "sorted hyphen-joined labels, e.g. 'A-B' or 'NONE'."
        )

    def score_answer(self, answer, entry):
        canonical = "-".join(sorted(entry.metadata["winners"]))
        return 1.0 if answer == canonical else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'ballot_clone_counterfactuals (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/ballot_clone_counterfactuals',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

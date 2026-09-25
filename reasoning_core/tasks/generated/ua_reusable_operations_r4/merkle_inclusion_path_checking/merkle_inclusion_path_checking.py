import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'merkle_inclusion_path_checking (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_reusable_operations_r4/merkle_inclusion_path_checking',
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

design_choice = ("Present proofs as sequences of (side, hash) pairs with a final target root; "
                 "solvers must recompute the root and output it plus the first level where "
                 "their computed hash differs from the stated root, or 'valid' if all match.")


_BASE = 31


def _combine(current, sibling, side, mod):
    if side == "L":
        return (current * _BASE + sibling) % mod
    return (sibling * _BASE + current) % mod


@dataclass
class MerklePathConfig(Config):
    min_levels: int = 2
    max_levels: int = 3
    modulus: int = 97
    corruption_prob: float = 0.5

    def apply_difficulty(self, level):
        self.min_levels = 1 + level // 2
        self.max_levels = 2 + level
        self.modulus = 97 + 90 * level


class MerkleInclusionPathChecking(Task):
    summary = ("Verify Merkle inclusion proofs: fold a leaf through (side, sibling) levels with a "
               "modulus hash, compare each level's computed value to its stated value, and answer "
               "the recomputed root plus the first mismatching level, or 'valid' when all match.")
    config_cls = MerklePathConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        mod = int(cfg.modulus)
        m = random.randint(int(cfg.min_levels), int(cfg.max_levels))
        leaf = random.randrange(mod)
        siblings = [random.randrange(mod) for _ in range(m)]
        sides = [random.choice(("L", "R")) for _ in range(m)]

        actual = [leaf]
        cur = leaf
        for i in range(m):
            cur = _combine(cur, siblings[i], sides[i], mod)
            actual.append(cur)

        corrupt = None
        if random.random() < cfg.corruption_prob:
            corrupt = random.randint(1, m)
            newval = (actual[corrupt] + 1 + random.randrange(mod - 1)) % mod
            if newval == actual[corrupt]:
                newval = (actual[corrupt] + 1) % mod
        stated = list(actual)
        if corrupt is not None:
            stated[corrupt] = newval

        first_mismatch = None
        for i in range(1, m + 1):
            if actual[i] != stated[i]:
                first_mismatch = i
                break

        root = int(actual[m])
        if first_mismatch is None:
            status = "valid"
            assert corrupt is None
        else:
            status = str(int(first_mismatch))
            assert corrupt is not None and first_mismatch == corrupt
        answer = f"{root}|{status}"

        levels = [
            {"side": side, "sibling": int(siblings[i]), "stated": int(stated[i + 1])}
            for i, side in enumerate(sides)
        ]
        return Entry(
            metadata={
                "leaf": int(leaf),
                "modulus": int(mod),
                "levels": levels,
                "root": root,
                "status": status,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        lines = [
            "A Merkle tree inclusion path from a leaf to the root lists each level on the way up.",
            "Every level has a sibling value sitting on one side of the path node, and a stated "
            "value that the path node is claimed to have at that level.",
            "Starting from the leaf value, combine the current value with the sibling into a "
            "parent node using (current*31 + sibling) mod M when the sibling is on the left (L), "
            "and (sibling*31 + current) mod M when the sibling is on the right (R). The result of "
            "one level is the current value of the next. Recompute the whole path using only the "
            "leaf and the given siblings (ignore the stated values when combining), then compare "
            "each level's computed value against that level's stated value. The stated value of "
            "the top level is the stated root.",
        ]
        lines.append(f"Modulus M: {metadata['modulus']}")
        lines.append(f"Leaf value: {metadata['leaf']}")
        for idx, lvl in enumerate(metadata["levels"], start=1):
            lines.append(
                f"Level {idx}: sibling on side {lvl['side']}, sibling value {lvl['sibling']}, "
                f"stated node value {lvl['stated']}"
            )
        lines.append(
            "Answer the recomputed root, a pipe '|', then the first level (1-indexed) where your "
            "computed value differs from that level's stated value, or the word 'valid' if every "
            "level matches. Example: '441|valid' or '441|2'."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == str(entry["answer"]).strip() else 0.0

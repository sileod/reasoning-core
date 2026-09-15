import random

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'instruction_priority (draw 1 of 3)',
 'hypothesis': 'ASTRA0:instruction_priority',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/instruction_priority',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1002768851,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

MAX_LEVEL = 5
RANK_NAMES = ["", "lowest", "low", "medium", "high", "highest"]


def _rank_name(rank):
    return RANK_NAMES[rank]


class InstructionPriorityConfig(Config):
    n_instructions: int = 3
    max_rank: int = 3

    def apply_difficulty(self, level):
        self.n_instructions = 3 + level
        self.max_rank = min(5, 3 + level // 2)


class InstructionPriority(Task):
    summary = "Answer whether an action is required under conflicting numeric-rank (1-5) instructions; a direct contradiction resolves to the higher rank while compatible lower-rank instructions still hold."
    design_choice = "Authority levels are numeric ranks (1-5); conflict only when instructions directly contradict, and compatible parts of lower-rank instructions must still be followed."
    config_cls = InstructionPriorityConfig

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        ans = answer.strip().lower()
        if ans not in ("yes", "no"):
            return 0.0
        return 1.0 if ans == entry["answer"] else 0.0

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_instructions
        max_rank = cfg.max_rank

        prominent = ["move the crate to the north", "open the doors",
                     "raise the flag", "power down the generator",
                     "sound the alarm", "release the valves"]

        while True:
            target_verb = random.choice(prominent)
            other = random.choice([v for v in prominent if v != target_verb])

            do_rank = random.randint(1, max_rank)
            dont_rank = random.randint(1, max_rank)

            commands = []
            commands.append(("do", do_rank, target_verb))
            commands.append(("do_not", dont_rank, "do not " + target_verb))
            for _ in range(max(0, n - 2)):
                commands.append(("extra", random.randint(1, max_rank),
                                 random.choice([other, "do not " + other, "return to base"])))

            outcome = "yes" if do_rank > dont_rank else "no"

            final = _final_commands(commands)
            if final is None:
                continue
            gold = _check_final(final, target_verb)
            if gold is None or gold != outcome:
                continue
            if gold != outcome:
                continue
            break

        lines = []
        lines.append("Answer this question with exactly yes or no.")
        lines.append("Each instruction carries a numeric rank 1 (lowest) to 5 (highest). "
                     "Obey every instruction, except that when two instructions directly "
                     "contradict, follow only the higher-ranked one. A lower-ranked instruction "
                     "still applies everywhere it does not directly contradict a higher one.")
        for kind, rank, verb in commands:
            lines.append(f"[{_rank_name(rank)} ({rank})] {verb}.")
        lines.append(random.choice([
            f"Should the operator {target_verb}?",
            f"Is the operator required to {target_verb}?",
            f"Must the operator {target_verb}?",
        ]))

        return Entry(metadata={
            "commands": [[k, r, v] for k, r, v in commands],
            "target_verb": target_verb,
            "answer": outcome,
            "final": final,
        }, answer=outcome)

    def render_prompt(self, metadata):
        lines = []
        lines.append("Answer this question with exactly yes or no.")
        lines.append("Each instruction carries a numeric rank 1 (lowest) to 5 (highest). "
                     "Obey every instruction, except that when two instructions directly "
                     "contradict, follow only the higher-ranked one. A lower-ranked instruction "
                     "still applies everywhere it does not directly contradict a higher one.")
        for r in metadata["commands"]:
            kind, rank, verb = r
            lines.append(f"[{_rank_name(rank)} ({rank})] {verb}.")
        lines.append(random.choice([
            f"Should the operator {metadata['target_verb']}?",
            f"Is the operator required to {metadata['target_verb']}?",
            f"Must the operator {metadata['target_verb']}?",
        ]))
        return "\n".join(lines)


def _contradicts(a_verb, b_verb):
    if a_verb == b_verb:
        return True
    if a_verb == "do not " + b_verb or b_verb == "do not " + a_verb:
        return True
    return False


def _final_commands(commands):
    """Higher rank survives; lower rank is dropped only where it directly
    contradicts (in the retained set)."""
    final = []
    for kind, rank, verb in sorted(commands, key=lambda c: -c[1]):
        if any(crank > rank and _contradicts(cverb, verb)
               for ckind, crank, cverb in commands):
            continue
        final.append((kind, rank, verb))
    return final


def _check_final(final, target_verb):
    if not final:
        return None
    requires = False
    forbids = False
    for kind, rank, verb in final:
        if verb == target_verb:
            requires = True
        if verb == "do not " + target_verb:
            forbids = True
    if requires and forbids:
        return None
    if requires:
        return "yes"
    if forbids:
        return "no"
    return None

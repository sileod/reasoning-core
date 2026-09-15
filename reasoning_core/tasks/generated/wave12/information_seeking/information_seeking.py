import random

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'information_seeking (draw 1 of 3)',
 'hypothesis': 'ASTRA0:information_seeking',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/information_seeking',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2463459592,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class InformationSeekingConfig(Config):
    max_value: int = 10
    num_candidates: int = 4
    num_states: int = 3

    def apply_difficulty(self, level):
        self.max_value = 6 + level * 4
        self.num_candidates = min(3 + level, 7)
        self.num_states = min(2 + level // 2, 6)


class InformationSeeking(Task):
    summary = ("Choose the observation or question that best distinguishes remaining "
               "hypotheses under a supplied finite model: pick the candidate query whose "
               "answer partitions the still-viable candidate set most evenly, with a "
               "fixed tie-break rule over candidate names.")
    config_cls = InformationSeekingConfig

    design_choice = ("Answer is a canonical string naming one of a fixed set of candidate "
                     "observations/questions, with a tie-breaking rule to ensure a unique "
                     "correct answer per instance.")

    def generate_entry(self):
        cfg = self.config
        while True:
            num_hypotheses = random.randint(
                max(2, cfg.num_candidates), cfg.num_candidates + 2)
            hypotheses = random.sample(range(10), num_hypotheses)

            # Each candidate question yields a subset of hypotheses (those answering "yes").
            # We build candidate -> set of positive hypothesis indices.
            candidates = []
            candidate_names = []
            for i in range(cfg.num_candidates):
                name = f"Q{i + 1}"
                candidate_names.append(name)
                size = random.randint(0, num_hypotheses)
                pos = set(random.sample(range(num_hypotheses), size))
                candidates.append(pos)

            # Find the candidate that best splits the FULL hypothesis set (at level 0 all
            # are viable). At higher levels we still reduce over the full set as the
            # "remaining hypotheses".
            remaining = set(range(num_hypotheses))

            best_balance = None
            best_candidates = []
            for idx, pos in enumerate(candidates):
                yes = len(pos & remaining)
                no = len(remaining) - yes
                balance = -abs(yes - no)
                if best_balance is None or balance > best_balance:
                    best_balance = balance
                    best_candidates = [candidate_names[idx]]
                elif balance == best_balance:
                    best_candidates.append(candidate_names[idx])

            # Tie-break: lexicographically smallest candidate name.
            if len(best_candidates) > 1:
                best_candidates.sort()
            answer = best_candidates[0]

            # The answer is a candidate name among candidates list; always well-defined.
            # Domain check: answer must be one of the candidate names.
            if answer in candidate_names:
                break

        metadata = {
            "hypotheses": hypotheses,
            "candidates": {name: sorted(pos)
                           for name, pos in zip(candidate_names, candidates)},
            "num_viable": num_hypotheses,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        lines.append(
            "A model has a set of hypotheses, each of which may be true. "
            "You may ask exactly one yes/no question (an observation). "
            "For each candidate question below, the numbers in brackets are the "
            "indices of the hypotheses that would answer 'yes' to it.")
        hyps = ", ".join(f"H{k}" for k in metadata["hypotheses"])
        lines.append(f"Current hypotheses: {hyps}.")
        viable = list(range(metadata["num_viable"]))
        lines.append(f"All hypotheses are currently viable (indices {viable}).")
        cand_lines = []
        for name in sorted(metadata["candidates"].keys()):
            pos = metadata["candidates"][name]
            cand_lines.append(f"{name}: yes for {pos if pos else 'none'}")
        lines.append("Candidate questions:\n" + "\n".join(cand_lines))
        lines.append(
            "Choose the candidate question that best distinguishes the remaining "
            "hypotheses (split them as evenly as possible into yes and no groups). "
            "If two candidates split equally well, pick the lexicographically smallest "
            "name (Q1 < Q2 < ...). Answer with one candidate name only, e.g. Q2.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip()
        return 1.0 if a == entry.answer else 0.0

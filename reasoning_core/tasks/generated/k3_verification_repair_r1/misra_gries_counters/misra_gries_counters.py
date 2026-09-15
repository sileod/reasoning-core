import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class MisraGriesConfig(Config):
    n: int = 24
    alphabet: int = 6
    k: int = 3

    def apply_difficulty(self, level):
        self.n = self.n + 8 * level
        self.alphabet = min(12, 4 + level)
        self.k = 3 if level < 3 else 4


class MisraGriesCounters(Task):
    summary = ("Maintain k-minus-one Misra-Gries cancellation counters over varied-length "
               "streams from varied alphabets: increment on a hit, occupy an empty slot, or "
               "decrement all on a miss; report the final counter map as a sorted key:value "
               "string, including the majority-vote case.")
    config_cls = MisraGriesConfig
    task_version = 2
    design_choice = ("Vary sequence length and alphabet size across instances; require exact "
                     "final counter map as a canonical sorted string of key:value pairs.")

    def generate_entry(self):
        k = self.config.k
        alpha = list(range(self.config.alphabet))
        n = self.config.n

        counter = {}
        for _ in range(200):
            seq = [random.choice(alpha) for _ in range(n)]
            counter = {}
            for x in seq:
                if x in counter:
                    counter[x] += 1
                elif len(counter) < k - 1:
                    counter[x] = 1
                else:
                    for key in list(counter):
                        counter[key] -= 1
                        if counter[key] == 0:
                            del counter[key]
            if counter:
                break

        final_spec = {key: int(v) for key, v in sorted(counter.items())}
        if not final_spec:
            raise RuntimeError("failed to produce a non-empty misra-gries counter map")
        answer = ",".join(f"{key}:{final_spec[key]}" for key in sorted(final_spec))

        majority = []
        total = len(seq)
        for key in sorted(alpha):
            c = seq.count(key)
            if c > total / 2:
                majority.append(key)
        has_majority = len(majority) > 0

        return Entry(metadata={
            "seq": seq,
            "k": k,
            "n": n,
            "alphabet": alpha,
            "counts": [int(seq.count(i)) for i in sorted(alpha)],
            "counter": [[int(key), int(v)] for key, v in sorted(counter.items())],
            "has_majority": has_majority,
            "majority": majority,
        }, answer=answer)

    def render_prompt(self, metadata):
        k = metadata["k"]
        seq_text = " ".join(str(x) for x in metadata["seq"])
        a = metadata["alphabet"]
        return (f"Using the Misra-Gries majority algorithm with {k - 1} counters, process the "
                f"stream of symbols from alphabet {a}: {seq_text}. "
                f"On a hit increment the counter; if the symbol has no counter and a slot is free, "
                f"occupy it with count 1; otherwise decrement every counter by 1 and drop any that "
                f"reach 0. Write the final counter map in sorted-symbol order as comma-separated "
                f"key:value pairs (for example '0:2,3:1'); if every counter is empty write 'none'.")

    def score_answer(self, answer, entry):
        gold = entry.answer
        norm = "".join(answer.split())
        gold_norm = "".join(gold.split())
        if gold_norm == "none":
            return 1.0 if norm == "none" else 0.0
        if norm == "none":
            return 0.0
        if norm == gold_norm:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'misra_gries_counters (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/misra_gries_counters',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

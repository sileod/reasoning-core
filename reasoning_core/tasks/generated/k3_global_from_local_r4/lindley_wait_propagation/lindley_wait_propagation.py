import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class LindleyWaitConfig(Config):
    count: int = 5
    max_arrival: int = 9
    max_service: int = 9

    def apply_difficulty(self, level):
        self.count = 4 + stochastic_rounding(level * 2)
        self.max_arrival = 2 + stochastic_rounding(level * 2)
        self.max_service = self.max_arrival + 4 + stochastic_rounding(level * 2)


def waits(arrivals, services):
    w = []
    cur = 0
    for a, s in zip(arrivals, services):
        cur = max(0, cur - a + s)
        w.append(cur)
    return w


def parse_wait(answer):
    if "/" in answer:
        num, den = answer.split("/")
        return int(num), int(den)
    return int(answer), 1


def _answer_str(w):
    if w % 1 == 0:
        return str(int(w))
    return f"{w.numerator}/{w.denominator}"


class LindleyWaitPropagation(Task):
    summary = ("Propagate waits through a single-server queue via the Lindley recursion over "
               "arrival and service sequences: carry each wait forward, marking busy periods; "
               "answers are a queried wait, busy-period spans, or peak backlog.")
    design_choice = ("Queries ask for the wait of a specific job index, with arrivals and services "
                     "given as integer lists; answer is that wait as a fraction or integer.")
    config_cls = LindleyWaitConfig

    def generate_entry(self):
        while True:
            n = self.config.count
            arrivals = [random.randint(1, self.config.max_arrival) for _ in range(n)]
            services = [random.randint(1, self.config.max_service) for _ in range(n)]
            w = waits(arrivals, services)
            idx = random.randrange(n)
            target = w[idx]
            if target < 0:
                continue
            if target.numerator < 0 or target.denominator <= 0:
                continue
            break
        metadata = {"arrivals": arrivals, "services": services, "index": idx}
        return Entry(metadata=metadata, answer=_answer_str(target))

    def score_answer(self, answer, entry):
        gold = entry.answer
        try:
            num, _ = parse_wait(answer.strip())
            gnum, _ = parse_wait(gold.strip())
        except ValueError:
            return 0.0
        w = waits(entry.metadata["arrivals"], entry.metadata["services"])
        correct = int(w[entry.metadata["index"]])
        return 1.0 if num == correct else 0.0

    def render_prompt(self, metadata):
        return (
            "A single server processes jobs that arrive at integer times. Arrivals (in time "
            "units between consecutive jobs) are "
            f"{metadata['arrivals']} and service times are {metadata['services']}. "
            "The wait of a job is how long it waits for service after arriving, computed by the "
            "Lindley recursion w_{n} = max(0, w_{n-1} - arrival_n + service_n). "
            f"What is the wait of job index {metadata['index']} (0-based)? "
            "Answer as an integer if it is whole, otherwise as a fraction num/den in lowest terms."
        )


TASK_META = {'parent_source_id': None,
 'idea': 'lindley_wait_propagation (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_global_from_local_r4/lindley_wait_propagation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

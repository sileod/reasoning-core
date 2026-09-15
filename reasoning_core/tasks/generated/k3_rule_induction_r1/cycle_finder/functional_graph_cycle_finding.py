import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'functional_graph_cycle_finding (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_rule_induction_r1/functional_graph_cycle_finding',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class CycleConfig(Config):
    domain_size: int = 8

    def apply_difficulty(self, level):
        self.domain_size = stochastic_rounding(min(8 + level * 3, 28))


def _simulate(table, start):
    """Return (entry_point, tail_length, cycle_length)."""
    seen = {}
    x = start
    i = 0
    while x not in seen:
        seen[x] = i
        x = table[x]
        i += 1
    entry_i = seen[x]
    tail = entry_i
    cycle = i - entry_i
    entry_point = x
    return entry_point, tail, cycle


class CycleFinder(Task):
    summary = ("Given an explicit successor table on a numeric domain and a start element, "
               "simulate the iterates to locate the trajectory's entry into its eventual cycle and "
               "report entry point, tail length and cycle length across maps whose in-trees merge into "
               "one cycle.")
    config_cls = CycleConfig
    design_choice = ("Represent the function as an explicit table of successor values for each element, "
                     "with a numeric domain; the solver must parse the table and simulate iterates "
                     "without any formulaic shortcut.")

    def generate_entry(self):
        n = self.config.domain_size
        domain = list(range(n))

        cycle_len = random.randint(1, n)
        cycle_start = random.randint(0, n - cycle_len)
        cycle = domain[cycle_start:cycle_start + cycle_len]
        random.shuffle(cycle)
        cycle_set = set(cycle)
        table = {cycle[-1]: cycle[0]}
        for i in range(len(cycle) - 1):
            table[cycle[i]] = cycle[i + 1]

        tail_nodes = []
        for v in domain:
            if v not in cycle_set:
                tail_nodes.append(v)

        for v in tail_nodes:
            table[v] = random.choice(domain)

        start = random.choice(domain)

        entry_point, tail, clen = _simulate(table, start)

        table_text = ", ".join(
            "f({}) = {}".format(v, table[v]) for v in sorted(domain)
        )
        prompt = (
            "A function f is defined on the set of integers "
            "{} by the following successor rules: {}. "
            "Starting from the element {}, iterate f repeatedly: "
            "f(x), f(f(x)), ... until the trajectory repeats and settles into a cycle. "
            "Report three integers separated by spaces: the entry point (the first value at which "
            "the trajectory enters the cycle), the tail length (number of iterates before the entry "
            "point, counting the start as iterate 0), and the cycle length. Format: '<entry> <tail> <cycle>'."
            .format(
                "{" + ", ".join(str(v) for v in domain) + "}",
                table_text,
                start,
            )
        )
        answer = "{} {} {}".format(entry_point, tail, clen)

        entry = Entry(
            metadata={
                "successor_table": {str(k): v for k, v in table.items()},
                "domain": domain,
                "start": start,
                "entry_point": entry_point,
                "tail_length": tail,
                "cycle_length": clen,
            },
            answer=answer,
        )
        return entry

    def render_prompt(self, metadata):
        n = len(metadata["domain"])
        domain = metadata["domain"]
        table = {int(k): v for k, v in metadata["successor_table"].items()}
        table_text = ", ".join(
            "f({}) = {}".format(v, table[int(v)]) for v in sorted(domain)
        )
        return (
            "A function f is defined on the set of integers "
            "{} by the following successor rules: {}. "
            "Starting from the element {}, iterate f repeatedly. "
            "Report three integers separated by spaces: the entry point (first value at which "
            "the trajectory enters the cycle), the tail length (number of iterates before the entry "
            "point, counting the start as iterate 0), and the cycle length. Format: '<entry> <tail> <cycle>'."
            .format(
                "{" + ", ".join(str(v) for v in sorted(domain)) + "}",
                table_text,
                metadata["start"],
            )
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        parts = answer.split()
        if len(parts) != 3:
            return 0.0
        try:
            a = int(parts[0])
            b = int(parts[1])
            c = int(parts[2])
        except ValueError:
            return 0.0
        meta = entry.metadata
        if (
            a == meta["entry_point"]
            and b == meta["tail_length"]
            and c == meta["cycle_length"]
        ):
            return 1.0
        return 0.0

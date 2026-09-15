import random
from dataclasses import dataclass

from reasoning_core.template import Task, Entry, Config, edict, stochastic_rounding as sround


TASK_META = {'parent_source_id': None,
 'idea': 'stack_sorting_discipline (draw 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_invariants_r1/stack_sorting_discipline',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 382564971,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


design_choice = ("Return the element popped at the k-th pop, but if the stack becomes "
                 "blocked before k pops, return the blocked value instead.")


@dataclass
class StackSortingConfig(Config):
    n: int = 10

    def apply_difficulty(self, level):
        self.n = sround(self.n + level)


def _simulate(perm):
    n = len(perm)
    inp = list(perm)
    stack = []
    pops = []
    expected = 1
    while True:
        if stack and stack[-1] == expected:
            stack.pop()
            pops.append(expected)
            expected += 1
            if expected > n:
                return pops, None
        elif inp:
            stack.append(inp.pop(0))
        else:
            return pops, stack[-1]


class StackSortingDiscipline(Task):
    summary = ("Route an input permutation through a single LIFO stack to emit the "
               "identity by greedily interleaving pushes and pops, and return the element "
               "emitted at the k-th pop, or the blocking top-of-stack value when the stack "
               "blocks before k pops.")
    config_cls = StackSortingConfig

    def generate_entry(self):
        cfg = self.config
        perm = list(range(1, cfg.n + 1))
        random.shuffle(perm)
        pops, blocked = _simulate(perm)
        k = random.randint(1, cfg.n)
        if k <= len(pops):
            answer = pops[k - 1]
        else:
            answer = blocked
        if not (1 <= answer <= cfg.n):
            raise RuntimeError('answer out of domain')
        recon, _ = _simulate(perm)
        if k <= len(pops):
            assert recon[k - 1] == answer
        else:
            assert blocked is not None
        answers = str(answer)
        metadata = edict({
            'perm': perm,
            'k': k,
            'sortable': blocked is None,
            'num_pops': len(pops),
            'blocked': blocked,
        })
        metadata.payload = {
            'perm': perm,
            'k': k,
        }
        metadata['_answer'] = answers
        return Entry(metadata=metadata, answer=answers)

    def render_prompt(self, metadata):
        return (f"We route the input permutation {metadata.perm} through a single LIFO "
                f"stack. The target output is the identity 1,2,...,n in increasing order. "
                f"We process greedily: whenever the next expected value (the smallest not "
                f"yet emitted, starting at 1) is on top of the stack, pop and emit it; "
                f"otherwise push the next unused element of the input permutation onto the "
                f"stack. If the input is exhausted but the next expected value is not on "
                f"top of the stack, the stack is blocked and cannot emit any more values. "
                f"Record the emitted values in the order they are popped. Let k = "
                f"{metadata.k}. Give the k-th emitted value; however, if the stack becomes "
                f"blocked before k values are emitted, give the blocking value (the element "
                f"on top of the stack at the moment it blocks) instead.\n"
                f"The answer is a single integer.")

    def score_answer(self, answer, entry):
        got = answer.strip()
        try:
            iv = int(got)
        except ValueError:
            return 0.0
        if str(iv) == got and iv == int(entry.answer):
            return 1.0
        return 0.0

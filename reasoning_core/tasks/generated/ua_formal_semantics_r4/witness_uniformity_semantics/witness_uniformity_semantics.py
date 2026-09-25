import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class UniformityConfig(Config):
    nvars: int = 2
    nclauses: int = 2
    domain_size: int = 2
    lit_per_clause: int = 2

    def apply_difficulty(self, level):
        self.nvars = 2 + self._step(level)
        self.nclauses = 2 + self._step(level)
        self.domain_size = 2 + self._step(max(0, level - 2))
        self.lit_per_clause = 2

    @staticmethod
    def _step(level):
        if level <= 0:
            return 0
        if level <= 3:
            return 1
        if level <= 5:
            return 2
        return 3


def eval_literal(assign, var, op, val):
    a = assign.get(var, 0)
    if op == "=":
        return a == val
    if op == "!=":
        return a != val
    if op == ">":
        return a > val
    if op == "<":
        return a < val


def product(domain, repeat):
    pools = [list(domain)] * repeat
    result = [[]]
    for pool in pools:
        result = [x + [y] for x in result for y in pool]
    return result


class WitnessUniformitySemantics(Task):
    summary = "Evaluate quantified clauses with declared witness dependencies and independence constraints over finite relations; return whether a uniform witness policy satisfies every combination of universal choices."

    design_choice = "Represent each clause as a conjunction of atomic relation literals over integer domains, with witness variables as existential quantifiers and universals as separate domains, answer as 'yes' or 'no'."

    config_cls = UniformityConfig

    def generate_entry(self):
        cfg = self.config
        nvars = cfg.nvars
        nclauses = cfg.nclauses
        dom = cfg.domain_size
        lpc = cfg.lit_per_clause

        for _attempt in range(2000):
            witnesses = [f"y{i}" for i in range(nvars)]
            universals = [f"x{i}" for i in range(max(1, (nvars + 1) // 2))]

            clauses = []
            for _ in range(nclauses):
                clause = []
                for _l in range(lpc):
                    var = random.choice(witnesses + universals)
                    op = random.choice(["=", "!=", ">", "<"])
                    val = random.randint(0, dom - 1)
                    clause.append((var, op, val))
                clauses.append(clause)

            univ_domain = list(range(dom))
            univ_choices = []
            for combo in product(univ_domain, repeat=len(universals)):
                univ_choices.append(dict(zip(universals, combo)))

            witness_assignments = []
            for combo in product(univ_domain, repeat=len(witnesses)):
                witness_assignments.append(dict(zip(witnesses, combo)))

            def clause_sat(wa, ua):
                assign = dict(ua)
                assign.update(wa)
                return any(
                    all(eval_literal(assign, var, op, val) for var, op, val in clause)
                    for clause in clauses
                )

            uniform_works = any(
                all(clause_sat(policy, ua) for ua in univ_choices)
                for policy in witness_assignments
            )

            answer = "yes" if uniform_works else "no"

            metadata = {
                "witnesses": witnesses,
                "universals": universals,
                "domain": list(range(dom)),
                "clauses": [list(c) for c in clauses],
            }
            entry = Entry(metadata=metadata, answer=answer)
            return entry

        raise RuntimeError("failed to generate instance")

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip().lower() == entry.answer else 0.0

    def render_prompt(self, metadata):
        body = []
        for clause in metadata["clauses"]:
            lits = [f"{var}{op}{val}" for var, op, val in clause]
            body.append("(" + " AND ".join(lits) + ")")
        clause_str = " AND ".join(body)
        parts = []
        for i, var in enumerate(metadata["universals"]):
            parts.append(f"forall {var} in {list(range(len(metadata['domain'])))}")
        univ_str = ", ".join(parts)
        text = (
            f"Consider quantified clauses over the integer domain "
            f"D = {list(range(len(metadata['domain'])))}. The witness "
            f"variables are {metadata['witnesses']} and the universal "
            f"variables are {metadata['universals']}. A uniform witness "
            f"policy is a single assignment fixing every witness variable, "
            f"used regardless of the values the universal variables take. "
            f"Does there exist a uniform witness policy such that {univ_str}: "
            f"at least one clause is satisfied? The clauses are:\n"
            f"{clause_str}\n"
            f"Answer 'yes' or 'no'."
        )
        return text


TASK_META = {'parent_source_id': None,
 'idea': 'witness_uniformity_semantics (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_semantics_r4/witness_uniformity_semantics',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

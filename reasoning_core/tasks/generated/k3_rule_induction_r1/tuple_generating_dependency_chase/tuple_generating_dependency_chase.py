import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class TupleGeneratingDependencyChaseConfig(Config):
    num_facts: int = 4
    num_tgds: int = 1
    dom_size: int = 8
    arity: int = 2
    max_steps: int = 6
    cap: int = 10

    def apply_difficulty(self, level):
        self.num_facts = stochastic_rounding(self.num_facts + level)
        self.num_tgds = stochastic_rounding(self.num_tgds + level // 2)
        self.dom_size = stochastic_rounding(self.dom_size + 3 * level)
        self.arity = 2 if level < 3 else 3
        self.max_steps = stochastic_rounding(self.max_steps + level)
        self.cap = stochastic_rounding(self.cap + 3 * level)


def _parse_answer(answer):
    return sorted(eval(answer))


class TupleGeneratingDependencyChase(Task):
    summary = (
        "Apply universal and existential tuple-generating dependencies to a small "
        "relational instance by repeatedly introducing required atoms and fresh "
        "witnesses, returning the derived atom set or a queried membership."
    )
    design_choice = (
        "Answer format: return the full set of derived atoms as a canonical sorted "
        "list of tuples, versus a membership query for a single target atom with "
        "binary yes/no."
    )
    config_cls = TupleGeneratingDependencyChaseConfig

    def _build_system(self, cfg):
        arity = cfg.arity
        # Each TGD is a list of head-position kinds over one body/head relation of
        # arity `arity`: 'uni' copies the body variable at that position,
        # 'exi' introduces a brand-new existential witness.
        dependencies = []
        for _ in range(max(1, cfg.num_tgds)):
            kinds = []
            for _ in range(arity):
                kinds.append(random.choice(["uni", "exi"]))
            if not any(k == "exi" for k in kinds):
                kinds[random.randrange(arity)] = "exi"
            dependencies.append(kinds)
        return dependencies

    def generate_entry(self):
        cfg = self.config
        arity = cfg.arity
        dependencies = self._build_system(cfg)

        facts = set()
        while len(facts) < cfg.num_facts:
            tup = tuple(random.randrange(cfg.dom_size) for _ in range(arity))
            facts.add(tup)
        facts = sorted(facts)

        derived = self._run_chase(facts, dependencies, cfg)
        answer_atoms = sorted(derived)
        answer = repr(answer_atoms)
        metadata = {
            "facts": sorted(facts),
            "dependencies": dependencies,
            "arity": arity,
            "derived": answer_atoms,
        }
        return Entry(metadata=metadata, answer=answer)

    def _run_chase(self, facts, dependencies, cfg):
        # Single-pass chase: each TGD is applied once to each original fact tuple
        # (in TGD order, then fact order), introducing a freshly numbered witness
        # for each existential position. No recursion, so the process is finite and
        # the fresh-witness numbering below matches the prompt exactly.
        arity = cfg.arity
        derived = set(facts)
        used = set()
        for t in facts:
            used.update(t)
        fresh_counter = 0
        while fresh_counter in used:
            fresh_counter += 1

        for kinds in dependencies:
            for tup in facts:
                head = []
                for j, k in enumerate(kinds):
                    if k == "uni":
                        head.append(tup[j])
                    else:
                        while fresh_counter in used:
                            fresh_counter += 1
                        head.append(fresh_counter)
                        used.add(fresh_counter)
                        fresh_counter += 1
                head_t = tuple(head)
                if head_t not in derived:
                    derived.add(head_t)
        return derived

    def render_prompt(self, metadata):
        arity = metadata["arity"]
        facts = metadata["facts"]
        deps = metadata["dependencies"]
        rel = "R"
        lines = [
            "We have a finite relational instance over a single relation R of "
            f"arity {arity}. Its facts are:"
        ]
        lines.append("\n".join(f"R({', '.join(map(str, t))})" for t in facts))
        lines.append("")
        lines.append(
            "A tuple-generating dependency (TGD) is a rule: whenever a tuple "
            f"satisfying the body is present, the head tuple must be derived too. "
            f"The head mentions the same variables x0..x{arity - 1}, each position "
            "being either a universal copy of a body position (value carried over "
            "verbatim) or an existential fresh witness: a brand-new constant not "
            "equal to any constant already in the instance or previously "
            "introduced, never reused."
        )
        lines.append("")
        lines.append("The dependencies are:")
        for i, kinds in enumerate(deps):
            head_parts = []
            for j, k in enumerate(kinds):
                head_parts.append(f"x{j}" if k == "uni" else f"fresh{i}_{j}")
            lines.append(
                f"TGD {i}: R({', '.join('x' + str(j) for j in range(arity))}) -> R({', '.join(head_parts)})"
            )
        lines.append(
            "where each x with an index is the universal copy of the body value in "
            "that position, and each fresh name labels an existential witness."
        )
        lines.append("")
        lines.append(
            "Application rule (no recursion): go through the TGDs in the order "
            "listed above; for each one, apply it exactly once to each original "
            "fact tuple, in the order the facts are listed. Universal heads copy "
            "fact values verbatim. For each existential head position, introduce a "
            "fresh witness: the smallest non-negative integer not yet appearing "
            "among the original facts and not yet used as a fresh witness anywhere, "
            "assigned in increasing order as existential positions are filled while "
            "walking the TGDs and facts. Do not apply any TGD to tuples you derive "
            "yourself. If a head atom duplicates one already derived, keep only one "
            "copy."
        )
        lines.append("")
        lines.append(
            "Give the complete final derived atom set (facts plus everything the "
            "chase derives) as a canonical Python list of tuples sorted "
            "lexicographically, e.g. [(0, 0, 0), (1, 4, 2), ...], integers inside "
            "each tuple, constants in ascending order."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        def norm(data):
            return sorted(tuple(int(x) for x in t) for t in data)
        try:
            user = _parse_answer(answer)
            gold = entry.metadata["derived"]
        except Exception:
            return 0.0
        return 1.0 if norm(user) == norm(gold) else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'tuple_generating_dependency_chase (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_rule_induction_r1/tuple_generating_dependency_chase',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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

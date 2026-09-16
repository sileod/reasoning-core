import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'plural_predication_readings (draw 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scope_and_binding_r1/plural_predication_readings',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class PluralConfig(Config):
    atoms: int = 2
    arity: int = 1

    def apply_difficulty(self, level):
        self.atoms = 3 + (level >= 4)
        self.arity = 1 if random.random() < 0.5 else 2


def _verdicts(masks, arity, unary, binary):
    verdicts = []
    for mask in masks:
        subset = [i for i, b in enumerate(mask) if b]
        if arity == 1:
            dist = all(unary[i] for i in subset)
            coll = any(unary[i] for i in subset)
        else:
            dist = all(any(binary[a][b] for b in subset) for a in subset)
            coll = any(binary[a][b] for a in subset for b in subset)
        verdicts.append((int(dist), int(coll), int(dist or coll)))
    return verdicts


def exact_score(answer, entry):
    if answer is None:
        return 0.0
    return 1.0 if str(answer).strip() == entry.answer.strip() else 0.0


def score_answer(answer, entry):
    return exact_score(answer, entry)


class PluralPredicationReadings(Task):
    summary = ("Classify plural predications over atom-sum models as distributive, "
               "collective, or cumulative, using forcing and neutral predicates/adverbs "
               "(gather, each, respectively); answers are the per-reading truth verdicts "
               "for 3-4 atoms and unary/binary predicates.")
    config_cls = PluralConfig
    design_choice = ("Vary the number of atoms in the model (2, 3, or 4) and the "
                     "predicate arity (unary or binary), with truth verdicts for each "
                     "reading given as a canonical triple of 0/1s.")

    def generate_entry(self):
        cfg = self.config
        atoms = cfg.atoms
        arity = cfg.arity
        unary = [random.randint(0, 1) for _ in range(atoms)]
        binary = [[random.randint(0, 1) for _ in range(atoms)] for _ in range(atoms)]
        masks = [c for c in itertools.product([0, 1], repeat=atoms) if sum(c) >= 2]
        if not masks:
            raise RuntimeError("no sums available")
        verdicts = _verdicts(masks, arity, unary, binary)
        names = [f"a{i}" for i in range(atoms)]
        sums = ["".join(n for n, b in zip(names, m) if b) for m in masks]
        answer = ";".join(f"{d},{c},{u}" for (d, c, u) in verdicts)
        for (m, v) in zip(masks, verdicts):
            recheck = _verdicts([m], arity, unary, binary)[0]
            assert tuple(recheck) == tuple(v), "verifier disagreement"
        metadata = {
            "atoms": int(atoms),
            "arity": int(arity),
            "unary_truths": [int(x) for x in unary],
            "binary_rel": [[int(x) for x in row] for row in binary],
            "sums": sums,
            "verdicts": [[int(d), int(c), int(u)] for (d, c, u) in verdicts],
            "payload": {
                "atoms": int(atoms),
                "arity": int(arity),
                "unary_truths": [int(x) for x in unary],
                "binary_rel": [[int(x) for x in row] for row in binary],
                "sums": sums,
            },
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        payload = metadata["payload"]
        atoms = payload["atoms"]
        arity = payload["arity"]
        names = [f"a{i}" for i in range(atoms)]
        lines = []
        lines.append(f"Consider a model with {atoms} atoms, and evaluate the plural "
                     f"predication over every sum of two or more of these atoms.")
        if arity == 1:
            loud = [n for n, t in zip(names, payload["unary_truths"]) if t]
            lines.append("The loud atoms are: " +
                         (", ".join(loud) if loud else "none") + ".")
            lines.append("Distributive reading holds under a sum iff every atom in the sum is "
                         "loud; collective reading holds iff at least one atom in the sum is loud.")
        else:
            rel = payload["binary_rel"]
            pairs = [f"{names[a]}R{names[b]}" for a in range(atoms) for b in range(atoms)
                     if rel[a][b]]
            lines.append("The binary relation R holds for the pairs: " +
                         (", ".join(pairs) if pairs else "none") + ".")
            lines.append("Distributive reading holds under a sum iff every atom in it bears R "
                         "to at least one atom in the same sum; collective reading holds iff at "
                         "least one atom in it bears R to another atom in the same sum.")
        lines.append("The sums under consideration are: " + ", ".join(payload["sums"]) + ".")
        lines.append("For each sum give the truth verdict triple (distributive, collective, "
                     "cumulative) as 0/1 for false/true.")
        lines.append("Cumulative is true iff distributive or collective is true.")
        lines.append("Answer with one semicolon-separated triple per sum, in the order the "
                     "sums were listed. For example 1,1,1;0,1,1 means the first sum is true on "
                     "all three readings and the second is only collectively and cumulatively true.")
        return "\n".join(lines)

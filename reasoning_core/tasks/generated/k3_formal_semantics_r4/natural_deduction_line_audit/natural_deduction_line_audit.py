import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class NDConfig(Config):
    max_premises: int = 3
    max_steps: int = 4

    def apply_difficulty(self, level):
        self.max_premises = 2 + level
        self.max_steps = 3 + level


class NaturalDeductionLineAudit(Task):
    summary = "Audit natural-deduction lines against and-elimination, implication-elimination, or-elimination and assumption discharge; answers are the first unjustified line or a validity verdict."

    config_cls = NDConfig

    def generate_entry(self):
        while True:
            entry = self._build()
            if entry is not None:
                return entry

    def _build(self):
        atoms = []
        while len(atoms) < 6:
            a = "P%d" % random.randint(1, 12)
            if a not in atoms:
                atoms.append(a)
        A, B, C = atoms[0], atoms[1], atoms[2]

        kinds = ["valid", "and"]
        if self.config.max_premises >= 3:
            kinds += ["imp", "orel"]
        kind = random.choice(kinds)
        lines = []

        def add(statement, jst):
            lines.append({"statement": statement, "jst": jst})

        if kind == "valid":
            add(A, "premise")
            add(B, "premise")
            add("%s and %s" % (A, B), "and-introduction on 1, 2")
            add(A, "and-elimination on 3")
            add("conclusion: %s" % A, "discharged from 4")
        elif kind == "and":
            add(A, "premise")
            add(B, "premise")
            add("%s and %s" % (A, B), "and-introduction on 1, 2")
            add(A, "and-elimination on 3")
            add("conclusion: %s" % A, "discharged from 4")
        elif kind == "imp":
            add("%s implies %s" % (A, B), "premise")
            add("%s implies %s" % (B, C), "premise")
            add(A, "premise")
            add(B, "implication-elimination on 1, 3")
            add(C, "implication-elimination on 2, 4")
            add("conclusion: %s" % C, "discharged from 5")
        else:
            add("%s or %s" % (A, B), "premise")
            add("%s implies %s" % (A, C), "premise")
            add("%s implies %s" % (B, C), "premise")
            add(C, "or-elimination on 1, 2, 3")
            add("%s or %s" % (C, A), "or-introduction on 4")
            add("conclusion: %s or %s" % (C, A), "discharged from 5")

        correct = True
        corrupt_idx = None
        if random.random() < 0.5:
            if kind == "valid":
                corrupt_idx = 3
                lines[3]["jst"] = "implication-elimination on 3"
            elif kind == "and":
                corrupt_idx = 2
                lines[2]["jst"] = "or-introduction on 1, 3"
            elif kind == "imp":
                corrupt_idx = 3
                lines[3]["jst"] = "and-elimination on 1, 5"
            else:
                corrupt_idx = 3
                lines[3]["jst"] = "and-elimination on 4, 5, 6"
            lines[corrupt_idx]["valid"] = False
            correct = False

        metadata = {
            "lines": ["%d. %s" % (i + 1, l["statement"]) for i, l in enumerate(lines)],
            "justifications": [l["jst"] for l in lines],
            "kind": kind,
        }

        if correct:
            answer = "VALID"
        else:
            answer = str(corrupt_idx + 1)
        metadata["answer"] = answer
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        parts = []
        for t, j in zip(metadata["lines"], metadata["justifications"]):
            parts.append("%s   (%s)" % (t, j))
        body = "\n".join(parts)
        return ("A natural-deduction proof is given, one line per numbered step, "
                "each with a rule citation in parentheses. Valid citations are: "
                "premise; and-introduction on the two conjunct-lines; and-elimination "
                "on the conjunction; implication-elimination on an implication and "
                "its antecedent; or-introduction on the disjunct-line; or-elimination "
                "on the disjunction and two implication-lines; and 'discharged from "
                "N' on a conclusion line whose target formula was derived by line N. "
                "A premise is always justified. A line is unjustified when the cited "
                "rule does not fit its formula or the cited lines.\n\n%s\n\nIs every "
                "line justified, or is there an unjustified line? If every line is "
                "justified, answer VALID. Otherwise give the number of the FIRST "
                "line (the smallest number) that has no valid justification.") % body

    def score_answer(self, answer, entry):
        try:
            gold = entry.answer
        except Exception:
            return 0.0
        if isinstance(answer, str):
            a = answer.strip().upper()
        else:
            a = str(answer).strip().upper()
        g = gold.strip().upper()
        return 1.0 if a == g else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'natural_deduction_line_audit (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_semantics_r4/natural_deduction_line_audit',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1259343118,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

"""Jev-shaped tasks: an answer that is also a typed decision, and the conventions around it.

A task is Jev-shaped when its answer is a Decision. By convention its state is metadata.payload, drawn only from
random.Random(state_seed) where state_seed is a generate_entry keyword recorded in metadata.state_seed, so
several questions over one state share a seed and any of them regenerates from (level, seed). Task's default
render_prompt shows the state and Decision.prompt(); the default score_answer (exact string) already fits, since
the prompt names the exact answer strings. jev_row() exports an entry to the jev-bench schema.
"""
import json
from collections.abc import Mapping


class Decision(str):
    """An answer that is also a Jev-style decision: a typed question (`type` choice / noul / score,
    `instructions`, `criteria`), the chosen `label`, and optionally `soft`, the exact distribution in
    jev-bench's shapes: P(yes) for noul, {option: p} for choice, [p per level] for score.

    It IS the answer string -- the label for choice, "Yes"/"No" for noul, the level index for score -- so
    training, scoring and serialization see a plain str; generate_example writes it to metadata.decision and
    Entry.from_dict restores it.
    """
    TYPES = ("choice", "noul", "score")

    def __new__(cls, label, *, instructions, criteria=None, type="choice", soft=None):
        if type == "noul":
            label = str(label).lower() in ("1", "true", "yes")
            text, options = ("Yes" if label else "No"), [True, False]
        elif type == "score":
            label, options = int(label), range(len(criteria))
            text = str(label)
        elif type == "choice":
            label = text = str(label)
            options = list(criteria)
        else:
            raise ValueError(f"Decision type must be one of {cls.TYPES}, got {type!r}")
        if label not in options:
            raise ValueError(f"Decision label {label!r} is not one of the options {list(options)}")
        mass = soft if type == "noul" else 1 if soft is None else sum(
            soft.values() if isinstance(soft, Mapping) else soft)
        if soft is not None and not (0 <= mass <= 1 if type == "noul" else abs(mass - 1) < 1e-6):
            raise ValueError(f"Decision soft labels must be a probability distribution, got {soft!r}")
        obj = super().__new__(cls, text)
        obj.label, obj.soft = label, soft
        obj.question = {"type": type, "instructions": instructions, "criteria": criteria}
        return obj

    def prompt(self):
        """The question as a plain model is asked it: the instructions and the exact answer format."""
        q = self.question
        levels = q["criteria"] if q["type"] == "score" else []
        plain = all(str(c).split()[0] == str(i) for i, c in enumerate(levels))   # "0", "1", ..., "9 or more"
        capped = "".join(f" ({i} means {c})" for i, c in enumerate(levels) if plain and str(c) != str(i))
        fmt = ("Answer Yes or No." if q["type"] == "noul" else
               f"Answer with a number from 0 to {len(levels) - 1}{capped}." if q["type"] == "score" and plain else
               "Answer with the level number: " + "; ".join(f"{i} = {str(c).rstrip('.')}" for i, c in
                                                             enumerate(levels)) + "."
               if q["type"] == "score" else "Answer with one of: " + ", ".join(q["criteria"]) + ".")
        return f"{q['instructions']}\n{fmt}"

    def to_dict(self):
        return {"question": self.question, "label": self.label, "soft": self.soft}

    @classmethod
    def from_dict(cls, d):
        q = d["question"]
        return cls(d["label"], instructions=q["instructions"], criteria=q["criteria"], type=q["type"],
                   soft=d.get("soft"))

    def __reduce__(self):  # str subclasses with keyword-only __new__ do not pickle by default
        return Decision.from_dict, (self.to_dict(),)


def jev_row(entry, split="train"):
    """A Jev-shaped entry as a row of the jev-bench schema (every field a string). The id's first three
    `:` fields name the state group -- task, level and state_seed -- as tasksource's grouped Jev rows do."""
    d, m = entry.answer, entry.metadata
    group = f"{entry.task}:{m.get('_level')}:{m.get('state_seed')}"
    return {"id": f"{group}:{split}:{m.get('_deduplication_key') or ''}", "task": entry.task,
            "primitive": d.question["type"], "state": json.dumps(m.payload),
            "question": json.dumps({k: v for k, v in d.question.items() if v is not None}),
            "label": {True: "1", False: "0"}.get(d.label, str(d.label)),
            "soft_label": "" if d.soft is None else json.dumps(d.soft)}


def render_records(records, style):
    """Flat records as JSON, a Markdown table, CSV, or key=value lines: one state, several surface forms."""
    columns = list(records[0])
    if style == "json":
        return json.dumps(records, ensure_ascii=False)
    if style == "table":
        rows = [" | ".join(str(r[c]) for c in columns) for r in records]
        return "\n".join([" | ".join(columns), " | ".join("---" for _ in columns), *rows])
    if style == "csv":
        return "\n".join([",".join(columns), *(",".join(str(r[c]) for c in columns) for r in records)])
    return "\n".join("; ".join(f"{c}={r[c]}" for c in columns) for r in records)

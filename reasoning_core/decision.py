"""Jev-shaped tasks: an answer that is also a typed decision, and the conventions around it.

A task is Jev-shaped when its answer is a Decision. By convention its state is metadata.payload, drawn only from
random.Random(state_seed) where state_seed is a generate_entry keyword recorded in metadata.state_seed, so
several questions over one state share a seed and any of them regenerates from (level, seed); pose() builds the
entry and lists the state's question ids. Task's default render_prompt shows the state and Decision.prompt(); the
default score_answer (exact string) already fits, since the prompt names the exact answer strings. jev_row()
exports an entry to the jev-bench schema, jev_request() a whole state to the Jev / Kev request schema.
"""
import json
import random
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


def pose(questions, payload, state_seed, question=None, **metadata):
    """The entry asking one of a state's `questions` ({question_id: Decision}): `question`, or one drawn with the
    ordinary RNG. metadata.question_ids lists them all, so an exporter can ask every question of the state."""
    from .template import Entry   # template imports this module
    qid = question or random.choice(sorted(questions))
    if qid not in questions:
        raise KeyError(f"question {qid!r} is not asked of this state; it asks {sorted(questions)}")
    return Entry({"payload": payload, "state_seed": state_seed, "question_id": qid,
                  "question_ids": sorted(questions), **metadata}, questions[qid])


def jev_request(task, state_seed, level=0):
    """One state of a Jev-shaped task with every question asked of it, as a labelled Jev / Kev request:
    {"state", "questions": {id: {type, instructions, criteria, label, target}}, "_meta"}. Labels follow the API: the
    option name (choice), a bool (noul), the level index (score); `target`, the soft label keyed the same way, is
    there when the task has one."""
    first = task.generate_example(level=level, state_seed=state_seed)
    entries = {first.metadata.question_id: first}
    for qid in first.metadata.question_ids:
        if qid not in entries:
            entries[qid] = task.generate_example(level=level, state_seed=state_seed, question=qid)
    questions = {}
    for qid, entry in sorted(entries.items()):
        d = entry.answer
        q = {**{k: v for k, v in d.question.items() if v is not None}, "label": d.label}
        if d.soft is not None:
            q["target"] = ({"true": d.soft, "false": round(1 - d.soft, 6)} if q["type"] == "noul" else
                           {str(i): p for i, p in enumerate(d.soft)} if q["type"] == "score" else dict(d.soft))
        questions[qid] = q
    return {"state": json.loads(json.dumps(first.metadata.payload)), "questions": questions,
            "_meta": {"source": first.task, "group_id": f"{first.task}:{level}:{state_seed}"}}


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

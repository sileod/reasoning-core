"""Named-dimension profiles of generated examples, answered by cheap judges.

An embedding model returns numbers that mean nothing. Here every coordinate is a question
with a name -- "does solving it need many sequential steps?" -- answered with a probability
by a decision model such as Jev (fractions of a cent, a third of a second). The answers are
the vector, so a match or a correlation can be read, and a new dimension is a new question.

One state per example: the rendered prompt and the generator's reference answer. The answer
is there because a generator can be wrong, and `correct` is how that shows: a low p(correct)
is an adjudication target, not a verdict, since Jev does not do arithmetic.

Examples are stored with their profiles, so a dimension added later is asked of the same
examples rather than of new draws, and a judge that fails (Span's free tier has a daily
cap) leaves its own columns empty without holding up the others.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
from pathlib import Path
import random

from .judge import Question, make_judge

MAX_STATE_CHARS = 60_000   # Jev reads 32k tokens; a prompt past this is not one we ship
# Per example, not the task's own allowance: lean_candidate_compilation waited 35 minutes on
# a Lean REPL importing Mathlib over NFS, and the generator retries its deadline ten times.
SAMPLE_SECONDS = 30


@dataclass(frozen=True)
class Dimension:
    """A question whose answer distribution reduces to one number in [0, 1].

    The value is the probability mass on each choice times that choice's weight; by default
    the first choice weighs 1 and every other 0, so a yes/no question reads as p(yes).
    """

    name: str
    question: str
    choices: tuple = ("yes", "no")
    weights: tuple = ()

    def question_(self):
        return Question(self.name, self.question, self.choices)

    def value(self, probs):
        if not probs:
            return None
        weights = self.weights or (1.0,) + (0.0,) * (len(self.choices) - 1)
        return sum(probs.get(choice, 0.0) * weight
                   for choice, weight in zip(self.choices, weights))


DIMENSIONS = (
    Dimension("glance", "Could a capable language model state the correct final answer "
              "immediately, from recognition alone, with no written working?"),
    Dimension("ease", "How hard is this problem to answer correctly without writing any "
              "working?", ("easy", "medium", "hard"), (1.0, 0.5, 0.0)),
    Dimension("steps", "Does solving the problem require many sequential reasoning steps "
              "(more than five)?"),
    Dimension("state", "Does solving the problem require keeping track of changing state or "
              "many intermediate values?"),
    Dimension("arithmetic", "Does solving the problem require nontrivial arithmetic?"),
    Dimension("formal", "Is the problem written mainly in formal notation (symbols, code, "
              "logic formulas) rather than natural language?"),
    Dimension("realistic", "Does the problem read like a realistic question a person might "
              "ask, set in a real-world context?"),
    Dimension("exam", "Does the problem resemble a question from a standard exam or "
              "benchmark (math competition, logic puzzle, reading comprehension)?"),
    Dimension("shortcut", "Could the answer be guessed or found by a superficial shortcut "
              "without truly solving the problem?"),
    Dimension("wellposed", "Is the problem clear, well-posed and unambiguous, with exactly "
              "one correct answer?"),
    Dimension("format", "Does the problem state exactly what form the answer must take?"),
    Dimension("general", "Does solving the problem exercise a general reasoning skill that "
              "would help on many other kinds of problems?"),
    Dimension("knowledge", "Does solving the problem require outside world knowledge beyond "
              "what the problem states?"),
    Dimension("code", "Does the problem involve reading, writing or executing program code?"),
    Dimension("correct", "Is the REFERENCE ANSWER a correct answer to the PROBLEM?"),
)


def state_of(example):
    return (f"PROBLEM:\n{example['prompt']}\n\n"
            f"REFERENCE ANSWER:\n{example['answer']}")[:MAX_STATE_CHARS]


def sample(task_name, level, n, seed):
    """n examples of one task at one level, reproducibly. Main thread only: the generator's
    deadline is a signal."""
    import reasoning_core

    random.seed(f"{seed}:{task_name}:{level}")
    task = reasoning_core.get_task(task_name)
    examples = [task.generate_example(level=level, timeout=SAMPLE_SECONDS) for _ in range(n)]
    # The metadata rides along so a task's own scorer can judge an answer later.
    return task.behavior_hash(), [
        {"prompt": example.prompt, "answer": str(example.answer),
         "metadata": json.loads(json.dumps(example.metadata, default=str))}
        for example in examples]


def profile(example, judges, dimensions=DIMENSIONS):
    """{judge name: {dimension: value or None}}, each judge asked independently."""
    questions = [dimension.question_() for dimension in dimensions]
    state = state_of(example)
    with ThreadPoolExecutor(len(judges)) as pool:
        asked = {name: pool.submit(judge.evaluate, state, questions)
                 for name, judge in judges.items()}
    return {name: {dimension.name: dimension.value(future.result()[dimension.name]["probs"])
                   for dimension in dimensions}
            for name, future in asked.items()}


def _missing(row, judges, dimensions):
    """Judges owing an answer. A judge may declare what it `answers` (Span: two-way only);
    one that cannot answer a dimension is never asked it again."""
    have = row.get("signals") or {}
    return {name for name, judge in judges.items()
            if any((have.get(name) or {}).get(d.name) is None
                   and getattr(judge, "answers", lambda _: True)(d.question_())
                   for d in dimensions)}


def collect(tasks, out, *, levels=(0, 2, 4, 6), n=3, seed=43, judges=("jev", "span"),
            dimensions=DIMENSIONS, workers=8, log=lambda line: print(line, flush=True)):
    """Sample, profile and store every (task, level); resumable, and re-asks only the gaps.

    `out` is JSONL, one row per example. A row missing a judge's answer to any dimension --
    a new dimension, or a judge that was down last time -- is asked again by that judge.
    """
    out = Path(out)
    rows = {}
    if out.exists():
        for line in out.read_text().splitlines():
            row = json.loads(line)
            rows[(row["task"], row["level"], row["index"])] = row
    sampled = {key[:2] for key in rows}
    broken = {row["task"] for row in rows.values() if "error" in row}
    judges = {name: make_judge(name) for name in judges}

    def ask(row):
        needed = _missing(row, judges, dimensions)
        if needed:
            fresh = profile(row, {name: judges[name] for name in needed}, dimensions)
            signals = row.setdefault("signals", {})
            for name, values in fresh.items():   # an abstention never erases an answer
                signals.setdefault(name, {}).update(
                    {key: value for key, value in values.items() if value is not None})
        return row

    with ThreadPoolExecutor(workers) as pool:
        for task_name in tasks:
            for level in levels:
                if task_name in broken:
                    break
                if (task_name, level) not in sampled:
                    try:
                        behavior, examples = sample(task_name, level, n, seed)
                    except Exception as error:  # noqa: BLE001 - a broken generator is data
                        rows[(task_name, level, -1)] = {
                            "task": task_name, "level": level, "index": -1,
                            "error": f"{type(error).__name__}: {error}"[:300]}
                        broken.add(task_name)   # one failure per task: higher levels cost more
                        continue
                    for index, example in enumerate(examples):
                        rows[(task_name, level, index)] = {
                            "task": task_name, "level": level, "index": index,
                            "behavior_hash": behavior, **example}
            mine = [row for key, row in rows.items() if key[0] == task_name and "prompt" in row]
            list(pool.map(ask, mine))
            _write(out, rows.values())
            log(f"  {task_name}: {len(mine)} examples")
    return list(rows.values())


def _write(path, rows):
    staged = path.with_suffix(path.suffix + ".tmp")
    staged.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    staged.replace(path)

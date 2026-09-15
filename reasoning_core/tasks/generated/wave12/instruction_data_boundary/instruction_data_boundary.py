import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


QUOTES = ['"', "'"]

VERBS = [
    "say", "repeat", "write", "type", "print", "list", "count", "report",
    "translate", "reverse", "capitalize", "shout", "whisper", "read", "spell",
]

NORMS = [
    "as quickly as you can",
    "after a brief pause",
    "without thinking",
    "in a calm voice",
    "if it is not too much trouble",
]


@dataclass
class BoundaryConfig(Config):
    quote_index: int = 0
    num_nouns: int = 3
    has_wrap: bool = False

    def apply_difficulty(self, level):
        self.quote_index = level % 2
        self.num_nouns = 2 + level
        self.has_wrap = level >= 3


def _make_verb():
    return random.choice(VERBS)


def _make_command():
    verb = _make_verb()
    noun = random.choice(["message", "token", "phrase", "term", "word", "string"])
    return f"{verb} the {noun}"


def _make_wrap():
    return random.choice(["ahead of the rest", "before continuing", "and nothing else"])


def _wrap_command(cmd, wrap):
    return f"{cmd} {wrap}"


class InstructionDataBoundary(Task):
    summary = "Process quoted text containing commands without treating those commands as instructions; vary quoted command contents, quote marks, verb/noun phrasing, surrounding nouns and prefix/suffix wrapping across levels."
    design_choice = ("Instances are conversational turns where a quoted command sits inside a user "
                     "utterance, and the model must output the exact quoted substring without executing it.")
    config_cls = BoundaryConfig

    def generate_entry(self):
        q = QUOTES[self.config.quote_index]
        cmd = _make_command()
        if self.config.has_wrap:
            cmd = _wrap_command(cmd, _make_wrap())
        quoted = f"{q}{cmd}{q}"

        filler = random.sample(
            ["please", "kindly", "go on", "if you can", "for now", "next"],
            min(2, self.config.num_nouns - 1),
        )
        before = " ".join(filler)

        nouns = random.sample(
            ["line", "sentence", "reply", "turn", "note", "comment"],
            min(self.config.num_nouns, 6),
        )
        after = " ".join(nouns)

        prompt = f"{before} {quoted} {after}".strip()
        if random.random() < 0.5:
            prompt = f'User said "{prompt}". What was the quoted command?'
        else:
            prompt = f'In the message "{prompt}", copy the quoted command exactly.'

        return Entry(
            metadata={"quoted": quoted, "prompt": prompt},
            answer=cmd,
        )

    def render_prompt(self, metadata):
        return metadata["prompt"]

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            answer = str(answer)
        answer = answer.strip()
        if answer == gold:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'instruction_data_boundary (draw 1 of 3)',
 'hypothesis': 'ASTRA0:instruction_data_boundary',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/instruction_data_boundary',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1356906099,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

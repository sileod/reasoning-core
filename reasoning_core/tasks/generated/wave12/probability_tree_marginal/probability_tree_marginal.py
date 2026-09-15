import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'probability_tree_marginal (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:probability_tree_marginal',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/probability_tree_marginal',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3139243041,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_OUTCOME_NAMES = [
    "heads", "tails",
    "rain", "sun",
    "left", "right",
    "up", "down",
    "red", "blue",
    "hot", "cold",
    "high", "low",
    "win", "loss",
    "east", "west",
]

_STATE_LETTERS = ["A", "B", "C", "D", "E"]


@dataclass
class MarginalConfig(Config):
    steps: int = 2
    states: int = 3
    branches: int = 2

    def apply_difficulty(self, level):
        self.steps = 2 + level
        self.states = 3
        self.branches = 2 if level < 3 else 3


def _frac(s):
    if "/" in s:
        a, b = s.split("/")
        return Fraction(int(a), int(b))
    return Fraction(int(s))


def _frac_str(fr):
    if fr.denominator == 1:
        return str(fr.numerator)
    return "%d/%d" % (fr.numerator, fr.denominator)


def _build_transition(states, branches):
    """Return (trans, names). trans[i] = list of (name, prob_frac, next_state)."""
    names = {}
    trans = []
    for i in range(states):
        dens = random.choice([2, 3, 4])
        weights = [random.randint(1, dens - 1) for _ in range(branches)]
        if sum(weights) == 0:
            weights[0] = 1
        total = sum(weights)
        row = []
        for b in range(branches):
            p = Fraction(weights[b], total)
            nxt = random.randrange(states)
            name = _OUTCOME_NAMES[random.randrange(len(_OUTCOME_NAMES))]
            row.append((name, p, nxt))
        trans.append(row)
    return trans


class ProbabilityTreeMarginal(Task):
    summary = (
        "Evaluate multi-step branching Markov processes with state-dependent "
        "named outcomes and conditional rational transition probabilities over "
        "a small state space, returning the exact probability of reaching a "
        "target state at a fixed horizon as a reduced fraction."
    )
    design_choice = (
        "Answer as an exact reduced fraction, with the process described by "
        "a sequence of named branch outcomes and their conditional probabilities."
    )

    config_cls = MarginalConfig

    def generate_entry(self):
        cfg = self.config
        states = cfg.states
        branches = cfg.branches
        steps = cfg.steps
        start = 0

        trans = _build_transition(states, branches)
        for i in range(states):
            s = sum(p for (_, p, _) in trans[i])
            assert s == 1, "rows must sum to 1"

        target = random.randrange(states)

        dp_cur = [Fraction(0)] * states
        dp_cur[start] = Fraction(1)
        for _ in range(steps):
            dp_next = [Fraction(0)] * states
            for i in range(states):
                for (_, p, j) in trans[i]:
                    dp_next[j] += dp_cur[i] * p
            dp_cur = dp_next
        prob = dp_cur[target]
        assert 0 <= prob <= 1, "probability must lie in [0,1]"

        name_map = {i: _STATE_LETTERS[i] for i in range(states)}
        trans_json = []
        for i in range(states):
            row = []
            for (nm, p, nxt) in trans[i]:
                row.append([nm, _frac_str(p), name_map[nxt]])
            trans_json.append({"from": name_map[i], "outcomes": row})

        metadata = {
            "states": states,
            "steps": steps,
            "start": name_map[start],
            "target": name_map[target],
            "transitions": trans_json,
            "answer_frac": _frac_str(prob),
        }
        ans = _frac_str(prob)
        return Entry(metadata=metadata, answer=ans)

    def render_prompt(self, metadata):
        lines = []
        lines.append(
            "A discrete-time branching process starts in state %s. At each step "
            "the current state moves to exactly one of its outcomes, drawn with "
            "the listed conditional probability, and the state changes to the "
            "outcome's destination. The transitions are independent across "
            "steps. The states and their conditional transitions are:"
            % metadata["start"]
        )
        for t in metadata["transitions"]:
            parts = ", ".join(
                "to %s with probability %s (outcome %s)" % (o[2], o[1], o[0])
                for o in t["outcomes"]
            )
            lines.append("- From state %s: %s." % (t["from"], parts))
        lines.append(
            "What is the exact probability, as a reduced fraction p/q, that the "
            "process is in state %s after %d steps? Give only the fraction."
            % (metadata["target"], metadata["steps"])
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = _frac(entry.answer)
        candidate = _fraction_of(answer)
        if candidate is None:
            return 0.0
        return 1.0 if candidate == gold else 0.0


def _fraction_of(answer):
    if answer is None:
        return None
    s = str(answer).strip()
    try:
        if "/" in s:
            a, b = s.split("/")
            return Fraction(int(a.strip()), int(b.strip()))
        return Fraction(int(s))
    except Exception:
        return None

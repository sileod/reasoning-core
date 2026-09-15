import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class MealyCompositionConfig(Config):
    num_states: int = 2
    alphabet_size: int = 3
    word_len: int = 3

    def apply_difficulty(self, level):
        self.num_states = min(4, 2 + level // 2)
        self.alphabet_size = min(5, 3 + level // 3)
        self.word_len = 3 + level


_SYMBOLS = "abcdefghij"


def _build_machine(num_states, alphabet_size):
    symbols = list(_SYMBOLS[:alphabet_size])
    trans = {}
    for s in range(num_states):
        for sym in symbols:
            nxt = random.randrange(num_states)
            out = random.choice(symbols)
            trans[(s, sym)] = (nxt, out)
    return symbols, trans


def _run(trans, start_state, word):
    out = []
    state = start_state
    for sym in word:
        nxt, osym = trans[(state, sym)]
        out.append(osym)
        state = nxt
    return "".join(out), state


def _render_machine(trans, num_states):
    rows = []
    for s in range(num_states):
        for sym in _SYMBOLS:
            if (s, sym) in trans:
                nxt, osym = trans[(s, sym)]
                rows.append(f"({s},{sym})->({nxt},{osym})")
    return rows


class MealyCompositionRun(Task):
    summary = "Pipe one Mealy machine's emitted word into a second machine over a shared output/input alphabet, tracking each machine's state and emission table, returning the final cascaded output word and state pair."
    design_choice = "Represent machines as explicit transition tables mapping (state, symbol) to (next state, output symbol), with instances given as two tables and an input word."
    config_cls = MealyCompositionConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        symbols_a, ta = _build_machine(cfg.num_states, cfg.alphabet_size)
        symbols_b, tb = _build_machine(cfg.num_states, cfg.alphabet_size)
        nsa_actual = cfg.num_states
        nsb_actual = cfg.num_states
        word = [random.choice(symbols_a) for _ in range(cfg.word_len)]
        w1, sa = _run(ta, 0, word)
        w2, sb = _run(tb, 0, w1)

        assert all(c in symbols_a for c in w1)
        assert all(c in symbols_b for c in w2)
        assert 0 <= sa < nsa_actual and 0 <= sb < nsb_actual

        trans_a = [[s, sym, ta[(s, sym)][0], ta[(s, sym)][1]] for s in range(nsa_actual) for sym in _SYMBOLS[: cfg.alphabet_size]]
        trans_b = [[s, sym, tb[(s, sym)][0], tb[(s, sym)][1]] for s in range(nsb_actual) for sym in _SYMBOLS[: cfg.alphabet_size]]

        metadata = {
            "num_states_a": nsa_actual,
            "num_states_b": nsb_actual,
            "alphabet": list(_SYMBOLS[: cfg.alphabet_size]),
            "input_word": "".join(word),
            "trans_a": trans_a,
            "trans_b": trans_b,
            "answer_word": w2,
            "answer_state_a": sa,
            "answer_state_b": sb,
        }
        answer = f"{w2};{sa};{sb}"
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        lines.append(
            f"Two Mealy machines A and B share the input/output alphabet "
            f"{{{', '.join(metadata['alphabet'])}}}. "
            f"Machine A has states 0..{metadata['num_states_a'] - 1} and machine B has states "
            f"0..{metadata['num_states_b'] - 1}."
        )
        lines.append("Machine A transitions (state,symbol)->(next state, output symbol):")
        lines.append(", ".join(_render_machine({tuple(t[:2]): (t[2], t[3]) for t in metadata['trans_a']}, metadata['num_states_a'])))
        lines.append("Machine B transitions (state,symbol)->(next state, output symbol):")
        lines.append(", ".join(_render_machine({tuple(t[:2]): (t[2], t[3]) for t in metadata['trans_b']}, metadata['num_states_b'])))
        lines.append(f"Both machines start in state 0.")
        lines.append(
            f"Feed the input word '{metadata['input_word']}' into machine A, reading one symbol "
            f"per step and emitting its output symbol each step. Then feed machine A's emitted "
            f"word into machine B, again starting in state 0. Track each machine's state after "
            f"processing every symbol of its consumed word."
        )
        lines.append(
            "Answer as the final output word produced by machine B, a semicolon, machine A's "
            "final state, a semicolon, then machine B's final state. For example 'abc;1;0' means "
            "machine B emitted 'abc', machine A ended in state 1, and machine B ended in state 0."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        parts = answer.split(";")
        if len(parts) != 3:
            return 0.0
        w, sa, sb = parts[0], parts[1], parts[2]
        gold_w = entry.metadata["answer_word"]
        if sorted(w) != sorted(gold_w):
            return 0.0
        try:
            ia, ib = int(sa), int(sb)
        except (TypeError, ValueError):
            return 0.0
        if w != gold_w or ia != entry.metadata["answer_state_a"] or ib != entry.metadata["answer_state_b"]:
            return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'mealy_composition_run (draw 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/mealy_composition_run',
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

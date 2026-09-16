import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'mealy_moore_machine_conversion (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relational_structures_r1/mealy_moore_machine_conversion',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "a canonical table string listing each state's row as 'state:input1->next,output;input2->next,output' with states renamed S0,S1,..."


@dataclass
class MealyMooreConfig(Config):
    num_states: int = 2
    num_inputs: int = 2

    def apply_difficulty(self, level):
        self.num_states = 2 + level
        self.num_inputs = 2 if level < 3 else 3


def _s(idx):
    return f"S{idx}"


def _freeze(pairs):
    return tuple(pairs)


def mealy_to_moore(n, m, transitions):
    """transitions[s][i] = (next_state, output). Returns (moore_trans, moore_out)
    where moore states are ordered and each is a (mealy_state, output) pair.
    Standard construction: new state for each (q, b) where b is the output on an
    entering edge; plus a start state for q0 whose output equals a reference output.
    Two edges entering the same mealy state with different outputs become distinct
    Moore states, so the model is well defined.
    """
    start_out = transitions[0][0][1]
    states = []          # list of keys: ('start',) or (mealy_state, output)
    idx = {}
    states.append(('start',))
    idx[('start',)] = 0
    out = [start_out]
    moore_trans = []
    frontier = [('start',)]
    k = 0
    while k < len(frontier):
        key = frontier[k]
        k += 1
        if key[0] == 'start':
            src = 0
        else:
            src, _ = key
        row = []
        for i in range(m):
            nxt, o = transitions[src][i]
            nkey = (nxt, o)
            if nkey not in idx:
                idx[nkey] = len(states)
                states.append(nkey)
                out.append(o)
                frontier.append(nkey)
            row.append(idx[nkey])
        moore_trans.append(row)
    return moore_trans, out


def moore_to_mealy(moore_trans, moore_out, m):
    """mealy_trans[s][i] = (next_state, output) where output = output of next state."""
    mealy = []
    for s in range(len(moore_trans)):
        row = []
        for i in range(m):
            nxt = moore_trans[s][i]
            row.append((nxt, moore_out[nxt]))
        mealy.append(row)
    return mealy


def render_mealy(trans, m):
    rows = []
    for s in range(len(trans)):
        parts = []
        for i in range(m):
            nxt, o = trans[s][i]
            parts.append(f"{i}->{_s(nxt)},{o}")
        rows.append(f"{_s(s)}:{';'.join(parts)}")
    return "|".join(rows)


def render_moore(moore_trans, moore_out, m):
    rows = []
    for s in range(len(moore_trans)):
        parts = []
        for i in range(m):
            nxt = moore_trans[s][i]
            parts.append(f"{i}->{_s(nxt)},{moore_out[nxt]}")
        rows.append(f"{_s(s)}:{';'.join(parts)}")
    return "|".join(rows)


class MealyMooreMachineConversion(Task):
    summary = ("Convert Mealy machines to equivalent Moore machines and back, splitting "
               "states so every input-output trace is preserved across varied alphabets; "
               "answer the converted transition/output table.")
    config_cls = MealyMooreConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.num_states
        m = self.config.num_inputs
        direction = random.choice(['mealy_to_moore', 'moore_to_mealy'])
        label_balance = bool(random.getrandbits(1))

        if direction == 'mealy_to_moore':
            while True:
                transitions = []
                for s in range(n):
                    row = []
                    for i in range(m):
                        row.append((random.randrange(n), random.choice(['0', '1'])))
                    transitions.append(row)
                moore_trans, moore_out = mealy_to_moore(n, m, transitions)
                if _verify_m2m(n, m, transitions, moore_trans, moore_out):
                    break
            prompt_table = render_mealy(transitions, m)
            answer = render_moore(moore_trans, moore_out, m)
            metadata = {
                "direction": "mealy_to_moore",
                "num_states": n,
                "num_inputs": m,
                "presented": transitions,
            }
        else:
            while True:
                moore_trans = []
                for s in range(n):
                    moore_trans.append([random.randrange(n) for _ in range(m)])
                moore_out = [random.choice(['0', '1']) for _ in range(n)]
                mealy = moore_to_mealy(moore_trans, moore_out, m)
                if _verify_m2o(n, m, moore_trans, moore_out, mealy):
                    break
            prompt_table = render_moore(moore_trans, moore_out, m)
            answer = render_mealy(mealy, m)
            metadata = {
                "direction": "moore_to_mealy",
                "num_states": n,
                "num_inputs": m,
                "presented": moore_trans,
                "moore_outputs": moore_out,
            }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        if metadata["direction"] == "mealy_to_moore":
            return (
                f"A Mealy machine has states and outputs on each transition "
                f"({metadata['num_inputs']} inputs, inputs labeled 0..{metadata['num_inputs'] - 1}). "
                f"Its transition/output table is:\n{metadata['presented']}\n"
                f"Convert it to an equivalent Moore machine by splitting states so every "
                f"input-output trace is preserved. Give the resulting Moore table, each row as "
                f"'state:input->next,output' (separate inputs with ';', rows with '|'), states "
                f"renamed S0,S1,... in the order you create them."
            )
        else:
            out_block = ", ".join(
                f"S{i}:{out}" for i, out in enumerate(metadata["moore_outputs"])
            )
            return (
                f"A Moore machine has an output attached to each state "
                f"({metadata['num_inputs']} inputs, inputs labeled "
                f"0..{metadata['num_inputs'] - 1}). Its per-state outputs are: "
                f"{out_block}. Its transition table lists each state's successors by input:\n"
                f"{metadata['presented']}\n"
                f"Convert it to an equivalent Mealy machine (output on each transition). "
                f"Give the resulting Mealy table, each row as 'state:input->next,output' "
                f"(separate inputs with ';', rows with '|'), states named S0,S1,..."
            )

    def score_answer(self, answer, entry):
        metadata = entry["metadata"]
        gold = entry["answer"]
        if not isinstance(answer, str):
            return 0.0
        if answer.strip() == gold.strip():
            return 1.0
        return normalized_match(answer, gold)


def _verify_m2m(n, m, transitions, moore_trans, moore_out):
    """Check the Moore machine reproduces mealy outputs on words of length up to 4."""
    for length in range(1, 5):
        for _ in range(20):
            word = [random.randrange(m) for _ in range(length)]
            st = 0
            mo = []
            for i in word:
                st, o = transitions[st][i]
                mo.append(o)
            cur = 0
            seq = [moore_out[cur]]
            for i in word:
                cur = moore_trans[cur][i]
                seq.append(moore_out[cur])
            if seq[1:] != mo:
                return False
    return True


def _verify_m2o(n, m, moore_trans, moore_out, mealy):
    """Check the Mealy machine reproduces moore outputs (offset by one) on words."""
    for length in range(1, 5):
        for _ in range(20):
            word = [random.randrange(m) for _ in range(length)]
            cur = 0
            mo = []
            for i in word:
                mo.append(moore_out[cur])
                cur = moore_trans[cur][i]
            mo.append(moore_out[cur])
            st = 0
            mw = []
            for i in word:
                nxt, o = mealy[st][i]
                st = nxt
                mw.append(o)
            if mw != mo[:-1]:
                return False
    return True


def normalized_match(answer, gold):
    """Normalize whitespace and compare row-wise to tolerate minor spacing."""
    norm_a = "".join(answer.split())
    norm_g = "".join(gold.split())
    return 1.0 if norm_a == norm_g else 0.0

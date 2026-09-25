import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class CoarseStateAutonomyConfig(Config):
    fine_states: int = 6
    coarse_states: int = 2

    def apply_difficulty(self, level):
        self.fine_states = stochastic_rounding(4 + level * 2)
        self.coarse_states = max(2, int(round(self.fine_states / 3)))


def _closed(agg, t, fine_states, coarse_states):
    for c in range(coarse_states):
        block = [f for f in range(fine_states) if agg[f] == c]
        if not block:
            continue
        first = agg[t[block[0]]]
        for f in block[1:]:
            if agg[t[f]] != first:
                return False
    return True


def _block_outputs(agg, t, c, fine_states):
    outs = set()
    for f in range(fine_states):
        if agg[f] == c:
            outs.add(agg[t[f]])
    return outs


def _build_agg(fine_states, coarse_states):
    while True:
        agg = [random.randrange(coarse_states) for _ in range(fine_states)]
        if len(set(agg)) == coarse_states:
            return agg


def _build_regular_t(agg, t, fine_states, coarse_states):
    coarse_t = [random.randrange(coarse_states) for _ in range(coarse_states)]
    for f in range(fine_states):
        target_c = coarse_t[agg[f]]
        candidates = [g for g in range(fine_states) if agg[g] == target_c]
        t[f] = random.choice(candidates)
    return coarse_t


def _closed_instance(fine_states, coarse_states):
    agg = _build_agg(fine_states, coarse_states)
    t = [0] * fine_states
    _build_regular_t(agg, t, fine_states, coarse_states)
    return agg, t


def _nonclosed_instance(fine_states, coarse_states):
    for attempt in range(60):
        agg = _build_agg(fine_states, coarse_states)
        t = [0] * fine_states
        _build_regular_t(agg, t, fine_states, coarse_states)
        blocks = {}
        for f in range(fine_states):
            blocks.setdefault(agg[f], []).append(f)
        big = [c for c, b in blocks.items() if len(b) >= 2]
        if not big:
            continue
        c = random.choice(big)
        f0, other = random.sample(blocks[c], 2)
        if agg[t[f0]] == agg[t[other]]:
            other_out = agg[t[other]]
            candidates = [g for g in range(fine_states) if agg[g] != other_out]
            t[f0] = random.choice(candidates)
        if not _closed(agg, t, fine_states, coarse_states):
            return agg, t
    return None


def _witness_strings(agg, t, fine_states, coarse_states):
    meta = {"agg": agg, "t": t}
    ws = []
    for f in range(fine_states):
        if _block_outputs(agg, t, agg[f], fine_states).__len__() < 2:
            continue
        ws.append((f, agg[t[f]]))
    return ws


class CoarseStateAutonomy(Task):
    summary = ("Given fine-state transitions and a fixed aggregation map, determine whether "
               "aggregate states evolve without hidden detail: output 'closed' or a witness pair "
               "(fine state, aggregate state) where the aggregate update is ambiguous.")
    config_cls = CoarseStateAutonomyConfig
    design_choice = ("Instances provide a fixed aggregation map and a sequence of fine-state transitions; "
                     "the solver must output 'closed' or a witness pair (fine state, aggregate state) "
                     "where the aggregate update is ambiguous.")

    def generate_entry(self):
        cfg = self.config
        fine_states = cfg.fine_states
        coarse_states = cfg.coarse_states

        which = random.random() < 0.25
        if which:
            agg, t = _closed_instance(fine_states, coarse_states)
            answer = "closed"
        else:
            inst = None
            for _ in range(60):
                inst = _nonclosed_instance(fine_states, coarse_states)
                if inst is not None:
                    break
            if inst is None:
                agg, t = _closed_instance(fine_states, coarse_states)
                answer = "closed"
                which = True
            else:
                agg, t = inst
                if not _closed(agg, t, fine_states, coarse_states):
                    ws = _witness_strings(agg, t, fine_states, coarse_states)
                    f, c = random.choice(ws)
                    answer = f"{f},{c}"
                else:
                    answer = "closed"
                    which = True

        metadata = {
            "fine_states": fine_states,
            "coarse_states": coarse_states,
            "agg": agg,
            "fine_t": t,
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        fine_states = metadata["fine_states"]
        coarse_states = metadata["coarse_states"]
        agg_txt = ", ".join(f"{f}:{metadata['agg'][f]}" for f in range(fine_states))
        t_txt = ", ".join(f"{f}:{metadata['fine_t'][f]}" for f in range(fine_states))
        return (
            f"There are {fine_states} fine states 0..{fine_states - 1} and {coarse_states} "
            f"aggregate states 0..{coarse_states - 1}. The aggregation map (fine state -> "
            f"aggregate state) is: [{agg_txt}].\n"
            f"The fine-state transition map is (fine state -> next fine state): [{t_txt}].\n"
            f"An abstraction has no hidden detail ('closed') if, within every aggregate state, all "
            f"fine states map to the same aggregate state under the transition. Determine whether "
            f"this aggregation is closed.\n"
            f"Answer exactly 'closed', or if not closed give one witness pair 'f,c' where f is a "
            f"fine state and c its resulting aggregate state, such that another fine state in the "
            f"same aggregate maps to a different aggregate state."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        gold = entry.answer
        normalized = str(answer).strip()
        meta = entry.metadata
        agg = meta["agg"]
        t = meta["fine_t"]
        fine_states = meta["fine_states"]
        coarse_states = meta["coarse_states"]

        if gold == "closed":
            return 1.0 if normalized == "closed" else 0.0
        if normalized == "closed":
            already = _closed(agg, t, fine_states, coarse_states)
            return 0.0 if not already else 1.0
        try:
            f, c = normalized.split(",")
            ff = int(f)
            cc = int(c)
        except ValueError:
            return 0.0
        if not (0 <= ff < fine_states and 0 <= cc < coarse_states):
            return 0.0
        if agg[t[ff]] != cc:
            return 0.0
        if _block_outputs(agg, t, agg[ff], fine_states).__len__() < 2:
            return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'coarse_state_autonomy (variant 1 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_latent_representation_r4/coarse_state_autonomy',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2409743872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

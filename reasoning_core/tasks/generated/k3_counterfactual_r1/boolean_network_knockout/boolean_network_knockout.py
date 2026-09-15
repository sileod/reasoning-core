import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'boolean_network_knockout (draw 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_counterfactual_r1/boolean_network_knockout',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}



@dataclass
class BooleanNetworkKnockoutConfig(Config):
    n: int = 4
    k: int = 2

    def apply_difficulty(self, level):
        self.n = 4 + level
        self.k = 2 + (level // 3)
        if self.k >= self.n:
            self.k = self.n - 1


def _make_tables(n, k):
    tables = []
    for _ in range(n):
        deps = random.sample(range(n), k)
        cases = [random.randint(0, 1) for _ in range(1 << k)]
        tables.append((deps, cases))
    return tables


def _step(state, tables, clamped=None):
    n = len(state)
    new = list(state)
    for target in range(n):
        if clamped is not None and target == clamped[0]:
            new[target] = clamped[1]
            continue
        deps, cases = tables[target]
        idx = 0
        for j, d in enumerate(deps):
            idx |= state[d] << j
        new[target] = cases[idx]
    return tuple(new)


def _attractor(start, tables, clamped=None):
    state = start
    seen = {}
    order = []
    t = 0
    while state not in seen:
        seen[state] = t
        order.append(state)
        state = _step(state, tables, clamped)
        t += 1
    cs = seen[state]
    return tuple(order[cs:]), cs


def _find_divergence(start, tables, target_node, fixed_val, bound):
    orig = start
    clamp = start
    for t in range(1, bound + 1):
        new_orig = _step(orig, tables)
        new_clamp = _step(clamp, tables, (target_node, fixed_val))
        if new_clamp != new_orig:
            return t
        orig = new_orig
        clamp = new_clamp
    return 0


def _normalize(rep):
    m = len(rep)
    rotations = [tuple(rep[rot:] + rep[:rot]) for rot in range(m)]
    return min(rotations)


class BooleanNetworkKnockout(Task):
    summary = "Simulate synchronous Boolean networks to their attractor cycle, then clamp one node to a fixed value and recompute; across varied update tables and initial states, answer the new attractor and the divergence step."
    design_choice = "Encode the Boolean network update tables as deterministic truth tables and have solvers output the new attractor as a canonical bitstring plus the first time step where it differs from the original attractor."
    config_cls = BooleanNetworkKnockoutConfig

    def generate_entry(self):
        n = self.config.n
        k = self.config.k
        for _ in range(2000):
            tables = _make_tables(n, k)
            start = tuple(random.randint(0, 1) for _ in range(n))
            target_node = random.randrange(n)
            fixed_val = random.randint(0, 1)
            orig_cyc, pstart = _attractor(start, tables)
            if len(orig_cyc) == 1:
                continue
            if len(orig_cyc) > 60 or pstart > 4000:
                continue
            new_cyc, _ = _attractor(start, tables, (target_node, fixed_val))
            if len(new_cyc) > 60:
                continue
            if set(new_cyc) == set(orig_cyc):
                continue
            bound = pstart + len(orig_cyc) + len(new_cyc) + 5
            div = _find_divergence(start, tables, target_node, fixed_val, bound)
            if div == 0:
                continue
            rep = [tuple((fixed_val if i == target_node else b) for i, b in enumerate(s)) for s in new_cyc]
            norm = _normalize(rep)
            cyc_str = "-".join("".join(str(b) for b in s) for s in norm)
            answer = f"{cyc_str} {div}"
            return Entry(metadata={
                "n": n, "k": k,
                "tables": [[list(d), list(c)] for d, c in tables],
                "start": list(start),
                "target_node": target_node,
                "fixed_val": fixed_val,
                "final_cycle": [list(s) for s in norm],
                "div_step": div,
            }, answer=answer)
        raise RuntimeError("no valid boolean-network knockout instance found")

    def render_prompt(self, metadata):
        n = metadata["n"]
        lines = ["Consider a synchronous Boolean network on n = %d nodes." % n]
        lines.append("Each node updates to a deterministic Boolean function of k other nodes, given as truth tables (dependency list, then the 2^k outputs in binary order of the dependency bits, bit j encoding dependency deps[j] = 1).")
        lines.append("Update tables:")
        for target in range(n):
            deps, cases = metadata["tables"][target]
            lines.append(f"  node {target}: deps {deps} -> {''.join(str(c) for c in cases)}")
        lines.append(f"The network runs synchronously from the initial state {''.join(str(b) for b in metadata['start'])} until it enters its attractor cycle.")
        tn = metadata["target_node"]
        fv = metadata["fixed_val"]
        lines.append(f"Now node {tn} is clamped to the fixed value {fv}: its value remains {fv} forever, all other nodes update normally, and the network runs synchronously from the same initial state until it enters a NEW attractor cycle.")
        lines.append("Answer with two items separated by a single space: (1) the new attractor cycle, written in the rotation that is lexicographically smallest, its states listed in order joined by '-' where each state is an n-bit string, and (2) the first synchronization step (0-indexed, initial state is step 0) at which the clamped network's state differs from the original network's state.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        try:
            cyc_part, step_part = answer.strip().rsplit(" ", 1)
            step = int(step_part)
        except (ValueError, IndexError):
            return 0.0
        pieces = cyc_part.split("-")
        n = entry.metadata["n"]
        if not pieces:
            return 0.0
        try:
            rep = [tuple(int(ch) for ch in p) for p in pieces]
        except ValueError:
            return 0.0
        if any(len(s) != n for s in rep):
            return 0.0
        if any(b not in (0, 1) for s in rep for b in s):
            return 0.0
        if _normalize(rep) != _normalize([tuple(s) for s in entry.metadata["final_cycle"]]):
            return 0.0
        if step != entry.metadata["div_step"]:
            return 0.0
        return 1.0

    def distractor_candidates(self, entry):
        cyc = [tuple(s) for s in entry.metadata["final_cycle"]]
        base = "-".join("".join(str(b) for b in s) for s in cyc)
        step = entry.metadata["div_step"]
        cands = []
        wrong_cyc = []
        for s in cyc:
            wrong_cyc.append(tuple(1 - b for b in s))
        wc = "-".join("".join(str(b) for b in s) for s in wrong_cyc)
        cands.append(f"{wc} {step}")
        cands.append(f"{base} {step - 1 if step > 0 else step + 1}")
        cands.append(f"{base} {step + 1 if step else step}")
        return cands

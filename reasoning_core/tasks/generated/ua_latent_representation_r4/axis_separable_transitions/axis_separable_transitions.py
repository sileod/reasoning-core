"""Axis-separable latent transitions.

A transition table over product states may factor as independent per-coordinate
mechanisms, possibly composed with a hidden permutation applied to the
coordinates themselves. The table is given in full; the task asks whether it is
axis-separable (up to a coordinate permutation) and, when it is, to recover the
hidden permutation as a list of coordinate indices.
"""

import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class AxisSeparableTransitionsV2Config(Config):
    C: int = 3          # number of coordinates (indices 0..C-1)
    R: int = 2          # value range for each coordinate (0..R-1)

    def apply_difficulty(self, level):
        self.C = min(4, stochastic_rounding(self.C + level // 3))


def _lex_products(C, R):
    """All product states in lexicographic order: tuples of length C, each
    entry in 0..R-1, row-major."""
    return list(itertools.product(range(R), repeat=C))


def _from_perm_components(base, pi, state):
    """Compose per-coordinate maps base[j] with hidden coordinate permutation pi.

    Big target coordinate j takes value base[pi[j]][state[pi[j]]]: the map
    assigned to big coordinate j reads source coordinate pi[j].
    """
    C = len(base)
    return tuple(base[pi[j]][state[pi[j]]] for j in range(C))


def _is_separable(base, big_table, C, R):
    """Search all permutations; return the FIRST (lexicographic) (pi, maps) if
    the big table factors via some coordinate permutation, else None. Uniqueness
    is guaranteed by generation (see _make_separable)."""
    for pi in itertools.permutations(range(C)):
        maps = []
        ok = True
        for j in range(C):
            g = [None] * R
            for s in _lex_products(C, R):
                v = s[pi[j]]
                target = big_table[s][j]
                if g[v] is None:
                    g[v] = target
                elif g[v] != target:
                    ok = False
                    break
            if not ok:
                break
            maps.append(g)
        if ok:
            return (pi, maps)
    return None


class AxisSeparableTransitions(Task):
    summary = ("Factor transition tables on product states into independent "
               "coordinate mechanisms, allowing hidden coordinate permutations; "
               "determine separability or recover a queried component transition.")
    config_cls = AxisSeparableTransitionsV2Config

    design_choice = ("Instances present a full transition table over all product "
                     "states, with the hidden permutation applied to coordinates; "
                     "solvers must output yes/no separability plus the recovered "
                     "permutation as a list of coordinate indices.")

    def _make_separable(self, C, R):
        """Build a uniquely-separable table; return (base, pi, big). Unique
        recovered permutation is enforced by resampling."""
        while True:
            base = []
            for _ in range(C):
                ident = list(range(R))
                random.shuffle(ident)
                base.append(ident)
            pi = list(range(C))
            random.shuffle(pi)
            big = {}
            for s in _lex_products(C, R):
                big[s] = _from_perm_components(base, pi, s)
            verif = _is_separable(base, big, C, R)
            if verif is not None and verif[0] == tuple(pi):
                return base, pi, big

    def _make_inseparable(self, C, R):
        """Build a transition table that is NOT axis-separable under any
        permutation: start from a separable construction and perturb a single
        entry so no permutation reproduces the factorized structure, while
        remaining a valid deterministic table."""
        while True:
            base = []
            for _ in range(C):
                ident = list(range(R))
                random.shuffle(ident)
                base.append(ident)
            pi = list(range(C))
            random.shuffle(pi)
            big = {}
            for s in _lex_products(C, R):
                big[s] = _from_perm_components(base, pi, s)
            entries = list(_lex_products(C, R))
            s_pert = random.choice(entries)
            j_pert = random.randrange(C)
            newval = random.randrange(R)
            if newval == big[s_pert][j_pert]:
                continue
            cand = dict(big)
            cand[s_pert] = tuple(
                newval if j == j_pert else big[s_pert][j]
                for j in range(C))
            if _is_separable(base, cand, C, R) is None:
                return cand

    def generate_entry(self):
        C = self.config.C
        R = self.config.R
        separable = random.random() < 0.67
        if separable:
            base, pi, big = self._make_separable(C, R)
            answer = "yes " + " ".join(str(i) for i in pi)
            rec_pi = list(pi)
        else:
            big = self._make_inseparable(C, R)
            base = None
            pi = None
            answer = "no"
            rec_pi = None

        states = list(_lex_products(C, R))
        table = [[list(s), list(big[s])] for s in states]
        metadata = {
            "C": C,
            "R": R,
            "separable": bool(separable),
            "pi": list(pi) if pi is not None else None,
            "base": base,
            "table": table,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        C = metadata["C"]
        R = metadata["R"]
        lines = []
        lines.append(
            f"A transition rule maps each state of a product system to a next "
            f"state. There are {C} coordinates, each taking values 0..{R - 1}. "
            f"The rule is axis-separable if there is a permutation of the "
            f"coordinates (a bijection from source coordinates to target "
            f"coordinates) such that each target coordinate's next value "
            f"depends only on the current value of the one matching source "
            f"coordinate. The full transition table is:")
        for s, t in metadata["table"]:
            lines.append(f"{tuple(s)} -> {tuple(t)}")
        lines.append(
            f"Is the rule axis-separable? If yes, answer 'yes' followed by a "
            f"space, then the recovered permutation as the list of source "
            f"coordinate indices read in target-coordinate order (e.g. for "
            f"{C} coordinates 'yes 1 0 2'). If no, answer exactly 'no'.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        a = str(answer).strip()
        return 1.0 if a == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'axis_separable_transitions (variant 2 of 3)',
 'hypothesis': 'P012',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_latent_representation_r4/axis_separable_transitions',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 214538085,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

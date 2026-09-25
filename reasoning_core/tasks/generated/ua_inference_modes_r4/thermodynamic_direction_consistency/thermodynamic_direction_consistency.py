"""Thermodynamic direction consistency: which single reaction removal restores a
shared scalar potential over species with fixed rational potential differences."""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


def _fmt(x):
    return str(x) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def _consistent(reactions, exclude):
    """Union-find consistency check on difference constraints phi[v]-phi[u]=d.

    Returns True if the reactions (minus the excluded index) admit a shared
    scalar potential (every cycle sums to zero), False otherwise.
    """
    parent = {}
    dist = {}

    def find(x):
        if parent[x] == x:
            return x, Fraction(0)
        r, d0 = find(parent[x])
        dist[x] = dist[x] + d0
        parent[x] = r
        return r, dist[x]

    for i, (u, v, d) in enumerate(reactions):
        if i == exclude:
            continue
        if u not in parent:
            parent[u] = u
            dist[u] = Fraction(0)
        if v not in parent:
            parent[v] = v
            dist[v] = Fraction(0)
        ru, du = find(u)
        rv, dv = find(v)
        if ru == rv:
            if dv - du != d:
                return False
        else:
            parent[ru] = rv
            dist[ru] = dv - du - d
    return True


@dataclass
class ThermodynamicDirectionConsistencyConfig(Config):
    species: int = 5
    partners: int = 2
    filler: int = 1
    pot: int = 6
    den: int = 3
    defect: int = 2

    def apply_difficulty(self, level):
        self.species = self.species + level
        self.partners = min(self.species - 2, self.partners + level // 2)
        if self.partners < 2:
            self.partners = 2
        self.filler = self.filler + level
        self.den = min(4, self.den + level // 3)
        self.defect = self.defect + level
        self.pot = self.pot + level


class ThermodynamicDirectionConsistency(Task):
    summary = ("Test whether proposed directions of coupled transformations admit a shared "
               "scalar potential over species with fixed rational potential differences; "
               "vary stoichiometry via rational differences, reversible steps, and defect "
               "magnitudes; answer the index of the single reaction whose removal restores "
               "consistency.")
    design_choice = ("Vary the fixed potential differences between species as rational values "
                     "and ask the solver to identify which single reaction, when removed, "
                     "restores consistency, with the answer being the reaction index.")
    config_cls = ThermodynamicDirectionConsistencyConfig

    def generate_entry(self):
        cfg = self.config
        n_species = cfg.species

        while True:
            potentials = [
                Fraction(random.randint(-cfg.pot, cfg.pot),
                         random.randint(1, cfg.den))
                for _ in range(n_species)
            ]
            p, q = random.sample(range(n_species), 2)
            defect = random.choice([-1, 1]) * random.randint(1, cfg.defect)
            reactions = []
            hub_val = potentials[q] - potentials[p] + defect
            reactions.append([p, q, hub_val])
            hub_idx = 0

            others = [x for x in range(n_species) if x != p and x != q]
            partners = random.sample(others, min(cfg.partners, len(others)))
            for r in partners:
                reactions.append([p, r, potentials[r] - potentials[p]])
                reactions.append([r, q, potentials[q] - potentials[r]])

            # filler consistent edges among distinct species pairs
            n_filler = cfg.filler
            tries = 0
            added = 0
            attempts = set()
            while added < n_filler and tries < n_filler * 30:
                tries += 1
                u, v = random.sample(range(n_species), 2)
                if u == v:
                    continue
                key = (u, v) if u < v else (v, u)
                if key in attempts:
                    continue
                attempts.add(key)
                reactions.append([u, v, potentials[v] - potentials[u]])
                added += 1

            # verify: exactly one removable reaction restores consistency
            if n_species >= cfg.partners + 2 and len(partners) >= 2 and len(reactions) >= 4:
                good = [i for i in range(len(reactions))
                        if _consistent(reactions, i)]
                if len(good) == 1:
                    answer = good[0]
                    break

        # shuffle the reaction list; re-derive answer position
        order = list(range(len(reactions)))
        random.shuffle(order)
        shuffled = [reactions[i] for i in order]
        answer = order.index(answer)

        meta = {
            "species": n_species,
            "potentials": [(_fmt(x)) for x in potentials],
            "reactions": [[u, v, _fmt(d)] for (u, v, d) in shuffled],
            "answer": answer,
        }
        return Entry(metadata=meta, answer=str(answer))

    def render_prompt(self, metadata):
        n = metadata["species"]
        lines = [
            f"There are {n} chemical species with unknown scalar potentials. A reaction "
            "between two species proposes that the potential change in the stated direction "
            "equals a given (fixed, rational) amount. All reactions together admit a shared "
            "scalar potential only if every closed cycle of proposed changes sums to zero "
            "(a potential is a value per species making every listed change exact).",
        ]
        for i, (u, v, d) in enumerate(metadata["reactions"]):
            lines.append(f"Reaction {i}: species {v} minus species {u} changes by {d}")
        lines.append(
            "Exactly one of these reactions, if removed, would make all remaining proposed "
            "changes consistent with a shared scalar potential. Give the index of that "
            "reaction. The answer is one integer."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        try:
            got = int(str(answer).strip())
        except (TypeError, ValueError):
            return 0.0
        return 1.0 if got == int(entry.answer) else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'thermodynamic_direction_consistency (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_inference_modes_r4/thermodynamic_direction_consistency',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

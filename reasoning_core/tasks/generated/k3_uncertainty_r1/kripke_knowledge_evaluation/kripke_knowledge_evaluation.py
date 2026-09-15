import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class KripkeKnowledgeConfig(Config):
    n_worlds: int = 4
    n_atoms: int = 2
    n_agents: int = 2

    def apply_difficulty(self, level):
        self.n_worlds = stochastic_rounding(4 + 2 * level)
        self.n_atoms = stochastic_rounding(2 + level // 2)
        self.n_agents = 2


class KripkeKnowledgeEvaluation(Task):
    summary = "Evaluate nested knowledge claims on a given possible-worlds model — worlds, an atom valuation, and each agent's indistinguishability links; queries nest one agent's knowledge inside another's and answers are booleans or world sets."
    design_choice = "Queries ask whether agent A knows that agent B knows a proposition, with answers restricted to true/false only."
    config_cls = KripkeKnowledgeConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_worlds
        n_atoms = cfg.n_atoms

        while True:
            atoms = [f"p{i}" for i in range(n_atoms)]
            val = []
            for _ in range(n):
                wv = []
                for _ in range(n_atoms):
                    wv.append(random.choice([True, False]))
                val.append(wv)

            rel_a = self._gen_equiv(n)
            rel_b = self._gen_equiv(n)

            if len(rel_a) < n or len(rel_b) < n:
                continue

            ca = self._img(rel_a, 0)
            u = set()
            for w in ca:
                for wp in self._img(rel_b, w):
                    u.add(wp)

            atom = random.choice(range(n_atoms))
            target = random.choice([0, 1])

            if target == 1:
                for w in range(n):
                    val[w][atom] = (w in u)
            else:
                z = random.choice(self._img(rel_b, 0))
                for w in range(n):
                    val[w][atom] = (w in u) and (w != z)
                val[z][atom] = False

            sol = self._solver(val, rel_a, rel_b, atom)
            if sol != target:
                continue

            world_names = list(range(n))
            metadata = {
                "worlds": world_names,
                "atoms": atoms,
                "valuation": [[bool(v) for v in wv] for wv in val],
                "rel_a": sorted(list(rel_a)),
                "rel_b": sorted(list(rel_b)),
                "agent_a": 0,
                "agent_b": 1,
                "atom": atom,
                "answer": sol,
            }
            return Entry(metadata=metadata, answer="True" if sol == 1 else "False")

    def _solver(self, val, rel_a, rel_b, atom):
        for w in self._img(rel_a, 0):
            if not self._b_knows(val, rel_b, atom, w):
                return 0
        return 1

    def _b_knows(self, val, rel_b, atom, w):
        for w_prime in self._img(rel_b, w):
            if not val[w_prime][atom]:
                return False
        return True

    def _gen_equiv(self, n):
        rel = set((i, i) for i in range(n))
        nodes = list(range(n))
        while nodes:
            size = min(len(nodes), random.randint(1, 3))
            block = random.sample(nodes, size)
            for i in block:
                nodes.remove(i)
            for i in block:
                for j in block:
                    rel.add((i, j))
        return rel

    def _img(self, rel, w):
        out = []
        for (i, j) in rel:
            if i == w and j not in out:
                out.append(j)
        return out

    def render_prompt(self, metadata):
        lines = []
        lines.append("We have a possible-worlds model. The set of worlds is "
                     f"{metadata['worlds']}. The atoms are {metadata['atoms']}.")
        val_str = "; ".join(
            f"at {i} {a} is {'true' if metadata['valuation'][i][j] else 'false'}"
            for i in range(len(metadata['worlds']))
            for j, a in enumerate(metadata['atoms'])
        )
        lines.append(f"Valuation: {val_str}.")
        lines.append(
            f"Agent A considers two worlds indistinguishable when they are linked "
            f"by an edge in {sorted(metadata['rel_a'])} "
            f"(reflexive: every world is linked to itself).")
        lines.append(
            f"Agent B considers two worlds indistinguishable when they are linked "
            f"by an edge in {sorted(metadata['rel_b'])} "
            f"(reflexive: every world is linked to itself).")
        lines.append(
            f"An agent knows a claim when it holds in every world it considers "
            f"possible from the current world.")
        lines.append(
            f"Question: At world 0, does agent A know that agent B knows that "
            f"{metadata['atoms'][metadata['atom']]} is "
            f"{'true' if metadata['valuation'][0][metadata['atom']] else 'false'}?")
        lines.append("Answer with True or False exactly.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if answer is None:
            return 0.0
        norm = str(answer).strip().lower()
        gnorm = str(gold).strip().lower()
        if norm == gnorm:
            return 1.0
        if norm in {"true", "false"} and gnorm in {"true", "false"} and norm != gnorm:
            return 0.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'kripke_knowledge_evaluation (draw 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_uncertainty_r1/kripke_knowledge_evaluation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

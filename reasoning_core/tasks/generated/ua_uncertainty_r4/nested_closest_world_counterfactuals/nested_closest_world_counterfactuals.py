import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'nested_closest_world_counterfactuals (variant 1 of 3)',
 'hypothesis': 'P012',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/nested_closest_world_counterfactuals',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1277236794,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Represent each world as a bit-vector over atomic propositions and each "
                 "closeness order as a lexicographic tie-break on weighted Hamming distance "
                 "to the actual world, with ties broken by a fixed world index.")

PROP_NAMES = ["P", "Q", "R", "S", "T", "U", "V", "W"]


@dataclass
class NestedCounterfactualConfig(Config):
    num_worlds: int = 4
    num_props: int = 3
    depth: int = 2
    max_weight: int = 6
    impossible_prob: float = 0.18
    lits_per: int = 1

    def apply_difficulty(self, level):
        self.num_worlds = 4 + level
        self.num_props = 3 + (level // 2)
        self.depth = 2 + (level // 2)
        self.lits_per = 1 + (level // 3)
        self.max_weight = 4 + 2 * level


def _dist(centroid, v, worlds, weights):
    return sum(
        weights[i] for i in range(len(weights))
        if worlds[centroid][i] != worlds[v][i]
    )


def _satisfies(world, lits):
    return all(world[p] == val for p, val in lits.items())


def closest_world(centroid, lits, worlds, weights):
    """Unique closest world to `centroid` satisfying literal dict `lits`; None if impossible.

    Weighted Hamming distance first, ties broken by the fixed world index (lower = closer).
    """
    best = None
    bestkey = None
    for v in range(len(worlds)):
        if not _satisfies(worlds[v], lits):
            continue
        key = (_dist(centroid, v, worlds, weights), v)
        if bestkey is None or key < bestkey:
            bestkey = key
            best = v
    return best


def _random_constraint(k, n_lits):
    props = random.sample(range(k), n_lits)
    return {p: bool(random.getrandbits(1)) for p in props}


def _impossible_constraint(worlds, k):
    for _ in range(50):
        lits = {p: bool(random.getrandbits(1)) for p in range(k)}
        if not any(_satisfies(w, lits) for w in worlds):
            return lits
    return None


def evaluate_answer(worlds, weights, clauses, target):
    centroid = 0
    for c in clauses:
        v = closest_world(centroid, c["lits"], worlds, weights)
        if v is None:
            return ("yes", True) if c["modal"] == "would" else ("no", False)
        centroid = v
    truth = bool(worlds[centroid][target])
    return ("yes" if truth else "no", truth)


def _lit_phrase(prop_name, val):
    return prop_name if val else "not " + prop_name


def render_statement(clauses, target_name, prop_names):
    phr = []
    for c in clauses:
        conj = " and ".join(
            _lit_phrase(prop_names[p], v) for p, v in sorted(c["lits"].items())
        )
        phr.append(f"{c['modal']} ( {conj} )")
    inner = " ".join(phr) + f" then {target_name}"
    return inner


class NestedClosestWorldCounterfactuals(Task):
    summary = ("Evaluate nested would/might counterfactuals over world-relative closeness "
               "orders with ties (weighted Hamming distance, tie-broken by world index) and "
               "impossible antecedents; return yes/no by selecting the closest antecedent "
               "world separately at each scope.")
    config_cls = NestedCounterfactualConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n = cfg.num_worlds
        k = cfg.num_props
        d = cfg.depth
        names = PROP_NAMES[:k]

        for _ in range(300):
            worlds = [
                [bool(random.getrandbits(1)) for _ in range(k)] for _ in range(n)
            ]
            weights = [random.randint(1, cfg.max_weight) for _ in range(k)]

            clauses = []
            injected = False
            moves = 0
            centroid = 0
            for _i in range(d):
                modal = random.choice(["would", "might"])
                if (not injected) and random.random() < cfg.impossible_prob:
                    cons = _impossible_constraint(worlds, k)
                    if cons is not None:
                        clauses.append({"modal": modal, "lits": cons, "impossible": True})
                        injected = True
                        continue
                    cons = _random_constraint(k, 1)
                else:
                    cons = _random_constraint(k, cfg.lits_per)
                v = closest_world(centroid, cons, worlds, weights)
                impossible = v is None
                clauses.append({"modal": modal, "lits": cons, "impossible": impossible})
                if not impossible:
                    if v != centroid:
                        moves += 1
                    centroid = v

            if moves >= 1:
                break

        target = random.randrange(k)
        ans, _truth = evaluate_answer(worlds, weights, clauses, target)

        names = PROP_NAMES[:k]
        metadata = {
            "props": names,
            "worlds": [[int(b) for b in w] for w in worlds],
            "weights": [int(w) for w in weights],
            "target": target,
            "clauses": [
                {"modal": c["modal"],
                 "lits": [[int(p), bool(v)] for p, v in sorted(c["lits"].items())],
                 "impossible": bool(c["impossible"])}
                for c in clauses
            ],
            "answer": ans,
        }
        return Entry(metadata=metadata, answer=ans)

    def render_prompt(self, metadata):
        names = metadata["props"]
        target_name = names[metadata["target"]]
        setup = []
        setup.append(
            f"Reasoning domain: the actual world is world 0, and there are "
            f"{len(metadata['worlds'])} worlds total, each a truth assignment to the "
            f"propositions {', '.join(names)}."
        )
        top = ["worlds:"]
        for i, w in enumerate(metadata["worlds"]):
            trues = [names[j] for j, b in enumerate(w) if b]
            top.append(f"  world {i}: " + (", ".join(trues) if trues else "none"))
        weights = ", ".join(f"{names[i]}:{metadata['weights'][i]}"
                            for i in range(len(names)))
        top.append(
            "distance weight per differing proposition: " + weights
        )
        body = "\n".join(top)
        clause_ls = []
        for c in metadata["clauses"]:
            conj = " and ".join(
                _lit_phrase(names[p], v) for p, v in sorted(c["lits"])
            )
            clause_ls.append(f"{c['modal']} ( {conj} )")
        statement = " ".join(clause_ls) + f" then {target_name}"
        return (
            "\n".join(setup) + "\n" + body + "\n\n"
            "Closeness, relative to a focal world, ranks worlds by (weighted Hamming "
            "distance to the focal world, then by world index, lower index closer). "
            "Evaluate nested counterfactuals outermost first; each scope's antecedent "
            "selects the unique closest world satisfying it, centered on the current "
            "world. If an antecedent has no satisfying world, 'would' is vacuously true "
            "and 'might' is false there.\n"
            f"Under this nested statement: {statement}\n"
            "Is the whole statement true? Reply with exactly one word, either yes or no, "
            "as the final answer."
        )

    def score_answer(self, answer, entry):
        gold = str(entry["answer"]).strip().lower()
        got = str(answer).strip().lower()
        return 1.0 if got == gold else 0.0

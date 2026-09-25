import random

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'stoichiometric_bootstrap_planning (variant 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_inference_modes_r4/stoichiometric_bootstrap_planning',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Encode the answer as a compact canonical string of reaction names and counts, "
                 "e.g., 'R1x2,R3x1,R2x4', with the solver required to output the sequence in "
                 "canonical sorted order.")


def _canon_answer(reaction_names, counts):
    pairs = sorted(zip(reaction_names, counts))
    return ",".join(f"{name}x{c}" for name, c in pairs if c > 0)


def _check_solution(reactions, kind, target_idx, target_qty, waste_cap, loan, solution,
                    fire_budget):
    counts = [solution[r] if r < len(solution) else 0 for r in range(len(reactions))]
    net = {}
    waste_prod = {}
    for r, c in enumerate(counts):
        if c:
            for s, k in reactions[r]["cons"].items():
                net[s] = net.get(s, 0) - k * c
            for s, k in reactions[r]["prod"].items():
                net[s] = net.get(s, 0) + k * c
                if kind[s] == "waste":
                    waste_prod[s] = waste_prod.get(s, 0) + k * c
    if net.get(target_idx, 0) < target_qty:
        return False
    for s in kind:
        k = kind[s]
        if k in ("intermediate", "catalyst", "borrowed"):
            if net.get(s, 0) != 0:
                return False
        if k == "borrowed":
            consumed = max(0, -net.get(s, 0))
            if consumed > loan.get(s, 0):
                return False
        if k == "waste":
            if waste_prod.get(s, 0) > waste_cap:
                return False
    return True


class _SearchBudget(Exception):
    pass


def _solve(reactions, kind, target_idx, target_qty, waste_cap, loan, fire_budget,
           cost_per):
    # kind is keyed by species index for the solver.
    n = len(kind)
    species_idx = list(kind.keys())
    best_cost = [None]
    best = [None]
    counts = [0] * len(reactions)
    nodes = [0]
    NODE_BUDGET = 80000

    # Seed a tight upper bound with the pure direct plan (reaction 0 = Rd),
    # whenever producing target directly stays within the waste cap.
    if reactions:
        rd = reactions[0]
        tp = rd["prod"].get(target_idx, 0)
        if tp > 0:
            waste_idx = None
            for i in species_idx:
                if kind[i] == "waste":
                    waste_idx = i
                    break
            k = -(-target_qty // tp)
            if k <= fire_budget:
                if waste_idx is None or rd["prod"].get(waste_idx, 0) * k <= waste_cap:
                    seed = [0] * len(reactions)
                    seed[0] = k
                    best_cost[0] = k * cost_per[0]
                    best[0] = seed

    def state_key(net, waste_prod):
        net_t = tuple((i, net.get(i, 0)) for i in species_idx)
        waste_t = tuple((i, waste_prod.get(i, 0)) for i in species_idx if kind[i] == "waste")
        return net_t, waste_t

    memo = {}

    def feasible(net, waste_prod):
        if net.get(target_idx, 0) < target_qty:
            return False
        for i in species_idx:
            k = kind[i]
            if k in ("intermediate", "catalyst", "borrowed"):
                if net.get(i, 0) != 0:
                    return False
            if k == "borrowed":
                if max(0, -net.get(i, 0)) > loan.get(i, 0):
                    return False
            if k == "waste":
                if waste_prod.get(i, 0) > waste_cap:
                    return False
        return True

    def dfs(r, cost, net, waste_prod):
        nonlocal nodes
        nodes[0] += 1
        if nodes[0] > NODE_BUDGET:
            raise _SearchBudget
        if best_cost[0] is not None and cost >= best_cost[0]:
            return
        key = (r, cost, state_key(net, waste_prod))
        prev = memo.get((r, state_key(net, waste_prod)))
        if prev is not None and cost >= prev:
            return
        memo[(r, state_key(net, waste_prod))] = cost
        if r == len(reactions):
            if feasible(net, waste_prod):
                best_cost[0] = cost
                best[0] = list(counts)
            return
        reac = reactions[r]
        cq = cost_per[r]
        for c in range(0, fire_budget + 1):
            counts[r] = c
            nnet = dict(net)
            nwaste = dict(waste_prod)
            if c:
                for s, k in reac["cons"].items():
                    nnet[s] = nnet.get(s, 0) - k * c
                for s, k in reac["prod"].items():
                    nnet[s] = nnet.get(s, 0) + k * c
                    if kind[s] == "waste":
                        nwaste[s] = nwaste.get(s, 0) + k * c
            dfs(r + 1, cost + c * cq, nnet, nwaste)
        counts[r] = 0

    dfs(0, 0, {}, {})
    return best[0], best_cost[0]


class StoichiometricBootstrapConfig(Config):
    n_target_qty: int = 2
    n_inter: int = 1
    n_extra_reac: int = 1
    waste_cap: int = 3
    borrow_amt: int = 2
    fire_budget: int = 6
    cost_max: int = 2

    def apply_difficulty(self, level):
        self.n_target_qty = min(5, 1 + level)
        self.n_inter = min(2, 1 + level // 3)
        self.n_extra_reac = min(2, 1 + level // 3)
        self.waste_cap = 1 + level
        self.borrow_amt = 2 + (1 if level >= 3 else 0)
        self.fire_budget = 3 + level // 3
        self.cost_max = 1 + (1 if level >= 2 else 0)


class StoichiometricBootstrapPlannerV2(Task):
    task_name = "stoichiometric_bootstrap_planner"
    summary = ("Plan reaction firings with integer stoichiometry, reusable catalysts, "
               "unavailable intermediates and waste caps; return a least-cost sequence "
               "achieving target stock while restoring borrowed species.")
    config_cls = StoichiometricBootstrapConfig
    design_choice = design_choice

    def generate_entry(self):
        cfg = self.config
        for _attempt in range(200):
            entry = self._try_generate(cfg)
            if entry is not None:
                return entry
        raise RuntimeError("stoichiometric_bootstrap_planning: no admissible instance")

    def _try_generate(self, cfg):
        species = []
        idx = {}
        kind = {}
        reactions = []
        fire_budget = cfg.fire_budget

        def add_species(name, k):
            species.append(name)
            idx[name] = len(species) - 1
            kind[len(species) - 1] = k

        add_species("raw", "raw")
        add_species("T", "target")
        for i in range(cfg.n_inter):
            add_species(f"I{i}", "intermediate")
        add_species("C", "catalyst")
        add_species("B", "borrowed")
        add_species("W", "waste")

        raw = idx["raw"]
        target = idx["T"]
        cat = idx["C"]
        bor = idx["B"]
        was = idx["W"]
        inter_species = [idx[f"I{i}"] for i in range(cfg.n_inter)]

        rnames = []
        rcost = []
        rdata = []

        # Direct raw -> target reaction (guarantees solvability); usually priced to lose to
        # cheaper routes, so it is rarely the unique optimum.
        direct_cost = random.randint(2, cfg.cost_max + 2)
        direct = {"cons": {raw: 1}, "prod": {target: 1, was: random.randint(1, 2)}}
        rnames.append("Rd")
        rcost.append(direct_cost)
        rdata.append(direct)

        # Efficient route: sometimes cheap without the borrowed species, sometimes it must
        # consume and restore the borrowed species B.
        re_present = random.random() < 0.7
        if re_present:
            cons_eff = {}
            uses_borrow = random.random() < 0.5
            if uses_borrow:
                cons_eff[bor] = 1
            elif random.random() < 0.5:
                cons_eff[cat] = 1
            prod_eff = {target: random.randint(1, 2)}
            rnames.append("Re")
            rcost.append(1)
            rdata.append({"cons": cons_eff, "prod": prod_eff})

        # Restore reaction: returns the borrowed species (consuming raw).
        rnames.append("Rb")
        rcost.append(1)
        rdata.append({"cons": {raw: 1}, "prod": {bor: 1}})

        # Intermediate generator reactions.
        k = 0
        prev_raw = raw
        for inter in inter_species:
            c = random.randint(1, 2)
            reac = {"cons": {prev_raw: c}, "prod": {inter: c + 1}}
            rnames.append(f"Rg{k}")
            rcost.append(1)
            rdata.append(reac)
            prev_raw = inter
            k += 1

        # Extra random reactions to add structural variety.
        index_list = list(range(len(species)))
        for m in range(cfg.n_extra_reac):
            reac = {"cons": {}, "prod": {}}
            if random.random() < 0.5:
                reac["cons"][was] = random.randint(1, cfg.waste_cap)
            srcs = [s for s in index_list if kind[s] in ("raw", "intermediate", "catalyst")]
            if srcs and random.random() < 0.4:
                reac["cons"][random.choice(srcs)] = 1
            if random.random() < 0.3:
                reac["cons"][bor] = 1
            prod_choices = [s for s in index_list if kind[s] in ("target", "intermediate")]
            if prod_choices:
                reac["prod"][random.choice(prod_choices)] = random.randint(1, 2)
            if random.random() < 0.3:
                reac["prod"][bor] = random.randint(1, 2)
            rnames.append(f"Ra{m}")
            rcost.append(random.randint(1, cfg.cost_max + 1))
            rdata.append(reac)

        reactions = rdata
        target_qty = cfg.n_target_qty
        waste_cap = cfg.waste_cap
        loan = {bor: cfg.borrow_amt}
        cost_per = rcost

        try:
            sol, best_cost = _solve(reactions, kind, target, target_qty, waste_cap, loan,
                                    fire_budget, cost_per)
        except _SearchBudget:
            return None
        if sol is None or best_cost is None:
            return None
        if not _check_solution(reactions, kind, target, target_qty, waste_cap, loan, sol,
                               fire_budget):
            return None

        # Domain assertions on the produced answer.
        assert best_cost >= 0, "cost must be non-negative"
        for c in sol:
            assert c >= 0, "firing counts must be non-negative integers"
        assert sum(sol) <= fire_budget * len(reactions)

        # The firing vector is the least-cost solution within the bounded search.
        cheaper = [c for c in sol if True]
        answer = _canon_answer(rnames, sol)
        if not answer:
            return None

        metadata = {
            "species": species,
            "kind": {species[i]: kind[i] for i in range(len(species))},
            "target": "T",
            "target_qty": target_qty,
            "waste_cap": waste_cap,
            "loan": {species[s]: k for s, k in loan.items()},
            "reaction_names": rnames,
            "reactions": [
                {"name": rnames[i],
                 "cons": {species[s]: k for s, k in reactions[i]["cons"].items()},
                 "prod": {species[s]: k for s, k in reactions[i]["prod"].items()},
                 "cost": cost_per[i]}
                for i in range(len(reactions))
            ],
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        species = metadata["species"]
        kind = metadata["kind"]
        idx_to_name = {i: species[i] for i in range(len(species))}
        name_to_idx = {name: i for i, name in enumerate(species)}

        def fmt(d):
            pairs = []
            for nm, cnt in sorted(d.items()):
                pairs.append(f"{nm} x{cnt}")
            return ", ".join(pairs) or "nothing"

        lines = [
            "You are planning a chemical synthesis. Species and their roles:",
        ]
        for s in species:
            k = kind[s]
            role = {
                "raw": "unlimited raw material",
                "target": "target product",
                "intermediate": "intermediate (must end at zero)",
                "catalyst": "reusable catalyst (must end at zero)",
                "waste": "waste byproduct",
                "borrowed": "borrowed species (must be restored)",
            }[k]
            lines.append(f"  {s}: {role}")
        lines.append("Available reactions (coefficient entries mean that many molecules):")
        for r in metadata["reactions"]:
            cons = fmt(r["cons"])
            prod = fmt(r["prod"])
            lines.append(f"  {r['name']} (cost {r['cost']}): consumes {cons}; produces {prod}")
        loan_txt = ", ".join(f"{s} x{k} borrowed" for s, k in metadata["loan"].items()) or "none"
        lines.append(f"There are {len(species)} species. Waste produced in total "
                     f"({metadata['waste_cap']} max per waste species). Loan: {loan_txt}.")
        lines.append(
            f"Fire reactions (reaction name followed by the number of times, e.g. R3x2) so that "
            f"the target {metadata['target']} reaches at least {metadata['target_qty']}, every "
            f"intermediate, catalyst and borrowed species ends back at zero, and no waste species "
            f"exceeds {metadata['waste_cap']} produced. Minimize the total cost (sum of firing "
            f"costs). Output the least-cost firing plan as a comma-separated sorted-by-name list "
            f"of only non-zero firings, e.g. R1x2,R3x1,R2x4.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        if answer == gold:
            return 1.0
        return 0.0

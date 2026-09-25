import random
from dataclasses import dataclass
from itertools import product

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'resolution_interpolant_extraction (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r4/resolution_interpolant_extraction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1618848011,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_ATOM_NAMES = [")a%d" % i for i in range(8)]


def _lit_lits(lit):
    neg = lit[0] == "!"
    name = lit[1:] if neg else lit
    return neg, name


def _neg(lit):
    return ("!" + lit[1:]) if lit[0] == "!" else ("!" + lit)


def _clause_atoms(clause):
    out = set()
    for lit in clause:
        _, name = _lit_lits(lit)
        out.add(name)
    return out


def _eval_clause_true(clause, assign):
    for lit in clause:
        neg, name = _lit_lits(lit)
        val = assign[name]
        if (not neg and val) or (neg and not val):
            return True
    return False


def _subtree_true(nodes, clausesets, node, assign):
    for c in clausesets[node]:
        if not _eval_clause_true(c, assign):
            return False
    return True


class RIEV3(Config):
    num_roots: int = 4
    num_atoms: int = 4
    min_priv: int = 0

    def apply_difficulty(self, level):
        self.num_roots = 4 + level // 2
        self.num_atoms = 3 + level // 2
        self.min_priv = level // 3


class ResolutionInterpolantExtraction(Task):
    """Propagate partial interpolants through partitioned resolution refutations with shared and private atoms, using supplied extraction rules; return a queried node's interpolant as a truth table."""

    summary = "Propagate partial interpolants through partitioned resolution refutations with shared and private atoms, using supplied extraction rules; return a queried node's interpolant as a truth table."
    config_cls = RIEV3

    def generate_entry(self):
        cfg = self.config
        n_atoms = cfg.num_atoms
        atom_names = _ATOM_NAMES[:n_atoms]

        for _try in range(400):
            root_clauses = []
            seen = set()
            for _ in range(cfg.num_roots):
                cl = self._rand_clause(atom_names)
                key = frozenset(cl)
                if key in seen:
                    continue
                seen.add(key)
                root_clauses.append(cl)

            if len(root_clauses) < 2:
                continue

            clausesets = {i: [c] for i, c in enumerate(root_clauses)}
            atoms_of = {i: _clause_atoms(c) for i, c in enumerate(root_clauses)}
            parent = {}
            next_id = len(root_clauses)
            active = list(range(len(root_clauses)))

            combined = True
            while len(active) > 1 and combined:
                combined = False
                pairs = []
                for i in range(len(active)):
                    for j in range(i + 1, len(active)):
                        a, b = active[i], active[j]
                        shared = atoms_of[a] & atoms_of[b]
                        if not shared:
                            continue
                        pairs.append((a, b))
                if not pairs:
                    break
                a, b = random.choice(pairs)
                new_id = next_id
                next_id += 1
                clausesets[new_id] = clausesets[a] + clausesets[b]
                atoms_of[new_id] = atoms_of[a] | atoms_of[b]
                parent[new_id] = (a, b)
                active = [x for x in active if x not in (a, b)]
                active.append(new_id)
                combined = True

            if len(active) != 1:
                continue

            root = active[0]

            leaf_atoms = [atoms_of[i] for i in range(len(root_clauses))]
            shared_atoms = set()
            for i in range(len(root_clauses)):
                for j in range(i + 1, len(root_clauses)):
                    shared_atoms |= (leaf_atoms[i] & leaf_atoms[j])
            all_used = shared_atoms | set.union(*leaf_atoms)
            private_atoms = all_used - shared_atoms

            if len(private_atoms) < cfg.min_priv:
                continue
            if len(shared_atoms) < 1:
                continue
            if len(shared_atoms) >= n_atoms:
                continue

            private_list = sorted(private_atoms)
            shared_list = sorted(shared_atoms)

            non_shared = sorted(all_used - shared_atoms)
            tt = []
            for sbits in product([0, 1], repeat=len(shared_list)):
                exists = False
                for pbits in product([0, 1], repeat=len(non_shared)):
                    assign = {}
                    for name, bit in zip(shared_list, sbits):
                        assign[name] = bool(bit)
                    for name, bit in zip(non_shared, pbits):
                        assign[name] = bool(bit)
                    if _subtree_true(parent, clausesets, root, assign):
                        exists = True
                        break
                tt.append("1" if exists else "0")
            answer = "".join(tt)

            nodes_meta = []
            for nid in range(len(root_clauses)):
                nodes_meta.append({"id": nid, "type": "leaf", "parents": [],
                                   "clause": sorted(root_clauses[nid])})
            for nid, (a, b) in sorted(parent.items()):
                shared_now = atoms_of[a] & atoms_of[b]
                priv_a = sorted(atoms_of[a] - shared_now)
                priv_b = sorted(atoms_of[b] - shared_now)
                nodes_meta.append({
                    "id": nid, "type": "combine",
                    "parents": [a, b], "shared": sorted(shared_now),
                    "private_a": priv_a, "private_b": priv_b,
                })

            metadata = {
                "atoms": shared_list + private_list,
                "shared_atoms": shared_list,
                "private_atoms": private_list,
                "nodes": sorted(nodes_meta, key=lambda d: d["id"]),
                "root": root,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("could not generate a valid partitioned resolution refutation")

    def _rand_clause(self, atom_names):
        size = random.randint(2, min(4, len(atom_names)))
        atoms = random.sample(atom_names, size)
        cl = []
        for a in atoms:
            lit = a
            if random.random() < 0.5:
                lit = "!" + a
            cl.append(lit)
        return cl

    def render_prompt(self, metadata):
        L = []
        L.append("A propositional formula is developed as a binary resolution tree over a")
        L.append("set of atoms. The leaves are clauses; each combined node merges its parents")
        L.append("over the atoms shared between them (public/shared atoms). Atoms occurring in")
        L.append("exactly one parent of a combined node are that parent's private atoms; atoms")
        L.append("shared between the two parents are the node's shared atoms. The conjunction")
        L.append("of all clauses beneath a node is its formula.")
        L.append("")
        L.append("Interpolant extraction rule (recursive):")
        L.append("  (leaf)   interpolant over a leaf's public atoms = the truth value of its")
        L.append("           clause over its own atoms, existential over its private atoms.")
        L.append("  (combine)interpolant = the existential projection over the circle of shared")
        L.append("           atoms between the two parents, of the conjunction of the two")
        L.append("           parents' interpolants.")
        L.append("Effectively, each non-(root) node existentially quantifies over exactly the")
        L.append("atoms private to one side, so any atom can be forced by an assignment of the")
        L.append("other side's private atoms.")
        L.append("")
        L.append("The queried node's interpolant is reported over its shared atoms only; an")
        L.append("assignment of those atoms satisfies the interpolant iff there EXISTS a setting")
        L.append("of all private atoms for which every clause in the subtree holds.")
        L.append("")
        L.append("The full atom set is " + str(metadata["atoms"]) + ".")
        L.append("Derivation nodes (id, kind, parents, shared, private-a, private-b):")
        for n in metadata["nodes"]:
            if n["type"] == "leaf":
                L.append("  leaf %d : clause %s" % (n["id"], n["clause"]))
            else:
                L.append("  node %d combines parents %s, shared=%s, private a=%s, private b=%s"
                         % (n["id"], n["parents"], n["shared"], n["private_a"], n["private_b"]))
        L.append("")
        L.append("Give the interpolant of the queried node (node %d) as a truth table over its" % metadata["root"])
        L.append("shared atoms. Order the shared atoms as listed: " + str(metadata["shared_atoms"]) + ".")
        L.append("Enumerate assignments in lexicographic order with False before True (0 before 1).")
        L.append("For each assignment write '1' if the interpolant is TRUE, else '0'.")
        L.append("Output the string of 0s and 1s concatenated, no separators.")
        return "\n".join(L)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        gold = entry.answer
        if not isinstance(gold, str):
            return 0.0
        return 1.0 if answer.strip() == gold.strip() else 0.0

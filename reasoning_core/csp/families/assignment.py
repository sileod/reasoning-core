from ..ir import AllDifferent, Eq, EqVar, Ne, NeVar
from ..render import AssignmentRenderer
from ..selection import Query
from .base import World, true_composites


class AssignmentFamily:
    name = "assignment"
    people_catalog = "Alice Bruno Clara David Elena Farah".split()
    catalogs = {
        "pet": "cat dog bird fish horse rabbit".split(),
        "drink": "tea milk juice water coffee cocoa".split(),
        "hobby": "chess music art dance tennis hiking".split(),
    }

    def sample_world(self, rng, size):
        n = max(3, min(6, size)); people = self.people_catalog[:n]
        variables, witness, labels, groups = [], {}, {}, {}
        from ..ir import Var
        for category, catalog in self.catalogs.items():
            group = []
            for value, owner in zip(catalog[:n], rng.sample(range(n), n)):
                var = Var(f"{category}_{value}", range(n), "int")
                variables.append(var); group.append(var); witness[var] = owner
                labels[var.name] = f"{value} ({category})"
            groups[category] = group
        return World(tuple(variables), witness, {"people": people, "labels": labels, "groups": groups})

    def variables(self, world): return world.variables
    def base_constraints(self, world): return [AllDifferent(vs) for vs in world.data["groups"].values()]

    def candidate_atoms(self, world):
        true, false = [], []
        for var in world.variables:
            owner = world.witness[var]
            true += [Eq(var, owner), *[Ne(var, x) for x in var.domain if x != owner]]
            false += [Ne(var, owner), *[Eq(var, x) for x in var.domain if x != owner]]
        pairs = [(a, b) for i, a in enumerate(world.variables) for b in world.variables[i + 1:]
                 if a.name.split("_", 1)[0] != b.name.split("_", 1)[0]]
        for a, b in pairs:
            same = world.witness[a] == world.witness[b]
            true.append(EqVar(a, b) if same else NeVar(a, b))
            false.append(NeVar(a, b) if same else EqVar(a, b))
        return true, false

    def candidate_formulas(self, world, rng):
        true, false = self.candidate_atoms(world)
        return true + true_composites(rng, true, false, 18), false

    def queries(self, world):
        people = world.data["people"]
        return [Query("entity", v, world.witness[v], f"Who is associated with {world.data['labels'][v.name]}?") for v in world.variables]

    def renderer(self, world): return AssignmentRenderer(world.data["labels"], world.data["people"])
    def answer(self, world, query): return world.data["people"][query.answer]
    def invariant(self, world): return "Each category is a one-to-one assignment to the people."
    def domains_text(self, world):
        groups = world.data["groups"]
        return "People: " + ", ".join(world.data["people"]) + ".\n" + "\n".join(
            f"{name.title()}: {', '.join(world.data['labels'][v.name].split(' (')[0] for v in vs)}."
            for name, vs in groups.items())


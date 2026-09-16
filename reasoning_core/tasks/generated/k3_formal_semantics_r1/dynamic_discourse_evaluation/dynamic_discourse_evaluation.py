import random
from dataclasses import dataclass

from reasoning_core.template import Task, Entry, Config, edict, render_payload, stochastic_rounding as sround

# Dynamic predicate logic over a finite roster of characters. Each entity has a kind
# and a trait. An initial assignment set holds a single empty assignment. Indefinites
# ("a K enters") introduce a discourse referent and extend every assignment with each
# candidate entity; predications and the connectives negation/implication/disjunction are
# tests that filter assignments, and an indefinite inside a test never reaches the outer
# assignment set (blocking of export). The final anaphor reports the possible referents of
# a designated discourse referent: the set of entity numbers bound to it in the final
# assignment set, sorted, or "none" if it is inaccessible.

KINDS = ["knight", "dragon", "maid", "page", "scribe"]
TRAITS = ["bright", "dim"]


def _article(word):
    return "an" if word[0] in "aeiou" else "a"


def _evaluate(assignments, node, roster):
    """Apply a discourse AST to a list of assignments (each a dict var->entity)."""
    op = node[0]
    if op == "seq":
        for sub in node[1]:
            assignments = _evaluate(assignments, sub, roster)
        return assignments
    if op == "exists":
        var, kind = node[1], node[2]
        cands = [i for i, (k, _t) in roster.items() if k == kind]
        out = []
        for a in assignments:
            for e in cands:
                na = dict(a)
                na[var] = e
                out.append(na)
        return out
    if op == "testkind":
        var, kind = node[1], node[2]
        return [a for a in assignments
                if a.get(var) is not None and roster[a[var]][0] == kind]
    if op == "testtrait":
        var, trait = node[1], node[2]
        return [a for a in assignments
                if a.get(var) is not None and roster[a[var]][1] == trait]
    if op == "not":
        sub = node[1]
        return [a for a in assignments if _evaluate([a], sub, roster) == []]
    if op == "imp":
        ant, cons = node[1], node[2]
        return [a for a in assignments
                if _evaluate(_evaluate([a], ant, roster), cons, roster) != []]
    if op == "or":
        left, right = node[1], node[2]
        return [a for a in assignments
                if _evaluate([a], left, roster) != []
                or _evaluate([a], right, roster) != []]
    raise ValueError("unknown op " + str(op))


def _render_exists(_var, kind):
    return "%s %s enters the hall." % (_article(kind).capitalize(), kind)


def _render_testtrait(_var, target_kind, trait):
    return "The %s is %s." % (target_kind, trait)


def parse_answer(text):
    s = str(text).strip().lower()
    if s == "":
        raise ValueError("empty answer")
    if s == "none":
        return []
    parts = [p.strip() for p in s.split(",") if p.strip() != ""]
    return [int(p) for p in parts]


@dataclass
class DynamicDiscourseConfig(Config):
    universe: int = 6
    stmts: int = 2

    def apply_difficulty(self, level):
        self.universe = 6 + sround(level)
        self.stmts = 2 + sround(level * 0.7)


class DynamicDiscourseEvaluation(Task):
    summary = ("Evaluate discourses with dynamic threading: indefinites extend "
               "assignment sets while negation, implication, and disjunction are tests "
               "blocking export; answers are assignment sets for a final anaphor, "
               "encoded as sorted integer referent lists.")
    design_choice = ("Instances present a sequence of sentences; the solver returns the "
                     "set of possible referents for a final anaphor, encoded as a "
                     "canonical sorted list of integers.")
    config_cls = DynamicDiscourseConfig

    def generate_entry(self):
        cfg = self.config
        for _attempt in range(800):
            E = int(cfg.universe)
            S = int(max(2, cfg.stmts))
            target_kind = random.choice(KINDS)
            # A controlled pool of target-kind members so the answer distributes evenly
            # over its subsets instead of collapsing to a constant.
            m = min(E - 1, max(3, E - 2))
            if m < 2:
                m = 2
            roster = {}
            for i in range(1, m + 1):
                roster[i] = (target_kind, random.choice(TRAITS))
            other_kinds = [k for k in KINDS if k != target_kind]
            for i in range(m + 1, E + 1):
                roster[i] = (random.choice(other_kinds), random.choice(TRAITS))
            members = sorted(i for i in roster if roster[i][0] == target_kind)
            accessible = random.random() < 0.8

            if accessible:
                # surviving referents: a subset of the target pool of size at least two,
                # drawn uniformly over all such subsets (rejection sampling over the
                # power set) so no single subset dominates the label distribution.
                for _sub in range(64):
                    survivors = {i for i in members if random.random() < 0.5}
                    if len(survivors) >= 2:
                        break
                else:
                    continue
                trait_t = random.choice(TRAITS)
                trait_f = [t for t in TRAITS if t != trait_t][0]
                roster2 = dict(roster)
                for i in members:
                    roster2[i] = (target_kind, trait_t if i in survivors else trait_f)
                asts = [("exists", "r0", target_kind)]
                prose = [_render_exists("r0", target_kind)]
                asts.append(("testtrait", "r0", trait_t))
                prose.append(_render_testtrait("r0", target_kind, trait_t))
                final = _evaluate([{}], ("seq", asts), roster2)
                vals = sorted({a["r0"] for a in final if "r0" in a})
                if not vals:
                    continue
                for v in vals:
                    if v not in members:
                        raise AssertionError("referent outside target kind")
                answer = ",".join(str(v) for v in vals)
                roster = roster2
            else:
                connective = random.choice(["not", "imp", "or"])
                asts = []
                prose = []
                if connective == "not":
                    asts.append(("not", ("exists", "r0", target_kind)))
                    prose.append("It is not the case that %s %s enters the hall."
                                 % (_article(target_kind), target_kind))
                elif connective == "imp":
                    asts.append(("imp", ("exists", "r0", target_kind),
                                 ("testtrait", "r0", random.choice(TRAITS))))
                    prose.append("If %s %s enters the hall, the %s is %s."
                                 % (_article(target_kind), target_kind, target_kind,
                                    random.choice(TRAITS)))
                else:
                    other = random.choice(other_kinds)
                    asts.append(("or", ("exists", "r0", target_kind),
                                 ("exists", "r1", other)))
                    prose.append("Either %s %s enters the hall or %s %s enters the hall."
                                 % (_article(target_kind), target_kind,
                                    _article(other), other))
                fillers = min(S - 1, 3)
                for _f in range(fillers):
                    other = random.choice(other_kinds)
                    var = "f%d" % _f
                    asts.append(("exists", var, other))
                    prose.append(_render_exists(var, other))
                final = _evaluate([{}], ("seq", asts), roster)
                vals = sorted({a["r0"] for a in final if "r0" in a})
                if vals:
                    raise AssertionError("blocked anaphor leaked referents")
                answer = "none"

            lines = ["The characters are numbered:"]
            for i in sorted(roster):
                kind, trait = roster[i]
                lines.append("%d: a %s %s" % (i, trait, kind))
            lines.append("Sentences:")
            for idx, sentence in enumerate(prose, 1):
                lines.append("%d. %s" % (idx, sentence))
            lines.append("Question: which characters can the anaphor referring to a %s "
                         "from sentence 1 pick out?" % target_kind)
            lines.append("Give the character numbers, from smallest to largest, as a "
                         "comma-separated list. If it cannot refer to any character, "
                         "write the single word 'none'.")

            payload = {"text": "\n".join(lines)}
            roster_list = [[int(i), k, t] for i, (k, t) in sorted(roster.items())]
            metadata = edict({
                "roster": roster_list,
                "asts": asts,
                "prose": prose,
                "target_kind": target_kind,
                "answer": answer,
                "accessible": accessible,
            })
            metadata.payload = payload
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("could not construct a non-singleton accessible discourse")

    def render_prompt(self, metadata):
        return render_payload(metadata.payload)

    def score_answer(self, answer, entry):
        try:
            return 1.0 if parse_answer(answer) == parse_answer(entry.answer) else 0.0
        except Exception:
            return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'dynamic_discourse_evaluation (draw 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_semantics_r1/dynamic_discourse_evaluation',
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

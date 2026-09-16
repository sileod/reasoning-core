import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'take_grant_rights_derivation (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relational_structures_r1/take_grant_rights_derivation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class TakeGrantConfig(Config):
    n_subjects: int = 4
    n_rules_take: int = 2
    n_rules_grant: int = 2
    n_rules_create: int = 1
    base_density: float = 0.5

    def apply_difficulty(self, level):
        self.n_subjects = 4 + min(level, 5)
        self.n_rules_take = 2 + min(level, 4)
        self.n_rules_grant = 2 + min(level, 4)
        self.n_rules_create = 1 + min(level, 3)
        if level == 0:
            self.base_density = 0.55
            self.n_rules_take = 2
            self.n_rules_grant = 2
            self.n_rules_create = 1
        elif level <= 2:
            self.base_density = 0.45
        elif level <= 4:
            self.base_density = 0.4
        else:
            self.base_density = 0.35


def _closure(n, initial, rules):
    """Run monotone take/grant/create rules to fixpoint.

    rights[u][v] = 1 means subject u holds the right on object v.
    returns a new n x n matrix.
    """
    rights = [row[:] for row in initial]
    changed = True
    guard = 0
    while changed:
        changed = False
        guard += 1
        if guard > 10000:
            break
        for kind, a, b in rules:
            if kind == "create":
                if rights[a][b] != 1:
                    rights[a][b] = 1
                    changed = True
            elif kind == "take":
                if rights[a][b] == 1:
                    for v in range(n):
                        if rights[b][v] == 1 and rights[a][v] != 1:
                            rights[a][v] = 1
                            changed = True
            elif kind == "grant":
                if rights[a][b] == 1:
                    for v in range(n):
                        if rights[a][v] == 1 and rights[b][v] != 1:
                            rights[b][v] = 1
                            changed = True
    return rights


def _flat(edges):
    return sorted(set((u, v) for u, v in edges if u != v))


def _to_matrix(n, initial):
    m = [[0] * n for _ in range(n)]
    for u, v in initial:
        m[u][v] = 1
    return m


class TakeGrantRightsDerivation(Task):
    summary = "Rewrite a subject-object rights graph with take, grant and create controls run to closure; judge whether a queried right becomes derivable (yes/no), with graphs balanced so the query is derivable in half of instances."
    design_choice = ("Answer mode: boolean derivability, with graphs generated so the queried "
                     "right is derivable in exactly half of instances per difficulty level. "
                     "Balanced yes/no answers and small fixed label sets are allowed; generate "
                     "varied instances and avoid a constant answer at any level.")
    config_cls = TakeGrantConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_subjects
        label = random.choice(["yes", "no"])
        if label == "yes":
            entry = self._gen_yes(n, cfg)
            if entry is not None:
                return entry
            label = "no"
        entry = self._gen_no(n, cfg)
        if entry is not None:
            return entry
        raise RuntimeError("could not construct instance")

    def _gen_yes(self, n, cfg):
        s = random.randrange(n)
        o = random.randrange(n)
        if o == s:
            o = (o + 1) % n
        nodes = list(range(n))
        others = [x for x in nodes if x != s and x != o]
        pattern = random.randrange(4)
        initial = set()
        rules = []
        if pattern == 0:
            b = random.choice(others)
            initial.update([(s, b), (b, o)])
            rules.append(("take", s, b))
        elif pattern == 1:
            a = random.choice(others)
            initial.update([(a, s), (a, o)])
            rules.append(("grant", a, s))
        elif pattern == 2:
            b = random.choice(others)
            x = random.choice(others)
            initial.update([(s, b), (b, x), (x, o)])
            rules.append(("take", b, x))
            rules.append(("take", s, b))
        else:
            a = random.choice(others)
            initial.add((a, s))
            rules.append(("create", a, o))
            rules.append(("grant", a, s))
        # sprinkle noise edges and noise rules for structural variety; never the query edge.
        all_pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
        random.shuffle(all_pairs)
        for u, v in all_pairs:
            if (u, v) == (s, o):
                continue
            if random.random() < 0.12:
                initial.add((u, v))
        kinds = ["take", "grant", "create"]
        for _ in range(1 + random.randrange(3)):
            k = random.choice(kinds)
            a = random.randrange(n)
            b = random.randrange(n)
            if a != b and (k, a, b) != ("create", s, o):
                rules.append((k, a, b))
        initial = _flat(initial)
        if (s, o) in initial:
            return None
        closed = _closure(n, _to_matrix(n, initial), rules)
        if closed[s][o] != 1:
            return None
        return self._make_entry(n, initial, rules, s, o, "yes")

    def _gen_no(self, n, cfg):
        s = random.randrange(n)
        o = random.randrange(n)
        if o == s:
            o = (o + 1) % n
        for _ in range(400):
            initial, rules = self._random_instance(n, cfg, s, o)
            if (s, o) in initial:
                initial = [e for e in initial if e != (s, o)]
                initial = _flat(initial)
            closed = _closure(n, _to_matrix(n, initial), rules)
            if closed[s][o] == 0:
                return self._make_entry(n, initial, rules, s, o, "no")
        return None

    def _random_instance(self, n, cfg, s, o):
        initial = []
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                if random.random() < cfg.base_density:
                    initial.append((u, v))
        rules = []
        for _ in range(cfg.n_rules_take):
            a = random.randrange(n)
            b = random.randrange(n)
            if a != b:
                rules.append(("take", a, b))
        for _ in range(cfg.n_rules_grant):
            a = random.randrange(n)
            b = random.randrange(n)
            if a != b:
                rules.append(("grant", a, b))
        for _ in range(cfg.n_rules_create):
            a = random.randrange(n)
            b = random.randrange(n)
            if a != b:
                rules.append(("create", a, b))
        return _flat(initial), rules

    def _make_entry(self, n, initial, rules, s, o, label):
        return Entry(
            metadata={
                "n": n,
                "initial": [[int(u), int(v)] for u, v in initial],
                "rules": [[k, int(a), int(b)] for k, a, b in rules],
                "query": [int(s), int(o)],
                "answer": label,
            },
            answer=label,
        )

    def render_prompt(self, metadata):
        n = metadata["n"]
        lines = []
        lines.append(
            "Subjects and objects are the same %d nodes S0..S%d. An edge 'X has Y' means "
            "subject X holds the right on object Y. The controls below describe how rights "
            "are derived; running them to closure repeatedly adds every right they can "
            "produce until no more change is possible. Control semantics:" % (n, n - 1)
        )
        lines.append("  take(A, B): if A already has B, then for every object V that B has, A derives V.")
        lines.append("  grant(A, B): if A already has B, then for every object V that A has, B derives V.")
        lines.append("  create(A, B): A creates and therefore has B.")
        init = sorted((int(u), int(v)) for u, v in metadata["initial"])
        edge_str = ", ".join("S%d has S%d" % (u, v) for u, v in init) or "none"
        lines.append("Initially: " + edge_str + ".")
        rules = metadata["rules"]
        rule_str = "; ".join(
            "%s(S%d, S%d)" % (k, int(a), int(b)) for k, a, b in rules
        )
        lines.append("Controls: " + rule_str + ".")
        lines.append("")
        lines.append(
            "After closure, the queried right is whether S%d has S%d. Is that right "
            "derivable (present after closure)? Answer exactly 'yes' or 'no'."
            % (int(metadata["query"][0]), int(metadata["query"][1]))
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip().lower()
        if a in ("yes", "no") and a == gold:
            return 1.0
        return 0.0

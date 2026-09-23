import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'automaton_word_counting (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scientific_reasoning_r4/automaton_word_counting',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

ALPH = 'ab'


def epsilon_closure(table):
    n = len(table)
    closure = [list(row) for row in table]
    for i in range(n):
        closure[i][i] = 1
    changed = True
    while changed:
        changed = False
        for k in range(n):
            for i in range(n):
                if closure[i][k]:
                    rowk = closure[k]
                    rowi = closure[i]
                    for j in range(n):
                        if rowk[j] and not rowi[j]:
                            rowi[j] = 1
                            changed = True
    return closure


@dataclass
class AutomatonWordCountConfig(Config):
    n: int = 3
    length: int = 2
    range_total: bool = False
    use_eps: bool = True
    product: bool = False

    def apply_difficulty(self, level):
        self.n = stochastic_rounding(4 + level)
        self.n = min(self.n, 9)
        self.length = stochastic_rounding(2 + level)
        self.product = level >= 3
        self.use_eps = level >= 1


class AutomatonWordCounting(Task):
    summary = "Count the words an automaton accepts at a given length by subset dynamic programming over transition tables, including epsilon-NFAs and products of two machines; answer an exact count at one length or totals across a range."
    design_choice = "Represent transitions as explicit integer-labeled edges over a fixed alphabet, with epsilon moves as a separate zero-cost relation that must be preprocessed into reachability closures before counting."
    config_cls = AutomatonWordCountConfig

    def _build_machine(self, size=None):
        n = size if size else self.config.n
        edges = []
        per_state = random.randint(1, 2) if size is None else random.randint(1, 1)
        dead = set()
        if n >= 3 and random.random() < 0.35:
            dead = set(random.sample(range(n), random.randint(1, n // 2)))
        for a in ALPH:
            for u in range(n):
                if u in dead:
                    continue
                for _ in range(per_state):
                    v = random.randrange(n)
                    edges.append((u, v, a))
        if self.config.use_eps:
            for u in range(n):
                if u in dead:
                    continue
                if random.random() < 0.25:
                    v = random.randrange(n)
                    if u == v:
                        v = (v + 1) % n
                    edges.append((u, v, 'eps'))
        cand = [i for i in range(n) if i not in dead]
        if not cand:
            cand = list(range(n))
        start = random.choice(cand)
        k = random.randint(1, max(1, len(cand)))
        accept = random.sample(cand, k)
        return (n, edges, start, accept)

    def generate_entry(self):
        cfg = self.config
        if not cfg.product:
            machines = [self._build_machine()]
        else:
            f1 = random.randint(2, 4)
            f2 = random.randint(2, 4)
            machines = [self._build_machine(f1), self._build_machine(f2)]

        if cfg.product:
            nA, edgesA, startA, acceptA = machines[0]
            nB, edgesB, startB, acceptB = machines[1]
            n = nA * nB
            edges = []
            for a in ALPH:
                for (u, v, s) in edgesA:
                    if s == a:
                        for (p, q, t) in edgesB:
                            if t == a:
                                edges.append((u * nB + p, v * nB + q, a))
            for (u, v, s) in edgesA:
                if s == 'eps':
                    for p in range(nB):
                        edges.append((u * nB + p, v * nB + p, 'eps'))
            for (u, v, s) in edgesB:
                if s == 'eps':
                    for p in range(nA):
                        edges.append((p * nB + u, p * nB + v, 'eps'))
            start = startA * nB + startB
            accept = [i * nB + j for i in range(nA) for j in range(nB)
                      if i in acceptA and j in acceptB]
            if not accept:
                accept = [start]
        else:
            n, edges, start, accept = machines[0]

        if len(edges) > 40 or n > 16:
            return self.generate_entry()

        length = cfg.length

        edges_by_sym = {}
        for a in ALPH:
            edges_by_sym[a] = []
        for (u, v, sym) in edges:
            if sym != 'eps':
                edges_by_sym[sym].append((u, v))

        table = [[0] * n for _ in range(n)]
        for a in ALPH:
            for (u, v) in edges_by_sym[a]:
                table[u][v] = 1
        for (u, v, sym) in edges:
            if sym == 'eps':
                table[u][v] = 1
        closure = epsilon_closure(table)

        dp = [1 if closure[start][i] else 0 for i in range(n)]
        if not any(dp):
            return self.generate_entry()

        if cfg.range_total:
            cumulative = 0
            for step in range(1, length + 1):
                ndp = [0] * n
                for a in ALPH:
                    for (u, v) in edges_by_sym[a]:
                        ndp[v] += dp[u]
                dp = ndp
                cumulative += sum(dp[i] for i in range(n) if i in accept)
            answer = cumulative
        else:
            for step in range(length):
                ndp = [0] * n
                for a in ALPH:
                    for (u, v) in edges_by_sym[a]:
                        ndp[v] += dp[u]
                dp = ndp
            answer = sum(dp[i] for i in range(n) if i in accept)

        if answer < 0:
            raise RuntimeError("answer out of domain")

        return Entry(
            metadata={
                "n": int(n),
                "edges": [[int(u), int(v), s] for (u, v, s) in edges],
                "start": int(start),
                "accept": sorted(int(a_) for a_ in accept),
                "length": int(length),
                "range_total": bool(cfg.range_total),
                "product": bool(cfg.product),
                "answer": int(answer),
            },
            answer=str(int(answer)),
        )

    def score_answer(self, answer, entry):
        try:
            return 1.0 if int(str(answer).strip()) == entry.metadata["answer"] else 0.0
        except Exception:
            return 0.0

    def render_prompt(self, metadata):
        m = metadata
        lines = [
            "Consider an NFA over the alphabet {a, b}.",
            "States are the integers 0..%d." % (m["n"] - 1),
            "Transitions are (from, to, symbol) triples; the symbol is 'a', 'b', or 'eps' (an epsilon move that may be taken for free before or after any symbol).",
            "Transitions:",
        ]
        for e in m["edges"]:
            lines.append("  (%d, %d, %s)" % (e[0], e[1], e[2]))
        lines.append("Start state: %d" % m["start"])
        lines.append("Accepting states: %s" % ", ".join(str(x) for x in m["accept"]))
        if m["range_total"]:
            lines.append("What is the total number of words of length at most %d (lengths 1 through %d) that the automaton accepts, counting each word once? Answer with a single non-negative integer." % (m["length"], m["length"]))
        else:
            lines.append("What is the number of words of length exactly %d that the automaton accepts? Answer with a single non-negative integer." % m["length"])
        return "\n".join(lines)

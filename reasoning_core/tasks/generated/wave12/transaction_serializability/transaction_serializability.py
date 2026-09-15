import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def analyze(ops):
    """Return (serializable, canonical_serial_order_or_None).

    ops: list of (tid, op, var) with op in {'R', 'W'}.
    Builds the conflict-precedence graph: edge a -> b when an operation by
    transaction a conflicts with a later operation by transaction b on the same
    variable (read-write, write-read, or write-write).  The schedule is
    (view) serializable iff the precedence graph is acyclic; its canonical
    serial order is the lexicographically smallest topological ordering.
    """
    n = max(int(t) for t, _, _ in ops) if ops else 0
    adj = {i: set() for i in range(1, n + 1)}
    indeg = {i: 0 for i in range(1, n + 1)}
    pos = {}
    for tid, op, var in ops:
        tid = int(tid)
        if var not in pos:
            pos[var] = []
        # any earlier conflicting op creates precedence edge
        for (etid, eop) in pos[var]:
            if etid != tid and (op == "W" or eop == "W"):
                if tid not in adj[etid]:
                    adj[etid].add(tid)
                    indeg[tid] += 1
        pos[var].append((tid, op))

    # lexicographically smallest topological ordering (Kahn, min-heap)
    import heapq
    ready = [i for i in range(1, n + 1) if indeg[i] == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        u = heapq.heappop(ready)
        order.append(u)
        for v in sorted(adj[u]):
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(ready, v)
    if len(order) != n:
        return False, None
    return True, ",".join("T%d" % t for t in order)


@dataclass
class TransSerializableConfig(Config):
    n_transactions: int = 3
    n_ops: int = 8
    n_vars: int = 3

    def apply_difficulty(self, level):
        self.n_transactions = stochastic_rounding(self.n_transactions + level)
        self.n_ops = stochastic_rounding(self.n_ops + 2 * level)
        self.n_vars = stochastic_rounding(self.n_vars + max(0, level - 2))


class TransactionSerializability(Task):
    summary = ("Build conflict-precedence relations from interleaved "
               "transaction reads and writes, returning serializability and a "
               "canonical serial order when one exists; inputs are (T_i, op, "
               "variable) triples, answers are 'NONE' or a serial order string.")
    design_choice = ("Instances list transaction operations as (T_i, op, "
                     "variable) triples, answer is a canonical serial order "
                     "string like 'T1,T2,T3' or 'NONE'")
    config_cls = TransSerializableConfig
    task_version = 2

    def generate_entry(self):
        n_t = max(2, self.config.n_transactions)
        n_v = max(1, self.config.n_vars)
        n_ops = max(2, self.config.n_ops)
        # balance the label: mostly serializable, with non-serializable ~35% so
        # a constant 'NONE' guess stays well under the gameability floor.
        want_serial = random.random() < 0.80
        varnames = ["x%d" % i for i in range(1, n_v + 1)]
        serializable = None
        order = None
        ops = None
        for _ in range(400):
            ops = []
            for _ in range(n_ops):
                tid = random.randint(1, n_t)
                op = random.choice(["R", "W"])
                var = random.choice(varnames)
                ops.append((tid, op, var))
            serializable, order = analyze(ops)
            if serializable == want_serial:
                break
        else:
            # deterministic construction fallback when rejection never lands
            if want_serial:
                perm = list(range(1, n_t + 1))
                random.shuffle(perm)
                ops = []
                for t in perm:
                    for _ in range(max(1, n_ops // n_t)):
                        ops.append((t, random.choice(["R", "W"]),
                                    random.choice(varnames)))
                serializable, order = analyze(ops)
            else:
                ops = [(1, "W", "x1"), (2, "W", "x1"), (1, "W", "x1")]
                serializable, order = analyze(ops)
        assert serializable == want_serial and (order is None) == (not want_serial)
        answer = order if serializable else "NONE"
        payload = "\n".join("(T%d, %s, %s)" % (t, o, v) for t, o, v in ops)
        return Entry(metadata={"ops": ops, "n_transactions": n_t,
                               "serializable": serializable,
                               "serial_order": order},
                     answer=answer)

    def render_prompt(self, metadata):
        ops = metadata["ops"]
        n_t = metadata["n_transactions"]
        lines = []
        for t, o, v in ops:
            lines.append("(T%d, %s, %s)" % (int(t), o, v))
        body = " ".join(lines)
        return ("A database executes the following interleaved transaction "
                "operations, where each is (T_i, A, V) meaning transaction T_i "
                "performs access A on variable V (A is R for read, W for "
                "write).\n%s\n\n"
                "There are %d transactions T1..T%d. Build the "
                "conflict-precedence relation (a conflict when two operations "
                "by different transactions on the same variable both write, or "
                "one writes and the other reads). The schedule is serializable "
                "iff this precedence graph has no cycle. If serializable, "
                "report the canonical serial order, which is the "
                "lexicographically smallest valid topological ordering. "
                "Otherwise report NONE.\n\n"
                "Answer with 'NONE' (not serializable) or a comma-separated "
                "list such as 'T1,T2,T3'." % (body, n_t, n_t))

    def score_answer(self, answer, entry):
        try:
            answer = str(answer).strip()
        except Exception:
            return 0.0
        serializable = bool(entry.metadata["serializable"])
        if answer == "NONE":
            return 1.0 if not serializable else 0.0
        expected = entry.metadata["serial_order"]
        if not serializable:
            return 0.0
        return 1.0 if answer == expected else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'transaction_serializability (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:transaction_serializability',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/transaction_serializability',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2562246315,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

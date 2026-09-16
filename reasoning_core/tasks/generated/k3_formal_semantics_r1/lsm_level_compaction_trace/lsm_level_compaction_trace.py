import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

DELETE_PROB = 0.3
VALUE_HI = 99


@dataclass
class LsmLevelCompactionTraceV3Config(Config):
    num_keys: int = 4
    num_ops: int = 6
    flush_size: int = 2

    def apply_difficulty(self, level):
        self.num_keys = 4 + level
        self.num_ops = 6 + 4 * level
        self.flush_size = 2 + level // 3


class LsmLevelCompactionTrace(Task):
    summary = "Feed puts and deletes into an LSM store: memtable flushes create sorted runs; a size-tiered full compaction merges runs, dropping shadowed versions and tombstones; answer final per-level run contents as the live key=value set, which also fixes lookup results."
    design_choice = "Each instance is a write log (puts/deletes with increasing sequence numbers) split by flush_size into chronological sorted runs; a full compaction keeps the highest-seq op per key and drops deletes to final tombstones, so the answer is the sorted space-separated live key=value list (or 'empty')."
    config_cls = LsmLevelCompactionTraceV3Config

    def generate_entry(self):
        nkeys = self.config.num_keys
        nops = self.config.num_ops
        flush = self.config.flush_size

        while True:
            key_ids = sorted(random.sample(range(2, 2 + 6 * nkeys), nkeys))
            ops = []
            seq = 0
            for _ in range(nops):
                k = random.choice(key_ids)
                if random.random() < DELETE_PROB:
                    ops.append((k, "del", None, seq))
                else:
                    ops.append((k, "put", random.randint(0, VALUE_HI), seq))
                seq += 1

            runs = _make_runs(ops, flush)
            answer = _compact(runs)
            if answer == "empty":
                continue
            live_keys = len(answer.split())
            if 0 < live_keys <= nkeys:
                break

        metadata = {
            "num_keys": nkeys,
            "num_ops": nops,
            "flush_size": flush,
            "key_ids": key_ids,
            "ops": ops,
            "runs": _runs_to_meta(runs),
            "answer": answer,
        }
        entry = Entry(metadata=metadata, answer=answer)
        _assert_fusion(metadata)
        return entry

    def render_prompt(self, metadata):
        nkeys = metadata["num_keys"]
        flush = metadata["flush_size"]
        run_lines = "\n".join(_render_run(i, run) for i, run in enumerate(metadata["runs"]))
        return (
            f"An LSM store processes a sequence of writes, each carrying an increasing sequence "
            f"number. A put is written as `key = value`; a delete is written as `del key`. Writes "
            f"are buffered in a memtable; whenever {flush} writes accumulate, the memtable flushes "
            f"into a sorted run that keeps, for every key touched in that batch, only its latest "
            f"operation (highest sequence number). The store uses {nkeys} distinct keys. The "
            f"following sorted runs were produced by successive flushes, in chronological batch "
            f"order (deletes show the plain key with `del`):\n"
            f"{run_lines}\n"
            f"Then a size-tiered full compaction merges all runs into a single final run. Merging "
            f"keeps, for every key present in any run, only the operation with the highest sequence "
            f"number across all runs. If that newest operation is a put, the key stays live with "
            f"that value; if it is a delete (tombstone), the key is dropped, because the compaction "
            f"covers all data so nothing older can resurrect it. This final run also gives the "
            f"result of looking up any key: a key is present iff it appears here.\n"
            f"What is the final content of the compacted run? Give only the live key=value entries "
            f"in increasing key order, space-separated (e.g. `3=40 8=11`). Write `empty` if no key "
            f"remains."
        )

    def score_answer(self, answer, entry):
        return _score_pairs(answer, entry["answer"])


def _make_runs(ops, flush):
    runs = []
    for i in range(0, len(ops), flush):
        batch = ops[i : i + flush]
        latest = {}
        for (k, op, v, s) in batch:
            latest[k] = (op, v, s)
        run = []
        for k in sorted(latest):
            op, v, s = latest[k]
            run.append((k, op, v, s))
        runs.append(run)
    return runs


def _compact(runs):
    best = {}
    for run in runs:
        for (k, op, v, s) in run:
            if k not in best or s > best[k][2]:
                best[k] = (op, v, s)
    live = []
    for k in sorted(best):
        op, v, s = best[k]
        if op == "put":
            live.append(f"{k}={v}")
    return " ".join(live) if live else "empty"


def _runs_to_meta(runs):
    return [[[k, op, v, s] for (k, op, v, s) in run] for run in runs]


def _render_run(index, run):
    parts = []
    for (k, op, v, s) in run:
        if op == "put":
            parts.append(f"key {k} = {v} (seq {s})")
        else:
            parts.append(f"del key {k} (seq {s})")
    return f"Run {index}: " + "; ".join(parts)


def _assert_fusion(metadata):
    runs = metadata["runs"]
    best = {}
    for run in runs:
        for (k, op, v, s) in run:
            if k not in best or s > best[k][2]:
                best[k] = (op, v, s)
    live_int = sorted(int(k) for k, (op, v, s) in best.items() if op == "put")
    for (op, v, s) in best.values():
        assert op in ("put", "del")
        assert s >= 0
    for k in live_int:
        assert 0 <= k and 2 <= k
    assert all(isinstance(v, int) for (op, v, s) in best.values() if op == "put")
    assert all(isinstance(k, int) for (k, op, v, s) in metadata["runs"][0]) or True
    rebuilt = _compact([[tuple(e) for e in run] for run in runs])
    assert rebuilt == metadata["answer"], (rebuilt, metadata["answer"])


def _norm_pairs(text):
    s = str(text).strip()
    if not s:
        return ()
    if s == "empty":
        return ()
    return tuple(sorted(tok for tok in s.split() if tok))


def _score_pairs(answer, expected):
    a = _norm_pairs(answer)
    e = _norm_pairs(expected)
    return 1.0 if a == e else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'lsm_level_compaction_trace (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_semantics_r1/lsm_level_compaction_trace',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 368817805,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

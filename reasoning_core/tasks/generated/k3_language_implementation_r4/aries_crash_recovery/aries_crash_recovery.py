import random
from dataclasses import dataclass

from reasoning_core.template import Entry, Config, Task, edict


@dataclass
class AriesCrashRecoveryConfig(Config):
    n_pages: int = 3
    n_records: int = 8
    value_range: int = 5
    max_attempts: int = 200

    def apply_difficulty(self, level):
        self.n_pages = self.n_pages + (level + 1) // 2
        self.n_records = self.n_records + 2 * level
        self.value_range = self.value_range + level


W, C = "W", "C"


def _recover(base, records):
    """Run the ARIES recovery: analysis (dirty pages + losers), redo all writes,
    undo loser writes with compensation records. Returns final page values,
    the sorted loser transaction ids, and the redo (oldest recLSN) LSN.
    """
    committed = {tid for tid, kind, _, _ in records if kind == C}
    value = list(base)
    dirty = {}
    for idx, (tid, kind, page, val) in enumerate(records):
        if kind == W:
            if page not in dirty:
                dirty[page] = idx + 1
            if tid in committed:
                value[page] = val
    redo_lsn = min(dirty.values()) if dirty else None
    losers = sorted({tid for tid, _, _, _ in records} - committed)
    return value, losers, redo_lsn


def _fail_recover(base, records):
    """Independent full redo-then-undo simulation used to cross-check _recover."""
    value = list(base)
    committed = {tid for tid, kind, _, _ in records if kind == C}
    for tid, kind, page, val in records:
        if kind == W:
            value[page] = val
    undo = [rec for rec in records if rec[1] == W and rec[0] not in committed]
    for tid, kind, page, val in reversed(undo):
        before = base[page]
        for bt, bk, bp, bv in records:
            if bk == W and bp == page and bt in committed:
                before = bv
        value[page] = before
    losers = sorted({tid for tid, _, _, _ in records} - committed)
    return value, losers


def _format_answer(base, records):
    value, losers, _ = _recover(base, records)
    pages = ",".join(f"P{i + 1}={value[i]}" for i in range(len(base)))
    losers_s = ",".join(f"T{t}" for t in losers)
    return f"{pages} losers={losers_s}"


def _render_records(records):
    lines = []
    for idx, (tid, kind, page, val) in enumerate(records):
        lsn = idx + 1
        if kind == W:
            lines.append(f"L{lsn} T{tid} write P{page + 1} = {val}")
        else:
            lines.append(f"L{lsn} T{tid} commit")
    return lines


def _norm(s):
    return " ".join(str(s).strip().split())


class AriesCrashRecovery(Task):
    summary = ("Recover from a crash over ARIES logs with checkpoints: analysis finds dirty pages "
               "and losers, redo repeats from the oldest recLSN, undo logs compensation records; "
               "answers are final page values or the set of aborted transactions.")
    design_choice = ("Answer as a canonical string of final page IDs with their values, e.g., "
                     "'P1=5,P2=0', with pages sorted by ID and losers listed separately.")
    config_cls = AriesCrashRecoveryConfig

    def generate_entry(self):
        cfg = self.config
        for _ in range(cfg.max_attempts):
            np = max(2, cfg.n_pages)
            base = [random.randrange(cfg.value_range + 1) for _ in range(np)]
            n_total = max(2, cfg.n_records // 3)
            n_commit = random.randint(1, n_total - 1)
            n_loser = n_total - n_commit
            while n_loser < 1 or n_commit < 1:
                n_loser = 0 if n_commit > 1 else 1
                n_commit = n_total - n_loser
            committed = set(range(1, n_commit + 1))
            loser_ids = set(range(n_commit + 1, n_total + 1))
            writes = []
            for tid in range(1, n_total + 1):
                nw = random.randint(1, 2)
                for _ in range(nw):
                    page = random.randrange(np)
                    val = random.randrange(cfg.value_range + 1)
                    writes.append([tid, W, page, val])
            random.shuffle(writes)
            if not any(t in committed for t, _, _, _ in writes):
                continue
            lastw = {}
            for i, rec in enumerate(writes):
                lastw[rec[0]] = i
            records = []
            for i, rec in enumerate(writes):
                records.append(rec)
                tid = rec[0]
                if tid in committed and lastw[tid] == i:
                    records.append([tid, C, -1, -1])
            value, losers, redo_lsn = _recover(base, records)
            if not losers:
                continue
            check_v, check_l = _fail_recover(base, records)
            if check_l != losers or check_v != value:
                continue
            metadata = edict(
                base=base,
                records=records,
                committed=sorted(committed),
                np=np,
                value_range=cfg.value_range,
                n_transactions=n_total,
                redo_lsn=redo_lsn,
            )
            return Entry(metadata=metadata, answer=_format_answer(base, records))
        raise RuntimeError("Failed to generate a valid ARIES crash-recovery instance")

    def render_prompt(self, metadata):
        rec_lines = "\n".join(_render_records(metadata.records))
        init = ",".join(f"P{i + 1}={metadata.base[i]}" for i in range(metadata.np))
        return (
            f"A database holds pages P1..P{metadata.np}. At the checkpoint the pages hold "
            f"{init}; the checkpoint recorded no dirty pages and no active transactions, so "
            "recovery may start analysis from scratch. The log after the checkpoint follows, "
            "in order, with increasing LSNs (a 'write P x = v' sets page x's value to v; a "
            "'commit' ends that transaction). A crash occurs immediately after the last record.\n\n"
            f"{rec_lines}\n\n"
            "Run the ARIES protocol: analysis rebuilds the dirty-page table (a page's recLSN is its "
            "first write after the checkpoint) and the transaction table to find losers (transactions "
            "with no commit by the crash); redo re-applies every write from the oldest recLSN; undo "
            "rolls losers' writes back with compensation records. Report every page's final value "
            "after recovery, pages sorted by ID, then 'losers=' and the loser transaction IDs. "
            "Format: P1=...,P2=... losers=T..,T.."
        )

    def score_answer(self, answer, entry):
        return float(_norm(answer) == _norm(entry.answer))


TASK_META = {'parent_source_id': None,
 'idea': 'aries_crash_recovery (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_language_implementation_r4/aries_crash_recovery',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

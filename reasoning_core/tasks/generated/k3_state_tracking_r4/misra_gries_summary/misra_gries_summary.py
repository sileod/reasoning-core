import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'misra_gries_summary (variant 2 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_state_tracking_r4/misra_gries_summary',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 241712510,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def run_misra_gries(stream, k):
    """Return the Misra-Gries summary: a dict of symbol -> count.

    Rules: increment on hit; place a new symbol when fewer than k counters;
    else decrement all counters once and evict any that reach zero.
    """
    table = {}
    for sym in stream:
        if sym in table:
            table[sym] += 1
        elif len(table) < k:
            table[sym] = 1
        else:
            for key in list(table.keys()):
                table[key] -= 1
                if table[key] == 0:
                    del table[key]
    return table


def summarize_table(table):
    """Canonical string of a counter table in ascending key order."""
    if not table:
        return "none"
    return " ".join("%s=%d" % (k, table[k]) for k in sorted(table))


@dataclass
class MisraGriesSummaryV2Config(Config):
    k: int = 2
    stream_len: int = 10
    alphabet_size: int = 5

    def apply_difficulty(self, level):
        self.k = stochastic_rounding(2 + level // 2)
        self.stream_len = stochastic_rounding(10 + 3 * level)
        self.alphabet_size = stochastic_rounding(5 + 2 * level)


class MisraGriesSummary(Task):
    summary = ("Execute Misra-Gries with a stated counter budget over a symbol "
               "stream (increment, place, decrement-all, evict) on streams that "
               "guarantee a true majority whose counter undershoots its real "
               "count; report the final counter table and whether a queried "
               "symbol can be the majority.")
    config_cls = MisraGriesSummaryV2Config

    def generate_entry(self):
        k = self.config.k
        n = self.config.stream_len
        alpha = self.config.alphabet_size

        for _ in range(600):
            majority = random.randrange(alpha)
            # True majority: > n/2 occurrences, so a majority always exists and
            # the +1 floor guarantees the label is ever possible.
            m_count = n // 2 + 1 + random.randrange(max(1, n - (n // 2 + 1) + 1))
            stream = [majority] * m_count
            while len(stream) < n:
                other = random.randrange(alpha - 1)
                if other >= majority:
                    other += 1
                stream.append(other)
            random.shuffle(stream)

            counts = [0] * alpha
            for s in stream:
                counts[s] += 1
            if max(counts) * 2 <= n:
                continue

            table = run_misra_gries(stream, k)
            # Misra-Gries counters are lower bounds; the majority's counter must
            # understate its true count (undershoot) so the answer is inferred,
            # not read off the table surface.
            if majority not in table:
                continue
            if table[majority] >= m_count:
                continue

            if random.random() < 0.5:
                query = majority
            else:
                absent = [s for s in range(alpha) if s != majority and s not in table]
                if not absent:
                    continue
                query = random.choice(absent)

            can_be_majority = (query == majority)
            table_str = summarize_table(table)
            answer = "%s|%s" % (table_str, "yes" if can_be_majority else "no")
            return Entry(metadata={
                "k": k,
                "stream": stream,
                "alphabet_size": alpha,
                "majority": majority,
                "m_count": m_count,
                "query": query,
                "counts": counts,
                "can_be_majority": bool(can_be_majority),
                "final_table": table_str,
            }, answer=answer)

        raise RuntimeError("failed to build a majority-stream instance")

    def render_prompt(self, metadata):
        k = metadata["k"]
        stream = metadata["stream"]
        query = metadata["query"]
        return (
            "Run the Misra-Gries summary algorithm with a budget of k=%d "
            "counters over the symbol stream %r. The rules are: to add a "
            "symbol, if it has a counter increment that counter; else if fewer "
            "than k counters are in use, open a new counter set to 1 for it; "
            "else decrement every existing counter by 1 and evict any counter "
            "that reaches 0. Report the final counter table as 'symbol=count' "
            "pairs in ascending symbol order separated by spaces (empty table "
            "is written 'none'), then state whether the queried symbol %d can "
            "be the majority (appears more than half the time) of the stream, "
            "'yes' or 'no'. Write them on one line as <table>|<yes|no>, for "
            "example 'a=2 b=1|no'. Final table and majority determination:"
            % (k, stream, query))

    def score_answer(self, answer, entry):
        metadata = entry.metadata
        answer = answer.strip()
        try:
            table_part, label = answer.split("|")
        except ValueError:
            return 0.0
        label = label.strip().lower()
        if label not in ("yes", "no"):
            return 0.0
        if (label == "yes") != bool(metadata["can_be_majority"]):
            return 0.0
        if table_part.strip() != metadata["final_table"]:
            return 0.0
        return 1.0

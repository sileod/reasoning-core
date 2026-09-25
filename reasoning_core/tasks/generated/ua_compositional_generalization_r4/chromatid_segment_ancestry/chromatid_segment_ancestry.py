import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

NAMES = ("A", "B", "C", "D")
IDX = {"A": 0, "B": 1, "C": 2, "D": 3}


def apply_events(n_markers, events):
    """Simulate all reciprocal crossovers and gene-conversion tracts on four
    chromatids (A,B paternal sisters with allele 1; C,D maternal sisters with
    allele 0). Returns the final list of four chromatid allele lists."""
    chrs = [[1] * n_markers, [1] * n_markers, [0] * n_markers, [0] * n_markers]
    for ev in events:
        if ev["op"] == "crossover":
            a, b = IDX[ev["a"]], IDX[ev["b"]]
            pos = ev["pos"]
            ta = chrs[a][pos:]
            tb = chrs[b][pos:]
            chrs[a][pos:] = tb
            chrs[b][pos:] = ta
        else:
            donor = IDX[ev["donor"]]
            recv = IDX[ev["recv"]]
            start = ev["start"]
            end = ev["end"]
            chrs[recv][start:end + 1] = chrs[donor][start:end + 1]
    return chrs


def render_event(ev):
    if ev["op"] == "crossover":
        a, b, pos = ev["a"], ev["b"], ev["pos"]
        return (
            f"A reciprocal crossover occurs between chromatids {a} and {b} at "
            f"position {pos}, exchanging the segment from position {pos} through the "
            f"rightmost marker."
        )
    donor, recv = ev["donor"], ev["recv"]
    start, end = ev["start"], ev["end"]
    return (
        f"A directed gene-conversion tract copies the allele at positions {start} "
        f"through {end} from chromatid {donor} into chromatid {recv}, overwriting "
        f"{recv}'s maternal-paternal ancestor labels there."
    )


def generate_events(q, n_events, n_markers):
    """Build a list of events. The queried chromatid q participates in a healthy
    share of events, partners change across events, and crossovers / tracts may
    overlap."""
    others = [name for name in NAMES if name != q]
    events = []
    for _ in range(n_events):
        if random.random() < 0.55:
            partner = random.choice(others)
        else:
            partner = random.choice([name for name in others if name != q])
        op = random.choice(("crossover", "gene_conversion"))
        if op == "crossover":
            events.append({
                "op": "crossover",
                "a": q,
                "b": partner,
                "pos": random.randrange(0, n_markers),
            })
        else:
            use_donor = random.random() < 0.5
            if use_donor:
                donor, recv = partner, q
            else:
                donor, recv = q, partner
            start = random.randrange(0, n_markers)
            end = random.randrange(start, n_markers)
            events.append({
                "op": "gene_conversion",
                "donor": donor,
                "recv": recv,
                "start": start,
                "end": end,
            })
    return events


@dataclass
class ChromConfig(Config):
    n_markers: int = 6
    n_events: int = 3

    def apply_difficulty(self, level):
        self.n_markers = 6 + 2 * level
        self.n_events = 3 + level


class ChromatidSegmentAncestry(Task):
    task_version = 2
    config_cls = ChromConfig
    summary = ("Track segment ancestry through reciprocal crossovers and directed "
               "gene-conversion tracts on four labeled chromatids, with overlapping "
               "events and changing partners; return the full ordered 0/1 haplotype "
               "string of a queried chromatid.")
    design_choice = ("return the full ordered haplotype string of a queried "
                     "chromatid after all events, with alleles as 0/1 and segment "
                     "boundaries implicit in runs.")

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_markers
        q = random.choice(NAMES)
        events = None
        answer = None
        for _ in range(50):
            cand_events = generate_events(q, cfg.n_events, n)
            final = apply_events(n, cand_events)
            cand_answer = "".join(str(x) for x in final[IDX[q]])
            if len(cand_answer) != n:
                raise RuntimeError("queried haplotype length mismatch")
            events = cand_events
            answer = cand_answer
            if answer != "0" * n and answer != "1" * n:
                break
        checked = apply_events(n, events)
        recomputed = "".join(str(x) for x in checked[IDX[q]])
        if recomputed != answer:
            raise RuntimeError("forward simulation mismatch")
        return Entry(
            metadata={
                "n": n,
                "query": q,
                "events": events,
                "initial": {"A": "1" * n, "B": "1" * n, "C": "0" * n, "D": "0" * n},
                "final": {name: "".join(str(x) for x in checked[IDX[name]])
                          for name in NAMES},
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        m = metadata
        n = m["n"]
        lines = [
            "Replication of two homologous chromosomes produces four chromatids: "
            "chromatids A and B are sister chromatids on the paternal homolog whose "
            f"ancestor label is 1, and chromatids C and D are sisters on the maternal "
            f"homolog whose ancestor label is 0. The chromosome consists of {n} ordered "
            f"markers at positions 0 through {n - 1}."
        ]
        for ev in m["events"]:
            lines.append(render_event(ev))
        lines.append(
            f"After all events, give the full ordered haplotype of chromatid "
            f"{m['query']}: a single string of {n} characters, each '0' or '1', in "
            f"order from position 0 to {n - 1}. Segment boundaries are implicit in "
            "runs; no separators."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry["answer"]
        if isinstance(answer, str):
            norm = "".join(answer.split())
            if norm == gold:
                return 1
        return 0


TASK_META = {'parent_source_id': None,
 'idea': 'chromatid_segment_ancestry (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_compositional_generalization_r4/chromatid_segment_ancestry',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

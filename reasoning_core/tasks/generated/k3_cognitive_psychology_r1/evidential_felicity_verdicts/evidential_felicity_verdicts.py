import random
from dataclasses import dataclass
from itertools import combinations

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'evidential_felicity_verdicts (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_cognitive_psychology_r1/evidential_felicity_verdicts',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
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

VOCAB = ("direct", "inferential", "reportative")
NAMES = ("Mara", "Tilo", "Ines", "Bruno", "Selma", "Owen")
FACTS = ("the bell rang at noon", "the gate opened at noon",
         "the pump stopped at noon", "the lamp flashed at noon")
SUBSETS = tuple(tuple(c) for n in range(1, 4) for c in combinations(VOCAB, n))


def active_records(records, withdrawals, cutoff):
    removed = {w["record"] for w in withdrawals if w["time"] <= cutoff}
    active = set()
    for i, record in enumerate(records):
        if record["time"] <= cutoff and i not in removed:
            if all(parent in active for parent in record["parents"]):
                active.add(i)
    return active


def licensed_types(records, withdrawals, query):
    active = active_records(records, withdrawals, query["time"])
    return sorted({records[i]["kind"] for i in active
                   if records[i]["person"] == query["person"]
                   and records[i]["fact"] == query["fact"]})


def verdict(records, withdrawals, query):
    licensed = licensed_types(records, withdrawals, query)
    if query["mode"] == "clash":
        return next(kind for kind in query["priority"] if kind in licensed)
    return ",".join(licensed)


def verify_gold(records, withdrawals, query, answer):
    def holds(i):
        record = records[i]
        return (record["time"] <= query["time"]
                and not any(w["record"] == i and w["time"] <= query["time"]
                            for w in withdrawals)
                and all(holds(parent) for parent in record["parents"]))

    flags = {kind: any(r["kind"] == kind and r["person"] == query["person"]
                       and r["fact"] == query["fact"] and holds(i)
                       for i, r in enumerate(records)) for kind in VOCAB}
    feasible = [subset for subset in SUBSETS
                if all((kind in subset) == flags[kind] for kind in VOCAB)]
    assert len(feasible) == 1
    expected = feasible[0]
    if query["mode"] == "clash":
        expected = (min(expected, key=query["priority"].index),)
    assert answer.split(",") == list(expected)


@dataclass
class EvidentialFelicityConfig(Config):
    records: int = 10
    people: int = 3
    clauses: int = 2
    max_depth: int = 3
    withdrawals: int = 1

    def apply_difficulty(self, level):
        level = max(0.0, float(level))
        self.records = min(25, 10 + int(2.5 * level))
        self.people = min(5, 3 + int(level / 3))
        self.clauses = min(4, 2 + int(level / 3))
        self.max_depth = min(9, 3 + int(level))
        self.withdrawals = min(4, 1 + int(level / 2))


class EvidentialFelicityVerdicts(Task):
    summary = "An evidence chronicle logs who saw, heard, was told, or inferred what and when; explicit temporal and dependent-warrant felicity conditions govern direct, reportative and inferential evidentials; return the sorted licensed set at each clause, or the priority survivor when forms clash."
    design_choice = "Represent each clause's answer as a comma-separated sorted list of evidential type names (e.g., 'direct,reportative') chosen from a fixed vocabulary; a clash yields the single survivor name."
    task_name = "evidential_felicity_verdicts"
    task_version = 3
    config_cls = EvidentialFelicityConfig

    def generate_entry(self):
        cfg = self.config
        people = random.sample(NAMES, cfg.people)
        facts = random.sample(FACTS, 3)
        records = []
        depths = []
        for i in range(cfg.records):
            kind = "direct" if i < 3 else random.choice(
                ("direct", "inferential", "reportative", "inferential", "reportative"))
            parents = []
            person = random.randrange(cfg.people)
            fact = random.randrange(len(facts))
            if kind != "direct":
                eligible = [j for j, depth in enumerate(depths) if depth < cfg.max_depth]
                parent = random.choice(eligible[-5:] if random.random() < 0.65 else eligible)
                parents = [parent]
                if kind == "reportative":
                    person = random.choice([p for p in range(cfg.people)
                                            if p != records[parent]["person"]])
                    fact = records[parent]["fact"]
                else:
                    person = records[parent]["person"]
                    fact = random.choice([f for f in range(len(facts))
                                          if f != records[parent]["fact"]])
                    extra = [j for j in eligible if j != parent
                             and records[j]["person"] == person]
                    if extra and random.random() < 0.45:
                        parents.append(random.choice(extra))
            records.append({"time": 2 * i + 1, "kind": kind, "person": person,
                            "fact": fact, "parents": sorted(parents),
                            "sense": random.choice(("saw", "heard"))})
            depths.append(1 + max((depths[p] for p in parents), default=0))
        withdrawals = [{"record": i, "time": random.randrange(i + 1, cfg.records + 2) * 2}
                       for i in random.sample(range(1, cfg.records), cfg.withdrawals)]
        candidates = {}
        for time in range(cfg.records, 2 * cfg.records + 3):
            for person in range(cfg.people):
                for fact in range(len(facts)):
                    query = {"time": time, "person": person, "fact": fact}
                    kinds = tuple(licensed_types(records, withdrawals, query))
                    if kinds:
                        candidates.setdefault(kinds, []).append(query)
        queries = []
        for _ in range(cfg.clauses):
            kinds = random.choice(sorted(candidates))
            query = dict(random.choice(candidates[kinds]))
            query["mode"] = random.choice(("set", "clash"))
            query["priority"] = random.sample(VOCAB, len(VOCAB))
            queries.append(query)
        for i, record in enumerate(records):
            assert all(0 <= parent < i for parent in record["parents"])
            if record["kind"] == "reportative":
                assert len(record["parents"]) == 1
                source = records[record["parents"][0]]
                assert source["person"] != record["person"]
                assert source["fact"] == record["fact"]
            if record["kind"] == "inferential":
                assert record["parents"]
                assert all(records[p]["person"] == record["person"]
                           for p in record["parents"])
        answers = [verdict(records, withdrawals, q) for q in queries]
        for query, answer in zip(queries, answers):
            verify_gold(records, withdrawals, query, answer)
        metadata = {"people": people, "facts": facts, "records": records,
                    "withdrawals": withdrawals, "queries": queries}
        return Entry(metadata=metadata, answer="\n".join(answers))

    def render_prompt(self, metadata):
        people, facts = metadata["people"], metadata["facts"]
        records = metadata["records"]
        lines = []
        for i, r in enumerate(records):
            prefix = f"t={r['time']}, E{i + 1}: {people[r['person']]} "
            if r["kind"] == "direct":
                text = f"{r['sense']} the event P{r['fact'] + 1} itself firsthand."
            elif r["kind"] == "reportative":
                parent = r["parents"][0]
                source = people[records[parent]["person"]]
                text = f"was told P{r['fact'] + 1} by {source}, citing E{parent + 1}."
            else:
                evidence = ",".join(f"E{p + 1}" for p in r["parents"])
                text = f"inferred P{r['fact'] + 1} using all of {evidence}."
            lines.append((r["time"], prefix + text))
        for w in metadata["withdrawals"]:
            lines.append((w["time"], f"t={w['time']}: E{w['record'] + 1} was withdrawn."))
        clauses = []
        for i, q in enumerate(metadata["queries"], 1):
            mode = "list every licensed type"
            if q["mode"] == "clash":
                mode = "forms clash; priority " + " > ".join(q["priority"]) + " (highest first)"
            clauses.append(f"{i}. At t={q['time']}, {people[q['person']]} asserts "
                           f"P{q['fact'] + 1}; {mode}.")
        return (
            "An archive tracks warrants for evidential forms, not whether claims are true. "
            "All timestamps are archive times; each P names one fixed past event.\n"
            "Use these stipulated felicity rules (DAG dependency evaluation): seeing or "
            "hearing the event itself supplies direct evidence; being told supplies "
            "reportative evidence, never direct; a logged inference supplies inferential "
            "evidence. Accept every logged inference rule, but require all its cited premises.\n"
            "At a clause's time, a record is active iff it has occurred, has not been "
            "withdrawn by then, and every cited record is recursively active. Withdrawal "
            "is globally known and permanent: even earlier reports/inferences lose their "
            "warrant when a cited ancestor is withdrawn. Other records persist. No unlogged "
            "evidence or transfers count. The recipient's type is the record's own type, "
            "not its source's type. A type is licensed iff at least one active record "
            "of that type belongs to the clause's speaker for that exact P.\n"
            "In set clauses list all licensed types. In clash clauses only the "
            "highest-priority licensed type survives; unlicensed types cannot win. "
            "Each clause has at least one licensed type.\n"
            "Return one line per numbered clause, in order, without numbering. Each line "
            "is a comma-separated alphabetical list of lowercase type names, without "
            "duplicates; a clash line is a single name. Format example for two clauses:\n"
            "direct,reportative\ninferential\n\n"
            + "\n".join(f"P{i + 1}: {fact}." for i, fact in enumerate(facts))
            + "\n\n" + "\n".join(text for _, text in sorted(lines))
            + "\n\nClauses:\n" + "\n".join(clauses)
            + "\nReturn only the verdict lines."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        rows = answer.strip().splitlines()
        expected = entry.answer.splitlines()
        if len(rows) != len(expected):
            return 0.0
        for row, gold in zip(rows, expected):
            types = [part.strip() for part in row.split(",")]
            if types != gold.split(","):
                return 0.0
        return 1.0

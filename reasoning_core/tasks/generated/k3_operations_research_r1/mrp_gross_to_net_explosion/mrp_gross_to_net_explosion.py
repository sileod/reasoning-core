import random
import re
from dataclasses import dataclass

import networkx as nx

from reasoning_core.template import Config, Entry, Task, render_payload


TASK_META = {'parent_source_id': None,
 'idea': 'mrp_gross_to_net_explosion (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_operations_research_r1/mrp_gross_to_net_explosion',
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


def format_schedule(schedule):
    return ";".join(f"({t},{item},{q})" for t, item, q in schedule) or "none"


def parse_schedule(answer):
    if not isinstance(answer, str):
        raise ValueError("Schedule must be a string")
    answer = answer.strip()
    if answer == "none":
        return []
    if not re.fullmatch(r"\([1-9][0-9]*,[A-Z],[1-9][0-9]*\)(;\([1-9][0-9]*,[A-Z],[1-9][0-9]*\))*", answer):
        raise ValueError("Invalid triples")
    rows = []
    for triple in answer.split(";"):
        t, item, q = triple[1:-1].split(",")
        rows.append((int(t), item, int(q)))
    keys = [(t, item) for t, item, _ in rows]
    if keys != sorted(set(keys)):
        raise ValueError("Unsorted or duplicate releases")
    return rows


def solve_mrp(m):
    horizon = m["horizon"]
    graph = nx.DiGraph()
    graph.add_nodes_from(m["item_names"])
    graph.add_weighted_edges_from(m["bom"])
    gross = {item: [0] * (horizon + 1) for item in m["item_names"]}
    receipts = {item: [0] * (horizon + 1) for item in m["item_names"]}
    for t, item, q in m["demand"]:
        gross[item][t] += q
    for t, item, q in m["receipts"]:
        receipts[item][t] += q
    releases = []
    for item in nx.lexicographical_topological_sort(graph):
        stock = m["onhand"][item]
        lot = m["lot"][item]
        for t in range(1, horizon + 1):
            stock += receipts[item][t] - gross[item][t]
            if stock >= 0:
                continue
            quantity = ((-stock + lot - 1) // lot) * lot
            release = t - m["lead"][item]
            if release < 1:
                raise ValueError("Insufficient lead-time allowance")
            releases.append((release, item, quantity))
            stock += quantity
            for child in sorted(graph.successors(item)):
                gross[child][release] += quantity * graph[item][child]["weight"]
    return sorted(releases)


def verify_schedule(m, schedule):
    horizon = m["horizon"]
    keys = [(t, item) for t, item, _ in schedule]
    assert keys == sorted(set(keys))
    for t, item, q in schedule:
        assert item in m["item_names"]
        assert type(q) is int and q > 0
        assert 1 <= t <= t + m["lead"][item] <= horizon
    for item in m["item_names"]:
        balance = m["onhand"][item]
        for t in range(1, horizon + 1):
            incoming = sum(q for s, i, q in schedule
                           if i == item and s + m["lead"][item] == t)
            available = balance + sum(q for s, i, q in m["receipts"]
                                      if (s, i) == (t, item))
            demand = sum(q for s, i, q in m["demand"] if (s, i) == (t, item))
            demand += sum(q * usage for parent, child, usage in m["bom"]
                          if child == item for s, i, q in schedule
                          if (s, i) == (t, parent))
            shortage = max(0, demand - available)
            if shortage == 0:
                assert incoming == 0
            else:
                assert incoming >= shortage
                assert incoming % m["lot"][item] == 0
                assert incoming - shortage < m["lot"][item]
            balance = available + incoming - demand
            assert balance >= 0


def make_payload(m):
    item_rows = ["item | on-hand | lead time | lot rule"]
    for item in m["item_names"]:
        rule = "LFL" if m["lot"][item] == 1 else f"multiple of {m['lot'][item]}"
        item_rows.append(f"{item} | {m['onhand'][item]} | {m['lead'][item]} | {rule}")
    return {
        "item_records": "\n".join(item_rows),
        "bill_of_materials": "\n".join(
            f"{parent} -> {child}: {usage}" for parent, child, usage in m["bom"]),
        "independent_demand": format_schedule(m["demand"]),
        "scheduled_receipts": format_schedule(m["receipts"]),
    }


@dataclass
class MrpExplosionConfig(Config):
    layers: int = 3
    demand_periods: int = 2
    extra_edge_probability: float = 0.15

    def apply_difficulty(self, level):
        self.layers = 3 + int(level // 2)
        self.demand_periods = 2 + int(level // 2)
        self.extra_edge_probability = min(0.45, 0.15 + 0.05 * level)


class MrpGrossToNetExplosion(Task):
    summary = "Explode multi-level branching and shared-component bills of material: net independent and dependent gross requirements against on-hand and scheduled receipts, shift by lead time, apply lot-for-lot or lot-multiple rules; answers are complete planned-order release schedules ordered by period then item."
    design_choice = "Answer format: output the complete planned-order release schedule as a canonical string of (period, item, quantity) triples, ordered by period then item"
    config_cls = MrpExplosionConfig
    task_version = 3

    def generate_entry(self):
        c = self.config
        layers = c.layers
        n = layers + random.randint(1, 2)
        labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:n])
        random.shuffle(labels)
        depths = list(range(layers)) + [random.randrange(1, layers) for _ in range(n - layers)]
        edges = {(i, i + 1) for i in range(layers - 1)}
        for child in range(layers, n):
            parent = random.choice([i for i in range(n) if depths[i] < depths[child]])
            edges.add((parent, child))
        for parent in range(n):
            for child in range(n):
                if depths[parent] < depths[child] and random.random() < c.extra_edge_probability:
                    edges.add((parent, child))
        bom = sorted([labels[a], labels[b], random.randint(1, 3)] for a, b in sorted(edges))
        start = 2 * layers + 1
        horizon = start + c.demand_periods + 1
        items = sorted(labels)
        onhand = {i: random.randint(0, 8) for i in items}
        lead = {i: random.randint(1, 2) for i in items}
        lot = {i: random.choice([1, 1, random.randint(3, 9)]) for i in items}
        demand = [[t, labels[0], random.randint(10, 24)]
                  for t in sorted(random.sample(range(start, horizon + 1), c.demand_periods))]
        for i in items:
            if i != labels[0] and random.random() < 0.4:
                demand.append([random.randint(start, horizon), i, random.randint(2, 12)])
        receipts = [[random.randint(1, horizon), i, random.randint(1, 12)]
                    for i in items if random.random() < 0.65]
        if not receipts:
            receipts.append([random.randint(1, horizon), random.choice(items), random.randint(1, 12)])
        m = {"item_names": items, "bom": bom, "horizon": horizon, "onhand": onhand,
             "lead": lead, "lot": lot, "demand": sorted(demand), "receipts": sorted(receipts)}
        answer = format_schedule(solve_mrp(m))
        verify_schedule(m, parse_schedule(answer))
        m["payload"] = make_payload(m)
        return Entry(metadata=m, answer=answer)

    def render_prompt(self, metadata):
        return (
            f"A factory needs its complete MRP planned-order release schedule for periods 1 through {metadata['horizon']}. "
            "Use standard gross-to-net BOM explosion, processing parents before components.\n"
            "Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, "
            "in the parent's planned RELEASE period, not its receipt period. Sum requirements from all parents "
            "and add the listed independent demand.\n"
            "On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption. "
            "Carry surplus forward. For each item, work chronologically: net gross demand against carried stock plus "
            "scheduled receipts; if there is a shortage, plan a receipt in that period. LFL means exactly the shortage; "
            "multiple of k means round the shortage up to the next multiple of k. Otherwise plan nothing. "
            "A planned receipt in period t requires a release in period t minus that item's lead time.\n"
            "There is no safety stock, scrap, capacity limit, backlog, or other demand/receipt. "
            "Scheduled receipts are existing commitments: do not output their releases or explode them into component demand. "
            "All necessary new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).\n\n"
            + render_payload(metadata["payload"])
            + "\n\nReturn all positive planned releases for every item as (period,item,quantity) triples, "
            "ordered by increasing period then alphabetically by item, separated by semicolons with no spaces. "
            "Combine each period-item into one triple. Format example: (1,A,12);(1,C,6);(3,B,9). "
            "If there are no planned releases, return none."
        )

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip() == entry.answer)

import random
from dataclasses import dataclass

import networkx as nx

from reasoning_core.template import Config, Entry, Task, render_payload


TASK_META = {'parent_source_id': None,
 'idea': 'mrp_order_release_explosion (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_operations_research_r4/mrp_order_release_explosion',
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


def lot_quantity(need, rule, forward_gross):
    tag, arg = rule
    if tag == "LFL":
        return max(1, need)
    if tag == "MUL":
        k = arg
        return ((need + k - 1) // k) * k
    p = arg
    total = need
    for g in forward_gross[: p - 1]:
        if g > 0:
            total += g
    return max(1, total)


def solve_mrp(m):
    horizon = m["horizon"]
    graph = nx.DiGraph()
    graph.add_nodes_from(m["item_names"])
    graph.add_weighted_edges_from(m["bom"])
    gross = {item: [0] * (horizon + 2) for item in m["item_names"]}
    sched = {item: [0] * (horizon + 2) for item in m["item_names"]}
    for t, item, q in m["demand"]:
        gross[item][t] += q
    for t, item, q in m["receipts"]:
        sched[item][t] += q
    planned = []
    first_shortage = {}
    for item in nx.lexicographical_topological_sort(graph):
        stock = m["onhand"][item]
        first_shortage[item] = None
        forward = [gross[item][t] for t in range(1, horizon + 1)]
        for t in range(1, horizon + 1):
            stock += sched[item][t] - gross[item][t]
            if stock >= 0:
                continue
            need = -stock
            if first_shortage[item] is None:
                first_shortage[item] = t
            qty = lot_quantity(need, m["lot"][item], forward[t:t + m["poq"][item]])
            release = t - m["lead"][item]
            if release < 1:
                raise RuntimeError("lead time too tight")
            planned.append((release, item, qty))
            stock += qty
            for child in sorted(graph.successors(item)):
                gross[child][release] += qty * graph[item][child]["weight"]
    return sorted(planned), first_shortage


def verify_plan(m, planned, first_shortage):
    horizon = m["horizon"]
    graph = nx.DiGraph()
    graph.add_nodes_from(m["item_names"])
    graph.add_weighted_edges_from(m["bom"])
    gross = {item: [0] * (horizon + 2) for item in m["item_names"]}
    sched = {item: [0] * (horizon + 2) for item in m["item_names"]}
    for t, item, q in m["demand"]:
        gross[item][t] += q
    for t, item, q in m["receipts"]:
        sched[item][t] += q
    for release, item, q in planned:
        assert item in m["item_names"]
        assert type(q) is int and q > 0
        assert 1 <= release + m["lead"][item] <= horizon
    incoming = {item: [0] * (horizon + 2) for item in m["item_names"]}
    for release, item, q in planned:
        incoming[item][release + m["lead"][item]] += q
        for child, usage in graph[item].items():
            gross[child][release] += q * usage["weight"]
    mismatch = None
    for item in nx.lexicographical_topological_sort(graph):
        stock = m["onhand"][item]
        first = None
        for t in range(1, horizon + 1):
            stock += sched[item][t] - gross[item][t]
            if stock < 0:
                if first is None:
                    first = t
                assert incoming[item][t] > 0
                stock += incoming[item][t]
                assert stock >= 0
            else:
                assert incoming[item][t] == 0
        expected = first_shortage[item]
        if (first is None) != (expected is None) or (first != expected):
            mismatch = (item, first, expected)
            break
    assert mismatch is None, f"shortage mismatch {mismatch}"


def format_schedule(schedule):
    return ";".join(f"({t},{item},{q})" for t, item, q in schedule) or "none"


def make_payload(m):
    item_rows = ["item | on-hand | lead time | lot rule"]
    for item in m["item_names"]:
        tag, arg = m["lot"][item]
        if tag == "LFL":
            rule = "LFL"
        elif tag == "MUL":
            rule = f"fixed multiple of {arg}"
        else:
            rule = f"period quantity covering {arg} periods"
        item_rows.append(f"{item} | {m['onhand'][item]} | {m['lead'][item]} | {rule}")
    return {
        "item_records": "\n".join(item_rows),
        "bill_of_materials": "\n".join(
            f"{parent} -> {child}: {usage}" for parent, child, usage in m["bom"]),
        "independent_demand": format_schedule(m["demand"]),
        "scheduled_receipts": format_schedule(m["receipts"]),
    }


@dataclass
class MrpReleaseConfig(Config):
    layers: int = 2
    demand_periods: int = 2

    def apply_difficulty(self, level):
        self.layers = 2 + int(level // 2)
        self.demand_periods = 2 + int(level // 2)


class MrpOrderReleaseExplosion(Task):
    summary = "Count lead-time-offset multilevel BOM explosion: net independent and dependent gross demand against on-hand and scheduled receipts using lot-for-lot, fixed-multiple, or period-quantity rules; answers are the first shortage period (the earliest period any planned-order receipt is required)."
    design_choice = "Answer format: a single integer for the first shortage period, versus a compact list of planned order release quantities per period per level"
    config_cls = MrpReleaseConfig
    task_version = 2

    def generate_entry(self):
        c = self.config
        for _attempt in range(400):
            layers = c.layers
            n = layers + random.randint(1, 2)
            labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:n])
            random.shuffle(labels)
            depths = list(range(layers)) + [random.randrange(1, layers) for _ in range(n - layers)]
            edges = {(i, i + 1) for i in range(layers - 1)}
            for child in range(layers, n):
                parent = random.choice([i for i in range(n) if depths[i] < depths[child]])
                edges.add((parent, child))
            bom = sorted([labels[a], labels[b], random.randint(1, 3)] for a, b in sorted(edges))
            start = 2 * layers + 1
            horizon = start + c.demand_periods + 2
            items = sorted(labels)
            onhand = {i: random.randint(0, 18) for i in items}
            lead = {i: random.randint(1, 2) for i in items}
            lot = {}
            poq = {}
            for i in items:
                choice = random.random()
                if choice < 0.34:
                    lot[i] = ("LFL", 1)
                elif choice < 0.67:
                    lot[i] = ("MUL", random.randint(3, 9))
                else:
                    lot[i] = ("POQ", random.randint(2, 3))
                poq[i] = 1 if lot[i][0] != "POQ" else lot[i][1]
            demand = []
            for t in sorted(random.sample(range(start, horizon + 1), c.demand_periods)):
                demand.append([t, labels[0], random.randint(4, 14)])
            for i in items:
                if i != labels[0] and random.random() < 0.4:
                    demand.append([random.randint(start, horizon), i, random.randint(2, 10)])
            receipts = [[random.randint(start - 1, horizon), i, random.randint(1, 8)]
                        for i in items if random.random() < 0.55]
            if not receipts:
                receipts.append([random.randint(start - 1, horizon), random.choice(items), random.randint(1, 8)])
            m = {"item_names": items, "bom": bom, "horizon": horizon, "onhand": onhand,
                 "lead": lead, "lot": lot, "poq": poq,
                 "demand": sorted(demand), "receipts": sorted(receipts)}
            try:
                planned, first_shortage = solve_mrp(m)
            except RuntimeError:
                continue
            if not planned:
                continue
            shortages = [t for t in first_shortage.values() if t is not None]
            if not shortages:
                continue
            answer = min(shortages)
            assert 1 <= answer <= horizon
            verify_plan(m, planned, first_shortage)
            assert min(r + m["lead"][item] for r, item, q in planned) == answer
            m["payload"] = make_payload(m)
            return Entry(metadata=m, answer=str(answer))
        raise RuntimeError("failed to build a valid MRP instance")

    def render_prompt(self, metadata):
        return (
            f"A factory runs its MRP over periods 1 through {metadata['horizon']}. "
            "Explode the bill of materials gross-to-net, processing each parent item before the components it uses. "
            "Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, "
            "in the parent's planned RELEASE period, not its receipt period. Sum component need from all parents "
            "and add the listed independent demand.\n"
            "On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption "
            "and are existing commitments (do not output their releases or explode them). Carry surplus forward. "
            "For each item work chronologically: net gross demand against carried stock plus scheduled receipts; "
            "when a net requirement exceeds zero in a period you must schedule a planned-order receipt in that period. "
            "Lot rules set only the ORDER size: LFL orders exactly the net requirement; a fixed multiple of k rounds "
            "the order up to the next multiple of k; a period quantity covering P periods orders the net requirement "
            "plus the gross requirements of the following P-1 periods. A planned receipt in period t needs a release "
            "in period t minus that item's lead time. There is no safety stock, scrap, backlog, or capacity limit.\n"
            "All new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).\n\n"
            + render_payload(metadata["payload"])
            + "\n\nState the FIRST SHORTAGE PERIOD: the smallest period number between 1 and the horizon at which "
            "any item's net requirement exceeds zero, that is, the earliest period at which any planned-order receipt "
            "must be scheduled. Answer is exactly that single integer."
        )

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip() == entry.answer)

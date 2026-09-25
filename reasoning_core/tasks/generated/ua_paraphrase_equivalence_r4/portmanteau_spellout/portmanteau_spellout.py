"""Portmanteau spell-out: realize featural words under precedence, blocking and allomorphs."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

P_VALUES = ["I", "II", "III"]
N_VALUES = ["Sg", "Pl"]
G_VALUES = ["M", "F"]

SINGLE_POOL = ["o", "e", "i", "a", "u", "oy", "ei", "au", "io", "ue"]
PORT_POOL = ["mos", "tis", "ram", "non", "sel", "kun", "vor", "dil"]
TRIPLE_POOL = ["mixto", "kador", "lunra", "serpo", "valdo"]

_CTX_SUFFIX = {"M": "x", "F": "w", "Sg": "a", "Pl": "u", "I": "1", "II": "2", "III": "3"}


def _pair_names(n):
    if n == 2:
        return ["pair12"]
    return ["pair12", "pair23", "triple123"]


def _ctx_neighbor(table, pos, neighbor_val):
    return table["ctx"][str(pos)][str(neighbor_val)]


def _spellout(table):
    """Greedy spell-out. Deterministic given the structured table."""
    n = table["n"]
    vals = table["vals"]  # list of values, index 0 = pos1
    precedence = list(table["precedence"])
    blocked = set(table["blocked"])  # string boundaries like "12", "23"
    pairs = table["pairs"]  # "12"/"23" -> {(v1,v2): token} using string keys
    triple = table["triple"]  # for n==3: {(v1,v2,v3): token} or None
    ctx = table["ctx_positions"]  # list of positions that are contextual

    covered = [False] * n
    taken = []  # (start_pos, end_pos, token) 1-indexed

    def pair_token(boundary, i, j):
        if boundary in blocked:
            return None
        entry = pairs.get(boundary)
        if not entry:
            return None
        key = vals[i] + "|" + vals[j]
        return entry.get(key)

    for mname in precedence:
        if mname == "pair12":
            tok = pair_token("12", 0, 1)
            if tok and not covered[0] and not covered[1]:
                covered[0] = covered[1] = True
                taken.append((1, 2, tok))
        elif mname == "pair23":
            tok = pair_token("23", 1, 2)
            if tok and not covered[1] and not covered[2]:
                covered[1] = covered[2] = True
                taken.append((2, 3, tok))
        else:  # triple123
            if n == 3 and "12" not in blocked and "23" not in blocked and triple:
                key = vals[0] + "|" + vals[1] + "|" + vals[2]
                tok = triple.get(key)
                if tok and not covered[0] and not covered[1] and not covered[2]:
                    covered[0] = covered[1] = covered[2] = True
                    taken.append((1, 3, tok))

    tok_by_start = {s: (e, t) for s, e, t in taken}

    def single_spell(i):
        pos = i
        val = vals[i - 1]
        if pos in ctx:
            if pos < n:
                neigh = vals[i]
            else:
                neigh = vals[i - 2]
            return _ctx_neighbor(table, pos, neigh)
        return table["single"][str(pos)][val]

    parts = []
    i = 1
    while i <= n:
        if i in tok_by_start:
            e, t = tok_by_start[i]
            parts.append(t)
            i = e + 1
        else:
            parts.append(single_spell(i))
            i += 1
    return "".join(parts)


def _build_table(n, context_prob, block_prob):
    vals = [random.choice(P_VALUES), random.choice(N_VALUES)]
    if n == 3:
        vals.append(random.choice(G_VALUES))
    vals = list(vals)

    posval = {1: P_VALUES, 2: N_VALUES, 3: G_VALUES}
    single = {}
    for p in range(1, n + 1):
        single[str(p)] = {v: random.choice(SINGLE_POOL) for v in posval[p]}

    ctx_positions = [p for p in range(1, n + 1) if random.random() < context_prob]
    ctx = {}
    for p in ctx_positions:
        ctx[str(p)] = {}
        if p < n:
            for nv in posval[p + 1]:
                ctx[str(p)][str(nv)] = random.choice(SINGLE_POOL) + _CTX_SUFFIX.get(
                    random.choice(P_VALUES + N_VALUES + G_VALUES), ""
                )
        else:
            for nv in posval[p - 1]:
                ctx[str(p)][str(nv)] = random.choice(SINGLE_POOL) + _CTX_SUFFIX.get(
                    random.choice(P_VALUES + N_VALUES + G_VALUES), ""
                )

    blocked = set()
    boundaries = ["12"] if n == 2 else ["12", "23"]
    for b in boundaries:
        if random.random() < block_prob:
            blocked.add(b)

    pairs = {}
    for b in boundaries:
        pairs[b] = {}
    if "12" in boundaries:
        for v1 in P_VALUES:
            for v2 in N_VALUES:
                if random.random() < 0.6:
                    pairs["12"][v1 + "|" + v2] = random.choice(PORT_POOL)
    if n == 3:
        for v2 in N_VALUES:
            for v3 in G_VALUES:
                if random.random() < 0.6:
                    pairs["23"][v2 + "|" + v3] = random.choice(PORT_POOL)

    triple = None
    if n == 3:
        triple = {}
        for v1 in P_VALUES:
            for v2 in N_VALUES:
                for v3 in G_VALUES:
                    if random.random() < 0.5:
                        triple[v1 + "|" + v2 + "|" + v3] = random.choice(TRIPLE_POOL)

    precedence = list(_pair_names(n))
    if n == 3:
        random.shuffle(precedence)

    block_list = sorted(blocked)
    return {
        "n": n,
        "vals": list(vals),
        "single": single,
        "ctx_positions": list(ctx_positions),
        "ctx": ctx,
        "blocked": block_list,
        "pairs": pairs,
        "triple": triple,
        "precedence": precedence,
    }


@dataclass
class PortmanteauConfig(Config):
    n3_prob: float = 0.0
    context_prob: float = 0.15
    block_prob: float = 0.0

    def apply_difficulty(self, level):
        self.n3_prob = 0.0 if level < 2 else min((level - 1) / 4.0, 1.0)
        self.context_prob = min(0.15 + 0.12 * level, 0.6)
        self.block_prob = min(0.12 * level, 0.5)


class PortmanteauSpellout(Task):
    summary = (
        "Realize adjacent grammatical features using competing single-feature and portmanteau "
        "exponents under supplied precedence rules; vary blocking boundaries and contextual "
        "allomorphs; answers give the surface word."
    )
    design_choice = (
        "Vary the number of adjacent features per word (2 vs 3) and supply precedence rules as "
        "a total order, so solvers must decide whether a portmanteau covering two features "
        "blocks a third feature's exponent."
    )
    task_version = 2
    config_cls = PortmanteauConfig

    def generate_entry(self):
        n = 2 if random.random() >= self.config.n3_prob else 3
        table = _build_table(n, self.config.context_prob, self.config.block_prob)
        surface = _spellout(table)
        assert isinstance(surface, str) and surface, "surface must be a non-empty string"
        assert _spellout(table) == surface, "spell-out must be deterministic"
        return Entry(metadata={"table": table}, answer=surface)

    def render_prompt(self, metadata):
        t = metadata["table"]
        n = t["n"]
        posname = {1: "P", 2: "N", 3: "G"}
        lines = []
        lines.append(
            "A featural word is realized as a surface string by choosing exponents for its adjacent "
            "features. Spell the word out with the greedy algorithm described below and give the "
            "surface word."
        )
        lines.append("")
        lines.append(f"The word has {n} adjacent features in this fixed order: " + ", ".join(
            f"P{posname[i]}={t['vals'][i-1]}" for i in range(1, n + 1)
        ) + ".")
        lines.append("")
        # single exponents
        singles = []
        for i in range(1, n + 1):
            if i in t["ctx_positions"]:
                singles.append(f"P{i} is CONTEXTUAL")
            else:
                singles.append(f"P{i} spells '{t['single'][str(i)][t['vals'][i-1]]}'")
        lines.append("Single-feature exponents (used only when the feature is not merged into a "
                     "portmanteau): " + "; ".join(singles) + ".")
        # contextual variants
        ctx_lines = []
        for i in t["ctx_positions"]:
            if i < n:
                ctx_lines.append(
                    f"P{i} spells its contextual allomorph by the NEXT feature's value: "
                    + ", ".join(f"'{v}'->'{w}'" for v, w in sorted(t["ctx"][str(i)].items()))
                )
            else:
                ctx_lines.append(
                    f"P{i} spells its contextual allomorph by the PREVIOUS feature's value: "
                    + ", ".join(f"'{v}'->'{w}'" for v, w in sorted(t["ctx"][str(i)].items()))
                )
        for c in ctx_lines:
            lines.append(c)
        lines.append("")
        # portmanteau
        for b, entry in sorted(t["pairs"].items()):
            if not entry:
                continue
            i, j = int(b[0]), int(b[1])
            shown = ", ".join(
                f"[{k.split('|')[0]}, {k.split('|')[1]}]->'{v}'" for k, v in sorted(entry.items())
            )
            lines.append(f"A portmanteau may merge features P{i} and P{j} for the listed value pairs: {shown}.")
        if t["triple"]:
            shown = ", ".join(
                f"[{k.split('|')[0]}, {k.split('|')[1]}, {k.split('|')[2]}]->'{v}'"
                for k, v in sorted(t["triple"].items())
            )
            lines.append(f"A portmanteau may merge all three features for the listed value triples: {shown}.")
        if t["blocked"]:
            bmap = {"12": "between P1 and P2", "23": "between P2 and P3"}
            lines.append("Blocking boundaries: " + "; ".join(bmap[b] for b in t["blocked"])
                         + " are blocked, so no portmanteau may cross them.")
        else:
            lines.append("There are no blocking boundaries.")
        lines.append("")
        lines.append(
            "Greedy spell-out: process the merge candidates in the precedence order "
            + ", ".join(t["precedence"])
            + ". A merge is usable if it crosses no blocking boundary and its value pair/triple "
            "has a portmanteau entry, and if none of its positions is already covered by a taken "
            "merge; take it, then take remaining merges in order. Finally realize every still-"
            "uncovered feature singly (with its contextual allomorph if flagged)."
        )
        lines.append("")
        lines.append("Give the surface word only.")
        return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'portmanteau_spellout (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_paraphrase_equivalence_r4/portmanteau_spellout',
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

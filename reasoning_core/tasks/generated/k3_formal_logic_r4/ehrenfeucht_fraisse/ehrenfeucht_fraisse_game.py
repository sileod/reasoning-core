"""Determine the winner of the k-round Ehrenfeucht-Fraisse game on two small
undirected graphs, and (when Spoiler wins) Spoiler's canonical winning first move:

the lexicographically smallest vertex pair (a-name, b-name) such that opening on
that pair guarantees Spoiler a win.  Generation balances both outcomes by drawing
random same-size graph pairs for Spoiler instances and identical isomorphic copies
for Duplicator instances; vertex names are randomized per instance so the canonical
first move is not readable off the surface of the prompt.

The game is solved exactly by recursive back-and-forth over a partial injective
map (Spoiler picks a fresh or matched element; any response that breaks injectivity
immediately hands Spoiler a win, so only bijective continuations matter).
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'ehrenfeucht_fraisse_game (variant 2 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_logic_r4/ehrenfeucht_fraisse_game',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2701974858,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

A_LETTERS = ('a', 'b', 'c', 'd', 'e')
B_LETTERS = ('p', 'q', 'r', 's', 't')


def _rand_graph(n):
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.5:
                adj[i].add(j)
                adj[j].add(i)
    return {i: frozenset(adj[i]) for i in range(n)}


def _partial_iso(pmap, ea, eb):
    plist = sorted(pmap)
    for i in range(len(plist)):
        for j in range(i + 1, len(plist)):
            a1, b1 = plist[i]
            a2, b2 = plist[j]
            if (a2 in ea[a1]) != (b2 in eb[b1]):
                return False
    return True


def _spoiler_wins(pmap, r, ea, eb, na, nb, memo):
    key = (r, pmap)
    if key in memo:
        return memo[key]
    if r == 0:
        res = not _partial_iso(pmap, ea, eb)
        memo[key] = res
        return res
    used_a = frozenset(a for a, _ in pmap)
    used_b = frozenset(b for _, b in pmap)
    forward = {a: b for a, b in pmap}
    backward = {b: a for a, b in pmap}
    for a in range(na):
        if a in forward:
            if _spoiler_wins(pmap, r - 1, ea, eb, na, nb, memo):
                memo[key] = True
                return True
            continue
        win = True
        for b in range(nb):
            if b in used_b:
                continue
            if not _spoiler_wins(pmap | frozenset({(a, b)}), r - 1,
                                 ea, eb, na, nb, memo):
                win = False
                break
        if win:
            memo[key] = True
            return True
    for b in range(nb):
        if b in backward:
            if _spoiler_wins(pmap, r - 1, ea, eb, na, nb, memo):
                memo[key] = True
                return True
            continue
        win = True
        for a in range(na):
            if a in used_a:
                continue
            if not _spoiler_wins(pmap | frozenset({(a, b)}), r - 1,
                                 ea, eb, na, nb, memo):
                win = False
                break
        if win:
            memo[key] = True
            return True
    memo[key] = False
    return False


def _winning_sets(ea, eb, na, nb, rounds):
    wfa = []
    for a in range(na):
        if all(_spoiler_wins(frozenset({(a, b)}), rounds - 1, ea, eb, na, nb, {})
               for b in range(nb)):
            wfa.append(a)
    wfb = []
    for b in range(nb):
        if all(_spoiler_wins(frozenset({(a, b)}), rounds - 1, ea, eb, na, nb, {})
               for a in range(na)):
            wfb.append(b)
    return wfa, wfb


def _canonical(wfa, wfb, na, nb, aname, bname):
    best = None
    for i in wfa:
        for j in range(nb):
            pair = (aname[i], bname[j])
            if best is None or pair < best:
                best = pair
    for i in range(na):
        for j in wfb:
            pair = (aname[i], bname[j])
            if best is None or pair < best:
                best = pair
    return best


def _edges(adj, names):
    out = []
    for i in range(len(names)):
        for j in adj[i]:
            if i < j:
                out.append(f"{names[i]}-{names[j]}")
    return ", ".join(sorted(out)) if out else "none"


@dataclass
class EHFraisseConfig(Config):
    size: int = 2
    rounds: int = 2

    def apply_difficulty(self, level):
        self.size = 2 + int(0.5 * level)
        self.rounds = 2 + int(0.5 * level)


class EhrenfeuchtFraisseV2(Task):
    task_name = "ehrenfeucht_fraisse"
    summary = ("Determine the winner of the k-round Ehrenfeucht-Fraisse game on two "
               "small undirected graphs by recursive back-and-forth over vertex "
               "choices; for Spoiler wins give the lexicographically smallest "
               "winning first-move pair.")
    design_choice = ("Answer the winning player and a canonical winning first move, "
                     "where spoiler's first move is the lexicographically smallest "
                     "element pair that guarantees a win.")
    config_cls = EHFraisseConfig
    task_version = 2

    def generate_entry(self):
        size = self.config.size
        rounds = self.config.rounds
        aname = random.sample(A_LETTERS, size)
        bname = random.sample(B_LETTERS, size)
        if random.random() < 0.35:
            g = _rand_graph(size)
            ea = {i: g[i] for i in range(size)}
            eb = {i: g[i] for i in range(size)}
        else:
            for _ in range(300):
                g1 = _rand_graph(size)
                g2 = _rand_graph(size)
                if _spoiler_wins(frozenset(), rounds, g1, g2, size, size, {}):
                    ea, eb = g1, g2
                    break
            else:
                ea = {i: frozenset() for i in range(size)}
                eb = {i: frozenset(j for j in range(size) if j != i)
                      for i in range(size)}
        spoiler = _spoiler_wins(frozenset(), rounds, ea, eb, size, size, {})
        if spoiler:
            wfa, wfb = _winning_sets(ea, eb, size, size, rounds)
            canonical = _canonical(wfa, wfb, size, size, aname, bname)
            assert canonical is not None
            aa, bb = canonical
            answer = f"Spoiler; {aa},{bb}"
            winner = "Spoiler"
        else:
            answer = "Duplicator"
            winner = "Duplicator"
            canonical = None
        metadata = {
            "rounds": int(rounds),
            "a": list(aname),
            "b": list(bname),
            "a_edges": _edges(ea, aname),
            "b_edges": _edges(eb, bname),
            "winner": winner,
            "canonical": list(map(str, canonical)) if canonical else None,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return (
            f"Two players play the {metadata['rounds']}-round Ehrenfeucht-Fraisse game "
            f"on two undirected graphs A and B. In each round Spoiler picks a vertex in "
            f"either graph, then Duplicator picks a vertex in the other graph. After all "
            f"rounds, if the chosen vertices of A and B form an isomorphism of the induced "
            f"subgraphs, Duplicator wins; otherwise Spoiler wins.\n"
            f"Graph A has vertices {{{', '.join(metadata['a'])}}} and edges "
            f"{metadata['a_edges']}.\n"
            f"Graph B has vertices {{{', '.join(metadata['b'])}}} and edges "
            f"{metadata['b_edges']}.\n"
            f"Who wins the {metadata['rounds']}-round game? If Duplicator wins, answer "
            f"exactly 'Duplicator'. If Spoiler wins, answer 'Spoiler; <a>,<b>' where "
            f"<a>,<b> is the lexicographically smallest pair (A-vertex, B-vertex, "
            f"compared by these vertex names) such that Spoiler can guarantee a win by "
            f"opening on that pair."
        )

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == str(entry.answer).strip() else 0.0

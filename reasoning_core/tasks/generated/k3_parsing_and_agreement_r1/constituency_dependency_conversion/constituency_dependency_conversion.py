import random
from dataclasses import dataclass

from reasoning_core.template import Entry, Config, Task, edict, stochastic_rounding as sround

PRETERMINAL = {"Det", "N", "V", "P", "Adj"}

WORD_POOLS = {
    "Det": ["the", "a", "an", "some", "every", "each", "this", "that", "these",
            "those", "no", "any", "all", "both", "many", "few"],
    "N": ["cat", "dog", "bird", "tree", "house", "river", "mountain", "child",
          "teacher", "book", "garden", "window", "tiger", "forest", "engineer",
          "doctor", "ship", "castle", "stone", "lamp", "island", "valley",
          "bridge", "village", "market", "temple", "cart", "cabin", "field",
          "meadow", "brook", "cliff", "shore", "crag", "howl", "ledge",
          "tor", "lode", "mere", "hollow", "bog", "frith"],
    "Adj": ["big", "small", "red", "blue", "old", "young", "happy", "sad",
            "tall", "short", "bright", "dim", "rapid", "slow", "mighty", "faint",
            "sweet", "sour", "keen", "dull", "stout", "lank", "grim", "meek",
            "vast", "bare", "deep", "ham", "wild", "soft", "harsh", "warm",
            "cool", "fair", "dark", "fresh", "still", "swift", "clear"],
    "V": ["chased", "sees", "built", "painted", "carried", "found", "opened",
          "closed", "held", "sang", "wrote", "read", "bought", "caught",
          "brought", "took", "gave", "made", "kept", "drew", "hired",
          "tended", "lifted", "trimmed", "mended"],
    "P": ["in", "on", "at", "of", "by", "with", "from", "for", "about",
          "under", "after", "before", "near", "beside", "across", "above"],
}

RULES_TEXT = (
    "S:NP subj; VP:NP obj, VP:PP arg; NP:Det det, NP:Adj mod, NP:PP mod; PP:NP comp"
)


@dataclass
class ConstituencyDependencyConversionConfig(Config):
    max_np_mods: int = 1
    max_vp_args: int = 1
    pp_prob: float = 0.15

    def apply_difficulty(self, level):
        self.max_np_mods = sround(1 + 0.5 * level)
        self.max_vp_args = sround(1 + 0.5 * level)
        self.pp_prob = min(0.6, 0.15 + 0.06 * level)


def _head_pos(label, child_labels):
    if label == "S":
        return 1
    if label == "VP":
        return 0
    if label == "NP":
        for i, cl in enumerate(child_labels):
            if cl == "N":
                return i
        return -1
    if label == "PP":
        return 0
    return -1


def _func(parent_label, child_label):
    if parent_label == "S":
        return "subj"
    if parent_label == "VP":
        if child_label == "NP":
            return "obj"
        if child_label == "PP":
            return "arg"
        return "adv"
    if parent_label == "NP":
        if child_label == "Det":
            return "det"
        return "mod"
    if parent_label == "PP":
        return "comp"
    return "mod"


def _head_token(node):
    label, payload = node
    if label in PRETERMINAL:
        return payload
    hi = _head_pos(label, [c[0] for c in payload])
    return _head_token(payload[hi])


def _arcs(node):
    label, payload = node
    if label in PRETERMINAL:
        return []
    child_labels = [c[0] for c in payload]
    hi = _head_pos(label, child_labels)
    head = _head_token(node)
    res = []
    for i, child in enumerate(payload):
        if i == hi:
            res.extend(_arcs(child))
        else:
            dep = _head_token(child)
            res.append((head, dep, _func(label, child_labels[i])))
            res.extend(_arcs(child))
    return res


def _tree_string(node):
    label, payload = node
    if label in PRETERMINAL:
        return f"({label} {payload})"
    inner = " ".join(_tree_string(c) for c in payload)
    return f"({label} {inner})"


def _gen_np(amods):
    children = [["Det", None]]
    for _ in range(amods):
        children.append(["Adj", None])
    children.append(["N", None])
    return ["NP", children]


def _gen_tree(level, cfg):
    subj_mods = random.randrange(0, min(cfg.max_np_mods, 1 + level // 2) + 1)
    subj_children = [["Det", None]]
    for _ in range(subj_mods):
        subj_children.append(["Adj", None])
    subj_children.append(["N", None])
    subj = ["NP", subj_children]
    vp_children = [["V", None]]
    n_args = random.randrange(1, min(cfg.max_vp_args, 1 + level // 2) + 1)
    allow_pp = random.random() < cfg.pp_prob
    for _ in range(n_args):
        if allow_pp and random.random() < 0.4:
            pobj = ["NP", [["Det", None], ["N", None]]]
            vp_children.append(["PP", [["P", None], pobj]])
        else:
            amods = random.randrange(0, min(2, cfg.max_np_mods) + 1)
            vp_children.append(_gen_np(amods))
    vp = ["VP", vp_children]
    return ["S", [subj, vp]]


def _fill_words(node, used):
    label, payload = node
    if label in PRETERMINAL:
        pool = [w for w in WORD_POOLS[label] if w not in used]
        if not pool:
            return None
        word = random.choice(pool)
        used.add(word)
        node[1] = word
        return [word]
    tokens = []
    for child in payload:
        stop = _fill_words(child, used)
        if stop is None:
            return None
        tokens.extend(stop)
    return tokens


class ConstituencyDependencyConversion(Task):
    summary = ("Convert constituency trees into bilexical dependencies: percolate lexical "
               "heads with a head-rule table, label arcs by grammatical function; answers "
               "are the full arc set or the governor and dependents of a queried token.")
    config_cls = ConstituencyDependencyConversionConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(120):
            tree = _gen_tree(cfg.level, cfg)
            used = set()
            words = _fill_words(tree, used)
            if words is None or len(words) < 4 or len(set(words)) != len(words):
                continue
            arcs = sorted(_arcs(tree))
            mode = "A" if random.random() < 0.5 else "B"
            if mode == "A":
                parts = [f"{g} -> {d} : {f}" for g, d, f in arcs]
                answer = " ; ".join(parts)
                query = None
            else:
                deps_map = {}
                gov_map = {}
                for g, d, f in arcs:
                    deps_map.setdefault(g, []).append((d, f))
                    gov_map[d] = g
                root_token = _head_token(tree)
                interesting = [w for w in words if w in deps_map or w == root_token]
                query = random.choice(interesting if interesting else words)
                deps = sorted(deps_map.get(query, []))
                gov = gov_map.get(query, "ROOT")
                dep_str = ", ".join(f"{d}:{f}" for d, f in deps) if deps else "NONE"
                answer = f"GOV={gov} ; DEPS={dep_str}"
            metadata = edict({
                "tree_string": _tree_string(tree),
                "mode": mode,
                "answer": answer,
                "query": query,
                "arcs": arcs,
                "tokens": sorted(words),
            })
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("Failed to generate constituency instance")

    def render_prompt(self, metadata):
        tree = metadata["tree_string"]
        head_rules = (
            "Head-percolation rules:\n"
            "- The head of S is its VP child.\n"
            "- The head of VP is its V child.\n"
            "- The head of NP is its N child.\n"
            "- The head of PP is its P child.\n"
            "- A preterminal's head is its word.\n"
            "For every non-head child, draw an arc from the parent's head word to that "
            "child's head word, labeled by grammatical function: S's NP child is 'subj'; "
            "VP's NP child is 'obj' and VP's PP child is 'arg'; NP's Det and Adj children "
            "are 'det' and 'mod', and NP's PP child is 'mod'; PP's NP child is 'comp'.\n"
        )
        if metadata["mode"] == "A":
            return (
                f"Constituency parse tree:\n{tree}\n\n{head_rules}"
                "List every labeled dependency arc. Answer format: each arc as 'governor -> "
                "dependent : label', arcs sorted by governor, then dependent, then label, "
                "joined with ' ; '."
            )
        q = metadata["query"]
        return (
            f"Constituency parse tree:\n{tree}\n\n{head_rules}"
            f"Consider the word '{q}' in the dependency tree. What is its governor and its "
            "dependents with their labels? The root token has governor ROOT. Answer format: "
            "'GOV=<governor or ROOT> ; DEPS=<word:label, ...>' with dependents sorted by "
            "word then label, or 'NONE' if it has none."
        )

    def score_answer(self, answer, entry):
        norm = lambda x: " ".join(str(x).split())
        return float(norm(answer) == norm(entry.answer))


TASK_META = {'parent_source_id': None,
 'idea': 'constituency_dependency_conversion (draw 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_parsing_and_agreement_r1/constituency_dependency_conversion',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1618848011,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'parsimony_ancestral_state_inference (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_latent_structure_reconstruction_r4/parsimony_ancestral_state_inference',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Generate trees with a fixed number of tips (e.g., 8) but vary depth and branching symmetry to control ambiguity frequency, with tip labels drawn from a small alphabet (2-4 states)."


@dataclass
class ParsimonyConfig(Config):
    n_states: int = 2
    n_tips: int = 8

    def apply_difficulty(self, level):
        self.n_states = 2 if level < 1 else (3 if level < 4 else 4)
        self.n_tips = 8


def _intersection(sets):
    if not sets:
        return set()
    result = set(sets[0])
    for s in sets[1:]:
        result &= s
    return result


def _fitch_upward(root, children, tip_to_label):
    """Fitch parsimony: return (node->state_set, min_number_of_changes).

    Sets are the most-parsimonious ancestral state sets. The score is the total
    number of empty intersections over internal nodes (minimum changes).
    """
    sets = {}
    cost = 0
    order = []
    stack = [root]
    while stack:
        v = stack.pop()
        order.append(v)
        stack.extend(children[v])
    for v in reversed(order):
        if not children[v]:
            sets[v] = {tip_to_label[v]}
        else:
            child_sets = [sets[w] for w in children[v]]
            inter = _intersection(child_sets)
            if inter:
                sets[v] = inter
            else:
                union = set()
                for s in child_sets:
                    union |= s
                sets[v] = union
                cost += 1
    return sets, cost


def _valid_root_states(root_sets):
    return sorted(root_sets)


def _one_optimal_root(root_sets):
    return min(root_sets)


def _letter(state):
    return chr(ord("A") + int(state))


class ParsimonyAncestralStateInference(Task):
    summary = ("Infer ancestral states on a rooted tree with labeled tips: an upward "
               "intersection/union pass then a downward pass fixing ambiguities; answer "
               "the minimal change count, valid root states, or one optimal labeling.")
    config_cls = ParsimonyConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n_states = cfg.n_states
        n_tips = cfg.n_tips

        while True:
            tip_labels = [random.randrange(n_states) for _ in range(n_tips)]
            if len(set(tip_labels)) < min(2, n_states):
                continue
            tip_to_label = {t: tip_labels[t] for t in range(n_tips)}

            children = {}
            tips = list(range(n_tips))
            next_label = n_tips
            while len(tips) > 1:
                p1 = random.choice(tips)
                tips.remove(p1)
                p2 = random.choice(tips)
                tips.remove(p2)
                children[next_label] = [p1, p2]
                tips.append(next_label)
                next_label += 1
            root = tips[0]

            names = list(range(root + 1))
            for v in names:
                if v not in children:
                    children[v] = []

            sets, cost = _fitch_upward(root, children, tip_to_label)
            root_states = _valid_root_states(sets[root])
            one_root = _one_optimal_root(sets[root])

            if not root_states:
                continue
            if cost < 0:
                continue
            break

        mode = random.randrange(3)
        if mode == 0:
            answer = str(cost)
        elif mode == 1:
            answer = ",".join(_letter(s) for s in root_states)
        else:
            answer = _letter(one_root)

        metadata = {
            "n_tips": n_tips,
            "n_states": n_states,
            "tip_labels": tip_labels,
            "children": {str(k): [c for c in v] for k, v in children.items()},
            "root": root,
            "mode": mode,
        }

        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        children = {int(k): v for k, v in metadata["children"].items()}
        root = metadata["root"]
        tip_labels = metadata["tip_labels"]
        n_tips = metadata["n_tips"]
        n_states = metadata["n_states"]
        mode = metadata["mode"]

        def desc(v):
            if v < n_tips:
                return f"tip{v}={_letter(tip_labels[v])}"
            ch = children[v]
            if len(ch) == 1:
                return f"node{v}->{desc(ch[0])}"
            return f"node{v}->({desc(ch[0])}, {desc(ch[1])})"

        tree = desc(root)
        last_state = _letter(n_states - 1)
        alphabet = "{" + _letter(0) + ".." + last_state + "}"
        if mode == 0:
            q = ("Here is a rooted tree whose tips carry one state each from the set "
                 + alphabet + "; every internal node also gets one state. The "
                 "parsimony score is the number of branches whose two endpoint states differ. "
                 "Find the minimum parsimony score over all ways to label the internal nodes. "
                 "Answer with a single positive integer.")
        elif mode == 1:
            q = ("Tip states are drawn from " + alphabet + ". A root state is "
                 "'valid' if it can be assigned to the root in some optimal (minimum-change) "
                 "labeling. List every valid root state in ascending order, separated by commas "
                 "with no spaces.")
        else:
            q = ("Different optimal (minimum-change) labelings may assign different states to "
                 "the root of this tree. Give one state that can validly be placed at the root "
                 "in some optimal labeling. Answer with a single letter.")

        return f"{q}\nTree: {tree}"

    def score_answer(self, answer, entry):
        mode = entry.metadata["mode"]
        val = str(answer).strip().upper()
        if mode == 0:
            try:
                return 1.0 if int(val) == int(entry.answer) else 0.0
            except ValueError:
                return 0.0
        return 1.0 if val == entry.answer else 0.0

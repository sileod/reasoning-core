"""Resolve relative paths through dot segments and symbolic links."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'filesystem_path_resolution (draw 2 of 3)',
 'hypothesis': 'manual_high_value_80:filesystem_path_resolution',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/filesystem_path_resolution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 186835038,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

STATUS = {0: "RESOLVED", 1: "LOOP", 2: "ESCAPE"}


@dataclass
class PathConfig(Config):
    depth: int = 3
    nlinks: int = 2
    link_len: int = 3

    def apply_difficulty(self, level):
        self.depth = stochastic_rounding(self.depth + level)
        self.nlinks = stochastic_rounding(self.nlinks + level)
        self.link_len = stochastic_rounding(self.link_len + level)


def _parent(root, loc):
    cur = root
    for d in loc:
        cur = cur[d]
    return cur


def resolve_path(segs, root, max_hops=40):
    loc = []
    pending = list(segs)
    hops = 0
    while True:
        if not pending:
            return "RESOLVED"
        if hops > max_hops:
            return "LOOP"
        seg = pending[0]
        if seg == ".":
            pending = pending[1:]
            continue
        if seg == "..":
            if not loc:
                return "ESCAPE"
            loc.pop()
            pending = pending[1:]
            continue
        cur = _parent(root, loc)
        child = cur.get(seg)
        if child is None:
            return "RESOLVED"
        if isinstance(child, dict):
            loc.append(seg)
            pending = pending[1:]
        else:
            expand = child.split("/") if child else [".."]
            pending = expand + pending[1:]
            hops += 1


def _collect_links(root):
    links = []
    for name, val in root.items():
        if isinstance(val, str):
            links.append((name, val))
        elif isinstance(val, dict):
            links.extend(_collect_links(val))
    return links


class FilesystemPathResolution(Task):
    summary = ("Resolve relative paths through dot segments and symbolic links under stated root and link "
               "rules, returning the canonical target or error state as a RESOLVED/LOOP/ESCAPE flag.")
    design_choice = ("Answer type: a boolean flag 'RESOLVED' or 'LOOP'/'ESCAPE' for each path, where the "
                     "solver must output a single error code instead of a path, making the answer a small "
                     "label set.")
    config_cls = PathConfig

    def generate_entry(self):
        depth = self.config.depth
        names = ["d%d" % i for i in range(depth)]
        root = {}
        cur = root
        for nm in names:
            nxt = {}
            cur[nm] = nxt
            cur = nxt

        for k in range(self.config.nlinks):
            lk = random.randrange(2, self.config.link_len + 2)
            parts = [random.choice(names) for _ in range(lk)]
            root["l%d" % k] = "/".join(parts)

        mode = random.randrange(3)
        if mode == 2:
            segs = [".."] * random.randrange(1, 4)
            answer = "ESCAPE"
        elif mode == 1:
            root["l0"] = "l0/x"
            segs = ["l0"]
            answer = "LOOP"
        else:
            k = random.randrange(1, depth + 1)
            segs = [random.choice(names) for _ in range(k)]
            answer = "RESOLVED"

        gold = resolve_path(segs, root)
        if gold != answer:
            answer = gold
        links = _collect_links(root)
        path = "/".join(segs)
        return Entry(
            metadata={"path": path, "links": links, "chain": names, "mode": mode},
            answer=answer,
        )

    def render_prompt(self, metadata):
        links_txt = "; ".join("%s->%s" % (n, t) for n, t in metadata["links"])
        return (
            "The filesystem root contains directories %s and symbolic links %s. "
            "Resolve the relative path '%s' through dot segments and links. "
            "Write one of RESOLVED, LOOP, or ESCAPE as your final answer."
            % ("/".join(metadata["chain"]), links_txt, metadata["path"])
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip().upper() == entry.answer else 0.0

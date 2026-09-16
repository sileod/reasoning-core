import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

ALPHA = "abcdefghijklmnopqrstuvwxyz"


@dataclass
class SuffixAutomatonConfig(Config):
    length: int = 6
    alphabet_size: int = 3

    def apply_difficulty(self, level):
        self.length = stochastic_rounding(self.length + 2 * level)
        self.alphabet_size = min(4, 2 + (level // 2))


def _build_sam(s):
    """Grow a suffix automaton over s one char at a time.

    Returns list of states in creation order, each {'len','link','next'} where
    next maps char->state id. State numbering follows creation order.
    """
    states = [{"len": 0, "link": -1, "next": {}}]
    last = 0
    for ch in s:
        cur = len(states)
        states.append({"len": states[last]["len"] + 1, "link": 0, "next": {}})
        p = last
        while p != -1 and ch not in states[p]["next"]:
            states[p]["next"][ch] = cur
            p = states[p]["link"]
        if p == -1:
            states[cur]["link"] = 0
        else:
            q = states[p]["next"][ch]
            if states[p]["len"] + 1 == states[q]["len"]:
                states[cur]["link"] = q
            else:
                clone = len(states)
                states.append(
                    {
                        "len": states[p]["len"] + 1,
                        "link": states[q]["link"],
                        "next": dict(states[q]["next"]),
                    }
                )
                while p != -1 and states[p]["next"].get(ch) == q:
                    states[p]["next"][ch] = clone
                    p = states[p]["link"]
                states[q]["link"] = clone
                states[cur]["link"] = clone
        last = cur
    return states


def _format_table(states):
    lines = []
    for sid in range(len(states)):
        st = states[sid]
        trans = ",".join(f"{c}->{states[sid]['next'][c]}" for c in sorted(states[sid]["next"]))
        lines.append(f"{sid}:(len {st['len']},link {st['link']},{trans})")
    return "\n".join(lines)


def _state_tuple(states):
    """Canonical answer: tuple of (len, link, sorted outgoing transitions)."""
    triples = []
    for sid in range(len(states)):
        st = states[sid]
        tr = tuple((c, states[sid]["next"][c]) for c in sorted(states[sid]["next"]))
        triples.append((st["len"], st["link"], tr))
    return tuple(triples)


def _parse_answer(answer):
    """Parse the answer into a tuple of (len, link, sorted transitions tuple)."""
    lines = [ln.strip() for ln in answer.strip().splitlines() if ln.strip()]
    out = []
    for ln in lines:
        rest = ln.split(":", 1)[1]
        rest = rest.strip().lstrip("(").rstrip(")")
        parts = rest.split(",")
        ln_val = int(parts[0].strip())
        link_val = int(parts[1].strip())
        trans_str = ",".join(parts[2:])
        trans = []
        if trans_str:
            for tok in trans_str.split(","):
                tok = tok.strip()
                if not tok:
                    continue
                c, to = tok.split("->")
                trans.append((c, int(to)))
        trans.sort(key=lambda t: t[0])
        out.append((ln_val, link_val, tuple(trans)))
    return tuple(out)


def _normalize(x):
    """Recursively convert nested lists/tuples into nested tuples for comparison."""
    if isinstance(x, (list, tuple)):
        return tuple(_normalize(v) for v in x)
    return x


class suffix_automaton_growth_trace(Task):
    summary = (
        "Extend a suffix automaton one character at a time: follow suffix links, "
        "create clone states to split equivalence classes, redirect transitions; "
        "vary alphabet size and repetitiveness; answer the final (length, link, "
        "transitions) state table."
    )
    design_choice = (
        "Answer the state table as a canonical list of triples (len, link, sorted "
        "outgoing transitions) with states numbered in creation order, requiring "
        "exact match."
    )
    config_cls = SuffixAutomatonConfig

    def generate_entry(self):
        length = self.config.length
        alpha_size = self.config.alphabet_size
        alphabet = ALPHA[:alpha_size]
        s = "".join(random.choice(alphabet) for _ in range(length))
        states = _build_sam(s)
        table = _format_table(states)
        answer = "\n".join(
            f"{i}:({ln},{lk}," + ",".join(f"{c}->{to}" for c, to in tr) + ")"
            for i, (ln, lk, tr) in enumerate(_state_tuple(states))
        )
        answer_toks = _state_tuple(states)
        assert states[0]["link"] == -1
        for st in states:
            assert st["len"] >= 0
            for c, t in st["next"].items():
                assert 0 <= t < len(states)
        return Entry(
            metadata={
                "s": s,
                "alphabet_size": alpha_size,
                "length": length,
                "state_count": len(states),
                "state_table": table,
                "answer_tokens": [list(t) for t in answer_toks],
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        s = metadata["s"]
        return (
            f"We build a suffix automaton (SAM) over the string \"{s}\" by "
            "extending it one character at a time, reading the string from left to "
            "right and appending each next character at each step. States are "
            "numbered in creation order: state 0 is the initial state with len 0 "
            "and link -1, and every new state (including clones) is added with the "
            "next unused integer id. For each appended character, apply the "
            "standard online SAM construction: create a new state for the extended "
            "string, walk suffix links from the previous last state adding the new "
            "transition, and when a transition already exists, either set the link "
            "if the target's len matches, or split by creating a clone state and "
            "redirecting the conflicting transitions.\n\n"
            "Give the final state table of the completed automaton, one line per "
            "state in creation order (so line i is state i), each line exactly:\n"
            "i:(len,link,transitions)\n"
            "where len is that state's longest-string length, link is its suffix "
            "link id (-1 only for state 0), and transitions is a comma-separated "
            "list of c->to entries for that state's outgoing transitions sorted by "
            "character, empty if the state has no outgoing transitions. Nothing "
            "else.\n"
            "Format example for two states:\n"
            "0:(0,-1,a->1)\n1:(1,0,)\n"
            "Answer with only the state table lines."
        )

    def score_answer(self, answer, entry):
        true = entry.metadata.get("answer_tokens")
        if true is None:
            return 0.0
        try:
            got = _parse_answer(answer)
        except Exception:
            return 0.0
        if _normalize(got) != _normalize(true):
            return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'suffix_automaton_growth_trace (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dynamic_structures_r1/suffix_automaton_growth_trace',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

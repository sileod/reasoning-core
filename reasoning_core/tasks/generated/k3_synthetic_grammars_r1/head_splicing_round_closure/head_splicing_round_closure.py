import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'head_splicing_round_closure (draw 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_synthetic_grammars_r1/head_splicing_round_closure',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_ALPH = "01"
_POOL_CAP = 60


def _make_starter(exon_len):
    chars = [random.choice(_ALPH) for _ in range(exon_len)]
    lo = random.randrange(0, len(chars) + 1)
    hi = random.randrange(0, len(chars) + 1)
    if hi < lo:
        lo, hi = hi, lo
    chars.insert(lo, "A")
    chars.insert(hi, "D")
    return "".join(chars)


def _closure(starters, rounds):
    pool = set(starters)
    for _ in range(rounds):
        plist = sorted(pool)
        new = set()
        for x in plist:
            dpos = [i for i, c in enumerate(x) if c == "D"]
            for y in plist:
                apos = [i for i, c in enumerate(y) if c == "A"]
                for xd in dpos:
                    for ya in apos:
                        prod = x[:xd + 1] + y[ya:]
                        if prod not in pool and prod not in new:
                            new.add(prod)
                            if len(pool) + len(new) > _POOL_CAP:
                                return None
        if not new:
            break
        pool |= new
    return pool


@dataclass
class HeadSplicingRoundClosureConfig(Config):
    num_starters: int = 2
    exon_len: int = 2
    rounds: int = 1

    def apply_difficulty(self, level):
        self.num_starters = stochastic_rounding(3 + level // 4)
        self.exon_len = stochastic_rounding(2 + level // 2)
        self.rounds = stochastic_rounding(1 + level // 4)


class HeadSplicingRoundClosure(Task):
    summary = ("Run rounds of Head splicing over a starter string set over 0/1 exons with donor and "
               "acceptor palindromic pairing sites: match a D in one string and an A in another, cut and "
               "join prefix-through-D with suffix-from-A, pool recombinants in parallel each round; answer "
               "the lexicographically sorted list of distinct new strings after k rounds.")
    design_choice = ("Site patterns are fixed-length palindromic pairs; instances vary only in starter "
                     "strings and round count, with answer as sorted recombinants.")
    config_cls = HeadSplicingRoundClosureConfig

    def generate_entry(self):
        for _ in range(200):
            starters = [_make_starter(self.config.exon_len)
                        for _ in range(self.config.num_starters)]
            pool = _closure(starters, self.config.rounds)
            if pool is None:
                continue
            rec = sorted(pool - set(starters))
            if 1 <= len(rec) <= _POOL_CAP:
                answer = "[" + ", ".join(rec) + "]"
                return Entry(metadata={"starters": starters,
                                       "rounds": self.config.rounds,
                                       "recombinants": rec},
                             answer=answer)
        raise RuntimeError("head_splicing_round_closure: no valid instance in budget")

    def render_prompt(self, metadata):
        starters = metadata["starters"]
        start_line = "\n".join(f"S{i + 1} = {s}" for i, s in enumerate(starters))
        return (f"Head splicing acts on a pool of strings over the alphabet 0/1 plus two single-character "
                f"palindromic pairing sites: a donor site D and an acceptor site A. One splice takes any "
                f"string X containing a D and any string Y containing an A. Choose a D inside X and an A "
                f"inside Y, writing X = P\u00b7D\u00b7Q and Y = R\u00b7A\u00b7S. The recombinant is "
                f"P\u00b7D\u00b7A\u00b7S: the prefix of X up to and including its D, followed by the suffix "
                f"of Y beginning at its A. One round applies every possible such splice within the current "
                f"pool in parallel, and the new pool is the old pool plus all recombinants produced. "
                f"Starting from the starter strings below, run exactly {metadata['rounds']} rounds, then "
                f"list the distinct recombinant strings: every string present after the rounds that was not "
                f"one of the starters. Give your answer as a single list in lexicographic order using "
                f"character order 0 < 1 < A < D, formatted like [s1, s2, s3].\n\n"
                f"Starters:\n{start_line}")

    def score_answer(self, answer, entry):
        return 1.0 if str(answer or "").strip() == str(entry.answer).strip() else 0.0

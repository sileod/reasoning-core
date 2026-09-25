"""Joint share information: secret-sharing encoders over biased random bits and correlated shares.

A hidden bit H (uniform) drives two correlated share bits S0,S1: S0 equals H with probability
t0, S1 equals H with probability t1, independent given H. A biased random bit R equals 1 with
probability p, independent of everything else. The secret b is a deterministic encoder g(H,R):
b = g_{H,R}. A coalition observes some subset of {S0, S1}. We ask whether the coalition
recovers the secret (b fully determined), has perfect secrecy (its observation never changes
the probability of b), or suffers partial leakage, and which coalition is minimal and recovers.
"""

import random
import itertools
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class JointShareConfig(Config):
    n_instances: int = 64

    def apply_difficulty(self, level):
        pass


class JointShareInformation(Task):
    summary = (
        "Analyze finite secret-sharing encoders with biased randomness, correlated shares, "
        "and missing observations; answer minimal recovering coalitions or whether a coalition "
        "has perfect secrecy, partial leakage, or recovery."
    )
    design_choice = (
        "Represent the encoder as a deterministic function of a biased random bit and two "
        "correlated share bits; ask for the minimal coalition that recovers the secret or "
        "has perfect secrecy."
    )
    config_cls = JointShareConfig

    def _joint(self, g, t0, t1, p=0.5):
        # marginalize (H,R) -> states[(s0,s1)] = [weight_total, weight_b1]
        states = {}
        for hh in (0, 1):
            for s0 in (0, 1):
                ps0 = t0 if s0 == hh else 1 - t0
                for s1 in (0, 1):
                    ps1 = t1 if s1 == hh else 1 - t1
                    for rr in (0, 1):
                        prr = p if rr == 1 else 1 - p
                        gv = g[hh * 2 + rr]
                        w = 0.5 * ps0 * ps1 * prr
                        st = (s0, s1)
                        states.setdefault(st, [0.0, 0.0])
                        states[st][0] += w
                        states[st][1] += w * gv
        return states

    def _cond(self, states, subset, values):
        w0 = w1 = 0.0
        for (s0, s1), (wt, wt1) in states.items():
            ok = True
            for idx, val in zip(subset, values):
                if (s0 if idx == 0 else s1) != val:
                    ok = False
                    break
            if ok:
                w0 += wt - wt1
                w1 += wt1
        return w0, w1

    def _prior(self, states):
        tot = w1 = 0.0
        for wt, wt1 in states.values():
            tot += wt
            w1 += wt1
        return w1 / tot

    def _full_category(self, states):
        # classify full coalition {S0,S1}: recovery / perfect / leakage
        pr = self._prior(states)
        recovers = True
        perf = True
        for st, (wt, wt1) in states.items():
            if wt < 1e-9:
                continue
            c = wt1 / wt
            if not (wt1 < 1e-9 or (wt - wt1) < 1e-9):
                recovers = False
            if abs(c - pr) > 1e-6:
                perf = False
        if recovers:
            return "recovery"
        if perf:
            return "perfect"
        return "leakage"

    def _minimal_coalition(self, states):
        # nonempty subsets of {0,1}; return minimal bit-string or 'none'
        rec = []
        for mask in (1, 2, 3):
            subset = [i for i in (0, 1) if mask & (1 << i)]
            ok = True
            for values in itertools.product((0, 1), repeat=len(subset)):
                w0, w1 = self._cond(states, subset, values)
                if w0 + w1 < 1e-9:
                    continue
                if not (w0 < 1e-9 or w1 < 1e-9):
                    ok = False
                    break
            if ok:
                rec.append(frozenset(subset))
        if not rec:
            return "none"
        minimal = min(rec, key=len)
        return "".join(str(i) for i in sorted(minimal))

    def generate_entry(self):
        p = 0.5
        # difficulty: widen the bias p with level
        level = getattr(self.config, "_level", 0)
        p = min(0.18 + 0.1 * level, 0.85)

        for _ in range(2000):
            r = random.random()
            if r < 0.34:
                # ---- minimal recovering coalition (secret depends only on H) ----
                v0, v1 = random.randint(0, 1), random.randint(0, 1)
                g = [v0, v0, v1, v1]
                t0 = 1.0 if random.random() < 0.6 else random.uniform(0.55, 0.9)
                t1 = 1.0 if random.random() < 0.4 else random.uniform(0.55, 0.9)
                states = self._joint(g, t0, t1, p)
                pr = self._prior(states)
                if not (1e-6 < pr < 1 - 1e-6):
                    continue
                ans = self._minimal_coalition(states)
                if ans == "none" and random.random() < 0.5:
                    continue
                q = (
                    "Which nonempty subset of {S0,S1} is minimal among those that fully "
                    "determine the secret from what they observe? Answer with '0' (only S0), "
                    "'1' (only S1), '01' (both), or 'none' if none recovers."
                )
                typ = "minimal"
            elif r < 0.67:
                # ---- perfect secrecy of a random nonempty coalition ----
                if random.random() < 0.5:
                    # shares uninformative -> perfect secrecy yes
                    g = [random.randint(0, 1) for _ in range(4)]
                    t0 = t1 = 0.5
                    target = "yes"
                else:
                    # shares informative -> not perfect
                    x0, x1 = random.randint(0, 1), random.randint(0, 1)
                    g = [x0, 1 - x0, x1, 1 - x1]
                    t0 = random.uniform(0.75, 0.95)
                    t1 = random.uniform(0.75, 0.95)
                    target = "no"
                states = self._joint(g, t0, t1, p)
                pr = self._prior(states)
                if not (1e-6 < pr < 1 - 1e-6):
                    continue
                coalition = random.randint(1, 3)
                subset = [i for i in (0, 1) if coalition & (1 << i)]
                same = True
                for values in itertools.product((0, 1), repeat=len(subset)):
                    w0, w1 = self._cond(states, subset, values)
                    if w0 + w1 < 1e-9:
                        continue
                    if abs(w1 / (w0 + w1) - pr) > 1e-6:
                        same = False
                        break
                ans = "yes" if same else "no"
                if ans != target:
                    continue
                maskstr = "".join(str(i) for i in subset)
                q = (
                    f"Consider the coalition that observes shares {{{_names(maskstr)}}}. Does "
                    "this coalition have perfect secrecy, meaning what it observes never "
                    "changes the probability that the secret is 1? Answer yes or no."
                )
                typ = "secrecy"
            else:
                # ---- classify the full coalition {S0,S1} ----
                roll = random.random()
                if roll < 1 / 3:
                    # recovery: secret depends only on H and a share pins H
                    v0, v1 = random.randint(0, 1), random.randint(0, 1)
                    g = [v0, v0, v1, v1]
                    t0 = 1.0
                    t1 = random.uniform(0.8, 1.0)
                    target = "recovery"
                elif roll < 2 / 3:
                    # perfect secrecy for the full coalition
                    g = [random.randint(0, 1) for _ in range(4)]
                    t0 = t1 = 0.5
                    target = "perfect"
                else:
                    # partial leakage
                    g = [0, 1, 1, 0]
                    t0 = random.uniform(0.75, 0.9)
                    t1 = random.uniform(0.75, 0.9)
                    target = "leakage"
                states = self._joint(g, t0, t1, p)
                pr = self._prior(states)
                if not (1e-6 < pr < 1 - 1e-6):
                    continue
                ans = self._full_category(states)
                if ans != target:
                    continue
                q = (
                    "The coalition observing both shares {S0,S1} either recovers the secret, "
                    "has perfect secrecy, or suffers partial leakage. Which is it? Answer "
                    "recovery, perfect, or leakage."
                )
                typ = "classify"
            break
        else:
            raise RuntimeError("joint_share_information: failed to produce a valid instance")

        metadata = {
            "g": [int(x) for x in g],
            "p": float(p),
            "t0": float(t0),
            "t1": float(t1),
            "prior": float(pr),
            "type": typ,
            "answer": ans,
        }
        if typ == "secrecy":
            metadata["coalition_str"] = maskstr
        return Entry(metadata=metadata, answer=ans)

    def render_prompt(self, metadata):
        g00, g01, g10, g11 = metadata["g"]
        p = metadata["p"]
        t0 = metadata["t0"]
        t1 = metadata["t1"]
        prior = metadata["prior"]
        typ = metadata["type"]
        head = (
            "A secret bit is produced by a deterministic encoder from a biased random bit R "
            f"and two correlated share bits S0,S1. R equals 1 with probability {p:.3f} and 0 "
            "otherwise, independent of everything else. The share bits are correlated with a "
            f"hidden uniform bit H: S0 equals H with probability {t0:.2f} and S1 equals H with "
            f"probability {t1:.2f}. The encoder truth table gives the secret as a function of "
            f"(H,R): g(0,0)={g00}, g(0,1)={g01}, g(1,0)={g10}, g(1,1)={g11}. The unconditional "
            f"probability that the secret is 1 is {prior:.3f}."
        )
        if typ == "minimal":
            q = (
                "Which nonempty subset of {S0,S1} is minimal among those that fully determine "
                "the secret from what they observe? Answer '0' (only S0), '1' (only S1), '01' "
                "(both), or 'none'."
            )
        elif typ == "secrecy":
            coalition = metadata.get("coalition_str", "")
            q = (
                f"Consider the coalition that observes shares {{{_names(coalition)}}}. Does it "
                "have perfect secrecy? Answer yes or no."
            )
        else:
            q = (
                "The coalition observing both shares {S0,S1} either recovers the secret, has "
                "perfect secrecy, or suffers partial leakage. Answer the outcome."
            )
        return head + "\n" + q + "\nState only your final answer."

    def score_answer(self, answer, entry):
        gold = entry["answer"]
        return 1.0 if answer.strip() == gold else 0.0


def _names(s):
    parts = ["S0" if c == "0" else "S1" for c in s]
    if not parts:
        return "the empty coalition"
    return ",".join(parts)


TASK_META = {'parent_source_id': None,
 'idea': 'joint_share_information (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_shortcuts_fail_r4/joint_share_information',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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

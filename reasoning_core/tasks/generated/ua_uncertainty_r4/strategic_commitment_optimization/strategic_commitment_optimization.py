import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'strategic_commitment_optimization (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/strategic_commitment_optimization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class StackelbergCommitmentConfig(Config):
    n_leader: int = 3
    n_follower: int = 2
    payoff_lo: int = -5
    payoff_hi: int = 5

    def apply_difficulty(self, level):
        self.n_leader = stochastic_rounding(3 + level * 1.0)
        self.n_follower = stochastic_rounding(2 + level * 1.0)
        self.payoff_lo = -6 - level
        self.payoff_hi = 6 + level


def _best_response(follower_payoffs):
    best = None
    best_idx = 0
    for i, p in enumerate(follower_payoffs):
        if best is None or p > best:
            best = p
            best_idx = i
    return best_idx


def _optimal_commitment(leader_actions, follower_actions, leader_pay, follower_pay):
    best_com = None
    best_val = None
    for li in range(len(leader_actions)):
        fi = _best_response(follower_pay[li])
        effective = leader_pay[li][fi]
        if best_val is None or effective > best_val:
            best_val = effective
            best_com = leader_actions[li]
    return best_com


def _solve(metadata):
    la = metadata["leader_actions"]
    fa = metadata["follower_actions"]
    lp = metadata["leader_pay"]
    fp = metadata["follower_pay"]
    return _optimal_commitment(la, fa, lp, fp)


class StrategicCommitmentOptimization(Task):
    summary = "Stackelberg commitment: choose a leader action maximizing its payoff under the follower's deterministic best response with stated tie-breaks, over random finite integer leader/follower payoff matrices."
    design_choice = "Instances present the commitment as a pure action from a finite set, and the solver must return the action string that maximizes the leader's payoff under the follower's best response with deterministic tie-breaking."
    config_cls = StackelbergCommitmentConfig

    def generate_entry(self):
        cfg = self.config
        n_l = max(2, int(cfg.n_leader))
        n_f = max(2, int(cfg.n_follower))
        for _ in range(1000):
            leader_actions = [f"L{i}" for i in range(n_l)]
            follower_actions = [f"F{i}" for i in range(n_f)]
            leader_pay = []
            follower_pay = []
            for _li in range(n_l):
                leader_pay.append(
                    [random.randint(cfg.payoff_lo, cfg.payoff_hi) for _ in range(n_f)]
                )
                follower_pay.append(
                    [random.randint(cfg.payoff_lo, cfg.payoff_hi) for _ in range(n_f)]
                )
            metadata = {
                "leader_actions": leader_actions,
                "follower_actions": follower_actions,
                "leader_pay": leader_pay,
                "follower_pay": follower_pay,
            }
            answer = _solve(metadata)
            assert answer in leader_actions
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("failed to draw a valid instance")

    def render_prompt(self, metadata):
        la = metadata["leader_actions"]
        fa = metadata["follower_actions"]
        lp = metadata["leader_pay"]
        fp = metadata["follower_pay"]
        ls = ", ".join(la)
        fs = ", ".join(fa)
        lines = []
        header = "        " + "".join(f"{f:>7}" for f in fa)
        lines.append(header)
        for li, a in enumerate(la):
            cells = [
                f"{lp[li][fi]}/{fp[li][fi]}" for fi in range(len(fa))
            ]
            row = f"{a:<8}" + "".join(f"{c:>7}" for c in cells)
            lines.append(row)
        matrix = "\n".join(lines)
        return (
            "A leader can bind to exactly one action chosen from {" + ls + "}. The follower, "
            "seeing the chosen action, then picks the follower action from {" + fs + "} that "
            "maximizes the follower's own payoff (ties broken toward the smallest index, "
            "F0 before F1 before F2, and so on). The leader's payoff is the value in the "
            "selected cell of the payoff matrix below; the leader commits to the action that "
            "maximizes the leader's own payoff, and ties among leader actions are broken toward "
            "the smallest index.\n\n"
            "Payoff matrix (rows are leader actions, columns are follower actions; each cell "
            "shows leader/follower payoff):\n" + matrix + "\n\n"
            "Which leader action does the leader commit to? Name exactly one action string from {"
            + ls + "}."
        )

    def score_answer(self, answer, entry):
        ref = entry["answer"]
        a = str(answer).strip()
        if a == ref:
            return 1
        if a in entry["metadata"]["leader_actions"]:
            return 0
        return 0

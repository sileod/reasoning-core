"""Group sequential trial: accumulate z scores across looks and report the
stopping look and efficacy/futility decision under O'Brien-Fleming boundaries."""

import random
from dataclasses import dataclass

from scipy.stats import norm
from reasoning_core.template import Config, Entry, Task


def of_bounds(k, num_looks, alpha=0.05, beta=0.2):
    """Two-sided O'Brien-Fleming efficacy boundaries and one-sided futility.

    alpha-spending (Kim-DeMets O'Brien-Fleming): alpha_i = alpha * (i/K)^3.
    Cumulative boundary constant for spending alpha per group by a normal
    inverse: b_i = inv_Phi(1 - alpha_i/2).  Boundary at look k on the z scale:
    B_k = b_K * sqrt(k/K).  Default is O'Brien-Fleming (constant critical
    value on the information scale).  Futility boundary is flat at -C with
    C = inv_Phi(1 - beta) on the z scale (a simple non-binding futility rule).
    """
    B_K = norm.ppf(1 - alpha / 2.0)
    B = [B_K * (k / num_looks) ** 0.5 for k in range(1, num_looks + 1)]
    C = norm.ppf(1 - beta)
    return B, C


@dataclass
class BoundaryConfig(Config):
    num_looks: int = 3
    drift_min: float = -1.5
    drift_max: float = 1.5
    z_unit: float = 1.0

    def apply_difficulty(self, level):
        self.num_looks = random.randint(2, min(2 + level, 10))
        mag = 0.5 + 0.35 * level
        self.drift_min = -mag
        self.drift_max = mag


class SequentialBoundaryCrossing(Task):
    """Accumulate log-likelihood increments or per-look z scores, checking efficacy
    and futility boundaries at each look across drift and boundary schedules; report
    the stopping look and final decision."""
    summary = ("Accumulate per-look z scores across 2-10 O'Brien-Fleming alpha-spending "
               "group-sequential looks, comparing each cumulative z against time-varying "
               "efficacy and futility boundaries; report terminating look (1..K) and "
               "'efficacy' if upper efficacy crossed, 'futility' if lower futility crossed, "
               "'continue' otherwise, over varying true drift and look counts.")
    config_cls = BoundaryConfig
    design_choice = ("Vary the number of looks between 2 and 10, with boundaries computed "
                     "from an O'Brien-Fleming alpha-spending function, and require reporting "
                     "the stopping look index and 'efficacy' or 'futility' decision.")

    def generate_entry(self):
        cfg = self.config
        K = cfg.num_looks
        B, C = of_bounds(K, cfg.num_looks)
        z_unit = cfg.z_unit

        # Draw a true per-look drift.
        drift = random.uniform(cfg.drift_min, cfg.drift_max)

        stopping_look = None
        decision = None
        z_cum = 0.0
        z_by_look = []
        for k in range(1, K + 1):
            z_k = drift * z_unit + random.gauss(0.0, 1.0)
            z_cum += z_k
            z_by_look.append(round(z_cum, 4))
            Bk = B[k - 1]
            if z_cum > Bk:
                stopping_look = k
                decision = "efficacy"
                break
            if z_cum < -C:
                stopping_look = k
                decision = "futility"
                break
        if stopping_look is None:
            stopping_look = K
            decision = "continue"

        z_cum = round(z_cum, 4)
        drift = round(drift, 4)

        # Domain assertions: drift finite, z_final finite, decision in set.
        assert -10 <= drift <= 10
        assert abs(z_cum) < 1e6
        assert decision in ("efficacy", "futility", "continue")
        assert 1 <= stopping_look <= K

        # Independently recompute the stopping decision from z_by_look to check gold.
        zcheck = 0.0
        dcheck = None
        lcheck = None
        for k, zk in enumerate(z_by_look, start=1):
            zcheck = zk
            if zcheck > B[k - 1]:
                lcheck = k
                dcheck = "efficacy"
                break
            if zcheck < -C:
                lcheck = k
                dcheck = "futility"
                break
        if lcheck is None:
            lcheck = K
            dcheck = "continue"
        assert (lcheck, dcheck) == (stopping_look, decision)

        metadata = {
            "num_looks": K,
            "cumulative_z": z_by_look,
            "decision": decision,
            "stopping_look": stopping_look,
            "drift": drift,
            "z_unit": z_unit,
            "efficacy_boundaries": [round(b, 4) for b in B],
            "futility_boundary": round(C, 4),
        }
        answer = f"{stopping_look} {decision}"
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        zs = ", ".join(f"{z:.4f}" for z in metadata["cumulative_z"])
        return (
            f"In a group-sequential clinical trial with {metadata['num_looks']} planned "
            f"looks, boundaries come from an O'Brien-Fleming alpha-spending function "
            f"(two-sided efficacy) and a flat futility boundary. After each interim look "
            f"the cumulative z statistic is compared to the boundaries; the trial stops "
            f"early for efficacy if the cumulative z exceeds the efficacy boundary, stops "
            f"early for futility if it falls below the futility boundary, and otherwise "
            f"continues (after the final look it is 'continue' if neither boundary was "
            f"crossed). The per-look cumulative z statistics were, in order: [{zs}]. "
            f"The efficacy boundaries at look k are B_k = {list(metadata['efficacy_boundaries'])}, "
            f"and the futility boundary is {metadata['futility_boundary']} (crossed when the "
            f"cumulative z is below its negative: z < -{metadata['futility_boundary']}). "
            f"Report the stopping look index and the decision, as the look number followed "
            f"by the word 'efficacy', 'futility' or 'continue', for example '2 futility'."
        )

    def score_answer(self, answer, entry):
        decision = entry.metadata["decision"]
        stopping_look = entry.metadata["stopping_look"]
        target = f"{stopping_look} {decision}"
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == target else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'sequential_boundary_crossing (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scientific_reasoning_r4/sequential_boundary_crossing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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

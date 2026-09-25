"""Mechanical backlash induction: infer slack from a motor trace, predict load readouts."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class BacklashInductionConfig(Config):
    b_lo: int = 2
    b_hi: int = 4
    x_hi: int = 16
    s_hi: int = 3
    d_hi: int = 3

    def apply_difficulty(self, level):
        self.b_hi = 2 * (2 + level)
        self.b_lo = 2
        self.x_hi = 10 + 6 * level
        self.s_hi = max(2, level + 1)
        self.d_hi = max(3, 2 * level + 2)


def _load_track(B, xs):
    """Dead-zone backlash hysteresis (centre-following, width B), used to verify gold.

    Boundary rails: driving up gives load = motor - B/2; driving down gives
    load = motor + B/2.  Between them the load is frozen.
    """
    b2 = B / 2.0
    y = xs[0] - b2
    for x in xs[1:]:
        if x - b2 > y:
            y = x - b2
        elif x + b2 < y:
            y = x + b2
    return y


def _final_load(B, scene, xm, s0, command):
    """Analytic final load for one constructed scene, independent of _load_track."""
    b2 = B // 2
    total = s0 + command
    if scene == 1:
        if total < B:
            return xm - b2
        return (xm - total) + b2
    if total < B:
        return -xm + b2
    return (-xm + total) - b2


def _parse_int(answer):
    try:
        return int(float(str(answer).strip()))
    except (TypeError, ValueError):
        return None


class MechanicalBacklashInduction(Task):
    summary = ("Infer slack and directional dead zones from an actuator's motor trace "
               "around a reversal, then execute new reversals and partial slack takeups "
               "to determine final load readouts in mm.")
    design_choice = ("Each instance provides a single actuator's position-vs-time trace "
                     "with a marked reversal; the solver must output the final position "
                     "after a specified partial takeup command, with slack magnitude and "
                     "direction implied by the trace.")
    config_cls = BacklashInductionConfig

    def generate_entry(self):
        cfg = self.config
        B = 2 * random.randint(cfg.b_lo // 2, cfg.b_hi // 2)
        scene = random.choice((1, -1))
        xm = random.randint(cfg.b_hi, cfg.x_hi)
        s0 = random.randint(1, min(cfg.s_hi, B - 1))
        command = random.randint(0, cfg.d_hi)

        answer = _final_load(B, scene, xm, s0, command)
        if not (B >= 2 and (B % 2) == 0 and 1 <= s0 < B and command >= 0
                and isinstance(answer, int)):
            raise RuntimeError("backlash induction invariant violated")

        turn_motor = xm if scene == 1 else -xm
        turn_load = xm - B // 2 if scene == 1 else -xm + B // 2
        trace_end_motor = turn_motor - s0 if scene == 1 else turn_motor + s0
        cmd_dir = "down" if scene == 1 else "up"

        # Independently verify through the full kinematic trajectory.
        motor_traj = [0, turn_motor, trace_end_motor,
                      trace_end_motor - command if scene == 1 else trace_end_motor + command]
        verify = _load_track(B, motor_traj)
        if int(round(verify)) != answer:
            raise RuntimeError(f"backlash verification mismatch: {verify} != {answer}")

        metadata = {
            "B": B,
            "scene": scene,
            "xm": xm,
            "s0": s0,
            "command": command,
            "turn_motor": turn_motor,
            "turn_load": turn_load,
            "trace_end_motor": trace_end_motor,
            "final_load": answer,
            "cmd_dir": cmd_dir,
        }
        return Entry(metadata=metadata, answer=str(answer))

    def render_prompt(self, metadata):
        scene = metadata["scene"]
        B = metadata["B"]
        command = metadata["command"]
        turn_motor = metadata["turn_motor"]
        trace_end_motor = metadata["trace_end_motor"]
        cmd_dir = metadata["cmd_dir"]

        if scene == 1:
            drive = (f"the motor drove up from 0 mm to {turn_motor} mm, with the load "
                     f"riding one half-gap behind the motor; the motor then reversed and "
                     f"descended to {trace_end_motor} mm")
            gap_note = f"the motor descended the {B} mm backlash gap with the load motionless"
        else:
            drive = (f"the motor drove down from 0 mm to {turn_motor} mm, with the load "
                     f"riding one half-gap ahead of the motor; the motor then reversed and "
                     f"ascended to {trace_end_motor} mm")
            gap_note = f"the motor ascended the {B} mm backlash gap with the load motionless"

        return (
            "An actuator positions a load through a coupling with a constant backlash gap. "
            "While engaged the load tracks the motor with a fixed half-gap offset, but "
            "whenever the motor reverses, the load stays still until the motor has "
            "traversed the entire gap, then it tracks the motor again. The gap is "
            "symmetric in both directions.\n\n"
            f"Trace: {drive}; {gap_note}, and the load has not yet begun moving again, so "
            "it is still at the position it held when the motor reversed.\n\n"
            f"The motor is now commanded to continue {cmd_dir} by another {command} mm.\n\n"
            "What is the load's position (in mm) after this command? Answer with a single "
            "number only."
        )

    def score_answer(self, answer, entry):
        gold = _parse_int(entry["answer"])
        got = _parse_int(answer)
        if gold is None or got is None:
            return 0.0
        return 1.0 if got == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'mechanical_backlash_induction (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_rule_induction_r4/mechanical_backlash_induction',
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

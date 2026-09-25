"""Convert coupled voltage-current termination equations to incident/reflected wave constraints."""

import random
from dataclasses import dataclass

import sympy as sp

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'multiport_wave_relation_translation (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_semantics_preserving_translation_r4/multiport_wave_relation_translation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _fmt_frac(r):
    p = int(sp.numer(r))
    q = int(sp.denom(r))
    if q == 1:
        return str(p)
    if q < 0:
        p, q = -p, -q
    return f"{p}/{q}"


def _norm(s):
    return "".join(str(s).split())


def _gamma(spec, z0):
    kind = spec["kind"]
    if kind == "short":
        return sp.Integer(-1)
    if kind == "open":
        return sp.Integer(1)
    if kind == "matched":
        return sp.Integer(0)
    zl = sp.Rational(spec["num"], spec["den"])
    return (zl - z0) / (zl + z0)


@dataclass
class WaveConfig(Config):
    num_ports: int = 2
    max_load: int = 6
    max_frac: int = 0

    def apply_difficulty(self, level):
        self.num_ports = 2 + level
        self.max_load = 4 + 2 * level
        self.max_frac = level


class MultiportWaveRelationTranslation(Task):
    summary = ("Convert coupled voltage-current termination equations into incident/reflected "
               "wave constraints under stated reference impedances; answer per-port equivalent "
               "relations b_i = c*a_i with rational reflection coefficients, covering shorts, "
               "opens, matched and resistive loads on multiport networks.")
    design_choice = ("Answer as a canonical set of wave-relation equations (e.g., a_1 = b_1, "
                     "a_2 = -b_2) with ports labeled 1..N, using symbolic coefficients 0, +/-1, "
                     "or fractional real numbers.")
    config_cls = WaveConfig

    def generate_entry(self):
        ports = []
        answers = []
        for i in range(1, self.config.num_ports + 1):
            z0 = random.randint(1, 8)
            kind = random.choice(["short", "open", "matched", "load", "load", "load"])
            num = den = None
            if kind == "load":
                if self.config.max_frac > 0 and random.random() < 0.35:
                    den = random.randint(2, 4)
                    num = random.randint(1, self.config.max_load)
                else:
                    den = 1
                    num = random.randint(1, self.config.max_load)
            else:
                num = den = None
            spec = {"kind": kind, "num": num, "den": den}
            g = _gamma(spec, sp.Rational(z0))
            assert g == g and sp.im(g) == 0
            assert -1 <= float(g) <= 1
            ports.append({"index": i, "z0": z0, **spec})
            answers.append(f"b_{i} = {_fmt_frac(g)}*a_{i}")
        answer = "; ".join(answers)
        return Entry(metadata={"ports": ports}, answer=answer)

    def render_prompt(self, metadata):
        lines = [
            "Each port i carries voltage V_i and current I_i related to incident wave a_i and "
            "reflected wave b_i by V_i = sqrt(Z_i)*(a_i + b_i) and I_i = (1/sqrt(Z_i))*(a_i - b_i).",
            "Ports and their terminations:",
        ]
        for p in metadata["ports"]:
            tag = p["kind"]
            if tag == "short":
                term = "a short (V = 0)"
            elif tag == "open":
                term = "an open (I = 0)"
            elif tag == "matched":
                term = f"a matched load equal to Z_i = {p['z0']} (V = {p['z0']} I)"
            else:
                zl = _fmt_frac(sp.Rational(p["num"], p["den"]))
                term = f"a load of Z_L = {zl} (V = {zl} I)"
            lines.append(f"  Port {p['index']}: reference impedance Z_{p['index']} = {p['z0']}, terminated by {term}")
        lines.append(
            "Write the incident/reflected wave constraint produced by each termination, one equation "
            "per port, in the exact form  b_<i> = c*a_<i>  where c is the reflection coefficient as an "
            "exact rational fraction (an integer like 1 or -1 is a valid c; use 0 for a matched load). "
            "Example of the exact format:  b_1 = -1*a_1; b_2 = 1/2*a_2"
        )
        lines.append("Answer only the relations, ports in order, separated by \"; \".")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        return 1.0 if _norm(answer) == _norm(gold) else 0.0

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'polarization_projection_cascade (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_psychometrics_r5/polarization_projection_cascade',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

ANG = (0, 30, 60, 90)


def cos2_frac(diff_deg):
    d = diff_deg % 180
    if d == 0 or d == 180:
        return Fraction(1)
    if d == 30 or d == 150:
        return Fraction(3, 4)
    if d == 60 or d == 120:
        return Fraction(1, 4)
    return Fraction(0, 1)


def compute_intensity(node, intensity, pol_angle):
    if node[0] == "cascade":
        angles = node[1]
        cur = intensity
        p = pol_angle
        for a in angles:
            if p is None:
                cur = cur / 2
            else:
                cur = cur * cos2_frac(a - p)
            p = a
        return cur
    k = node[1]
    total = Fraction(0, 1)
    for child in node[2]:
        total += compute_intensity(child, intensity / k, pol_angle)
    return total


def format_fraction(fr):
    fr = Fraction(fr)
    return str(fr.numerator) if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"


def parse_fraction(text):
    text = str(text).strip()
    if "/" in text:
        a, b = text.split("/")
        return Fraction(int(a), int(b))
    return Fraction(int(text))


@dataclass
class PolarizationConfig(Config):
    arm_len: int = 2
    max_depth: int = 0
    top_arms: int = 1
    split_lo: int = 2
    split_hi: int = 3

    def apply_difficulty(self, level):
        self.arm_len = max(2, stochastic_rounding(3 + 0.6 * level))
        self.max_depth = max(0, stochastic_rounding(level / 2))
        self.top_arms = 1 + ((level + 1) // 3)
        if level >= 4:
            self.split_lo, self.split_hi = 3, 4
        else:
            self.split_lo, self.split_hi = 2, 3


class PolarizationProjectionCascade(Task):
    summary = "Track unpolarized light through rotated polarizers, equal beam splits, and incoherent recombinations via Malus's law with rational 30-degree angles; distinguish blocked paths from partial attenuation and return output intensity as a reduced fraction of the input."
    design_choice = "Use a fixed sequence of polarizer angles and ask for the final intensity as a fraction of the input, with answers being rational numbers in lowest terms."
    config_cls = PolarizationConfig

    def _gen_cascade(self):
        length = random.randint(2, max(2, self.config.arm_len))
        return [random.choice(ANG) for _ in range(length)]

    def _gen_node(self, depth):
        if depth >= self.config.max_depth or random.random() < 0.5:
            return ("cascade", self._gen_cascade())
        k = random.randint(self.config.split_lo, self.config.split_hi)
        children = [self._gen_node(depth + 1) for _ in range(k)]
        return ("split", k, children)

    def generate_entry(self):
        cfg = self.config
        top = cfg.top_arms
        if top <= 1:
            node = self._gen_node(0)
            root = node
        else:
            children = [self._gen_node(0) for _ in range(top)]
            root = ("split", top, children)

        answer = compute_intensity(root, Fraction(1, 1), None)
        if answer < 0 or answer > 1:
            raise RuntimeError("answer out of [0,1] domain")

        ans_num = answer.numerator
        ans_den = answer.denominator

        return Entry(
            metadata={
                "angles": [int(a) for a in ANG],
                "program": root,
                "ans_num": int(ans_num),
                "ans_den": int(ans_den),
            },
            answer=format_fraction(answer),
        )

    def score_answer(self, answer, entry):
        try:
            got = parse_fraction(answer)
        except Exception:
            return 0.0
        want = Fraction(entry.metadata["ans_num"], entry.metadata["ans_den"])
        return 1.0 if got == want else 0.0

    def render_prompt(self, metadata):
        prog = metadata["program"]
        lines = [
            "A beam of unpolarized light of intensity 1 enters an optical assembly and its output intensity is measured as a fraction of the input.",
            "Malus's law: light polarized at an angle difference of d degrees from a polarizer's axis passes with factor cos^2(d); unpolarized light passing any polarizer keeps exactly half. A beam splitter divides the light equally among its arms and the arms recombine incoherently (their intensities add). All polarizer axes are drawn from {0, 30, 60, 90} degrees.",
            "Assembly structure:",
        ]

        def fmt_angles(angles):
            return ", ".join(f"{a}°" for a in angles)

        def render(node, indent):
            pad = "  " * indent
            if node[0] == "cascade":
                lines.append(pad + "Arm with polarizers at: " + fmt_angles(node[1]) + ".")
            else:
                lines.append(pad + f"Beam split into {node[1]} equal arms:")
                for child in node[2]:
                    render(child, indent + 1)

        render(prog, 0)
        lines.append("What fraction of the input intensity emerges? Answer as a rational number in lowest terms (write 1 for unchanged and 0 for fully blocked).")
        return "\n".join(lines)

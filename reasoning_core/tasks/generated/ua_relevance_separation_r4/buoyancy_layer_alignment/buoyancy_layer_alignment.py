import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'buoyancy_layer_alignment (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_relevance_separation_r4/buoyancy_layer_alignment',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _parse_layers(layer_str):
    return [float(x) for x in layer_str.split(",")]


def _volume_of(radius_top, radius_bottom, height):
    if radius_top == radius_bottom:
        return math.pi * radius_top * radius_top * height
    return math.pi * height * (radius_top * radius_top
                               + radius_top * radius_bottom
                               + radius_bottom * radius_bottom) / 3.0


def _candidate_indices(layers, body_bottom, body_top, taper_ratio):
    """Candidate waterline indices: layer boundaries crossed by the body
    plus interior points."""
    idx = []
    for i in range(1, len(layers)):
        y = layers[i]
        if body_bottom < y < body_top:
            idx.append(("b", i))
    mid = 0.5 * (body_bottom + body_top)
    idx.append(("i", mid))
    return idx


def _submerged_volume(body_bottom, body_top, wl, radius_top, radius_bottom, height):
    """Volume of the submerged portion of the tapered body below waterline wl."""
    if wl <= body_bottom:
        return 0.0
    if wl >= body_top:
        return _volume_of(radius_top, radius_bottom, height)
    frac = (wl - body_bottom) / height
    bottom_r = radius_bottom
    top_wl_r = bottom_r + (radius_top - radius_bottom) * frac
    return _volume_of(bottom_r, top_wl_r, wl - body_bottom)


@dataclass
class BuoyancyConfig(Config):
    max_layers: int = 5

    def apply_difficulty(self, level):
        self.max_layers = stochastic_rounding(self.max_layers + level)


class BuoyancyLayerAlignment(Task):
    summary = "Balance segmented prismatic bodies across immiscible fluid layers, varying cross-sections, ballast, and flooded versus sealed cavities; return equilibrium waterlines, submerged fractions, or sinking outcomes."
    design_choice = "Model a discrete set of candidate waterlines at layer boundaries and interior points; return the index of the stable equilibrium layer or 'sinks' if none exists."

    config_cls = BuoyancyConfig

    def generate_entry(self):
        target = random.choice(["sinks", "float"])
        for _attempt in range(300):
            entry = self._one_instance()
            if (target == "sinks") == (entry.answer == "sinks"):
                return entry
        return entry

    def _one_instance(self):
        n_layers = random.randint(2, self.config.max_layers)
        n_layers = max(2, min(n_layers, 7))

        layers = []
        y = random.uniform(0.05, 0.3)
        for i in range(n_layers):
            layers.append(y)
            y += random.uniform(0.25, 0.9)
        layers.append(y)
        dens = [random.uniform(0.6, 2.0) for _ in range(n_layers)]

        body_bottom = random.uniform(layers[0], layers[1])
        body_top = random.uniform(body_bottom + 0.3, body_bottom + 2.2)
        height = body_top - body_bottom

        radius_bottom = random.uniform(0.2, 0.8)
        radius_top = random.uniform(radius_bottom * 0.4, radius_bottom * 1.8)

        body_density = random.uniform(0.5, 1.4)

        ballast = 0.0
        if random.random() < 0.45:
            ballast = random.uniform(0.1, 1.0)
            body_density = min(1.5, body_density + random.uniform(0.0, 0.4))

        flooded = random.random() < 0.5

        total_vol = _volume_of(radius_top, radius_bottom, height)

        if flooded and random.random() < 0.5:
            cavity_vol = total_vol * random.uniform(0.3, 0.7)
            cavity_start = body_bottom + random.uniform(0.05, 0.3) * height
            cavity_end = min(body_top, cavity_start + random.uniform(0.1, 0.6) * height)
        else:
            cavity_vol = 0.0
            cavity_start = body_bottom
            cavity_end = body_bottom

        def net_force(wl, fluid_density):
            if flooded and cavity_vol > 0.0:
                sub_vol = _submerged_volume(body_bottom, body_top, wl,
                                            radius_top, radius_bottom, height)
                displaced_vol = sub_vol
                body_mass = body_density * (total_vol - cavity_vol) + ballast
                displaced_mass = fluid_density * displaced_vol
                return displaced_mass - body_mass
            else:
                sub_vol = _submerged_volume(body_bottom, body_top, wl,
                                            radius_top, radius_bottom, height)
                body_mass = body_density * total_vol + ballast
                displaced_mass = fluid_density * sub_vol
                return displaced_mass - body_mass

        candidates = _candidate_indices(layers, body_bottom, body_top,
                                        radius_top / radius_bottom if radius_bottom else 1.0)

        results = []
        for kind, ref in candidates:
            if kind == "b":
                i = ref
                wl = layers[i]
                layer_above = i - 1
                fluid_density = dens[layer_above]
                f = net_force(wl, fluid_density)
            else:
                wl = ref
                fluid_density = max(dens)
                f = net_force(wl, fluid_density)
            results.append((kind, ref, wl, fluid_density, f))

        stable = []
        for i, (kind, ref, wl, _, f) in enumerate(results):
            if kind == "b":
                above = net_force(wl - 1e-4, dens[ref - 1])
                below = net_force(wl + 1e-4, dens[max(0, min(len(dens) - 1, ref))])
                stable_flag = (f >= 0.0) and (above >= 0.0)
            else:
                r = next(r for r in results if r[0] == "i")
                stable_flag = abs(f) < 1e-3
            if stable_flag:
                stable.append(i)

        if not stable:
            answer = "sinks"
        else:
            sorted_stable = sorted(stable, key=lambda i: (results[i][1] if results[i][0] != "i" else results[i][1],
                                                          results[i][0]))
            answer = str(sorted_stable[0])

        metadata = {
            "layers": [round(x, 4) for x in layers],
            "densities": [round(x, 4) for x in dens],
            "body_bottom": round(body_bottom, 4),
            "body_top": round(body_top, 4),
            "radius_top": round(radius_top, 4),
            "radius_bottom": round(radius_bottom, 4),
            "body_density": round(body_density, 4),
            "ballast": round(ballast, 4),
            "flooded": flooded,
            "cavity_vol": round(cavity_vol, 4),
            "cavity_start": round(cavity_start, 4),
            "cavity_end": round(cavity_end, 4),
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        m = metadata
        if m["flooded"]:
            if m["cavity_vol"] > 0:
                cavity_txt = (
                    f"An open flooded cavity of volume {m['cavity_vol']} holds no trapped air; it "
                    f"removes that much solid material from the hull (effective solid density "
                    f"{m['body_density']} over volume {m['body_top'] - m['body_bottom']:.4f} minus "
                    f"{m['cavity_vol']}), while the hull still displaces its full submerged volume."
                )
            else:
                cavity_txt = "The body is a plain solid with no interior cavity."
        else:
            cavity_txt = "The body is a sealed solid with no interior cavity."
        lines = [
            "A tapered prismatic body floats upright in a stack of immiscible fluids.",
            f"Fluid layers have upper boundaries at y = {m['layers']} (height units) "
            f"with densities {m['densities']}.",
            f"The body's tapered cross-section spans from the bottom radius {m['radius_bottom']} "
            f"to the top radius {m['radius_top']} over height {m['body_top'] - m['body_bottom']:.4f}, "
            f"sitting with its base between y = {m['body_bottom']} and y = {m['body_top']}.",
            f"It has solid density {m['body_density']}, plus a ballast of {m['ballast']} added mass. "
            f"{cavity_txt}",
            "The body floats if net buoyant force can balance its weight at some waterline; "
            "otherwise it sinks.",
            "Consider the candidate waterlines at each layer boundary it crosses and the interior "
            "midpoint of the body. Return the index of the stable equilibrium layer (0-based, smallest "
            "stable candidate), or the word 'sinks' if no waterline gives a stable float.",
        ]
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if isinstance(answer, str):
            answer = answer.strip().lower()
        gold = gold.strip().lower()
        return 1.0 if answer == gold else 0.0

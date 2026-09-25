import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


@dataclass
class NestedMembraneEvolutionConfig(Config):
    n_compartments: int = 3
    max_rounds: int = 2
    max_tokens: int = 3
    max_span: int = 3

    def apply_difficulty(self, level):
        self.n_compartments = _clamp(2 + level, 2, 6)
        self.max_rounds = _clamp(2 + level, 2, 5)
        self.max_tokens = _clamp(2 + level // 2, 2, 5)
        self.max_span = _clamp(2 + level, 2, 6)


class NestedMembraneEvolution(Task):
    summary = ("Evolve nested compartments through simultaneous token consumption, inward or outward "
               "transport, division, and deferred dissolution under stated rule priorities; determine "
               "compartment contents after successive rounds.")
    config_cls = NestedMembraneEvolutionConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_compartments
        initial = [random.randint(0, cfg.max_tokens * 2) for _ in range(n)]

        transport_in = [random.random() < 0.4 for _ in range(n - 1)]
        transport_out = [random.random() < 0.4 for _ in range(n - 1)]
        division = [random.random() < 0.2 for _ in range(n)]
        dissolve = [random.random() < 0.25 for _ in range(n)]
        r = random.randint(1, cfg.max_rounds)

        state = list(initial)

        def simulate():
            cur = list(state)
            draft = [False] * n
            for _ in range(r):
                draft = [False] * n
                # (1) dissolution: compartments at floor set to zero
                for i in range(n):
                    if cur[i] == 0 and dissolve[i]:
                        cur[i] = 0
                # (2) outward transports: inner -> outer
                for i in range(n - 1):
                    if not transport_out[i]:
                        continue
                    amt = min(cur[i + 1], cur[i])
                    cur[i + 1] -= amt
                    cur[i] += amt
                # (3) inward transports: outer -> inner
                for i in range(n - 1):
                    if not transport_in[i]:
                        continue
                    amt = min(cur[i], cur[i + 1])
                    cur[i] -= amt
                    cur[i + 1] += amt
                # (4) division: double bounded
                for i in range(n):
                    if division[i]:
                        cur[i] = min(cfg.max_tokens * 2, cur[i] * 2)
                # (5) simultaneous consumption
                for i in range(n):
                    if cur[i] > 0:
                        cur[i] -= 1
            return cur

        result = simulate()

        prompt = _render(cfg, n, initial, transport_in, transport_out,
                         division, dissolve, r)

        return Entry(
            metadata={
                "initial": initial,
                "transport_in": transport_in,
                "transport_out": transport_out,
                "division": division,
                "dissolve": dissolve,
                "rounds": r,
                "max_tokens": cfg.max_tokens,
                "result": result,
            },
            answer=str(result),
        )

    def render_prompt(self, metadata):
        _ = self
        return _render_r(metadata)

    def score_answer(self, answer, entry):
        result = entry["metadata"]["result"]
        try:
            parsed = _parse_list(answer)
        except Exception:
            return 0.0
        if parsed == result:
            return 1.0
        return 0.0


def _parse_list(s):
    s = s.strip().strip("[]")
    if not s:
        return []
    return [int(x.strip()) for x in s.split(",")]


def _render(cfg, n, initial, tin, tout, div, dis, r):
    comps = ", ".join(f"c{i}" for i in range(n))
    lines = [
        f"Nested compartments {comps} (c0 outermost) hold initial token counts "
        f"{initial}."
    ]
    if any(tin) or any(tout):
        spec = []
        for i in range(n - 1):
            if tin[i]:
                spec.append(f"{i}->{i+1} inward (min of the two moves inward)")
            if tout[i]:
                spec.append(f"{i+1}->{i} outward (min of the two moves outward)")
        lines.append("Active transports (applied in the order stated): " + "; ".join(spec) + ".")
    div_list = [i for i in range(n) if div[i]]
    if div_list:
        lines.append("Division compartments (contents double, capped at "
                     + str(cfg.max_tokens * 2) + "): " + str(div_list) + ".")
    dis_list = [i for i in range(n) if dis[i]]
    if dis_list:
        lines.append("Deferred-dissolution compartments (contents vanish when they reach 0 this "
                     "round): " + str(dis_list) + ".")
    lines.append(
        f"Run {max(1, r)} round(s). Each round, in order: (1) dissolution set-to-zero, "
        "(2) outward transports, (3) inward transports, (4) division, (5) consumption of 1 token "
        "from every compartment holding at least 1. Report final token counts as a list "
        "[c0, c1, ...]."
    )
    return "\n".join(lines)


def _render_r(md):
    n = len(md["initial"])
    comps = ", ".join(f"c{i}" for i in range(n))
    lines = [
        f"Nested compartments {comps} (c0 outermost) hold initial token counts "
        f"{md['initial']}."
    ]
    tin = md["transport_in"]
    tout = md["transport_out"]
    if any(tin) or any(tout):
        spec = []
        for i in range(n - 1):
            if tin[i]:
                spec.append(f"{i}->{i+1} inward (min of the two moves inward)")
            if tout[i]:
                spec.append(f"{i+1}->{i} outward (min of the two moves outward)")
        lines.append("Active transports (applied in the order stated): " + "; ".join(spec) + ".")
    div = [i for i in range(n) if md["division"][i]]
    if div:
        lines.append("Division compartments (contents double, capped at "
                     + str(md["max_tokens"] * 2) + "): " + str(div) + ".")
    dis = [i for i in range(n) if md["dissolve"][i]]
    if dis:
        lines.append("Deferred-dissolution compartments (contents vanish when they reach 0 this "
                     "round): " + str(dis) + ".")
    lines.append(
        f"Run {max(1, md['rounds'])} round(s). Each round, in order: (1) dissolution set-to-zero, "
        "(2) outward transports, (3) inward transports, (4) division, (5) consumption of 1 token "
        "from every compartment holding at least 1. Report final token counts as a list "
        "[c0, c1, ...]."
    )
    return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'nested_membrane_evolution (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_relational_structures_r4/nested_membrane_evolution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1140349348,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

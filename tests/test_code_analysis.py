import random

from reasoning_core.tasks.code_analysis import CodeAnalysis, CodeAnalysisConfig


class _NeedChoice(Exception):
    def __init__(self, options):
        self.options = list(options)


def _value_from_domain(value):
    if value in {"True", "False"}:
        return value == "True"
    if value.isdigit():
        return int(value)
    return value


def _value_to_domain(value):
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _execute_step_outcomes(src, vars_, state):
    outcomes = set()
    pending_paths = [()]
    original_choice = random.choice
    try:
        while pending_paths:
            path = pending_paths.pop()
            ns = {}
            exec(src, ns, ns)
            for i, (name, domain) in enumerate(vars_):
                ns[name] = _value_from_domain(domain[state[i]])

            choice_index = {"i": 0}

            def choice(options):
                i = choice_index["i"]
                choice_index["i"] += 1
                if i < len(path):
                    return path[i]
                raise _NeedChoice(options)

            ns["random"].choice = choice
            try:
                ns["step"]()
            except _NeedChoice as e:
                pending_paths.extend(path + (option,) for option in e.options)
                continue

            outcomes.add(
                tuple(domain.index(_value_to_domain(ns[name])) for name, domain in vars_)
            )
    finally:
        random.choice = original_choice
    return outcomes


def test_rendered_program_matches_kripke_transitions():
    state = random.getstate()
    random.seed(0)
    try:
        cfg = CodeAnalysisConfig(n_vars=4, n_modes=4, domain_size=3, max_states=128)
        task = CodeAnalysis(config=cfg)
        motifs = set()

        for _ in range(160):
            k = task._make_kripke()
            motifs.add(k.program.motif)
            src = task._render_program(k)

            for sid in range(len(k.states)):
                expected = {k.states[j] for j in k.succ[sid]}
                got = _execute_step_outcomes(src, k.vars, k.states[sid])
                assert got == expected, (k.program.motif, sid, expected, got)

        assert {"workflow", "cooldown", "retry_fail", "lock", "buffer", "alarm", "coupled_flag"} <= motifs
    finally:
        random.setstate(state)

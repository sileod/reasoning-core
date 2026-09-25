import random

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'sandpile_recurrence_membership (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_latent_structure_reconstruction_r4/sandpile_recurrence_membership',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Present configurations with varying sink boundary strengths and require checking that every nonempty cluster can be reduced to zero by toppling, with the answer being a canonical yes/no string."


class SandpileRecurrenceMembershipV2Config(Config):
    sites: int = 4
    max_mult: int = 2

    def apply_difficulty(self, level):
        self.sites = 4 + level
        self.max_mult = 2 + (level >= 3)


class SandpileRecurrenceMembership(Task):
    summary = "Use local grain counts, edge multiplicities, and sink connections to distinguish stable configurations that belong to the recurrent addition-and-relaxation regime from configurations that are transient."
    config_cls = SandpileRecurrenceMembershipV2Config

    def generate_entry(self):
        n = max(3, self.config.sites)
        max_mult = max(1, self.config.max_mult)

        recurrent = random.random() < 0.5
        for _ in range(400):
            m = [random.randint(1, max_mult) for _ in range(n - 1)]
            s = [random.randint(1, max_mult) for _ in range(n)]
            deg = _degrees(n, m, s)
            if recurrent:
                grains = _make_recurrent(n, deg)
            else:
                grains = _make_transient(n, deg)
            if _is_recurrent(n, m, s, deg, grains) == recurrent:
                answer = "recurrent" if recurrent else "transient"
                return Entry(metadata={"grains": grains, "m": m, "s": s,
                                       "recurrent": recurrent}, answer=answer)
        raise RuntimeError("could not build a valid sandpile instance")

    def render_prompt(self, metadata):
        grains = metadata["grains"]
        m = metadata["m"]
        s = metadata["s"]
        body = ", ".join(str(v) for v in grains)
        edge = ", ".join(str(v) for v in m)
        snk = ", ".join(str(v) for v in s)
        return (
            "A sandpile runs on a line of chain-link sites. Between adjacent "
            f"sites i and i+1 there are edge multiplicities [{edge}], and each "
            f"site is wired to an absorbing sink by sink connections [{snk}], "
            "so a site topples whenever its grain count reaches the sum of the "
            "multiplicities of its edges plus its sink connection, sending one "
            "grain along each edge. A configuration is stable when no site "
            "would topple. Starting from any configuration, adding grains and "
            "relaxing by toppling reaches either a recurrent configuration (one "
            f"that can recur) or a transient one. The site grain counts are "
            f"[{body}]. Decide whether this stable configuration is in the "
            "recurrent regime or the transient regime, by working out whether "
            "every nonempty cluster can be reduced to zero by toppling. "
            "The answer is a single word, either recurrent or transient; "
            "write nothing else."
        )

    def score_answer(self, answer, entry):
        expected = entry.answer
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip().lower()
        if a not in ("recurrent", "transient"):
            return 0.0
        return 1.0 if a == expected else 0.0


def _degrees(n, m, s):
    deg = list(s)
    for i in range(n):
        if i > 0:
            deg[i] += m[i - 1]
        if i < n - 1:
            deg[i] += m[i]
    return deg


def _make_recurrent(n, deg):
    return [random.randint(deg[i] // 2, deg[i] - 1) for i in range(n)]


def _make_transient(n, deg):
    start = random.randrange(n)
    length = random.randint(1, n)
    grains = [random.randint(0, deg[i] - 1) for i in range(n)]
    for k in range(length):
        idx = (start + k) % n
        grains[idx] = 0
    return grains


def _is_recurrent(n, m, s, deg, grains):
    burned = [False] * n
    progress = True
    while progress:
        progress = False
        for i in range(n):
            if burned[i]:
                continue
            edges_to_burned = s[i]
            if i > 0 and burned[i - 1]:
                edges_to_burned += m[i - 1]
            if i < n - 1 and burned[i + 1]:
                edges_to_burned += m[i]
            if grains[i] >= deg[i] - edges_to_burned:
                burned[i] = True
                progress = True
    return all(burned)




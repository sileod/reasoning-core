import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

_CLITICS = {
    "me": (1, "obl"),
    "nos": (1, "obl"),
    "te": (2, "obl"),
    "vos": (2, "obl"),
    "le": (3, "dat"),
    "les": (3, "dat"),
    "la": (3, "acc"),
    "lo": (3, "acc"),
}
_CASE_ORDER = {"obl": 0, "dat": 1, "acc": 2}

_ADVERBS = ["ainda", "sempre", "j\u00e1", "hoje", "ontem"]
_FINITE = ["vejo", "compro", "trago", "fa\u00e7o", "escrevo", "entrego"]
_RESTRUCT = ["quer", "pode", "precisa", "deve", "querer"]
_INFINITIVE = ["dar", "comprar", "escrever", "fazer", "trazer", "entregar"]
_SUBJECTS = ["o jo\u00e3o", "a maria", "ela", "ele"]


def order_cluster(clitics):
    return "-".join(
        sorted(clitics, key=lambda c: (_CLITICS[c][0], _CASE_ORDER[_CLITICS[c][1]], c))
    )


def normalize_answer(answer):
    if not isinstance(answer, str):
        return ""
    return " ".join(answer.split())


@dataclass
class CliticClusterConfig(Config):
    clitic_min: int = 2
    clitic_max: int = 2
    include_restructuring: bool = True

    def apply_difficulty(self, level):
        self.clitic_min = 2 + int(level >= 2) + int(level >= 5)
        self.clitic_max = 2 + int(level >= 2) + int(level >= 4)


class CliticClusterPlacement(Task):
    summary = (
        "Template-order a clitic cluster by person and case hierarchies, then place it "
        "at second position, on the finite verb, or raised past restructuring verbs; "
        "answers give the ordered cluster string and its clausal host."
    )
    design_choice = (
        "Vary the clitic cluster length (2-4 clitics) and require the answer to include "
        "the full ordered cluster plus the host verb's surface form."
    )
    task_version = 2
    config_cls = CliticClusterConfig

    def generate_entry(self):
        size = random.randint(self.config.clitic_min, self.config.clitic_max)
        clitics = random.sample(list(_CLITICS.keys()), size)
        cluster = order_cluster(clitics)
        mode = random.choice(["second", "finite", "raised"])
        subject = random.choice(_SUBJECTS)

        if mode == "second":
            adverb = random.choice(_ADVERBS)
            verb = random.choice(_FINITE)
            host = verb
            extra = {"adverb": adverb, "verb": verb}
        elif mode == "finite":
            verb = random.choice(_FINITE)
            host = verb
            extra = {"verb": verb}
        else:
            matrix = random.choice(_RESTRUCT)
            inf = random.choice(_INFINITIVE)
            host = matrix
            extra = {"matrix": matrix, "inf": inf}

        answer = f"{cluster}|{host}"

        assert answer == f"{order_cluster(clitics)}|{host}"
        cluster_part = answer.split("|")[0]
        assert order_cluster(cluster_part.split("-")) == cluster_part
        assert host in _FINITE or host in _RESTRUCT

        return Entry(
            metadata={"clitics": clitics, "cluster": cluster, "mode": mode,
                      "host": host, "subject": subject, **extra},
            answer=answer,
        )

    def render_prompt(self, metadata):
        order_rule = (
            "Clitic cluster order: 1st person before 2nd before 3rd; within a person, "
            "oblique/dative before accusative; ties break alphabetically. So the fixed "
            "order is: me < nos < te < vos < le < les < la < lo."
        )
        clitics = ", ".join(metadata["clitics"])
        fmt = "Answer as `cluster|host`, e.g. `me-le|compro`."
        mode = metadata["mode"]
        if mode == "second":
            body = (
                f"A clause fronts the adverb \"{metadata['adverb']}\". The clitic cluster "
                f"is placed in second position, right after the adverb, attaching to the "
                f"finite verb that follows it, \"{metadata['verb']}\". Clitics: {clitics}."
            )
        elif mode == "finite":
            body = (
                f"No constituent is fronted. The clitic cluster is placed immediately "
                f"before the finite verb \"{metadata['verb']}\". Clitics: {clitics}."
            )
        else:
            body = (
                f"{metadata['subject']} {metadata['matrix']} {metadata['inf']}. The "
                f"restructuring verb \"{metadata['matrix']}\" takes the infinitive "
                f"\"{metadata['inf']}\"; the clitic cluster is raised to attach to the "
                f"matrix finite verb \"{metadata['matrix']}\" rather than the embedded "
                f"infinitive. Clitics: {clitics}."
            )
        return f"{order_rule}\n\n{body}\n\n{fmt}"

    def score_answer(self, answer, entry):
        ref = entry["answer"]
        return 1.0 if normalize_answer(answer) == normalize_answer(ref) else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'clitic_cluster_placement (draw 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_parsing_and_agreement_r1/clitic_cluster_placement',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

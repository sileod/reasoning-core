import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'de_re_de_dicto_evaluation (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scope_and_binding_r1/de_re_de_dicto_evaluation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


DESIGN_CHOICE = ("Answer format: per-reading verdicts as a canonical string of two letters, "
                 "e.g., 'TR' for de re true / de dicto false, with balanced distribution across "
                 "the four possible pairs.")


NAMES = ["Alice", "Bob", "Carla", "Dan", "Elena", "Faye", "Greg", "Hana",
         "Ivan", "June", "Kai", "Lena", "Mina", "Niko", "Omar", "Pia"]
ROLES = ["chef", "pilot", "doctor", "lawyer", "teacher", "artist", "farmer",
         "nurse", "engineer", "writer", "barber", "guard", "baker", "coach"]


def _pick_role():
    return random.choice(ROLES)


@dataclass
class DeReDeDictoConfig(Config):
    table_size: int = 6

    def apply_difficulty(self, level):
        self.table_size = 6 + level


class DeReDeDictoEvaluation(Task):
    summary = ("Evaluate belief reports over a listed world table, resolving de re readings "
               "(keyed to the actual referent) against de dicto readings (keyed to the agent's "
               "description), with quantifying-in cases; answers are per-reading verdicts.")
    design_choice = DESIGN_CHOICE
    config_cls = DeReDeDictoConfig

    def generate_entry(self):
        sz = self.config.table_size
        assert sz >= 4

        # description profession and claimed profession
        p = _pick_role()
        # de re verdict: is the actual referent (the person who is Q) the P?
        re_true = random.random() < 0.5
        # keep the world/description consistent: the person who is Q really is P iff re_true
        q = p if re_true else _other_role(p)

        # de dicto verdict: is the description-keyed referent (the person the target
        # takes to be Q) the P?
        dicto_true = random.random() < 0.5

        target = random.choice(NAMES)
        # actual referent (is the Q) and believed referent (target takes to be the Q)
        ract, rbel = random.sample([n for n in NAMES if n != target], 2)

        world = {}
        world[target] = _other_role(p)
        world[ract] = q
        world[rbel] = p if dicto_true else _other_role(p)

        # fill the rest of the world table
        pool = [n for n in NAMES if n not in world]
        random.shuffle(pool)
        for i in range(len(world), sz):
            name = pool[i - len(world)]
            r = _pick_role()
            world[name] = r

        lines = "\n".join(f"{a} -- the {r}" for a, r in sorted(world.items()))

        answer = ("T" if re_true else "F") + ("T" if dicto_true else "F")
        metadata = {
            "world_table": lines,
            "target": target,
            "actual_referent": ract,
            "believed_referent": rbel,
            "description": q,
            "claimed": p,
            "de_re": re_true,
            "de_dicto": dicto_true,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        w = metadata["world_table"]
        t = metadata["target"]
        ract = metadata["actual_referent"]
        rbel = metadata["believed_referent"]
        q = metadata["description"]
        p = metadata["claimed"]
        return (
            "The following is the actual assignment of people to professions (the world):\n"
            f"{w}\n\n"
            f"Belief report: {t} believes that the person who is the {q} is the {p}.\n\n"
            "As it happens, "
            f"{t} has a false belief about who the {q} really is: {t} thinks "
            f"the person who is the {q} is {rbel}, but in actual fact the person who is the "
            f"{q} is {ract}.\n\n"
            "Evaluate the belief report under two readings and answer with exactly two "
            "letters. The first letter is the verdict for the de re reading, in which the "
            f"description 'the person who is the {q}' is resolved to the actual referent "
            f"{ract}; it is T iff that actual person really is the {p}. The second letter is "
            "the verdict for the de dicto reading, in which the report is evaluated as keyed "
            "to the description as the agent holds it (the person the target takes to be the "
            f"description's referent, {rbel}); it is T iff that person is the {p}. "
            "Write T or F for each reading, e.g. 'TF' means de re true and de dicto false. "
            "Give only the two letters."
        )


def _other_role(excluded):
    r = _pick_role()
    guard = 0
    while r == excluded and guard < 40:
        r = _pick_role()
        guard += 1
    return r

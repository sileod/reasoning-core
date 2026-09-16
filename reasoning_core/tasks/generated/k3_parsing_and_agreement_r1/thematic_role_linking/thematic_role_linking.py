"""Thematic role linking: map overt arguments onto a verb's ordered thematic grid.

Assignment P010v1. Design choice: output a compact role sequence for all overt
arguments in canonical order, e.g. 'AGENT THEME LOCATION', with obliques marked
by their preposition in parentheses.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'thematic_role_linking (draw 1 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_parsing_and_agreement_r1/thematic_role_linking',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2409743872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Answer format: output a compact role sequence for all overt arguments in canonical order, e.g., 'AGENT THEME LOCATION', with obliques marked by their preposition in parentheses."

# realization -> ordered overt-argument roles (subject first).
REALIZATIONS = {
    "active": ["AGENT", "THEME"],
    "passive": ["THEME", "AGENT"],
    "dative": ["AGENT", "THEME", "RECIPIENT"],
    "locative": ["AGENT", "THEME", "LOCATION"],
    "causative": ["AGENT", "THEME", "RECIPIENT"],
}

# bare nouns; templates add the definite article.
VERBS = [("gave", "given", "give"), ("sent", "sent", "send"),
         ("tossed", "tossed", "toss"), ("handed", "handed", "hand"),
         ("passed", "passed", "pass")]
THEMES = ["parcel", "letter", "box", "package", "key", "horse", "book",
          "gift", "medal", "rope"]
AGENTS = ["courier", "teacher", "nurse", "driver", "postman", "clerk",
          "guard", "engineer"]
RECIPIENTS = ["mayor", "captain", "doctor", "lawyer", "farmer", "artist",
              "judge", "pilot"]
PLACES = ["station", "market", "office", "harbor", "castle", "garden",
          "school", "bank"]

# per-role oblique prepositions (shown in the answer in parentheses).
PREPS = {"AGENT": ["by"], "RECIPIENT": ["to", "for"],
         "LOCATION": ["in", "on", "at", "under", "behind"],
         "THEME": ["with", "for"]}


@dataclass
class RoleConfig(Config):
    oblique_chance: float = 0.35
    causative_chance: float = 0.08

    def apply_difficulty(self, level):
        self.oblique_chance = min(0.85, 0.35 + 0.07 * level)
        self.causative_chance = min(0.45, 0.08 + 0.05 * level)


class ThematicRoleLinking(Task):
    summary = "Map overt arguments onto a verb's ordered thematic grid across active, passive, dative-shift, locative and causative realizations with oblique-marked and implicit roles; answers give each argument's role or a queried role's filler."
    config_cls = RoleConfig
    task_version = 2

    def generate_entry(self):
        verb_active, verb_past, verb_base = random.choice(VERBS)
        theme = random.choice(THEMES)
        agent = random.choice(AGENTS)
        recipient = random.choice(RECIPIENTS)
        place = random.choice(PLACES)

        realization = random.choice(list(REALIZATIONS.keys()))
        if realization != "causative" and random.random() < self.config.causative_chance:
            realization = "causative"

        roles = list(REALIZATIONS[realization])
        filler = {"AGENT": agent, "THEME": theme, "RECIPIENT": recipient,
                  "LOCATION": place}

        # Oblique demotion. In the passive the AGENT is always the by-phrase
        # (inherently oblique); in the locative the LOCATION is always a
        # prepositional phrase (inherently oblique). All other non-subject
        # roles may optionally be demoted to a prepositional phrase.
        inherently = []
        if realization == "passive":
            inherently = ["AGENT"]
        elif realization == "locative":
            inherently = ["LOCATION"]

        oblique = list(inherently)
        subj_role = roles[0]
        for role in roles[1:]:
            if role in inherently:
                continue
            if random.random() < random.uniform(0.0, self.config.oblique_chance):
                oblique.append(role)

        # Assign a preposition to each oblique role.
        prep_of = {}
        for role in oblique:
            prep_of[role] = random.choice(PREPS[role])

        # Render a phrase for each argument: bare "the N" or, if oblique, a
        # prepositional phrase whose preposition is visible in the surface.
        def phrase(role):
            if role in prep_of:
                return f"{prep_of[role]} the {filler[role]}"
            return f"the {filler[role]}"

        if realization == "active":
            surface = f"The {agent} {verb_active} {phrase('THEME')}"
        elif realization == "passive":
            surface = f"The {theme} was {verb_past} {phrase('AGENT')}"
        elif realization == "dative":
            surface = (f"The {agent} {verb_active} {phrase('RECIPIENT')} "
                       f"{phrase('THEME')}")
        elif realization == "locative":
            surface = (f"The {agent} {verb_active} {phrase('THEME')} "
                       f"{phrase('LOCATION')}")
        else:  # causative
            surface = (f"The {agent} caused {phrase('RECIPIENT')} to "
                       f"{verb_base} {phrase('THEME')}")
        surface = surface.rstrip() + "."

        # Canonical answer sequence: AGENT THEME RECIPIENT LOCATION, with each
        # role present marked by its preposition in parentheses if oblique.
        order = ["AGENT", "THEME", "RECIPIENT", "LOCATION"]
        seq = []
        for role in order:
            if role in roles:
                if role in oblique:
                    seq.append(f"{role} ({prep_of[role]})")
                else:
                    seq.append(role)
        answer = " ".join(seq)

        return Entry(metadata={
            "surface": surface,
            "realization": realization,
            "oblique": oblique,
            "answer_seq": seq,
        }, answer=answer)

    def render_prompt(self, metadata):
        return (f"Consider: \"{metadata['surface']}\"  "
                f"List the thematic role of every overt argument in canonical "
                f"order AGENT THEME RECIPIENT LOCATION, marking an argument "
                f"realized as an oblique phrase with its preposition in "
                f"parentheses (e.g. 'AGENT THEME LOCATION (at)'). "
                f"Answer with the space-separated role sequence.")

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        norm = " ".join(answer.split())
        gold = " ".join(entry.metadata["answer_seq"])
        return 1.0 if norm == gold else 0.0

import json
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround
from reasoning_core.tasks.generated.jev._common import canonical_json, choice_answer, jev_prompt, json_score, noul_answer


AGENTS = ["alice", "bob", "carol"]
LOCATIONS = ["desk", "locker", "archive", "lab"]


@dataclass
class JevEntityBeliefTrackingConfig(Config):
    n_events: int = 5
    n_objects: int = 2

    def apply_difficulty(self, level):
        self.n_events = sround(self.n_events + 1.4 * level)
        self.n_objects = sround(self.n_objects + 0.35 * level)


class JevEntityBeliefTracking(Task):
    summary = "Track world state and agent-specific beliefs across partially witnessed object moves, then answer parallel Jev location and agreement judgments."
    config_cls = JevEntityBeliefTrackingConfig

    def generate_entry(self):
        objects = [f"item_{i+1}" for i in range(max(1, self.config.n_objects))]
        world = {obj: random.choice(LOCATIONS) for obj in objects}
        beliefs = {agent: dict(world) for agent in AGENTS}
        initial = dict(world)
        events = []
        for i in range(max(2, self.config.n_events)):
            obj = random.choice(objects)
            dest = random.choice([x for x in LOCATIONS if x != world[obj]])
            witnesses = random.sample(AGENTS, random.randint(0, len(AGENTS)))
            world[obj] = dest
            for agent in witnesses:
                beliefs[agent][obj] = dest
            events.append({"step": i + 1, "object": obj, "destination": dest, "witnesses": witnesses})
        target_obj = random.choice(objects)
        target_agent = random.choice(AGENTS)
        state = {
            "initial_locations": initial,
            "events": events,
            "belief_rule": "A move always changes the true location. An agent updates that object's believed location only when listed as a witness; otherwise the agent keeps its previous belief.",
            "query_agent": target_agent,
            "query_object": target_obj,
        }
        questions = {
            "world_location": {"type": "choice", "instructions": "Where is query_object actually located after all events?", "criteria": {x: x for x in LOCATIONS}},
            "agent_belief_location": {"type": "choice", "instructions": "Where does query_agent believe query_object is after all events?", "criteria": {x: x for x in LOCATIONS}},
            "belief_matches_world": {"type": "noul", "instructions": "Does query_agent's final belief about query_object match the true final location?"},
        }
        actual = world[target_obj]
        believed = beliefs[target_agent][target_obj]
        answers = {
            "world_location": choice_answer(actual, LOCATIONS),
            "agent_belief_location": choice_answer(believed, LOCATIONS),
            "belief_matches_world": noul_answer(actual == believed),
        }
        return Entry(metadata=edict(state=state, questions=questions), answer=canonical_json(answers))

    def render_prompt(self, m):
        return jev_prompt(m.state, m.questions)

    def score_answer(self, answer, entry):
        return json_score(answer, entry)

    def balancing_key(self, problem):
        return int(json.loads(problem.answer)["belief_matches_world"]["noul"])

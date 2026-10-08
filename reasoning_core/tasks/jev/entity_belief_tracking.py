"""Track world state and agent-specific beliefs across partially witnessed object moves.

Levels add events, objects, and agents; from level 2 a second-order question asks where one agent thinks another
agent believes an object is. Ported from tasksource.jev.procedural.entity_belief_tracking; its level tables stop
at 4.
"""
import random
from dataclasses import dataclass

from reasoning_core.decision import Decision
from reasoning_core.template import Config, Entry, Task, stochastic_rounding as sround

AGENTS = ["alice", "bob", "carol", "dave"]
LOCATIONS = ["desk", "locker", "archive", "lab"]
MORE_LOCATIONS = LOCATIONS + ["shelf", "drawer", "cabinet", "garage", "attic", "basement", "kitchen", "office",
                              "mailroom", "vault", "studio", "workshop"]
N_EVENTS = [3, 5, 8, 11, 15]
N_OBJECTS = [1, 2, 2, 3, 3]
N_AGENTS = [2, 3, 3, 4, 4]
RULE = ("Everyone starts knowing the initial locations. A move always changes the true location. The witnesses of "
        "a move see it and see who else witnessed it. An agent's belief about an object changes only when they "
        "witness a move of it. What an agent thinks another agent believes changes only when the first agent "
        "witnesses a move: it becomes the destination if the other agent witnessed that move too, and stays as it "
        "was otherwise.")


@dataclass
class EntityBeliefTrackingConfig(Config):
    def apply_difficulty(self, level):
        pass  # the generator reads the level


class EntityBeliefTracking(Task):
    summary = "Track where objects are and where each agent believes they are, across partially witnessed moves."
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or EntityBeliefTrackingConfig())

    def generate_entry(self, state_seed=None, question=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, level = random.Random(state_seed), min(self.config.level, 4)
        agents = AGENTS[:N_AGENTS[level]]
        locations = rng.sample(MORE_LOCATIONS, rng.randint(len(LOCATIONS), len(MORE_LOCATIONS)))
        objects = [f"item_{i+1}" for i in range(N_OBJECTS[level])]
        world = {obj: rng.choice(locations) for obj in objects}
        initial = dict(world)
        beliefs = {agent: dict(world) for agent in agents}
        nested = {(a, b): dict(world) for a in agents for b in agents if a != b}  # what a thinks b believes
        events = []
        for i in range(max(2, sround(N_EVENTS[level] * rng.uniform(0.85, 1.15), seed=rng.random()))):
            obj = rng.choice(objects)
            dest = rng.choice([x for x in locations if x != world[obj]])
            witnesses = sorted(rng.sample(agents, rng.randint(0, len(agents))), key=agents.index)
            world[obj] = dest
            for a in witnesses:
                beliefs[a][obj] = dest
                for b in witnesses:
                    if b != a:
                        nested[a, b][obj] = dest
            events.append({"step": i + 1, "object": obj, "destination": dest, "witnesses": witnesses})
        target_obj = rng.choice(objects)
        target_agent = rng.choice(agents)
        other = rng.choice([a for a in agents if a != target_agent])
        state = {"locations": locations, "initial_locations": initial, "events": events, "belief_rule": RULE}
        where = dict.fromkeys(locations)
        actual, believed = world[target_obj], beliefs[target_agent][target_obj]
        questions = {
            "world_location": Decision(actual, criteria=where,
                                       instructions=f"Where is {target_obj} actually located after all events?"),
            "agent_belief_location": Decision(believed, criteria=where, instructions=
                                              f"Where does {target_agent} believe {target_obj} is after all events?"),
            "belief_matches_world": Decision(actual == believed, type="noul", instructions=
                f"After all events, does {target_agent} believe {target_obj} is where it actually is?"),
        }
        if level >= 2:
            questions["nested_belief_location"] = Decision(nested[target_agent, other][target_obj], criteria=where,
                instructions=f"After all events, where does {target_agent} think {other} believes {target_obj} is?")
        qid = question or random.choice(sorted(questions))
        return Entry({"payload": state, "state_seed": state_seed, "question_id": qid}, questions[qid])

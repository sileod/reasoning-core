import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround


AGENT_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Heidi"]
OBJECT_NAMES = ["key", "coin", "ring", "note", "map", "ticket", "button", "card"]
ROOM_NAMES = ["kitchen", "study", "hall", "pantry", "garden", "bedroom", "office"]
CONTAINER_NAMES = [
    "box",
    "drawer",
    "bag",
    "tin",
    "basket",
    "crate",
    "bowl",
    "chest",
    "jar",
    "case",
    "cabinet",
    "vase",
    "tray",
    "bin",
]


@dataclass
class TheoryOfMindConfig(Config):
    n_agents: int = 3
    n_objects: int = 2
    n_rooms: int = 2
    n_containers: int = 4
    length: int = 6
    depth: int = 1
    min_salient: int = 1
    max_tries: int = 500

    p_move: float = 0.42
    p_walk: float = 0.30
    p_peek: float = 0.10
    p_tell: float = 0.18
    p_private_tell: float = 0.70
    p_false_tell: float = 0.50

    def apply_difficulty(self, level):
        self.n_agents = sround(3 + 0.6 * level)
        self.n_objects = sround(2 + 0.35 * level)
        self.n_rooms = sround(2 + 0.25 * level)
        self.n_containers = sround(4 + 0.8 * level)
        self.length = sround(6 + 2.2 * level)
        self.depth = min(3, sround(1 + 0.45 * level))
        self.min_salient = min(3, sround(1 + 0.35 * level))


@dataclass(frozen=True)
class Event:
    kind: str
    args: tuple
    obs: frozenset


def apply_event(event, state, viewer=None):
    if event.kind == "walk":
        agent, _src, dst = event.args
        state[("at", agent)] = dst
    elif event.kind == "move":
        _agent, obj, dst = event.args
        state[("loc", obj)] = dst
    elif event.kind == "peek":
        agent, obj, true_container = event.args
        if viewer == agent:
            state[("loc", obj)] = true_container
    elif event.kind == "tell":
        _speaker, listeners, obj, claim = event.args
        if viewer in set(listeners):
            state[("loc", obj)] = claim
    else:
        raise ValueError(f"unknown event kind: {event.kind}")


def replay(trace, init, chain=()):
    state = dict(init)
    viewer = chain[-1] if chain else None
    required_observers = set(chain)

    for event in trace:
        if required_observers <= event.obs:
            apply_event(event, state, viewer)

    return state


def profile(trace, init, chain, fact):
    return [replay(trace, init, chain[:i])[fact] for i in range(len(chain) + 1)]


def salient(trace, init, chain, fact):
    answer = replay(trace, init, chain)[fact]
    causes = []
    for i in range(len(trace)):
        deleted = trace[:i] + trace[i + 1 :]
        if replay(deleted, init, chain)[fact] != answer:
            causes.append(i)
    return causes


def _normalize(x):
    x = str(x).strip().lower()
    x = x.strip(" \t\n\r.,;:!?\"'")
    if x.startswith("the "):
        x = x[4:]
    return x


def _names(pool, n, stem):
    if n <= len(pool):
        return pool[:n]
    return pool + [f"{stem}{i}" for i in range(len(pool) + 1, n + 1)]


def _join(items):
    items = list(items)
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _state_from_metadata(init):
    state = {}
    for agent, room in init["at"].items():
        state[("at", agent)] = room
    for obj, container in init["loc"].items():
        state[("loc", obj)] = container
    return state


def _state_to_metadata(state, agents, objects):
    return {
        "at": {agent: state[("at", agent)] for agent in agents},
        "loc": {obj: state[("loc", obj)] for obj in objects},
    }


def _event_from_metadata(data):
    args = tuple(tuple(x) if isinstance(x, list) else x for x in data["args"])
    return Event(data["kind"], args, frozenset(data["obs"]))


def _event_to_metadata(event):
    def serializable(x):
        if isinstance(x, tuple):
            return [serializable(y) for y in x]
        return x

    return {
        "kind": event.kind,
        "args": serializable(event.args),
        "obs": sorted(event.obs),
    }


def _question_text(chain, obj):
    chain = tuple(chain)
    if not chain:
        return f"Where is the {obj} really?"
    if len(chain) == 1:
        return f"Where does {chain[0]} think the {obj} is?"

    s = f"{chain[-1]} thinks the {obj} is"
    for agent in reversed(chain[:-1]):
        if agent == chain[0]:
            s = f"{agent} think {s}"
        else:
            s = f"{agent} thinks {s}"
    return f"Where does {s}?"


class TheoryOfMind(Task):
    summary = "Track agent beliefs, locations, and actions for Theory of Mind scenarios."
    config_cls = TheoryOfMindConfig

    def _sample_world(self):
        n_agents = max(1, self.config.n_agents)
        n_objects = max(1, self.config.n_objects)
        n_rooms = max(2, self.config.n_rooms)
        n_containers = max(2 * n_rooms, self.config.n_containers)

        agents = _names(AGENT_NAMES, n_agents, "Agent")
        objects = _names(OBJECT_NAMES, n_objects, "object")
        rooms = _names(ROOM_NAMES, n_rooms, "room")
        containers = _names(CONTAINER_NAMES, n_containers, "container")
        random.shuffle(containers)

        room_of = {container: rooms[i % n_rooms] for i, container in enumerate(containers)}
        state = {}
        for agent in agents:
            state[("at", agent)] = random.choice(rooms)
        for obj in objects:
            state[("loc", obj)] = random.choice(containers)

        return agents, objects, rooms, containers, room_of, state

    def _people_in_room(self, state, agents, room):
        return {agent for agent in agents if state[("at", agent)] == room}

    def _make_walk(self, state, agents, rooms):
        agent = random.choice(agents)
        src = state[("at", agent)]
        dst = random.choice([room for room in rooms if room != src])
        obs = self._people_in_room(state, agents, src) | self._people_in_room(state, agents, dst)
        return Event("walk", (agent, src, dst), frozenset(obs))

    def _make_move(self, state, agents, objects, room_of):
        random_agents = random.sample(agents, len(agents))
        for agent in random_agents:
            room = state[("at", agent)]
            available = [obj for obj in objects if room_of[state[("loc", obj)]] == room]
            if not available:
                continue
            obj = random.choice(available)
            current = state[("loc", obj)]
            targets = [c for c, r in room_of.items() if r == room and c != current]
            if not targets:
                continue
            obs = self._people_in_room(state, agents, room)
            return Event("move", (agent, obj, random.choice(targets)), frozenset(obs))
        return None

    def _make_peek(self, state, agents, objects, room_of):
        random_agents = [
            agent
            for agent in random.sample(agents, len(agents))
            if len(self._people_in_room(state, agents, state[("at", agent)])) == 1
        ]
        for agent in random_agents:
            room = state[("at", agent)]
            visible_objects = [obj for obj in objects if room_of[state[("loc", obj)]] == room]
            if visible_objects:
                obj = random.choice(visible_objects)
                return Event("peek", (agent, obj, state[("loc", obj)]), frozenset({agent}))
        return None

    def _make_tell(self, state, agents, objects, containers):
        speakers = random.sample(agents, len(agents))
        for speaker in speakers:
            room = state[("at", speaker)]
            others = [agent for agent in agents if agent != speaker and state[("at", agent)] == room]
            if not others:
                continue

            obj = random.choice(objects)
            true_container = state[("loc", obj)]
            if random.random() < self.config.p_false_tell and len(containers) > 1:
                claim = random.choice([container for container in containers if container != true_container])
            else:
                claim = true_container

            if random.random() < self.config.p_private_tell:
                listener = random.choice(others)
                listeners = (listener,)
                obs = {speaker, listener}
            else:
                random.shuffle(others)
                n_listeners = random.randint(1, len(others))
                listeners = tuple(sorted(others[:n_listeners], key=agents.index))
                obs = self._people_in_room(state, agents, room)
            return Event("tell", (speaker, listeners, obj, claim), frozenset(obs))
        return None

    def _make_trace(self, init, agents, objects, rooms, containers, room_of):
        state = dict(init)
        trace = []
        weights = {
            "move": self.config.p_move,
            "walk": self.config.p_walk,
            "peek": self.config.p_peek,
            "tell": self.config.p_tell,
        }
        kinds = list(weights)
        kind_weights = [weights[k] for k in kinds]

        makers = {
            "walk": lambda: self._make_walk(state, agents, rooms),
            "move": lambda: self._make_move(state, agents, objects, room_of),
            "peek": lambda: self._make_peek(state, agents, objects, room_of),
            "tell": lambda: self._make_tell(state, agents, objects, containers),
        }

        for _ in range(self.config.length):
            event = None
            for kind in random.choices(kinds, weights=kind_weights, k=8) + ["walk"]:
                event = makers[kind]()
                if event is not None and (not trace or event != trace[-1]):
                    break
                event = None
            if event is None:
                break
            trace.append(event)
            apply_event(event, state, None)

        return trace

    def _last_mentioned_container(self, trace, obj):
        last = None
        for event in trace:
            if event.kind == "move":
                _agent, moved_obj, dst = event.args
                if moved_obj == obj:
                    last = dst
            elif event.kind == "peek":
                _agent, peek_obj, true_container = event.args
                if peek_obj == obj:
                    last = true_container
            elif event.kind == "tell":
                _speaker, _listeners, told_obj, claim = event.args
                if told_obj == obj:
                    last = claim
        return last

    def _choose_question(self, trace, init, agents, objects):
        depth = max(1, min(self.config.depth, len(agents)))
        chains = list(itertools.permutations(agents, depth))
        random.shuffle(chains)
        shuffled_objects = random.sample(objects, len(objects))

        if depth >= 2:
            want_answer_eq_reality = random.random() < 0.5
        else:
            want_answer_eq_reality = random.random() < 0.30

        for chain in chains:
            for obj in shuffled_objects:
                fact = ("loc", obj)
                prof = profile(trace, init, chain, fact)
                hard_causes = salient(trace, init, chain, fact)
                # Events assign absolute locations, so only the last applicable
                # assignment to the queried fact can be individually deletion-salient.
                effective_min_salient = min(self.config.min_salient, 1)
                if len(hard_causes) < effective_min_salient:
                    continue

                if depth >= 2:
                    if prof[-1] == prof[-2]:
                        continue
                    if (prof[-1] == prof[0]) != want_answer_eq_reality:
                        continue
                elif (prof[-1] == prof[0]) != want_answer_eq_reality:
                    continue

                if prof[-1] == self._last_mentioned_container(trace, obj) and random.random() >= 0.20:
                    continue

                return {
                    "chain": chain,
                    "object": obj,
                    "profile": prof,
                    "salient": hard_causes,
                    "answer": prof[-1],
                }
        return None

    def generate_entry(self):
        for _ in range(self.config.max_tries):
            agents, objects, rooms, containers, room_of, init = self._sample_world()
            trace = self._make_trace(init, agents, objects, rooms, containers, room_of)
            question = self._choose_question(trace, init, agents, objects)
            if question is None:
                continue

            metadata = edict(
                {
                    "agents": agents,
                    "objects": objects,
                    "rooms": rooms,
                    "containers": containers,
                    "room_of": room_of,
                    "init": _state_to_metadata(init, agents, objects),
                    "trace": [_event_to_metadata(event) for event in trace],
                    "chain": list(question["chain"]),
                    "object": question["object"],
                    "profile": question["profile"],
                    "salient": question["salient"],
                    "depth": len(question["chain"]),
                    "answer_eq_reality": question["profile"][-1] == question["profile"][0],
                }
            )
            return Entry(metadata=metadata, answer=question["answer"])

        raise RuntimeError("failed to generate a valid theory_of_mind example")

    def _rules_text(self):
        return (
            "Rules: People see what happens in their room. For walking, people in the old or new "
            "room see it. When someone hears a location sentence, the listener believes that "
            "sentence, even if it is wrong. People keep old beliefs about events they did not see. "
            "For nested beliefs, use only events seen by every person in the belief chain."
        )

    def _start_text(self, metadata):
        parts = []
        init = metadata.init
        for agent in metadata.agents:
            parts.append(f"{agent} is in the {init['at'][agent]}.")

        for room in metadata.rooms:
            containers = [c for c in metadata.containers if metadata.room_of[c] == room]
            if containers:
                parts.append(f"The {_join(containers)} are in the {room}.")

        for obj in metadata.objects:
            parts.append(f"The {obj} is in the {init['loc'][obj]}.")
        return " ".join(parts)

    def _event_text(self, event):
        if event.kind == "walk":
            agent, _src, dst = event.args
            return f"{agent} walks to the {dst}."
        if event.kind == "move":
            agent, obj, dst = event.args
            return f"{agent} puts the {obj} in the {dst}."
        if event.kind == "peek":
            agent, obj, true_container = event.args
            return f"Alone, {agent} checks the {obj} and sees it in the {true_container}."
        if event.kind == "tell":
            speaker, listeners, obj, claim = event.args
            return f"{speaker} says to {_join(listeners)}, \"The {obj} is in the {claim}.\""
        raise ValueError(f"unknown event kind: {event.kind}")

    def _story_text(self, metadata):
        trace = [_event_from_metadata(event) for event in metadata.trace]
        return " ".join(self._event_text(event) for event in trace)

    def render_prompt(self, metadata):
        return "\n\n".join(
            [
                self._rules_text(),
                "Start: " + self._start_text(metadata),
                "Story: " + self._story_text(metadata),
                "Question: " + _question_text(metadata.chain, metadata.object),
                "Answer with one container name.",
            ]
        )

    def score_answer(self, answer, entry):
        return float(_normalize(answer) == _normalize(entry.answer))

    def _assert_entry_invariants(self, entry):
        metadata = entry.metadata
        init = _state_from_metadata(metadata.init)
        trace = [_event_from_metadata(event) for event in metadata.trace]
        chain = tuple(metadata.chain)
        fact = ("loc", metadata.object)

        assert self.score_answer(entry.answer, entry) == 1
        assert entry.answer in metadata.containers
        assert replay(trace, init, chain)[fact] == entry.answer
        assert profile(trace, init, chain, fact) == list(metadata.profile)
        assert salient(trace, init, chain, fact) == list(metadata.salient)

        for i in metadata.salient:
            deleted = trace[:i] + trace[i + 1 :]
            assert replay(deleted, init, chain)[fact] != entry.answer

        seen = [event for event in trace if set(chain) <= event.obs]
        assert replay(trace, init, chain) == replay(seen, init, chain)

    def _assert_all_seen_case(self):
        agents = ("Alice", "Bob", "Carol")
        init = {
            ("at", "Alice"): "kitchen",
            ("at", "Bob"): "kitchen",
            ("at", "Carol"): "kitchen",
            ("loc", "key"): "box",
        }
        all_agents = frozenset(agents)
        trace = [
            Event("move", ("Alice", "key", "drawer"), all_agents),
            Event("walk", ("Bob", "kitchen", "study"), all_agents),
            Event("move", ("Carol", "key", "box"), all_agents),
        ]
        actual = replay(trace, init, ())
        for agent in agents:
            assert replay(trace, init, (agent,)) == actual

    def validate(self, n_samples=10, cache=False, refresh=False):
        examples = super().validate(n_samples=n_samples, cache=cache, refresh=refresh)
        self._assert_entry_invariants(self.generate_example())
        for entry in examples[: min(3, len(examples))]:
            self._assert_entry_invariants(entry)
        self._assert_all_seen_case()
        return examples

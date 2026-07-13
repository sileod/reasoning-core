import itertools
import json
import math
import random
import re
from collections import Counter
from dataclasses import dataclass, replace
from functools import cache
from types import MappingProxyType
from typing import Mapping

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround


AGENT_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Heidi"]
OBJECT_NAMES = ["key", "coin", "ring", "note", "map", "ticket", "button", "card"]
CONTAINER_NAMES = [
    "box", "drawer", "bag", "tin", "basket", "crate", "bowl", "chest",
    "jar", "case", "cabinet", "vase", "tray", "bin",
]


@dataclass
class BeliefTrackingConfig(Config):
    modal_depth: int = 1
    critical_event_count: int = 1
    epistemic_traps: int = 0
    distractor_events: int = 0
    temporal_gap: int = 0
    agent_load: int = 3
    object_load: int = 1
    candidate_count: int = 3
    observation_asymmetry: float = 0.10
    target_conflicts: int = 0
    max_tries: int = 200

    def apply_difficulty(self, level):
        t = min(max(level / 5, 0), 1)
        self.modal_depth = sround(1 + 3.0 * t)
        self.critical_event_count = sround(1 + 4.0 * t)
        self.epistemic_traps = sround(0.2 + 2.0 * t)
        self.distractor_events = sround(0.3 + 2.0 * t)
        self.temporal_gap = sround(0.2 + 3.0 * t)
        self.agent_load = sround(3 + 2.0 * t)
        self.object_load = sround(1 + 2.0 * t)
        self.candidate_count = sround(3 + 3.0 * t)
        self.observation_asymmetry = 0.10 + 0.55 * t
        self.target_conflicts = sround(2.0 * t)


@dataclass(frozen=True)
class Percept:
    kind: str
    args: tuple


@dataclass(frozen=True)
class Event:
    truth: Percept
    views: Mapping[tuple[str, ...], Percept | None]
    mode: str
    details: tuple = ()


@dataclass(frozen=True)
class EventSpec:
    kind: str
    actor: str | None = None
    target: str | None = None
    policy: str | None = None
    report_type: str | None = None
    scene: str = ""
    object: str | None = None
    destination: str | None = None
    observers: tuple[str, ...] = ()
    content_source_chain: tuple[str, ...] = ()
    asserted_proposition_chain: tuple[str, ...] = ()
    attribution_update: bool = True
    adoption_policy: str = "attribute_only"
    delivery_observers: tuple[str, ...] = ()
    awareness_chains: tuple[tuple[str, ...], ...] = ()
    false_claim: str | None = None
    claim_options: tuple[str, ...] = ()
    surface_form: str = "explicit_quote"
    role: str = ""


@cache
def valid_chains(agents, depth):
    return tuple(
        chain
        for chain in itertools.product(agents, repeat=depth)
        if all(a != b for a, b in itertools.pairwise(chain))
    )


@cache
def all_chains(agents, max_depth):
    return tuple(chain for depth in range(1, max_depth + 1) for chain in valid_chains(agents, depth))


@cache
def _chain_set(agents, max_depth):
    return frozenset(all_chains(agents, max_depth))


@cache
def _public_chains(agents, max_depth, participants):
    return tuple(
        chain for chain in all_chains(agents, max_depth)
        if all(agent in participants for agent in chain)
    )


def _collapse_adjacent(chain):
    out = []
    for agent in chain:
        if not out or out[-1] != agent:
            out.append(agent)
    return tuple(out)


def _with_views(agents, max_depth, assignments):
    valid = _chain_set(tuple(agents), max_depth)
    views = {}
    for chain, percept in assignments.items():
        chain = _collapse_adjacent(chain)
        if chain in valid:
            views[chain] = percept
    return MappingProxyType(views)


def apply_percept(percept, state):
    if percept.kind == "move":
        obj, destination = percept.args
        state[("loc", obj)] = destination
    elif percept.kind == "claim":
        _speaker, _source_chain, obj, container, _policy = percept.args
        state[("loc", obj)] = container
    elif percept.kind in {"conversation", "failed_message"}:
        pass
    else:
        raise ValueError(f"unknown percept kind: {percept.kind}")


def replay(trace, init, chain=()):
    state = dict(init)
    chain = tuple(chain)
    for event in trace:
        percept = event.truth if not chain else event.views.get(chain)
        if percept is not None:
            apply_percept(percept, state)
    return state


def profile(trace, init, chain, fact):
    return [replay(trace, init, tuple(chain)[:i])[fact] for i in range(len(chain) + 1)]


def fixed_trace_critical_events(trace, init, chain, fact):
    answer = replay(trace, init, chain)[fact]
    return [
        i for i in range(len(trace))
        if replay(trace[:i] + trace[i + 1 :], init, chain)[fact] != answer
    ]


def force_visible(trace, index, chain):
    event = trace[index]
    views = dict(event.views)
    views[tuple(chain)] = event.truth
    changed = replace(event, views=MappingProxyType(views))
    return trace[:index] + [changed] + trace[index + 1 :]


def detect_forced_visibility_traps(trace, init, chain, fact):
    answer = replay(trace, init, chain)[fact]
    critical = set(fixed_trace_critical_events(trace, init, chain, fact))
    return [
        i for i in range(len(trace))
        if i not in critical and replay(force_visible(trace, i, chain), init, chain)[fact] != answer
    ]


def layer_deletion_diagnostic(trace, init, chain, fact):
    answer = replay(trace, init, chain)[fact]
    return [
        i for i in range(len(chain))
        if replay(trace, init, _collapse_adjacent(chain[:i] + chain[i + 1 :]))[fact] != answer
    ]


def _move_views(spec, percept, agents, max_depth):
    observers = spec.observers
    participants = tuple(dict.fromkeys(((spec.actor,) if spec.actor else ()) + observers))
    assignments = {}
    if spec.scene == "public_observation":
        assignments.update({
            chain: percept
            for chain in _public_chains(tuple(agents), max_depth, participants)
        })
    elif spec.scene == "private_observation":
        if spec.actor:
            assignments[(spec.actor,)] = percept
        for observer in observers:
            assignments[(observer,)] = percept
            if spec.actor and observer != spec.actor:
                assignments[(observer, spec.actor)] = percept
    elif spec.scene == "one_way_observation":
        subject, watcher = observers
        if spec.actor:
            assignments[(spec.actor,)] = percept
        assignments[(subject,)] = percept
        assignments[(watcher,)] = percept
        if spec.actor:
            assignments[(subject, spec.actor)] = percept
            assignments[(watcher, spec.actor)] = percept
        assignments[(watcher, subject)] = percept
        if spec.actor:
            assignments[(watcher, subject, spec.actor)] = percept
    elif spec.scene == "missed_observation":
        if spec.actor:
            assignments[(spec.actor,)] = percept
    else:
        raise ValueError(f"unknown move scene: {spec.scene}")
    assignments.update({chain: percept for chain in spec.awareness_chains})
    return _with_views(agents, max_depth, assignments)


def _report_views(spec, percept, agents, max_depth):
    if spec.scene == "failed_message":
        return MappingProxyType({})
    assignments = {}
    proposition_chain = spec.asserted_proposition_chain
    if spec.report_type == "belief_report" and spec.attribution_update:
        assignments[_collapse_adjacent((spec.target,) + proposition_chain)] = percept
    if spec.report_type == "direct_claim" and spec.adoption_policy == "accept":
        assignments[(spec.target,)] = percept
    if spec.report_type == "belief_report" and spec.adoption_policy == "accept":
        assignments[(spec.target,)] = percept
    aware_observers = spec.delivery_observers
    if spec.scene in {"face_to_face", "confirmed_message", "visible_conversation"}:
        aware_observers = tuple(dict.fromkeys((spec.actor,) + aware_observers))
    for observer in aware_observers:
        aware = _collapse_adjacent((observer, spec.target) + proposition_chain)
        assignments[aware] = percept
    if spec.scene == "visible_conversation":
        conversation = Percept("conversation", (spec.actor, spec.target))
        for observer in spec.observers:
            assignments[(observer,)] = conversation
    return _with_views(agents, max_depth, assignments)


def realise_event(spec, trace, init, agents, max_depth):
    if spec.kind == "move":
        percept = Percept("move", (spec.object, spec.destination))
        return Event(percept, _move_views(spec, percept, agents, max_depth), spec.scene)
    if spec.kind == "report":
        if spec.policy == "honest":
            content = replay(trace, init, spec.content_source_chain)[("loc", spec.object)]
        elif spec.policy == "deceptive":
            source = spec.content_source_chain or (spec.actor,)
            believed = replay(trace, init, source)[("loc", spec.object)]
            content = next(
                (claim for claim in spec.claim_options if claim != believed),
                spec.false_claim,
            )
        elif spec.policy == "asserted":
            content = spec.false_claim
        else:
            raise ValueError(f"unknown report policy: {spec.policy}")
        percept = Percept(
            "claim",
            (spec.actor, spec.asserted_proposition_chain, spec.object, content, spec.policy),
        )
        truth_kind = "failed_message" if spec.scene == "failed_message" else "conversation"
        truth = Percept(truth_kind, (spec.actor, spec.target))
        return Event(
            truth, _report_views(spec, percept, agents, max_depth), spec.scene,
            (spec.object, content),
        )
    raise ValueError(f"unknown event spec kind: {spec.kind}")


def materialize(specs, init, agents, max_depth):
    return materialize_suffix([], specs, init, agents, max_depth)


def materialize_suffix(prefix, specs, init, agents, max_depth):
    events = list(prefix)
    for spec in specs:
        events.append(realise_event(spec, events, init, agents, max_depth))
    return events


def _disable_spec(spec):
    if spec.kind == "move":
        return replace(spec, scene="missed_observation")
    return replace(spec, scene="failed_message")


def rematerialized_critical_specs(specs, init, agents, max_depth, chain, fact):
    baseline = materialize(specs, init, agents, max_depth)
    answer = replay(baseline, init, chain)[fact]
    critical = []
    for i in range(len(specs)):
        changed = materialize_suffix(
            baseline[:i], specs[i + 1 :], init, agents, max_depth
        )
        if replay(changed, init, chain)[fact] != answer:
            critical.append(i)
    return critical


def backbone_event_necessity(specs, init, agents, max_depth, chain, fact, backbone):
    baseline = materialize(specs, init, agents, max_depth)
    answer = replay(baseline, init, chain)[fact]
    necessary = []
    for index in backbone:
        changed_specs = list(specs)
        changed_specs[index] = _disable_spec(changed_specs[index])
        changed = materialize_suffix(
            baseline[:index], changed_specs[index:], init, agents, max_depth
        )
        if replay(changed, init, chain)[fact] != answer:
            necessary.append(index)
    return necessary


def full_chain_visibility_interventions(specs, init, agents, max_depth, chain, fact, candidates):
    """Add only an awareness relation; retain the event and every actual observer."""
    baseline = materialize(specs, init, agents, max_depth)
    answer = replay(baseline, init, chain)[fact]
    critical = []
    for index in candidates:
        spec = specs[index]
        if spec.kind != "move":
            continue
        changed_specs = list(specs)
        changed_specs[index] = replace(
            spec, awareness_chains=spec.awareness_chains + (tuple(chain),)
        )
        changed = materialize_suffix(
            baseline[:index], changed_specs[index:], init, agents, max_depth
        )
        if replay(changed, init, chain)[fact] != answer:
            critical.append(index)
    return critical


def _make_visible(spec, observer, chain):
    if spec.kind == "move":
        return replace(
            spec,
            awareness_chains=tuple(dict.fromkeys(
                spec.awareness_chains + ((observer,), tuple(chain))
            )),
        )
    if spec.scene == "failed_message":
        return replace(spec, scene="unconfirmed_message")
    return spec


def rematerialized_trap_specs(specs, init, agents, max_depth, chain, fact, candidates):
    baseline = materialize(specs, init, agents, max_depth)
    answer = replay(baseline, init, chain)[fact]
    observer = chain[-1]
    traps = []
    for index in candidates:
        changed_specs = list(specs)
        changed_specs[index] = _make_visible(changed_specs[index], observer, chain)
        changed = materialize_suffix(
            baseline[:index], changed_specs[index:], init, agents, max_depth
        )
        if replay(changed, init, chain)[fact] != answer:
            traps.append(index)
    return traps


def certified_report_properties(specs, trace, init):
    deceptive, conflicts = [], []
    for index, (spec, event) in enumerate(zip(specs, trace)):
        if spec.kind != "report" or spec.policy != "deceptive":
            continue
        source = spec.content_source_chain or (spec.actor,)
        speaker_belief = replay(trace[:index], init, source)[("loc", spec.object)]
        if event.details[1] == speaker_belief:
            continue
        deceptive.append(index)
        if spec.role != "target_conflict":
            continue
        reported = _collapse_adjacent((spec.target,) + spec.asserted_proposition_chain)
        for later_event in trace[index + 1 :]:
            percept = later_event.views.get(reported)
            if percept is None:
                continue
            if percept.kind == "move" and percept.args[0] == spec.object:
                if percept.args[1] != event.details[1]:
                    conflicts.append(index)
                break
            if percept.kind == "claim" and percept.args[2] == spec.object:
                if percept.args[3] != event.details[1]:
                    conflicts.append(index)
                break
    return deceptive, conflicts


def report_spec_is_sound(spec):
    if spec.kind != "report":
        return True
    if spec.report_type == "direct_claim":
        shape_ok = not spec.asserted_proposition_chain and not spec.attribution_update
    elif spec.report_type == "belief_report":
        shape_ok = bool(spec.asserted_proposition_chain) and spec.attribution_update
    else:
        return False
    surface_ok = spec.surface_form in {"explicit_quote", "indirect_report"}
    if spec.surface_form == "indirect_report" and spec.policy != "honest":
        surface_ok = False
    delivery_ok = spec.scene in {
        "face_to_face", "confirmed_message", "unconfirmed_message",
        "failed_message", "visible_conversation",
    } and not spec.delivery_observers
    return shape_ok and surface_ok and delivery_ok


def expected_views(spec, percept, agents, max_depth):
    """Independent semantic oracle for every required view and percept value."""
    assignments = {}
    if spec.kind == "move":
        actor = (spec.actor,) if spec.actor else ()
        if spec.scene == "public_observation":
            participants = tuple(dict.fromkeys(actor + spec.observers))
            assignments.update(
                (chain, percept)
                for chain in all_chains(tuple(agents), max_depth)
                if all(agent in participants for agent in chain)
            )
        elif spec.scene == "private_observation":
            assignments.update(((agent,), percept) for agent in actor + spec.observers)
            assignments.update(
                ((observer, spec.actor), percept)
                for observer in spec.observers
                if spec.actor and observer != spec.actor
            )
        elif spec.scene == "one_way_observation":
            subject, watcher = spec.observers
            assignments.update(((agent,), percept) for agent in actor + spec.observers)
            if spec.actor:
                assignments[(subject, spec.actor)] = percept
                assignments[(watcher, spec.actor)] = percept
            assignments[(watcher, subject)] = percept
            if spec.actor:
                assignments[(watcher, subject, spec.actor)] = percept
        elif spec.scene == "missed_observation":
            assignments.update(((agent,), percept) for agent in actor)
        else:
            raise ValueError(f"unknown move scene: {spec.scene}")
        assignments.update((chain, percept) for chain in spec.awareness_chains)
        return {
            _collapse_adjacent(chain): value
            for chain, value in assignments.items()
            if _collapse_adjacent(chain) in _chain_set(tuple(agents), max_depth)
        }

    if spec.scene == "failed_message":
        return {}
    proposition_chain = spec.asserted_proposition_chain
    if spec.report_type == "belief_report" and spec.attribution_update:
        assignments[_collapse_adjacent((spec.target,) + proposition_chain)] = percept
    if spec.adoption_policy == "accept":
        assignments[(spec.target,)] = percept
    aware_observers = spec.delivery_observers
    if spec.scene in {"face_to_face", "confirmed_message", "visible_conversation"}:
        aware_observers = tuple(dict.fromkeys((spec.actor,) + aware_observers))
    for observer in aware_observers:
        chain = _collapse_adjacent((observer, spec.target) + proposition_chain)
        assignments[chain] = percept
    if spec.scene == "visible_conversation":
        conversation = Percept("conversation", (spec.actor, spec.target))
        assignments.update(((observer,), conversation) for observer in spec.observers)
    return {
        _collapse_adjacent(chain): value
        for chain, value in assignments.items()
        if _collapse_adjacent(chain) in _chain_set(tuple(agents), max_depth)
    }


def _percept_to_data(percept):
    def encode(value):
        return [encode(item) for item in value] if isinstance(value, tuple) else value

    return None if percept is None else {"kind": percept.kind, "args": encode(percept.args)}


def _percept_from_data(data):
    def decode(value):
        return tuple(decode(item) for item in value) if isinstance(value, list) else value

    return None if data is None else Percept(data["kind"], decode(data["args"]))


def _event_to_metadata(event):
    return {
        "truth": _percept_to_data(event.truth),
        "views": [
            {"chain": list(chain), "percept": _percept_to_data(percept)}
            for chain, percept in event.views.items()
        ],
        "mode": event.mode,
        "details": _percept_to_data(Percept("details", event.details))["args"],
    }


def _event_from_metadata(data):
    details = _percept_from_data({"kind": "details", "args": data.get("details", [])}).args
    return Event(
        _percept_from_data(data["truth"]),
        MappingProxyType({
            tuple(item["chain"]): _percept_from_data(item["percept"])
            for item in data["views"]
        }),
        data["mode"],
        details,
    )


def _spec_to_metadata(spec):
    return {
        "kind": spec.kind,
        "actor": spec.actor,
        "target": spec.target,
        "policy": spec.policy,
        "report_type": spec.report_type,
        "scene": spec.scene,
        "object": spec.object,
        "destination": spec.destination,
        "observers": list(spec.observers),
        "content_source_chain": list(spec.content_source_chain),
        "asserted_proposition_chain": list(spec.asserted_proposition_chain),
        "attribution_update": spec.attribution_update,
        "adoption_policy": spec.adoption_policy,
        "delivery_observers": list(spec.delivery_observers),
        "awareness_chains": [list(chain) for chain in spec.awareness_chains],
        "false_claim": spec.false_claim,
        "claim_options": list(spec.claim_options),
        "surface_form": spec.surface_form,
        "role": spec.role,
    }


def _spec_from_metadata(data):
    return EventSpec(
        kind=data["kind"],
        actor=data["actor"],
        target=data["target"],
        policy=data["policy"],
        report_type=data["report_type"],
        scene=data["scene"],
        object=data["object"],
        destination=data["destination"],
        observers=tuple(data["observers"]),
        content_source_chain=tuple(data["content_source_chain"]),
        asserted_proposition_chain=tuple(data["asserted_proposition_chain"]),
        attribution_update=data["attribution_update"],
        adoption_policy=data["adoption_policy"],
        delivery_observers=tuple(data["delivery_observers"]),
        awareness_chains=tuple(tuple(chain) for chain in data["awareness_chains"]),
        false_claim=data["false_claim"],
        claim_options=tuple(data["claim_options"]),
        surface_form=data["surface_form"],
        role=data["role"],
    )


def _state_to_metadata(state, objects):
    return {"loc": {obj: state[("loc", obj)] for obj in objects}}


def _state_from_metadata(data):
    return {("loc", obj): container for obj, container in data["loc"].items()}


def _question_text(chain, obj):
    if len(chain) == 1:
        return f"Where does {chain[0]} think the {obj} is?"
    inner = f"{chain[-1]} thinks the {obj} is"
    for i, agent in enumerate(reversed(chain[:-1])):
        inner = f"{agent} think {inner}" if i == len(chain) - 2 else f"{agent} thinks {inner}"
    return f"Where does {inner}?"


def _utterance_text(spec, content):
    chain = spec.asserted_proposition_chain
    speaker_is_outer_layer = bool(chain and chain[0] == spec.actor)
    if speaker_is_outer_layer:
        chain = chain[1:]
    inner = f"the {spec.object} is in the {content}"
    for agent in reversed(chain):
        inner = f"{agent} thinks {inner}"
    return f"I think {inner}" if speaker_is_outer_layer else inner


def _attribution_text(spec):
    chain = spec.asserted_proposition_chain
    if chain and chain[0] == spec.actor:
        chain = chain[1:]
    inner = f"the location of the {spec.object}"
    for agent in reversed(chain):
        inner = f"{agent}'s belief about {inner}"
    return f"{spec.actor} believes about {inner}"


def _join(items):
    items = list(dict.fromkeys(items))
    if len(items) < 3:
        return " and ".join(items)
    return ", ".join(items[:-1]) + f", and {items[-1]}"


class BeliefTracking(Task):
    summary = "Track ordered beliefs through observation and communication."
    config_cls = BeliefTrackingConfig

    def _delivery_scene(self):
        return random.choices(
            ("face_to_face", "confirmed_message", "unconfirmed_message"),
            weights=(0.45, 0.25, 0.30),
            k=1,
        )[0]

    def _sample_knobs(self):
        def noisy(value, minimum=0, maximum=None):
            value = max(minimum, value + random.choice((-1, 0, 0, 1)))
            return min(value, maximum) if maximum is not None else value

        modal_depth = noisy(self.config.modal_depth, 1, 4)
        candidate_count = noisy(self.config.candidate_count, 3, len(CONTAINER_NAMES))
        critical_event_count = (
            1
            if modal_depth > 1 and random.random() < 0.5 / candidate_count
            else min(
                modal_depth + 2,
                max(modal_depth, noisy(self.config.critical_event_count, 1, 6)),
            )
        )
        return {
            "modal_depth": modal_depth,
            "critical_event_count": critical_event_count,
            "epistemic_traps": noisy(self.config.epistemic_traps),
            "distractor_events": noisy(self.config.distractor_events),
            "temporal_gap": noisy(self.config.temporal_gap),
            "agent_load": noisy(self.config.agent_load, 3, len(AGENT_NAMES)),
            "object_load": noisy(self.config.object_load, 1, len(OBJECT_NAMES)),
            "candidate_count": candidate_count,
            "observation_asymmetry": min(
                0.9, max(0.05, self.config.observation_asymmetry + random.uniform(-0.08, 0.08))
            ),
            "target_conflicts": noisy(self.config.target_conflicts),
        }

    def _sample_world(self, knobs):
        depth = knobs["modal_depth"]
        extra = max(0, knobs["critical_event_count"] - depth)
        n_agents = max(knobs["agent_load"], min(depth + 1 + bool(extra), len(AGENT_NAMES)))
        agents = random.sample(AGENT_NAMES, n_agents)
        objects = random.sample(OBJECT_NAMES, knobs["object_load"])
        containers = random.sample(CONTAINER_NAMES, knobs["candidate_count"])
        init = {("loc", obj): random.choice(containers) for obj in objects}
        return agents, objects, containers, init

    def _relay_backbone(
        self, agents, obj, containers, init, depth, critical_event_count, asymmetry
    ):
        proof_chain = random.choice(valid_chains(tuple(agents), depth))
        inner = proof_chain[-1]
        common_observation = critical_event_count == 1 and depth > 1
        if common_observation:
            observer = inner
            chain = (inner,)
            initial = init[("loc", obj)]
            destination = random.choice([container for container in containers if container != initial])
            alternatives = [container for container in containers if container != destination]
            first_seen, bridge = random.sample(alternatives, 2)
            actor = proof_chain[0]
            observers = tuple(
                agent for agent in dict.fromkeys(proof_chain[1:]) if agent != actor
            )
            specs = [
                EventSpec(
                    kind="move", actor=actor, scene="public_observation", object=obj,
                    destination=value, observers=observers, role=role,
                )
                for value, role in (
                    (first_seen, "target_setup"),
                    (bridge, "target_bridge"),
                    (destination, "critical"),
                )
            ]
            return specs, proof_chain, destination
        extra_relays = critical_event_count - depth
        outsiders = [agent for agent in agents if agent not in proof_chain]
        observer = random.choice(outsiders) if extra_relays else inner
        chain = (inner,)
        initial = init[("loc", obj)]
        destination = initial if random.random() < 1 / len(containers) else random.choice([
            container for container in containers if container != initial
        ])
        alternatives = [container for container in containers if container != destination]
        mover = random.choice([agent for agent in agents if agent != observer])
        watcher_candidates = [
            agent for agent in agents
            if agent not in proof_chain and agent not in (observer, mover)
        ]
        roll = random.random()
        if roll < 0.25:
            scene, observers = "public_observation", (observer,)
        elif roll < 0.25 + asymmetry / 2 and watcher_candidates:
            watcher = random.choice(watcher_candidates)
            scene, observers = "one_way_observation", (observer, watcher)
        else:
            scene, observers = "private_observation", (observer,)
        specs = []
        first_seen = destination if random.random() < 1 / len(containers) else random.choice(alternatives)
        bridge = random.choice([container for container in alternatives if container != first_seen])
        for setup, role in ((first_seen, "target_setup"), (bridge, "target_bridge")):
            specs.append(EventSpec(
                kind="move", actor=mover, scene=scene, object=obj, destination=setup,
                observers=observers, role=role,
            ))
        specs.append(EventSpec(
            kind="move", actor=mover, scene=scene, object=obj, destination=destination,
            observers=observers, role="critical",
        ))
        speaker = observer
        for hop in range(extra_relays):
            remaining = extra_relays - hop
            listener = inner if remaining == 1 else random.choice([
                agent for agent in agents if agent not in (speaker, inner)
            ])
            specs.append(EventSpec(
                kind="report", actor=speaker, target=listener, policy="honest",
                report_type="direct_claim", scene=self._delivery_scene(), object=obj,
                content_source_chain=(speaker,),
                asserted_proposition_chain=(), adoption_policy="accept",
                attribution_update=False,
                surface_form=(
                    "explicit_quote" if random.random() < 0.5 / len(containers)
                    else "indirect_report"
                ),
                role="critical",
            ))
            speaker = listener
        for listener in reversed(proof_chain[:-1]):
            specs.append(
                EventSpec(
                    kind="report", actor=chain[0], target=listener, policy="honest",
                    report_type="belief_report", scene=self._delivery_scene(), object=obj,
                    content_source_chain=chain,
                    asserted_proposition_chain=chain,
                    surface_form=(
                        "explicit_quote" if random.random() < 0.5 / len(containers)
                        else "indirect_report"
                    ),
                    role="critical",
                )
            )
            chain = (listener,) + chain
        return specs, chain, destination

    def _world_specs(self, knobs, agents, objects, containers, init):
        obj = random.choice(objects)
        backbone, proof_chain, answer = self._relay_backbone(
            agents, obj, containers, init, knobs["modal_depth"],
            knobs["critical_event_count"], knobs["observation_asymmetry"]
        )
        specs = []
        outsiders = [agent for agent in agents if agent not in proof_chain]
        outsider = random.choice(outsiders or [agent for agent in agents if agent != proof_chain[-1]])
        first_destination = answer if random.random() < 1 / len(containers) else random.choice([
            container for container in containers if container != answer
        ])
        specs.append(EventSpec(
            kind="move", actor=outsider, scene="private_observation", object=obj,
            destination=first_destination, role="target_interference",
        ))

        first_report = next(
            (i for i, spec in enumerate(backbone) if spec.kind == "report"),
            len(backbone),
        )
        specs.extend(backbone[:first_report])
        trap_specs = []
        for _ in range(knobs["epistemic_traps"]):
            destination = random.choice([container for container in containers if container != answer])
            trap_specs.append(EventSpec(
                kind="move", actor=outsider, scene="private_observation", object=obj,
                destination=destination, role="trap",
            ))

        reports = backbone[first_report:]
        conflict_slots = Counter(
            random.randrange(len(reports)) for _ in range(knobs["target_conflicts"])
        ) if reports else Counter()
        for report_number, report in enumerate(reports):
            if trap_specs:
                take = (
                    len(trap_specs)
                    if report_number == len(reports) - 1
                    else random.randint(0, len(trap_specs))
                )
                specs.extend(trap_specs[:take])
                trap_specs = trap_specs[take:]
            for _ in range(conflict_slots[report_number]):
                false_claim = random.choice([container for container in containers if container != answer])
                specs.append(replace(
                    report,
                    policy="deceptive",
                    false_claim=false_claim,
                    claim_options=tuple(random.sample(containers, len(containers))),
                    surface_form="explicit_quote",
                    role="target_conflict",
                ))
            specs.append(report)
        specs.extend(trap_specs)

        if not reports:
            observer = proof_chain[0]
            critical_index = next(
                i for i, spec in enumerate(specs) if spec.role == "critical"
            )
            for _ in range(knobs["target_conflicts"]):
                speaker = random.choice([agent for agent in agents if agent != observer])
                false_claim = random.choice([container for container in containers if container != answer])
                specs.insert(critical_index, EventSpec(
                    kind="report", actor=speaker, target=observer, policy="deceptive",
                    report_type="direct_claim", scene=self._delivery_scene(), object=obj,
                    content_source_chain=(speaker,), asserted_proposition_chain=(),
                    attribution_update=False, adoption_policy="accept", false_claim=false_claim,
                    claim_options=tuple(random.sample(containers, len(containers))),
                    surface_form="explicit_quote", role="target_conflict",
                ))
                critical_index += 1

        other_objects = [candidate for candidate in objects if candidate != obj]
        distractors = []
        for _ in range(knobs["distractor_events"]):
            if not other_objects:
                speaker, listener = random.sample(agents, 2)
                distractors.append(EventSpec(
                    kind="report", actor=speaker, target=listener, policy="honest",
                    report_type="belief_report", scene="failed_message", object=obj,
                    content_source_chain=(speaker,),
                    asserted_proposition_chain=(speaker,), role="distractor",
                ))
                continue
            distractor_obj = random.choice(other_objects)
            actor = random.choice(agents)
            observer_pool = [agent for agent in agents if agent != actor]
            observers = random.sample(
                observer_pool, random.randint(1, min(3, len(observer_pool)))
            )
            scene = (
                "private_observation"
                if random.random() < knobs["observation_asymmetry"]
                else "public_observation"
            )
            if scene == "private_observation":
                observers = observers[:1]
            distractors.append(EventSpec(
                kind="move", actor=actor, scene=scene, object=distractor_obj,
                destination=random.choice(containers), observers=tuple(observers),
                role="distractor",
            ))
        for distractor in distractors:
            specs.insert(random.randrange(len(specs) + 1), distractor)

        communication_roll = random.random()
        if communication_roll < knobs["observation_asymmetry"]:
            speaker, listener = random.sample(agents, 2)
            source_chain = (speaker,)
            failed = EventSpec(
                kind="report", actor=speaker, target=listener, policy="honest",
                report_type="belief_report", scene="failed_message", object=obj,
                content_source_chain=source_chain,
                asserted_proposition_chain=source_chain, role="failed_delivery",
            )
            specs.insert(random.randrange(len(specs) + 1), failed)
        elif communication_roll < min(0.95, knobs["observation_asymmetry"] + 0.15):
            speaker, listener, observer = random.sample(agents, 3)
            conversation_obj = random.choice(other_objects or objects)
            visible = EventSpec(
                kind="report", actor=speaker, target=listener, policy="honest",
                report_type="belief_report", scene="visible_conversation", object=conversation_obj,
                content_source_chain=(speaker,), asserted_proposition_chain=(speaker,),
                observers=(observer,),
                surface_form=(
                    "explicit_quote" if random.random() < 0.5 / len(containers)
                    else "indirect_report"
                ),
                role="visible_conversation",
            )
            specs.insert(random.randrange(len(specs) + 1), visible)

        outcome = answer if random.random() < 1 / len(containers) else random.choice([
            container for container in containers if container != answer
        ])
        outcome_spec = EventSpec(
            kind="move",
            actor=None if len(proof_chain) == 1 else outsider,
            scene="missed_observation" if len(proof_chain) == 1 else "private_observation",
            object=obj,
            destination=outcome,
            observers=() if len(proof_chain) == 1 else (proof_chain[-1],),
            role="target_outcome",
        )
        final_critical = max(
            i for i, spec in enumerate(specs) if spec.role == "critical"
        )
        decoy_content = answer if random.random() < 1 / len(containers) else random.choice([
            container for container in containers if container != answer
        ])
        if len(proof_chain) > 1 and specs[final_critical].kind == "report":
            template = specs[final_critical]
            decoy = replace(
                template, scene="failed_message", policy="asserted",
                false_claim=decoy_content, surface_form="explicit_quote", role="chain_decoy",
            )
        else:
            decoy = EventSpec(
                kind="report", actor=outsider, target=proof_chain[0], policy="asserted",
                report_type=("belief_report" if proof_chain[1:] else "direct_claim"),
                scene="failed_message", object=obj,
                asserted_proposition_chain=proof_chain[1:], false_claim=decoy_content,
                attribution_update=bool(proof_chain[1:]),
                adoption_policy=("attribute_only" if proof_chain[1:] else "accept"),
                surface_form="explicit_quote",
                role="chain_decoy",
            )
        specs.insert(final_critical + 1, decoy)
        specs.insert(final_critical + 1, outcome_spec)
        refresh_at = final_critical + 2
        source_chain = (proof_chain[-1],)
        for listener in reversed(proof_chain[1:-1]):
            specs.insert(refresh_at, EventSpec(
                kind="report", actor=source_chain[0], target=listener, policy="honest",
                report_type="belief_report", scene=self._delivery_scene(), object=obj,
                content_source_chain=source_chain,
                asserted_proposition_chain=source_chain,
                surface_form="explicit_quote",
                role="subchain_refresh",
            ))
            source_chain = (listener,) + source_chain
            refresh_at += 1
        for _ in range(knobs["temporal_gap"]):
            if other_objects:
                specs.append(EventSpec(
                    kind="move", actor=None, scene="missed_observation",
                    object=random.choice(other_objects), destination=random.choice(containers),
                    role="temporal_gap",
                ))
            else:
                speaker, listener = random.sample(agents, 2)
                specs.append(EventSpec(
                    kind="report", actor=speaker, target=listener, policy="honest",
                    report_type="belief_report", scene="failed_message", object=obj,
                    content_source_chain=(speaker,),
                    asserted_proposition_chain=(speaker,), role="temporal_gap",
                ))
        return specs, obj, proof_chain

    def _enumerate_candidates(self, specs, trace, init, agents, objects, knobs):
        depth = knobs["modal_depth"]
        candidates = set()
        for spec, event in zip(specs, trace):
            if spec.kind == "report" and spec.scene != "failed_message":
                chain = _collapse_adjacent((spec.target,) + spec.asserted_proposition_chain)
                if len(chain) == depth:
                    candidates.add((chain, spec.object))
            elif spec.kind == "move":
                for event_chain, percept in event.views.items():
                    if len(event_chain) == depth and percept == event.truth:
                        candidates.add((event_chain, spec.object))
        candidates = list(candidates)
        random.shuffle(candidates)
        for chain, obj in candidates:
            fact = ("loc", obj)
            causal = rematerialized_critical_specs(specs, init, agents, knobs["modal_depth"], chain, fact)
            required = knobs["critical_event_count"]
            if len(causal) < required:
                continue
            backbone = [
                i for i, spec in enumerate(specs)
                if spec.role == "critical"
            ]
            necessity = backbone_event_necessity(
                specs, init, agents, knobs["modal_depth"], chain, fact, backbone
            )
            if len(necessity) < required:
                continue
            trap_candidates = [
                i for i, spec in enumerate(specs)
                if i not in causal
            ]
            traps = rematerialized_trap_specs(
                specs, init, agents, knobs["modal_depth"], chain, fact, trap_candidates
            )
            if len(traps) < knobs["epistemic_traps"]:
                continue
            yield chain, obj, causal, necessity, traps

    def _twin(self, specs, init, agents, depth, chain, fact, causal):
        index = causal[0]
        twin_specs = list(specs)
        twin_specs[index] = _disable_spec(twin_specs[index])
        twin_trace = materialize(twin_specs, init, agents, depth)
        return twin_specs, twin_trace, replay(twin_trace, init, chain)[fact], index

    def generate_entry(self):
        for _ in range(self.config.max_tries):
            knobs = self._sample_knobs()
            agents, objects, containers, init = self._sample_world(knobs)
            specs, _target_obj, _proof_chain = self._world_specs(
                knobs, agents, objects, containers, init
            )
            trace = materialize(specs, init, agents, knobs["modal_depth"])
            if not all(report_spec_is_sound(spec) for spec in specs):
                continue
            deceptive, certified_conflicts = certified_report_properties(specs, trace, init)
            requested_deceptions = [
                i for i, spec in enumerate(specs) if spec.policy == "deceptive"
            ]
            if deceptive != requested_deceptions or len(certified_conflicts) != knobs["target_conflicts"]:
                continue
            candidate = next(self._enumerate_candidates(
                specs, trace, init, agents, objects, knobs
            ), None)
            if candidate is None:
                continue
            chain, obj, causal, necessity, traps = candidate
            fact = ("loc", obj)
            answer = replay(trace, init, chain)[fact]
            twin_specs, twin_trace, twin_answer, twin_index = self._twin(
                specs, init, agents, knobs["modal_depth"], chain, fact, causal
            )
            if twin_answer == answer:
                continue
            fixed = fixed_trace_critical_events(trace, init, chain, fact)
            layers = layer_deletion_diagnostic(trace, init, chain, fact)
            visibility_interventions = full_chain_visibility_interventions(
                specs,
                init,
                agents,
                knobs["modal_depth"],
                chain,
                fact,
                [i for i, spec in enumerate(specs) if spec.role == "target_outcome"],
            )
            metadata = edict(
                agents=agents,
                objects=objects,
                containers=containers,
                init=_state_to_metadata(init, objects),
                specs=[_spec_to_metadata(spec) for spec in specs],
                trace=[_event_to_metadata(event) for event in trace],
                chain=list(chain),
                object=obj,
                query_kind="belief",
                knobs=knobs,
                requested_target_conflicts=knobs["target_conflicts"],
                certified_target_conflicts=certified_conflicts,
                certified_deceptive_reports=deceptive,
                critical_events=causal,
                fixed_trace_critical_events=fixed,
                trap_event_indices=traps,
                requested_epistemic_traps=knobs["epistemic_traps"],
                certified_visibility_sensitive_events=traps,
                delivery_mechanisms=dict(Counter(
                    spec.scene for spec in specs if spec.kind == "report"
                )),
                initial_state_semantics="common_knowledge",
                backbone_event_necessity=necessity,
                full_chain_visibility_interventions=visibility_interventions,
                layer_deletion_diagnostic=layers,
                noncritical_nontrap_event_indices=[
                    i for i in range(len(specs)) if i not in set(causal + traps)
                ],
                profile=profile(trace, init, chain, fact),
                twin_specs=[_spec_to_metadata(spec) for spec in twin_specs],
                twin_trace=[_event_to_metadata(event) for event in twin_trace],
                twin_answer=twin_answer,
                twin_intervention_index=twin_index,
                answer_eq_reality=answer == replay(trace, init)[fact],
                temporal_gap=sum(spec.role == "temporal_gap" for spec in specs),
                length=len(trace),
            )
            twin_metadata = edict(dict(metadata))
            twin_metadata.specs = metadata.twin_specs
            twin_metadata.trace = metadata.twin_trace
            metadata.twin_prompt = self.render_prompt(twin_metadata)
            prompt, surface_spans = self._render_with_spans(metadata)
            metadata.surface_spans = surface_spans
            mentions = self._textual_mentions(prompt, containers)
            answer_mentions = [position for position, value in mentions if value == answer]
            metadata.textual_mentions = mentions
            metadata.answer_mention_positions = answer_mentions
            metadata.answer_mention_count = len(answer_mentions)
            metadata.answer_occurrence_contexts = [
                prompt[max(0, position - 40) : position + len(answer) + 40]
                for position in answer_mentions
            ]
            metadata.last_answer_mention_char_distance = (
                prompt.index("\n\nQuestion:") - answer_mentions[-1] if answer_mentions else None
            )
            metadata.baselines = self._baselines(
                specs, trace, init, chain, fact, mentions, prompt, containers,
                surface_spans,
            )
            proper_values = [
                value
                for name, value in metadata.baselines.items()
                if name.startswith("subchain:")
            ]
            metadata.differs_from_all_proper_prefixes_and_suffixes = bool(proper_values) and all(
                value != answer for value in proper_values
            )
            update_index, mechanism = self._final_update(specs, trace, chain, obj)
            metadata.final_chain_update_position = update_index
            metadata.final_chain_update_position_quantile = (
                update_index / max(1, len(trace) - 1) if update_index is not None else None
            )
            metadata.final_update_mechanism = mechanism
            matching_quotes = self._matching_quotes(surface_spans, chain, obj)
            metadata.answer_in_matching_quote = any(
                quote["content"] == answer for quote in matching_quotes
            )
            metadata.final_answer_occurrence_inside_quote = bool(answer_mentions) and any(
                span["quoted"]
                and span["start"] <= answer_mentions[-1] < span["end"]
                for span in surface_spans
            )
            target_values = [
                event.truth.args[1]
                for event in trace
                if event.truth.kind == "move" and event.truth.args[0] == obj
            ] + [
                event.details[1]
                for event in trace
                if event.truth.kind in {"conversation", "failed_message"}
                and event.details[0] == obj
            ]
            value_counts = Counter(target_values)
            entropy = -sum(
                (count / len(target_values)) * math.log2(count / len(target_values))
                for count in value_counts.values()
            )
            metadata.target_event_value_entropy_bits = entropy
            metadata.target_event_value_perplexity = 2**entropy
            reader_rules = (
                "quote:last_delivered_matching",
                "reader:direct_final_update",
                "innermost_belief",
                "target:first_witnessed",
                "target:last_witnessed",
            )
            metadata.defeats_selected_reader_baselines = (
                metadata.differs_from_all_proper_prefixes_and_suffixes and all(
                metadata.baselines.get(name) != answer for name in reader_rules
                )
            )
            metadata.balance_axis = random.choice(
                ["answer", "reality", "initial", "first_text", "last_text"]
            )
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("failed to generate a grounded, certified belief_tracking example")

    def _event_text(self, spec, event):
        if spec.kind == "move":
            actor = spec.actor or f"The {spec.object}"
            move = (
                f"{actor} moves the {spec.object} to the {spec.destination}."
                if spec.actor
                else f"The {spec.object} falls into the {spec.destination}."
            )
            if spec.scene == "public_observation":
                participants = tuple(dict.fromkeys(((spec.actor,) if spec.actor else ()) + spec.observers))
                if len(participants) == 1:
                    return f"{move} {participants[0]} witnesses the move."
                return f"{move} {_join(participants)} watch together and can see one another."
            if spec.scene == "private_observation":
                if spec.observers:
                    return f"{move} Unknown to the others, {spec.observers[0]} watches through a window."
                return move + " No one else sees the move."
            if spec.scene == "one_way_observation":
                subject, watcher = spec.observers
                watched = f"{spec.actor} make the move" if spec.actor else "it happen"
                return (
                    f"{move} {subject} watches {watched}, while {watcher} secretly "
                    f"watches {subject} watching {watched}."
                )
            if spec.scene == "missed_observation" and spec.actor:
                return f"{move} {spec.actor} knows where they put it, but nobody else sees the move."
            return move + " Nobody sees this happen."

        content = event.details[1]
        if spec.surface_form == "explicit_quote":
            utterance = (
                f"The {spec.object} is in the {content}"
                if spec.report_type == "direct_claim"
                else _utterance_text(spec, content)
            )
            payload = f'"{utterance}"'
        elif spec.surface_form == "indirect_report":
            if spec.report_type == "direct_claim":
                payload = f"what {spec.actor} believes about where the {spec.object} is"
            else:
                payload = f"exactly what {_attribution_text(spec)}"
        else:
            raise ValueError(f"unknown report surface: {spec.surface_form}")
        if spec.surface_form == "explicit_quote":
            face_content = f", {payload}"
            message_content = f"the message {payload}"
        else:
            face_content = f" {payload}"
            message_content = f"a message stating {payload}"
        acceptance = ""
        if spec.scene != "failed_message" and spec.adoption_policy == "accept":
            acceptance = f" {spec.target} accepts the stated location."

        if spec.scene == "face_to_face":
            return f"{spec.actor} tells {spec.target} face to face{face_content}.{acceptance}"
        if spec.scene == "confirmed_message":
            return (
                f"{spec.actor} sends {spec.target} {message_content}. "
                f"{spec.target} confirms receipt.{acceptance}"
            )
        if spec.scene == "unconfirmed_message":
            return (
                f"{spec.actor} sends {spec.target} {message_content}. "
                f"{spec.target} receives it, but {spec.actor} receives no delivery confirmation."
                f"{acceptance}"
            )
        if spec.scene == "failed_message":
            return (
                f"{spec.actor} sends {spec.target} {message_content}, "
                "but it is not delivered."
            )
        if spec.scene == "visible_conversation":
            witness_verb = "sees" if len(spec.observers) == 1 else "see"
            return (
                f"{spec.actor} tells {spec.target}{face_content}.{acceptance} "
                f"{_join(spec.observers)} {witness_verb} them talking but cannot hear the words."
            )
        raise ValueError(f"unknown delivery scene: {spec.scene}")

    def _start_text(self, metadata):
        locations = (
            f"the {obj} is in the {metadata.init['loc'][obj]}"
            for obj in metadata.objects
        )
        return f"Initially, everyone knows that {_join(locations)}."

    def _story_text(self, metadata):
        return self._story_render(metadata)[0]

    def _story_render(self, metadata):
        specs = [_spec_from_metadata(data) for data in metadata.specs]
        trace = [_event_from_metadata(data) for data in metadata.trace]
        parts, spans, offset = [], [], 0
        for index, (spec, event) in enumerate(zip(specs, trace)):
            text = self._event_text(spec, event)
            if parts:
                offset += 1
            parts.append(text)
            if spec.kind == "report":
                reported = _collapse_adjacent(
                    (spec.target,) + spec.asserted_proposition_chain
                )
                spans.append({
                    "event_index": index,
                    "start": offset,
                    "end": offset + len(text),
                    "proposition_chain": list(reported),
                    "object": spec.object,
                    "container": (
                        event.details[1]
                        if spec.surface_form == "explicit_quote"
                        else None
                    ),
                    "delivered": spec.scene != "failed_message",
                    "quoted": spec.surface_form == "explicit_quote",
                    "report_type": spec.report_type,
                    "surface_form": spec.surface_form,
                })
            offset += len(text)
        return " ".join(parts), spans

    def _render_with_spans(self, metadata):
        start = self._start_text(metadata)
        story, spans = self._story_render(metadata)
        story_block = "Story: " + story
        question = "Question: " + _question_text(metadata.chain, metadata.object)
        prompt = "\n\n".join([
            start, story_block, question, "Answer with one container name."
        ])
        story_offset = len(start) + 2 + len("Story: ")
        for span in spans:
            span["start"] += story_offset
            span["end"] += story_offset
        return prompt, spans

    def render_prompt(self, metadata):
        return self._render_with_spans(metadata)[0]

    def _textual_mentions(self, prompt, containers):
        mentions = []
        for container in containers:
            mentions.extend((match.start(), container) for match in re.finditer(
                rf"\b{re.escape(container)}\b", prompt, flags=re.IGNORECASE
            ))
        return sorted(mentions)

    def _chain_match_baseline(self, prompt, chain, containers):
        story = prompt.split("Story: ", 1)[1].split("\n\nQuestion:", 1)[0]
        prediction = None
        for sentence in re.split(r'(?<=[."])\s+(?=[A-Z])', story):
            if all(agent in sentence for agent in dict.fromkeys(chain)):
                mentioned = [container for container in containers if re.search(
                    rf"\b{re.escape(container)}\b", sentence, flags=re.IGNORECASE
                )]
                if mentioned:
                    prediction = mentioned[-1]
        return prediction

    def _target_baselines(self, trace, chain, obj):
        moves, visible, claims = [], [], []
        seen_by = {agent: [] for agent in dict.fromkeys(chain)}
        for event in trace:
            if event.truth.kind == "move" and event.truth.args[0] == obj:
                destination = event.truth.args[1]
                moves.append(destination)
                direct = [
                    event_chain[0]
                    for event_chain, percept in event.views.items()
                    if len(event_chain) == 1 and percept == event.truth
                ]
                if direct:
                    visible.append(destination)
                for agent in seen_by:
                    if agent in direct:
                        seen_by[agent].append(destination)
            if event.truth.kind in {"conversation", "failed_message"} and event.details[0] == obj:
                claims.append(event.details[1])
        baselines = {
            "target:first_move": moves[0] if moves else None,
            "target:last_move": moves[-1] if moves else None,
            "target:first_witnessed": visible[0] if visible else None,
            "target:last_witnessed": visible[-1] if visible else None,
            "target:last_claim": claims[-1] if claims else None,
            "target:third_move": moves[2] if len(moves) > 2 else None,
        }
        for position, agent in enumerate(chain):
            destinations = seen_by[agent]
            baselines[f"target:first_seen_at:{position}"] = destinations[0] if destinations else None
            baselines[f"target:last_seen_at:{position}"] = destinations[-1] if destinations else None
        return baselines

    def _matching_quotes(self, spans, chain, obj):
        return [
            {
                "index": span["event_index"],
                "delivered": span["delivered"],
                "content": span["container"],
            }
            for span in spans
            if span["quoted"]
            and span["object"] == obj
            and tuple(span["proposition_chain"]) == tuple(chain)
        ]

    def _quote_baselines(self, spans, chain, obj):
        quotes = self._matching_quotes(spans, chain, obj)
        delivered = [quote for quote in quotes if quote["delivered"]]
        return {
            "quote:first_delivered_matching": delivered[0]["content"] if delivered else None,
            "quote:last_delivered_matching": delivered[-1]["content"] if delivered else None,
            "quote:last_matching_including_failed": quotes[-1]["content"] if quotes else None,
        }

    def _direct_final_update_baseline(self, specs, trace, chain, obj):
        prediction = None
        for spec, event in zip(specs, trace):
            percept = event.views.get(tuple(chain))
            if percept is None:
                continue
            if percept.kind == "move" and percept.args[0] == obj:
                prediction = percept.args[1]
            elif percept.kind == "claim" and percept.args[2] == obj:
                prediction = (
                    percept.args[3]
                    if spec.surface_form == "explicit_quote"
                    else None
                )
        return prediction

    def _final_update(self, specs, trace, chain, obj):
        final = (None, "initial_common_knowledge")
        for index, (spec, event) in enumerate(zip(specs, trace)):
            percept = event.views.get(tuple(chain))
            if percept is None:
                continue
            if percept.kind == "claim" and percept.args[2] == obj:
                final = (
                    index,
                    "delivered_report_explicit"
                    if spec.surface_form == "explicit_quote"
                    else "delivered_report_indirect",
                )
            elif percept.kind == "move" and percept.args[0] == obj:
                final = (
                    index,
                    "joint_observation" if event.mode == "public_observation" else event.mode,
                )
        return final

    def _final_answer_in_quote(self, prompt, answer):
        positions = [match.start() for match in re.finditer(rf"\b{re.escape(answer)}\b", prompt)]
        if not positions:
            return False
        position = positions[-1]
        return prompt[:position].count('"') % 2 == 1

    def _baselines(
        self, specs, trace, init, chain, fact, mentions, prompt, containers, spans
    ):
        values = [value for _position, value in mentions]
        counts = Counter(values)
        most_frequent = min(counts, key=lambda value: (-counts[value], values.index(value)))
        baselines = {
            "initial": init[fact],
            "reality": replay(trace, init)[fact],
            "first_text": values[0],
            "last_text": values[-1],
            "most_frequent_text": most_frequent,
            "chain_match": self._chain_match_baseline(prompt, chain, containers),
        }
        if len(chain) > 1:
            baselines["innermost_belief"] = replay(trace, init, (chain[-1],))[fact]
            for i in range(1, len(chain)):
                baselines[f"subchain:prefix:{i}"] = replay(trace, init, chain[:i])[fact]
                baselines[f"subchain:suffix:{i}"] = replay(trace, init, chain[i:])[fact]
        baselines.update(self._target_baselines(trace, chain, fact[1]))
        baselines.update(self._quote_baselines(spans, chain, fact[1]))
        direct = self._direct_final_update_baseline(
            specs, trace, chain, fact[1]
        )
        baselines["reader:direct_final_update"] = direct
        return baselines

    def score_answer(self, answer, entry):
        normalized = str(answer).strip().lower().strip(" \t\n\r.,;:!?\"'")
        if normalized.startswith("the "):
            normalized = normalized[4:]
        return float(normalized == str(entry.answer).lower())

    def balancing_key(self, problem):
        axis = problem.metadata.balance_axis
        if axis == "answer":
            value = problem.answer
        else:
            value = problem.metadata.baselines[axis] == problem.answer
        return f"{axis}:{value}"

    def shortcut_report(self, examples):
        report = {}
        for depth in sorted({len(entry.metadata.chain) for entry in examples}):
            bucket = [entry for entry in examples if len(entry.metadata.chain) == depth]
            chance = sum(1 / len(entry.metadata.containers) for entry in bucket) / len(bucket)
            names = sorted({name for entry in bucket for name in entry.metadata.baselines})
            for name in names:
                applicable = [
                    entry for entry in bucket
                    if entry.metadata.baselines.get(name) is not None
                ]
                hits = sum(
                    entry.metadata.baselines[name] == entry.answer for entry in applicable
                )
                coverage = len(applicable) / len(bucket)
                conditional = hits / len(applicable) if applicable else None
                overall = (hits + (len(bucket) - len(applicable)) * chance) / len(bucket)
                report[f"depth:{depth}:{name}"] = {
                    "coverage": coverage,
                    "conditional_accuracy": conditional,
                    "overall_accuracy_with_defined_fallback": overall,
                    "chance": chance,
                    "advantage": overall - chance,
                    "n": len(bucket),
                    "defined_n": len(applicable),
                }
            counts = Counter(entry.answer for entry in bucket)
            accuracy = max(counts.values()) / len(bucket)
            report[f"depth:{depth}:majority_answer"] = {
                "coverage": 1.0,
                "conditional_accuracy": accuracy,
                "overall_accuracy_with_defined_fallback": accuracy,
                "chance": chance,
                "advantage": accuracy - chance,
                "n": len(bucket),
                "defined_n": len(bucket),
            }
        return report

    def generate_balanced_batch(
        self, batch_size=32, deduplication=False, progress=False, workers=1,
        max_advantage=0.15, max_rounds=3, **kwargs
    ):
        """Select a batch and reject it unless every measured shortcut is near chance."""
        for _round in range(max_rounds):
            pool = [self.generate_example(**kwargs) for _ in range(max(batch_size + 4, 12))]
            selected, hits, defined, depth_counts, seen = [], Counter(), Counter(), Counter(), set()
            while len(selected) < batch_size:

                def cost(entry):
                    key_prefix = len(entry.metadata.chain)
                    chance = 1 / len(entry.metadata.containers)
                    baseline_cost = sum(
                        abs(
                            hits[(key_prefix, name)]
                            + (value == entry.answer)
                            - chance * (defined[(key_prefix, name)] + 1)
                        )
                        for name, value in entry.metadata.baselines.items()
                        if value is not None
                    )
                    answer_cost = abs(
                        hits[(key_prefix, f"answer:{entry.answer}")] + 1
                        - chance * (depth_counts[key_prefix] + 1)
                    )
                    return baseline_cost + answer_cost

                candidate_indices = [
                    i for i, entry in enumerate(pool)
                    if not deduplication or self.deduplication_key(entry) not in seen
                ]
                if not candidate_indices:
                    break
                chosen_index = min(candidate_indices, key=lambda i: cost(pool[i]))
                chosen = pool.pop(chosen_index)
                selected.append(chosen)
                seen.add(self.deduplication_key(chosen))
                depth = len(chosen.metadata.chain)
                for name, value in chosen.metadata.baselines.items():
                    if value is not None:
                        defined[(depth, name)] += 1
                        hits[(depth, name)] += value == chosen.answer
                hits[(depth, f"answer:{chosen.answer}")] += 1
                depth_counts[depth] += 1
            if len(selected) == batch_size and all(
                abs(item["advantage"]) <= max_advantage
                for name, item in self.shortcut_report(selected).items()
                if not (
                    name.startswith("depth:1:target:last_seen_at")
                    or name == "depth:1:target:last_witnessed"
                )
                and item["n"] >= 8
            ) and all(
                len({entry.metadata.final_update_mechanism for entry in selected
                     if len(entry.metadata.chain) == depth}) > 1
                for depth in {len(entry.metadata.chain) for entry in selected}
                if sum(len(entry.metadata.chain) == depth for entry in selected) >= 8
            ):
                return selected
        raise RuntimeError("failed shortcut gate; expand the pool or relax max_advantage")

    def deduplication_key(self, problem):
        m = problem.metadata
        spec_agents = []
        for spec in m.specs:
            spec_agents.extend(value for value in (spec["actor"], spec["target"]) if value)
            spec_agents.extend(spec["observers"])
            spec_agents.extend(spec["delivery_observers"])
            spec_agents.extend(spec["content_source_chain"])
            spec_agents.extend(spec["asserted_proposition_chain"])
            spec_agents.extend(agent for chain in spec["awareness_chains"] for agent in chain)
        agent_order = list(dict.fromkeys(list(m.chain) + spec_agents))
        spec_objects = [spec["object"] for spec in m.specs]
        object_order = list(dict.fromkeys([m.object] + spec_objects + list(m.objects)))
        spec_containers = [
            spec["destination"]
            for spec in m.specs
            if spec["kind"] == "move"
        ] + [
            spec["false_claim"]
            for spec in m.specs
            if spec["kind"] == "report" and spec["false_claim"] is not None
        ]
        container_order = list(dict.fromkeys(
            [m.init["loc"][m.object]] + spec_containers
            + [m.init["loc"][obj] for obj in object_order] + list(m.containers)
        ))
        maps = {
            **{value: f"A{i}" for i, value in enumerate(agent_order)},
            **{value: f"O{i}" for i, value in enumerate(object_order)},
            **{value: f"C{i}" for i, value in enumerate(container_order)},
        }

        def canonical(value):
            if isinstance(value, dict):
                return {canonical(key): canonical(item) for key, item in value.items()}
            if isinstance(value, list):
                return [canonical(item) for item in value]
            return maps.get(value, value)

        latent = canonical({
            "chain": m.chain,
            "object": m.object,
            "init": m.init,
            "specs": m.specs,
        })
        return json.dumps(latent, sort_keys=True)

    def _assert_entry_invariants(self, entry):
        m = entry.metadata
        init = _state_from_metadata(m.init)
        specs = [_spec_from_metadata(data) for data in m.specs]
        assert all(report_spec_is_sound(spec) for spec in specs)
        trace = materialize(specs, init, m.agents, m.knobs["modal_depth"])
        chain, fact = tuple(m.chain), ("loc", m.object)
        assert [_event_to_metadata(event) for event in trace] == list(m.trace)
        rendered_prompt, rendered_spans = self._render_with_spans(m)
        assert rendered_spans == list(m.surface_spans)
        assert rendered_prompt == self.render_prompt(m)
        for spec, event in zip(specs, trace):
            percept = event.truth if spec.kind == "move" else Percept(
                "claim",
                (
                    spec.actor,
                    spec.asserted_proposition_chain,
                    spec.object,
                    event.details[1],
                    spec.policy,
                ),
            )
            assert dict(event.views) == expected_views(
                spec, percept, m.agents, m.knobs["modal_depth"]
            )
        assert replay(trace, init, chain)[fact] == entry.answer
        assert rematerialized_critical_specs(
            specs, init, m.agents, m.knobs["modal_depth"], chain, fact
        ) == list(m.critical_events)
        assert len(m.critical_events) == m.knobs["critical_event_count"]
        assert len(m.backbone_event_necessity) == m.knobs["critical_event_count"]
        assert len(m.trap_event_indices) >= m.knobs["epistemic_traps"]
        deceptive, conflicts = certified_report_properties(specs, trace, init)
        assert deceptive == list(m.certified_deceptive_reports)
        assert conflicts == list(m.certified_target_conflicts)
        assert len(conflicts) == m.requested_target_conflicts
        assert len(m.certified_visibility_sensitive_events) >= m.requested_epistemic_traps
        assert not {"nested", "layer_contrast"} & {spec.scene for spec in specs}
        if m.differs_from_all_proper_prefixes_and_suffixes:
            assert m.full_chain_visibility_interventions
        assert "model of" not in self.render_prompt(m).lower()
        assert "viewpoint" not in self.render_prompt(m).lower()
        assert "registers" not in self.render_prompt(m).lower()
        twin = [_event_from_metadata(data) for data in m.twin_trace]
        assert replay(twin, init, chain)[fact] == m.twin_answer != entry.answer
        assert m.twin_prompt != self.render_prompt(m)
        assert all(a != b for a, b in itertools.pairwise(chain))

    def validate(self, n_samples=10, cache=False, refresh=False):
        examples = super().validate(n_samples=n_samples, cache=cache, refresh=refresh)
        for entry in examples[: min(3, len(examples))]:
            self._assert_entry_invariants(entry)
        self._assert_entry_invariants(self.generate_example())
        return examples

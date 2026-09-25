import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

OPERATORS = ["begin", "finish", "start", "stop", "enjoy"]

ENTITIES = {
    "book": [("read", 2.0), ("write", 1.0)],
    "essay": [("write", 3.0), ("read", 1.5)],
    "poem": [("write", 2.5), ("recite", 1.0)],
    "meal": [("cook", 2.5), ("eat", 2.0)],
    "film": [("watch", 2.5), ("direct", 1.0)],
    "play": [("perform", 3.0), ("watch", 1.0)],
    "sculpture": [("sculpt", 3.0), ("view", 1.0)],
    "toy": [("play_with", 2.5), ("make", 1.0)],
    "garden": [("tend", 2.5), ("clean", 1.0)],
    "house": [("build", 2.0), ("clean", 1.5)],
    "puzzle": [("solve", 2.5), ("assemble", 2.0)],
    "symphony": [("compose", 3.0), ("conduct", 1.0)],
    "report": [("write", 3.0), ("read", 1.5), ("review", 1.0)],
    "room": [("paint", 2.0), ("clean", 1.5), ("decorate", 1.0)],
    "article": [("read", 2.0), ("write", 1.5)],
    "song": [("sing", 3.0), ("record", 1.0), ("compose", 1.5)],
    "door": [("paint", 2.0)],
    "piano": [("play", 2.5)],
}
ALL_RELATION_VALUES = {v for rels in ENTITIES.values() for _, v in rels}


def sorted_rels(entity):
    rels = ENTITIES[entity]
    return sorted(rels, key=lambda v: (-v[1], v[0]))


def build_events(operator, inner_operator, entity):
    events = []
    for verb, _s in sorted_rels(entity):
        ev = f"{inner_operator}({verb}({entity}))" if inner_operator else f"{verb}({entity})"
        events.append(f"{operator}({ev})")
    return events


def format_list(events):
    return "[" + ", ".join('"%s"' % ev for ev in events) + "]"


def _lexicon_text():
    lines = []
    for e in sorted(ENTITIES):
        rels_txt = ", ".join(f"{v} {s:g}" for v, s in ENTITIES[e])
        lines.append(f"{e}: {rels_txt}")
    return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'lexical_event_coercion (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_semantics_r4/lexical_event_coercion',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

LEXICON_TEXT = _lexicon_text()


@dataclass
class LexicalEventCoercionV1Config(Config):
    depth: int = 1

    def apply_difficulty(self, level):
        self.depth = 2 if level >= 3 else 1


class LexicalEventCoercion(Task):
    summary = (
        "Resolve entity arguments of event-selecting predicates through stated purpose, "
        "creation, and use relations; compose nested coercions and competing lexical "
        "routes; return the licensed event interpretations."
    )
    design_choice = (
        'Answer as a canonical bracket-enclosed event list, e.g., ["begin(book)", '
        '"read(book)"] when a predicate licenses multiple coercions, with ordering by '
        "stated relation strength."
    )
    config_cls = LexicalEventCoercionV1Config
    task_version = 2

    def generate_entry(self):
        entity = random.choice(sorted(ENTITIES))
        operator = random.choice(OPERATORS)
        inner_operator = None
        if self.config.depth >= 2:
            opts = [o for o in OPERATORS if o != operator]
            inner_operator = random.choice(opts)
        rels = sorted_rels(entity)
        events = build_events(operator, inner_operator, entity)
        answer = format_list(events)
        assert format_list(build_events(operator, inner_operator, entity)) == answer
        return Entry(
            metadata={
                "entity": entity,
                "operator": operator,
                "inner_operator": inner_operator,
                "relations": rels,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        return _render(metadata)

    def score_answer(self, answer, entry=None):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip()
        if entry is None:
            return 0.0
        return 1.0 if a == entry["answer"] else 0.0


def _render(md):
    entity = md["entity"]
    operator = md["operator"]
    inner = md.get("inner_operator")
    if inner:
        query = f"{operator} to {inner} the {entity}"
        methods = (
            f"For the verb chain '{query}', the inner verb {inner} first coerces the "
            f"entity {entity} into each event {inner}(verb({entity})) for every relation "
            f"of {entity}; the outer verb {operator} then wraps each into "
            f"{operator}({inner}(verb({entity})))."
        )
    else:
        query = f"{operator} the {entity}"
        methods = (
            f"For the verb '{query}', the selecting verb {operator} coerces the entity "
            f"{entity} into each event {operator}(verb({entity})) for every relation of "
            f"{entity}."
        )
    return (
        "In complement coercion, an event-selecting verb applied to a noun whose "
        "denotation is an entity coerces that entity into one of its characterized "
        "events through stated purpose, creation, or use relations. Each relation names "
        "an event verb and a real-valued strength; the licensed interpretations are "
        "ordered from strongest to weakest relation, with ties broken by verb name. "
        "Coercion verbs: " + ", ".join(OPERATORS) + ". Event lexicon (entity: verb with "
        "strength):\n" + LEXICON_TEXT + "\n\n" + methods +
        "\n\nInstance: '" + query + "'\n"
        "List the licensed event interpretations of this instance. Give only the "
        "bracket-enclosed list ordered by relation strength, e.g. "
        '["begin(read(book))", "begin(write(book))"].'
    )

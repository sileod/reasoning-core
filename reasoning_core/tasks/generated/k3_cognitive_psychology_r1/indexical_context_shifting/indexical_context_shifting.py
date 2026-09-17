import random
from dataclasses import dataclass
from itertools import product

from reasoning_core.template import Config, Entry, Task, render_payload

TASK_META = {'parent_source_id': None,
 'idea': 'indexical_context_shifting (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_cognitive_psychology_r1/indexical_context_shifting',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

REFERENTS = (
    ("Mira", "Tomas", "Adele", "Rashid"),
    ("Yuki", "Paulo", "Ingrid", "Samir"),
    ("Lena", "Omar", "Nadia", "Felix"),
    ("Zora", "Hugo", "Elif", "Dario"),
)
CONTEXTS = tuple(product(range(4), repeat=2))


@dataclass
class IndexicalConfig(Config):
    depth: int = 2

    def apply_difficulty(self, level):
        self.depth = 2 + int(1.5 * level)


def shift(context, operator):
    day, city = context
    kind, sign, offset = operator
    if kind == "day":
        return ((day + sign * city + offset) % 4, city)
    if kind == "city":
        return (day, (city + sign * day + offset) % 4)
    if kind == "swap":
        return (city, day)
    raise ValueError("Unknown shift kind")


def verify(start, operators, final, answer):
    possible = [tuple(start)]
    for kind, sign, offset in operators:
        following = []
        for old_day, old_city in possible:
            for day, city in CONTEXTS:
                if kind == "day":
                    valid = city == old_city and (day - old_day - sign * old_city - offset) % 4 == 0
                elif kind == "city":
                    valid = day == old_day and (city - old_city - sign * old_day - offset) % 4 == 0
                elif kind == "swap":
                    valid = day == old_city and city == old_day
                else:
                    raise ValueError("Unknown shift kind")
                if valid:
                    following.append((day, city))
        possible = following
        assert len(possible) == 1
    assert possible == [tuple(final)]
    assert REFERENTS[possible[0][0]][possible[0][1]] == answer
    assert answer in {name for row in REFERENTS for name in row}


def operator_text(operator):
    kind, sign, offset = operator
    if kind == "swap":
        return "swap day and city simultaneously"
    other = "city" if kind == "day" else "day"
    term = f" {'+' if sign == 1 else '-'} {other}" if sign else ""
    return f"{kind} <- ({kind}{term} + {offset}) mod 4; {other} unchanged"


class IndexicalContextShifting(Task):
    summary = "Resolve the indexical I through a fixed character table mapping day/city context coordinates to referents; nested time/place shifts, cross-coordinate shifts and swaps rewrite coordinates, with the innermost denotation answered as one canonical character name."
    design_choice = "Answer the denotation of an indexical at a queried coordinate after applying a sequence of shift operators, with the answer being a canonical referent string from a fixed table."
    config_cls = IndexicalConfig
    task_version = 3

    def generate_entry(self):
        depth = random.randint(self.config.depth, self.config.depth + 2)
        start = random.choice(CONTEXTS)
        operators = []
        previous = None
        for _ in range(depth):
            kind = random.choice([k for k in ("day", "city", "swap") if k != previous])
            sign = random.choice((-1, 0, 1)) if kind != "swap" else 0
            offset = random.randrange(1, 4) if sign == 0 and kind != "swap" else random.randrange(4)
            operators.append([kind, sign, offset if kind != "swap" else 0])
            previous = kind
        trace = [list(start)]
        for operator in operators:
            trace.append(list(shift(trace[-1], operator)))
        day, city = trace[-1]
        answer = REFERENTS[day][city]
        verify(start, operators, trace[-1], answer)
        table = "day \\ city | 0 | 1 | 2 | 3\n" + "\n".join(
            f"{day} | " + " | ".join(row) for day, row in enumerate(REFERENTS)
        )
        expression = "I"
        for i in reversed(range(depth)):
            expression = f"S{i + 1}[{expression}]"
        payload = {
            "character_table": table,
            "starting_context": f"day={start[0]}, city={start[1]}",
            "shift_definitions": "\n".join(
                f"S{i + 1}: {operator_text(op)}" for i, op in enumerate(operators)
            ),
            "embedded_utterance": expression,
        }
        return Entry(metadata={"start": list(start), "operators": operators,
                               "trace": trace, "payload": payload}, answer=answer)

    def render_prompt(self, metadata):
        return (
            "In a staged diary, a context has two coordinates, day and city, each coded 0, 1, 2 or 3. "
            "The indexical I denotes the character in the table at the current day row and city column. "
            "S[utterance] rewrites the context using S before interpreting the utterance inside it. "
            "Use sequential context substitution: evaluate shifts from the outermost bracket inward, "
            "each exactly once. Every right-hand side uses the context entering that shift, not the "
            "original context. 'mod 4' means the remainder in 0..3, including for negative numbers. "
            "There is no additional shift when reading I.\n\n"
            + render_payload(metadata["payload"])
            + "\n\nWho does the innermost I denote at its resulting coordinate? "
            "Return only the exact character name; for example, if the lookup yields Mira, write Mira. "
            "Do not return coordinates or an explanation."
        )

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip() == entry.answer)

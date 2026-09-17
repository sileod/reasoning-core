import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'conflict_response_selection (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_cognitive_psychology_r1/conflict_response_selection',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

KEYS = ("LEFT", "RIGHT")
LABELS = KEYS + ("CONGRUENT", "INCONGRUENT")
FAMILIES = ("stroop", "flanker", "simon", "global_local")
SYMBOLS = {
    "stroop": ("RED", "BLUE", "GREEN", "YELLOW"),
    "flanker": ("<", ">", "^", "v"),
    "simon": ("RED", "BLUE", "GREEN", "YELLOW"),
    "global_local": ("H", "S", "E", "F"),
}
CODES = ("A", "B", "C", "D")


def response(symbol, metadata):
    value = symbol
    for table in metadata["tables"]:
        value = table[value]
    return metadata["keys"][value]


def displayed_dimensions(metadata):
    display = metadata["display"]
    family = metadata["family"]
    if family == "stroop":
        dimensions = (display["ink"], display["word"])
        return dimensions if metadata["cue"] == "ink" else dimensions[::-1]
    if family == "flanker":
        row = display["row"]
        center = len(row) // 2
        flankers = row[:center] + row[center + 1:]
        assert len(row) % 2 == 1 and len(set(flankers)) == 1
        return row[center], flankers[0]
    if family == "simon":
        return display["color"], display["side"]
    dimensions = (display["global"], display["local"])
    return dimensions if metadata["cue"] == "global" else dimensions[::-1]


def verified_answer(metadata):
    target, distractor = displayed_dimensions(metadata)
    target_key = response(target, metadata)
    distractor_key = distractor if metadata["family"] == "simon" else response(distractor, metadata)
    if metadata["mode"] == "response":
        return target_key
    return "CONGRUENT" if target_key == distractor_key else "INCONGRUENT"


@dataclass
class ConflictConfig(Config):
    stages: int = 1

    def apply_difficulty(self, level):
        self.stages = 1 + int(max(0, level))


class ConflictResponseSelection(Task):
    summary = "Stroop, flanker, Simon, and global-local trial families: map the cued display dimension through staged response rules while a distractor dimension competes; answers are the required keypress or a congruent/incongruent verdict."
    design_choice = "Answer format: the required keypress label from a fixed set (e.g., 'LEFT'/'RIGHT') versus a congruent/incongruent verdict; each trial emits one of these, with balanced counts per level."
    config_cls = ConflictConfig
    task_version = 3

    def generate_entry(self):
        family = random.choice(FAMILIES)
        symbols = SYMBOLS[family]
        tables = []
        source = symbols
        for _ in range(self.config.stages):
            tables.append(dict(zip(source, random.sample(CODES, len(CODES)))))
            source = CODES
        keys = dict(zip(CODES, random.sample(["LEFT", "LEFT", "RIGHT", "RIGHT"], 4)))
        preimages = {key: [code for code in CODES if keys[code] == key] for key in KEYS}
        for table in reversed(tables):
            preimages = {key: [symbol for symbol, code in table.items() if code in values]
                         for key, values in preimages.items()}
        assert all(len(values) == 2 for values in preimages.values())
        answer = random.choice(LABELS)
        mode = "response" if answer in KEYS else "verdict"
        target_key = answer if mode == "response" else random.choice(KEYS)
        congruent = random.choice((True, False)) if mode == "response" else answer == "CONGRUENT"
        distractor_key = target_key if congruent else KEYS[1 - KEYS.index(target_key)]
        target = random.choice(preimages[target_key])
        distractor = random.choice(preimages[distractor_key])
        if family == "stroop":
            cue = random.choice(("ink", "word"))
            display = {cue: target, "word" if cue == "ink" else "ink": distractor}
        elif family == "flanker":
            cue = "center"
            width = random.choice((3, 5, 7, 9))
            row = [distractor] * width
            row[width // 2] = target
            display = {"row": row}
        elif family == "simon":
            cue = "color"
            display = {"color": target, "side": distractor_key}
        else:
            cue = random.choice(("global", "local"))
            display = {cue: target, "local" if cue == "global" else "global": distractor}
        metadata = {"family": family, "mode": mode, "cue": cue, "display": display,
                    "tables": tables, "keys": keys}
        for key, values in preimages.items():
            assert all(response(value, metadata) == key for value in values)
        shown_target, shown_distractor = displayed_dimensions(metadata)
        assert response(shown_target, metadata) == target_key
        actual_distractor = shown_distractor if family == "simon" else response(shown_distractor, metadata)
        assert (target_key == actual_distractor) == congruent
        assert verified_answer(metadata) == answer
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        family, display, cue = metadata["family"], metadata["display"], metadata["cue"]
        if family == "stroop":
            trial = f"The word {display['word']} is printed in {display['ink']} ink."
            selection = f"The cue is {cue.upper()}; the other dimension is the distractor."
        elif family == "flanker":
            trial = "The arrow row is " + " ".join(display["row"]) + "."
            selection = "The cue is the CENTER arrow; the identical flanking arrows supply one distractor symbol."
        elif family == "simon":
            trial = f"A {display['color']} square appears on the {display['side']} side of the screen."
            selection = ("The cue is COLOR. The distractor is screen side: left side means LEFT key, "
                         "right side means RIGHT key, without using the code tables.")
        else:
            trial = f"A large {display['global']} is formed entirely from small {display['local']} letters."
            selection = f"The cue is {cue.upper()} (global = large letter, local = small letter); the other scale is the distractor."
        lines = [f"In a {family.replace('_', '-')} response-conflict trial, use this block's arbitrary response rule.",
                 trial, selection,
                 "Use sequential table lookup: translate a symbol at stage 1, then translate its code once at each later stage in order, then look up its key. Arrow direction has no additional meaning."]
        for index, table in enumerate(metadata["tables"], 1):
            lines.append(f"Stage {index}: " + "; ".join(f"{a} -> {b}" for a, b in table.items()))
        lines.append("Final keys: " + "; ".join(f"{a} -> {b}" for a, b in metadata["keys"].items()))
        if metadata["mode"] == "verdict":
            lines.append("Map both the cued and distractor dimensions to keys independently. Report CONGRUENT if their keys agree, otherwise INCONGRUENT; compare keys, not raw symbols. Example answer format: CONGRUENT.")
        else:
            lines.append("Map only the cued dimension and report its required keypress, LEFT or RIGHT. Example answer format: LEFT.")
        lines.append("Return only the single label, without explanation.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip().upper() == entry.answer)

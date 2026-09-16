import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'vowel_harmony_spreading (draw 2 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_parsing_and_agreement_r1/vowel_harmony_spreading',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 241712510,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def compute(system, trigger, unders, roles):
    """Return (surf, disharmonic) where surf is list of per-affix list of 3
    str tokens in order backness, round, ATR. A token is '0', '1' or 'X'."""
    n = len(unders)
    surf = [[None, None, None] for _ in range(n)]
    disharmonic = False
    src = [int(x) for x in trigger]
    alive = [True, True, True]
    for i in range(n):
        for fi in range(3):
            u = unders[i][fi]
            role = roles[i][fi]
            if system == "root":
                if role == "U":
                    if alive[fi]:
                        surf[i][fi] = str(src[fi])
                    else:
                        surf[i][fi] = str(u)
                        disharmonic = True
                elif role == "N":
                    surf[i][fi] = str(u)
                else:  # "B" opaque blocker
                    if alive[fi]:
                        surf[i][fi] = "X"
                        alive[fi] = False
                        src[fi] = 0
                    else:
                        surf[i][fi] = str(u)
                        disharmonic = True
            else:  # dominant-recessive: "B" marks a dominant source, never blocked
                if role == "B":
                    surf[i][fi] = str(u)
                    src[fi] = u
                else:  # "U" recessive, copies nearest live source
                    surf[i][fi] = str(src[fi])
    return surf, disharmonic


def melody_string(surf):
    return " | ".join("-".join(row) for row in surf)


@dataclass
class VowelHarmonyConfig(Config):
    num_affixes: int = 2

    def apply_difficulty(self, level):
        self.num_affixes = 2 + level


class VowelHarmonySpreading(Task):
    summary = "Spread harmony features (backness, round, ATR) from trigger vowels across affix chains, with opaque blockers and transparent neutrals in root-controlled and dominant-recessive systems; answers give the surface melody or mark disharmony."
    config_cls = VowelHarmonyConfig
    design_choice = "For each affix position, output a fixed-length binary vector (e.g., '1-0-1') indicating which of the three features (backness, round, ATR) spread there, with 'X' for blocked positions."

    def generate_entry(self):
        for _ in range(300):
            n = self.config.num_affixes
            system = random.choice(["root", "dominant"])
            trigger = [str(random.randint(0, 1)) for _ in range(3)]
            unders = []
            roles = []
            for _ in range(n):
                unders.append([random.randint(0, 1) for _ in range(3)])
                row = []
                for _ in range(3):
                    r = random.random()
                    if system == "root":
                        if r < 0.55:
                            row.append("U")
                        elif r < 0.70:
                            row.append("N")
                        else:
                            row.append("B")
                    else:
                        row.append("U" if r < 0.55 else "B")
                roles.append(row)
            surf, disharmonic = compute(system, trigger, unders, roles)

            want = (system == "root" and random.random() < 0.35)
            if disharmonic != want:
                continue

            if system == "root" and disharmonic:
                answer = "disharmony"
            else:
                answer = melody_string(surf)

            metadata = {
                "system": system,
                "trigger": "-".join(trigger),
                "unders": ["-".join(str(v) for v in row) for row in unders],
                "roles": ["-".join(row) for row in roles],
                "surf": [melody_string([row]) for row in surf],
                "disharmonic": disharmonic,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("could not generate a valid entry")

    def render_prompt(self, metadata):
        m = metadata
        lines = []
        lines.append(f"This is a {m['system']}-controlled vowel harmony system.")
        lines.append("Features per vowel appear in the order backness, round, ATR.")
        lines.append(f"Trigger root vowel: <{m['trigger']}>")
        for i in range(len(m["unders"])):
            lines.append(
                f"Suffix {i + 1}: underlying <{m['unders'][i]}> "
                f"{m['roles'][i]}"
            )
        lines.append(
            "In a root-controlled system a root feature spreads rightward through "
            "undergoers; an 'N' suffix is transparent (shows its own value, passes "
            "the spread), a 'B' suffix is an opaque blocker that stops the spread "
            "(shown as X) and any later undergoer then reverts to its own value, "
            "making the word disharmonious. In a dominant-recessive system 'B' is a "
            "dominant suffix: it re-sets the feature for all following suffixes; "
            "there is no X and the word is always harmonic."
        )
        lines.append(
            "Give the surface melody: one fixed-length vector per suffix in order "
            "backness-round-ATR (0/1/X), suffixes joined by ' | ', e.g. '1-0-X | "
            "0-1-1'. If any suffix reverts making the word disharmonious, answer "
            "exactly 'disharmony'."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == entry.answer else 0.0

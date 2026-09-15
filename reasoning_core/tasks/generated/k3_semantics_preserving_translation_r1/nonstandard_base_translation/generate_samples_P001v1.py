import importlib.util
import random
from pathlib import Path

_HERE = Path(__file__).parent
_MODULE = _HERE / "nonstandard_base_translation.py"

_spec = importlib.util.spec_from_file_location("nonstandard_base_translation_task", _MODULE)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
NonstandardBaseTranslation = _mod.NonstandardBaseTranslation

random.seed(1662004003)

OUT = _HERE / "samples_P001v1.md"

task = NonstandardBaseTranslation()

LEVELS = (0, 2, 5)
N_PER_LEVEL = 2

lines = []
for level in LEVELS:
    lines.append(f"# Level {level}")
    lines.append("")
    task.config.set_level(level)
    for _ in range(N_PER_LEVEL):
        entry = task.generate_entry()
        prompt = task.render_prompt(entry.metadata)
        lines.append(prompt)
        lines.append("")
        lines.append(f"Answer: {entry.answer}")
        lines.append("")

OUT.write_text("\n".join(lines))
print(OUT)

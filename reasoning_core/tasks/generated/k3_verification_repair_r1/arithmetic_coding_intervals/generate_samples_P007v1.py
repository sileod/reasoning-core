import importlib.util
import random
from pathlib import Path

_HERE = Path(__file__).parent
_SPEC = importlib.util.spec_from_file_location(
    "arithmetic_coding_intervals", _HERE / "arithmetic_coding_intervals.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
ArithmeticCodingConfig = _MOD.ArithmeticCodingConfig
ArithmeticCodingIntervals = _MOD.ArithmeticCodingIntervals

random.seed(1139467751)

OUT = Path(__file__).with_name("samples_P007v1.md")
task = ArithmeticCodingIntervals()
lines = []

for lvl in (0, 2, 5):
    cfg = ArithmeticCodingConfig()
    cfg.set_level(lvl)
    task.config = cfg
    lines.append(f"## Level {lvl}\n")
    for _ in range(2):
        ex = task.generate_example()
        lines.append("**Prompt:**\n")
        lines.append(task.render_prompt(ex.metadata))
        lines.append("\n")
        lines.append("**Answer:**\n")
        lines.append(ex.answer)
        lines.append("\n")
    lines.append("")

OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")

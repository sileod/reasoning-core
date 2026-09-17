"""Seeded sample generator for evidential_felicity_verdicts (trial P003v1)."""

import random
from pathlib import Path

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "evidential_felicity_verdicts",
    Path(__file__).with_name("evidential_felicity_verdicts.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def main():
    random.seed(2267388306)
    task = _mod.EvidentialFelicityVerdicts()
    out = [f"# Samples: evidential_felicity_verdicts (P003v1)\n"]
    for level in (0, 2, 5):
        cfg = task.config_cls()
        cfg.set_level(level)
        task.config = cfg
        out.append(f"\n## Level {level}\n")
        for _ in range(2):
            e = task.generate_entry()
            out.append("### Prompt\n")
            out.append(task.render_prompt(e.metadata) + "\n")
            out.append("\n### Answer\n")
            out.append(e.answer + "\n")
    path = Path(__file__).with_name("samples_P003v1.md")
    path.write_text("\n".join(out))


if __name__ == "__main__":
    main()

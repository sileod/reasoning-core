import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_psychometrics_r5.figure_symmetry_audit.figure_symmetry_audit import (
    FigureSymmetryAudit,
    FigureSymmetryAuditConfig,
)

SEED = 2267388306


def main():
    random.seed(SEED)
    out_path = Path(__file__).with_name('samples_P003v1.md')
    lines = []
    for level in (0, 2, 5):
        lines.append(f'## Level {level}')
        cfg = FigureSymmetryAuditConfig()
        cfg.set_level(level)
        task = FigureSymmetryAudit()
        task.config = cfg
        for _ in range(2):
            x = task.generate_example()
            lines.append('### Prompt')
            lines.append(task.render_prompt(x.metadata))
            lines.append('')
            lines.append('### Answer')
            lines.append(x.answer)
            lines.append('')
        lines.append('')
    out_path.write_text('\n'.join(lines))
    print(f'wrote {out_path}')


if __name__ == '__main__':
    main()

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_controlled_nli_r1.definitional_unfolding_subsumption.definitional_unfolding_subsumption import (
    DefinitionalUnfoldingSubsumption,
)


def main():
    random.seed(241712510)
    task = DefinitionalUnfoldingSubsumption()
    lines = ['# Samples for P007v2', '']
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.extend([f'## Level {level}', ''])
        for i in range(2):
            entry = task.generate_entry()
            lines.extend([f'### Example {i + 1}', '', '**Prompt:**', '', '```',
                          task.render_prompt(entry.metadata), '```', '',
                          '**Answer:**', '', '```', entry.answer, '```', ''])
    Path(__file__).with_name('samples_P007v2.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()

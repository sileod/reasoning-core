"""Generate samples_P006v1.md for the nuisance contrast identifiability task."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_invariants_r4.nuisance_contrast_identifiability.nuisance_contrast_identifiability import (
    NuisanceContrastConfig,
    NuisanceContrastIdentifiability,
)

SEED = 798610012


def main():
    random.seed(SEED)
    task = NuisanceContrastIdentifiability()
    out = Path(__file__).with_name('samples_P006v1.md')
    lines = []
    lines.append('# Samples for nuisance_contrast_identifiability (P006v1)')
    lines.append('')
    for level in (0, 2, 5):
        cfg = NuisanceContrastConfig()
        cfg.set_level(level)
        task.config = cfg
        lines.append('## Level %d' % level)
        lines.append('')
        for _ in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append('**Prompt**')
            lines.append('```')
            lines.append(prompt)
            lines.append('```')
            lines.append('')
            lines.append('**Answer**')
            lines.append('```')
            lines.append(ex.answer)
            lines.append('```')
            lines.append('')
    out.write_text('\n'.join(lines))
    print('wrote', out)


if __name__ == '__main__':
    main()

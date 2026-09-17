"""Generate samples_P006v3.md for the coset enumeration index trial, byte-reproducibly."""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coset_enumeration_index import CosetEnumerationIndex

TRIAL_ID = 'P006v3'
SEED = 2639544549
LEVELS = (0, 2, 5)


def main():
    random.seed(SEED)
    task = CosetEnumerationIndex()
    lines = [f'# Samples for {TRIAL_ID} (coset_enumeration_index)', '']
    for level in LEVELS:
        lines.append(f'## Level {level}')
        lines.append('')
        task.config.set_level(level)
        for i in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append(f'### Example {i + 1}')
            lines.append('')
            lines.append('**Prompt:**')
            lines.append('')
            lines.append('```')
            lines.append(prompt)
            lines.append('```')
            lines.append('')
            lines.append('**Answer:**')
            lines.append('')
            lines.append('```')
            lines.append(entry.answer)
            lines.append('```')
            lines.append('')
    out = Path(__file__).with_name(f'samples_{TRIAL_ID}.md')
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {out}')


if __name__ == '__main__':
    main()

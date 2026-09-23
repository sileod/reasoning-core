import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')))

from reasoning_core.tasks.generated.k3_state_tracking_r4.finite_difference_extension.finite_difference_extension import (  # noqa: E501
    FiniteDifferenceExtension,
)

SEED = 682015719
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'samples_P008v1.md')


def main():
    random.seed(SEED)
    task = FiniteDifferenceExtension()
    levels = [0, 2, 5]
    lines = []
    for level in levels:
        lines.append('# Level %d' % level)
        lines.append('')
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append('## Example %d (level %d)' % (i + 1, level))
            lines.append('')
            lines.append('**Prompt**')
            lines.append('```')
            lines.append(task.render_prompt(ex.metadata))
            lines.append('```')
            lines.append('')
            lines.append('**Answer**')
            lines.append('```')
            lines.append(ex.answer)
            lines.append('```')
            lines.append('')
    with open(OUT, 'w') as f:
        f.write('\n'.join(lines))
    print('wrote', OUT)


if __name__ == '__main__':
    main()

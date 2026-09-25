"""Byte-reproducible sample generation for algebraic_norm_descent (P011v1)."""

import random

from pathlib import Path

from reasoning_core.tasks.generated.ua_state_tracking_r4.algebraic_norm_descent import (
    algebraic_norm_descent as mod,
)

random.seed(2305351643)


def main():
    out = Path(__file__).with_name('samples_P011v1.md')
    with out.open('w') as f:
        for level in (0, 2, 5):
            f.write('# Level %d\n\n' % level)
            task = mod.AlgebraicNormDescent()
            task.config.set_level(level)
            for i in range(2):
                x = task.generate_example()
                f.write('## Example %d\n\n' % (i + 1))
                f.write(task.render_prompt(x.metadata))
                f.write('\n\nAnswer: %s\n\n' % x.answer)


if __name__ == '__main__':
    main()

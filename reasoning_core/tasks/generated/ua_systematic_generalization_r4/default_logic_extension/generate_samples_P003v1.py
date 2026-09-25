import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.default_logic_extension.default_logic_extension import (
    DefaultLogicExtension,
)

SEED = 2267388306


def main():
    random.seed(SEED)
    out = Path(__file__).with_name('samples_P003v1.md')
    task = DefaultLogicExtension(config=DefaultLogicExtension.config_cls())
    lines = []
    for level in (0, 2, 5):
        lines.append(f'## Level {level}')
        for _ in range(2):
            ex = task.generate_example(level=level)
            lines.append('**Prompt:**')
            lines.append(ex.prompt)
            lines.append('')
            lines.append('**Answer:**')
            lines.append(ex.answer)
            lines.append('')
            lines.append('---')
            lines.append('')
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'wrote {out}')


if __name__ == '__main__':
    main()

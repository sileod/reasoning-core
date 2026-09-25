import random
from pathlib import Path

from masked_stencil_identification import MaskedStencilIdentification

SEED = 2267388306


def main():
    random.seed(SEED)
    out = Path(__file__).with_name('samples_P003v1.md')
    task = MaskedStencilIdentification()
    lines = []
    for level in (0, 2, 5):
        lines.append(f'## Level {level}')
        for i in range(2):
            ex = task.generate_example(level=level)
            lines.append(f'### Example {i + 1}')
            lines.append('Prompt:')
            lines.append(ex.prompt)
            lines.append('Answer:')
            lines.append(ex.answer)
            lines.append('')
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()

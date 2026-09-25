import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_verification_repair_r4.counterpoint_dissonance_audit.counterpoint_dissonance_audit import (
    CounterpointDissonanceAudit,
)


def main():
    random.seed(2267388306)
    task = CounterpointDissonanceAudit()
    out = []
    for level in (0, 2, 5):
        out.append(f'## Level {level}\n')
        task.config.set_level(level)
        for _ in range(2):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            out.append('**Prompt:**')
            out.append(prompt)
            out.append('')
            out.append('**Answer:**')
            out.append(x.answer)
            out.append('')
    path = Path(__file__).with_name('samples_P003v1.md')
    path.write_text('\n'.join(out), encoding='utf-8')


if __name__ == '__main__':
    main()

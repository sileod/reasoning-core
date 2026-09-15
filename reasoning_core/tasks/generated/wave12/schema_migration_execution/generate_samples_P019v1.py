import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.schema_migration_execution.schema_migration_execution import (
    SchemaMigrationExecution,
)


def main():
    random.seed(469753138)
    task = SchemaMigrationExecution()
    out = Path(__file__).with_name('samples_P019v1.md')
    lines = []
    for level in (0, 2, 5):
        lines.append(f'## Level {level}')
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f'### Example {i+1}')
            lines.append(f'**Prompt:**')
            lines.append(ex.metadata['_prompt'] if '_prompt' in ex.metadata else
                         task.render_prompt(ex.metadata))
            lines.append('')
            lines.append(f'**Answer:** {ex.answer}')
            lines.append('')
    out.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()

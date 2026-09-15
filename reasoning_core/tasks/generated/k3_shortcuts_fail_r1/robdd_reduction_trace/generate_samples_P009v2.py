import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.robdd_reduction_trace.robdd_reduction_trace import (
    RobddReductionTrace,
)

random.seed(2701974858)

task = RobddReductionTrace()
out_path = Path(__file__).with_name('samples_P009v2.md')

lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append('')
    lines.append('Level %d' % level)
    lines.append('')
    for i in range(2):
        e = task.generate_example()
        lines.append('Example %d' % (i + 1))
        lines.append('')
        lines.append('Prompt:')
        lines.append(task.render_prompt(e.metadata))
        lines.append('')
        lines.append('Answer:')
        lines.append(e.answer)
        lines.append('')

out_path.write_text('\n'.join(lines))
print('wrote', out_path)

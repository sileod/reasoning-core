import importlib.util
import random
from pathlib import Path

_MODULE = Path(__file__).with_name('ratchet_motion_rectification.py')
_spec = importlib.util.spec_from_file_location('ratchet_mod', _MODULE)
_ratchet = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ratchet)
RatchetMotionRectification = _ratchet.RatchetMotionRectification

OUT = Path(__file__).with_name('samples_P005v1.md')

random.seed(729651269)

lines = []
for level in (0, 2, 5):
    lines.append(f'# Level {level}')
    lines.append('')
    task = RatchetMotionRectification()
    task.config.set_level(level)
    for k in range(2):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        lines.append(prompt)
        lines.append('')
        lines.append(f'Answer: {ex.answer}')
        lines.append('')

OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f'wrote {OUT}')

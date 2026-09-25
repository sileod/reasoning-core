import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.heap_extension_truth.heap_extension_truth import (
    HeapExtensionTruth,
)

random.seed(1139467751)

task = HeapExtensionTruth()
out = []
for level in (0, 2, 5):
    out.append("## Level %d" % level)
    chosen = []
    if level >= 2:
        for _ in range(200):
            ex = task.generate_example(level=level)
            f = ex.metadata["formula"]
            if "-*" in f or "*" in f:
                chosen.append(ex)
                if len(chosen) == 2:
                    break
    else:
        chosen = [task.generate_example(level=level) for _ in range(2)]
    for i, ex in enumerate(chosen):
        out.append("### Example %d" % (i + 1))
        out.append("Prompt:")
        out.append(ex.prompt)
        out.append("Answer: %s" % ex.answer)
        out.append("")

Path(__file__).with_name("samples_P007v1.md").write_text("\n".join(out))
print("wrote samples_P007v1.md")

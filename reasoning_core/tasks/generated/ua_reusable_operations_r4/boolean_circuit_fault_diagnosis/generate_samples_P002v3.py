import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_reusable_operations_r4.boolean_circuit_fault_diagnosis.boolean_circuit_fault_diagnosis import (
    BooleanCircuitFaultDiagnosis,
)

SEED = 368817805
OUT = Path(__file__).with_name("samples_P002v3.md")

random.seed(SEED)

lines = []
lines.append("# P002v3 samples - boolean_circuit_fault_diagnosis")
lines.append("")
for level in (0, 2, 5):
    lines.append("## Level %d" % level)
    lines.append("")
    t = BooleanCircuitFaultDiagnosis()
    t.config.set_level(level)
    for i in range(2):
        ex = t.generate_example()
        prompt = t.render_prompt(ex.metadata)
        lines.append("### Example %d" % (i + 1))
        lines.append("")
        lines.append(prompt)
        lines.append("")
        lines.append("Answer: %s" % ex.answer)
        lines.append("")

OUT.write_text("\n".join(lines))
print("wrote", OUT)

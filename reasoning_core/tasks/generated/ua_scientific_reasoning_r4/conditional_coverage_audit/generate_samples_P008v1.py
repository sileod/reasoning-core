import importlib.util
import pathlib
import random

random.seed(682015719)

_mod_path = pathlib.Path(__file__).with_name("conditional_coverage_audit.py")
_spec = importlib.util.spec_from_file_location("conditional_coverage_audit_trial", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

task = _mod.ConditionalCoverageAudit()

out_path = pathlib.Path(__file__).with_name("samples_P008v1.md")
lines = []
for level in (0, 2, 5):
    lines.append("# Level %d" % level)
    task.config.set_level(level)
    for _ in range(2):
        ex = task.generate_example()
        lines.append("## Example")
        lines.append("Prompt:")
        lines.append(ex.prompt)
        lines.append("Answer:")
        lines.append(ex.answer)
        lines.append("")
out_path.write_text("\n".join(lines))

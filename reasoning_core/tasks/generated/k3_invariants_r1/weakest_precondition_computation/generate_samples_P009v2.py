import importlib.util
import random
from pathlib import Path

_HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wpc_module", _HERE / "weakest_precondition_computation.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
Task = MOD.WeakestPreconditionComputation

random.seed(2701974858)


def main():
    out = []
    out.append("# Samples for weakest_precondition_computation (P009v2)\n")
    task = Task()
    # Force difficulty so levels 0,2,5 each carry two examples.
    for level, count in ((0, 2), (2, 2), (5, 2)):
        out.append("## Level %d\n" % level)
        for _ in range(count):
            task.config.set_level(level)
            x = task.generate_example()
            out.append("**Prompt**")
            out.append("```")
            out.append(task.render_prompt(x.metadata))
            out.append("```")
            out.append("")
            out.append("**Answer**")
            out.append("```")
            out.append(x.answer)
            out.append("```")
            out.append("")
    target = _HERE / "samples_P009v2.md"
    target.write_text("\n".join(out))


if __name__ == "__main__":
    main()

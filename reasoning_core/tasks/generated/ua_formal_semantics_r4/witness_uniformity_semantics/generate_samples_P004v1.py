import random
from pathlib import Path

random.seed(3536382515)

HERE = Path(__file__).resolve().parent


def _load():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "wus", HERE / "witness_uniformity_semantics.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_samples():
    mod = _load()
    task_cls = mod.WitnessUniformitySemantics
    lines = ["# Witness uniformity semantics samples", ""]
    for level in [0, 2, 5]:
        lines.append(f"## Level {level}")
        lines.append("")
        conf = mod.UniformityConfig()
        conf.set_level(level)
        task = task_cls(config=conf)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i+1}")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append(f"**Answer:** {ex.answer}")
            lines.append("")
    text = "\n".join(lines)
    (HERE / "samples_P004v1.md").write_text(text)


if __name__ == "__main__":
    _write_samples()

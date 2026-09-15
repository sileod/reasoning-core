import random
from pathlib import Path

import reasoning_core.tasks.generated.k3_verification_repair_r1.pipeline_hazard_trace.pipeline_hazard_trace as mod

random.seed(3536382515)

OUT = Path(__file__).with_name("samples_P004v1.md")


def render(level, count):
    cfg = mod.PipelineHazardConfig()
    cfg.set_level(level)
    if count is not None:
        cfg.count = count
    return mod.PipelineHazardTraceTask(config=cfg)


def main():
    chunks = ["# samples_P004v1"]
    for level in (0, 2, 5):
        task = render(level, None)
        chunks.append(f"\n## Level {level}\n")
        for _ in range(2):
            ex = task.generate_example()
            chunks.append("**Example prompt**\n")
            chunks.append("```\n" + ex.prompt + "\n```\n")
            chunks.append("**Answer**\n")
            chunks.append(f"`{ex.answer}`\n")
    OUT.write_text("\n".join(chunks) + "\n")


if __name__ == "__main__":
    main()

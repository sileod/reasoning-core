import random
from pathlib import Path

random.seed(1259343118)

from reasoning_core.tasks.generated.ua_synthetic_grammars_r4.metalinguistic_negation_targeting.metalinguistic_negation_targeting import MetalingNegationTargetingV3  # noqa: E402

OUT = Path(__file__).with_name("samples_P003v3.md")

lines = ["# samples_P003v3", ""]
with OUT.open("w") as fh:
    fh.write("# samples_P003v3\n\n")
    for level in (0, 2, 5):
        task = MetalingNegationTargetingV3()
        task.config.set_level(level)
        fh.write("## Level {}\n\n".format(level))
        for i in range(2):
            ex = task.generate_example()
            fh.write("### Example {}\n\n".format(i + 1))
            fh.write("Prompt:\n\n{}\n\n".format(ex.prompt))
            fh.write("Answer: {}\n\n".format(ex.answer))

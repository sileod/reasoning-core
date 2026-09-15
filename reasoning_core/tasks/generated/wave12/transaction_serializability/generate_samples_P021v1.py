"""Byte-reproducible sample generation for transaction_serializability."""
import os
import random
import sys
from pathlib import Path

random.seed(2562246315)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from transaction_serializability import TransactionSerializability
from reasoning_core.template import Entry  # noqa: F401


def main():
    task = TransactionSerializability()
    out = []
    for level in (0, 2, 5):
        cfg = task.config_cls()
        cfg.set_level(level)
        task.config = cfg
        out.append("## Level %d" % level)
        for i in range(2):
            ex = task.generate_example()
            out.append("### Example %d" % (i + 1))
            out.append(task.render_prompt(ex.metadata))
            out.append("Answer: %s" % ex.answer)
            out.append("")
        out.append("")
    outfile = HERE / "samples_P021v1.md"
    outfile.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("wrote", outfile)


if __name__ == "__main__":
    main()

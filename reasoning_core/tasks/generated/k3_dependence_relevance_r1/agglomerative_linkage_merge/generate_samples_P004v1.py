import random
from pathlib import Path

import importlib.util

_HERE = Path(__file__).parent
_SPEC = importlib.util.spec_from_file_location(
    "agglomerative_linkage_merge",
    _HERE / "agglomerative_linkage_merge.py",
)
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

AggloConfig = _MOD.AggloConfig
AgglomerativeLinkageMerge = _MOD.AgglomerativeLinkageMerge

random.seed(3536382515)


def main():
    out = []
    task = AgglomerativeLinkageMerge()
    for lvl in (0, 2, 5):
        out.append(f"# Level {lvl}")
        out.append("")
        cfg = AggloConfig()
        cfg.set_level(lvl)
        task.config = cfg
        for _ in range(2):
            e = task.generate_entry()
            prompt = task.render_prompt(e.metadata)
            out.append("**Prompt:**")
            out.append("")
            out.append("```")
            out.append(prompt)
            out.append("```")
            out.append("")
            out.append("**Answer:**")
            out.append("")
            out.append("```")
            out.append(e.answer)
            out.append("```")
            out.append("")
    with open(_HERE / "samples_P004v1.md", "w") as f:
        f.write("\n".join(out))
    print("wrote samples_P004v1.md")


if __name__ == "__main__":
    main()

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_operations_research_r4.dpll_clause_search import (
    dpll_clause_search as mod,
)
from reasoning_core.tasks.generated.k3_operations_research_r4.dpll_clause_search.dpll_clause_search import (
    DpllClauseSearch,
)

SEED = 4238614268
OUT = Path(__file__).with_name("samples_P001v3.md")


def main():
    random.seed(SEED)
    lines = []
    for level in (0, 2, 5):
        mod._VERDICT_SEEN.clear()
        task = DpllClauseSearch(config=mod.DPLLClauseSearchConfig().set_level(level))
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            prompt = ex.prompt if ex.prompt else task.render_prompt(ex.metadata)
            lines.append(prompt)
            lines.append("")
            lines.append(f"**Answer:** {ex.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

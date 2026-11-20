"""influence_varfmt_v1: task-agnostic answer wrappers, always announced in the prompt."""

from reasoning_core.evaluation.training.data import VARFMT_TEMPLATES, format_row


def test_varfmt_varies_the_wrapper_never_the_answer():
    rows = [{"prompt": f"task {i}?", "answer": f"ans{i}"} for i in range(200)]
    out = [format_row(r, "</s>", "influence_varfmt_v1") for r in rows]
    assert all(r["answer"] in o["completion"] and r["prompt"] in o["prompt"] for r, o in zip(rows, out))
    assert all(o["completion"].endswith("</s>") for o in out)
    used = {(o["prompt"].replace(r["prompt"], "{p}"), o["completion"].replace(r["answer"], "{a}"))
            for r, o in zip(rows, out)}
    assert len(used) == len(VARFMT_TEMPLATES)
    assert format_row(rows[0], "</s>", "influence_varfmt_v1") == out[0]  # deterministic


def test_every_wrapper_is_announced_in_the_prompt():
    for pre, suf, lead, tail in VARFMT_TEMPLATES:
        cue = (pre + suf).strip()
        assert cue, "a template with no prompt cue makes the wrapper unpredictable"
        if lead or tail:  # framing inside the completion must be spelled out by an instruction
            assert (lead.strip() or tail.strip()) in suf

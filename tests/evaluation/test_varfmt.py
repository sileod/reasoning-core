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


def test_episode_puts_demos_in_the_prompt_in_one_template():
    from reasoning_core.evaluation.training.data import format_episode
    demos = [{"prompt": "2+2?", "answer": "4"}, {"prompt": "3+3?", "answer": "6"}]
    row = {"prompt": "1+1?", "answer": "2"}
    out = format_episode(demos, row, "</s>", 4)  # "The answer is <answer>."
    assert out["completion"] == "The answer is 2.</s>"
    assert out["prompt"].count('Reply in the form') == 3
    assert "The answer is 4.\n\n" in out["prompt"] and "The answer is 6.\n\n" in out["prompt"]
    assert out["prompt"].endswith('1+1?\nReply in the form "The answer is <answer>."\n')
    assert format_episode([], row, "</s>", 0) == {"prompt": "1+1?\nAnswer:", "completion": " 2</s>"}
    assert format_row(row, "</s>", "influence_icl_v2") == format_row(row, "</s>", "influence_varfmt_v2")
    assert format_episode([], row, "</s>", 0, "influence_icl_v1")["prompt"] == "1+1?\nAnswer: "  # v1 kept as it ran


def test_v2_prompts_never_end_in_a_space_and_keep_the_v1_text():
    from reasoning_core.evaluation.training.data import VARFMT_TEMPLATES_V2
    for (pre, suf, lead, tail), v1 in zip(VARFMT_TEMPLATES_V2, VARFMT_TEMPLATES):
        assert not suf.endswith(" ") and pre + suf + lead + tail == "".join(v1)
    rows = [{"prompt": f"task {i}?", "answer": f"ans{i}"} for i in range(50)]
    for r in rows:
        a, b = format_row(r, "</s>", "influence_varfmt_v1"), format_row(r, "</s>", "influence_varfmt_v2")
        assert a["prompt"] + a["completion"] == b["prompt"] + b["completion"] and not b["prompt"].endswith(" ")

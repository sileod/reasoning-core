import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "cyclic_trace_invariants",
    os.path.join(os.path.dirname(__file__), "cyclic_trace_invariants.py"),
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CyclicTraceInvariants = mod.CyclicTraceInvariants
render_word = mod.render_word
eval_word = mod.eval_word
build_matrices = mod.build_matrices


def test_summary_and_design_choice_literals():
    assert isinstance(CyclicTraceInvariants.summary, str)
    assert "cyclicity" in CyclicTraceInvariants.summary
    assert "yes" in CyclicTraceInvariants.design_choice
    assert "no" in CyclicTraceInvariants.design_choice


def test_generate_and_render_runnable():
    task = CyclicTraceInvariants()
    for level in (0, 3, 6):
        cfg = task.config_cls()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(5):
            entry = task.generate_entry()
            assert entry.answer in ('yes', 'no')
            prompt = task.render_prompt(entry.metadata)
            assert entry.metadata['word1'] in prompt
            assert entry.metadata['word2'] in prompt
            assert task.score_answer(entry.answer, entry) == 1.0


def test_score_answer_strict():
    task = CyclicTraceInvariants()
    cfg = task.config_cls()
    cfg.set_level(0)
    task.config = cfg
    entry = task.generate_entry()
    other = 'no' if entry.answer == 'yes' else 'yes'
    assert task.score_answer(other, entry) == 0.0
    assert task.score_answer('', entry) == 0.0
    assert task.score_answer('yesno', entry) == 0.0
    assert task.score_answer(None, entry) == 0.0


def test_labels_balanced():
    task = CyclicTraceInvariants()
    cfg = task.config_cls()
    cfg.set_level(6)
    task.config = cfg
    labels = []
    for _ in range(60):
        labels.append(task.generate_entry().answer)
    yes = labels.count('yes')
    no = labels.count('no')
    assert 0.25 <= yes / len(labels) <= 0.75
    assert 0.25 <= no / len(labels) <= 0.75


def test_parse_render_round_trip():
    w1 = _parse_word(_parse_word.__doc__ or "")
    assert render_word([('A', 'T'), ('B', ''), ('C', 'X')]) == ['A^T', 'B', 'C^X']


def _parse_word(s):
    out = []
    for part in s.split(' * '):
        if part.endswith('^T'):
            out.append((part[:-2], 'T'))
        elif part.endswith('^X'):
            out.append((part[:-2], 'X'))
        else:
            out.append((part, ''))
    return out

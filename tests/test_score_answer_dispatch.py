import json

import pytest

from reasoning_core import score_answer
from reasoning_core.template import edict


class NoDeepcopy:
    def __deepcopy__(self, memo):
        raise NotImplementedError("proxy cannot be deep-copied")


def test_dispatch_decodes_string_metadata_without_deepcopying_the_row():
    entry = edict(
        answer="crate",
        metadata=json.dumps({"_task": "reference_tracking"}),
        unrelated_proxy=NoDeepcopy(),
    )

    assert score_answer("crate", entry) == 1.0
    assert isinstance(entry.metadata, str)


def test_regression_proxy_really_rejects_deepcopy():
    import copy

    with pytest.raises(NotImplementedError):
        copy.deepcopy(NoDeepcopy())


@pytest.mark.parametrize("task", __import__("reasoning_core").list_tasks())
def test_dispatched_scorer_never_touches_self(task):
    # dispatch scores with a self stub; a wrong answer reaching super() used to raise here
    try:
        score_answer("reajrjrje9595!", edict(answer="x", metadata={"_task": task}))
    except RuntimeError as error:
        assert "should not use self" not in str(error), task
    except Exception:
        pass  # the toy entry lacks task metadata; only self-use matters here

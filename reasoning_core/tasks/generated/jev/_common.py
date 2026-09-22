import json


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def jev_prompt(state, questions):
    request = {"state": state, "questions": questions}
    return (
        "Produce the reference answers for this Jev/System One request. "
        "Return only the JSON object that belongs under the API response's `answers` field.\n"
        + json.dumps(request, ensure_ascii=False, indent=2, sort_keys=True)
    )


def choice_answer(choice, options):
    return {
        "type": "choice",
        "choice": choice,
        "probabilities": {option: float(option == choice) for option in options},
        "confidence": 1.0,
    }


def noul_answer(value):
    return {"type": "noul", "noul": float(value)}


def score_answer(index, criteria):
    legend = {str(i): value for i, value in enumerate(criteria)}
    return {
        "type": "score",
        "score": float(index),
        "legend": legend,
        "probabilities": {str(i): float(i == index) for i in range(len(criteria))},
        "confidence": 1.0,
    }


def json_score(answer, entry):
    reference = entry["answer"] if isinstance(entry, dict) else entry.answer
    try:
        return float(json.loads(str(answer).strip()) == json.loads(str(reference).strip()))
    except (TypeError, ValueError, json.JSONDecodeError):
        return 0.0

"""Find one record among many whose ids differ from the target by one or two digits.

From level 2 the question names an original id that was reissued one to three times; the chain must be followed
to the listed id, and near-miss ids have reissue chains of their own. Ported from
tasksource.jev.procedural.needle_retrieval; its level tables stop at 4.
"""
import random
from dataclasses import dataclass

from reasoning_core.decision import Decision, render_records
from reasoning_core.template import Config, Entry, Task, stochastic_rounding as sround

CITIES = ["Oslo", "Lima", "Accra", "Hanoi", "Quito", "Porto", "Dakar", "Perth", "Tunis", "Osaka",
          "Bergen", "Cusco", "Lagos", "Hue", "Cuenca", "Braga", "Thies", "Darwin", "Sfax", "Kobe"]
SIZES = [8, 20, 50, 120, 250]
HOPS = [0, 0, 1, 2, 3]
DOMAINS = [("locker", "city"), ("shipment", "destination"), ("badge", "office"), ("account", "branch")]


def _near(key, rng):
    """A different id sharing most digits with ``key``: a swap or a one-digit change."""
    digits = list(key)
    i, j = rng.sample(range(4), 2)
    if digits[i] != digits[j] and rng.random() < 0.5:
        digits[i], digits[j] = digits[j], digits[i]
    else:
        digits[i] = rng.choice([d for d in "0123456789" if d != digits[i]])
    return "".join(digits)


@dataclass
class NeedleRetrievalConfig(Config):
    def apply_difficulty(self, level):
        pass  # the generator reads the level


class NeedleRetrieval(Task):
    summary = "Look up one record among near-miss ids, following reissued-id chains, as typed decisions."
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or NeedleRetrievalConfig())

    def generate_entry(self, state_seed=None, question=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, level = random.Random(state_seed), min(self.config.level, 4)
        noun, field = rng.choice(DOMAINS)
        n = max(4, sround(SIZES[level] * rng.uniform(0.7, 1.3), seed=rng.random()))
        target = f"{rng.randrange(10_000):04d}"
        keys = {target}
        while len(keys) < min(n, 4):  # guaranteed near misses of the target
            keys.add(_near(target, rng))
        while len(keys) < n:
            keys.add(_near(target, rng) if rng.random() < 0.2 else f"{rng.randrange(10_000):04d}")
        keys = sorted(sorted(keys), key=lambda _: rng.random())  # sort first: set order depends on the hash seed
        prefix = f"{noun[0].upper()}-"
        records = [{"id": prefix + key, field: rng.choice(CITIES)} for key in keys]
        gold = records[keys.index(target)]
        near = [r for r in records if r is not gold and sum(a != b for a, b in zip(r["id"], gold["id"])) <= 2]

        others = list(dict.fromkeys(r[field] for r in near if r[field] != gold[field]))
        others += [c for c in rng.sample(CITIES, len(CITIES)) if c != gold[field] and c not in others]
        options = sorted([gold[field], *others[:rng.randint(6, len(CITIES)) - 1]], key=lambda _: rng.random())

        proposed = gold[field] if rng.random() < 0.5 else others[0]
        listed = {r["id"] for r in records}
        if rng.random() < 0.5:
            probe = rng.choice(near)["id"]
        else:
            probe = gold["id"]
            while probe in listed:
                probe = prefix + _near(target, rng)

        used = set(keys) | {probe[len(prefix):]}  # the id_listed probe must not turn out to be a reissued id

        def fresh(near_to):
            while True:
                candidate = _near(near_to, rng) if rng.random() < 0.7 else f"{rng.randrange(10_000):04d}"
                if candidate not in used:
                    used.add(candidate)
                    return candidate

        reissued = {}  # old id -> new id
        chain = [target]
        for _ in range(HOPS[level]):
            chain.insert(0, fresh(chain[0]))
            reissued[prefix + chain[0]] = prefix + chain[1]
        for _ in range(2 * HOPS[level]):  # near-miss chains that end at other records
            end = rng.choice([k for k in keys if k != target])
            start = fresh(chain[0])
            if rng.random() < 0.5:
                middle = fresh(start)
                reissued[prefix + start], reissued[prefix + middle] = prefix + middle, prefix + end
            else:
                reissued[prefix + start] = prefix + end

        style = rng.choice(["json", "table", "csv", "lines", "prose"])
        if style == "prose":
            state = " ".join(f"The {noun} {r['id']} has {field} {r[field]}." for r in records)
        else:
            state = render_records(records, style)
        if reissued:
            moves = sorted(reissued.items(), key=lambda _: rng.random())
            state += (f"\n\nReissued {noun} ids (a reissued id is no longer listed; look up its new id):\n"
                      + "\n".join(f"{old} -> {new}" for old, new in moves))
        key = prefix + chain[0]
        questions = {
            "value_of_id": Decision(gold[field], criteria=dict.fromkeys(options), instructions=rng.choice([
                "Which {f} is listed for {n} {k}?", "What is the {f} of {n} {k}?",
                "Look up {n} {k}. Which {f} does it have?"]).format(f=field, n=noun, k=key)),
            "id_has_value": Decision(proposed == gold[field], type="noul", instructions=rng.choice([
                "Is {n} {k} listed with {f} {v}?", "Does {n} {k} have {f} {v}?"]).format(
                f=field, n=noun, k=key, v=proposed)),
            "id_listed": Decision(probe in listed, type="noul", instructions=rng.choice([
                "Is there a {n} with id {p}?", "Does the list include {n} {p}?"]).format(n=noun, p=probe)),
        }
        qid = question or random.choice(sorted(questions))
        return Entry({"payload": state, "state_seed": state_seed, "question_id": qid}, questions[qid])

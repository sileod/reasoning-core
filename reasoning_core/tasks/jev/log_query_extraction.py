"""Answer log queries with spans: every request id or user matching a filter, or the one that is latest or slowest.

Logs come as plain lines, logfmt or JSON lines, and from level 2 may merge hosts out of time order. Filters
conjoin level, service, status code, latency bounds and user, some negated; services include near-miss names
(auth / auth-proxy) and request ids share prefixes. An empty answer is null. Levels add lines, conditions,
near-miss services and disorder.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core.tasks.jev._extraction import FIRST, Doc, extraction_entry

SERVICES = ["auth", "billing", "search", "gateway", "media", "notify"]
NEAR = {"auth": "auth-proxy", "billing": "billing-worker", "search": "search-index", "gateway": "gateway-v2",
        "media": "media-cdn", "notify": "notify-sms"}
STATUS = {"INFO": [200, 201, 204, 304], "WARN": [401, 404, 429], "ERROR": [500, 502, 503]}
FORMATS = {
    "plain": "{t} {lvl} [{svc}] req={rid} user={user} status={st} latency={ms}ms",
    "logfmt": "time={t} level={lvl} service={svc} request_id={rid} user={user} status={st} duration_ms={ms}",
    "json": '{"ts": "{t}", "level": "{lvl}", "service": "{svc}", "req": "{rid}", "user": "{user}", '
            '"code": {st}, "ms": {ms}}',  # Doc fills {word} slots only: JSON braces stay literal
}


def _condition(rng, lines, kind, negate):
    """A filter (text, test) of `kind` whose value comes from a line, so it can match."""
    x = rng.choice(lines)
    if kind == "lvl":
        v = x["lvl"]
        return (f"its level is not {v}", lambda y: y["lvl"] != v) if negate else (f"its level is {v}", lambda y: y["lvl"] == v)
    if kind == "svc":
        v = x["svc"]
        return ((f"its service is not exactly {v}", lambda y: y["svc"] != v) if negate else
                (f"its service is exactly {v}", lambda y: y["svc"] == v))
    if kind == "st":
        v = x["st"]
        return ((f"its status code is at least {v}", lambda y: y["st"] >= v) if rng.random() < 0.5 else
                (f"its status code is below {v}", lambda y: y["st"] < v))
    if kind == "ms":
        v = x["ms"] // 10 * 10
        return ((f"it took more than {v} ms", lambda y: y["ms"] > v) if rng.random() < 0.5 else
                (f"it took at most {v} ms", lambda y: y["ms"] <= v))
    v = x["user"]
    return (f"its user is not {v}", lambda y: y["user"] != v) if negate else (f"its user is {v}", lambda y: y["user"] == v)


@dataclass
class LogQueryExtractionConfig(Config):
    lines: float = 6.0
    conditions: float = 1.0
    negation: float = 0.0
    near_services: float = 0.0
    unordered: float = 0.0
    fields: float = 2.0

    def apply_difficulty(self, level):
        self.lines = 6 + 4 * level
        self.conditions = 1 + 0.6 * level
        self.negation = min(0.4, 0.1 * level)
        self.near_services = min(0.8, 0.25 * level)
        self.unordered = min(0.8, max(0.0, 0.3 * (level - 1)))
        self.fields = 2 + 0.3 * level


class LogQueryExtraction(Task):
    summary = ("Extract every request id or user of log lines matching conjunctive filters on level, exact service "
               "(near-miss names), status, latency and user, or the latest/slowest match, from plain, logfmt or "
               "JSON-lines logs, possibly out of time order.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or LogQueryExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, c = random.Random(state_seed), self.config
        n = max(4, sround(c.lines, seed=rng.random()))
        services = rng.sample(SERVICES, 3)
        services += [NEAR[s] for s in services if rng.random() < c.near_services]
        users = [u.lower() for u in rng.sample(FIRST, min(len(FIRST), 2 + n // 4))]
        prefix = f"{rng.randrange(16 ** 3):03x}"
        seconds = sorted(rng.sample(range(9 * 3600, 18 * 3600), n))
        latencies = rng.sample(range(5, 3000), n)  # distinct: "slowest" is unique
        lines, rids = [], set()
        for s, ms in zip(seconds, latencies):
            lvl = rng.choices(sorted(STATUS), weights=[2, 5, 3])[0]
            rid = prefix + f"{rng.randrange(16 ** 4):04x}"
            if rid in rids:
                continue
            rids.add(rid)
            lines.append({"t": f"{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}", "s": s, "lvl": lvl,
                          "svc": rng.choice(services), "rid": rid, "user": rng.choice(users),
                          "st": rng.choice(STATUS[lvl]), "ms": ms})
        unordered = rng.random() < c.unordered
        shown = rng.sample(lines, len(lines)) if unordered else lines
        style = rng.choice(sorted(FORMATS))
        doc = Doc().add(f"Service logs ({'merged from two hosts, not in time order' if unordered else 'in time order'}):\n")
        for x in shown:
            i = lines.index(x)
            doc.add(FORMATS[style] + "\n", **{**{k: str(v) for k, v in x.items()},
                                              "rid": (x["rid"], f"rid{i}"), "user": (x["user"], f"user{i}")})

        fields, spans = [], {}
        for f in range(max(1, sround(c.fields, seed=rng.random()))):
            k, allow_empty = min(5, max(1, sround(c.conditions, seed=rng.random()))), rng.random() < 0.15
            for _ in range(50):
                conditions = [_condition(rng, lines, kind, rng.random() < c.negation)
                              for kind in rng.sample(["lvl", "svc", "st", "ms", "user"], k)]
                match = [i for i, x in enumerate(lines) if all(test(x) for _, test in conditions)]
                if match or allow_empty:
                    break
            phrase = " and ".join(text for text, _ in conditions)
            what = rng.choice(["rid", "rid", "user", "latest", "slowest"]) if match else "rid"
            if what == "latest":
                match = [max(match, key=lambda i: lines[i]["s"])]
            elif what == "slowest":
                match = [max(match, key=lambda i: lines[i]["ms"])]
            name = {"rid": "request_ids", "user": "users", "latest": "latest_user", "slowest": "slowest_request"}[what]
            instruction = {"rid": "Every request id of a line where {}.", "user": "Every user of a line where {}.",
                           "latest": "The user of the latest line (by time) where {}.",
                           "slowest": "The request id of the slowest line where {}."}[what].format(phrase)
            fields.append({"name": f"{name}_{f + 1}", "type": "list" if what in ("rid", "user") else "text",
                           "instruction": instruction})
            mark = "user" if what in ("user", "latest") else "rid"
            spans[f"{name}_{f + 1}"] = [span for i in match for span in doc.marks[f"{mark}{i}"]]
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, style=style)

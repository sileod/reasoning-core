"""Evaluate path queries on a configuration made of a base layer and override layers, in JSON, YAML or XML.

Latent structure: a random tree of blocks (scalar keys and nested sub-blocks drawn from one shared vocabulary, so
keys repeat at several depths) with a `services` list of records, plus override layers that change, add or drop
keys, or replace the list. A merge mode, stated in the document, folds the layers in order: deep (blocks merge key by
key; a scalar or list replaces the earlier one) or replace (a top-level block replaces the earlier block whole).
Queries are a tiny path language evaluated on the merged tree: an exact path (database.pool.max_size), the only
occurrence of a key anywhere under a block, or a conjunction of predicates (equality, comparison) selecting
services records, projected on one key (one record, or every match as a list). The solver returns the merged leaf,
whose span is where its winning layer writes it, unquoted; nothing found is null, while the key exists elsewhere.
Levels add depth, branching, sections, records, predicates, layers and near-miss service names.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core.tasks.jev._extraction import Doc, extraction_entry

SECTIONS = ["server", "database", "cache", "queue", "auth", "logging", "storage", "metrics"]
SUBS = ["pool", "tls", "limits", "replica", "backup", "proxy"]
ZONES = ["eu-west", "us-east", "ap-south", "eu-north"]
SCALARS = {  # key -> (value(rng), quoted in JSON)
    "host": (lambda rng: f"{rng.choice(['db', 'node', 'edge', 'core'])}-{rng.randint(1, 99)}.{rng.choice(ZONES)}."
                         "internal", True),
    "port": (lambda rng: str(rng.randint(1024, 9999)), False),
    "timeout_ms": (lambda rng: str(rng.choice(range(250, 10_000, 250))), False),
    "retries": (lambda rng: str(rng.randint(0, 9)), False),
    "enabled": (lambda rng: rng.choice(["true", "false"]), False),
    "level": (lambda rng: rng.choice(["debug", "info", "warn", "error"]), True),
    "max_size": (lambda rng: str(rng.randint(2, 512)), False),
    "region": (lambda rng: rng.choice(ZONES), True),
}
SERVICES = ["auth", "billing", "search", "gateway", "media", "notify", "orders", "reports"]
NEAR = {"auth": "auth-proxy", "billing": "billing-worker", "search": "search-index", "gateway": "gateway-v2",
        "media": "media-cdn", "notify": "notify-sms", "orders": "orders-sync", "reports": "reports-batch"}
RULES = {"deep": "Override layers apply in order and are deep-merged: nested blocks merge key by key, while a "
                 "scalar or a list in a later layer replaces the earlier one.",
         "replace": "Override layers apply in order; a top-level block in a later layer replaces the earlier block "
                    "entirely, so keys it omits are gone."}


def merge(base, layer, mode, top=True):
    """The base with the layer folded in: deep merges blocks at every depth, replace swaps top-level blocks."""
    out = dict(base)
    for k, v in layer.items():
        nested = isinstance(v, dict) and isinstance(out.get(k), dict) and (mode == "deep" or not top)
        out[k] = merge(out[k], v, mode, False) if nested else v
    return out


def leaves(node, path=()):
    """(path, leaf) of the scalars outside lists."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from leaves(v, path + (k,))
    elif isinstance(node, tuple):
        yield path, node


def blocks(node, path=()):
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            yield from blocks(v, path + (k,))


def _render(node, fmt, ind):
    """Pieces of the text: raw strings and (text, mark) leaves."""
    pad = " " * ind
    if fmt == "json":
        if isinstance(node, tuple):
            return ['"', node[:2], '"'] if node[2] else [node[:2]]
        if isinstance(node, dict) and all(isinstance(v, tuple) for v in node.values()):  # a flat block on one line
            out = ["{"]
            for i, (k, v) in enumerate(node.items()):
                out += [", " * (i > 0) + f'"{k}": '] + _render(v, fmt, ind)
            return out + ["}"]
        items = list(enumerate(node.items() if isinstance(node, dict) else node))
        out = ["{\n" if isinstance(node, dict) else "[\n"]
        for i, kv in items:
            key, value = kv if isinstance(node, dict) else (None, kv)
            out += [pad + "  " + (f'"{key}": ' if key else "")] + _render(value, fmt, ind + 2)
            out += [",\n" if i < len(items) - 1 else "\n"]
        return out + [pad + ("}" if isinstance(node, dict) else "]")]
    out = []
    for k, v in node.items():
        if fmt == "yaml":
            if isinstance(v, tuple):
                out += [f"{pad}{k}: ", v[:2], "\n"]
            elif isinstance(v, dict):
                out += [f"{pad}{k}:\n"] + _render(v, fmt, ind + 2)
            else:
                out += [f"{pad}{k}:\n"]
                for item in v:
                    lines = _render(item, fmt, ind + 4)
                    out += [pad + "  - " + lines[0][ind + 4:]] + lines[1:]
        elif isinstance(v, tuple):
            out += [f"{pad}<{k}>", v[:2], f"</{k}>\n"]
        elif isinstance(v, dict):
            out += [f"{pad}<{k}>\n"] + _render(v, fmt, ind + 2) + [f"{pad}</{k}>\n"]
        else:  # <services> of <service name="..." port="..."/> records, values as attributes
            out += [f"{pad}<{k}>\n"]
            for item in v:
                out += [f"{pad}  <{k[:-1]}"]
                for a, b in item.items():
                    out += [f' {a}="', b[:2], '"']
                out += ["/>\n"]
            out += [f"{pad}</{k}>\n"]
    return out


@dataclass
class NestedStructureExtractionConfig(Config):
    sections: float = 2.0
    depth: float = 1.0
    branching: float = 0.6
    records: float = 2.0
    leaves: float = 10.0
    layers: float = 0.4
    preds: float = 1.0
    near: float = 0.2
    missing: float = 0.15
    fields: float = 2.0

    def apply_difficulty(self, level):
        self.sections = 2 + 0.4 * level
        self.depth = 1 + 0.4 * level
        self.branching = 0.6 + 0.2 * level
        self.records = 2 + 0.5 * level
        self.leaves = 10 + 3 * level
        self.layers = 0.4 + 0.4 * level
        self.preds = 1 + 0.5 * level
        self.near = min(0.8, 0.2 + 0.15 * level)
        self.missing = 0.15 + 0.02 * level
        self.fields = 2 + 1.2 * level


class NestedStructureExtraction(Task):
    summary = ("Evaluate exact-path, any-depth and predicate-filter queries on a JSON, YAML or XML config whose "
               "override layers are deep-merged or replace whole blocks, and extract the winning values as written.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or NestedStructureExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, c = random.Random(state_seed), self.config
        fmt, mode = rng.choice(["json", "yaml", "xml"]), rng.choice(sorted(RULES))
        count = iter(range(10 ** 6))

        def leaf(key, text=None, quoted=None):
            return (SCALARS[key][0](rng) if text is None else text, f"x{next(count)}",
                    SCALARS[key][1] if quoted is None else quoted)

        budget = [sround(c.leaves, seed=rng.random())]

        def block(depth, name=None):  # scalars, then sub-blocks while the leaf budget lasts
            node = {k: leaf(k) for k in rng.sample(sorted(SCALARS), rng.randint(2, 3))}
            budget[0] -= len(node)
            subs = [s for s in SUBS if s != name]
            for sub in rng.sample(subs, min(len(subs), sround(c.branching, seed=rng.random()))) if depth else []:
                if budget[0] > 0:
                    node[sub] = block(depth - 1, sub)
            return node

        def record(name):
            item = {"name": leaf("level", name, True), "host": leaf("host"), "port": leaf("port"),
                    "enabled": leaf("enabled"), "weight": leaf("retries", str(rng.randint(1, 9)))}
            if rng.random() < 0.6:
                item["region"] = leaf("region")
            return item

        names = []
        for name in rng.sample(SERVICES, len(SERVICES)):  # near-miss pairs: auth and auth-proxy
            names += [name, NEAR[name]] if rng.random() < c.near else [rng.choice([name, NEAR[name]])]
        names = names[:max(2, sround(c.records, seed=rng.random()))]
        base = {s: block(sround(c.depth, seed=rng.random()))
                for s in rng.sample(SECTIONS, min(len(SECTIONS), sround(c.sections, seed=rng.random())))}
        base["services"] = [record(n) for n in names]

        layers, merged = [], base
        for _ in range(sround(c.layers, seed=rng.random())):  # each changes, adds or drops keys, or the list
            layer = {}
            for section in rng.sample(sorted(merged), rng.randint(1, min(2, len(merged)))):
                if section == "services":  # a new list: some records dropped, some values changed
                    items = [{k: leaf(k if k in SCALARS else "retries", *v[::2]) for k, v in i.items()}
                             for i in merged["services"] if rng.random() < 0.85]
                    for item in rng.sample(items, min(len(items), 2)):
                        item[k] = leaf(k := rng.choice(["port", "enabled", "host", "region"]))
                    layer["services"] = items
                    continue
                copy = {}
                for path, (text, _, quoted) in leaves(merged[section]):
                    roll = rng.random()
                    if roll < 0.3 or (mode == "replace" and roll < 0.9):  # changed, or carried over (replace)
                        node = copy
                        for k in path[:-1]:
                            node = node.setdefault(k, {})
                        node[path[-1]] = leaf(path[-1]) if roll < 0.3 else leaf(path[-1], text, quoted)
                extra = rng.choice(sorted(SCALARS))
                if rng.random() < 0.4 and extra not in merged[section]:
                    copy[extra] = leaf(extra)
                layer[section] = copy or {extra: leaf(extra)}
            layers.append(layer)
            merged = merge(merged, layer, mode)

        all_leaves = list(leaves({k: v for k, v in merged.items() if k != "services"}))
        all_keys = {p[-1] for p, _ in all_leaves}
        items = merged["services"]

        def predicate(item, kind):
            k = rng.choice(["name", "region", "enabled"] if kind == "eq" else ["port", "weight"])
            if k not in item:
                return None
            v = item[k][0]
            if kind == "eq":
                return f'`{k}` is "{v}"' if k != "enabled" else f"`{k}` is {v}", lambda i: k in i and i[k][0] == v
            n = int(v) - rng.choice([0, 1, int(v) // 4])
            return f"`{k}` is at least {n}", lambda i: k in i and int(i[k][0]) >= n

        fields, gold = [], {}
        for f in range(min(7, max(2, sround(c.fields, seed=rng.random())))):
            kind, null, hit = rng.choice(["path", "under", "pick", "list"]), rng.random() < c.missing, []
            if kind == "path" and all_leaves:
                path, value = rng.choice(all_leaves)
                parent = next(b for p, b in blocks(merged) if p == path[:-1])
                others = sorted(all_keys - set(parent))
                if null and others:  # a key set elsewhere but not in this block
                    path = path[:-1] + (rng.choice(others),)
                else:
                    hit = [value]
                instruction = f"The value at the path `{'.'.join(path)}` of the merged configuration."
            elif kind == "under" and all_leaves:
                scopes = [(p, b) for p, b in blocks(merged) if p and any(isinstance(v, dict) for v in b.values())]
                path, scope = rng.choice(scopes or [(p, b) for p, b in blocks(merged) if p])
                found = {}
                for p, v in leaves(scope):
                    found.setdefault(p[-1], []).append(v)
                once, absent = [k for k, vs in found.items() if len(vs) == 1], sorted(all_keys - set(found))
                if not once and not absent:
                    continue
                key = rng.choice(absent) if absent and (null or not once) else rng.choice(once)
                hit = found.get(key, [])
                instruction = (f"The `{key}` set anywhere inside `{'.'.join(path)}` of the merged configuration, "
                               "at any depth (it occurs at most once there).")
            elif kind in ("pick", "list"):
                preds, target = [], rng.choice(items) if items else {}
                for _ in range(max(1, sround(c.preds, seed=rng.random()))):
                    p = predicate(target, rng.choice(["eq", "cmp"])) if target else None
                    if p and p[0].split("`")[1] not in [q[0].split("`")[1] for q in preds]:
                        preds.append(p)
                if kind == "pick" and target:
                    if sum(all(t(i) for _, t in preds) for i in items) != 1:
                        name = target["name"][0]
                        preds.append((f'`name` is "{name}"', lambda i, n=name: i["name"][0] == n))
                    ghost = next((n for n in [NEAR.get(target["name"][0]), target["name"][0].split("-")[0]]
                                  if n and n not in names), None)
                    if null and ghost:  # the name of a near miss that is not in the list
                        preds = [p for p in preds if not p[0].startswith("`name`")]
                        preds.append((f'`name` is "{ghost}"', lambda i, g=ghost: i["name"][0] == g))
                preds = preds or [("`enabled` is true", lambda i: i["enabled"][0] == "true")]
                used = {p.split("`")[1] for p, _ in preds}
                key = rng.choice([k for k in ["host", "port", "region", "weight", "name"] if k not in used and
                                  (k != "name" or kind == "list")])
                match = [i for i in items if all(t(i) for _, t in preds)]
                hit = [i[key] for i in match if key in i]
                phrase = " and ".join(p for p, _ in preds)
                instruction = (f"The `{key}` of the `services` record whose {phrase}, in the merged configuration; "
                               f"null if no record matches or it has no `{key}`." if kind == "pick" else
                               f"Every `{key}` of a `services` record whose {phrase}, in the merged configuration, "
                               "in order of appearance.")
            else:
                continue
            name = f"{kind}_{f + 1}"
            fields.append({"name": name, "type": "list" if kind == "list" else "text", "instruction": instruction})
            gold[name] = [h[1] for h in hit]

        if fmt == "json":
            pieces = _render({"_comment": (RULES[mode], None, True), "base": base,
                              **({"overrides": layers} if layers else {})}, fmt, 0)
        elif fmt == "yaml":
            pieces = [f"# {RULES[mode]} Documents after the first are the override layers.\n"] + _render(base, fmt, 0)
            for layer in layers:
                pieces += ["---\n"] + _render(layer, fmt, 0)
        else:
            pieces = [f"<!-- {RULES[mode]} -->\n<config>\n  <base>\n"] + _render(base, fmt, 4) + ["  </base>\n"]
            for i, layer in enumerate(layers, 1):
                pieces += [f'  <override order="{i}">\n'] + _render(layer, fmt, 4) + ["  </override>\n"]
            pieces += ["</config>"]
        doc = Doc()
        for piece in pieces:
            doc.add("{p}", p=piece)
        spans = {n: [s for m in ms for s in doc.marks[m]] for n, ms in gold.items()}
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, format=fmt)

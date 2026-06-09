
import difflib
import random
import re
import hashlib
from dataclasses import dataclass
from easydict import EasyDict as edict
from faker import Faker
from rapidfuzz.distance import Levenshtein
import whatthepatch
from reasoning_core.template import Task, DevTask, Problem, Config, edict
from typing import List

fake = Faker()

def with_lineno(lines: List[str]) -> str:
    return "\n".join(f"{i+1:<4} | {line}" for i, line in enumerate(lines))

def get_short_hash():
    """Generates a git-style short hash (7 chars)."""
    r = str(random.random()).encode('utf-8')
    return hashlib.sha1(r).hexdigest()[:7]

@dataclass
class DiffConfig(Config):
    min_versions: int = 2
    max_versions: int = 5
    nb_lines: int = 5
    mutation_rate: float = 0.2

    def update(self, c):
        self.max_versions += c
        self.nb_lines += c

def mutate_words_in_line(line, vocab, rate):
    """Mutates words within a single string (line)."""
    words = line.split()
    if not words: return line
    
    if random.random() > rate:
        return line

    new_words = []
    for word in words:
        r = random.random()
        if r < 0.05:   # Delete word
            continue
        elif r < 0.15: # Substitute word
            new_words.append(random.choice(vocab))
        else:
            new_words.append(word)
    
    if not new_words and words:
        new_words = [random.choice(vocab)]
        
    return " ".join(new_words)

def mutate_lines(lines, vocab, rate):
    """Evolves a list of lines (sentences)."""
    new_lines = []
    
    for line in lines:
        r = random.random()
        if r < rate / 5:       # Delete entire line
            continue
        elif r < rate:         # Modify line
            new_lines.append(mutate_words_in_line(line, vocab, rate)) 
        elif r < rate * 1.2:   # Insert new line
            new_lines.append(" ".join(fake.words(nb=5)))
            new_lines.append(line)
        else:
            new_lines.append(line)
            
    if not new_lines:
        new_lines.append(" ".join(fake.words(nb=5)))
        
    return new_lines

def get_git_diff(src_lines, tgt_lines):
    """Generates a standard Git-style unified diff without file headers."""
    diff = difflib.unified_diff(src_lines, tgt_lines, lineterm='')
    # Strip the first two lines (--- and +++) to leave only chunks
    return "\n".join(list(diff)[2:])

class VersionedTask:
    def __init__(self, config=DiffConfig()):
        super().__init__(config=config)
        self.vocab = list(fake.words(nb=500, unique=True))
        self.balancing_key_ratio = 0.1

    def generate_version_chain(self):
        lines = [fake.sentence(nb_words=6).rstrip('.') for _ in range(self.config.nb_lines)]
        vid = get_short_hash()
        
        chain = [{'id': vid, 'lines': lines}]

        n_versions = random.randint(self.config.min_versions, self.config.max_versions)
        for _ in range(n_versions - 1):
            prev_lines = chain[-1]['lines']
            new_lines = mutate_lines(prev_lines, self.vocab, self.config.mutation_rate)
            new_vid = get_short_hash()
            chain.append({'id': new_vid, 'lines': new_lines})
            
        return chain

    def select_pair(self, chain):
        idxs = list(range(len(chain)))
        i = random.choice(idxs)
        j = random.choice([x for x in idxs if x != i])
        return chain[i], chain[j]

class DiffPrediction(VersionedTask, Task):
    def generate(self):
        chain = self.generate_version_chain()
        src, tgt = self.select_pair(chain)
        diff_str = get_git_diff(src['lines'], tgt['lines'])
        if not diff_str.strip() and  self.balancing_key_ratio<random.random():
            # No changes between versions; regenerate
            return self.generate()
        history_text = []
        for v in chain:
            content = with_lineno(v['lines'])
            history_text.append(f"Version {v['id']}:\n{content}\n")

        meta = edict(
            history="\n".join(history_text),
            src_id=src['id'],
            tgt_id=tgt['id'],
            src_text="\n".join(src['lines']),
            tgt_text="\n".join(tgt['lines'])
        )
        return Problem(meta, diff_str)

    def prompt(self, meta):
        return (f"Below is the version history of a file.\n\n"
                f"{meta.history}\n"
                f"Generate the Unified Diff to transform version {meta.src_id} into version {meta.tgt_id}.\n"
                f"The answer is the diff chunks only (no file headers), or empty if no changes.")

    def score_answer(self, answer, entry):
        meta = entry.get('metadata', {})
        src_text = meta.get('src_text')
        tgt_text = meta.get('tgt_text')
        
        if not src_text or not tgt_text:
            return Levenshtein.normalized_similarity(answer.strip(), entry['answer'].strip())

        try:
            patches = list(whatthepatch.parse_patch(answer))
            if not patches:
                patched_text = src_text
            else:
                patched_lines = whatthepatch.apply_diff(patches[0], src_text)
                patched_text = "\n".join(patched_lines)
            return Levenshtein.normalized_similarity(patched_text.strip(), tgt_text.strip())
        except Exception:
            return Levenshtein.normalized_similarity(answer.strip(), entry['answer'].strip())

import copy, json

@dataclass
class ConfigEditionConfig(Config):
    nb_sections: int = 4
    fields_per_section: int = 4
    nb_ops: int = 3
    max_depth: int = 2
    alias_rate: float = 0.25
    distractor_rate: float = 0.10
    dependency_rate: float = 0.15
    conflict_rate: float = 0.10
    list_rate: float = 0.20

    def update(self, c):
        self.nb_sections += c // 2
        self.fields_per_section += c // 3
        self.nb_ops += c
        self.max_depth = min(4, self.max_depth + c // 3)
        self.alias_rate = min(0.70, self.alias_rate + 0.04 * c)
        self.distractor_rate = min(0.45, self.distractor_rate + 0.03 * c)
        self.dependency_rate = min(0.60, self.dependency_rate + 0.04 * c)
        self.conflict_rate = min(0.45, self.conflict_rate + 0.035 * c)
        self.list_rate = min(0.55, self.list_rate + 0.035 * c)


class ConfigEdition(DevTask):
    value_pools = {
        "id": ["small", "base", "large", "fast", "accurate"],
        "backend": ["local", "cuda", "mps", "remote"],
        "precision": ["fp32", "fp16", "bf16", "int8"],
        "temperature": [0.0, 0.1, 0.2, 0.5, 0.7, 1.0],
        "top_p": [0.7, 0.8, 0.9, 0.95, 1.0],
        "max_tokens": [128, 256, 512, 1024, 2048],
        "batch_size": [8, 16, 32, 64, 128],
        "epochs": [1, 2, 3, 5, 10],
        "shuffle": [True, False],
        "seed": [0, 1, 7, 42, 1234],
        "enabled": [True, False],
        "ttl": [60, 300, 900, 3600, 86400],
        "timeout": [5, 10, 30, 60, 120],
        "retries": [0, 1, 2, 3, 5],
        "level": ["debug", "info", "warning", "error"],
        "format": ["text", "json", "compact"],
        "save_traces": [True, False],
        "endpoint": ["/v1/run", "/v1/chat", "/api/predict", "/health"],
        "port": [8000, 8080, 9000, 5000],
        "private": [True, False],
        "owner": ["research", "platform", "infra", "evals"],
        "mode": ["train", "eval", "serve", "debug"],
        "metrics": [["loss"], ["accuracy"], ["loss", "accuracy"], ["latency", "throughput"]],
        "features": [["cache"], ["streaming"], ["cache", "streaming"], ["logging", "tracing"]],
        "tags": [["baseline"], ["prod"], ["experimental"], ["debug", "nightly"]],
    }

    section_pools = {
        "model": ["id", "backend", "precision", "temperature", "top_p", "max_tokens"],
        "training": ["batch_size", "epochs", "shuffle", "seed", "metrics"],
        "cache": ["enabled", "ttl", "backend"],
        "logging": ["level", "format", "save_traces"],
        "server": ["endpoint", "port", "timeout", "retries"],
        "security": ["enabled", "private", "owner"],
        "runtime": ["mode", "timeout", "retries", "features"],
        "data": ["shuffle", "batch_size", "seed", "tags"],
        "evaluation": ["enabled", "batch_size", "metrics", "save_traces"],
    }

    new_key_pool = [
        "description", "owner", "format", "timeout", "retries", "enabled",
        "mode", "priority", "version", "ttl", "tags", "features", "save_traces"
    ]

    def __init__(self, config=ConfigEditionConfig()):
        super().__init__(config=config)

    def sample_value(self, key, old=None):
        if key in self.value_pools:
            values = copy.deepcopy(self.value_pools[key])
        elif key.endswith(("enabled", "private")) or key.startswith(("use_", "save_")):
            values = [True, False]
        elif key.endswith(("size", "count", "limit", "ttl", "timeout", "retries")):
            values = [0, 1, 2, 4, 8, 16, 32, 64, 128]
        elif key.endswith(("tags", "features", "metrics")):
            values = [["baseline"], ["fast"], ["stable"], ["debug", "nightly"]]
        else:
            values = ["alpha", "beta", "stable", "experimental", "default"]

        if old is not None and len(values) > 1:
            values = [v for v in values if v != old] or values
        return copy.deepcopy(random.choice(values))

    def generate_object(self):
        section_names = list(self.section_pools)
        n_sections = min(len(section_names), max(2, self.config.nb_sections))
        sections = random.sample(section_names, n_sections)
        obj = {}

        for section in sections:
            keys = self.section_pools[section][:]
            if random.random() > self.config.list_rate:
                keys = [k for k in keys if k not in {"metrics", "features", "tags"}] or keys
            random.shuffle(keys)
            n_fields = min(len(keys), max(2, self.config.fields_per_section))
            obj[section] = {k: self.sample_value(k) for k in keys[:n_fields]}

        for _ in range(max(0, self.config.max_depth - 2)):
            section = random.choice(list(obj))
            nested_key = random.choice(["limits", "defaults", "policy", "metadata"])
            if nested_key in obj[section]:
                continue
            nested_fields = random.sample(["enabled", "timeout", "retries", "owner", "mode"], 2)
            obj[section][nested_key] = {k: self.sample_value(k) for k in nested_fields}

        return obj

    def iter_leaf_paths(self, obj, prefix=()):
        if isinstance(obj, dict):
            if not obj:
                yield prefix
            for key, value in obj.items():
                yield from self.iter_leaf_paths(value, prefix + (key,))
        else:
            yield prefix

    def iter_dict_paths(self, obj, prefix=()):
        if isinstance(obj, dict):
            yield prefix
            for key, value in obj.items():
                yield from self.iter_dict_paths(value, prefix + (key,))

    def get_value(self, obj, path):
        cur = obj
        for key in path:
            cur = cur[key]
        return cur

    def get_parent(self, obj, path):
        cur = obj
        for key in path[:-1]:
            cur = cur[key]
        return cur

    def set_value(self, obj, path, value):
        self.get_parent(obj, path)[path[-1]] = value

    def delete_value(self, obj, path):
        del self.get_parent(obj, path)[path[-1]]

    def rename_key(self, obj, path, new_key):
        parent = self.get_parent(obj, path)
        parent[new_key] = parent.pop(path[-1])

    def choose_path(self, obj, pred=lambda value: True, recent_paths=None):
        paths = [p for p in self.iter_leaf_paths(obj) if p and pred(self.get_value(obj, p))]
        if not paths:
            return None
        recent_paths = recent_paths or []
        eligible_recent = [p for p in recent_paths if p in paths]
        if eligible_recent and random.random() < self.config.dependency_rate:
            return random.choice(eligible_recent)
        return random.choice(paths)

    def choose_dict_path(self, obj):
        return random.choice(list(self.iter_dict_paths(obj)))

    def fresh_key(self, parent, preferred=None):
        candidates = self.new_key_pool[:]
        if preferred:
            candidates = [preferred] + candidates
        random.shuffle(candidates)
        for key in candidates:
            if key not in parent:
                return key
        while True:
            key = fake.word().replace("-", "_")
            if key not in parent:
                return key

    def make_set(self, obj, recent_paths):
        path = self.choose_path(obj, lambda v: not isinstance(v, (dict, list)), recent_paths)
        if not path:
            return None
        old = self.get_value(obj, path)
        return edict(kind="set", path=path, old=old, value=self.sample_value(path[-1], old))

    def make_toggle(self, obj, recent_paths):
        path = self.choose_path(obj, lambda v: isinstance(v, bool), recent_paths)
        if not path:
            return None
        old = self.get_value(obj, path)
        return edict(kind="toggle", path=path, old=old, value=not old)

    def make_increment(self, obj, recent_paths):
        path = self.choose_path(obj, lambda v: isinstance(v, int) and not isinstance(v, bool), recent_paths)
        if not path:
            return None
        old = self.get_value(obj, path)
        delta = random.choice([-10, -5, -2, -1, 1, 2, 5, 10])
        if old + delta < 0:
            delta = abs(delta)
        return edict(kind="increment", path=path, old=old, delta=delta, value=old + delta)

    def make_delete(self, obj, recent_paths):
        paths = [p for p in self.iter_leaf_paths(obj) if p and len(self.get_parent(obj, p)) > 1]
        if not paths:
            return None
        path = random.choice(paths)
        return edict(kind="delete", path=path, old=self.get_value(obj, path))

    def make_rename(self, obj, recent_paths):
        paths = [p for p in self.iter_leaf_paths(obj) if p and len(p) >= 2]
        if not paths:
            return None
        path = random.choice(paths)
        parent = self.get_parent(obj, path)
        new_key = self.fresh_key(parent)
        return edict(
            kind="rename",
            path=path,
            new_path=path[:-1] + (new_key,),
            old_key=path[-1],
            new_key=new_key,
            old=self.get_value(obj, path),
        )

    def make_append(self, obj, recent_paths):
        path = self.choose_path(obj, lambda v: isinstance(v, list), recent_paths)
        if not path:
            return None
        old = self.get_value(obj, path)
        candidates = ["cache", "streaming", "tracing", "latency", "throughput", "nightly", "stable", "audit"]
        values = [v for v in candidates if v not in old] or candidates
        return edict(kind="append", path=path, value=random.choice(values))

    def make_add(self, obj, recent_paths):
        parent_path = self.choose_dict_path(obj)
        parent = self.get_value(obj, parent_path) if parent_path else obj
        key = self.fresh_key(parent)
        return edict(kind="add", path=parent_path + (key,), key=key, value=self.sample_value(key))

    def make_conflict(self, obj, recent_paths):
        path = self.choose_path(obj, lambda v: not isinstance(v, (dict, list)), recent_paths)
        if not path:
            return None
        old = self.get_value(obj, path)
        if isinstance(old, bool):
            return edict(kind="toggle", path=path, old=old, value=not old)
        if isinstance(old, int) and not isinstance(old, bool):
            return self.make_increment(obj, [path])
        return edict(kind="set", path=path, old=old, value=self.sample_value(path[-1], old))

    def apply_op(self, obj, op):
        if op.kind in {"set", "toggle", "increment"}:
            self.set_value(obj, op.path, op.value)
        elif op.kind == "delete":
            self.delete_value(obj, op.path)
        elif op.kind == "rename":
            self.rename_key(obj, op.path, op.new_key)
        elif op.kind == "append":
            self.get_value(obj, op.path).append(op.value)
        elif op.kind == "add":
            self.set_value(obj, op.path, op.value)

    def render_value(self, value):
        return json.dumps(value, sort_keys=True)

    def render_path(self, path):
        dot = ".".join(path)
        leaf = path[-1].replace("_", " ")
        parent = ".".join(path[:-1])

        aliases = {
            "cache.enabled": ["caching", "the cache"],
            "logging.level": ["the log level"],
            "logging.save_traces": ["trace saving"],
            "server.timeout": ["the server timeout"],
            "server.retries": ["server retry count"],
            "model.temperature": ["the model temperature"],
            "model.max_tokens": ["the token limit"],
            "training.batch_size": ["the training batch size"],
            "evaluation.enabled": ["evaluation"],
        }
        if dot in aliases and random.random() < self.config.alias_rate:
            return random.choice(aliases[dot])

        if not parent:
            return f"`{dot}`"

        templates = [
            "`{dot}`",
            "the `{leaf}` field under `{parent}`",
            "`{parent}`'s `{leaf}`",
        ]
        return random.choice(templates).format(dot=dot, leaf=leaf, parent=parent)

    def render_op(self, op):
        p = self.render_path(op.path)

        if op.kind == "set":
            return random.choice([
                f"set {p} to {self.render_value(op.value)}",
                f"change {p} from {self.render_value(op.old)} to {self.render_value(op.value)}",
                f"update {p}: {self.render_value(op.value)}",
            ])

        if op.kind == "toggle":
            if op.value is True:
                return random.choice([f"enable {p}", f"turn on {p}", f"set {p} to true"])
            return random.choice([f"disable {p}", f"turn off {p}", f"set {p} to false"])

        if op.kind == "increment":
            direction = "increase" if op.delta > 0 else "decrease"
            return f"{direction} {p} by {abs(op.delta)}"

        if op.kind == "delete":
            return random.choice([
                f"remove {p}",
                f"delete {p}",
                f"drop {p} from the config",
            ])

        if op.kind == "rename":
            return random.choice([
                f"rename {self.render_path(op.path)} to `{op.new_key}`",
                f"rename key `{op.old_key}` under `{'.'.join(op.path[:-1])}` to `{op.new_key}`",
            ])

        if op.kind == "append":
            return random.choice([
                f"append {self.render_value(op.value)} to {p}",
                f"add {self.render_value(op.value)} to the list at {p}",
            ])

        if op.kind == "add":
            return random.choice([
                f"add {self.render_path(op.path)} with value {self.render_value(op.value)}",
                f"create {self.render_path(op.path)} set to {self.render_value(op.value)}",
            ])

    def render_noop(self, obj, changed_paths):
        paths = [p for p in self.iter_leaf_paths(obj) if p not in changed_paths]
        if not paths:
            return None
        path = random.choice(paths)
        return random.choice([
            f"leave {self.render_path(path)} unchanged",
            f"do not modify {self.render_path(path)}",
        ])

    def generate_ops(self, obj):
        obj = copy.deepcopy(obj)
        ops = []
        instructions = []
        recent_paths = []
        changed_paths = set()

        def path_key(path):
            return tuple(path)

        makers = [
            (self.make_set, 3.0),
            (self.make_toggle, 1.5),
            (self.make_increment, 1.3),
            (self.make_add, 1.8),
            (self.make_delete, 1.0),
            (self.make_rename, 1.0),
            (self.make_append, 1.0),
        ]

        for _ in range(self.config.nb_ops):
            if recent_paths and random.random() < self.config.conflict_rate:
                op = self.make_conflict(obj, recent_paths)
            else:
                funcs, weights = zip(*makers)
                op = None
                for _attempt in range(8):
                    func = random.choices(funcs, weights=weights)[0]
                    op = func(obj, recent_paths)
                    if op:
                        break

            if not op:
                continue

            instructions.append(self.render_op(op))
            self.apply_op(obj, op)
            ops.append(op)

            if op.kind == "rename":
                recent_paths.append(path_key(op.new_path))
                changed_paths.add(path_key(op.path))
                changed_paths.add(path_key(op.new_path))
            else:
                recent_paths.append(path_key(op.path))
                changed_paths.add(path_key(op.path))

        for _ in range(max(0, int(round(self.config.nb_ops * self.config.distractor_rate)))):
            noop = self.render_noop(obj, changed_paths)
            if noop:
                instructions.insert(random.randint(0, len(instructions)), noop)

        return instructions, obj

    def dump_json(self, obj):
        return json.dumps(obj, indent=2, sort_keys=False)

    def generate(self):
        src = self.generate_object()
        instructions, tgt = self.generate_ops(src)

        meta = edict(
            src_text=self.dump_json(src),
            instructions="\n".join(f"{i + 1}. {x}" for i, x in enumerate(instructions)),
        )
        return Problem(meta, self.dump_json(tgt))

    def prompt(self, meta):
        return (
            "Apply the requested edits to the JSON config.\n"
            "Keep unrelated fields unchanged. Apply the instructions in order; if instructions conflict, later ones win.\n"
            "Preserve JSON data types. Return the updated JSON only.\n\n"
            f"Original config:\n{meta.src_text}\n\n"
            f"Change request:\n{meta.instructions}"
        )

    def strip_code_fence(self, text):
        text = str(text).strip()
        match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.S | re.I)
        if match:
            return match.group(1).strip()
        return text

    def parse_answer(self, text):
        return json.loads(self.strip_code_fence(text))

    def flatten(self, obj, prefix=()):
        if isinstance(obj, dict):
            if not obj:
                return {prefix: "{}"}
            flat = {}
            for key, value in obj.items():
                flat.update(self.flatten(value, prefix + (key,)))
            return flat
        if isinstance(obj, list):
            return {prefix: json.dumps(obj, sort_keys=True)}
        return {prefix: json.dumps(obj, sort_keys=True)}

    def object_similarity(self, pred, gold):
        pred_flat = self.flatten(pred)
        gold_flat = self.flatten(gold)

        if not pred_flat and not gold_flat:
            return 1.0

        exact = sum(1 for path, value in pred_flat.items() if gold_flat.get(path) == value)
        key_overlap = len(set(pred_flat) & set(gold_flat))

        precision = exact / max(1, len(pred_flat))
        recall = exact / max(1, len(gold_flat))
        exact_f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)

        key_precision = key_overlap / max(1, len(pred_flat))
        key_recall = key_overlap / max(1, len(gold_flat))
        key_f1 = 0.0 if key_precision + key_recall == 0 else 2 * key_precision * key_recall / (key_precision + key_recall)

        return 0.85 * exact_f1 + 0.15 * key_f1

    def score_answer(self, answer, entry):
        gold_text = entry["answer"]
        try:
            pred = self.parse_answer(answer)
            gold = self.parse_answer(gold_text)
            return self.object_similarity(pred, gold)
        except Exception:
            return Levenshtein.normalized_similarity(str(answer).strip(), str(gold_text).strip())


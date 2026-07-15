import random
import numpy as np
import datetime
import inflect
from dataclasses import dataclass
from reasoning_core.template import Task, Entry, Config, stochastic_rounding as sround
import itertools
import string
from ast import literal_eval

from faker import Faker
### Tool functions 🛠️

class SetList(list):
    def __repr__(self):
        # f-strings call __str__, which for lists defaults to calling this.
        return "{" + ", ".join(map(repr, self)) + "}"

def return_shuffle(domain):
    """Domain must be a collection of element convertible in list"""
    # Cast to SetList so it prints with curly braces but behaves like a list
    domain = SetList(domain)
    random.shuffle(domain)
    return domain

def random_subdomain(domain, size=None):
    """Domain must be a collection of element convertible in list, and frac must be a float between 0 and 1. \n
    return a random fraction of the domain."""
    domain = list(domain)
    subset = random.sample(domain, size)
    return return_shuffle(subset)

def create_intension(domain : list, length : int):
        """Returns a contiguous subdomain (of domain) of size length."""
        n = len(domain)
        i = np.random.randint(n-length)
        return domain[i:i+length]

_inflect = inflect.engine()

def make_domains(size, ordered=False):

    NUM = [int(i) for i in range(1,size+1)]
    NUM_EN = [_inflect.number_to_words(i).replace(',', '') for i in NUM]
    start = (datetime.date(2020, 1, 1))
    DATES = [(start + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(size)]
    DATES_EN = [(start + datetime.timedelta(days=i)).strftime('%B %d, %Y') for i in range(size)]

    gen = itertools.chain.from_iterable((''.join(p) for p in itertools.product(string.ascii_lowercase, repeat=n)) for n in itertools.count(1))
    LETTERS = list(itertools.islice(gen, size))

    domains = [NUM, NUM_EN, DATES, DATES_EN, LETTERS]

    if not ordered:
        fake = Faker()
        fake.seed_instance(0)
        words = []
        words_set = set()
        for _ in range(size*3):
            w = f"{fake.word(part_of_speech='adjective')} {fake.word(part_of_speech='noun')}"
            if w not in words_set:
                words_set.add(w)
                words.append(w)
            if size<=len(words):
                break
        domains.insert(1, words)

    return domains

def intersection_metric(set1, set2):
    return len(set1 & set2)/len(set1 | set2)
    
### Task class 🎮 🎯

@dataclass
class SetOpsConfig(Config):
    domain_size: int = 1000
    set_size: int = 8
    n_domains : int = 2
    def apply_difficulty(self, level):
        self.set_size *= 2 ** level
        self.domain_size *= 2 ** level
        self.n_domains += level

@dataclass
class SetMissingElementConfig(SetOpsConfig):
    set_size: int = 10
    prob_no_missing: float = 0.1
    def apply_difficulty(self, level):
        # 2**level exploded set_size to 160 / domain to huge at L4 (~1080 tok): prompt-length tax made this a
        # net-hurter (global -0.29) despite a real bbh gain. Moderate 1.5**level ramp cuts the tax and flips it
        # to a helper (global +0.34, reward 0.63 non-trivial). Validated 2026-07-09 (RESCALE_AB_OLMO1B).
        self.set_size = sround(6 * 1.5 ** level)
        self.domain_size = sround(200 * 1.5 ** level)
        self.n_domains += level

class SetMissingElement(Task):
    """
    This is a perception task, goal is to probe attention sharpness. Domains are easy to guess.
    But LLMs tend to repeat elements from the input.
    https://aclanthology.org/2025.findings-ijcnlp.44.pdf
    """
    summary = "Identify missing elements from a shuffled sequence defined by set intension."
    def __init__(self, config=None):
        super().__init__(config=config or SetMissingElementConfig())
        self.balancing_key_ratio = 0.25
        self.domains = make_domains(self.config.domain_size, ordered=True)
        
    def generate_entry(self):
        chosen_domain = random.choice(self.domains[:self.config.n_domains])
        intention = create_intension(chosen_domain, self.config.set_size)
        n_missing = 0 if random.random() < self.config.prob_no_missing else random.randint(1, 3)
        removable = intention[1:-1]
        missing = sorted(random.sample(removable, min(n_missing, len(removable))), key=str)
        for e in missing: intention.remove(e)
        answer = "{" + ", ".join(map(repr, missing)) + "}"
        return Entry(metadata={'element_list': return_shuffle(intention), 'missing_count': len(missing)}, answer=answer)

    def render_prompt(self, metadata) -> str:
        S = metadata["element_list"]
        return f"Answer with the missing elements in the ordered span of {S} as a Python set."


    def score_answer(self, answer, entry):
        try:
            pred, truth = set(literal_eval(answer)), set(literal_eval(entry['answer']))
            return int(pred == truth) if not truth else intersection_metric(pred, truth)
        except:
            return 0

    def balancing_key(self, problem):
        n = problem.metadata.missing_count
        return f"missing_count={n if n < 3 else '3+'}"

@dataclass
class CountElementsConfig(Config):
    max_count: int = 3
    list_size: int = 10
    domain_size: int = 20
    def apply_difficulty(self, level):
        self.max_count += level
        self.list_size += level
        self.domain_size *= 2 ** level

class CountElements(Task):
    summary = "Count occurrences of a target element within a randomly generated list."
    def __init__(self, config=None):
        super().__init__(config=config or CountElementsConfig())
        self.domains = make_domains(self.config.domain_size)

    def generate_entry(self):
        count = random.randint(0, self.config.max_count)
        domain = random.choice(self.domains)
        target = random.choice(domain)
        others = [e for e in domain if e != target]
        n_others = self.config.list_size - count
        elements = [target] * count + random.choices(others, k=n_others)
        random.shuffle(elements)
        return Entry(metadata={'elements': elements, 'target': target}, answer=str(count))

    def render_prompt(self, metadata) -> str:
        return f"List: {metadata['elements']}\nHow many times does {metadata['target']!r} appear? The answer is a number."

    def score_answer(self, answer, entry):
        try: return 1 / (1 + abs(int(answer.strip()) - int(entry['answer'])))
        except: return 0

def _elem_key(x):
    return (0, x) if isinstance(x, int) else (1, str(x))


def _sorted(xs):
    return sorted(xs, key=_elem_key)


def repr_set(xs):
    xs = _sorted(xs)
    return "{}" if not xs else "{" + ", ".join(map(repr, xs)) + "}"


def repr_prompt_set(xs):
    xs = list(xs)
    return "{}" if not xs else "{" + ", ".join(map(repr, xs)) + "}"


def repr_answer(x):
    if isinstance(x, set):
        return repr_set(x)

    if isinstance(x, list):
        return "[" + ", ".join(map(repr, x)) + "]"

    return str(x)


def parse_set_like(x):
    x = x.strip()
    return set() if x in {"{}", "set()"} else set(literal_eval(x))


@dataclass
class Expr:
    src: str
    value: object
    kind: str
    vars: set


@dataclass
class Pred:
    src: str
    fn: object
    vars: set


def expr(src, value, kind, vars=()):
    return Expr(src, value, kind, set(vars))


def pred(src, fn, vars=()):
    return Pred(src, fn, set(vars))


def set_bin(left, op, right):
    if op == "&":
        value = left.value & right.value
    elif op == "|":
        value = left.value | right.value
    elif op == "-":
        value = left.value - right.value
    elif op == "^":
        value = left.value ^ right.value
    else:
        raise ValueError(op)

    return expr(
        f"({left.src} {op} {right.src})",
        value,
        "set",
        left.vars | right.vars,
    )


def len_expr(e):
    return expr(f"len({e.src})", len(e.value), "number", e.vars)


def sorted_expr(e):
    return expr(f"sorted({e.src})", _sorted(e.value), "list", e.vars)


def set_var(env):
    name = random.choice("ABC")
    return expr(name, env[name], "set", {name})


def set_from_list_var(env):
    name = random.choice("ABC")
    return expr(f"set({name})", set(env[name]), "set", {name})


def make_pred(env, source=None, v="x"):
    names = [n for n in "ABC" if n != source] or list("ABC")
    elems = _sorted(env[source] if source else {e for xs in env.values() for e in xs})
    y = random.choice(names)
    z = random.choice(elems)

    return random.choice([
        lambda: pred(
            f"{v} in {y}",
            lambda x, y=y: x in env[y],
            {y},
        ),
        lambda: pred(
            f"{v} not in {y}",
            lambda x, y=y: x not in env[y],
            {y},
        ),
        lambda: pred(
            f"{y}.count({v}) > 1",
            lambda x, y=y: env[y].count(x) > 1,
            {y},
        ),
        lambda: pred(
            f"{v} == {z!r}",
            lambda x, z=z: x == z,
        ),
        lambda: pred(
            f"{v} != {z!r}",
            lambda x, z=z: x != z,
        ),
    ])()


def and_pred(p, q):
    return pred(
        f"{p.src} and {q.src}",
        lambda x, p=p, q=q: p.fn(x) and q.fn(x),
        p.vars | q.vars,
    )


def make_cond(env, source=None):
    p = make_pred(env, source)

    if random.random() < 0.25:
        p = and_pred(p, make_pred(env, source))

    return p


def list_comp(env):
    name = random.choice("ABC")
    p = make_cond(env, name)
    value = [x for x in env[name] if p.fn(x)]

    return expr(
        f"[x for x in {name} if {p.src}]",
        value,
        "list",
        {name} | p.vars,
    )


def useful_list_comp(env, attempts=8):
    e = list_comp(env)

    if not e.value:
        for _ in range(attempts):
            candidate = list_comp(env)
            if candidate.value:
                return candidate

    return e


def set_comp(env):
    name = random.choice("ABC")
    p = make_cond(env, name)
    value = {x for x in env[name] if p.fn(x)}

    return expr(
        "{" + f"x for x in {name} if {p.src}" + "}",
        value,
        "set",
        {name} | p.vars,
    )


def set_from_list_comp(env):
    e = useful_list_comp(env)
    return expr(f"set({e.src})", set(e.value), "set", e.vars)


def list_count_expr(env):
    name = random.choice("ABC")
    x = random.choice(env[name])

    return expr(
        f"{name}.count({x!r})",
        env[name].count(x),
        "number",
        {name},
    )


def sum_count_expr(env):
    name = random.choice("ABC")
    for _ in range(8):
        p = make_cond(env, name)
        value = sum(1 for x in env[name] if p.fn(x))
        if value:
            break

    return expr(
        f"sum(1 for x in {name} if {p.src})",
        value,
        "number",
        {name} | p.vars,
    )


def compose_set_expr(term, min_depth, max_depth, ops="&|-^"):
    def part(depth):
        if depth >= max_depth or (depth >= min_depth and random.random() < 0.75):
            return term()

        return binary(depth)

    def binary(depth):
        left = part(depth + 1)
        right = part(depth + 1)

        for _ in range(3):
            if right.src != left.src:
                break

            right = part(depth + 1)

        return set_bin(left, random.choice(ops), right)

    return binary(0)


def make_set_expr_value(env, min_depth, max_depth):
    e = compose_set_expr(
        lambda: set_var(env),
        min_depth,
        max_depth,
        ops="&&&--|^",
    )

    return len_expr(e) if random.random() < 0.35 else e


def make_list_expr_value(env, min_depth, max_depth):
    def set_term():
        return random.choice([
            lambda: set_from_list_var(env),
            lambda: set_from_list_comp(env),
            lambda: set_comp(env),
        ])()

    def set_expr():
        return compose_set_expr(
            set_term,
            min_depth,
            max_depth,
            ops="&&&--|^",
        )

    def filtered_set_op():
        left = set_from_list_comp(env)
        right = set_term()
        return sorted_expr(set_bin(left, random.choice("&&&--|^"), right))

    return random.choice([
        lambda: useful_list_comp(env),
        lambda: len_expr(useful_list_comp(env)),
        lambda: sum_count_expr(env),
        lambda: list_count_expr(env),
        lambda: sorted_expr(set_expr()),
        lambda: len_expr(set_expr()),
        filtered_set_op,
    ])()


def with_dupes(xs, dup_prob=0.35):
    xs = _sorted(xs)
    random.shuffle(xs)
    pool = xs[:]

    for i in range(len(xs)):
        if random.random() < dup_prob:
            xs[i] = random.choice(pool)

    return xs


def make_similar_lists(domain, k, dup_prob=0.0):
    base = list(random_subdomain(domain, k))

    if dup_prob:
        pool = base[:]

        for i in range(k):
            if random.random() < dup_prob:
                base[i] = random.choice(pool)

    rest = [x for x in domain if x not in set(base)]
    edit_cap = min(max(1, k // 4), len(rest))
    n_edits = random.randint(1, edit_cap) if edit_cap else 0

    env = {}

    for name in "ABC":
        xs = list(base)

        if n_edits:
            positions = random.sample(range(k), n_edits)
            replacements = random.sample(rest, n_edits)

            for i, replacement in zip(positions, replacements):
                xs[i] = replacement

        env[name] = xs

    return env


@dataclass
class SetExpressionConfig(Config):
    domain_size: int = 32
    set_size: int = 8
    n_domains: int = 2
    min_depth: int = 1
    max_depth: int = 2

    diff_like_prob: float = 0.15
    list_prob: float = 0.25
    list_dup_prob: float = 0.35

    def apply_difficulty(self, level):
        # 2**level exploded set_size to 128 at L4 (~1170 tok) — length tax trimmed the transfer. Moderate
        # 1.5**level ramp on set_size/domain (KEEP max_depth+level, the real nesting-difficulty lever) cuts the
        # tax: global +2.06 -> +2.35, bbh +8.7, reward 0.68 non-trivial. Validated 2026-07-09 (RESCALE_AB_OLMO1B).
        self.set_size = sround(6 * 1.5 ** level)
        self.domain_size = sround(32 * 1.5 ** level)
        self.n_domains += level
        self.max_depth += level


class SetExpression(Task):
    summary = "Evaluate complex set expressions involving union, intersection, and nested lists."
    def __init__(self, config=None):
        super().__init__(config=config or SetExpressionConfig())
        self.balancing_key_ratio = 0.25
        self.domains = make_domains(self.config.domain_size)

    def on_config_level_change(self):
        self.domains = make_domains(self.config.domain_size)

    def make_env(self, domain, list_mode=False):
        k = min(self.config.set_size, len(domain))

        if self.config.diff_like_prob and random.random() < self.config.diff_like_prob:
            shown = make_similar_lists(
                domain,
                k,
                dup_prob=self.config.list_dup_prob if list_mode else 0.0,
            )
            env = shown if list_mode else {x: set(shown[x]) for x in "ABC"}
            return env, shown

        core_size = random.randint(max(1, k // 4), max(1, k // 2))
        core = random_subdomain(domain, core_size)
        rest = [x for x in domain if x not in set(core)]

        env = {
            x: set(core + random.sample(rest, k - len(core)))
            for x in "ABC"
        }

        if list_mode:
            env = {
                x: with_dupes(env[x], self.config.list_dup_prob)
                for x in "ABC"
            }

        return env, None

    def generate_entry(self):
        domain = random.choice(self.domains[:self.config.n_domains])
        list_mode = random.random() < self.config.list_prob
        env, shown = self.make_env(domain, list_mode=list_mode)

        e = (
            make_list_expr_value(env, self.config.min_depth, self.config.max_depth)
            if list_mode
            else make_set_expr_value(env, self.config.min_depth, self.config.max_depth)
        )

        meta = {
            "expr": e.src,
            "list_mode": list_mode,
        }

        for x in e.vars:
            if list_mode:
                meta[x] = env[x]
            else:
                meta[x] = shown[x] if shown else return_shuffle(env[x])

        return Entry(metadata=meta, answer=repr_answer(e.value))

    def render_prompt(self, m):
        lines = []

        for x in "ABC":
            if x not in m:
                continue

            value = repr(m[x]) if m.get("list_mode") else repr_prompt_set(m[x])
            lines.append(f"{x} = {value}")

        return "\n".join(lines) + f"\nEvaluate {m['expr']}."

    def score_answer(self, answer, entry):
        truth = entry["answer"]
        answer = answer.strip()

        try:
            if truth in {"True", "False"}:
                return int(answer == truth)

            if truth.lstrip("-").isdigit():
                return 1 / (1 + abs(int(answer) - int(truth)))

            if truth.startswith("["):
                pred = literal_eval(answer)
                truth = literal_eval(truth)
                return int(isinstance(pred, list) and pred == truth)

            pred = parse_set_like(answer)
            truth = parse_set_like(truth)

            return int(pred == truth) if not truth else intersection_metric(pred, truth)

        except Exception:
            return 0

    def balancing_key(self, problem):
        answer = problem.answer
        mode = "list" if problem.metadata.get("list_mode") else "set"

        if answer in {"True", "False"}:
            return f"{mode}:bool:{answer}"

        if answer.lstrip("-").isdigit():
            return f"{mode}:number:{answer}"

        try:
            if answer.startswith("["):
                return f"{mode}:list:{len(literal_eval(answer))}"

            return f"{mode}:set:{len(parse_set_like(answer))}"

        except Exception:
            return f"{mode}:expr"

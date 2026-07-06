import random
import numpy as np
import datetime
import inflect
from dataclasses import dataclass
from reasoning_core.template import Task, Problem, Config
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
    def update(self, c):
        self.set_size *= 1 + c
        self.domain_size *= 1 + c
        self.n_domains += c

    def apply_difficulty(self, level):
        self.set_size *= 2 ** level
        self.domain_size *= 2 ** level
        self.n_domains += level

@dataclass
class SetMissingElementConfig(SetOpsConfig):
    set_size: int = 10
    prob_no_missing: float = 0.1
    def update(self, c):
        self.set_size *= 1 + c
        self.domain_size *= 1 + c
        self.n_domains += c

    def apply_difficulty(self, level):
        self.set_size *= 2 ** level
        self.domain_size *= 2 ** level
        self.n_domains += level

class SetMissingElement(Task):
    def __init__(self, config=SetMissingElementConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio = 0.25
        self.domains = make_domains(self.config.domain_size, ordered=True)
        
    def generate(self):
        chosen_domain = random.choice(self.domains[:self.config.n_domains])
        intention = create_intension(chosen_domain, self.config.set_size)
        n_missing = 0 if random.random() < self.config.prob_no_missing else random.randint(1, 3)
        removable = intention[1:-1]
        missing = sorted(random.sample(removable, min(n_missing, len(removable))), key=str)
        for e in missing: intention.remove(e)
        answer = "{" + ", ".join(map(repr, missing)) + "}"
        return Problem(metadata={'element_list': return_shuffle(intention), 'missing_count': len(missing)}, answer=answer)

    def prompt(self, metadata) -> str:
        return (
            f"Set_A: {metadata['element_list']}\n"
            "The answer is the missing elements from Set_A as a Python set."
        )

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
    def update(self, c):
        self.max_count += c
        self.list_size += c
        self.domain_size *= 1 + c

    def apply_difficulty(self, level):
        self.max_count += level
        self.list_size += level
        self.domain_size *= 2 ** level

class CountElements(Task):
    def __init__(self, config=CountElementsConfig()):
        super().__init__(config=config)
        self.domains = make_domains(self.config.domain_size)

    def generate(self):
        count = random.randint(0, self.config.max_count)
        domain = random.choice(self.domains)
        target = random.choice(domain)
        others = [e for e in domain if e != target]
        n_others = self.config.list_size - count
        elements = [target] * count + random.choices(others, k=n_others)
        random.shuffle(elements)
        return Problem(metadata={'elements': elements, 'target': target}, answer=str(count))

    def prompt(self, metadata) -> str:
        return f"List: {metadata['elements']}\nHow many times does {metadata['target']!r} appear? The answer is a number."

    def score_answer(self, answer, entry):
        try: return 1 / (1 + abs(int(answer.strip()) - int(entry['answer'])))
        except: return 0

def _elem_key(x):
    # Numeric-aware: sort ints by value, not lexicographically (sorted(key=str) gives the
    # scrambled {1, 18, 2, 21, ...}). Natural order is a cleaner gold string; strings stay
    # alphabetical. The tuple's leading 0/1 keeps mixed sets comparable.
    return (0, x) if isinstance(x, int) else (1, str(x))


class MSet(dict):
    """Multiset {element: count}. &, |, - give per-element min, max, floored difference."""
    def __and__(s, o): return MSet({k: min(s[k], o[k]) for k in s if k in o})
    def __or__(s, o):  return MSet({k: max(s.get(k, 0), o.get(k, 0)) for k in {*s, *o}})
    def __sub__(s, o): return MSet({k: s[k] - o.get(k, 0) for k in s if s[k] > o.get(k, 0)})


def _ms_elems(ms):  # elements with repetition, in canonical (sorted) order
    return sorted((e for e, c in ms.items() for _ in range(c)), key=_elem_key)


def repr_set(xs):
    xs = sorted(xs, key=_elem_key)
    return "{}" if not xs else "{" + ", ".join(map(repr, xs)) + "}"


def repr_answer(x):
    if isinstance(x, MSet):                    # multiset -> sorted list (repeats preserved & parseable)
        return "[" + ", ".join(map(repr, _ms_elems(x))) + "]"
    return repr_set(x) if isinstance(x, set) else str(x)


def eval_setops(expr, env, multiset=False):
    card = (lambda s: sum(s.values())) if multiset else len       # multiset Card = total multiplicity
    return eval(expr, {"__builtins__": {}},
                {"Card": card, "Count": lambda x, s: s.get(x, 0), **env})


def make_set_expr(min_depth, max_depth, ops="&|-^"):
    def part(depth):
        if depth >= max_depth or (depth >= min_depth and random.random() < 0.85):
            return random.choice("ABC")
        return binary(depth)

    def binary(depth):
        left = part(depth + 1)
        right = part(depth + 1)
        for _ in range(3):
            if right != left:
                break
            right = part(depth + 1)
        return f"({left}{random.choice(ops)}{right})"

    expr = binary(0)
    return f"Card({expr})" if random.random() < 0.25 else expr


@dataclass
class SetExpressionConfig(Config):
    domain_size: int = 32
    set_size: int = 8
    n_domains: int = 2
    min_depth: int = 1
    max_depth: int = 2
    diff_like_prob: float = 0.15
    multiset_prob: float = 0.35
    max_mult: int = 3

    def update(self, c):
        self.set_size *= 1 + c
        self.domain_size *= 1 + c
        self.n_domains += c
        self.max_depth += c
        self.max_mult += c

    def apply_difficulty(self, level):
        self.set_size *= 2 ** level
        self.domain_size *= 2 ** level
        self.n_domains += level
        self.max_depth += level
        self.max_mult += level

class SetExpression(Task):
    def __init__(self, config=SetExpressionConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio = 0.25
        self.domains = make_domains(self.config.domain_size)

    def on_config_level_change(self):
        self.domains = make_domains(self.config.domain_size)

    def make_env(self, domain):
        k = self.config.set_size
        if self.config.diff_like_prob and random.random() < self.config.diff_like_prob:
            base = random_subdomain(domain, k)
            rest = [x for x in domain if x not in base]
            edit_cap = min(max(1, k // 4), len(rest))
            n_edits = random.randint(1, edit_cap) if edit_cap else 0
            shown = {}
            for name in "ABC":
                xs = SetList(base)
                edits = zip(random.sample(range(k), n_edits), random.sample(rest, n_edits))
                for i, replacement in edits:
                    xs[i] = replacement
                shown[name] = xs
            return {x: set(shown[x]) for x in "ABC"}, shown

        core = random_subdomain(domain, random.randint(max(1, k // 4), max(1, k // 2)))
        rest = list(set(domain) - set(core))
        env = {x: set(core + random.sample(rest, k - len(core))) for x in "ABC"}
        return env, None

    def generate(self):
        domain = random.choice(self.domains[:self.config.n_domains])
        env, shown = self.make_env(domain)
        # multiset only for the plain-random case — keep the diff-like "same ordered + edits" mode
        multiset = shown is None and random.random() < self.config.multiset_prob
        if multiset:
            env = {x: MSet({e: random.randint(1, self.config.max_mult) for e in env[x]}) for x in env}
        expr = make_set_expr(self.config.min_depth, self.config.max_depth, "&|-" if multiset else "&|-^")
        if multiset and "Card(" not in expr and random.random() < 0.4:   # counting op (subsumes count_elements)
            pool = sorted(set().union(*(set(env[x]) for x in "ABC")), key=_elem_key)
            expr = f"Count({random.choice(pool)!r}, {expr})"
        answer = eval_setops(expr, env, multiset)

        used = expr.replace("Card", "").replace("Count", "")   # set vars only, not the Card/Count keywords
        meta = {"expr": expr, "multiset": multiset}
        for x in "ABC":
            if x not in used:
                continue
            if multiset:
                xs = _ms_elems(env[x]); random.shuffle(xs); meta[x] = xs
            else:
                meta[x] = shown[x] if shown else return_shuffle(env[x])
        return Problem(metadata=meta, answer=repr_answer(answer))

    def prompt(self, m):
        sets = "\n".join(f"{x}: {m[x]}" for x in "ABC" if x in m)
        note = ("\nA, B, C are multisets (elements repeat); &, |, - combine counts by min, max, "
                "subtract; Count(x, S) is x's count. Give a multiset result as a sorted list."
                if m.get("multiset") else "")
        return f"{sets}\nEvaluate {m['expr']}.{note}"

    def score_answer(self, answer, entry):
        truth = entry["answer"]

        try:
            if truth in {"True", "False"}:
                return int(answer.strip() == truth)

            if truth.lstrip("-").isdigit():
                return 1 / (1 + abs(int(answer) - int(truth)))

            if truth.startswith("["):                     # multiset: multiplicity-aware, order-invariant
                return int(sorted(literal_eval(answer)) == sorted(literal_eval(truth)))

            pred = set() if answer.strip() == "set()" else set(literal_eval(answer))
            truth = set() if truth == "set()" else set(literal_eval(truth))
            return int(pred == truth) if not truth else intersection_metric(pred, truth)

        except Exception:
            return 0

    def balancing_key(self, problem):
        answer = problem.answer
        if answer in {"True", "False"}:
            return f"bool:{answer}"
        if answer.lstrip("-").isdigit():
            return f"number:{answer}"
        try:
            xs = set() if answer in {"{}", "set()"} else set(literal_eval(answer))
            return f"set:{len(xs)}"
        except Exception:
            return "set"

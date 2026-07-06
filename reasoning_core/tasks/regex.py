import json
import random, re, itertools
from pathlib import Path
import string
import exrex
import regex
from dataclasses import dataclass
from gramforge import init_grammar, generate
from reasoning_core.template import Task, DevTask, Problem, register_dataset, Reward, Config
from easydict import EasyDict as edict
from faker import Faker
import sys, os
from functools import wraps
import codecs
from collections import defaultdict

#import re2 as re
r"""
ROADMAP:
Explicit Quantifiers ({n}, {n,m})
Explicit Character Sets ([abc])
Negated Character Classes ([^a-z], [^abc])
Escaped Literals (\+, \*, \?, etc.)
Non-Capturing Groups ((?:...))
"""


def shutup(f):
    @wraps(f)
    def wrapper(*a, **kw):
        with open(os.devnull, 'w') as devnull:
            old = sys.stdout
            sys.stdout = devnull
            try: return f(*a, **kw)
            finally: sys.stdout = old
    return wrapper


fake = Faker()

wordlist = fake.words(nb=100,unique=True)


def regex_grammar(fsm_subset=False, alpha=None, words=None):
    R = init_grammar(["re"], preprocess_template=lambda x: x)

    R("start(regex)", "{0}")
    R("regex(regex,regex)", "{0}{1}", weight=2)
    R("regex(regex)", "({0})", weight=2)
    R("regex(regex,regex)", "{0}|{1}", weight=1)
    R("regex(char)", "{0}", weight=1)
    R("regex(word)", "{0}", weight=1)

    if fsm_subset: #greenery
        assert alpha and words
        R("regex(regex)?", "{0}?")
        R("regex(regex)*", "{0}*")
        R("regex(regex)+", "{0}+")
        for w in words: R("word", w)
        for c in alpha: R("char", c)
        return R

    for w in random.sample(wordlist, 8):
        R("word", w)

    R("regex(regex)?", "{0}?")
    R("regex(regex)*", "{0}*")
    R("regex(regex)+", "{0}+")

    for i in range(1, 4):
        R("count_exact", "{{%d}}" % i)
        for j in range(i + 1, 6):
            R("count_range", "{{%d,%d}}" % (i, j))

    R("regex(regex,count_exact)", "{0}{1}")
    R("regex(regex,count_range)", "{0}{1}")

    R("regex(rangechar,rangechar)", "[{0}-{1}]")
    R("regex(rangechar,rangechar)", "[^{0}-{1}]")
    R("regex(char,char,char)", "[{0}{1}{2}]")
    R("regex(char,char,char)", "[^{0}{1}{2}]")

    R("regex(regex)", "(?:{0})")

    R("regex(predef)", "{0}", weight=3)

    for c in string.ascii_letters + string.digits:
        R("char", c)
        R("rangechar", c)

    for s in [r"\d", r"\w", ".", r"\."]:
        R("predef", s, weight=1)

    for s in [r"\D", r"\W"]:
        R("predef", s, weight=0.25)

    for s in [r"\+", r"\*", r"\?", r"\\", r"\(", r"\)", r"\[", r"\]"]:
        R("predef", s, weight=0.25)

    return R


@shutup
def safe_regex(r):
    try:
        sample_instance(r, max_tries=10)
        return True
    except (ValueError, Exception):
        return False

def sample_regex(config, max_tries=100):
    max_depth = config.max_depth
    min_depth = config.min_depth

    G = regex_grammar()
    for _ in range(max_tries):
        x = generate(G.start(), depth=max_depth, min_depth=min_depth, mode=config.gramforge_algorithm)
        if len(x.leaves)<=1:
            continue
        r = x @ 're'
        if safe_regex(r):
            return r
    raise RuntimeError("No valid regex found")



@dataclass
class RegexConfig(Config):
    n_ex: int = 8
    max_depth: int = 5
    min_depth: int = 3
    n_alpha: int = 4
    max_answer_len: int = 24
    max_synth_nodes: int = 200_000
    require_unique: bool = True
    gramforge_algorithm = "sequential"
    def update(self, c):
        self.n_ex += c
        self.max_depth += c
        self.min_depth += c

    def apply_difficulty(self, level):
        self.n_ex += level
        self.max_depth += level
        self.min_depth += level

@shutup
def sample_instance(r_str, max_tries=100):
    """Generates a non-empty string that is verified by re.fullmatch()."""
    try:
        #p = re.compile(r_str)
        p = regex.compile(r_str)

    except re.error:
        raise ValueError(f"Could not compile invalid regex: {r_str}")

    for _ in range(max_tries):
        s = exrex.getone(r_str, 5)
        # Verify the generated string is a non-empty full match and has no unprintable characters
        if s and s.isprintable() and p.fullmatch(s, timeout=5):
            return s
    raise ValueError(f"Could not generate a verified string for regex: {r_str}")

class RegexFollowing(Task):
    def __init__(self, config=RegexConfig()):
        super().__init__(config=config)

    def generate(self):
        meta = edict()
        r = sample_regex(self.config)
        meta.regex = r
        meta.string = sample_instance(r)
        return Problem(meta, meta.string)


    def score_answer(self, answer, entry):
        try:
            answer_str, pattern = str(answer), entry['metadata']['regex']
            expected_len = len(entry['metadata']['string'])
            target_len_penalty = abs(len(answer_str) - expected_len)
            
            max_edits = len(answer_str) + len(pattern)
            
            distance = next((e for e in range(min(max_edits, 10) + 1)
                            if regex.fullmatch(f'(?:{pattern}){{e<={e}}}', answer_str, timeout=0.5)),
                            max_edits) # Corrected parenthesis here
                            
            return 1.0 / (1.0 + distance + target_len_penalty)
        
        except (TimeoutError, regex.error):
            return None

    def prompt(self, meta):
        n = len(meta.string)
        return f"The answer is a {n}-character string that fully matches the regular expression: {meta.regex}"

    def balancing_key(self, problem):
        return problem.metadata.regex

def strip_anchors_safe(text: str) -> str:
    """Strips optional ^, non-escaped $, and markdown formatting from a regex string."""
    if "```" in text:
        m = regex.search(r"```(?:regex|re|text)?\n(.*?)\n```", text, regex.DOTALL)
        if m: text = m.group(1)
    text = text.strip('\r\n').strip('`').strip('\r\n')
    m = regex.match(r"^\^?(.*?)(?<!\\)\$?$", text)
    return m.group(1) if m else text


def _fullmatch_sig(pattern, strings):
    try:
        r = regex.compile(pattern)
        return tuple(bool(r.fullmatch(s, timeout=0.1)) for s in strings)
    except (regex.error, TimeoutError):
        return None


def _consistent(pattern, positives, negatives):
    strings = positives + negatives
    if "" not in positives and "" not in negatives:
        strings = strings + [""]
        negatives = negatives + [""]
    sig = _fullmatch_sig(pattern, strings)
    if sig is None:
        return False
    return sig == (True,) * len(positives) + (False,) * len(negatives)


def _uses_only_induction_syntax(pattern, alphabet):
    return all(c in set(alphabet) | set("|()*+?") for c in pattern)


def _wrap_postfix(x):
    return x if len(x) == 1 else f"({x})"


def _wrap_concat_arg(x):
    return f"({x})" if "|" in x and not (x.startswith("(") and x.endswith(")")) else x


def _concat(x, y):
    return f"{_wrap_concat_arg(x)}{_wrap_concat_arg(y)}"


def _alt(x, y):
    if x == y:
        return x
    a, b = sorted([x, y])
    return f"{a}|{b}"


def synthesize_shortest_regex(
    positives,
    negatives,
    alphabet,
    max_len=24,
    max_nodes=200_000,
    require_unique=True,
):
    examples = positives + negatives
    if "" not in positives and "" not in negatives:
        examples = examples + [""]
        negatives = negatives + [""]

    universe = {"", *alphabet, *examples}
    for s in examples:
        universe.update(s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1))
    universe.update("".join(p) for p in itertools.product(alphabet, repeat=2))
    universe = sorted(universe, key=lambda s: (len(s), s))
    index = {s: i for i, s in enumerate(universe)}
    pos_mask = sum(1 << index[s] for s in positives)
    neg_mask = sum(1 << index[s] for s in negatives)
    empty_mask = 1 << index[""]

    by_len = defaultdict(list)
    best_src_by_sig = {}
    target_by_len = defaultdict(set)
    sig_words = {}
    concat_cache = {}
    star_cache = {}
    nodes = 0

    def words(sig):
        if sig not in sig_words:
            sig_words[sig] = [s for s, i in index.items() if sig & (1 << i)]
        return sig_words[sig]

    def concat_sig(a, b):
        key = (a, b)
        if key not in concat_cache:
            out = 0
            for x in words(a):
                for y in words(b):
                    i = index.get(x + y)
                    if i is not None:
                        out |= 1 << i
            concat_cache[key] = out
        return concat_cache[key]

    def star_sig(sig):
        if sig not in star_cache:
            out = empty_mask
            prev = -1
            while out != prev:
                prev = out
                out |= concat_sig(out, sig)
            star_cache[sig] = out
        return star_cache[sig]

    def add(src, sig):
        nonlocal nodes
        if len(src) > max_len:
            return True
        nodes += 1
        if (sig & pos_mask) == pos_mask and not (sig & neg_mask):
            target_by_len[len(src)].add(src)
        old = best_src_by_sig.get(sig)
        if old is not None and (len(old), old) <= (len(src), src):
            return nodes <= max_nodes
        best_src_by_sig[sig] = src
        by_len[len(src)].append((src, sig))
        return nodes <= max_nodes

    for c in alphabet:
        if not add(c, 1 << index[c]):
            return None

    for L in range(1, max_len + 1):
        winners = sorted(src for src, sig in by_len[L] if (sig & pos_mask) == pos_mask and not (sig & neg_mask))
        if winners:
            if require_unique and len(target_by_len[L]) > 1:
                return None
            return winners[0]

        pool = [r for k in range(1, L + 1) for r in by_len[k]]

        for x, sx in pool:
            wx = _wrap_postfix(x)
            if len(wx) + 1 == L + 1:
                for src, sig in (
                    (f"{wx}*", star_sig(sx)),
                    (f"{wx}+", concat_sig(sx, star_sig(sx))),
                    (f"{wx}?", sx | empty_mask),
                ):
                    if not add(src, sig):
                        return None

        for x, sx in pool:
            for y, sy in pool:
                if len(x) + len(y) > L + 1:
                    continue
                xy = _concat(x, y)
                if len(xy) == L + 1 and not add(xy, concat_sig(sx, sy)):
                    return None
                if len(x) + len(y) + 1 != L + 1:
                    continue
                xy = _alt(x, y)
                if len(xy) == L + 1 and not add(xy, sx | sy):
                    return None

    return None


class RegexInduction(Task):
    def __init__(self, config=RegexConfig()):
        super().__init__(config=config)

    def generate(self):
        cfg = self.config
        alphabet = ALPHA[:max(2, cfg.n_alpha)]
        words = [a + b for a in alphabet for b in alphabet][:6]
        G = regex_grammar(
            fsm_subset=True,
            alpha=alphabet,
            words=random.sample(words, min(len(words), 4)),
        )

        for _ in range(100):
            hidden_regex, _fsm = _sample_regex(
                G,
                cfg.max_depth,
                cfg.min_depth,
                cfg.gramforge_algorithm,
            )

            if hidden_regex is None:
                continue

            positives = set()
            for _ in range(cfg.n_ex * 20):
                try:
                    s = sample_instance(hidden_regex)
                except ValueError:
                    continue

                if s and set(s) <= set(alphabet):
                    positives.add(s)

                if len(positives) == cfg.n_ex:
                    break

            if len(positives) < 2:
                continue

            negatives = set()
            for _ in range(cfg.n_ex * 50):
                s = "".join(random.choice(alphabet) for _ in range(random.randint(1, 5)))

                try:
                    if not regex.fullmatch(hidden_regex, s, timeout=0.2):
                        negatives.add(s)
                except TimeoutError:
                    continue

                if len(negatives) == cfg.n_ex:
                    break

            if len(negatives) < cfg.n_ex:
                continue

            positives = sorted(positives)
            negatives = sorted(negatives)

            answer = synthesize_shortest_regex(
                positives,
                negatives,
                alphabet,
                max_len=cfg.max_answer_len,
                max_nodes=cfg.max_synth_nodes,
                require_unique=cfg.require_unique,
            )

            if answer is None:
                continue

            meta = edict(
                hidden_regex=hidden_regex,
                positives=positives,
                negatives=negatives,
                alphabet=alphabet,
                shortest_regex=answer,
            )

            return Problem(meta, answer)

        return None

    def score_answer(self, answer, entry):
        pred = strip_anchors_safe(str(answer))
        meta = entry.metadata

        if not _uses_only_induction_syntax(pred, meta["alphabet"]):
            return 0.0
        if not _consistent(pred, meta["positives"], meta["negatives"]):
            return 0.0

        opt = meta["shortest_regex"]
        if pred == opt:
            return 1.0
        if len(pred) < len(opt):
            return 0.0
        return 1.0 / (1.0 + len(pred) - len(opt))

    def prompt(self, meta):
        pos_examples = ", ".join(f"'{s}'" for s in meta["positives"])
        neg_examples = ", ".join(f"'{s}'" for s in meta["negatives"])
        sigma = "".join(meta["alphabet"])

        return (
            f"Positive: {pos_examples}\n"
            f"Negative: {neg_examples}\n"
            f"The answer is the shortest regex matching all positives and no negatives. "
            f"Use only literals from Σ={{{sigma}}}, concatenation, |, parentheses, "
            f"and postfix *, +, ?. Break ties lexicographically."
        )




@dataclass
class RegexRetrievalConfig(Config):
    max_depth: int = 4
    min_depth: int = 2
    n_sentences: int = 3
    n_chunks: int = 6
    max_matches: int = 8
    empty_rate: float = 0.12
    literal_rate: float = 0.15
    natural_rate: float = 0.7
    structured_rate: float = 0.2
    gramforge_algorithm = "sequential"

    def update(self, c):
        self.max_depth += c
        self.min_depth += c
        self.n_sentences += c
        self.n_chunks += c
        self.max_matches += c

    def apply_difficulty(self, level):
        self.max_depth += level
        self.min_depth += level
        self.n_sentences += level
        self.n_chunks += level
        self.max_matches += level

def _find_matches(pattern, text, timeout=0.2):
    try:
        matches = [m.group(0) for m in regex.finditer(pattern, text, timeout=timeout)]
    except (regex.error, TimeoutError):
        return None
    return matches if all(matches) else None


def clean_text(s):
    return s.isascii() and s.isprintable()


def _has_regex_abstraction(pattern):
    return bool(regex.search(r"(?<!\\)[|*+?{\[.]|\\[dDwW]", pattern))


class RegexRetrieval(DevTask):
    def __init__(self, config=RegexRetrievalConfig()):
        super().__init__(config=config)

    def _natural(self, cfg):
        text = fake.paragraph(nb_sentences=cfg.n_sentences)
        patterns = [
            r"\b[A-Z][a-z]+\b",
            r"\b[a-z]{4,7}\b",
            r"\b\w*[aeiou]{2}\w*\b",
            r"\b[a-z]+(?:ed|ing|ly)\b",
        ]
        return random.choice(patterns), text, "natural"

    def _structured(self, cfg):
        items = [
            fake.email(),
            fake.date(pattern="%Y-%m-%d"),
            fake.bothify(text="ID-###-??").upper(),
            fake.phone_number(),
            fake.postcode(),
        ]
        patterns = [r"\b[\w.-]+@[\w.-]+\.\w+\b", r"\b\d{4}-\d{2}-\d{2}\b", r"\bID-\d{3}-[A-Z]{2}\b"]
        return random.choice(patterns), " ".join(random.sample(items, len(items))), "structured"

    def _generated(self, cfg):
        pattern = sample_regex(cfg)
        chunks = []
        for _ in range(cfg.n_chunks):
            r = pattern if random.random() < 0.45 else sample_regex(cfg)
            chunks.append(sample_instance(r))
        sep = random.choice([" ", " ", ", ", ". "])
        return pattern, sep.join(chunks), "generated"

    def generate(self):
        cfg = self.config
        p = random.random()
        make = self._natural if p < cfg.natural_rate else self._structured if p < cfg.natural_rate + cfg.structured_rate else self._generated
        for _ in range(100):
            try:
                pattern, text, source = make(cfg)
            except (RuntimeError, ValueError):
                continue
            if not clean_text(text):
                continue
            if not _has_regex_abstraction(pattern) and random.random() > cfg.literal_rate:
                continue

            matches = _find_matches(pattern, text)
            if matches is None or any(len(x) > 80 for x in matches):
                continue
            if not matches:
                if random.random() > cfg.empty_rate:
                    continue
            elif (
                len(matches) > cfg.max_matches
                or sum(map(len, matches)) > 0.4 * len(text)
                or sum(len(x) == 1 for x in matches) > 0.5 * len(matches)
            ):
                continue

            meta = edict(regex=pattern, text=text, matches=matches, source=source)
            return Problem(meta, json.dumps(matches, ensure_ascii=True, separators=(",", ":")))
        return None

    def prompt(self, meta):
        return (
            f"Text: {meta['text']}\n"
            f"Regex: {meta['regex']}\n"
            f"The answer is a JSON array of exact non-overlapping matches, left-to-right, including duplicates. "
            f"The answer is [] if none."
        )

    def score_answer(self, answer, entry):
        try:
            pred = json.loads(str(answer))
        except json.JSONDecodeError:
            return 0.0
        return float(pred == entry.metadata["matches"])


from greenery import parse as gparse

ALPHA = "abcdefgh"



def _sample_pair(G, depth, min_depth, mode, max_tries=40):
    """Sample two non-equivalent regexes."""
    r1, f1 = _sample_regex(G, depth, min_depth, mode)
    if f1 is None:
        return None
    for _ in range(max_tries):
        r2, f2 = _sample_regex(G, depth, min_depth, mode)
        if f2 is not None and not f1.equivalent(f2):
            return r1, f1, r2, f2
    return None


def _shortest_witness(fsm):
    """Shortest string in fsm, or None if empty."""
    for s in fsm.strings(otherchars=[]):
        return s
    return None


@dataclass
class RegexReasoningConfig(Config):
    max_depth: int = 4
    min_depth: int = 2
    n_alpha: int = 3
    gramforge_algorithm: str = "sequential"

    def update(self, c):
        self.max_depth += c
        self.min_depth += c
        self.n_alpha += 0.5 * c

    def apply_difficulty(self, level):
        self.max_depth += level
        self.min_depth += level
        self.n_alpha += 0.5 * level

def _sample_regex(G, depth, min_depth, mode="sequential", max_tries=60):
    for _ in range(max_tries):
        x = generate(G.start(), depth=depth, min_depth=min_depth, mode=mode)
        if len(x.leaves) <= 1:
            continue
        r = x @ "re"
        try:
            f = gparse(r).to_fsm()
            if not f.empty():
                return r, f
        except Exception:
            continue
    return None, None

class RegexReasoning(Task):
    def __init__(self, config=RegexReasoningConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio = 0.25

    def generate(self):
        cfg = self.config
        alpha = ALPHA[: max(2, cfg.n_alpha)]
        words = [a + b for a in alpha for b in alpha][:6]
        G = regex_grammar(fsm_subset=True, alpha=alpha, words=random.sample(words, min(len(words), 4)))

        pair = _sample_pair(G, cfg.max_depth, cfg.min_depth, cfg.gramforge_algorithm)
        if pair is None:
            return None
        r1, f1, r2, f2 = pair

        qtype = random.choice(["equivalence", "containment", "distinguishing"])

        if qtype == "equivalence":
            # ~40% "Yes" (reuse same regex string), ~60% "No" (use the pair)
            if random.random() < 0.4:
                meta = edict(qtype="equivalence", regex_a=r1, regex_b=r1)
                return Problem(meta, "Yes")
            meta = edict(qtype="equivalence", regex_a=r1, regex_b=r2)
            return Problem(meta, "No")

        if qtype == "containment":
            # Force ~50% Yes by building a superset via union
            if random.random() < 0.5:
                sup = gparse(f"({r1})|({r2})")
                r_sup = str(sup)
                # A=r1 ⊆ B=r1|r2 is always true
                meta = edict(qtype="containment", regex_a=r1, regex_b=r_sup)
                return Problem(meta, "Yes")
            else:
                is_sub = f1.issubset(f2)
                if random.random() < 0.5:
                    meta = edict(qtype="containment", regex_a=r1, regex_b=r2)
                    return Problem(meta, "Yes" if is_sub else "No")
                else:
                    meta = edict(qtype="containment", regex_a=r2, regex_b=r1)
                    return Problem(meta, "Yes" if f2.issubset(f1) else "No")

        # distinguishing
        sd = f1.symmetric_difference(f2)
        witness = _shortest_witness(sd)
        if witness is None:
            return None
        meta = edict(qtype="distinguishing", regex_a=r1, regex_b=r2)
        return Problem(meta, witness)

    def prompt(self, metadata):
        a, b = metadata["regex_a"], metadata["regex_b"]
        qt = metadata["qtype"]
        if qt == "equivalence":
            return (
                f"A = {a}\nB = {b}\n"
                f"Do A and B accept exactly the same set of strings?\n"
                f"The answer is Yes or No."
            )
        elif qt == "containment":
            return (
                f"A = {a}\nB = {b}\n"
                f"Is every string accepted by A also accepted by B?\n"
                f"The answer is Yes or No."
            )
        else:
            return (
                f"A = {a}\nB = {b}\n"
                f"Find the shortest string that is accepted by exactly one of A or B (but not both).\n"
                f"The answer is the shortest such string."
            )

    def score_answer(self, answer, entry):
        qt = entry.metadata["qtype"]
        answer = str(answer).strip()
        if answer.lower() in ("ε", "\\epsilon", "ε (the empty string)", '""', "''"):
            answer = ""
        if qt in ("equivalence", "containment"):
            norm = answer.lower().strip().rstrip(".")
            return float(norm == entry.answer.lower()) if norm in ("yes", "no") else 0.0
        # distinguishing: verify witness semantically
        try:
            fa = gparse(entry.metadata["regex_a"]).to_fsm()
            fb = gparse(entry.metadata["regex_b"]).to_fsm()
        except Exception:
            return 0.0
        if fa.accepts(answer) == fb.accepts(answer):
            return 0.0
        expected_len = len(entry.answer)
        return 1.0 / (1.0 + max(0, len(answer) - expected_len))

    def balancing_key(self, problem):
        if problem.metadata.qtype == "distinguishing":
            n = len(problem.answer)
            bucket = "empty" if n == 0 else "1" if n == 1 else "2" if n == 2 else "3+"
            return f"distinguishing:len={bucket}"
        return f"{problem.metadata.qtype}:{problem.answer}"

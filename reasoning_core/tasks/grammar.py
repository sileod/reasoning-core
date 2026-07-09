from gramforge import init_grammar, generate_with_choices
from gramforge import generate as gramforge_generate
from tqdm.auto import tqdm
from functools import cache
from contextlib import contextmanager
from nltk.parse.generate import generate as nltk_generate
from nltk import CFG, ChartParser
from nltk.parse.earleychart import EarleyChartParser
import sys
from reasoning_core.template import Task, DevTask, Entry, Config
import random
from pathlib import Path
from nltk.data import path as nltk_path
import string
from easydict import EasyDict as edict
from faker import Faker
import re
from collections import Counter, defaultdict
from gramforge.grammars import simple_english_grammar, arith_grammar, dyck_grammar
from gramforge import gramforge_to_nltk
from rapidfuzz.distance import Levenshtein
from itertools import islice
from nltk.grammar import CFG, Nonterminal
from itertools import islice, combinations


fake = Faker()

existing_grammars = [
    simple_english_grammar(), simple_english_grammar(questions=False),
    dyck_grammar(), dyck_grammar(include_unicode=False)
]
existing_grammars = [gramforge_to_nltk(g) for g in existing_grammars]

wordlist = list(fake.words(nb=500,unique=True))

from dataclasses import dataclass

@dataclass
class GrammarConfig(Config):
    n_types: int = 4
    n_terminals: int = 5
    perturbation_rate: float = 0.5

    gramforge_algorithm="sequential"
    min_depth:int =5
    max_depth:int =8

    min_prod_depth:int=4
    max_prod_depth:int=6

    random_grammar_prob:float = 0.3
    tagging_prob: float = 0.5
    target_num_rules=10

    n_resampled_grammars: int=200
    prob_resampling_grammar: float=0.1
    max_tokens:int =16

    min_k: int = 3
    max_k: int = 5
    min_blanks: int = 2
    max_blanks: int = 3
    min_options: int = 4
    max_options: int = 25
    def apply_difficulty(self, level):
        self.n_types += level
        self.n_terminals += level
        self.min_depth += level
        self.max_depth += level
        self.prob_resampling_grammar = max(0.0, self.prob_resampling_grammar - 0.1 * level)
        self.max_tokens += 2 * level

def meta_grammar(config):
    R=init_grammar(['cfg'])
    R('start(grammar)', '0')
    R('grammar(nonterminal,rules)', 'S -> 0\n1')

    R('rules(rule)', '0')
    R('rules(rule,rules)', '0\n1')
    R('rules(rule,rule,rules)', '0\n1\n2')

    R('rule(nonterminal,rhs)', '0 -> 1', constraint=[lambda x: x[0] @ 0 != x[1] @ 0])

    R('rhs(expr)', '0')

    R('expr(symbol)', '0')
    R('expr(symbol,expr)', '0 1')
    R('expr(expr,symbol)', '0 1')

    R('symbol(nonterminal)', '0')
    R('symbol(terminal)', '0')
    R('expr(dyck)','0')

    for x in string.ascii_uppercase[:config.n_types]:
        R('nonterminal', x)

    R('terminal(t_rnd)', '0')
    for x in random.sample(wordlist, config.n_terminals):
        R('t_rnd', f"'{x}'")

    paren_types = [
        ('square', '[', ']'), ('curly', '<', '>'),
    ]

    for name, open_char, close_char in paren_types:
        R('dyck(expr)', f"'{open_char}'0'{close_char}'")

    return R

def nltk_to_gramforge(g):
    import nltk
    R = init_grammar(['lang'])
    for p in g.productions():
        lhs = str(p.lhs()).lower()
        args, tokens, idx = [], [], 0
        for sym in p.rhs():
            if isinstance(sym, nltk.grammar.Nonterminal):
                tokens.append(str(idx))
                args.append(str(sym).lower())
                idx += 1
            else:
                tokens.append(sym)
        sig = f"{lhs}({','.join(args)})" if args else lhs
        R(sig, ' '.join(tokens))
    return R


def trim_grammar(grammar, target_size=10, retries=10, shrink_tries=1000, seed=None, max_steps=10000):
    rng = random.Random(seed)

    by_lhs = defaultdict(list)
    for p in grammar.productions():
        by_lhs[p.lhs()].append(p)

    def get_new_deps(rule, defined):
        return [s for s in rule.rhs() if isinstance(s, Nonterminal) and s not in defined]

    def prune(prods):
        if not prods:
            return []

        # map for reachability walk
        local_map = defaultdict(list)
        for p in prods:
            local_map[p.lhs()].append(p)

        # 1) reachable
        reachable = {grammar.start()}
        stack = [grammar.start()]
        while stack:
            lhs = stack.pop()
            for p in local_map.get(lhs, []):
                for s in p.rhs():
                    if isinstance(s, Nonterminal) and s not in reachable:
                        reachable.add(s)
                        stack.append(s)

        prods = [p for p in prods if p.lhs() in reachable]

        # 2) productive (fixed point)
        productive = set()
        changed = True
        while changed:
            changed = False
            for p in prods:
                if p.lhs() in productive:
                    continue
                if all((not isinstance(s, Nonterminal)) or (s in productive) for s in p.rhs()):
                    productive.add(p.lhs())
                    changed = True

        if grammar.start() not in productive:
            return []

        # 3) drop rules that reference unproductive NTs
        return [p for p in prods
                if p.lhs() in productive and
                   all((not isinstance(s, Nonterminal)) or (s in productive) for s in p.rhs())]

    for _ in range(retries):
        kept = set()
        defined = set()
        pending = [grammar.start()]

        # --- PHASE 1: GROW ---
        steps = 0
        while steps < max_steps:
            steps += 1

            if pending:
                lhs = pending.pop()
                if lhs in defined:
                    continue
                options = by_lhs.get(lhs, [])
                if not options:
                    break
            elif len(kept) < target_size:
                expandable = [(l, [p for p in by_lhs[l] if p not in kept]) for l in defined]
                expandable = [(l, opts) for l, opts in expandable if opts]
                if not expandable:
                    break
                lhs, options = rng.choice(expandable)
            else:
                break

            if not options:
                continue

            # Improved near-budget selection: minimize number of NEW deps
            if len(kept) >= target_size:
                dep_counts = [(len(get_new_deps(p, defined)), p) for p in options]
                m = min(c for c, _ in dep_counts)
                options = [p for c, p in dep_counts if c == m]

            rule = rng.choice(options)
            kept.add(rule)
            defined.add(lhs)
            pending.extend(get_new_deps(rule, defined))

        # --- PHASE 2: SHRINK ---
        current = prune(list(kept))
        if not current:
            continue

        for _ in range(shrink_tries):
            if len(current) <= target_size:
                break
            cand = rng.choice(current)
            trial = [p for p in current if p != cand]
            trial = prune(trial)
            if trial:
                current = trial

        return CFG(grammar.start(), current)

    print(f"Warning: trimming failed after {retries} retries.")
    return grammar



def prune_cfg(grammar):
    prods = list(grammar.productions())

    by_lhs = defaultdict(list)
    for p in prods:
        by_lhs[p.lhs()].append(p)

    # reachable from start
    reachable = {grammar.start()}
    stack = [grammar.start()]
    while stack:
        lhs = stack.pop()
        for p in by_lhs.get(lhs, []):
            for s in p.rhs():
                if isinstance(s, Nonterminal) and s not in reachable:
                    reachable.add(s)
                    stack.append(s)

    prods = [p for p in prods if p.lhs() in reachable]

    # productive NTs
    productive = set()
    changed = True
    while changed:
        changed = False
        for p in prods:
            if all((isinstance(s, str) or s in productive) for s in p.rhs()):
                if p.lhs() not in productive:
                    productive.add(p.lhs())
                    changed = True

    if grammar.start() not in productive:
        return None

    prods = [
        p for p in prods
        if p.lhs() in productive
        and all((isinstance(s, str) or s in productive) for s in p.rhs())
    ]

    return CFG(grammar.start(), prods)

def sample_cfg(config=GrammarConfig, productive_only=False):
    if random.random() > config.random_grammar_prob:
        g = random.choice(existing_grammars)
        if len(g.productions()) > config.target_num_rules:
            g = trim_grammar(g, config.target_num_rules)
        if productive_only:
            g = prune_cfg(g)
            if g is None:
                raise ValueError("Existing grammar became unproductive")
        return g

    for _ in range(1000):
        MG = meta_grammar(config).start()
        for _ in range(100):
            try:
                x = gramforge_generate(MG, depth=config.max_depth, min_depth=config.min_depth, mode=config.gramforge_algorithm)
                g = CFG.fromstring(x@"cfg")
            except ValueError:
                continue

            if productive_only:
                g = prune_cfg(g)
                if g is None:
                    continue

            try:
                prods = list(islice(nltk_generate(g, depth=config.max_prod_depth), 10))
            except (RecursionError, ValueError):
                continue

            if len(prods) > 3:
                return g

    raise ValueError("Failed to sample CFG")

@contextmanager
def resampled_grammar(config, **kw):
    if random.random() < config.prob_resampling_grammar:
        seed = random.randint(0, config.n_resampled_grammars - 1)
        state = random.getstate()
        try:
            random.seed(seed)
            yield sample_cfg(config, productive_only=True)
        finally:
            random.setstate(state)
    else:
        yield sample_cfg(config, **kw)

def perturb(tokens, config=GrammarConfig):
    return random.choice([
        lambda t: random.sample(t, len(t)),
        lambda t: (lambda i: t[:i]+t[i+1:])(random.randrange(len(t))) if len(t)>1 else t,
        #lambda _: (gramforge_generate(nltk_to_unigram(sample_cfg(config)).get_rules('s', shuffle=True)[0], depth=5, mode=config.gramforge_algorithm) @ 'lang').split()
        lambda _: (gramforge_generate(nltk_to_gramforge(sample_cfg(config)), depth=5, mode=config.gramforge_algorithm) @ 'lang').split()

    ])(tokens)

def make_cot(g, tokens):
    # Get up to 2 parses to detect ambiguity without exhaustively searching
    ps = list(islice(EarleyChartParser(g).parse(tokens), 2))
    
    lines = []
    for i, t in enumerate(ps, 1):
        lines.append(f"Parse {i}:")
        for idx in t.treepositions('leaves'):
            # Construct path: Root -> ... -> POS
            path = [t[idx[:k]].label() for k in range(len(idx))]
            lines.append(f"'{t[idx]}': {' > '.join(path)} (Depth: {len(path)})")

    return "\n".join(lines), ps

def generate_parse(config=GrammarConfig):
    meta = edict()
    while True:
        with resampled_grammar(config) as g:
            g_u = nltk_to_gramforge(g)
            
            try:
                tokens = (gramforge_generate(g_u, depth=config.max_prod_depth, min_depth=config.min_prod_depth, mode=config.gramforge_algorithm) @ "lang").split()
            except ValueError: continue

            if random.random() < config.perturbation_rate:
                try:
                    tokens = perturb(tokens, config)
                except ValueError:
                    continue
            
            if len(tokens) > config.max_tokens:
                continue

            try:
                meta.cot, meta.parses = make_cot(g, tokens)
            except (RecursionError, ValueError):
                continue

            meta.label = ("unparsable" if not meta.parses else 
                         "ambiguous"   if len(meta.parses) > 1 else 
                         "unambiguous")
            meta.tokens = tokens
            meta.g = "\n".join(str(p) for p in g.productions())
            return meta


class Parsability(DevTask):
    def __init__(self, config: GrammarConfig = GrammarConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio=1/3

    def generate_entry(self):
        meta = generate_parse(self.config)
        del meta['parses'] #can blow up_
        return Entry(meta, meta.label)

    def render_prompt(self, meta):
        g, tokens = meta.g, meta.tokens
        return (
            f"(GRAMMAR)\n{g}\n\n"
            f"(STRING)\n{' '.join(tokens)}\n\n"
            f"(QUESTION)\nWhat is the parsability of this string?\n"
            f"The answer is exactly one word: unambiguous, ambiguous, or unparsable."
        )


class Parsing(DevTask):
    def __init__(self, config: GrammarConfig = GrammarConfig()):
        config.perturbation_rate = 0.0
        super().__init__(config=config)

    def generate_entry(self):
        while True:
            meta = generate_parse(self.config)
            if meta.label != 'unambiguous': continue
            _, _, tail = meta.cot.partition('\n')
            if not tail: continue  # Skip if cot has no content after header
            meta.cot = tail

            t = meta.parses[0] # Get the Tree object directly

            if random.random() < self.config.tagging_prob:
                meta.mode = 'tagging'
                leaves = []
                for idx in t.treepositions('leaves'):
                    token = t[idx]
                    pos = t[idx[:-1]].label() # Parent label
                    depth = len(idx)          # Distance from root
                    leaves.append(f"{token}<{pos}:{depth}>")
                return Entry(meta, " ".join(leaves))
            else:
                meta.mode = 'parsing'
                tree_str = " ".join(str(t).split())
                return Entry(meta, tree_str)

    def render_prompt(self, meta):
        g, tokens = meta.g, meta.tokens
        head = f"(GRAMMAR)\n{g}\n\n(STRING)\n{' '.join(tokens)}\n\n(QUESTION)\n"
        
        if meta.mode == 'tagging':
            return (head + 
                "Identify the Part-of-Speech (immediate parent) and tree depth for each token.\n"
                "format per token: token<POS:depth>\n"
                "Example: the<Det:3> cat<Noun:3>")
        
        ex = """Given G_ex: S -> NP VP, NP -> 'd' N, N -> 'n', VP -> 'v' and "d n v", correct is (S (NP d (N n)) (VP v))."""
        return (head + 
            "The answer is the fully parenthesized parse tree of STRING in Lisp style.\n"
            f"{ex}")


    def score_answer(self, answer, entry):
        norm = lambda s: re.sub(r'\s+', ' ', str(s).strip()).replace('"','').replace("'",'')

        reference = entry['answer']
        if not answer: return 0.0
        
        return Levenshtein.normalized_similarity(norm(answer), norm(reference))


def labeled_rules(meta):
    lines = meta.g.splitlines()
    return "\n".join(f"R{i}: {rule}" for i, rule in enumerate(lines)), {
        rule: f"R{i}" for i, rule in enumerate(lines)
    }


class ParsingDerivation(Task):
    summary = "Determine the derivation production rule sequence parsing a given string."
    def __init__(self, config: GrammarConfig = GrammarConfig()):
        config.perturbation_rate = 0.0
        super().__init__(config=config)

    def generate_entry(self):
        while True:
            meta = generate_parse(self.config)
            if meta.label != "unambiguous" or len(meta.parses) != 1:
                continue
            _, labels = labeled_rules(meta)
            try:
                answer = " ".join(labels[str(p)] for p in meta.parses[0].productions())
            except KeyError:
                continue
            meta.pop("parses", None)
            meta.pop("cot", None)
            return Entry(meta, answer)

    def render_prompt(self, meta):
        g, _ = labeled_rules(meta)
        return (
            f"(GRAMMAR)\n{g}\n\n"
            f"(STRING)\n{' '.join(meta.tokens)}\n\n"
            "(QUESTION)\n"
            "The answer is the rule labels used in the leftmost derivation of STRING, in order, separated by spaces."
        )

    def score_answer(self, answer, entry):
        pred = re.findall(r"\bR\d+\b", str(answer))
        gold = entry["answer"].split()
        # token-level edit-distance similarity (each R# is one token): partial credit
        # for near-correct derivations instead of all-or-nothing exact match.
        return Levenshtein.normalized_similarity(pred, gold)



def _edge_str(edge):
    rhs = [str(s) for s in edge.rhs()]
    dot = edge.dot()
    rhs = rhs[:dot] + ['•'] + rhs[dot:]
    return f"{edge.lhs()}→{' '.join(rhs)}"

def get_valid_next_tokens(grammar, prefix):
    """
    Exact next-token oracle for prefix-safe grammars:
    - valid next terminals
    - whether STOP is valid
    - lightweight edge-based justifications
    """
    parser = EarleyChartParser(grammar)
    nullable, first = _compute_nullable_and_first(grammar)

    try:
        chart = parser.chart_parse(list(prefix))
    except ValueError:
        return set(), False, {}

    n = len(prefix)
    valid_tokens = set()
    justifications = {}
    can_stop = False

    for edge in chart.select(end=n):
        edge_txt = _edge_str(edge)

        if edge.is_complete():
            if edge.start() == 0 and edge.lhs() == grammar.start():
                can_stop = True
                justifications.setdefault("STOP", edge_txt)
            continue

        remainder = edge.rhs()[edge.dot():]
        toks, _ = _first_of_sequence(remainder, first, nullable)

        for tok in toks:
            valid_tokens.add(tok)
            justifications.setdefault(tok, edge_txt)

    return valid_tokens, can_stop, justifications


def _build_cot(tokens, can_stop, justifications):
    parts = []

    if can_stop and 'STOP' in justifications:
        parts.append(f"{justifications['STOP']}⇒STOP")

    grouped = defaultdict(list)
    for tok in sorted(tokens):
        grouped[justifications.get(tok, "continuation")].append(tok)

    for reason, toks in sorted(grouped.items()):
        if len(toks) > 3:
            parts.append(f"{reason}⇒{{{','.join(toks)}}}")
        else:
            parts.extend(f"{reason}⇒{tok}" for tok in toks)

    return "\n".join(parts) if parts else "continuation"


class Continuation(DevTask):
    """Grammar continuation task using proper CFG parsing."""
    
    def __init__(self, config: GrammarConfig = GrammarConfig()):
        super().__init__(config=config)
        self.balancing_key_ratio = 0.1
        
    def generate_entry(self):
        for _ in range(100):
            with resampled_grammar(self.config, productive_only=True) as g:
                try:
                    sentence = (gramforge_generate(
                        nltk_to_gramforge(g),
                        depth=self.config.max_prod_depth,
                        min_depth=self.config.min_prod_depth,
                        mode=self.config.gramforge_algorithm,
                    ) @ "lang").split()
                except (RecursionError, ValueError):
                    continue
                
                min_len = 3 + self.config.level
                if len(sentence) < min_len or len(sentence) > self.config.max_tokens:
                    continue

                max_prefix = len(sentence) - 1
                min_prefix = min(max_prefix, 2 + self.config.level)
                cuts = list(range(min_prefix, max_prefix + 1))
                if len(cuts) > 6:
                    cuts = [min_prefix, max_prefix] + random.sample(cuts[1:-1], 4)
                candidates = []
                for prefix_len in cuts:
                    prefix = list(sentence[:prefix_len])
                    try:
                        tokens, can_stop, justifications = get_valid_next_tokens(g, prefix)
                    except Exception:
                        continue
                    n_answers = len(tokens) + int(can_stop)
                    if n_answers:
                        candidates.append((prefix_len + n_answers, prefix,
                                           tokens, can_stop, justifications))

                if not candidates:
                    continue

                preferred = [c for c in candidates
                             if len(c[2]) + int(c[3]) > 1]
                if self.config.level >= 3:
                    preferred = [c for c in preferred
                                 if len(c[2]) + int(c[3]) >= 3] or preferred
                if preferred and random.random() < 0.8:
                    candidates = preferred
                best = max(c[0] for c in candidates)
                _, prefix, tokens, can_stop, justifications = random.choice(
                    [c for c in candidates if c[0] == best]
                )
                
                answer = '|'.join(sorted(tokens))
                if can_stop:
                    answer = (answer + '|STOP') if answer else 'STOP'
                
                cot = _build_cot(tokens, can_stop, justifications)
                
                return Entry(
                    edict(g="\n".join(str(p) for p in g.productions()), 
                          prefix=prefix, depth=len(prefix), cot=cot),
                    answer
                )
        raise ValueError("Failed to generate continuation after 100 attempts")
    
    def render_prompt(self, meta):
        pfx = ' '.join(meta.prefix) if meta.prefix else '<empty>'
        return (f"List valid next tokens for this prefix. "
                f"The answer is the valid tokens sorted alphabetically and separated by |, with STOP at the end if the prefix forms a complete string.\n"
                f"(GRAMMAR)\n{meta.g}\n(PREFIX)\n{pfx}")

    def score_answer(self, answer, entry):
        prepr = lambda x: {e.strip() for e in x.split('|')}
        try:
            ref, ans = prepr(entry['answer']), prepr(answer)
            inter = len(ref & ans)
            # Jaccard
            return inter / max(len(ref | ans), 1)
        except Exception:  # also: bare except catches KeyboardInterrupt
            return 0


# --- Error Detection Task ---

def _span_hits(seq, span):
    k = len(span)
    return [i for i in range(len(seq) - k + 1) if seq[i:i+k] == span]

def min_context(tokens, idx):
    for start in range(idx, -1, -1):
        if len(_span_hits(tokens, tokens[start:idx+1])) == 1:
            return ' '.join([*tokens[start:idx], f'>>{tokens[idx]}<<'])
    return ' '.join([*tokens[:idx], f'>>{tokens[idx]}<<'])

def grammar_terminals(g):
    return sorted({s for p in g.productions() for s in p.rhs() if isinstance(s, str)})

def prefix_has_completion(g, prefix):
    valid, can_stop, _ = get_valid_next_tokens(g, prefix)
    return can_stop or bool(valid)

def first_error_marked(g, tokens):
    lines = []
    for i, tok in enumerate(tokens):
        prev_valid, _, _ = get_valid_next_tokens(g, tokens[:i])

        if not prefix_has_completion(g, tokens[:i+1]):
            lines.append(f"{tok} ∉ {{{','.join(sorted(prev_valid)[:8])}}}")
            ans = min_context(tokens, i)
            lines.append(f"Answer: {ans}")
            return ans, i, '\n'.join(lines)

        lines.append(f"{tok} ✓")

    _, can_stop, _ = get_valid_next_tokens(g, tokens)
    return ('OK' if can_stop else 'INCOMPLETE'), -1, '\n'.join(lines)

def corrupt_once(g, tokens):
    terms = grammar_terminals(g)
    if len(terms) < 2:
        raise ValueError("Need ≥2 terminals")
    for _ in range(80):
        op = random.choices(['substitute', 'insert', 'delete'], weights=[6, 2, 2])[0]
        if op == 'delete' and len(tokens) < 3:
            continue
        if op == 'delete':
            pos = random.randrange(len(tokens))
            out = tokens[:pos] + tokens[pos+1:]
        elif op == 'insert':
            pos = random.randrange(len(tokens) + 1)
            valid, _, _ = get_valid_next_tokens(g, tokens[:pos])
            bad = [t for t in terms if t not in valid]
            if not bad:
                continue
            out = tokens[:pos] + [random.choice(bad)] + tokens[pos:]
        else:  # substitute
            pos = random.randrange(len(tokens))
            valid, _, _ = get_valid_next_tokens(g, tokens[:pos])
            # prefer terminals valid elsewhere but invalid here
            bad = [t for t in terms if t not in valid and t != tokens[pos]]
            if not bad:
                continue
            out = list(tokens)
            out[pos] = random.choice(bad)

        answer, idx, cot = first_error_marked(g, out)
        if answer not in ('OK', 'INCOMPLETE'):
            return out, answer, idx, cot
    raise ValueError("Failed to corrupt")

def get_marked_index(toks):
    for i, t in enumerate(toks):
        if t.startswith('>>') and t.endswith('<<'):
            return i
    return -1

def _norm_marked(s):
    s = re.sub(r'>>\s+', '>>', str(s).strip())
    s = re.sub(r'\s+<<', '<<', s)
    return re.sub(r'\s+', ' ', s)

class SyntaxErrorDetection(Task):
    summary = "Locate syntax errors or grammatical perturbations in generated sentences."
    def __init__(self, config: GrammarConfig = GrammarConfig()):
        config.perturbation_rate = 0.0
        super().__init__(config=config)

    def generate_entry(self):
        for _ in range(100):
            with resampled_grammar(self.config, productive_only=True) as g:
                if len(grammar_terminals(g)) < 2:
                    continue
                try:
                    toks = (gramforge_generate(
                        nltk_to_gramforge(g),
                        depth=self.config.max_prod_depth,
                        min_depth=self.config.min_prod_depth,
                        mode=self.config.gramforge_algorithm
                    ) @ "lang").split()
                except ValueError:
                    continue
                if len(toks) < 3:
                    continue

                roll = random.random()
                if roll < 0.15:
                    ans, idx, cot = first_error_marked(g, toks)
                    if ans != 'OK':
                        continue
                    out = toks
                elif roll < 0.30:
                    out = toks[:random.randint(1, len(toks) - 1)]
                    ans, idx, cot = first_error_marked(g, out)
                    if ans != 'INCOMPLETE':
                        continue
                else:
                    try:
                        out, ans, idx, cot = corrupt_once(g, toks)
                    except ValueError:
                        continue

                return Entry(
                    edict(g="\n".join(str(p) for p in g.productions()),
                          tokens=out, error_index=idx, cot=cot),
                    ans
                )
        raise ValueError("Failed to generate locate-error task")

    def render_prompt(self, meta):
        return (
            f"(GRAMMAR)\n{meta.g}\n\n"
            f"(STRING)\n{' '.join(meta.tokens)}\n\n"
            f"The answer is the shortest contiguous span from STRING that ends at the first invalid token "
            f"and occurs only once in STRING.\n"
            f"Mark the invalid token as >>token<<.\n"
            f"If the token alone is enough, answer just >>token<<.\n"
            f"If STRING is fully grammatical, answer OK.\n"
            f"If all shown tokens are valid but more are needed, answer INCOMPLETE.\n"
            f"One line only."
        )

    def score_answer(self, answer, entry):
            if not answer: return 0.0
            a, r = _norm_marked(answer), _norm_marked(entry['answer'])
            if a == r: return 1.0
            if {'OK', 'INCOMPLETE'} & {a, r}: return 0.0

            a_toks = a.split()
            marked = [t.startswith('>>') and t.endswith('<<') for t in a_toks]
            if marked.count(True) != 1 or not marked[-1]:
                return 0.0

            span = [t.replace('>>', '').replace('<<', '') for t in a_toks]
            hits = _span_hits(entry.metadata['tokens'], span)
            
            if entry.metadata['error_index'] not in {h + len(span) - 1 for h in hits}:
                return 0.0

            # Strict penalty: the span is correct but occurs multiple times in the text
            if len(hits) > 1:
                return 0.5 

            # Unambiguous location: minimum 0.9, scales to 1.0 based on how concise the prefix is
            efficiency = len(r.split()) / len(a_toks)
            return min(1.0, max(0.9, efficiency))


# --- Constrained Generation ---


def _compute_nullable_and_first(grammar):
    """Exact nullable + FIRST sets via fixed-point iteration (no depth cutoff)."""
    nts = {p.lhs() for p in grammar.productions()}

    nullable = set()
    changed = True
    while changed:
        changed = False
        for p in grammar.productions():
            rhs = p.rhs()
            if not rhs or all(
                isinstance(s, Nonterminal) and s in nullable for s in rhs
            ):
                if p.lhs() not in nullable:
                    nullable.add(p.lhs())
                    changed = True

    first = {nt: set() for nt in nts}
    changed = True
    while changed:
        changed = False
        for p in grammar.productions():
            add, _ = _first_of_sequence(p.rhs(), first, nullable)
            before = len(first[p.lhs()])
            first[p.lhs()].update(add)
            if len(first[p.lhs()]) != before:
                changed = True

    return nullable, first


def _first_of_sequence(seq, first, nullable):
    """FIRST terminals reachable from a symbol sequence + whether it's all-nullable."""
    out = set()
    all_nullable = True
    for sym in seq:
        if isinstance(sym, str):
            out.add(sym)
            all_nullable = False
            break
        out.update(first.get(sym, set()))
        if sym not in nullable:
            all_nullable = False
            break
    return out, all_nullable


def _exact_next_tokens_and_stop(grammar, prefix, parser=None, nullable=None, first=None):
    """
    Sound next-token discovery via Earley boundary edges + exact FIRST/nullable.
    Returns (valid_tokens: set[str], can_stop: bool).
    """
    parser = parser or EarleyChartParser(grammar)
    if nullable is None or first is None:
        nullable, first = _compute_nullable_and_first(grammar)

    try:
        chart = parser.chart_parse(list(prefix))
    except ValueError:
        return set(), False

    n = len(prefix)
    valid_tokens = set()
    can_stop = False

    for edge in chart.select(end=n):
        if edge.is_complete():
            if edge.start() == 0 and edge.lhs() == grammar.start():
                can_stop = True
            continue
        remainder = edge.rhs()[edge.dot():]
        toks, _ = _first_of_sequence(remainder, first, nullable)
        valid_tokens.update(toks)

    return valid_tokens, can_stop


def exact_window_fills(grammar, prefix, k, suffix=(), max_states=1024):
    """All distinct k-token windows W such that prefix + W + suffix is grammatical.
    Empty suffix => W must yield STOP (original `exact_completions` behavior).
    Returns [] (safe skip) on state-space overflow."""
    prefix, suffix = list(prefix), list(suffix)
    parser = EarleyChartParser(grammar)
    nullable, first = _compute_nullable_and_first(grammar)

    frontier = {()}
    for _ in range(k):
        nxt = set()
        for win in frontier:
            toks, _ = _exact_next_tokens_and_stop(
                grammar, prefix + list(win), parser, nullable, first
            )
            for tok in toks:
                nxt.add(win + (tok,))
                if len(nxt) > max_states:
                    return []
        if not nxt:
            return []
        frontier = nxt

    if not suffix:
        return [list(w) for w in sorted(frontier)
                if _exact_next_tokens_and_stop(grammar, prefix + list(w),
                                               parser, nullable, first)[1]]
    return [list(w) for w in sorted(frontier)
            if next(parser.parse(prefix + list(w) + suffix), None) is not None]


def sample_blanking(target, cands, min_blanks, max_blanks, tries=20):
    """Sample a random hint set whose hints uniquely identify target among cands.
    Falls back to greedy minimal hinting."""
    k = len(target)
    max_blanks = min(max_blanks, k - 1)
    if min_blanks > max_blanks:
        return None

    unique = lambda hints: sum(
        all(c[i] == t for i, t in hints.items()) for c in cands
    ) == 1

    for _ in range(tries):
        n = random.randint(min_blanks, max_blanks)
        blanks = set(random.sample(range(k), n))
        hints = {i: target[i] for i in range(k) if i not in blanks}
        if unique(hints):
            return list(target), hints

    hinted = set(range(k))
    for pos in random.sample(range(k), k):
        if k - len(hinted) >= max_blanks:
            break
        trial = hinted - {pos}
        if unique({i: target[i] for i in trial}):
            hinted = trial
    if min_blanks <= k - len(hinted) <= max_blanks:
        return list(target), {i: target[i] for i in sorted(hinted)}
    return None


def _format_template(k, hints):
    return " ".join(hints.get(i, "___") for i in range(k))


class ConstrainedContinuation(Task):
    """Fill-in-the-blanks over a k-token window placed anywhere in a grammatical
    sentence. The window is wrapped by a PREFIX (possibly empty) and a SUFFIX
    (possibly empty); the model fills blanks so PREFIX + filled-TEMPLATE + SUFFIX
    is grammatical. When the suffix is empty the task is a continuation
    (Dyck-friendly); when non-empty it is a cloze (works on linear grammars too)."""
    summary = "Fill in blank tokens within a grammar-constrained sentence with prefix/suffix context."

    def __init__(self, config: GrammarConfig = GrammarConfig()):
        config.prob_resampling_grammar = 0.0  # needed for speed
        config.min_k = max(3, config.min_k)
        super().__init__(config=config)
        self.balancing_key_ratio = 0.25

    def generate_entry(self):
        for _ in range(200):
            with resampled_grammar(self.config, productive_only=True) as g:
                try:
                    sent = (gramforge_generate(
                        nltk_to_gramforge(g),
                        depth=self.config.max_prod_depth,
                        min_depth=self.config.min_prod_depth,
                        mode=self.config.gramforge_algorithm,
                    ) @ "lang").split()
                except (ValueError, RecursionError):
                    continue
                if not self.config.min_k <= len(sent) <= self.config.max_tokens:
                    continue

                slots = [(start, k)
                         for k in range(self.config.min_k, self.config.max_k + 1)
                         for start in range(0, len(sent) - k + 1)]
                random.shuffle(slots)

                for start, k in slots:
                    prefix = sent[:start]
                    suffix = sent[start + k:]
                    cands = exact_window_fills(g, prefix, k, suffix)
                    # A single candidate is a valid deterministic cloze: PREFIX
                    # and SUFFIX may already determine the window. When there
                    # are multiple candidates, TEMPLATE hints disambiguate.
                    if not cands or len(cands) > self.config.max_options:
                        continue

                    target = sent[start:start + k]
                    if list(target) not in cands:
                        continue  # defensive: truth should always be a candidate
                    result = sample_blanking(target, cands,
                                             self.config.min_blanks,
                                             self.config.max_blanks)
                    if result is None:
                        continue
                    target, hints = result
                    blanks = sorted(set(range(k)) - set(hints.keys()))

                    return Entry(
                        edict(
                            g="\n".join(str(p) for p in g.productions()),
                            k=k,
                            prefix=prefix,
                            suffix=suffix,
                            hints={str(i): tok for i, tok in hints.items()},
                            template=_format_template(k, hints),
                            blanks=blanks,
                            n_blanks=len(blanks),
                            n_hints=len(hints),
                            n_options=len(cands),
                        ),
                        " ".join(target),
                    )

        raise ValueError("Failed to generate constrained continuation after 200 attempts")

    def render_prompt(self, meta):
        pfx = " ".join(meta.prefix) if meta.prefix else "<empty>"
        sfx = " ".join(meta.suffix) if meta.get("suffix") else "<empty>"
        nb = meta.n_blanks
        bw = "blank" if nb == 1 else "blanks"
        return (
            f"(GRAMMAR)\n{meta.g}\n\n"
            f"(PREFIX)\n{pfx}\n\n"
            f"(TEMPLATE)\n{meta.template}\n\n"
            f"(SUFFIX)\n{sfx}\n\n"
            f"Fill in the {nb} {bw} (___) so that PREFIX + filled-TEMPLATE + SUFFIX "
            f"is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.\n"
            f"The answer is the {meta.k} tokens of the filled TEMPLATE, space-separated."
        )

    def score_answer(self, answer, entry):
        if not answer:
            return 0.0

        ans = answer.strip().split()
        ref = entry["answer"].split()

        if ans == ref:
            return 1.0
        if len(ans) != len(ref):
            return 0.0

        # Revealed positions are hard constraints stated in the prompt
        hints = entry.metadata["hints"]
        for i, tok in hints.items():
            idx = int(i)
            if idx >= len(ans) or ans[idx] != tok:
                return 0.0

        blanks = [int(b) for b in entry.metadata["blanks"]]
        if not blanks:
            return 0.0
        blank_correct = sum(1 for b in blanks if ans[b] == ref[b]) / len(blanks)

        try:
            g = CFG.fromstring(entry.metadata["g"])
            full = list(entry.metadata["prefix"]) + ans + list(entry.metadata.get("suffix", []))
            grammatical = next(EarleyChartParser(g).parse(full), None) is not None
        except Exception:
            grammatical = False

        if grammatical:
            return 0.3 + 0.6 * blank_correct   # 0.3 – 0.9
        return 0.15 * blank_correct             # 0.0 – 0.15


# --- Stress continuation: valid_next(G, prefix) with delayed recursive state ---
#
# One generic constructor, no per-grammar templates. Given a recursive CFG, it
# builds a paired prefix: identical k-token tail, different valid-next sets. The
# shared window certifies the answer is non-local; it depends on carried parse
# state rather than the visible suffix.

INF = float("inf")

@dataclass
class StressContinuationConfig(Config):
    depth: int = 2
    n_types: int = 3
    window: int = 4
    max_answer: int = 8
    def apply_difficulty(self, level):
        self.depth += level
        self.n_types = min(6, self.n_types + level)

def _typed_dyck(n_types):
    pairs = [("(", ")"), ("[", "]"), ("<", ">"), ("{", "}"),
             ("/", "\\"), (":", ";")][:n_types]
    items = " | ".join(f"'{o}' S '{c}'" for o, c in pairs) + " | 'x'"
    return CFG.fromstring(f"S -> Item Tail\nTail -> Item Tail |\nItem -> {items}")

def _stress_sources(config):
    return {
        "dyck": _typed_dyck(config.n_types),
        "agreement": CFG.fromstring("""
            S -> NP_sg VP_sg | NP_pl VP_pl
            NP_sg -> 'the' N_sg RC | 'the' N_sg
            NP_pl -> 'the' N_pl RC | 'the' N_pl
            RC -> 'that' NP_sg V_sg | 'that' NP_pl V_pl
            VP_sg -> 'runs' | 'sleeps'
            VP_pl -> 'run' | 'sleep'
            V_sg -> 'sees' | 'likes'
            V_pl -> 'see' | 'like'
            N_sg -> 'student' | 'teacher'
            N_pl -> 'students' | 'teachers'
        """),
        "filler_gap": CFG.fromstring("""
            S -> WHO AUX NP Vt | WHY AUX NP Adj
            WHO -> 'what' | 'who'
            WHY -> 'why' | 'when'
            AUX -> 'do'
            NP -> 'the' N RC | 'the' N
            RC -> 'that' NP Vt
            N -> 'kids' | 'cooks'
            Vt -> 'see' | 'like' | 'find'
            Adj -> 'happy' | 'sad' | 'kind'
        """),
    }

def _render_rules(g):
    return "\n".join(str(p) for p in g.productions())

def _stress_answer(g, prefix):
    toks, stop, _ = get_valid_next_tokens(g, prefix)
    out = set(toks)
    if stop:
        out.add("STOP")
    return out

def _by_lhs(g):
    d = defaultdict(list)
    for p in g.productions():
        d[p.lhs()].append(p)
    return d

def _reaches(by):
    reach = {nt: {s for p in ps for s in p.rhs()
                  if isinstance(s, Nonterminal)}
             for nt, ps in by.items()}
    changed = True
    while changed:
        changed = False
        for nt in reach:
            add = set().union(*(reach.get(m, set()) for m in reach[nt]))
            add -= reach[nt]
            if add:
                reach[nt] |= add
                changed = True
    return reach

def _min_height(by):
    h = {nt: INF for nt in by}
    changed = True
    while changed:
        changed = False
        for nt, prods in by.items():
            for p in prods:
                v = 1 + max((0 if isinstance(s, str) else h.get(s, INF)
                             for s in p.rhs()), default=0)
                if v < h[nt]:
                    h[nt] = v
                    changed = True
    return h

def _terminable(p, h):
    return all(isinstance(s, str) or h.get(s, INF) < INF for s in p.rhs())

def _children(by, x):
    return {s for p in by[x] for s in p.rhs() if isinstance(s, Nonterminal)}

def _expand_min(sym, h, by):
    if isinstance(sym, str):
        return [sym]
    p = min((p for p in by[sym] if _terminable(p, h)),
            key=lambda p: max((0 if isinstance(s, str) else h[s]
                               for s in p.rhs()), default=0))
    return [t for s in p.rhs() for t in _expand_min(s, h, by)]

def _expand_deep(sym, depth, h, by, reach, rec):
    if isinstance(sym, str) or depth <= 0 or sym not in rec:
        return _expand_min(sym, h, by)
    reentr = lambda s: isinstance(s, Nonterminal) and (
        s == sym or sym in reach.get(s, set()))
    rp = [p for p in by[sym] if _terminable(p, h)
          and any(reentr(s) for s in p.rhs())]
    if not rp:
        return _expand_min(sym, h, by)
    p = random.choice(rp)
    ri = next(i for i, s in enumerate(p.rhs()) if reentr(s))
    return [t for i, s in enumerate(p.rhs())
            for t in (_expand_deep(s, depth - 1, h, by, reach, rec)
                      if i == ri else _expand_min(s, h, by))]

def _route_to(sym, R, shared, h, by, reach, _d=0):
    if sym == R:
        return list(shared)
    if isinstance(sym, str) or _d > 40:
        return _expand_min(sym, h, by) if isinstance(sym, Nonterminal) else [sym]
    reaching = lambda s: isinstance(s, Nonterminal) and (
        s == R or R in reach.get(s, set()))
    cands = [p for p in by[sym] if any(reaching(s) for s in p.rhs())]
    if not cands:
        return _expand_min(sym, h, by)
    p = random.choice(cands)
    ri = next(j for j, s in enumerate(p.rhs()) if reaching(s))
    out = []
    for j, s in enumerate(p.rhs()):
        if j == ri:
            out += _route_to(s, R, shared, h, by, reach, _d + 1)
        else:
            out += _expand_min(s, h, by) if isinstance(s, Nonterminal) else [s]
    return out

def _feature_sites(by, reach, rec):
    sites = []
    for prods in by.values():
        for p, q in ((a, b) for a in prods for b in prods if a is not b):
            for i in range(min(len(p.rhs()), len(q.rhs())) - 1):
                xp, xq = p.rhs()[i], q.rhs()[i]
                if not (isinstance(xp, Nonterminal) and isinstance(xq, Nonterminal)):
                    continue
                common = ({xp} | reach.get(xp, set())) & (
                    {xq} | reach.get(xq, set())) & rec
                if not common:
                    continue
                kids = common & _children(by, xp) & _children(by, xq)
                R = xp if xp == xq and xp in common else min(kids or common, key=str)
                sites.append((p, q, i, R))
    return sites

def _build_side(prod, i, R, shared, h, by, reach):
    out = []
    for j, s in enumerate(prod.rhs()):
        if j < i:
            out += _expand_min(s, h, by) if isinstance(s, Nonterminal) else [s]
        elif j == i:
            out += _route_to(s, R, shared, h, by, reach)
        else:
            break
    return out

def _analyze(g):
    by = _by_lhs(g)
    reach = _reaches(by)
    rec = {nt for nt in reach if nt in reach[nt]}
    return by, reach, rec, _min_height(by), _feature_sites(by, reach, rec)

def _stress_pair(g, analysis, depth, k, max_answer, tries=60):
    by, reach, rec, h, sites = analysis
    for p, q, i, R in random.sample(sites, min(tries, len(sites))):
        shared = _expand_deep(R, depth, h, by, reach, rec)
        pa = _build_side(p, i, R, shared, h, by, reach)
        pb = _build_side(q, i, R, shared, h, by, reach)
        if len(pa) < k or len(pb) < k or pa[-k:] != pb[-k:]:
            continue
        aa, ab = _stress_answer(g, pa), _stress_answer(g, pb)
        if aa == ab or not (aa and ab):
            continue
        if max(len(aa), len(ab)) > max_answer:
            continue
        return (pa, aa), (pb, ab), dict(lhs=str(p.lhs()), R=str(R))
    return None

class StressContinuation(DevTask):
    def __init__(self, config: StressContinuationConfig = StressContinuationConfig()):
        super().__init__(config=config)
        self._sources = _stress_sources(self.config)
        self._analysis = {name: _analyze(g) for name, g in self._sources.items()}
        self.bank = defaultdict(list)

    def generate_entry(self):
        names = list(self._sources)
        k = self.config.window
        for _ in range(200):
            name = random.choice(names)
            g = self._sources[name]
            depth = self.config.depth + k + random.randint(0, 2)
            pair = _stress_pair(g, self._analysis[name], depth, k,
                                self.config.max_answer)
            if not pair:
                continue
            (pa, aa), (pb, ab), m = pair
            for pfx, ans in ((pa, aa), (pb, ab)):
                self.bank[tuple(pfx[-k:])].append(frozenset(ans))
            prefix, answer = random.choice([(pa, aa), (pb, ab)])
            meta = edict(g=_render_rules(g), prefix=prefix, source=name,
                         depth=depth, lhs=m["lhs"], feature=m["R"],
                         answer_size=len(answer), window=" ".join(prefix[-k:]),
                         suffix_flip=True)
            return Entry(meta, "|".join(sorted(answer)))
        raise ValueError("Failed to generate StressContinuation case after 200 attempts")

    def render_prompt(self, meta):
        pfx = " ".join(meta.prefix) if meta.prefix else "<empty>"
        return (
            "Given this projected CFG and prefix, list every terminal that may legally come next.\n"
            "If the prefix is already a complete string, include STOP. "
            "The answer is sorted alphabetically and separated by |.\n"
            f"(GRAMMAR)\n{meta.g}\n\n(PREFIX)\n{pfx}"
        )

    def score_answer(self, answer, entry):
        try:
            ref = {x.strip() for x in entry["answer"].split("|") if x.strip()}
            ans = {x.strip() for x in str(answer).split("|") if x.strip()}
            return len(ref & ans) / max(1, len(ref | ans))
        except Exception:
            return 0.0


# --- Stress + constrained continuation: deep reentrant difficulty, worked (space-separated) answer ---
#
# Keeps stress_continuation's controlled-difficulty generator (deep recursive derivations via
# _expand_deep routed from the start through a recursive symbol with _route_to) but, like
# constrained_continuation, asks for a WORKED continuation (terminals that complete the prefix into a
# grammatical string), space-separated — NOT the |-joined set of legal next tokens. Under answer-only
# loss this trains the procedure (close nested brackets / satisfy center-embedded agreement) in a
# natural token format, instead of an unnatural option-set answer key.

def _recursive_targets(start, by, reach, rec):
    return [R for R in rec if R == start or R in reach.get(start, set())]

@dataclass
class StressConstrainedContinuationConfig(Config):
    depth: int = 3
    n_types: int = 4
    min_cont: int = 2
    max_cont: int = 12
    dyck_weight: float = 0.34   # favor word grammars (agreement/filler_gap) over bracket-heavy dyck
    def apply_difficulty(self, level):
        self.depth += level
        self.n_types = min(6, self.n_types + level)
        self.max_cont = min(20, self.max_cont + 2 * level)

class StressConstrainedContinuation(DevTask):
    def __init__(self, config: StressConstrainedContinuationConfig = StressConstrainedContinuationConfig()):
        super().__init__(config=config)
        self._sources = _stress_sources(self.config)
        self._analysis = {name: _analyze(g) for name, g in self._sources.items()}
        self.balancing_key_ratio = 0.34

    def generate_entry(self):
        names = list(self._sources)
        weights = [self.config.dyck_weight if n == "dyck" else 1.0 for n in names]
        for _ in range(300):
            name = random.choices(names, weights=weights, k=1)[0]
            g = self._sources[name]
            by, reach, rec, h, sites = self._analysis[name]
            start = g.start()
            targets = _recursive_targets(start, by, reach, rec)
            if not targets:
                continue
            R = random.choice(targets)
            depth = self.config.depth + random.randint(0, 2)
            shared = _expand_deep(R, depth, h, by, reach, rec)
            full = _route_to(start, R, shared, h, by, reach)
            if len(full) < 4:
                continue
            lo, hi = max(1, len(full) // 4), max(2, (3 * len(full)) // 4)
            cut = random.randint(lo, hi)
            prefix, cont = full[:cut], full[cut:]
            if not (self.config.min_cont <= len(cont) <= self.config.max_cont):
                continue
            nxt, stp, _u = get_valid_next_tokens(g, prefix)
            if not nxt and not stp:    # prefix must be a valid grammatical prefix
                continue
            try:
                ok = next(EarleyChartParser(g).parse(full), None) is not None
            except Exception:
                ok = False
            if not ok:
                continue
            meta = edict(g=_render_rules(g), source=name, prefix=prefix,
                         depth=depth, full_len=len(full), cont_len=len(cont),
                         lhs=str(start), feature=str(R))
            return Entry(meta, " ".join(cont))
        raise ValueError("Failed to generate StressConstrainedContinuation after 300 attempts")

    def render_prompt(self, meta):
        pfx = " ".join(meta.prefix) if meta.prefix else "<empty>"
        return (
            "Given this CFG and a prefix from a deep derivation, continue it: provide terminals that, "
            "appended to the prefix, complete it into a grammatical string.\n"
            "The answer is the continuation terminals, space-separated.\n"
            f"(GRAMMAR)\n{meta.g}\n\n(PREFIX)\n{pfx}"
        )

    def score_answer(self, answer, entry):
        if not answer:
            return 0.0
        ans = str(answer).strip().split()
        ref = entry["answer"].split()
        try:
            g = CFG.fromstring(entry.metadata["g"])
            full = list(entry.metadata["prefix"]) + ans
            grammatical = next(EarleyChartParser(g).parse(full), None) is not None
        except Exception:
            grammatical = False
        if grammatical:
            return 1.0
        m = sum(1 for a, b in zip(ans, ref) if a == b)   # partial credit: aligned-token agreement
        return 0.5 * m / max(1, len(ref))

    def balancing_key(self, problem):
        return problem.metadata["source"]

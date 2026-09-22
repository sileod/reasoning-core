import random
import sys
from dataclasses import dataclass
from functools import lru_cache

from reasoning_core.template import Config, Entry, Task

PRIMS = {
    'dup': (1, 2),
    'drop': (1, 0),
    'swap': (2, 2),
    'over': (2, 3),
    'rot': (3, 3),
    '+': (2, 1),
    '-': (2, 1),
    '*': (2, 1),
}

WORDS = {
    'double': ['dup', '+'],
    'square': ['dup', '*'],
    'inc': ['1', '+'],
    'dec': ['1', '-'],
    'negate': ['0', 'swap', '-'],
    'sum': ['+'],
    'diff': ['-'],
    'prod': ['*'],
    'quad': ['double', 'double'],
    'sumsq': ['square', 'square', '+'],
}

PRIMS_POOL = tuple(PRIMS)

NEUTRAL = [
    (2, ('swap',)),
    (1, ('dup', 'drop')),
    (2, ('over', 'drop', 'drop')),
]

PROMPT_HEAD = (
    "A concatenative (Forth-style) machine runs over an integer stack; the stack top "
    "is the last value pushed. Literals push themselves. Primitives operate on the top "
    "values: dup: a -> a a; drop: a -> ; swap: a b -> b a; over: a b -> a b a; "
    "rot: a b c -> b c a; '+': a b -> a+b; '-': a b -> a-b; '*': a b -> a*b "
    "(rightmost is the top value). A word is a named block of tokens that expands, "
    "in place, to its definition every time it is called."
)


def _clean(text):
    if text is None:
        return ''
    return ' '.join(str(text).split())


def _rand_lit(max_lit):
    return random.randint(-max_lit, max_lit)


def _op(token, args):
    if token == 'dup':
        return [args[0], args[0]]
    if token == 'drop':
        return []
    if token == 'swap':
        return [args[1], args[0]]
    if token == 'over':
        return [args[1], args[0], args[0]]
    if token == 'rot':
        return [args[2], args[0], args[1]]
    if token == '+':
        return [args[0] + args[1]]
    if token == '-':
        return [args[0] - args[1]]
    if token == '*':
        return [args[0] * args[1]]
    raise ValueError(token)


def _atom(token):
    if isinstance(token, int):
        return token
    if isinstance(token, str):
        try:
            return int(token)
        except ValueError:
            return token
    return token


def flatten(tokens):
    out = []
    for t in tokens:
        t = _atom(t)
        if isinstance(t, int):
            out.append(t)
        elif t in WORDS:
            out.extend(flatten(WORDS[t]))
        else:
            out.append(t)
    return out


def exec_flat(seq, init=None):
    st = list(init) if init is not None else []
    for t in seq:
        if isinstance(t, int):
            st.append(t)
        else:
            c, p = PRIMS[t]
            if len(st) < c:
                return None, t
            st.extend(_op(t, st[-c:]))
            del st[-c:]
    return st, None


@lru_cache(maxsize=None)
def word_min(w):
    body = flatten(WORDS[w])
    for d in range(0, 4):
        res, under = exec_flat(body, init=[i + 1 for i in range(d)])
        if under is None:
            return d
    return 3


@lru_cache(maxsize=None)
def word_prod(w):
    d = word_min(w)
    res, _ = exec_flat(flatten(WORDS[w]), init=[0] * d)
    return len(res)


def _effect(token):
    if token in PRIMS:
        return PRIMS[token]
    return word_min(token), word_prod(token)


def _exec_word_top(stack, w):
    res, under = exec_flat(flatten(WORDS[w]), init=list(stack))
    if under is not None:
        return None
    return res[-1]


def extend_safe(start_h, budget, max_lit, allow_words):
    tokens = []
    h = start_h
    for _ in range(budget):
        pool = []
        for t, (c, p) in PRIMS.items():
            if c <= h:
                pool.append(t)
        if allow_words:
            for w in list(WORDS):
                if word_min(w) <= h:
                    pool.append(w)
        if random.random() < 0.45 or not pool:
            tokens.append(_rand_lit(max_lit))
            h += 1
        else:
            t = random.choice(pool)
            c, p = _effect(t)
            tokens.append(t)
            h += p - c
    return tokens


def build_safe(n_literals, budget, max_lit, allow_words=True):
    tokens = [_rand_lit(max_lit) for _ in range(n_literals)]
    tokens.extend(extend_safe(n_literals, budget, max_lit, allow_words))
    return tokens


def build_to_height(h, budget, max_lit):
    tokens = [_rand_lit(max_lit) for _ in range(h)]
    used = 0
    while used < budget:
        avail = [e for e in NEUTRAL if e[0] <= h]
        if not avail:
            break
        consumed, toks = random.choice(avail)
        tokens.extend(toks)
        used += len(toks)
    return tokens


def gen_mode1(cfg):
    n_seed = random.randint(2, 3)
    budget = max(0, cfg.prog_len - n_seed)
    for _ in range(200):
        prog = build_safe(n_seed, budget, cfg.max_lit, allow_words=True)
        st, under = exec_flat(flatten(prog))
        if under is None and st:
            stack_top_first = list(reversed(st))
            answer = ' '.join(str(x) for x in stack_top_first)
            meta = {
                'mode': 1,
                'program': prog,
                'stack': stack_top_first,
                'answer': answer,
            }
            return meta
    raise RuntimeError('mode1 failed')


def gen_mode2(cfg):
    ws = [w for w in WORDS if word_min(w) <= 2]
    for _ in range(200):
        w = random.choice(ws)
        d = word_min(w)
        left = build_safe(d, random.randint(0, 2), cfg.max_lit, allow_words=False)
        L, under = exec_flat(flatten(left))
        if under is not None:
            continue
        top_after = _exec_word_top(L, w)
        if top_after is None:
            continue
        post_h = len(L) - word_min(w) + word_prod(w)
        tail_budget = max(0, random.randint(0, cfg.prog_len - len(left) - 1))
        tail = extend_safe(max(1, post_h), tail_budget, cfg.max_lit, allow_words=False)
        prog = left + [w] + tail
        st2, u2 = exec_flat(flatten(prog))
        if u2 is not None:
            continue
        if not _surface_safe_count(prog, top_after):
            continue
        meta = {
            'mode': 2,
            'program': prog,
            'word': w,
            'top_after': int(top_after),
            'answer': str(int(top_after)),
        }
        return meta
    raise RuntimeError('mode2 failed')


def _lits_in(tokens):
    return [t for t in tokens if isinstance(t, int)]


def _surface_safe_count(prog, answer_int):
    lits = _lits_in(prog)
    if not lits:
        return True
    if int(prog[-1]) == answer_int if isinstance(prog[-1], int) else False:
        return False
    if int(prog[0]) == answer_int if isinstance(prog[0], int) else False:
        return False
    if max(lits) == answer_int and len([x for x in lits if x == answer_int]) == 1:
        xs = [x for x in lits if x != answer_int]
        return bool(xs)
    return True


def gen_mode3(cfg):
    ws = [w for w in WORDS if word_min(w) >= 2]
    for _ in range(200):
        w = random.choice(ws)
        dmin = word_min(w)
        prefix = build_to_height(dmin - 1, random.randint(0, 2), cfg.max_lit)
        st, under = exec_flat(flatten(prefix))
        if under is not None or len(st) != dmin - 1:
            continue
        prog = prefix + [w]
        st2, u2 = exec_flat(flatten(prog))
        if u2 is None:
            continue
        if w in _lits_in(prog):
            continue
        tail = extend_safe(1, random.randint(1, 2), cfg.max_lit, allow_words=False)
        prog = prefix + [w] + tail
        meta = {
            'mode': 3,
            'program': prog,
            'word': w,
            'prefix': prefix,
            'tail': tail,
            'answer': w,
        }
        return meta
    raise RuntimeError('mode3 failed')


@dataclass
class ConcatStackConfig(Config):
    prog_len: int = 5
    max_lit: int = 6

    def apply_difficulty(self, level):
        self.prog_len = 5 + level
        self.max_lit = 6 + 4 * level


class ConcatStackEvaluate(Task):
    summary = (
        "Execute concatenative programs: literals and primitives push and shuffle a stack "
        "while defined words expand in place at each call; modes ask for the final stack, "
        "the stack top after a nested call, or which word first underflows."
    )
    design_choice = (
        "Represent programs as fixed token sequences; answers are canonical stack renderings "
        "like '3 2 1' with balanced literal values across levels."
    )
    config_cls = ConcatStackConfig
    task_version = 2

    def generate_entry(self):
        mode = random.randint(1, 3)
        if mode == 1:
            meta = gen_mode1(self.config)
        elif mode == 2:
            meta = gen_mode2(self.config)
        else:
            meta = gen_mode3(self.config)
        return Entry(metadata=meta, answer=meta['answer'])

    def render_prompt(self, metadata):
        mode = metadata['mode']
        prog = ' '.join(str(t) for t in metadata['program'])
        used = sorted({t for t in metadata['program'] if t in WORDS}, key=str)
        if used:
            defs = ' | '.join('%s = %s' % (w, ' '.join(WORDS[w])) for w in used)
            dict_line = 'Definitions: ' + defs + '.'
        else:
            dict_line = ''
        if mode == 1:
            return (
                PROMPT_HEAD + ' ' + dict_line +
                "\n\nProgram: %s\n\n"
                "Evaluate the whole program. Give the final stack as space-separated "
                "integers from TOP (first) to BOTTOM (last); the answer is exactly that "
                "space-separated list." % prog
            )
        if mode == 2:
            w = metadata['word']
            return (
                PROMPT_HEAD + ' ' + dict_line +
                "\n\nProgram: %s\n\n"
                "After the word '%s' finishes executing at its call site, what is the top "
                "value of the stack? Answer with the single integer." % (prog, w)
            )
        return (
            PROMPT_HEAD + ' ' + dict_line +
            "\n\nProgram: %s\n\n"
            "Executing left to right, some word call may underflow (reach for values the "
            "stack does not hold). Which word is the FIRST to underflow? Answer with the "
            "word name." % prog
        )

    def score_answer(self, answer, entry):
        gold = entry['answer']
        return 1.0 if _clean(answer) == _clean(gold) else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'concatenative_stack_evaluation (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_parsing_and_agreement_r4/concatenative_stack_evaluation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

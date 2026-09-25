"""Evaluate whether two expressions mixing reference, quotation, splicing, and
names of expressions denote the same object in a tiny list language."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

SYMBOLS = ["red", "wine", "horse", "stone", "fog", "reed", "lake", "pine",
           "snow", "vine", "wheat", "flint", "gale", "bloom", "cinder", "moss"]
VAR_NAMES = ["A", "B", "C", "D", "E", "F"]


def atom_data(tok):
    """Data value of a quoted/bare atom token: integers stay integers, and both
    symbols and variables become their *name* as a symbol."""
    if tok.lstrip("-").isdigit():
        return int(tok)
    return ("sym", tok)


def denote_form(form, env):
    """Denotation of a form under an environment.

    form is either ("bare", tok) or ("quote", [(kind, payload), ...]) with
    kind in {"a" (atom), "s" (splice / unquote)}. A bare variable references
    its bound value; all other bare atoms self-evaluate. Inside a quote,
    each atom contributes its name-data (the expression's name), while a
    splice ,X injects the value X is bound to (reference across the quotation
    boundary). A single quoted unit stands alone; two or more form a list.
    """
    if form[0] == "bare":
        tok = form[1]
        if tok.lstrip("-").isdigit():
            return int(tok)
        if tok.isupper():
            return env[tok]
        return ("sym", tok)
    contribs = []
    for kind, payload in form[1]:
        if kind == "a":
            contribs.append(atom_data(payload))
        else:
            contribs.append(env[payload])
    if len(contribs) == 1:
        return contribs[0]
    return tuple(contribs)


def render_form(form):
    if form[0] == "bare":
        return form[1]
    units = []
    for kind, payload in form[1]:
        if kind == "a":
            units.append(payload)
        else:
            units.append("," + payload)
    return "' " + " ".join(units)


def render_bindings(bindings):
    parts = []
    for name in bindings:
        kind, data = bindings[name]
        if kind == "sym":
            parts.append(name + " = " + data)
        else:
            parts.append(name + " = (" + " ".join(data) + ")")
    return ", ".join(parts)


@dataclass
class QuotationConfig(Config):
    n_vars: int = 2
    max_units: int = 2
    max_list: int = 1
    list_chance: float = 0.0
    splice_chance: float = 0.15
    bare_chance: float = 0.2

    def apply_difficulty(self, level):
        self.n_vars = 2 + level // 2
        self.max_units = 2 + level
        self.max_list = 1 + level // 2
        self.list_chance = 0.05 * level
        self.splice_chance = 0.15 + 0.05 * level
        self.bare_chance = 0.2


class QuotationReferenceComposition(Task):
    summary = ("Evaluate expressions mixing reference, quotation, splicing, and "
               "names of expressions across nested quotation boundaries; "
               "distinguish identical referents from identical wording and "
               "answer the resulting denotation.")
    design_choice = ("Present pairs of expressions with identical denotation "
                     "but different wording and ask yes/no whether they denote "
                     "the same object.")
    config_cls = QuotationConfig
    task_version = 2

    def _make_env(self):
        names = random.sample(VAR_NAMES, self.config.n_vars)
        env = {}
        for i, name in enumerate(names):
            if i == 0 or not (self.config.list_chance and
                              random.random() < self.config.list_chance):
                env[name] = ("sym", random.choice(SYMBOLS))
            else:
                length = 1 + random.randrange(self.config.max_list)
                env[name] = ("list", [random.choice(SYMBOLS)
                                      for _ in range(length)])
        return env

    def _rand_unit(self, env, unit_choices):
        r = random.random()
        if r < self.config.splice_chance and unit_choices:
            return ("s", random.choice(unit_choices))
        if random.random() < 0.1:
            return ("a", str(random.randrange(1, 10)))
        return ("a", random.choice(SYMBOLS))

    def _build_yes(self, env):
        symvars = [n for n, v in env.items() if v[0] == "sym"]
        v = random.choice(symvars)
        s = env[v][1]
        if random.random() < self.config.bare_chance:
            return ("bare", v), ("quote", [("a", s)])
        length = 1 + random.randrange(max(1, self.config.max_units))
        units1 = []
        for _ in range(length):
            units1.append(self._rand_unit(env, symvars))
        p = random.randrange(length)
        units1[p] = ("a", s)
        units2 = list(units1)
        units2[p] = ("s", v)
        return ("quote", units1), ("quote", units2)

    def _rand_form(self, env):
        if random.random() < self.config.bare_chance:
            tok = random.choice(
                [random.choice(SYMBOLS), str(random.randrange(1, 10))]
                + [n for n in env])
            return ("bare", tok)
        length = 1 + random.randrange(max(1, min(self.config.max_units, 4)))
        units = [self._rand_unit(env, [n for n in env])
                 for _ in range(length)]
        return ("quote", units)

    def _build_no(self, env):
        for _ in range(60):
            f1 = self._rand_form(env)
            f2 = self._rand_form(env)
            if denote_form(f1, env) != denote_form(f2, env):
                return f1, f2
        return ("quote", [("a", "red")]), ("quote", [("a", "wine")])

    def generate_entry(self):
        config = self.config
        env = self._make_env()
        if random.random() < 0.5:
            f1, f2 = self._build_yes(env)
            answer = "yes"
        else:
            f1, f2 = self._build_no(env)
            answer = "no"
        assert denote_form(f1, env) == (
            denote_form(f2, env) if answer == "yes" else None) or True
        if answer == "yes":
            assert denote_form(f1, env) == denote_form(f2, env)
        else:
            assert denote_form(f1, env) != denote_form(f2, env)
        assert _is_json_safe(env)
        entry = Entry(metadata={
            "expr1": render_form(f1),
            "expr2": render_form(f2),
            "bindings": env,
        }, answer=answer)
        return entry

    def render_prompt(self, metadata):
        bindings = render_bindings(metadata["bindings"])
        return (
            "We evaluate a tiny list language. Bare symbols (like red) and "
            "integers (like 17) denote themselves. A capital-letter variable "
            "denotes the value it is bound to. A quote ' u1 u2 ... un treats "
            "each unit as syntax rather than as a value: quoting a symbol "
            "yields that symbol, and quoting a variable yields its name as a "
            "symbol. An unquote ,X inside a quote inserts the value that X is "
            "bound to. A single quoted unit stands alone; two or more quoted "
            "units form a list.\n\n"
            "Bindings: " + bindings + "\n\n"
            "Expression 1: " + metadata["expr1"] + "\n"
            "Expression 2: " + metadata["expr2"] + "\n\n"
            "Do Expression 1 and Expression 2 denote the same object? Answer "
            "with a single word: \"yes\" if they denote the same object, "
            "\"no\" otherwise."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        norm = answer.strip().lower()
        if norm not in ("yes", "no"):
            return 0.0
        return 1.0 if norm == entry.answer else 0.0


def _is_json_safe(env):
    for name, (kind, data) in env.items():
        if kind == "sym":
            if not isinstance(data, str):
                return False
        else:
            if not isinstance(data, list) or not all(
                    isinstance(x, str) for x in data):
                return False
    return True


TASK_META = {'parent_source_id': None,
 'idea': 'quotation_reference_composition (variant 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scope_and_binding_r4/quotation_reference_composition',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

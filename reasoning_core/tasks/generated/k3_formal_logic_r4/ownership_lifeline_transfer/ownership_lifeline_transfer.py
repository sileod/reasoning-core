import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround

TASK_META = {'parent_source_id': None,
 'idea': 'ownership_lifeline_transfer (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_logic_r4/ownership_lifeline_transfer',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_RULES = ("moved-value", "borrow-in-use", "no-active-loan")
_OP_WEIGHTS = {"move": 3, "borrow": 4, "reborrow": 3, "return": 3, "freeze": 2, "drop": 1}


def _letters(n):
    return [chr(ord("A") + i) for i in range(n)]


def _check(ev, owner, loans, frozen):
    op, a, b = ev
    if op == "move":
        if a != owner:
            return "moved-value"
        if frozen or loans:
            return "borrow-in-use"
        return None
    if op == "borrow":
        if a != owner:
            return "moved-value"
        return None
    if op in ("reborrow", "return"):
        if a not in loans:
            return "no-active-loan"
        return None
    if op == "drop":
        if a != owner:
            return "moved-value"
        if frozen or loans:
            return "borrow-in-use"
        return None
    return None


def _apply(ev, owner, loans, frozen):
    op, a, b = ev
    if op == "move":
        return (b, set(loans), frozen)
    if op == "borrow":
        loans = set(loans)
        loans.add(b)
        return (owner, loans, frozen)
    if op == "reborrow":
        loans = set(loans)
        loans.add(b)
        return (owner, loans, frozen)
    if op == "return":
        loans = set(loans)
        loans.discard(a)
        return (owner, loans, frozen)
    if op == "freeze":
        return (owner, set(loans), True)
    if op == "drop":
        return (None, set(), False)
    return (owner, set(loans), frozen)


def _first_illegal(events, owner):
    loans, frozen = set(), False
    for i, ev in enumerate(events):
        r = _check(ev, owner, loans, frozen)
        if r is not None:
            return (i, r)
        owner, loans, frozen = _apply(ev, owner, loans, frozen)
    return None


def _legit(op, owner, loans, frozen, names):
    if op == "move":
        if frozen or loans:
            return None
        others = [n for n in names if n != owner]
        if not others:
            return None
        return ("move", owner, random.choice(others))
    if op == "borrow":
        others = [n for n in names if n != owner]
        if not others:
            return None
        return ("borrow", owner, random.choice(others))
    if op == "reborrow":
        if not loans:
            return None
        return ("reborrow", random.choice(sorted(loans)), random.choice(names))
    if op == "return":
        if not loans:
            return None
        return ("return", random.choice(sorted(loans)), None)
    if op == "freeze":
        return ("freeze", None, None)
    if op == "drop":
        if frozen or loans:
            return None
        return ("drop", owner, None)
    return None


def _build_legal(count, owner, names):
    loans, frozen = set(), False
    events = []
    for i in range(count):
        op = random.choices(list(_OP_WEIGHTS), weights=list(_OP_WEIGHTS.values()))[0]
        if op == "drop" and i != count - 1:
            op = random.choice(["move", "borrow", "reborrow", "return", "freeze"])
        ev = _legit(op, owner, loans, frozen, names)
        if ev is None:
            op = random.choice(["move", "borrow", "reborrow", "return"])
            ev = _legit(op, owner, loans, frozen, names)
            if ev is None:
                ev = ("freeze", None, None)
        events.append(ev)
        owner, loans, frozen = _apply(ev, owner, loans, frozen)
    return events


def _constructible_rules(state, names):
    owner, loans, frozen = state
    rules = []
    if len(names) >= 2:
        rules.append("moved-value")
    if any(n not in loans for n in names):
        rules.append("no-active-loan")
    if frozen or loans:
        rules.append("borrow-in-use")
    return rules


def _make_poison(rule, state, names):
    owner, loans, frozen = state
    if rule == "moved-value":
        x = random.choice([n for n in names if n != owner])
        op = random.choice(["move", "borrow", "drop"])
        if op == "drop":
            return ("drop", x, None)
        others = [n for n in names if n != x] or [owner]
        return (op, x, random.choice(others))
    if rule == "no-active-loan":
        x = random.choice([n for n in names if n not in loans])
        op = random.choice(["return", "reborrow"])
        if op == "return":
            return ("return", x, None)
        return ("reborrow", x, random.choice(names))
    op = random.choice(["move", "drop"])
    if op == "drop":
        return ("drop", owner, None)
    others = [n for n in names if n != owner] or names
    return ("move", owner, random.choice(others))
    raise RuntimeError("unknown rule")


@dataclass
class OwnershipLifelineTransferV2Config(Config):
    count: int = 6
    nvars: int = 3

    def apply_difficulty(self, level):
        self.count = sround(self.count + level * 2)
        self.nvars = sround(self.nvars + level)


class OwnershipLifelineTransfer(Task):
    summary = "Apply move, split-borrow, reborrow, freeze, return-to-owner, and drop events through blocks and calls; answer owners and borrow caps at a point, or the first illegal use."
    design_choice = "Events may include an illegal move/borrow; answer is the first illegal event index and the rule violated, with no final-state query."
    task_version = 2
    config_cls = OwnershipLifelineTransferV2Config

    def generate_entry(self):
        names = _letters(max(2, int(self.config.nvars)))
        count = max(3, int(self.config.count))
        for _ in range(300):
            owner = random.choice(names)
            legal = _build_legal(count, owner, names)
            k = random.randrange(count)
            state = _first_illegal(legal[:k], owner)
            assert state is None, "legal-prefix build produced an illegal event"
            cur = owner
            loans, frozen = set(), False
            for ev in legal[:k]:
                cur, loans, frozen = _apply(ev, cur, loans, frozen)
            pre_state = (cur, loans, frozen)
            rules = _constructible_rules(pre_state, names)
            rule = random.choice(rules)
            poison = _make_poison(rule, pre_state, names)
            full = legal[:k] + [poison] + legal[k + 1:]
            fi = _first_illegal(full, owner)
            if fi is not None and fi[0] == k:
                idx, gold_rule = fi
                answer = f"{idx + 1}: {gold_rule}"
                metadata = edict({
                    "names": list(names),
                    "initial_owner": owner,
                    "events": full,
                    "illegal_index": int(idx),
                    "rule": gold_rule,
                })
                assert 1 <= idx + 1 <= len(full)
                return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("could not construct a poisoned ownership trace")

    def render_prompt(self, metadata):
        names = " ".join(metadata.names)
        lines = []
        for i, ev in enumerate(metadata.events):
            op, a, b = ev
            if op == "move":
                lines.append(f"{i + 1}: move {a} to {b}")
            elif op == "borrow":
                lines.append(f"{i + 1}: borrow {a} to {b}")
            elif op == "reborrow":
                lines.append(f"{i + 1}: reborrow {a} to {b}")
            elif op == "return":
                lines.append(f"{i + 1}: return {a}")
            elif op == "freeze":
                lines.append(f"{i + 1}: freeze")
            elif op == "drop":
                lines.append(f"{i + 1}: drop {a}")
            else:
                lines.append(f"{i + 1}: {op} {a} {b}")
        body = "\n".join(lines)
        return (
            f"Track a single value under the variables {names}. Exactly one variable is the "
            f"current owner of the value; any other variable is 'moved' and no longer owns it. "
            f"Several variables may hold overlapping shared borrows simultaneously. The events are:\n"
            f"- `move X to Y`: ownership transfers from X to Y (illegal if X is not the owner, or if "
            f"the value is frozen or any borrow is held).\n"
            f"- `borrow X to Y`: owner X lends a shared borrow that Y now holds (illegal if X is not "
            f"the owner; borrows may accumulate even when frozen).\n"
            f"- `reborrow X to Y`: Y takes a borrow from X's existing borrow (illegal if X holds no "
            f"loan).\n"
            f"- `return X`: X releases the borrow it holds (illegal if X holds no loan).\n"
            f"- `freeze`: the value becomes frozen, blocking any move or drop.\n"
            f"- `drop X`: X destroys the value (illegal if X is not the owner, or if the value is "
            f"frozen or any borrow is held).\n"
            f"The events below are applied in order.\n"
            f"{body}\n"
            f"Find the FIRST event that is illegal. Answer with its 1-based index and the rule it "
            f"violates, exactly as `N: rule` where rule is one of `moved-value`, `borrow-in-use`, "
            f"or `no-active-loan`. For example: `5: moved-value`."
        )

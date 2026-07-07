# Config Difficulty Knob Migration

## Goal

Migrate task difficulty scaling from implicit repeated `Config.update(c)` calls to an explicit `Config.apply_difficulty(level)` method.

The migration assumes a fixed unit step: legacy comparison replays `update(1)`. Do not use `Config.c` or `self.c` in new code.

Current behavior:

- `config.set_level(0)` resets to the base config.
- `config.set_level(1)` calls `update(1)` once.
- `config.set_level(2)` calls `update(1)` twice.
- In general, level `n` applies `update(1)` `n` times.

Desired behavior:

- `config.set_level(level)` resets to the base config.
- `config.set_level(level)` calls `apply_difficulty(level)` once.
- Each task config owns a direct, non-recursive formula for its difficulty knobs.
- Existing `update(c)` methods were temporarily kept during the migration so old and new behavior could be compared.
- Do not add `update(c)` to new configs.

## Important Files

- `TASK_AUTHORING_GUIDE.md`: task authoring rules.
- `GALLERY.md`: prompt and answer examples.
- `reasoning_core/template.py`: base `Config`, stochastic rounding, migration helper.
- `reasoning_core/tasks/`: task config classes.
- `tests/test_config_difficulty_migration.py`: migration test examples.

## New Shared Machinery

`reasoning_core.template.Config` now has:

```python
def apply_difficulty(self, level: int):
    for _ in range(level):
        self.update(1)
```

This default preserves legacy behavior. Migrated configs should override it with a direct formula.

`reasoning_core.template.stochastic_rounding(value)` contains the shared rounding rule used by `Config` int fields. During `set_level(...)`, it uses the active config seed automatically. In migrated task files, import it as `sround`:

```python
from reasoning_core.template import stochastic_rounding as sround
```

`reasoning_core.template.assert_difficulty_update_equivalence(config, levels=range(6))` checks that a migrated config's `apply_difficulty(level)` produces the same public rounded config state as repeated legacy `update(1)`.

## Example Migration

Linear example before:

```python
@dataclass
class ArithmeticsConfig(Config):
    min_depth: int = 3
    max_depth: int = 5
    out_decimals: int = 3
    out_digits: int = 6

    def update(self, c):
        self.min_depth += c
        self.max_depth += c
        self.out_digits += c
        self.out_decimals += c
```

After:

```python
@dataclass
class ArithmeticsConfig(Config):
    min_depth: int = 3
    max_depth: int = 5
    out_decimals: int = 3
    out_digits: int = 6

    def update(self, c):
        self.min_depth += c
        self.max_depth += c
        self.out_digits += c
        self.out_decimals += c

    def apply_difficulty(self, level):
        self.min_depth = sround(self.min_depth + level)
        self.max_depth = sround(self.max_depth + level)
        self.out_digits = sround(self.out_digits + level)
        self.out_decimals = sround(self.out_decimals + level)
```

Test:

```python
from reasoning_core.template import assert_difficulty_update_equivalence
from reasoning_core.tasks.arithmetics import ArithmeticsConfig


def test_arithmetics_apply_difficulty_matches_repeated_update():
    assert assert_difficulty_update_equivalence(ArithmeticsConfig(), levels=range(6))
```

Another migrated example with legacy `round(...)` behavior:

```python
def update(self, c):
    self.seq_len = max(8, self.seq_len + round(8 * c))
    self.vocab_size = max(16, self.vocab_size + round(8 * c))
    self.k = min(16, max(2, self.k + round(c / 2)))
    self.max_depth = max(4, self.max_depth + round(2 * c))

def apply_difficulty(self, level):
    self.seq_len = sround(max(8, self.seq_len + 8 * level))
    self.vocab_size = sround(max(16, self.vocab_size + 8 * level))
    self.k = sround(min(16, max(2, self.k + round(1 / 2) * level)))
    self.max_depth = sround(max(4, self.max_depth + 2 * level))
```

This preserves Python's legacy `round(0.5) == 0` behavior for `k`.

## Migration Instructions

1. Check the worktree first:

```bash
git status --short
```

Do not revert or rewrite unrelated dirty files.

2. Read the task config's existing `update(c)`.

3. Add `apply_difficulty(self, level)` to the same config class.

4. Translate repeated updates into a direct formula from the base config state.

Common patterns:

```python
# repeated: self.n += a * c, with c=1
self.n = sround(self.n + level * a)

# repeated: self.n *= (1 + c), with c=1
self.n = sround(self.n * (2 ** level))

# repeated: self.x += c; self.y += 2 * c, with c=1
self.x = sround(self.x + level)
self.y = sround(self.y + level * 2)
```

5. Remove `update(c)` from active task configs once `apply_difficulty(level)` has been reviewed. Keep deprecated-task compatibility separate.

6. Add or extend tests using `assert_difficulty_update_equivalence`.

7. Run the focused test:

```bash
python -m pytest tests/test_config_difficulty_migration.py
```

8. If a migrated task has a cheap existing validation test, run that too.

## Handling Nonlinear or Threshold Updates

Some configs include logic like:

```python
self.max_arity = min(4, self.max_arity + int(c >= 3))
```

For these, write the explicit formula carefully. If the formula is not obvious, keep it simple and exact:

```python
def apply_difficulty(self, level):
    self.n_vars = sround(self.n_vars + level * 0.6)
    self.max_domain = sround(self.max_domain + level * 0.4)
    self.n_constraints = sround(self.n_constraints + level * 1.1)
    self.coef_bound = sround(self.coef_bound + level * 0.3)
    self.max_arity = sround(min(4, self.max_arity + level * int(1 >= 3)))
```

Then rely on `assert_difficulty_update_equivalence(...)`.

## Stochastic Integer Fields

`Config` stores int-typed difficulty fields internally as floats and stochastically rounds when the field is read.

In migrated `apply_difficulty(level)` methods, call `sround(...)` when assigning int-typed difficulty fields. This makes the target-level config explicit while preserving the shared stochastic rounding rule.

Do not cast these fields to `int` inside `update` or `apply_difficulty` unless the old behavior already did that explicitly.

Use `assert_difficulty_update_equivalence`; it compares public rounded config values with a fixed test seed, avoiding random false failures.

## What Not To Do

- Do not remove the base compatibility fallback until deprecated tasks have either migrated or been explicitly retired.
- Do not change generation logic while migrating difficulty.
- Do not modify task prompts, scoring, or unrelated config defaults.
- Do not bulk-format files.
- Do not traverse or edit generated environments like `reasoning_core/openenv`, `.venv`, checkpoints, or cache folders.

## Completion Criteria

For each migrated config:

- `apply_difficulty(level)` exists.
- Active task configs do not define `update(c)`.
- A test proves `apply_difficulty(level)` equals repeated `update(1)` for representative levels, usually `range(6)`.
- Focused tests pass.

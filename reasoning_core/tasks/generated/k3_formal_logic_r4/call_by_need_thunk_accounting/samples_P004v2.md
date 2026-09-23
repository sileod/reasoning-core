# Level 0

**Prompt:**

```
Under call-by-need, a definition is evaluated only when its value is demanded, the first time it is needed; a shared thunk is memoized, so each expression runs at most once. A program defines these aliases and expressions:

    x0 = 1
    x1 = 1
    x2 = 1
    x3 = x1

The top-level expression whose value must be produced references (demands) the definitions x1.

Forcing that expression forces exactly those definitions reachable from x1 through the references in their right-hand sides.

List, in ascending lexicographic order and separated by commas, the names of all definitions that are NEVER demanded (never evaluated). If none are never demanded, answer the single word: none

Answer:
```

**Answer:** x0, x2, x3

**Prompt:**

```
Under call-by-need, a definition is evaluated only when its value is demanded, the first time it is needed; a shared thunk is memoized, so each expression runs at most once. A program defines these aliases and expressions:

    x0 = 1
    x1 = x0
    x2 = x0
    x3 = 1

The top-level expression whose value must be produced references (demands) the definitions x2.

Forcing that expression forces exactly those definitions reachable from x2 through the references in their right-hand sides.

List, in ascending lexicographic order and separated by commas, the names of all definitions that are NEVER demanded (never evaluated). If none are never demanded, answer the single word: none

Answer:
```

**Answer:** x1, x3



# Level 2

**Prompt:**

```
Under call-by-need, a definition is evaluated only when its value is demanded, the first time it is needed; a shared thunk is memoized, so each expression runs at most once. A program defines these aliases and expressions:

    x0 = 1
    x1 = 1
    x2 = 1
    x3 = x0 + x1
    x4 = x0 + x1 + x3
    x5 = x0 + x1 + x3 + x4
    x6 = x0
    x7 = x2

The top-level expression whose value must be produced references (demands) the definitions x5.

Forcing that expression forces exactly those definitions reachable from x5 through the references in their right-hand sides.

List, in ascending lexicographic order and separated by commas, the names of all definitions that are NEVER demanded (never evaluated). If none are never demanded, answer the single word: none

Answer:
```

**Answer:** x2, x6, x7

**Prompt:**

```
Under call-by-need, a definition is evaluated only when its value is demanded, the first time it is needed; a shared thunk is memoized, so each expression runs at most once. A program defines these aliases and expressions:

    x0 = 1
    x1 = 1
    x2 = 1
    x3 = x1
    x4 = x0 + x2 + x3
    x5 = x0
    x6 = x0 + x2 + x3 + x5
    x7 = x2 + x3 + x5

The top-level expression whose value must be produced references (demands) the definitions x5.

Forcing that expression forces exactly those definitions reachable from x5 through the references in their right-hand sides.

List, in ascending lexicographic order and separated by commas, the names of all definitions that are NEVER demanded (never evaluated). If none are never demanded, answer the single word: none

Answer:
```

**Answer:** x1, x2, x3, x4, x6, x7



# Level 5

**Prompt:**

```
Under call-by-need, a definition is evaluated only when its value is demanded, the first time it is needed; a shared thunk is memoized, so each expression runs at most once. A program defines these aliases and expressions:

    x00 = 1
    x01 = 1
    x02 = x00
    x03 = 1
    x04 = x00 + x03
    x05 = x00 + x01 + x02 + x04
    x06 = x01 + x02 + x03 + x04 + x05
    x07 = x00 + x01 + x02 + x04 + x05
    x08 = x00 + x01 + x03 + x04 + x05 + x06
    x09 = x01 + x02 + x03 + x04 + x05 + x06 + x07
    x10 = x00 + x01 + x03 + x04 + x05 + x07 + x08 + x09
    x11 = x00 + x01 + x02 + x03 + x04 + x05 + x06 + x07 + x08 + x09
    x12 = x02 + x04 + x05 + x07 + x08 + x09 + x11
    x13 = x02 + x03 + x04 + x06 + x07 + x08 + x10 + x11

The top-level expression whose value must be produced references (demands) the definitions x02, x08.

Forcing that expression forces exactly those definitions reachable from x02, x08 through the references in their right-hand sides.

List, in ascending lexicographic order and separated by commas, the names of all definitions that are NEVER demanded (never evaluated). If none are never demanded, answer the single word: none

Answer:
```

**Answer:** x07, x09, x10, x11, x12, x13

**Prompt:**

```
Under call-by-need, a definition is evaluated only when its value is demanded, the first time it is needed; a shared thunk is memoized, so each expression runs at most once. A program defines these aliases and expressions:

    x00 = 1
    x01 = 1
    x02 = x00 + x01
    x03 = x00 + x01
    x04 = x00 + x02
    x05 = x00 + x01 + x03 + x04
    x06 = x00 + x02 + x03 + x04
    x07 = x01 + x02 + x04 + x05 + x06
    x08 = x00 + x01 + x02 + x04 + x05 + x06 + x07
    x09 = x00 + x01 + x04 + x05 + x06 + x07 + x08
    x10 = x01 + x04 + x06 + x07
    x11 = x00 + x01 + x02 + x05 + x06 + x10
    x12 = x00 + x04 + x05 + x07 + x09
    x13 = x00 + x01 + x04 + x05 + x06 + x09 + x10 + x12

The top-level expression whose value must be produced references (demands) the definitions x05, x12.

Forcing that expression forces exactly those definitions reachable from x05, x12 through the references in their right-hand sides.

List, in ascending lexicographic order and separated by commas, the names of all definitions that are NEVER demanded (never evaluated). If none are never demanded, answer the single word: none

Answer:
```

**Answer:** x10, x11, x13



## Level 0

### Example

**Prompt**

```
A transition rule maps each state of a product system to a next state. There are 3 coordinates, each taking values 0..1. The rule is axis-separable if there is a permutation of the coordinates (a bijection from source coordinates to target coordinates) such that each target coordinate's next value depends only on the current value of the one matching source coordinate. The full transition table is:
(0, 0, 0) -> (1, 0, 0)
(0, 0, 1) -> (0, 0, 0)
(0, 1, 0) -> (1, 0, 1)
(0, 1, 1) -> (0, 0, 1)
(1, 0, 0) -> (1, 1, 0)
(1, 0, 1) -> (0, 1, 0)
(1, 1, 0) -> (1, 1, 1)
(1, 1, 1) -> (0, 1, 1)
Is the rule axis-separable? If yes, answer 'yes' followed by a space, then the recovered permutation as the list of source coordinate indices read in target-coordinate order (e.g. for 3 coordinates 'yes 1 0 2'). If no, answer exactly 'no'.
```

**Answer**: `yes 2 0 1`

### Example

**Prompt**

```
A transition rule maps each state of a product system to a next state. There are 3 coordinates, each taking values 0..1. The rule is axis-separable if there is a permutation of the coordinates (a bijection from source coordinates to target coordinates) such that each target coordinate's next value depends only on the current value of the one matching source coordinate. The full transition table is:
(0, 0, 0) -> (0, 0, 0)
(0, 0, 1) -> (1, 0, 0)
(0, 1, 0) -> (0, 1, 0)
(0, 1, 1) -> (1, 1, 0)
(1, 0, 0) -> (0, 0, 1)
(1, 0, 1) -> (1, 0, 1)
(1, 1, 0) -> (0, 1, 1)
(1, 1, 1) -> (1, 1, 1)
Is the rule axis-separable? If yes, answer 'yes' followed by a space, then the recovered permutation as the list of source coordinate indices read in target-coordinate order (e.g. for 3 coordinates 'yes 1 0 2'). If no, answer exactly 'no'.
```

**Answer**: `yes 2 1 0`

## Level 2

### Example

**Prompt**

```
A transition rule maps each state of a product system to a next state. There are 3 coordinates, each taking values 0..1. The rule is axis-separable if there is a permutation of the coordinates (a bijection from source coordinates to target coordinates) such that each target coordinate's next value depends only on the current value of the one matching source coordinate. The full transition table is:
(0, 0, 0) -> (0, 0, 0)
(0, 0, 1) -> (1, 0, 0)
(0, 1, 0) -> (0, 0, 1)
(0, 1, 1) -> (1, 0, 1)
(1, 0, 0) -> (0, 1, 0)
(1, 0, 1) -> (1, 1, 0)
(1, 1, 0) -> (0, 1, 1)
(1, 1, 1) -> (1, 1, 1)
Is the rule axis-separable? If yes, answer 'yes' followed by a space, then the recovered permutation as the list of source coordinate indices read in target-coordinate order (e.g. for 3 coordinates 'yes 1 0 2'). If no, answer exactly 'no'.
```

**Answer**: `yes 2 0 1`

### Example

**Prompt**

```
A transition rule maps each state of a product system to a next state. There are 3 coordinates, each taking values 0..1. The rule is axis-separable if there is a permutation of the coordinates (a bijection from source coordinates to target coordinates) such that each target coordinate's next value depends only on the current value of the one matching source coordinate. The full transition table is:
(0, 0, 0) -> (0, 1, 1)
(0, 0, 1) -> (0, 1, 0)
(0, 1, 0) -> (0, 0, 1)
(0, 1, 1) -> (0, 0, 0)
(1, 0, 0) -> (1, 1, 1)
(1, 0, 1) -> (1, 1, 0)
(1, 1, 0) -> (1, 0, 1)
(1, 1, 1) -> (1, 0, 0)
Is the rule axis-separable? If yes, answer 'yes' followed by a space, then the recovered permutation as the list of source coordinate indices read in target-coordinate order (e.g. for 3 coordinates 'yes 1 0 2'). If no, answer exactly 'no'.
```

**Answer**: `yes 0 1 2`

## Level 5

### Example

**Prompt**

```
A transition rule maps each state of a product system to a next state. There are 4 coordinates, each taking values 0..1. The rule is axis-separable if there is a permutation of the coordinates (a bijection from source coordinates to target coordinates) such that each target coordinate's next value depends only on the current value of the one matching source coordinate. The full transition table is:
(0, 0, 0, 0) -> (0, 1, 0, 1)
(0, 0, 0, 1) -> (1, 1, 0, 1)
(0, 0, 1, 0) -> (0, 1, 0, 0)
(0, 0, 1, 1) -> (1, 1, 0, 0)
(0, 1, 0, 0) -> (0, 0, 0, 1)
(0, 1, 0, 1) -> (1, 0, 0, 1)
(0, 1, 1, 0) -> (0, 0, 0, 0)
(0, 1, 1, 1) -> (1, 0, 0, 0)
(1, 0, 0, 0) -> (0, 1, 1, 1)
(1, 0, 0, 1) -> (1, 1, 1, 1)
(1, 0, 1, 0) -> (0, 1, 1, 0)
(1, 0, 1, 1) -> (1, 1, 1, 0)
(1, 1, 0, 0) -> (0, 0, 1, 1)
(1, 1, 0, 1) -> (1, 0, 1, 1)
(1, 1, 1, 0) -> (0, 0, 1, 0)
(1, 1, 1, 1) -> (1, 0, 1, 0)
Is the rule axis-separable? If yes, answer 'yes' followed by a space, then the recovered permutation as the list of source coordinate indices read in target-coordinate order (e.g. for 4 coordinates 'yes 1 0 2'). If no, answer exactly 'no'.
```

**Answer**: `yes 3 1 0 2`

### Example

**Prompt**

```
A transition rule maps each state of a product system to a next state. There are 4 coordinates, each taking values 0..1. The rule is axis-separable if there is a permutation of the coordinates (a bijection from source coordinates to target coordinates) such that each target coordinate's next value depends only on the current value of the one matching source coordinate. The full transition table is:
(0, 0, 0, 0) -> (0, 1, 1, 1)
(0, 0, 0, 1) -> (0, 0, 1, 1)
(0, 0, 1, 0) -> (0, 1, 1, 0)
(0, 0, 1, 1) -> (0, 0, 1, 0)
(0, 1, 0, 0) -> (0, 1, 0, 1)
(0, 1, 0, 1) -> (0, 0, 0, 1)
(0, 1, 1, 0) -> (0, 1, 0, 0)
(0, 1, 1, 1) -> (0, 0, 0, 0)
(1, 0, 0, 0) -> (1, 1, 1, 1)
(1, 0, 0, 1) -> (1, 0, 1, 1)
(1, 0, 1, 0) -> (1, 1, 1, 0)
(1, 0, 1, 1) -> (1, 0, 1, 0)
(1, 1, 0, 0) -> (1, 1, 0, 1)
(1, 1, 0, 1) -> (1, 0, 0, 1)
(1, 1, 1, 0) -> (1, 1, 0, 0)
(1, 1, 1, 1) -> (1, 0, 0, 0)
Is the rule axis-separable? If yes, answer 'yes' followed by a space, then the recovered permutation as the list of source coordinate indices read in target-coordinate order (e.g. for 4 coordinates 'yes 1 0 2'). If no, answer exactly 'no'.
```

**Answer**: `yes 0 3 1 2`


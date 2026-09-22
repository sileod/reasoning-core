## Level 0

### Prompt

This program defines nested generators connected by `yield from`. Executing it creates a generator `it` over a shared mutable list frame `st`.
```python
def g0(st, k):
    for i in range(k):
        r = yield st[0]
        st[0] = st[0] + (r if r is not None else 2)
    yield 11

def g1(st, k):
    yield 33
    yield from g0(st, k)
    yield 330
it = g1([5], 2)
```
The value received by the driver is the value each resumed generator yields. The driver's one-by-one resume sequence is: next, send -1, send 0.
`next` resumes a suspended generator and delivers the next yielded value; `send v` resumes it delivering `v` as the value of the current `yield` and returns the following yielded value; `close` closes the generator (and anything it delegates to) and the drive stops there. Completed loop turns are never replayed on re-entry.
The answer is the list of values the driver receives, in order, as a Python list of ints.

### Answer

[33, 5, 5]

### Prompt

This program defines nested generators connected by `yield from`. Executing it creates a generator `it` over a shared mutable list frame `st`.
```python
def g0(st, k):
    for i in range(k):
        r = yield st[0]
        st[0] = st[0] + (r if r is not None else 2)
    yield 11

def g1(st, k):
    yield 44
    yield from g0(st, k)
    yield 440
it = g1([2], 2)
```
The value received by the driver is the value each resumed generator yields. The driver's one-by-one resume sequence is: next, send 0, close.
`next` resumes a suspended generator and delivers the next yielded value; `send v` resumes it delivering `v` as the value of the current `yield` and returns the following yielded value; `close` closes the generator (and anything it delegates to) and the drive stops there. Completed loop turns are never replayed on re-entry.
The answer is the list of values the driver receives, in order, as a Python list of ints.

### Answer

[44, 2]

## Level 2

### Prompt

This program defines nested generators connected by `yield from`. Executing it creates a generator `it` over a shared mutable list frame `st`.
```python
def g0(st, k):
    for i in range(k):
        r = yield st[0]
        st[0] = st[0] + (r if r is not None else 3)
    yield 33

def g1(st, k):
    yield 66
    yield from g0(st, k)
    yield 660

def g2(st, k):
    yield 44
    yield from g1(st, k)
    yield 440
it = g2([2], 4)
```
The value received by the driver is the value each resumed generator yields. The driver's one-by-one resume sequence is: next, send 3, send -2, close.
`next` resumes a suspended generator and delivers the next yielded value; `send v` resumes it delivering `v` as the value of the current `yield` and returns the following yielded value; `close` closes the generator (and anything it delegates to) and the drive stops there. Completed loop turns are never replayed on re-entry.
The answer is the list of values the driver receives, in order, as a Python list of ints.

### Answer

[44, 66, 2]

### Prompt

This program defines nested generators connected by `yield from`. Executing it creates a generator `it` over a shared mutable list frame `st`.
```python
def g0(st, k):
    for i in range(k):
        r = yield st[0]
        st[0] = st[0] + (r if r is not None else 3)
    yield 33

def g1(st, k):
    yield 44
    yield from g0(st, k)
    yield 440

def g2(st, k):
    yield 55
    yield from g1(st, k)
    yield 550
it = g2([1], 4)
```
The value received by the driver is the value each resumed generator yields. The driver's one-by-one resume sequence is: next, send 1, send -2, send 2, send 0.
`next` resumes a suspended generator and delivers the next yielded value; `send v` resumes it delivering `v` as the value of the current `yield` and returns the following yielded value; `close` closes the generator (and anything it delegates to) and the drive stops there. Completed loop turns are never replayed on re-entry.
The answer is the list of values the driver receives, in order, as a Python list of ints.

### Answer

[55, 44, 1, 3, 3]

## Level 5

### Prompt

This program defines nested generators connected by `yield from`. Executing it creates a generator `it` over a shared mutable list frame `st`.
```python
def g0(st, k):
    for i in range(k):
        r = yield st[0]
        st[0] = st[0] + (r if r is not None else 4)
    yield 33

def g1(st, k):
    yield 55
    yield from g0(st, k)
    yield 550

def g2(st, k):
    yield 11
    yield from g1(st, k)
    yield 110

def g3(st, k):
    yield 66
    yield from g2(st, k)
    yield 660
it = g3([3], 7)
```
The value received by the driver is the value each resumed generator yields. The driver's one-by-one resume sequence is: next, send 4, send -3, send 1, send -1, send 1, close.
`next` resumes a suspended generator and delivers the next yielded value; `send v` resumes it delivering `v` as the value of the current `yield` and returns the following yielded value; `close` closes the generator (and anything it delegates to) and the drive stops there. Completed loop turns are never replayed on re-entry.
The answer is the list of values the driver receives, in order, as a Python list of ints.

### Answer

[66, 11, 55, 3, 2, 3]

### Prompt

This program defines nested generators connected by `yield from`. Executing it creates a generator `it` over a shared mutable list frame `st`.
```python
def g0(st, k):
    for i in range(k):
        r = yield st[0]
        st[0] = st[0] + (r if r is not None else 4)
    yield 33

def g1(st, k):
    yield 11
    yield from g0(st, k)
    yield 110

def g2(st, k):
    yield 44
    yield from g1(st, k)
    yield 440

def g3(st, k):
    yield 55
    yield from g2(st, k)
    yield 550
it = g3([3], 7)
```
The value received by the driver is the value each resumed generator yields. The driver's one-by-one resume sequence is: next, send 0, send 0, close.
`next` resumes a suspended generator and delivers the next yielded value; `send v` resumes it delivering `v` as the value of the current `yield` and returns the following yielded value; `close` closes the generator (and anything it delegates to) and the drive stops there. Completed loop turns are never replayed on re-entry.
The answer is the list of values the driver receives, in order, as a Python list of ints.

### Answer

[55, 44, 11]

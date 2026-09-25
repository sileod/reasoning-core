# Samples for online_nondeterminism_resolution (P006v1)

## Level 0

### Example 1

**Prompt:**

```
An automaton with states 0..4 (initial state 1) over binary alphabet {a,b} has safety acceptance. To resolve the nondeterminism online while preserving the accepted language, the standard powerset construction runs a deterministic simulation that, after each input symbol, tracks the set of all states reachable from the prefix read so far; this construction preserves the exact accepted language. The allowable memory class is {c*5 | c = 1..2}, i.e. up to 10 distinct tracked state-sets.
From state 0: on a to {0,4}, on b to {2}.
From state 1: on a to {2}, on b to {1,4}.
From state 2: on a to {3}, on b to {1,3}.
From state 3: on a to {1,3}, on b to {0}.
From state 4: on a to {0,2}, on b to {2}.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
```

**Answer:**

`no`

### Example 2

**Prompt:**

```
An automaton with states 0..4 (initial state 0) over binary alphabet {a,b} has buchi acceptance. To resolve the nondeterminism online while preserving the accepted language, the standard powerset construction runs a deterministic simulation that, after each input symbol, tracks the set of all states reachable from the prefix read so far; this construction preserves the exact accepted language. The allowable memory class is {c*5 | c = 1..2}, i.e. up to 10 distinct tracked state-sets.
From state 0: on a to {1}, on b to {3,4}.
From state 1: on a to {3}, on b to {0,1}.
From state 2: on a to {0}, on b to {0,2}.
From state 3: on a to {3}, on b to {4}.
From state 4: on a to {0}, on b to {2}.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
```

**Answer:**

`no`

## Level 2

### Example 1

**Prompt:**

```
An automaton with states 0..6 (initial state 2) over binary alphabet {a,b} has buchi acceptance. To resolve the nondeterminism online while preserving the accepted language, the standard powerset construction runs a deterministic simulation that, after each input symbol, tracks the set of all states reachable from the prefix read so far; this construction preserves the exact accepted language. The allowable memory class is {c*7 | c = 1..3}, i.e. up to 21 distinct tracked state-sets.
From state 0: on a to {3}, on b to {0,3}.
From state 1: on a to {0}, on b to {3,6}.
From state 2: on a to {5,6}, on b to {2,3}.
From state 3: on a to {1,4}, on b to {4}.
From state 4: on a to {5}, on b to {1}.
From state 5: on a to {3}, on b to {1}.
From state 6: on a to {0,5}, on b to {4,6}.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
```

**Answer:**

`no`

### Example 2

**Prompt:**

```
An automaton with states 0..6 (initial state 5) over binary alphabet {a,b} has buchi acceptance. To resolve the nondeterminism online while preserving the accepted language, the standard powerset construction runs a deterministic simulation that, after each input symbol, tracks the set of all states reachable from the prefix read so far; this construction preserves the exact accepted language. The allowable memory class is {c*7 | c = 1..3}, i.e. up to 21 distinct tracked state-sets.
From state 0: on a to {0,1}, on b to {1,4}.
From state 1: on a to {0}, on b to {3,6}.
From state 2: on a to {2,6}, on b to {2,5}.
From state 3: on a to {3,5}, on b to {3}.
From state 4: on a to {0,3}, on b to {6}.
From state 5: on a to {0,2}, on b to {0,2}.
From state 6: on a to {2}, on b to {2,3}.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
```

**Answer:**

`yes`

## Level 5

### Example 1

**Prompt:**

```
An automaton with states 0..9 (initial state 1) over binary alphabet {a,b} has safety acceptance. To resolve the nondeterminism online while preserving the accepted language, the standard powerset construction runs a deterministic simulation that, after each input symbol, tracks the set of all states reachable from the prefix read so far; this construction preserves the exact accepted language. The allowable memory class is {c*10 | c = 1..4}, i.e. up to 40 distinct tracked state-sets.
From state 0: on a to {2,9}, on b to {3,7}.
From state 1: on a to {3,6}, on b to {6,7}.
From state 2: on a to {4,8}, on b to {0,5}.
From state 3: on a to {9}, on b to {4}.
From state 4: on a to {7}, on b to {4,7}.
From state 5: on a to {1}, on b to {0,5}.
From state 6: on a to {1,3}, on b to {4}.
From state 7: on a to {2}, on b to {1,3}.
From state 8: on a to {1,3}, on b to {0}.
From state 9: on a to {9}, on b to {9}.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
```

**Answer:**

`no`

### Example 2

**Prompt:**

```
An automaton with states 0..9 (initial state 8) over binary alphabet {a,b} has buchi acceptance. To resolve the nondeterminism online while preserving the accepted language, the standard powerset construction runs a deterministic simulation that, after each input symbol, tracks the set of all states reachable from the prefix read so far; this construction preserves the exact accepted language. The allowable memory class is {c*10 | c = 1..4}, i.e. up to 40 distinct tracked state-sets.
From state 0: on a to {2,7}, on b to {2,8}.
From state 1: on a to {4}, on b to {1,9}.
From state 2: on a to {1,3}, on b to {3,7}.
From state 3: on a to {6,9}, on b to {6,7}.
From state 4: on a to {5,7}, on b to {0,3}.
From state 5: on a to {3,6}, on b to {7}.
From state 6: on a to {4}, on b to {3,8}.
From state 7: on a to {4,6}, on b to {1,4}.
From state 8: on a to {0}, on b to {4,7}.
From state 9: on a to {0}, on b to {1,6}.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
Question: does some bound within this memory class suffice to resolve the nondeterminism (track all reachable state-sets) and preserve the accepted language? Answer only 'yes' or 'no'.
```

**Answer:**

`no`

## Level 0

**Example 1**

Prompt:
```
This is a root-controlled vowel harmony system.
Features per vowel appear in the order backness, round, ATR.
Trigger root vowel: <1-1-1>
Suffix 1: underlying <1-0-0> U-U-U
Suffix 2: underlying <1-1-1> U-B-N
In a root-controlled system a root feature spreads rightward through undergoers; an 'N' suffix is transparent (shows its own value, passes the spread), a 'B' suffix is an opaque blocker that stops the spread (shown as X) and any later undergoer then reverts to its own value, making the word disharmonious. In a dominant-recessive system 'B' is a dominant suffix: it re-sets the feature for all following suffixes; there is no X and the word is always harmonic.
Give the surface melody: one fixed-length vector per suffix in order backness-round-ATR (0/1/X), suffixes joined by ' | ', e.g. '1-0-X | 0-1-1'. If any suffix reverts making the word disharmonious, answer exactly 'disharmony'.
```

Answer:
```
1-1-1 | 1-X-1
```

**Example 2**

Prompt:
```
This is a root-controlled vowel harmony system.
Features per vowel appear in the order backness, round, ATR.
Trigger root vowel: <1-0-0>
Suffix 1: underlying <1-0-1> U-N-B
Suffix 2: underlying <1-0-0> U-B-B
In a root-controlled system a root feature spreads rightward through undergoers; an 'N' suffix is transparent (shows its own value, passes the spread), a 'B' suffix is an opaque blocker that stops the spread (shown as X) and any later undergoer then reverts to its own value, making the word disharmonious. In a dominant-recessive system 'B' is a dominant suffix: it re-sets the feature for all following suffixes; there is no X and the word is always harmonic.
Give the surface melody: one fixed-length vector per suffix in order backness-round-ATR (0/1/X), suffixes joined by ' | ', e.g. '1-0-X | 0-1-1'. If any suffix reverts making the word disharmonious, answer exactly 'disharmony'.
```

Answer:
```
disharmony
```

## Level 2

**Example 1**

Prompt:
```
This is a dominant-controlled vowel harmony system.
Features per vowel appear in the order backness, round, ATR.
Trigger root vowel: <0-1-1>
Suffix 1: underlying <0-1-1> U-U-B
Suffix 2: underlying <0-0-1> B-B-U
Suffix 3: underlying <1-0-0> U-B-B
Suffix 4: underlying <1-1-1> B-U-B
In a root-controlled system a root feature spreads rightward through undergoers; an 'N' suffix is transparent (shows its own value, passes the spread), a 'B' suffix is an opaque blocker that stops the spread (shown as X) and any later undergoer then reverts to its own value, making the word disharmonious. In a dominant-recessive system 'B' is a dominant suffix: it re-sets the feature for all following suffixes; there is no X and the word is always harmonic.
Give the surface melody: one fixed-length vector per suffix in order backness-round-ATR (0/1/X), suffixes joined by ' | ', e.g. '1-0-X | 0-1-1'. If any suffix reverts making the word disharmonious, answer exactly 'disharmony'.
```

Answer:
```
0-1-1 | 0-0-1 | 0-0-0 | 1-0-1
```

**Example 2**

Prompt:
```
This is a dominant-controlled vowel harmony system.
Features per vowel appear in the order backness, round, ATR.
Trigger root vowel: <0-0-0>
Suffix 1: underlying <0-1-1> B-U-B
Suffix 2: underlying <1-0-0> U-U-B
Suffix 3: underlying <1-0-1> B-U-B
Suffix 4: underlying <0-1-0> U-B-U
In a root-controlled system a root feature spreads rightward through undergoers; an 'N' suffix is transparent (shows its own value, passes the spread), a 'B' suffix is an opaque blocker that stops the spread (shown as X) and any later undergoer then reverts to its own value, making the word disharmonious. In a dominant-recessive system 'B' is a dominant suffix: it re-sets the feature for all following suffixes; there is no X and the word is always harmonic.
Give the surface melody: one fixed-length vector per suffix in order backness-round-ATR (0/1/X), suffixes joined by ' | ', e.g. '1-0-X | 0-1-1'. If any suffix reverts making the word disharmonious, answer exactly 'disharmony'.
```

Answer:
```
0-0-1 | 0-0-0 | 1-0-1 | 1-1-1
```

## Level 5

**Example 1**

Prompt:
```
This is a dominant-controlled vowel harmony system.
Features per vowel appear in the order backness, round, ATR.
Trigger root vowel: <1-1-1>
Suffix 1: underlying <1-1-0> B-U-B
Suffix 2: underlying <1-1-0> U-U-U
Suffix 3: underlying <0-0-1> B-U-B
Suffix 4: underlying <1-0-0> U-U-B
Suffix 5: underlying <1-1-0> U-B-U
Suffix 6: underlying <1-1-0> B-U-U
Suffix 7: underlying <0-1-0> U-B-U
In a root-controlled system a root feature spreads rightward through undergoers; an 'N' suffix is transparent (shows its own value, passes the spread), a 'B' suffix is an opaque blocker that stops the spread (shown as X) and any later undergoer then reverts to its own value, making the word disharmonious. In a dominant-recessive system 'B' is a dominant suffix: it re-sets the feature for all following suffixes; there is no X and the word is always harmonic.
Give the surface melody: one fixed-length vector per suffix in order backness-round-ATR (0/1/X), suffixes joined by ' | ', e.g. '1-0-X | 0-1-1'. If any suffix reverts making the word disharmonious, answer exactly 'disharmony'.
```

Answer:
```
1-1-0 | 1-1-0 | 0-1-1 | 0-1-0 | 0-1-0 | 1-1-0 | 1-1-0
```

**Example 2**

Prompt:
```
This is a root-controlled vowel harmony system.
Features per vowel appear in the order backness, round, ATR.
Trigger root vowel: <1-1-1>
Suffix 1: underlying <0-1-1> U-U-U
Suffix 2: underlying <1-0-1> U-U-U
Suffix 3: underlying <1-0-0> B-B-B
Suffix 4: underlying <0-1-1> U-U-B
Suffix 5: underlying <0-1-1> N-U-U
Suffix 6: underlying <0-1-1> N-U-U
Suffix 7: underlying <0-0-1> U-U-U
In a root-controlled system a root feature spreads rightward through undergoers; an 'N' suffix is transparent (shows its own value, passes the spread), a 'B' suffix is an opaque blocker that stops the spread (shown as X) and any later undergoer then reverts to its own value, making the word disharmonious. In a dominant-recessive system 'B' is a dominant suffix: it re-sets the feature for all following suffixes; there is no X and the word is always harmonic.
Give the surface melody: one fixed-length vector per suffix in order backness-round-ATR (0/1/X), suffixes joined by ' | ', e.g. '1-0-X | 0-1-1'. If any suffix reverts making the word disharmonious, answer exactly 'disharmony'.
```

Answer:
```
disharmony
```


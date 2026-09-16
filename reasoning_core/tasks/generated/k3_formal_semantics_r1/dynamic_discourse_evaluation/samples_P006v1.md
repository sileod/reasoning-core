## Level 0

**Example 1**

Prompt:
```
Text:
The characters are numbered:
1: a bright knight
2: a bright knight
3: a dim knight
4: a bright knight
5: a dim maid
6: a bright dragon
Sentences:
1. A knight enters the hall.
2. The knight is bright.
Question: which characters can the anaphor referring to a knight from sentence 1 pick out?
Give the character numbers, from smallest to largest, as a comma-separated list. If it cannot refer to any character, write the single word 'none'.
```

Answer:
```
1,2,4
```

**Example 2**

Prompt:
```
Text:
The characters are numbered:
1: a bright knight
2: a dim knight
3: a bright knight
4: a bright knight
5: a dim maid
6: a dim maid
Sentences:
1. A knight enters the hall.
2. The knight is bright.
Question: which characters can the anaphor referring to a knight from sentence 1 pick out?
Give the character numbers, from smallest to largest, as a comma-separated list. If it cannot refer to any character, write the single word 'none'.
```

Answer:
```
1,3,4
```

## Level 2

**Example 1**

Prompt:
```
Text:
The characters are numbered:
1: a dim knight
2: a bright knight
3: a dim knight
4: a bright knight
5: a bright knight
6: a dim knight
7: a bright page
8: a dim scribe
Sentences:
1. A knight enters the hall.
2. The knight is dim.
Question: which characters can the anaphor referring to a knight from sentence 1 pick out?
Give the character numbers, from smallest to largest, as a comma-separated list. If it cannot refer to any character, write the single word 'none'.
```

Answer:
```
1,3,6
```

**Example 2**

Prompt:
```
Text:
The characters are numbered:
1: a bright maid
2: a bright maid
3: a dim maid
4: a bright maid
5: a bright maid
6: a bright maid
7: a dim dragon
8: a bright dragon
Sentences:
1. A maid enters the hall.
2. The maid is bright.
Question: which characters can the anaphor referring to a maid from sentence 1 pick out?
Give the character numbers, from smallest to largest, as a comma-separated list. If it cannot refer to any character, write the single word 'none'.
```

Answer:
```
1,2,4,5,6
```

## Level 5

**Example 1**

Prompt:
```
Text:
The characters are numbered:
1: a bright scribe
2: a dim scribe
3: a dim scribe
4: a dim scribe
5: a bright scribe
6: a dim scribe
7: a dim scribe
8: a dim scribe
9: a dim scribe
10: a dim dragon
11: a bright page
Sentences:
1. If a scribe enters the hall, the scribe is bright.
2. A maid enters the hall.
3. A dragon enters the hall.
4. A page enters the hall.
Question: which characters can the anaphor referring to a scribe from sentence 1 pick out?
Give the character numbers, from smallest to largest, as a comma-separated list. If it cannot refer to any character, write the single word 'none'.
```

Answer:
```
none
```

**Example 2**

Prompt:
```
Text:
The characters are numbered:
1: a dim maid
2: a bright maid
3: a bright maid
4: a dim maid
5: a dim maid
6: a bright maid
7: a bright maid
8: a dim maid
9: a dim maid
10: a bright scribe
11: a dim dragon
Sentences:
1. A maid enters the hall.
2. The maid is dim.
Question: which characters can the anaphor referring to a maid from sentence 1 pick out?
Give the character numbers, from smallest to largest, as a comma-separated list. If it cannot refer to any character, write the single word 'none'.
```

Answer:
```
1,4,5,8,9
```

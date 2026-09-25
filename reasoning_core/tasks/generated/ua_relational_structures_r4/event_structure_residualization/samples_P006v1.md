# Event Structure Residualization — samples

# Level 0

**Prompt:**
```
An event structure over events {1, 2, 3, 4} has causality edges (a -> b means event a must complete before event b can) and conflict edges (a # b means events a and b cannot both complete).
Causality: 1 -> 2, 1 -> 3, 1 -> 4, 2 -> 4
Conflict: 1 # 4, 2 # 4
Configuration completed: {1, 2, 3}
After this configuration, which events remain enabled? An event that has not completed remains enabled when it conflicts with no completed event and every event that must complete before it has already completed.
Answer with the sorted list of enabled event IDs, e.g. [3, 5]; [] if none.
```

**Answer:**
```
[]
```

**Prompt:**
```
An event structure over events {1, 2, 3, 4} has causality edges (a -> b means event a must complete before event b can) and conflict edges (a # b means events a and b cannot both complete).
Causality: 1 -> 2, 1 -> 4, 2 -> 3, 2 -> 4
Conflict: 1 # 4, 3 # 4
Configuration completed: {1, 2, 3}
After this configuration, which events remain enabled? An event that has not completed remains enabled when it conflicts with no completed event and every event that must complete before it has already completed.
Answer with the sorted list of enabled event IDs, e.g. [3, 5]; [] if none.
```

**Answer:**
```
[]
```

# Level 2

**Prompt:**
```
An event structure over events {1, 2, 3, 4, 5, 6, 7, 8} has causality edges (a -> b means event a must complete before event b can) and conflict edges (a # b means events a and b cannot both complete).
Causality: 1 -> 2, 1 -> 3, 1 -> 4, 1 -> 5, 2 -> 3, 2 -> 4, 2 -> 6, 2 -> 7, 2 -> 8, 3 -> 6, 6 -> 8
Conflict: 1 # 7, 3 # 7, 4 # 7, 4 # 8
Configuration completed: {1, 2, 3, 5, 6, 8}
After this configuration, which events remain enabled? An event that has not completed remains enabled when it conflicts with no completed event and every event that must complete before it has already completed.
Answer with the sorted list of enabled event IDs, e.g. [3, 5]; [] if none.
```

**Answer:**
```
[]
```

**Prompt:**
```
An event structure over events {1, 2, 3, 4, 5, 6, 7, 8} has causality edges (a -> b means event a must complete before event b can) and conflict edges (a # b means events a and b cannot both complete).
Causality: 1 -> 2, 1 -> 6, 2 -> 3, 2 -> 5, 3 -> 4, 4 -> 6, 4 -> 7, 5 -> 8, 6 -> 7, 6 -> 8
Conflict: 2 # 5, 5 # 6, 5 # 8, 7 # 8
Configuration completed: {1, 2, 3, 4, 6, 7}
After this configuration, which events remain enabled? An event that has not completed remains enabled when it conflicts with no completed event and every event that must complete before it has already completed.
Answer with the sorted list of enabled event IDs, e.g. [3, 5]; [] if none.
```

**Answer:**
```
[]
```

# Level 5

**Prompt:**
```
An event structure over events {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14} has causality edges (a -> b means event a must complete before event b can) and conflict edges (a # b means events a and b cannot both complete).
Causality: 1 -> 2, 1 -> 5, 2 -> 3, 2 -> 4, 2 -> 8, 2 -> 14, 3 -> 4, 3 -> 6, 3 -> 10, 4 -> 7, 4 -> 9, 5 -> 11, 5 -> 14, 6 -> 7, 6 -> 8, 7 -> 11, 9 -> 12, 11 -> 13
Conflict: 1 # 14, 4 # 12, 5 # 12, 8 # 12, 10 # 12, 11 # 12, 12 # 13
Configuration completed: {1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13}
After this configuration, which events remain enabled? An event that has not completed remains enabled when it conflicts with no completed event and every event that must complete before it has already completed.
Answer with the sorted list of enabled event IDs, e.g. [3, 5]; [] if none.
```

**Answer:**
```
[9]
```

**Prompt:**
```
An event structure over events {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14} has causality edges (a -> b means event a must complete before event b can) and conflict edges (a # b means events a and b cannot both complete).
Causality: 1 -> 2, 1 -> 3, 1 -> 4, 1 -> 5, 1 -> 9, 2 -> 3, 2 -> 14, 3 -> 4, 3 -> 7, 3 -> 8, 3 -> 10, 5 -> 6, 5 -> 9, 5 -> 10, 5 -> 12, 6 -> 7, 7 -> 11, 7 -> 13, 12 -> 13
Conflict: 1 # 14, 2 # 14, 4 # 8, 4 # 9, 4 # 13, 5 # 14, 10 # 14
Configuration completed: {1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13}
After this configuration, which events remain enabled? An event that has not completed remains enabled when it conflicts with no completed event and every event that must complete before it has already completed.
Answer with the sorted list of enabled event IDs, e.g. [3, 5]; [] if none.
```

**Answer:**
```
[]
```

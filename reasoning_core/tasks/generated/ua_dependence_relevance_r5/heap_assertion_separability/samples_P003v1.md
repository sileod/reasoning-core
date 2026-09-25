## Level 0
### Prompt
Consider a heap over cell universe {0, 1}. The current heap diagram allocates exactly the cells {1}. Decide whether the following spatial assertion holds over this heap. The assertion is: (cell 0 is owned) -** (cell 1 is owned). Semantics: emp holds only on the empty heap; 'cell k is owned' holds only when the heap is exactly {k}; P * Q holds when the heap splits into two disjoint parts respectively satisfying P and Q; P -** Q holds when adding any disjoint subheap satisfying P forces the result to satisfy Q. Answer with a single word, indicating your decision.

Answer:
false

### Prompt
Consider a heap over cell universe {0, 1}. The current heap diagram allocates exactly the cells {0, 1}. Decide whether the following spatial assertion holds over this heap. The assertion is: (cell 0 is owned) and (emp). Semantics: emp holds only on the empty heap; 'cell k is owned' holds only when the heap is exactly {k}; P * Q holds when the heap splits into two disjoint parts respectively satisfying P and Q; P -** Q holds when adding any disjoint subheap satisfying P forces the result to satisfy Q. Answer with a single word, indicating your decision.

Answer:
false

## Level 2
### Prompt
Consider a heap over cell universe {0, 1, 2, 3}. The current heap diagram allocates exactly the cells {0, 1, 2, 3}. Decide whether the following spatial assertion holds over this heap. The assertion is: (((emp) and (cell 1 is owned)) or ((cell 0 is owned) or (emp))) -** (((emp) and (cell 0 is owned)) -** ((emp) * (emp))). Semantics: emp holds only on the empty heap; 'cell k is owned' holds only when the heap is exactly {k}; P * Q holds when the heap splits into two disjoint parts respectively satisfying P and Q; P -** Q holds when adding any disjoint subheap satisfying P forces the result to satisfy Q. Answer with a single word, indicating your decision.

Answer:
true

### Prompt
Consider a heap over cell universe {0, 1, 2, 3}. The current heap diagram allocates exactly the cells {0, 1, 2, 3}. Decide whether the following spatial assertion holds over this heap. The assertion is: (((cell 3 is owned) and (cell 0 is owned)) or ((cell 1 is owned) * (cell 1 is owned))) or (((cell 2 is owned) and (emp)) -** ((cell 1 is owned) * (emp))). Semantics: emp holds only on the empty heap; 'cell k is owned' holds only when the heap is exactly {k}; P * Q holds when the heap splits into two disjoint parts respectively satisfying P and Q; P -** Q holds when adding any disjoint subheap satisfying P forces the result to satisfy Q. Answer with a single word, indicating your decision.

Answer:
true

## Level 5
### Prompt
Consider a heap over cell universe {0, 1, 2, 3, 4, 5, 6}. The current heap diagram allocates exactly the cells {2, 3, 4, 5, 6}. Decide whether the following spatial assertion holds over this heap. The assertion is: ((cell 5 is owned) and (emp)) * ((cell 6 is owned) -** (emp)). Semantics: emp holds only on the empty heap; 'cell k is owned' holds only when the heap is exactly {k}; P * Q holds when the heap splits into two disjoint parts respectively satisfying P and Q; P -** Q holds when adding any disjoint subheap satisfying P forces the result to satisfy Q. Answer with a single word, indicating your decision.

Answer:
false

### Prompt
Consider a heap over cell universe {0, 1, 2, 3, 4, 5, 6}. The current heap diagram allocates exactly the cells {0, 1, 2, 4, 5, 6}. Decide whether the following spatial assertion holds over this heap. The assertion is: (((cell 2 is owned) * (emp)) -** ((cell 6 is owned) * (cell 1 is owned))) * (((emp) -** (emp)) * ((emp) -** (emp))). Semantics: emp holds only on the empty heap; 'cell k is owned' holds only when the heap is exactly {k}; P * Q holds when the heap splits into two disjoint parts respectively satisfying P and Q; P -** Q holds when adding any disjoint subheap satisfying P forces the result to satisfy Q. Answer with a single word, indicating your decision.

Answer:
true

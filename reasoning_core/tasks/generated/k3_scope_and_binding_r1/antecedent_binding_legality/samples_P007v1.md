# samples_P007v1 - antecedent_binding_legality

## Level 0

### Example 1

**Prompt:**

Using the classic binding conditions (Principle A for anaphors, Principle B for pronouns, Principle C for names), decide whether coindexing the target expression with each candidate antecedent gives a grammatical (licensed) or ungrammatical (blocked) reading.

Sentence: Rosa thanked about Tess her
Tree: [S Rosa [VP thanked [PP about Tess] her]]

Target expression (T): her
Candidate antecedents:
  (1) Rosa
  (2) Tess
Answer with one word per candidate 'licensed' or 'blocked' in the order listed above, separated by commas and nothing else, for example: 'licensed, blocked'.

**Answer:**

`blocked, licensed`

### Example 2

**Prompt:**

Using the classic binding conditions (Principle A for anaphors, Principle B for pronouns, Principle C for names), decide whether coindexing the target expression with each candidate antecedent gives a grammatical (licensed) or ungrammatical (blocked) reading.

Sentence: Ana ignored to Eli Tess
Tree: [S Ana [VP ignored [PP to Eli] Tess]]

Target expression (T): Tess
Candidate antecedents:
  (1) Ana
  (2) Eli
Answer with one word per candidate 'licensed' or 'blocked' in the order listed above, separated by commas and nothing else, for example: 'licensed, blocked'.

**Answer:**

`blocked, licensed`

## Level 2

### Example 1

**Prompt:**

Using the classic binding conditions (Principle A for anaphors, Principle B for pronouns, Principle C for names), decide whether coindexing the target expression with each candidate antecedent gives a grammatical (licensed) or ungrammatical (blocked) reading.

Sentence: Ira expects Lia invited for Rosa him
Tree: [S Ira [VP expects [S Lia [VP invited [PP for Rosa] him]]]]

Target expression (T): him
Candidate antecedents:
  (1) Ira
  (2) Lia
  (3) Rosa
Answer with one word per candidate 'licensed' or 'blocked' in the order listed above, separated by commas and nothing else, for example: 'licensed, blocked'.

**Answer:**

`licensed, blocked, licensed`

### Example 2

**Prompt:**

Using the classic binding conditions (Principle A for anaphors, Principle B for pronouns, Principle C for names), decide whether coindexing the target expression with each candidate antecedent gives a grammatical (licensed) or ungrammatical (blocked) reading.

Sentence: Ken imagined Ira admired from Quinn Gil
Tree: [S Ken [VP imagined [S Ira [VP admired [PP from Quinn] Gil]]]]

Target expression (T): Gil
Candidate antecedents:
  (1) Ken
  (2) Ira
  (3) Quinn
Answer with one word per candidate 'licensed' or 'blocked' in the order listed above, separated by commas and nothing else, for example: 'licensed, blocked'.

**Answer:**

`blocked, blocked, licensed`

## Level 5

### Example 1

**Prompt:**

Using the classic binding conditions (Principle A for anaphors, Principle B for pronouns, Principle C for names), decide whether coindexing the target expression with each candidate antecedent gives a grammatical (licensed) or ungrammatical (blocked) reading.

Sentence: Quinn believes Max claimed Sam supposed Nora called near Lia about Ken her
Tree: [S Quinn [VP believes [S Max [VP claimed [S Sam [VP supposed [S Nora [VP called [PP near Lia] [PP about Ken] her]]]]]]]]

Target expression (T): her
Candidate antecedents:
  (1) Quinn
  (2) Max
  (3) Sam
  (4) Nora
  (5) Lia
  (6) Ken
Answer with one word per candidate 'licensed' or 'blocked' in the order listed above, separated by commas and nothing else, for example: 'licensed, blocked'.

**Answer:**

`licensed, licensed, licensed, blocked, licensed, licensed`

### Example 2

**Prompt:**

Using the classic binding conditions (Principle A for anaphors, Principle B for pronouns, Principle C for names), decide whether coindexing the target expression with each candidate antecedent gives a grammatical (licensed) or ungrammatical (blocked) reading.

Sentence: Eli imagined Nora expects Ira suspects Jill praised about Sam from Ken each other
Tree: [S Eli [VP imagined [S Nora [VP expects [S Ira [VP suspects [S Jill [VP praised [PP about Sam] [PP from Ken] each other]]]]]]]]

Target expression (T): each other
Candidate antecedents:
  (1) Eli
  (2) Nora
  (3) Ira
  (4) Jill
  (5) Sam
  (6) Ken
Answer with one word per candidate 'licensed' or 'blocked' in the order listed above, separated by commas and nothing else, for example: 'licensed, blocked'.

**Answer:**

`blocked, blocked, blocked, licensed, blocked, blocked`

# Samples for conventional_implicature_separation (P010v2)

## Level 0

### Example 1

**Prompt**

In projective-content semantics, the main clause is at-issue (its content is asserted), while content supplied by an appositive, an expressive, or a parenthetical is a conventional implicature that projects: it survives when the sentence is negated, put in a conditional, or embedded under an attitude verb. Belief and desire verbs leave their complement asserted; factive verbs (know, realize, regret) project their complement.
Sentence: Mary, that wretched scoundrel, should resign.
Content contributions with their sources: (1) expressive: Mary is a wretched scoundrel. The main contribution is (asserted): Mary should resign.
Now embed this sentence under negation, a conditional, and the attitude 'Mary know that ...' (know is factive, so its complement projects).
For each of 'negation', 'conditional', and 'attitude', list every content piece as a semicolon-separated string, each prefixed by A (asserted) or P (projective), main first. Format each row as the context, a colon, then 'A: main: <text>; P: <source>: <text>; ...'. Answer with exactly three lines, one per context, in the order negation, conditional, attitude.

**Answer**

negation: A: main: Mary should resign; P: expressive: Mary is a wretched scoundrel
conditional: A: main: Mary should resign; P: expressive: Mary is a wretched scoundrel
attitude: P: main: Mary should resign; P: expressive: Mary is a wretched scoundrel

### Example 2

**Prompt**

In projective-content semantics, the main clause is at-issue (its content is asserted), while content supplied by an appositive, an expressive, or a parenthetical is a conventional implicature that projects: it survives when the sentence is negated, put in a conditional, or embedded under an attitude verb. Belief and desire verbs leave their complement asserted; factive verbs (know, realize, regret) project their complement.
Sentence: Suki, who has never owned a car, attended the meeting.
Content contributions with their sources: (1) appositive: Suki has never owned a car. The main contribution is (asserted): Suki attended the meeting.
Now embed this sentence under negation, a conditional, and the attitude 'Suki believe that ...' (believe is non-factive, so its complement stays asserted).
For each of 'negation', 'conditional', and 'attitude', list every content piece as a semicolon-separated string, each prefixed by A (asserted) or P (projective), main first. Format each row as the context, a colon, then 'A: main: <text>; P: <source>: <text>; ...'. Answer with exactly three lines, one per context, in the order negation, conditional, attitude.

**Answer**

negation: A: main: Suki attended the meeting; P: appositive: Suki has never owned a car
conditional: A: main: Suki attended the meeting; P: appositive: Suki has never owned a car
attitude: A: main: Suki attended the meeting; P: appositive: Suki has never owned a car

## Level 2

### Example 1

**Prompt**

In projective-content semantics, the main clause is at-issue (its content is asserted), while content supplied by an appositive, an expressive, or a parenthetical is a conventional implicature that projects: it survives when the sentence is negated, put in a conditional, or embedded under an attitude verb. Belief and desire verbs leave their complement asserted; factive verbs (know, realize, regret) project their complement.
Sentence: Diego — who keeps meticulous notes —, that two-faced tyrant, attended the meeting.
Content contributions with their sources: (1) parenthetical: Diego keeps meticulous notes (2) expressive: Diego is a two-faced tyrant. The main contribution is (asserted): Diego attended the meeting.
Now embed this sentence under negation, a conditional, and the attitude 'Diego know that ...' (know is factive, so its complement projects).
For each of 'negation', 'conditional', and 'attitude', list every content piece as a semicolon-separated string, each prefixed by A (asserted) or P (projective), main first. Format each row as the context, a colon, then 'A: main: <text>; P: <source>: <text>; ...'. Answer with exactly three lines, one per context, in the order negation, conditional, attitude.

**Answer**

negation: A: main: Diego attended the meeting; P: parenthetical: Diego keeps meticulous notes; P: expressive: Diego is a two-faced tyrant
conditional: A: main: Diego attended the meeting; P: parenthetical: Diego keeps meticulous notes; P: expressive: Diego is a two-faced tyrant
attitude: P: main: Diego attended the meeting; P: parenthetical: Diego keeps meticulous notes; P: expressive: Diego is a two-faced tyrant

### Example 2

**Prompt**

In projective-content semantics, the main clause is at-issue (its content is asserted), while content supplied by an appositive, an expressive, or a parenthetical is a conventional implicature that projects: it survives when the sentence is negated, put in a conditional, or embedded under an attitude verb. Belief and desire verbs leave their complement asserted; factive verbs (know, realize, regret) project their complement.
Sentence: John, who is a brilliant surgeon, — who keeps meticulous notes — paid the rent.
Content contributions with their sources: (1) appositive: John is a brilliant surgeon (2) parenthetical: John keeps meticulous notes. The main contribution is (asserted): John paid the rent.
Now embed this sentence under negation, a conditional, and the attitude 'John believe that ...' (believe is non-factive, so its complement stays asserted).
For each of 'negation', 'conditional', and 'attitude', list every content piece as a semicolon-separated string, each prefixed by A (asserted) or P (projective), main first. Format each row as the context, a colon, then 'A: main: <text>; P: <source>: <text>; ...'. Answer with exactly three lines, one per context, in the order negation, conditional, attitude.

**Answer**

negation: A: main: John paid the rent; P: appositive: John is a brilliant surgeon; P: parenthetical: John keeps meticulous notes
conditional: A: main: John paid the rent; P: appositive: John is a brilliant surgeon; P: parenthetical: John keeps meticulous notes
attitude: A: main: John paid the rent; P: appositive: John is a brilliant surgeon; P: parenthetical: John keeps meticulous notes

## Level 5

### Example 1

**Prompt**

In projective-content semantics, the main clause is at-issue (its content is asserted), while content supplied by an appositive, an expressive, or a parenthetical is a conventional implicature that projects: it survives when the sentence is negated, put in a conditional, or embedded under an attitude verb. Belief and desire verbs leave their complement asserted; factive verbs (know, realize, regret) project their complement.
Sentence: Andre — who is quietly generous —, who is a brilliant surgeon,, that dreadful tyrant, missed the train.
Content contributions with their sources: (1) parenthetical: Andre is quietly generous (2) appositive: Andre is a brilliant surgeon (3) expressive: Andre is a dreadful tyrant. The main contribution is (asserted): Andre missed the train.
Now embed this sentence under negation, a conditional, and the attitude 'Andre regret that ...' (regret is factive, so its complement projects).
For each of 'negation', 'conditional', and 'attitude', list every content piece as a semicolon-separated string, each prefixed by A (asserted) or P (projective), main first. Format each row as the context, a colon, then 'A: main: <text>; P: <source>: <text>; ...'. Answer with exactly three lines, one per context, in the order negation, conditional, attitude.

**Answer**

negation: A: main: Andre missed the train; P: parenthetical: Andre is quietly generous; P: appositive: Andre is a brilliant surgeon; P: expressive: Andre is a dreadful tyrant
conditional: A: main: Andre missed the train; P: parenthetical: Andre is quietly generous; P: appositive: Andre is a brilliant surgeon; P: expressive: Andre is a dreadful tyrant
attitude: P: main: Andre missed the train; P: parenthetical: Andre is quietly generous; P: appositive: Andre is a brilliant surgeon; P: expressive: Andre is a dreadful tyrant

### Example 2

**Prompt**

In projective-content semantics, the main clause is at-issue (its content is asserted), while content supplied by an appositive, an expressive, or a parenthetical is a conventional implicature that projects: it survives when the sentence is negated, put in a conditional, or embedded under an attitude verb. Belief and desire verbs leave their complement asserted; factive verbs (know, realize, regret) project their complement.
Sentence: Mary, that no-good scoundrel, — who is famously punctual —, who is an only child, paid the rent.
Content contributions with their sources: (1) expressive: Mary is a no-good scoundrel (2) parenthetical: Mary is famously punctual (3) appositive: Mary is an only child. The main contribution is (asserted): Mary paid the rent.
Now embed this sentence under negation, a conditional, and the attitude 'Mary regret that ...' (regret is factive, so its complement projects).
For each of 'negation', 'conditional', and 'attitude', list every content piece as a semicolon-separated string, each prefixed by A (asserted) or P (projective), main first. Format each row as the context, a colon, then 'A: main: <text>; P: <source>: <text>; ...'. Answer with exactly three lines, one per context, in the order negation, conditional, attitude.

**Answer**

negation: A: main: Mary paid the rent; P: expressive: Mary is a no-good scoundrel; P: parenthetical: Mary is famously punctual; P: appositive: Mary is an only child
conditional: A: main: Mary paid the rent; P: expressive: Mary is a no-good scoundrel; P: parenthetical: Mary is famously punctual; P: appositive: Mary is an only child
attitude: P: main: Mary paid the rent; P: expressive: Mary is a no-good scoundrel; P: parenthetical: Mary is famously punctual; P: appositive: Mary is an only child

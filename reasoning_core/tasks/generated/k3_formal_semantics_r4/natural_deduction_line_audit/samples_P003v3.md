# Level 0

## Example 1

**Prompt:**

A natural-deduction proof is given, one line per numbered step, each with a rule citation in parentheses. Valid citations are: premise; and-introduction on the two conjunct-lines; and-elimination on the conjunction; implication-elimination on an implication and its antecedent; or-introduction on the disjunct-line; or-elimination on the disjunction and two implication-lines; and 'discharged from N' on a conclusion line whose target formula was derived by line N. A premise is always justified. A line is unjustified when the cited rule does not fit its formula or the cited lines.

1. P5   (premise)
2. P3   (premise)
3. P5 and P3   (and-introduction on 1, 2)
4. P5   (implication-elimination on 3)
5. conclusion: P5   (discharged from 4)

Is every line justified, or is there an unjustified line? If every line is justified, answer VALID. Otherwise give the number of the FIRST line (the smallest number) that has no valid justification.

**Answer:**

4

## Example 2

**Prompt:**

A natural-deduction proof is given, one line per numbered step, each with a rule citation in parentheses. Valid citations are: premise; and-introduction on the two conjunct-lines; and-elimination on the conjunction; implication-elimination on an implication and its antecedent; or-introduction on the disjunct-line; or-elimination on the disjunction and two implication-lines; and 'discharged from N' on a conclusion line whose target formula was derived by line N. A premise is always justified. A line is unjustified when the cited rule does not fit its formula or the cited lines.

1. P5   (premise)
2. P6   (premise)
3. P5 and P6   (and-introduction on 1, 2)
4. P5   (and-elimination on 3)
5. conclusion: P5   (discharged from 4)

Is every line justified, or is there an unjustified line? If every line is justified, answer VALID. Otherwise give the number of the FIRST line (the smallest number) that has no valid justification.

**Answer:**

VALID



# Level 2

## Example 1

**Prompt:**

A natural-deduction proof is given, one line per numbered step, each with a rule citation in parentheses. Valid citations are: premise; and-introduction on the two conjunct-lines; and-elimination on the conjunction; implication-elimination on an implication and its antecedent; or-introduction on the disjunct-line; or-elimination on the disjunction and two implication-lines; and 'discharged from N' on a conclusion line whose target formula was derived by line N. A premise is always justified. A line is unjustified when the cited rule does not fit its formula or the cited lines.

1. P3 implies P2   (premise)
2. P2 implies P5   (premise)
3. P3   (premise)
4. P2   (implication-elimination on 1, 3)
5. P5   (implication-elimination on 2, 4)
6. conclusion: P5   (discharged from 5)

Is every line justified, or is there an unjustified line? If every line is justified, answer VALID. Otherwise give the number of the FIRST line (the smallest number) that has no valid justification.

**Answer:**

VALID

## Example 2

**Prompt:**

A natural-deduction proof is given, one line per numbered step, each with a rule citation in parentheses. Valid citations are: premise; and-introduction on the two conjunct-lines; and-elimination on the conjunction; implication-elimination on an implication and its antecedent; or-introduction on the disjunct-line; or-elimination on the disjunction and two implication-lines; and 'discharged from N' on a conclusion line whose target formula was derived by line N. A premise is always justified. A line is unjustified when the cited rule does not fit its formula or the cited lines.

1. P5   (premise)
2. P4   (premise)
3. P5 and P4   (or-introduction on 1, 3)
4. P5   (and-elimination on 3)
5. conclusion: P5   (discharged from 4)

Is every line justified, or is there an unjustified line? If every line is justified, answer VALID. Otherwise give the number of the FIRST line (the smallest number) that has no valid justification.

**Answer:**

3



# Level 5

## Example 1

**Prompt:**

A natural-deduction proof is given, one line per numbered step, each with a rule citation in parentheses. Valid citations are: premise; and-introduction on the two conjunct-lines; and-elimination on the conjunction; implication-elimination on an implication and its antecedent; or-introduction on the disjunct-line; or-elimination on the disjunction and two implication-lines; and 'discharged from N' on a conclusion line whose target formula was derived by line N. A premise is always justified. A line is unjustified when the cited rule does not fit its formula or the cited lines.

1. P11 implies P5   (premise)
2. P5 implies P2   (premise)
3. P11   (premise)
4. P5   (implication-elimination on 1, 3)
5. P2   (implication-elimination on 2, 4)
6. conclusion: P2   (discharged from 5)

Is every line justified, or is there an unjustified line? If every line is justified, answer VALID. Otherwise give the number of the FIRST line (the smallest number) that has no valid justification.

**Answer:**

VALID

## Example 2

**Prompt:**

A natural-deduction proof is given, one line per numbered step, each with a rule citation in parentheses. Valid citations are: premise; and-introduction on the two conjunct-lines; and-elimination on the conjunction; implication-elimination on an implication and its antecedent; or-introduction on the disjunct-line; or-elimination on the disjunction and two implication-lines; and 'discharged from N' on a conclusion line whose target formula was derived by line N. A premise is always justified. A line is unjustified when the cited rule does not fit its formula or the cited lines.

1. P9 implies P6   (premise)
2. P6 implies P12   (premise)
3. P9   (premise)
4. P6   (implication-elimination on 1, 3)
5. P12   (implication-elimination on 2, 4)
6. conclusion: P12   (discharged from 5)

Is every line justified, or is there an unjustified line? If every line is justified, answer VALID. Otherwise give the number of the FIRST line (the smallest number) that has no valid justification.

**Answer:**

VALID



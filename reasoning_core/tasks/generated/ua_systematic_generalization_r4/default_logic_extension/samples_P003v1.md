## Level 0
**Prompt:**
Consider a default logic theory over propositional atoms a, b, c.
The known facts are c.
The defaults are (index: Prerequisite : Justification : Consequent): 0: ( : not c : not c).
Consider the extension E = c.
A default is applicable in E when E contains its prerequisite, E is consistent with its justification, and E does not already contain its consequent.
In this extension E, is the following default applicable: 0: ( : not c : not c)? Answer Yes or No only.

**Answer:**
No

---

**Prompt:**
Consider a default logic theory over propositional atoms a, b, c.
The known facts are b.
The defaults are (index: Prerequisite : Justification : Consequent): 0: ( : a : a).
Consider the extension E = a, b.
A default is applicable in E when E contains its prerequisite, E is consistent with its justification, and E does not already contain its consequent.
In this extension E, is the following default applicable: 0: ( : a : a)? Answer Yes or No only.

**Answer:**
No

---

## Level 2
**Prompt:**
Consider a default logic theory over propositional atoms a, b, c, d.
The known facts are a, b, d.
The defaults are (index: Prerequisite : Justification : Consequent): 0: (b :  : not c) 2: (b : c : not a) 1: (not c : not d : not a).
Imagine iterating to extensions as fixed points E = Gamma(E) as described, one extension at a time (in any order).
Is the formula a true in at least one extension of the theory? Answer Yes or No only.

**Answer:**
Yes

---

**Prompt:**
Consider a default logic theory over propositional atoms a, b, c, d.
The known facts are a, b, c, d.
The defaults are (index: Prerequisite : Justification : Consequent): 0: ( : not d : not d).
Imagine iterating to extensions as fixed points E = Gamma(E) as described, one extension at a time (in any order).
Is the formula not b true in at least one extension of the theory? Answer Yes or No only.

**Answer:**
No

---

## Level 5
**Prompt:**
Consider a default logic theory over propositional atoms a, b, c, d, e.
The known facts are a, d, e.
The defaults are (index: Prerequisite : Justification : Consequent): 2: (a : not e : b, d) 1: (not c : b, d : e) 3: (not c : a, b : not d) 0: (a, not c : not d : b).
Consider the extension E = a, d, e.
A default is applicable in E when E contains its prerequisite, E is consistent with its justification, and E does not already contain its consequent.
In this extension E, is the following default applicable: 3: (not c : a, b : not d)? Answer Yes or No only.

**Answer:**
No

---

**Prompt:**
Consider a default logic theory over propositional atoms a, b, c, d, e.
The known facts are b, c, e.
The defaults are (index: Prerequisite : Justification : Consequent): 4: (not b : a : not e) 0: (not d : not e : c) 3: (not e : not b : c) 2: (c, not e : not b : d) 1: (d, not c : not a : not e).
Imagine iterating to extensions as fixed points E = Gamma(E) as described, one extension at a time (in any order).
Is the formula e true in at least one extension of the theory? Answer Yes or No only.

**Answer:**
Yes

---


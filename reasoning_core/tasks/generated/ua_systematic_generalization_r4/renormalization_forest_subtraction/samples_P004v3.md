# Level 0

## Example 1

**Prompt:**

You are renormalizing a forest of divergent substructures by forest subtraction.
Each node is written as [weight] for a finite substructure, or as [weight|modulus] for a divergent one; nested children are listed between parentheses ( ) and separated by commas.
A node's bare value is its weight plus the renormalized values of all its children. The singular-part projection of a divergent node is the part of its bare value that is an exact whole multiple of its modulus; renormalizing that node subtracts that singular part, leaving the finite remainder bare value modulo the modulus. Finite nodes are taken as their bare value.
Nested divergences are consumed by this recursion and disjoint divergences combine by addition, so overlapping choices are never subtracted twice.
The forest's total renormalized value is the sum of the renormalized values of its top-level trees.
Forest: [2]([2|3]) , [2]([2|3])
What is the total renormalized value? Answer with one non-negative integer.

**Answer:**

8

## Example 2

**Prompt:**

You are renormalizing a forest of divergent substructures by forest subtraction.
Each node is written as [weight] for a finite substructure, or as [weight|modulus] for a divergent one; nested children are listed between parentheses ( ) and separated by commas.
A node's bare value is its weight plus the renormalized values of all its children. The singular-part projection of a divergent node is the part of its bare value that is an exact whole multiple of its modulus; renormalizing that node subtracts that singular part, leaving the finite remainder bare value modulo the modulus. Finite nodes are taken as their bare value.
Nested divergences are consumed by this recursion and disjoint divergences combine by addition, so overlapping choices are never subtracted twice.
The forest's total renormalized value is the sum of the renormalized values of its top-level trees.
Forest: [3] , [1]([1]) , [3|3]
What is the total renormalized value? Answer with one non-negative integer.

**Answer:**

5

# Level 2

## Example 1

**Prompt:**

You are renormalizing a forest of divergent substructures by forest subtraction.
Each node is written as [weight] for a finite substructure, or as [weight|modulus] for a divergent one; nested children are listed between parentheses ( ) and separated by commas.
A node's bare value is its weight plus the renormalized values of all its children. The singular-part projection of a divergent node is the part of its bare value that is an exact whole multiple of its modulus; renormalizing that node subtracts that singular part, leaving the finite remainder bare value modulo the modulus. Finite nodes are taken as their bare value.
Nested divergences are consumed by this recursion and disjoint divergences combine by addition, so overlapping choices are never subtracted twice.
The forest's total renormalized value is the sum of the renormalized values of its top-level trees.
Forest: [1] , [1|5]([3])
What is the total renormalized value? Answer with one non-negative integer.

**Answer:**

5

## Example 2

**Prompt:**

You are renormalizing a forest of divergent substructures by forest subtraction.
Each node is written as [weight] for a finite substructure, or as [weight|modulus] for a divergent one; nested children are listed between parentheses ( ) and separated by commas.
A node's bare value is its weight plus the renormalized values of all its children. The singular-part projection of a divergent node is the part of its bare value that is an exact whole multiple of its modulus; renormalizing that node subtracts that singular part, leaving the finite remainder bare value modulo the modulus. Finite nodes are taken as their bare value.
Nested divergences are consumed by this recursion and disjoint divergences combine by addition, so overlapping choices are never subtracted twice.
The forest's total renormalized value is the sum of the renormalized values of its top-level trees.
Forest: [1]([5] , [3|2]) , [3]([5] , [3])
What is the total renormalized value? Answer with one non-negative integer.

**Answer:**

18

# Level 5

## Example 1

**Prompt:**

You are renormalizing a forest of divergent substructures by forest subtraction.
Each node is written as [weight] for a finite substructure, or as [weight|modulus] for a divergent one; nested children are listed between parentheses ( ) and separated by commas.
A node's bare value is its weight plus the renormalized values of all its children. The singular-part projection of a divergent node is the part of its bare value that is an exact whole multiple of its modulus; renormalizing that node subtracts that singular part, leaving the finite remainder bare value modulo the modulus. Finite nodes are taken as their bare value.
Nested divergences are consumed by this recursion and disjoint divergences combine by addition, so overlapping choices are never subtracted twice.
The forest's total renormalized value is the sum of the renormalized values of its top-level trees.
Forest: [2|8]([7|7]([1|6]) , [3|3]([6|6] , [1] , [2])) , [8|3] , [3|7]([1|5]([2] , [8|2] , [6|4]))
What is the total renormalized value? Answer with one non-negative integer.

**Answer:**

8

## Example 2

**Prompt:**

You are renormalizing a forest of divergent substructures by forest subtraction.
Each node is written as [weight] for a finite substructure, or as [weight|modulus] for a divergent one; nested children are listed between parentheses ( ) and separated by commas.
A node's bare value is its weight plus the renormalized values of all its children. The singular-part projection of a divergent node is the part of its bare value that is an exact whole multiple of its modulus; renormalizing that node subtracts that singular part, leaving the finite remainder bare value modulo the modulus. Finite nodes are taken as their bare value.
Nested divergences are consumed by this recursion and disjoint divergences combine by addition, so overlapping choices are never subtracted twice.
The forest's total renormalized value is the sum of the renormalized values of its top-level trees.
Forest: [7|7]([7]([4|5] , [3] , [1]) , [7|4]) , [4] , [2|4]([3|2]([1|4]) , [6|3])
What is the total renormalized value? Answer with one non-negative integer.

**Answer:**

10

# Samples: strategy_realization_equivalence (P002v1)

Each example gives a full binary decision tree's all-Left history as a
list of nodes, and asks for the reduced-fraction realization probability.

## Level 0

Prompt:

A sequential decision problem is modeled as a full binary decision tree of depth 2. Consider the all-Left decision history, the path obtained by always branching Left; each of the 2 levels contributes one node on this path, listed top-down:

1. decision q 2/3
2. chance 1/5

At a chance node, nature branches Left with the stated probability and Right otherwise. At a decision node, the agent's plan either commits to Left, commits to Right, or makes a local random choice taking Left with the stated probability q. Compute the realization probability of the all-Left history: the product of the Left-branch probabilities at every level. Give the answer as a single reduced fraction "a/b" with b > 0, or "0" if the history is unreachable because some node commits to Right.

**Answer:** 2/15

Prompt:

A sequential decision problem is modeled as a full binary decision tree of depth 2. Consider the all-Left decision history, the path obtained by always branching Left; each of the 2 levels contributes one node on this path, listed top-down:

1. chance 3/4
2. decision q 1/3

At a chance node, nature branches Left with the stated probability and Right otherwise. At a decision node, the agent's plan either commits to Left, commits to Right, or makes a local random choice taking Left with the stated probability q. Compute the realization probability of the all-Left history: the product of the Left-branch probabilities at every level. Give the answer as a single reduced fraction "a/b" with b > 0, or "0" if the history is unreachable because some node commits to Right.

**Answer:** 1/4

## Level 2

Prompt:

A sequential decision problem is modeled as a full binary decision tree of depth 4. Consider the all-Left decision history, the path obtained by always branching Left; each of the 4 levels contributes one node on this path, listed top-down:

1. chance 1/3
2. decision q 2/3
3. decision right
4. decision left

At a chance node, nature branches Left with the stated probability and Right otherwise. At a decision node, the agent's plan either commits to Left, commits to Right, or makes a local random choice taking Left with the stated probability q. Compute the realization probability of the all-Left history: the product of the Left-branch probabilities at every level. Give the answer as a single reduced fraction "a/b" with b > 0, or "0" if the history is unreachable because some node commits to Right.

**Answer:** 0

Prompt:

A sequential decision problem is modeled as a full binary decision tree of depth 4. Consider the all-Left decision history, the path obtained by always branching Left; each of the 4 levels contributes one node on this path, listed top-down:

1. chance 1/3
2. decision left
3. chance 4/5
4. chance 3/4

At a chance node, nature branches Left with the stated probability and Right otherwise. At a decision node, the agent's plan either commits to Left, commits to Right, or makes a local random choice taking Left with the stated probability q. Compute the realization probability of the all-Left history: the product of the Left-branch probabilities at every level. Give the answer as a single reduced fraction "a/b" with b > 0, or "0" if the history is unreachable because some node commits to Right.

**Answer:** 1/5

## Level 5

Prompt:

A sequential decision problem is modeled as a full binary decision tree of depth 7. Consider the all-Left decision history, the path obtained by always branching Left; each of the 7 levels contributes one node on this path, listed top-down:

1. chance 4/5
2. chance 2/5
3. decision q 1/3
4. chance 2/5
5. decision q 3/4
6. decision q 1/2
7. decision left

At a chance node, nature branches Left with the stated probability and Right otherwise. At a decision node, the agent's plan either commits to Left, commits to Right, or makes a local random choice taking Left with the stated probability q. Compute the realization probability of the all-Left history: the product of the Left-branch probabilities at every level. Give the answer as a single reduced fraction "a/b" with b > 0, or "0" if the history is unreachable because some node commits to Right.

**Answer:** 2/125

Prompt:

A sequential decision problem is modeled as a full binary decision tree of depth 7. Consider the all-Left decision history, the path obtained by always branching Left; each of the 7 levels contributes one node on this path, listed top-down:

1. decision q 1/4
2. chance 4/5
3. decision left
4. decision left
5. chance 3/4
6. chance 2/5
7. decision right

At a chance node, nature branches Left with the stated probability and Right otherwise. At a decision node, the agent's plan either commits to Left, commits to Right, or makes a local random choice taking Left with the stated probability q. Compute the realization probability of the all-Left history: the product of the Left-branch probabilities at every level. Give the answer as a single reduced fraction "a/b" with b > 0, or "0" if the history is unreachable because some node commits to Right.

**Answer:** 0

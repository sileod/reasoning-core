# Level 0
Prompt:
Reasoning domain: the actual world is world 0, and there are 4 worlds total, each a truth assignment to the propositions P, Q, R.
worlds:
  world 0: P, R
  world 1: P
  world 2: P
  world 3: Q
distance weight per differing proposition: P:3, Q:4, R:2

Closeness, relative to a focal world, ranks worlds by (weighted Hamming distance to the focal world, then by world index, lower index closer). Evaluate nested counterfactuals outermost first; each scope's antecedent selects the unique closest world satisfying it, centered on the current world. If an antecedent has no satisfying world, 'would' is vacuously true and 'might' is false there.
Under this nested statement: might ( not P and not Q and R ) would ( not P ) then P
Is the whole statement true? Reply with exactly one word, either yes or no, as the final answer.
Answer: no

Prompt:
Reasoning domain: the actual world is world 0, and there are 4 worlds total, each a truth assignment to the propositions P, Q, R.
worlds:
  world 0: P
  world 1: R
  world 2: P, Q
  world 3: none
distance weight per differing proposition: P:1, Q:3, R:1

Closeness, relative to a focal world, ranks worlds by (weighted Hamming distance to the focal world, then by world index, lower index closer). Evaluate nested counterfactuals outermost first; each scope's antecedent selects the unique closest world satisfying it, centered on the current world. If an antecedent has no satisfying world, 'would' is vacuously true and 'might' is false there.
Under this nested statement: might ( P and not Q and R ) might ( not P ) then P
Is the whole statement true? Reply with exactly one word, either yes or no, as the final answer.
Answer: no

# Level 2
Prompt:
Reasoning domain: the actual world is world 0, and there are 6 worlds total, each a truth assignment to the propositions P, Q, R, S.
worlds:
  world 0: P, Q, R, S
  world 1: P, Q, R
  world 2: P, Q
  world 3: P, Q, S
  world 4: Q
  world 5: none
distance weight per differing proposition: P:8, Q:6, R:1, S:8

Closeness, relative to a focal world, ranks worlds by (weighted Hamming distance to the focal world, then by world index, lower index closer). Evaluate nested counterfactuals outermost first; each scope's antecedent selects the unique closest world satisfying it, centered on the current world. If an antecedent has no satisfying world, 'would' is vacuously true and 'might' is false there.
Under this nested statement: would ( not R ) would ( not S ) might ( not Q ) then S
Is the whole statement true? Reply with exactly one word, either yes or no, as the final answer.
Answer: no

Prompt:
Reasoning domain: the actual world is world 0, and there are 6 worlds total, each a truth assignment to the propositions P, Q, R, S.
worlds:
  world 0: none
  world 1: P, Q, R, S
  world 2: P, Q, R, S
  world 3: Q, R, S
  world 4: Q, R, S
  world 5: Q, R, S
distance weight per differing proposition: P:6, Q:3, R:2, S:4

Closeness, relative to a focal world, ranks worlds by (weighted Hamming distance to the focal world, then by world index, lower index closer). Evaluate nested counterfactuals outermost first; each scope's antecedent selects the unique closest world satisfying it, centered on the current world. If an antecedent has no satisfying world, 'would' is vacuously true and 'might' is false there.
Under this nested statement: would ( S ) might ( Q ) might ( not P and Q and R and not S ) then R
Is the whole statement true? Reply with exactly one word, either yes or no, as the final answer.
Answer: no

# Level 5
Prompt:
Reasoning domain: the actual world is world 0, and there are 9 worlds total, each a truth assignment to the propositions P, Q, R, S, T.
worlds:
  world 0: P, R
  world 1: P, Q
  world 2: P, Q, T
  world 3: R, S
  world 4: P, R, S, T
  world 5: P, Q, R, T
  world 6: P, Q, R, S, T
  world 7: P, Q, R, T
  world 8: Q, T
distance weight per differing proposition: P:9, Q:11, R:9, S:3, T:10

Closeness, relative to a focal world, ranks worlds by (weighted Hamming distance to the focal world, then by world index, lower index closer). Evaluate nested counterfactuals outermost first; each scope's antecedent selects the unique closest world satisfying it, centered on the current world. If an antecedent has no satisfying world, 'would' is vacuously true and 'might' is false there.
Under this nested statement: might ( P and not Q ) would ( not P and not S ) would ( not Q and not S ) might ( not P and T ) then T
Is the whole statement true? Reply with exactly one word, either yes or no, as the final answer.
Answer: yes

Prompt:
Reasoning domain: the actual world is world 0, and there are 9 worlds total, each a truth assignment to the propositions P, Q, R, S, T.
worlds:
  world 0: Q, R
  world 1: Q, R, S
  world 2: S
  world 3: P, Q, S, T
  world 4: R, S, T
  world 5: S, T
  world 6: P, Q, R, T
  world 7: P, Q, S
  world 8: R, S
distance weight per differing proposition: P:12, Q:2, R:3, S:9, T:14

Closeness, relative to a focal world, ranks worlds by (weighted Hamming distance to the focal world, then by world index, lower index closer). Evaluate nested counterfactuals outermost first; each scope's antecedent selects the unique closest world satisfying it, centered on the current world. If an antecedent has no satisfying world, 'would' is vacuously true and 'might' is false there.
Under this nested statement: would ( not R and S ) would ( not Q and not T ) would ( P and not R ) would ( not P and Q and not R and S and T ) then Q
Is the whole statement true? Reply with exactly one word, either yes or no, as the final answer.
Answer: yes

# End samples (nested_closest_world_counterfactuals)

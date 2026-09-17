# Samples: backdoor_adjustment_selection (P006v3)

## Level 0

### Example 1

Prompt:

A researcher wants the total causal effect of treatment X on outcome Y. The full causal DAG has nodes X, Y, bmi, exercise, sleep, stress, work. Its only directed edges are:
X -> Y; X -> bmi; exercise -> sleep; sleep -> stress; stress -> bmi.
There are no additional variables, edges or unlisted common causes. Unmeasured variables: sleep; keep them in the graph but do not adjust for them. Only these covariates are available for adjustment: bmi, exercise, stress, work.
Use Pearl's backdoor criterion, with Bayes-ball or ancestral moralization for d-separation: a valid set contains no descendants of X in the original DAG and d-separates X and Y after deleting every arrow out of X. A path is active given a set when every internal noncollider is outside the set and every collider is in the set or has a descendant in it.
Choose a valid set of minimum cardinality. Among ties choose the lexicographically smallest alphabetically sorted list of names. Reply only with its names in alphabetical order separated by commas (format example: age, bmi). Reply none for the empty set, or impossible if no subset of available covariates qualifies.

Answer: none

### Example 2

Prompt:

A researcher wants the total causal effect of treatment X on outcome Y. The full causal DAG has nodes X, Y, activity, bmi, cholesterol, smoking, work. Its only directed edges are:
X -> Y; X -> work; Y -> cholesterol; smoking -> X; smoking -> Y; smoking -> activity.
There are no additional variables, edges or unlisted common causes. Unmeasured variables: activity, bmi; keep them in the graph but do not adjust for them. Only these covariates are available for adjustment: cholesterol, smoking, work.
Use Pearl's backdoor criterion, with Bayes-ball or ancestral moralization for d-separation: a valid set contains no descendants of X in the original DAG and d-separates X and Y after deleting every arrow out of X. A path is active given a set when every internal noncollider is outside the set and every collider is in the set or has a descendant in it.
Choose a valid set of minimum cardinality. Among ties choose the lexicographically smallest alphabetically sorted list of names. Reply only with its names in alphabetical order separated by commas (format example: age, bmi). Reply none for the empty set, or impossible if no subset of available covariates qualifies.

Answer: smoking

## Level 2

### Example 1

Prompt:

A researcher wants the total causal effect of treatment X on outcome Y. The full causal DAG has nodes X, Y, age, bmi, diet, education, exercise, stress, work. Its only directed edges are:
X -> Y; X -> age; education -> X; education -> Y; education -> bmi; education -> stress; exercise -> bmi; stress -> bmi; work -> X; work -> bmi; work -> education; work -> stress.
There are no additional variables, edges or unlisted common causes. Unmeasured variables: stress; keep them in the graph but do not adjust for them. Only these covariates are available for adjustment: age, bmi, diet, education, exercise, work.
Use Pearl's backdoor criterion, with Bayes-ball or ancestral moralization for d-separation: a valid set contains no descendants of X in the original DAG and d-separates X and Y after deleting every arrow out of X. A path is active given a set when every internal noncollider is outside the set and every collider is in the set or has a descendant in it.
Choose a valid set of minimum cardinality. Among ties choose the lexicographically smallest alphabetically sorted list of names. Reply only with its names in alphabetical order separated by commas (format example: age, bmi). Reply none for the empty set, or impossible if no subset of available covariates qualifies.

Answer: education

### Example 2

Prompt:

A researcher wants the total causal effect of treatment X on outcome Y. The full causal DAG has nodes X, Y, activity, age, bmi, diet, education, income, work. Its only directed edges are:
X -> Y; X -> activity; X -> bmi; age -> Y; age -> income; education -> age; education -> diet; education -> income; work -> X.
There are no additional variables, edges or unlisted common causes. Unmeasured variables: income; keep them in the graph but do not adjust for them. Only these covariates are available for adjustment: activity, age, bmi, diet, education, work.
Use Pearl's backdoor criterion, with Bayes-ball or ancestral moralization for d-separation: a valid set contains no descendants of X in the original DAG and d-separates X and Y after deleting every arrow out of X. A path is active given a set when every internal noncollider is outside the set and every collider is in the set or has a descendant in it.
Choose a valid set of minimum cardinality. Among ties choose the lexicographically smallest alphabetically sorted list of names. Reply only with its names in alphabetical order separated by commas (format example: age, bmi). Reply none for the empty set, or impossible if no subset of available covariates qualifies.

Answer: none

## Level 5

### Example 1

Prompt:

A researcher wants the total causal effect of treatment X on outcome Y. The full causal DAG has nodes X, Y, bmi, cholesterol, diet, exercise, income, sleep, stress, support, weight, work. Its only directed edges are:
X -> Y; X -> bmi; bmi -> sleep; diet -> X; diet -> Y; diet -> cholesterol; exercise -> stress; income -> exercise; income -> stress; sleep -> Y; stress -> sleep; support -> sleep; weight -> cholesterol; work -> X; work -> cholesterol; work -> sleep.
There are no additional variables, edges or unlisted common causes. Unmeasured variables: income; keep them in the graph but do not adjust for them. Only these covariates are available for adjustment: bmi, cholesterol, diet, exercise, sleep, stress, support, weight, work.
Use Pearl's backdoor criterion, with Bayes-ball or ancestral moralization for d-separation: a valid set contains no descendants of X in the original DAG and d-separates X and Y after deleting every arrow out of X. A path is active given a set when every internal noncollider is outside the set and every collider is in the set or has a descendant in it.
Choose a valid set of minimum cardinality. Among ties choose the lexicographically smallest alphabetically sorted list of names. Reply only with its names in alphabetical order separated by commas (format example: age, bmi). Reply none for the empty set, or impossible if no subset of available covariates qualifies.

Answer: diet, work

### Example 2

Prompt:

A researcher wants the total causal effect of treatment X on outcome Y. The full causal DAG has nodes X, Y, activity, age, bmi, cholesterol, diet, income, sleep, stress, support, weight. Its only directed edges are:
X -> Y; age -> cholesterol; age -> diet; age -> support; bmi -> X; bmi -> diet; bmi -> sleep; bmi -> stress; cholesterol -> X; cholesterol -> Y; cholesterol -> sleep; cholesterol -> support; income -> activity; income -> diet; sleep -> X; support -> sleep; weight -> Y.
There are no additional variables, edges or unlisted common causes. Unmeasured variables: weight; keep them in the graph but do not adjust for them. Only these covariates are available for adjustment: activity, age, bmi, cholesterol, diet, income, sleep, stress, support.
Use Pearl's backdoor criterion, with Bayes-ball or ancestral moralization for d-separation: a valid set contains no descendants of X in the original DAG and d-separates X and Y after deleting every arrow out of X. A path is active given a set when every internal noncollider is outside the set and every collider is in the set or has a descendant in it.
Choose a valid set of minimum cardinality. Among ties choose the lexicographically smallest alphabetically sorted list of names. Reply only with its names in alphabetical order separated by commas (format example: age, bmi). Reply none for the empty set, or impossible if no subset of available covariates qualifies.

Answer: cholesterol

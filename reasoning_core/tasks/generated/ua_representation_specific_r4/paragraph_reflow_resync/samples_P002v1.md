# Level 0

## Example 1

A cached paragraph was laid out at width 12 (glue+discretionary-break), producing these lines (0-indexed, each line on its own row):
0: of zeta fox
1: brown rho on
2: the omega
3: kappa
4: epsilon
5: omega art
6: tau
The paragraph then changed (a word was edited, inserted, or removed, and the width became 10) and was re-wrapped. The new lines are:
0: of zeta
1: fox brown
2: rho on the
3: omega
4: kappa
5: epsilon
6: omega art
7: tau
Return the sorted list of line indices whose text differs between the old and new layouts. The answer is a sorted list of integers, e.g. [1, 3].

Answer: [0, 1, 2, 3, 4, 5, 6, 7]

## Example 2

A cached paragraph was laid out at width 12 (glue+discretionary-break), producing these lines (0-indexed, each line on its own row):
0: xi sigma the
1: phi epsilon
2: delta dolor
The paragraph then changed (a word was edited, inserted, or removed, and the width became 11) and was re-wrapped. The new lines are:
0: xi sigma
1: the phi
2: iota delta
3: dolor
Return the sorted list of line indices whose text differs between the old and new layouts. The answer is a sorted list of integers, e.g. [1, 3].

Answer: [0, 1, 2, 3]

# Level 2

## Example 1

A cached paragraph was laid out at width 11 (glue+discretionary-break), producing these lines (0-indexed, each line on its own row):
0: upsilon chi
1: jumps beta
2: omicron
3: amet over
4: rho quick
5: kappa brown
6: upsilon psi
7: of omicron
8: omega xi
The paragraph then changed (a word was edited, inserted, or removed, and the width became 10) and was re-wrapped. The new lines are:
0: upsilon
1: chi jumps
2: beta
3: omicron
4: and over
5: rho quick
6: kappa
7: brown
8: upsilon
9: psi of
10: omicron
11: omega xi
Return the sorted list of line indices whose text differs between the old and new layouts. The answer is a sorted list of integers, e.g. [1, 3].

Answer: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

## Example 2

A cached paragraph was laid out at width 11 (glue+discretionary-break), producing these lines (0-indexed, each line on its own row):
0: adipiscing
1: ipsum omega
2: chi brown
3: gamma amet
4: fox dolor
5: sit alpha
6: iota the
7: for sigma
8: of chi of
9: zeta
The paragraph then changed (a word was edited, inserted, or removed, and the width became 10) and was re-wrapped. The new lines are:
0: adipiscing
1: ipsum
2: omega chi
3: brown
4: gamma amet
5: fox dolor
6: sit the
7: iota the
8: for sigma
9: of chi of
10: zeta
Return the sorted list of line indices whose text differs between the old and new layouts. The answer is a sorted list of integers, e.g. [1, 3].

Answer: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Level 5

## Example 1

A cached paragraph was laid out at width 10 (glue-only), producing these lines (0-indexed, each line on its own row):
0: theta
1: ipsum nu
2: hbgbggijgccg
3: psi
4: deaabefahbd
5: phi and
6: jumps
7: igdbhcjgegd
8: on brown
9: for and
10: bdfijaafeeib
11: and
The paragraph then changed (a word was edited, inserted, or removed, and the width became 11) and was re-wrapped. The new lines are:
0: theta ipsum
1: nu
2: hbgbggijgccg
3: psi
4: deaabefahbd
5: phi and
6: jumps
7: igdbhcjgegd
8: on brown
9: for and
10: bdfijaafeeib
11: and
Return the sorted list of line indices whose text differs between the old and new layouts. The answer is a sorted list of integers, e.g. [1, 3].

Answer: [0, 1]

## Example 2

A cached paragraph was laid out at width 10 (glue-only), producing these lines (0-indexed, each line on its own row):
0: dolor
1: sigma
2: alpha lazy
3: sigma art
4: ipsum phi
5: alpha
6: omega
7: ajaiiedidejdiij
8: adjgdfgdcfa
9: with delta
10: kappa
11: quick
12: ejaibfbafiia
13: brown
14: jhfbhhhddad
15: quick
The paragraph then changed (a word was edited, inserted, or removed, and the width became 12) and was re-wrapped. The new lines are:
0: dolor sigma
1: alpha lazy
2: sigma art
3: ipsum phi
4: alpha omega
5: ajaiiedidejdiij
6: adjgdfgdcfa
7: with delta
8: kappa quick
9: ejaibfbafiia
10: brown
11: jhfbhhhddad
12: quick
Return the sorted list of line indices whose text differs between the old and new layouts. The answer is a sorted list of integers, e.g. [1, 3].

Answer: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


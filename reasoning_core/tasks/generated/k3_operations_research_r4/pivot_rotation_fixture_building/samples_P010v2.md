# P010v2 pivot_rotation_fixture_building samples

# Level 0

## Example 1

**Prompt:**

A round-robin tournament schedules games among 8 teams numbered 0..7. The circle (pivot) method with team 0 as the fixed pivot produces the schedule: in every round the other teams are arranged around team 0 and rotated each round, and the teams at symmetric positions play -- for i from 0 to 3, the team at position i is home against the team at position 4 (away). The season is a double season: the 7 basic rounds are played, then mirrored with each team's home and away swapped. Round indexes are 0-based. For round 5, list the pairings as Home@Away in position order, separated by ";". Also give team 3's home/away string over all rounds as a sequence of H (home) and A (away) letters, in round order. Also give the total break count: a break is when a team occupies the same venue (home or away) in two consecutive rounds, counted over every team and every pair of consecutive rounds. Answer with exactly one line of the form pairings|homeaway|breakcount, e.g. 0@5;1@4;2@3|AHHA|5.

**Answer:**

0@2;3@1;4@7;5@6|HAAAAHHAHHHHAA|74

## Example 2

**Prompt:**

A round-robin tournament schedules games among 8 teams numbered 0..7. The circle (pivot) method with team 0 as the fixed pivot produces the schedule: in every round the other teams are arranged around team 0 and rotated each round, and the teams at symmetric positions play -- for i from 0 to 3, the team at position i is home against the team at position 4 (away). The season is a double season: the 7 basic rounds are played, then mirrored with each team's home and away swapped. Round indexes are 0-based. For round 6, list the pairings as Home@Away in position order, separated by ";". Also give team 0's home/away string over all rounds as a sequence of H (home) and A (away) letters, in round order. Also give the total break count: a break is when a team occupies the same venue (home or away) in two consecutive rounds, counted over every team and every pair of consecutive rounds. Answer with exactly one line of the form pairings|homeaway|breakcount, e.g. 0@5;1@4;2@3|AHHA|5.

**Answer:**

0@1;2@7;3@6;4@5|HHHHHHHAAAAAAA|74

# Level 2

## Example 1

**Prompt:**

A round-robin tournament schedules games among 12 teams numbered 0..11. The circle (pivot) method with team 0 as the fixed pivot produces the schedule: in every round the other teams are arranged around team 0 and rotated each round, and the teams at symmetric positions play -- for i from 0 to 5, the team at position i is home against the team at position 6 (away). The season is a single round-robin of 11 rounds. Round indexes are 0-based. For round 2, list the pairings as Home@Away in position order, separated by ";". Also give team 7's home/away string over all rounds as a sequence of H (home) and A (away) letters, in round order. Also give the total break count: a break is when a team occupies the same venue (home or away) in two consecutive rounds, counted over every team and every pair of consecutive rounds. Answer with exactly one line of the form pairings|homeaway|breakcount, e.g. 0@5;1@4;2@3|AHHA|5.

**Answer:**

0@9;10@8;11@7;1@6;2@5;3@4|AAAAAHHHHHA|100

## Example 2

**Prompt:**

A round-robin tournament schedules games among 12 teams numbered 0..11. The circle (pivot) method with team 0 as the fixed pivot produces the schedule: in every round the other teams are arranged around team 0 and rotated each round, and the teams at symmetric positions play -- for i from 0 to 5, the team at position i is home against the team at position 6 (away). The season is a double season: the 11 basic rounds are played, then mirrored with each team's home and away swapped. Round indexes are 0-based. For round 9, list the pairings as Home@Away in position order, separated by ";". Also give team 0's home/away string over all rounds as a sequence of H (home) and A (away) letters, in round order. Also give the total break count: a break is when a team occupies the same venue (home or away) in two consecutive rounds, counted over every team and every pair of consecutive rounds. Answer with exactly one line of the form pairings|homeaway|breakcount, e.g. 0@5;1@4;2@3|AHHA|5.

**Answer:**

0@2;3@1;4@11;5@10;6@9;7@8|HHHHHHHHHHHAAAAAAAAAAA|202

# Level 5

## Example 1

**Prompt:**

A round-robin tournament schedules games among 18 teams numbered 0..17. The circle (pivot) method with team 0 as the fixed pivot produces the schedule: in every round the other teams are arranged around team 0 and rotated each round, and the teams at symmetric positions play -- for i from 0 to 8, the team at position i is home against the team at position 9 (away). The season is a double season: the 17 basic rounds are played, then mirrored with each team's home and away swapped. Round indexes are 0-based. For round 28, list the pairings as Home@Away in position order, separated by ";". Also give team 14's home/away string over all rounds as a sequence of H (home) and A (away) letters, in round order. Also give the total break count: a break is when a team occupies the same venue (home or away) in two consecutive rounds, counted over every team and every pair of consecutive rounds. Answer with exactly one line of the form pairings|homeaway|breakcount, e.g. 0@5;1@4;2@3|AHHA|5.

**Answer:**

6@0;5@7;4@8;3@9;2@10;1@11;17@12;16@13;15@14|AAAAHHHHHHHHAAAAAHHHHAAAAAAAAHHHHH|514

## Example 2

**Prompt:**

A round-robin tournament schedules games among 18 teams numbered 0..17. The circle (pivot) method with team 0 as the fixed pivot produces the schedule: in every round the other teams are arranged around team 0 and rotated each round, and the teams at symmetric positions play -- for i from 0 to 8, the team at position i is home against the team at position 9 (away). The season is a double season: the 17 basic rounds are played, then mirrored with each team's home and away swapped. Round indexes are 0-based. For round 33, list the pairings as Home@Away in position order, separated by ";". Also give team 5's home/away string over all rounds as a sequence of H (home) and A (away) letters, in round order. Also give the total break count: a break is when a team occupies the same venue (home or away) in two consecutive rounds, counted over every team and every pair of consecutive rounds. Answer with exactly one line of the form pairings|homeaway|breakcount, e.g. 0@5;1@4;2@3|AHHA|5.

**Answer:**

1@0;17@2;16@3;15@4;14@5;13@6;12@7;11@8;10@9|HHHHAAAAAAAAAHHHHAAAAHHHHHHHHHAAAA|514


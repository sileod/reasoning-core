# Samples for P011v1

## Level 0

Five latent attributes are scored by unknown strictly positive weights; each option is a binary vector over the five attributes (1 = attribute present). The value of an option is the weighted sum of its attributes, and a person prefers option u to option v whenever u's weighted sum exceeds v's.
Option 0 = (1, 0, 1, 0, 0)
Option 1 = (1, 0, 0, 0, 1)
Option 2 = (0, 0, 0, 1, 0)
Observed pairwise preferences (u > v means u preferred over v):
  2 > 0
Now the unseen comparison 1 > 2 is proposed. First decide whether there exists a strictly positive weight vector consistent with the observed preferences (an additive representation). Then decide the status of the proposed comparison among consistent weight vectors.
Answer exactly one of: 'infeasible' (no positive weight vector fits the observed preferences), 'feasible_not_forced' (a consistent additive representation exists and 1 > 2 holds for some but not all such representations), or 'feasible_and_forced' (a consistent additive representation exists and 1 > 2 holds for every one).

**Answer**: feasible_not_forced

Five latent attributes are scored by unknown strictly positive weights; each option is a binary vector over the five attributes (1 = attribute present). The value of an option is the weighted sum of its attributes, and a person prefers option u to option v whenever u's weighted sum exceeds v's.
Option 0 = (1, 0, 1, 1, 0)
Option 1 = (1, 0, 0, 0, 0)
Option 2 = (0, 0, 0, 1, 0)
Observed pairwise preferences (u > v means u preferred over v):
  1 > 2
Now the unseen comparison 0 > 2 is proposed. First decide whether there exists a strictly positive weight vector consistent with the observed preferences (an additive representation). Then decide the status of the proposed comparison among consistent weight vectors.
Answer exactly one of: 'infeasible' (no positive weight vector fits the observed preferences), 'feasible_not_forced' (a consistent additive representation exists and 0 > 2 holds for some but not all such representations), or 'feasible_and_forced' (a consistent additive representation exists and 0 > 2 holds for every one).

**Answer**: feasible_and_forced


## Level 2

Five latent attributes are scored by unknown strictly positive weights; each option is a binary vector over the five attributes (1 = attribute present). The value of an option is the weighted sum of its attributes, and a person prefers option u to option v whenever u's weighted sum exceeds v's.
Option 0 = (0, 0, 0, 1, 0)
Option 1 = (1, 1, 1, 1, 0)
Option 2 = (1, 1, 0, 1, 0)
Option 3 = (0, 1, 1, 1, 1)
Option 4 = (1, 0, 1, 1, 0)
Observed pairwise preferences (u > v means u preferred over v):
  2 > 1
  2 > 3
  0 > 1
  3 > 2
  0 > 3
  1 > 2
  2 > 0
  4 > 2
  1 > 0
  1 > 3
  2 > 4
  0 > 2
Now the unseen comparison 3 > 1 is proposed. First decide whether there exists a strictly positive weight vector consistent with the observed preferences (an additive representation). Then decide the status of the proposed comparison among consistent weight vectors.
Answer exactly one of: 'infeasible' (no positive weight vector fits the observed preferences), 'feasible_not_forced' (a consistent additive representation exists and 3 > 1 holds for some but not all such representations), or 'feasible_and_forced' (a consistent additive representation exists and 3 > 1 holds for every one).

**Answer**: infeasible

Five latent attributes are scored by unknown strictly positive weights; each option is a binary vector over the five attributes (1 = attribute present). The value of an option is the weighted sum of its attributes, and a person prefers option u to option v whenever u's weighted sum exceeds v's.
Option 0 = (1, 1, 0, 1, 1)
Option 1 = (1, 0, 0, 0, 0)
Option 2 = (0, 0, 0, 0, 1)
Option 3 = (1, 0, 1, 1, 1)
Option 4 = (0, 0, 1, 0, 1)
Observed pairwise preferences (u > v means u preferred over v):
  0 > 2
  4 > 2
  2 > 1
Now the unseen comparison 2 > 3 is proposed. First decide whether there exists a strictly positive weight vector consistent with the observed preferences (an additive representation). Then decide the status of the proposed comparison among consistent weight vectors.
Answer exactly one of: 'infeasible' (no positive weight vector fits the observed preferences), 'feasible_not_forced' (a consistent additive representation exists and 2 > 3 holds for some but not all such representations), or 'feasible_and_forced' (a consistent additive representation exists and 2 > 3 holds for every one).

**Answer**: feasible_not_forced


## Level 5

Five latent attributes are scored by unknown strictly positive weights; each option is a binary vector over the five attributes (1 = attribute present). The value of an option is the weighted sum of its attributes, and a person prefers option u to option v whenever u's weighted sum exceeds v's.
Option 0 = (0, 1, 1, 1, 0)
Option 1 = (1, 1, 1, 1, 0)
Option 2 = (1, 1, 1, 0, 0)
Option 3 = (1, 0, 1, 1, 1)
Option 4 = (0, 1, 0, 0, 1)
Option 5 = (0, 1, 1, 0, 1)
Option 6 = (0, 1, 0, 0, 0)
Option 7 = (1, 0, 0, 1, 0)
Observed pairwise preferences (u > v means u preferred over v):
  1 > 0
  4 > 1
  5 > 3
Now the unseen comparison 5 > 0 is proposed. First decide whether there exists a strictly positive weight vector consistent with the observed preferences (an additive representation). Then decide the status of the proposed comparison among consistent weight vectors.
Answer exactly one of: 'infeasible' (no positive weight vector fits the observed preferences), 'feasible_not_forced' (a consistent additive representation exists and 5 > 0 holds for some but not all such representations), or 'feasible_and_forced' (a consistent additive representation exists and 5 > 0 holds for every one).

**Answer**: feasible_and_forced

Five latent attributes are scored by unknown strictly positive weights; each option is a binary vector over the five attributes (1 = attribute present). The value of an option is the weighted sum of its attributes, and a person prefers option u to option v whenever u's weighted sum exceeds v's.
Option 0 = (1, 1, 0, 1, 0)
Option 1 = (1, 1, 1, 1, 1)
Option 2 = (1, 1, 1, 0, 1)
Option 3 = (0, 0, 1, 1, 1)
Option 4 = (1, 0, 1, 1, 1)
Option 5 = (0, 0, 1, 0, 0)
Option 6 = (0, 1, 1, 1, 0)
Option 7 = (1, 0, 0, 1, 1)
Observed pairwise preferences (u > v means u preferred over v):
  3 > 2
  1 > 5
  7 > 4
  6 > 4
  4 > 6
  1 > 0
  3 > 1
  6 > 3
  7 > 3
  5 > 0
  5 > 2
  3 > 4
  5 > 1
  7 > 1
  5 > 6
  0 > 6
  7 > 2
  6 > 1
  5 > 4
  4 > 1
  4 > 5
  0 > 1
  1 > 4
  0 > 3
  3 > 5
  6 > 5
  1 > 3
  2 > 0
  4 > 7
  0 > 5
  1 > 7
  4 > 3
  3 > 0
  3 > 6
  4 > 2
  0 > 2
  2 > 4
  1 > 6
  3 > 7
  0 > 4
  7 > 5
  1 > 2
  2 > 6
  6 > 2
  7 > 0
  6 > 0
  2 > 7
  4 > 0
  7 > 6
  2 > 3
  5 > 7
  2 > 5
  5 > 3
Now the unseen comparison 0 > 7 is proposed. First decide whether there exists a strictly positive weight vector consistent with the observed preferences (an additive representation). Then decide the status of the proposed comparison among consistent weight vectors.
Answer exactly one of: 'infeasible' (no positive weight vector fits the observed preferences), 'feasible_not_forced' (a consistent additive representation exists and 0 > 7 holds for some but not all such representations), or 'feasible_and_forced' (a consistent additive representation exists and 0 > 7 holds for every one).

**Answer**: infeasible


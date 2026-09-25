## Level 0
### Example 1
**Prompt:**
Two statisticians each propose a joint distribution over binary variables X and Y. Candidate distribution P0 gives X=0,Y=0: 1/4; X=0,Y=1: 1/4; X=1,Y=0: 0/1; X=1,Y=1: 1/2; candidate distribution P1 gives X=0,Y=0: 1/4; X=0,Y=1: 1/4; X=1,Y=0: 1/2; X=1,Y=1: 0/1. You fit a mixture P = w*P0 + (1-w)*P1 with unknown rational weight w. Find the unique rational weight w with 0<w<1 such that X and Y are independent under P. Give w as a fraction a/b in lowest terms, e.g. 3/5.

**Answer:** 1/2

### Example 2
**Prompt:**
Two statisticians each propose a joint distribution over binary variables X and Y. Candidate distribution P0 gives X=0,Y=0: 18/25; X=0,Y=1: 11/75; X=1,Y=0: 1/75; X=1,Y=1: 3/25; candidate distribution P1 gives X=0,Y=0: 0/1; X=0,Y=1: 2/3; X=1,Y=0: 1/3; X=1,Y=1: 0/1. You fit a mixture P = w*P0 + (1-w)*P1 with unknown rational weight w. Find the unique rational weight w with 0<w<1 such that X and Y are independent under P. Give w as a fraction a/b in lowest terms, e.g. 3/5.

**Answer:** 2/3

## Level 2
### Example 1
**Prompt:**
Two statisticians each propose a joint distribution over binary variables X and Y given a conditioning variable Z with equally likely levels.
At level Z=z1: candidate distribution P0 gives X=0,Y=0: 2/27; X=0,Y=1: 7/27; X=1,Y=0: 7/27; X=1,Y=1: 11/27; candidate distribution P1 gives X=0,Y=0: 1/6; X=0,Y=1: 1/6; X=1,Y=0: 1/6; X=1,Y=1: 1/2.
At level Z=z2: candidate distribution P0 gives X=0,Y=0: 8/45; X=0,Y=1: 7/45; X=1,Y=0: 22/45; X=1,Y=1: 8/45; candidate distribution P1 gives X=0,Y=0: 1/3; X=0,Y=1: 1/6; X=1,Y=0: 1/6; X=1,Y=1: 1/3.
At level Z=z3: candidate distribution P0 gives X=0,Y=0: 20/27; X=0,Y=1: 1/27; X=1,Y=0: 1/27; X=1,Y=1: 5/27; candidate distribution P1 gives X=0,Y=0: 0/1; X=0,Y=1: 1/2; X=1,Y=0: 1/2; X=1,Y=1: 0/1.
A mixture of weight w draws from P0 and weight 1-w draws from P1, using the SAME rational weight w in every level, so within level z the joint is M_z = w*P0 + (1-w)*P1. Find the unique rational weight w with 0<w<1 such that X and Y are conditionally independent given Z (independent within every level simultaneously). Give w as a fraction a/b in lowest terms, e.g. 3/5.

**Answer:** 3/5

### Example 2
**Prompt:**
Two statisticians each propose a joint distribution over binary variables X and Y given a conditioning variable Z with equally likely levels.
At level Z=z1: candidate distribution P0 gives X=0,Y=0: 1/2; X=0,Y=1: 0/1; X=1,Y=0: 0/1; X=1,Y=1: 1/2; candidate distribution P1 gives X=0,Y=0: 0/1; X=0,Y=1: 1/2; X=1,Y=0: 1/2; X=1,Y=1: 0/1.
At level Z=z2: candidate distribution P0 gives X=0,Y=0: 11/45; X=0,Y=1: 118/315; X=1,Y=0: 43/315; X=1,Y=1: 11/45; candidate distribution P1 gives X=0,Y=0: 1/5; X=0,Y=1: 18/35; X=1,Y=0: 3/35; X=1,Y=1: 1/5.
At level Z=z3: candidate distribution P0 gives X=0,Y=0: 6/175; X=0,Y=1: 17/525; X=1,Y=0: 472/525; X=1,Y=1: 6/175; candidate distribution P1 gives X=0,Y=0: 2/7; X=0,Y=1: 1/21; X=1,Y=0: 8/21; X=1,Y=1: 2/7.
A mixture of weight w draws from P0 and weight 1-w draws from P1, using the SAME rational weight w in every level, so within level z the joint is M_z = w*P0 + (1-w)*P1. Find the unique rational weight w with 0<w<1 such that X and Y are conditionally independent given Z (independent within every level simultaneously). Give w as a fraction a/b in lowest terms, e.g. 3/5.

**Answer:** 1/2

## Level 5
### Example 1
**Prompt:**
Two statisticians each propose a joint distribution over binary variables X and Y given a conditioning variable Z with equally likely levels.
At level Z=z1: candidate distribution P0 gives X=0,Y=0: 1/4; X=0,Y=1: 0/1; X=1,Y=0: 0/1; X=1,Y=1: 3/4; candidate distribution P1 gives X=0,Y=0: 0/1; X=0,Y=1: 1/4; X=1,Y=0: 3/4; X=1,Y=1: 0/1.
At level Z=z2: candidate distribution P0 gives X=0,Y=0: 7/24; X=0,Y=1: 3/8; X=1,Y=0: 7/24; X=1,Y=1: 1/24; candidate distribution P1 gives X=0,Y=0: 1/3; X=0,Y=1: 0/1; X=1,Y=0: 1/3; X=1,Y=1: 1/3.
At level Z=z3: candidate distribution P0 gives X=0,Y=0: 6/25; X=0,Y=1: 3/175; X=1,Y=0: 18/175; X=1,Y=1: 16/25; candidate distribution P1 gives X=0,Y=0: 0/1; X=0,Y=1: 1/7; X=1,Y=0: 6/7; X=1,Y=1: 0/1.
At level Z=z4: candidate distribution P0 gives X=0,Y=0: 1/2; X=0,Y=1: 0/1; X=1,Y=0: 0/1; X=1,Y=1: 1/2; candidate distribution P1 gives X=0,Y=0: 0/1; X=0,Y=1: 1/2; X=1,Y=0: 1/2; X=1,Y=1: 0/1.
At level Z=z5: candidate distribution P0 gives X=0,Y=0: 4/9; X=0,Y=1: 1/9; X=1,Y=0: 1/9; X=1,Y=1: 1/3; candidate distribution P1 gives X=0,Y=0: 1/18; X=0,Y=1: 7/18; X=1,Y=0: 7/18; X=1,Y=1: 1/6.
A mixture of weight w draws from P0 and weight 1-w draws from P1, using the SAME rational weight w in every level, so within level z the joint is M_z = w*P0 + (1-w)*P1. Find the unique rational weight w with 0<w<1 such that X and Y are conditionally independent given Z (independent within every level simultaneously). Give w as a fraction a/b in lowest terms, e.g. 3/5.

**Answer:** 1/2

### Example 2
**Prompt:**
Two statisticians each propose a joint distribution over binary variables X and Y given a conditioning variable Z with equally likely levels.
At level Z=z1: candidate distribution P0 gives X=0,Y=0: 103/144; X=0,Y=1: 7/144; X=1,Y=0: 29/144; X=1,Y=1: 5/144; candidate distribution P1 gives X=0,Y=0: 1/8; X=0,Y=1: 1/2; X=1,Y=0: 3/8; X=1,Y=1: 0/1.
At level Z=z2: candidate distribution P0 gives X=0,Y=0: 1/54; X=0,Y=1: 1/54; X=1,Y=0: 1/2; X=1,Y=1: 25/54; candidate distribution P1 gives X=0,Y=0: 1/3; X=0,Y=1: 1/3; X=1,Y=0: 0/1; X=1,Y=1: 1/3.
At level Z=z3: candidate distribution P0 gives X=0,Y=0: 8/45; X=0,Y=1: 241/360; X=1,Y=0: 11/360; X=1,Y=1: 11/90; candidate distribution P1 gives X=0,Y=0: 0/1; X=0,Y=1: 3/8; X=1,Y=0: 1/8; X=1,Y=1: 1/2.
At level Z=z4: candidate distribution P0 gives X=0,Y=0: 274/567; X=0,Y=1: 137/567; X=1,Y=0: 128/567; X=1,Y=1: 4/81; candidate distribution P1 gives X=0,Y=0: 2/21; X=0,Y=1: 1/21; X=1,Y=0: 4/21; X=1,Y=1: 2/3.
At level Z=z5: candidate distribution P0 gives X=0,Y=0: 14/81; X=0,Y=1: 40/81; X=1,Y=0: 10/81; X=1,Y=1: 17/81; candidate distribution P1 gives X=0,Y=0: 2/3; X=0,Y=1: 0/1; X=1,Y=0: 0/1; X=1,Y=1: 1/3.
A mixture of weight w draws from P0 and weight 1-w draws from P1, using the SAME rational weight w in every level, so within level z the joint is M_z = w*P0 + (1-w)*P1. Find the unique rational weight w with 0<w<1 such that X and Y are conditionally independent given Z (independent within every level simultaneously). Give w as a fraction a/b in lowest terms, e.g. 3/5.

**Answer:** 9/10

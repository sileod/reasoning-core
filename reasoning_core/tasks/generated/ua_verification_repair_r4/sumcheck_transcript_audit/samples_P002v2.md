## Level 0
### Example 1
**Prompt:**
```
A verifier checks a polynomial sumcheck transcript over the boolean hypercube in the prime field F_37. There are 2 variables and 2 rounds. The claimed total is 33. For each round, the polynomial f(t) must satisfy f(0)+f(1) == the claim entering that round, reduced mod 37; the next claim is f(r), also mod 37, where r is that round's challenge. Round 1 enters with claim = 33.
Round 1: claim entering = 33, f(t) = 8 + 17*t, challenge r = 4.
Round 2: claim entering = 2, f(t) = 17 + 8*t, challenge r = 1.
State the audit result exactly:
- "consistent" if every round satisfies f(0)+f(1) == claim (mod p);
- the 1-based round number of the first round that violates f(0)+f(1) == claim (mod p), if the transcription hides no '?'; or
- the single integer value of the hidden coefficient '?' that makes that round's consistency equation hold, if a '?' appears.
```
**Answer:**
```
2
```
### Example 2
**Prompt:**
```
A verifier checks a polynomial sumcheck transcript over the boolean hypercube in the prime field F_37. There are 2 variables and 2 rounds. The claimed total is 33. For each round, the polynomial f(t) must satisfy f(0)+f(1) == the claim entering that round, reduced mod 37; the next claim is f(r), also mod 37, where r is that round's challenge. Round 1 enters with claim = 33.
Round 1: claim entering = 33, f(t) = 8 + 17*t, challenge r = 4.
Round 2: claim entering = 2, f(t) = 17 + 8*t, challenge r = 1.
State the audit result exactly:
- "consistent" if every round satisfies f(0)+f(1) == claim (mod p);
- the 1-based round number of the first round that violates f(0)+f(1) == claim (mod p), if the transcription hides no '?'; or
- the single integer value of the hidden coefficient '?' that makes that round's consistency equation hold, if a '?' appears.
```
**Answer:**
```
2
```
## Level 2
### Example 1
**Prompt:**
```
A verifier checks a polynomial sumcheck transcript over the boolean hypercube in the prime field F_131. There are 4 variables and 4 rounds. The claimed total is 51. For each round, the polynomial f(t) must satisfy f(0)+f(1) == the claim entering that round, reduced mod 131; the next claim is f(r), also mod 131, where r is that round's challenge. Round 1 enters with claim = 51.
Round 1: claim entering = 51, f(t) = 23 + 6*t + 48*t^2 + 82*t^3, challenge r = 22.
Round 2: claim entering = 90, f(t) = 81 + 112*t + 10*t^2 + 68*t^3, challenge r = 88.
Round 3: claim entering = 25, f(t) = 122 + 70*t + 10*t^2 + 14*t^3, challenge r = 94.
Round 4: claim entering = 48, f(t) = 51 + 119*t + 5*t^2 + 6*t^3, challenge r = 116.
State the audit result exactly:
- "consistent" if every round satisfies f(0)+f(1) == claim (mod p);
- the 1-based round number of the first round that violates f(0)+f(1) == claim (mod p), if the transcription hides no '?'; or
- the single integer value of the hidden coefficient '?' that makes that round's consistency equation hold, if a '?' appears.
```
**Answer:**
```
3
```
### Example 2
**Prompt:**
```
A verifier checks a polynomial sumcheck transcript over the boolean hypercube in the prime field F_131. There are 4 variables and 4 rounds. The claimed total is 47. For each round, the polynomial f(t) must satisfy f(0)+f(1) == the claim entering that round, reduced mod 131; the next claim is f(r), also mod 131, where r is that round's challenge. Round 1 enters with claim = 47.
Round 1: claim entering = 47, f(t) = 13 + 118*t + 121*t^2 + 44*t^3, challenge r = 97.
Round 2: claim entering = 116, f(t) = 6 + 107*t + 90*t^2 + 38*t^3, challenge r = 32.
Round 3: claim entering = 120, f(t) = 83 + 79*t + 30*t^2 + 107*t^3, challenge r = 2.
Round 4: claim entering = 38, f(t) = ? + 28*t + 120*t^2 + 63*t^3, challenge r = 120.
State the audit result exactly:
- "consistent" if every round satisfies f(0)+f(1) == claim (mod p);
- the 1-based round number of the first round that violates f(0)+f(1) == claim (mod p), if the transcription hides no '?'; or
- the single integer value of the hidden coefficient '?' that makes that round's consistency equation hold, if a '?' appears.
```
**Answer:**
```
110
```
## Level 5
### Example 1
**Prompt:**
```
A verifier checks a polynomial sumcheck transcript over the boolean hypercube in the prime field F_1031. There are 6 variables and 6 rounds. The claimed total is 761. For each round, the polynomial f(t) must satisfy f(0)+f(1) == the claim entering that round, reduced mod 1031; the next claim is f(r), also mod 1031, where r is that round's challenge. Round 1 enters with claim = 761.
Round 1: claim entering = 761, f(t) = 401 + 459*t + 420*t^2 + 954*t^3 + 77*t^4 + 723*t^5, challenge r = 461.
Round 2: claim entering = 80, f(t) = 970 + 449*t + 337*t^2 + 755*t^3 + 884*t^4 + 201*t^5, challenge r = 781.
Round 3: claim entering = 138, f(t) = 946 + 667*t + 1011*t^2 + 628*t^3 + 685*t^4 + 410*t^5, challenge r = 318.
Round 4: claim entering = 353, f(t) = 305 + 37*t + 728*t^2 + 770*t^3 + 15*t^4 + 255*t^5, challenge r = 565.
Round 5: claim entering = 642, f(t) = 785 + 286*t + 192*t^2 + 20*t^3 + 88*t^4 + 548*t^5, challenge r = 789.
Round 6: claim entering = 662, f(t) = 918 + 962*t + 733*t^2 + 542*t^3 + 1002*t^4 + 742*t^5, challenge r = 277.
State the audit result exactly:
- "consistent" if every round satisfies f(0)+f(1) == claim (mod p);
- the 1-based round number of the first round that violates f(0)+f(1) == claim (mod p), if the transcription hides no '?'; or
- the single integer value of the hidden coefficient '?' that makes that round's consistency equation hold, if a '?' appears.
```
**Answer:**
```
1
```
### Example 2
**Prompt:**
```
A verifier checks a polynomial sumcheck transcript over the boolean hypercube in the prime field F_1031. There are 6 variables and 6 rounds. The claimed total is 812. For each round, the polynomial f(t) must satisfy f(0)+f(1) == the claim entering that round, reduced mod 1031; the next claim is f(r), also mod 1031, where r is that round's challenge. Round 1 enters with claim = 812.
Round 1: claim entering = 812, f(t) = 455 + 482*t + 405*t^2 + 312*t^3 + 552*t^4 + 213*t^5, challenge r = 248.
Round 2: claim entering = 571, f(t) = 1017 + 452*t + 286*t^2 + 931*t^3 + 900*t^4 + 92*t^5, challenge r = 513.
Round 3: claim entering = 412, f(t) = 49 + 836*t + 463*t^2 + 220*t^3 + 561*t^4 + 296*t^5, challenge r = 150.
Round 4: claim entering = 965, f(t) = 35 + 787*t + 791*t^2 + 217*t^3 + 143*t^4 + 1019*t^5, challenge r = 723.
Round 5: claim entering = 423, f(t) = 387 + 898*t + 991*t^2 + 736*t^3 + 773*t^4 + 375*t^5, challenge r = 352.
Round 6: claim entering = 381, f(t) = 685 + 469*t + ?*t^2 + 698*t^3 + 220*t^4 + 835*t^5, challenge r = 857.
State the audit result exactly:
- "consistent" if every round satisfies f(0)+f(1) == claim (mod p);
- the 1-based round number of the first round that violates f(0)+f(1) == claim (mod p), if the transcription hides no '?'; or
- the single integer value of the hidden coefficient '?' that makes that round's consistency equation hold, if a '?' appears.
```
**Answer:**
```
913
```

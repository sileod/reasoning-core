## Level 0
### Example 1
**Prompt:**
```
There are 2 goods numbered 0..1.
Bids: Bidder 0 wants goods {0} for value 4. Bidder 1 wants goods {0, 1} for value 3. Bidder 2 wants goods {0, 1} for value 2.
Bidder 0 is removed from the auction.
Winners are a subset of single-minded bidders whose bundles are pairwise disjoint (no two winners share a good), chosen to maximize total value. For each winner w, its pivotal (leave-one-out) VCG payment is the total value of the best allocation without w, minus the total value of the best allocation where the other winners still keep their own values. Compute the winning allocation and each winner's pivotal payment.
Answer as a list of (winner, payment) pairs, each written 'winner:payment', pairs separated by semicolons, ordered by winner id ascending. For example '2:13;5:4'.
```
**Answer:**
```
1:2
```
### Example 2
**Prompt:**
```
There are 2 goods numbered 0..1.
Bids: Bidder 0 wants goods {0, 1} for value 3. Bidder 1 wants goods {1} for value 4. Bidder 2 wants goods {0, 1} for value 4.
Bidder 0's value is changed to 4.
Winners are a subset of single-minded bidders whose bundles are pairwise disjoint (no two winners share a good), chosen to maximize total value. For each winner w, its pivotal (leave-one-out) VCG payment is the total value of the best allocation without w, minus the total value of the best allocation where the other winners still keep their own values. Compute the winning allocation and each winner's pivotal payment.
Answer as a list of (winner, payment) pairs, each written 'winner:payment', pairs separated by semicolons, ordered by winner id ascending. For example '2:13;5:4'.
```
**Answer:**
```
0:3
```
## Level 2
### Example 1
**Prompt:**
```
There are 2 goods numbered 0..1.
Bids: Bidder 0 wants goods {1} for value 9. Bidder 1 wants goods {0, 1} for value 1. Bidder 2 wants goods {0} for value 2. Bidder 3 wants goods {1} for value 5. Bidder 4 wants goods {0} for value 9.
No bid is edited; all bidders stay.
Winners are a subset of single-minded bidders whose bundles are pairwise disjoint (no two winners share a good), chosen to maximize total value. For each winner w, its pivotal (leave-one-out) VCG payment is the total value of the best allocation without w, minus the total value of the best allocation where the other winners still keep their own values. Compute the winning allocation and each winner's pivotal payment.
Answer as a list of (winner, payment) pairs, each written 'winner:payment', pairs separated by semicolons, ordered by winner id ascending. For example '2:13;5:4'.
```
**Answer:**
```
0:5;4:2
```
### Example 2
**Prompt:**
```
There are 4 goods numbered 0..3.
Bids: Bidder 0 wants goods {1, 3} for value 2. Bidder 1 wants goods {0, 2} for value 3. Bidder 2 wants goods {2, 3} for value 4. Bidder 3 wants goods {0, 1, 2, 3} for value 2. Bidder 4 wants goods {0, 1, 2} for value 4.
No bid is edited; all bidders stay.
Winners are a subset of single-minded bidders whose bundles are pairwise disjoint (no two winners share a good), chosen to maximize total value. For each winner w, its pivotal (leave-one-out) VCG payment is the total value of the best allocation without w, minus the total value of the best allocation where the other winners still keep their own values. Compute the winning allocation and each winner's pivotal payment.
Answer as a list of (winner, payment) pairs, each written 'winner:payment', pairs separated by semicolons, ordered by winner id ascending. For example '2:13;5:4'.
```
**Answer:**
```
0:1;1:2
```
## Level 5
### Example 1
**Prompt:**
```
There are 4 goods numbered 0..3.
Bids: Bidder 0 wants goods {0, 2, 3} for value 9. Bidder 1 wants goods {1, 3} for value 3. Bidder 2 wants goods {1, 2, 3} for value 9. Bidder 3 wants goods {2} for value 7. Bidder 4 wants goods {2} for value 9. Bidder 5 wants goods {0, 1, 2, 3} for value 10. Bidder 6 wants goods {0, 1, 2, 3} for value 12. Bidder 7 wants goods {0} for value 3.
No bid is edited; all bidders stay.
Winners are a subset of single-minded bidders whose bundles are pairwise disjoint (no two winners share a good), chosen to maximize total value. For each winner w, its pivotal (leave-one-out) VCG payment is the total value of the best allocation without w, minus the total value of the best allocation where the other winners still keep their own values. Compute the winning allocation and each winner's pivotal payment.
Answer as a list of (winner, payment) pairs, each written 'winner:payment', pairs separated by semicolons, ordered by winner id ascending. For example '2:13;5:4'.
```
**Answer:**
```
1:0;4:7;7:0
```
### Example 2
**Prompt:**
```
There are 2 goods numbered 0..1.
Bids: Bidder 0 wants goods {0, 1} for value 3. Bidder 1 wants goods {1} for value 9. Bidder 2 wants goods {1} for value 11. Bidder 3 wants goods {0} for value 9. Bidder 4 wants goods {1} for value 19. Bidder 5 wants goods {0, 1} for value 15. Bidder 6 wants goods {1} for value 7. Bidder 7 wants goods {0, 1} for value 3.
No bid is edited; all bidders stay.
Winners are a subset of single-minded bidders whose bundles are pairwise disjoint (no two winners share a good), chosen to maximize total value. For each winner w, its pivotal (leave-one-out) VCG payment is the total value of the best allocation without w, minus the total value of the best allocation where the other winners still keep their own values. Compute the winning allocation and each winner's pivotal payment.
Answer as a list of (winner, payment) pairs, each written 'winner:payment', pairs separated by semicolons, ordered by winner id ascending. For example '2:13;5:4'.
```
**Answer:**
```
3:0;4:11
```

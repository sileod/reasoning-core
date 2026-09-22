# Samples P008v1: ARIES crash recovery

## Level 0

### Example 1

PROMPT:
A database holds pages P1..P3. At the checkpoint the pages hold P1=1,P2=3,P3=1; the checkpoint recorded no dirty pages and no active transactions, so recovery may start analysis from scratch. The log after the checkpoint follows, in order, with increasing LSNs (a 'write P x = v' sets page x's value to v; a 'commit' ends that transaction). A crash occurs immediately after the last record.

L1 T1 write P3 = 3
L2 T2 write P3 = 1
L3 T1 write P2 = 2
L4 T1 commit

Run the ARIES protocol: analysis rebuilds the dirty-page table (a page's recLSN is its first write after the checkpoint) and the transaction table to find losers (transactions with no commit by the crash); redo re-applies every write from the oldest recLSN; undo rolls losers' writes back with compensation records. Report every page's final value after recovery, pages sorted by ID, then 'losers=' and the loser transaction IDs. Format: P1=...,P2=... losers=T..,T..

Answer: P1=1,P2=2,P3=3 losers=T2

### Example 2

PROMPT:
A database holds pages P1..P3. At the checkpoint the pages hold P1=3,P2=3,P3=4; the checkpoint recorded no dirty pages and no active transactions, so recovery may start analysis from scratch. The log after the checkpoint follows, in order, with increasing LSNs (a 'write P x = v' sets page x's value to v; a 'commit' ends that transaction). A crash occurs immediately after the last record.

L1 T1 write P1 = 1
L2 T2 write P2 = 2
L3 T1 write P3 = 0
L4 T1 commit

Run the ARIES protocol: analysis rebuilds the dirty-page table (a page's recLSN is its first write after the checkpoint) and the transaction table to find losers (transactions with no commit by the crash); redo re-applies every write from the oldest recLSN; undo rolls losers' writes back with compensation records. Report every page's final value after recovery, pages sorted by ID, then 'losers=' and the loser transaction IDs. Format: P1=...,P2=... losers=T..,T..

Answer: P1=1,P2=3,P3=0 losers=T2

## Level 2

### Example 1

PROMPT:
A database holds pages P1..P4. At the checkpoint the pages hold P1=0,P2=0,P3=2,P4=1; the checkpoint recorded no dirty pages and no active transactions, so recovery may start analysis from scratch. The log after the checkpoint follows, in order, with increasing LSNs (a 'write P x = v' sets page x's value to v; a 'commit' ends that transaction). A crash occurs immediately after the last record.

L1 T4 write P3 = 0
L2 T4 write P2 = 4
L3 T3 write P2 = 7
L4 T1 write P3 = 4
L5 T1 commit
L6 T2 write P1 = 2
L7 T2 write P4 = 6

Run the ARIES protocol: analysis rebuilds the dirty-page table (a page's recLSN is its first write after the checkpoint) and the transaction table to find losers (transactions with no commit by the crash); redo re-applies every write from the oldest recLSN; undo rolls losers' writes back with compensation records. Report every page's final value after recovery, pages sorted by ID, then 'losers=' and the loser transaction IDs. Format: P1=...,P2=... losers=T..,T..

Answer: P1=0,P2=0,P3=4,P4=1 losers=T2,T3,T4

### Example 2

PROMPT:
A database holds pages P1..P4. At the checkpoint the pages hold P1=4,P2=4,P3=3,P4=5; the checkpoint recorded no dirty pages and no active transactions, so recovery may start analysis from scratch. The log after the checkpoint follows, in order, with increasing LSNs (a 'write P x = v' sets page x's value to v; a 'commit' ends that transaction). A crash occurs immediately after the last record.

L1 T3 write P1 = 3
L2 T3 commit
L3 T1 write P4 = 6
L4 T4 write P1 = 6
L5 T2 write P2 = 3
L6 T1 write P1 = 4
L7 T1 commit
L8 T2 write P4 = 7
L9 T2 commit

Run the ARIES protocol: analysis rebuilds the dirty-page table (a page's recLSN is its first write after the checkpoint) and the transaction table to find losers (transactions with no commit by the crash); redo re-applies every write from the oldest recLSN; undo rolls losers' writes back with compensation records. Report every page's final value after recovery, pages sorted by ID, then 'losers=' and the loser transaction IDs. Format: P1=...,P2=... losers=T..,T..

Answer: P1=4,P2=3,P3=3,P4=7 losers=T4

## Level 5

### Example 1

PROMPT:
A database holds pages P1..P6. At the checkpoint the pages hold P1=4,P2=6,P3=0,P4=2,P5=7,P6=8; the checkpoint recorded no dirty pages and no active transactions, so recovery may start analysis from scratch. The log after the checkpoint follows, in order, with increasing LSNs (a 'write P x = v' sets page x's value to v; a 'commit' ends that transaction). A crash occurs immediately after the last record.

L1 T1 write P3 = 10
L2 T6 write P1 = 2
L3 T2 write P3 = 8
L4 T2 commit
L5 T3 write P6 = 10
L6 T5 write P1 = 10
L7 T5 write P2 = 5
L8 T4 write P2 = 4
L9 T6 write P6 = 2
L10 T3 write P4 = 1
L11 T3 commit
L12 T1 write P5 = 7
L13 T1 commit
L14 T4 write P4 = 3
L15 T4 commit

Run the ARIES protocol: analysis rebuilds the dirty-page table (a page's recLSN is its first write after the checkpoint) and the transaction table to find losers (transactions with no commit by the crash); redo re-applies every write from the oldest recLSN; undo rolls losers' writes back with compensation records. Report every page's final value after recovery, pages sorted by ID, then 'losers=' and the loser transaction IDs. Format: P1=...,P2=... losers=T..,T..

Answer: P1=4,P2=4,P3=8,P4=3,P5=7,P6=10 losers=T5,T6

### Example 2

PROMPT:
A database holds pages P1..P6. At the checkpoint the pages hold P1=3,P2=4,P3=8,P4=6,P5=6,P6=1; the checkpoint recorded no dirty pages and no active transactions, so recovery may start analysis from scratch. The log after the checkpoint follows, in order, with increasing LSNs (a 'write P x = v' sets page x's value to v; a 'commit' ends that transaction). A crash occurs immediately after the last record.

L1 T4 write P2 = 4
L2 T2 write P2 = 6
L3 T2 commit
L4 T5 write P1 = 4
L5 T6 write P3 = 4
L6 T4 write P3 = 9
L7 T4 commit
L8 T5 write P4 = 10
L9 T6 write P4 = 9
L10 T3 write P6 = 3
L11 T3 commit
L12 T1 write P2 = 0
L13 T1 commit

Run the ARIES protocol: analysis rebuilds the dirty-page table (a page's recLSN is its first write after the checkpoint) and the transaction table to find losers (transactions with no commit by the crash); redo re-applies every write from the oldest recLSN; undo rolls losers' writes back with compensation records. Report every page's final value after recovery, pages sorted by ID, then 'losers=' and the loser transaction IDs. Format: P1=...,P2=... losers=T..,T..

Answer: P1=3,P2=0,P3=9,P4=6,P5=6,P6=3 losers=T5,T6

## Level 0

In a replicated consensus log with 3 nodes, each node tracks the highest log index it has acknowledged. A log entry at index k is committed once it has been acknowledged by at least 2 nodes (a strict majority of 3). The committed index is the highest index k such that at least 2 nodes have acknowledged every entry from index 1 up to and including index k. Given:
node 0 has committed logs up to and including index 2
node 1 has committed logs up to and including index 2
node 2 has committed logs up to and including index 4
What is the highest committed log index? The answer is one integer.

Answer: 2

In a replicated consensus log with 3 nodes, each node tracks the highest log index it has acknowledged. A log entry at index k is committed once it has been acknowledged by at least 2 nodes (a strict majority of 3). The committed index is the highest index k such that at least 2 nodes have acknowledged every entry from index 1 up to and including index k. Given:
node 0 has committed logs up to and including index 1
node 1 has committed logs up to and including index 1
node 2 has committed logs up to and including index 1
What is the highest committed log index? The answer is one integer.

Answer: 1

## Level 2

In a replicated consensus log with 5 nodes, each node tracks the highest log index it has acknowledged. A log entry at index k is committed once it has been acknowledged by at least 3 nodes (a strict majority of 5). The committed index is the highest index k such that at least 3 nodes have acknowledged every entry from index 1 up to and including index k. Given:
node 0 has committed logs up to and including index 1
node 1 has committed logs up to and including index 4
node 2 has committed logs up to and including index 5
node 3 has committed logs up to and including index 6
node 4 has committed logs up to and including index 6
What is the highest committed log index? The answer is one integer.

Answer: 5

In a replicated consensus log with 5 nodes, each node tracks the highest log index it has acknowledged. A log entry at index k is committed once it has been acknowledged by at least 3 nodes (a strict majority of 5). The committed index is the highest index k such that at least 3 nodes have acknowledged every entry from index 1 up to and including index k. Given:
node 0 has committed logs up to and including index 2
node 1 has committed logs up to and including index 4
node 2 has committed logs up to and including index 4
node 3 has committed logs up to and including index 6
node 4 has committed logs up to and including index 6
What is the highest committed log index? The answer is one integer.

Answer: 4

## Level 5

In a replicated consensus log with 7 nodes, each node tracks the highest log index it has acknowledged. A log entry at index k is committed once it has been acknowledged by at least 4 nodes (a strict majority of 7). The committed index is the highest index k such that at least 4 nodes have acknowledged every entry from index 1 up to and including index k. Given:
node 0 has committed logs up to and including index 1
node 1 has committed logs up to and including index 2
node 2 has committed logs up to and including index 4
node 3 has committed logs up to and including index 6
node 4 has committed logs up to and including index 6
node 5 has committed logs up to and including index 6
node 6 has committed logs up to and including index 9
What is the highest committed log index? The answer is one integer.

Answer: 6

In a replicated consensus log with 7 nodes, each node tracks the highest log index it has acknowledged. A log entry at index k is committed once it has been acknowledged by at least 4 nodes (a strict majority of 7). The committed index is the highest index k such that at least 4 nodes have acknowledged every entry from index 1 up to and including index k. Given:
node 0 has committed logs up to and including index 1
node 1 has committed logs up to and including index 1
node 2 has committed logs up to and including index 4
node 3 has committed logs up to and including index 4
node 4 has committed logs up to and including index 4
node 5 has committed logs up to and including index 7
node 6 has committed logs up to and including index 7
What is the highest committed log index? The answer is one integer.

Answer: 4

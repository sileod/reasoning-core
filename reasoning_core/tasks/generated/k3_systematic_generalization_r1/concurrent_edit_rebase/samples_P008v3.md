# ConcurrentEditRebase samples (P008v3)

## Level 0

You are rebasing one concurrent edit onto another over an indexed buffer.

A buffer has N items with indices 0..N-1. An edit is one of:
  - "insert k before index i": inserts k new items immediately before the current item i (i=N appends at the end);
  - "delete [a, b)": removes the current items a, a+1, ..., b-1.

Two edits A and B are each specified against the ORIGINAL buffer, before either is applied. Edit A has priority and is applied first. Rebase B onto A: produce the edit Bp against the post-A buffer so that applying A and then Bp yields the same document as both edits taking effect.

Tie-break: when B inserts at the exact same position as A's insert, place Bp's insertion after A's newly inserted block.

Report Bp in exactly one of these forms:
  - "insert P"       (the new insertion position P)
  - "delete A B"     (the new range [a, b))
  - "no-op"          (B has no surviving effect after A)

buffer length N = 4
base edit A (priority, applied first): delete [3, 4)
incoming edit B (to rebase onto A): delete [3, 4)

What is the rebased edit Bp?

Answer: no-op

You are rebasing one concurrent edit onto another over an indexed buffer.

A buffer has N items with indices 0..N-1. An edit is one of:
  - "insert k before index i": inserts k new items immediately before the current item i (i=N appends at the end);
  - "delete [a, b)": removes the current items a, a+1, ..., b-1.

Two edits A and B are each specified against the ORIGINAL buffer, before either is applied. Edit A has priority and is applied first. Rebase B onto A: produce the edit Bp against the post-A buffer so that applying A and then Bp yields the same document as both edits taking effect.

Tie-break: when B inserts at the exact same position as A's insert, place Bp's insertion after A's newly inserted block.

Report Bp in exactly one of these forms:
  - "insert P"       (the new insertion position P)
  - "delete A B"     (the new range [a, b))
  - "no-op"          (B has no surviving effect after A)

buffer length N = 5
base edit A (priority, applied first): insert 1 before index 3
incoming edit B (to rebase onto A): insert 1 before index 5

What is the rebased edit Bp?

Answer: insert 6

## Level 2

You are rebasing one concurrent edit onto another over an indexed buffer.

A buffer has N items with indices 0..N-1. An edit is one of:
  - "insert k before index i": inserts k new items immediately before the current item i (i=N appends at the end);
  - "delete [a, b)": removes the current items a, a+1, ..., b-1.

Two edits A and B are each specified against the ORIGINAL buffer, before either is applied. Edit A has priority and is applied first. Rebase B onto A: produce the edit Bp against the post-A buffer so that applying A and then Bp yields the same document as both edits taking effect.

Tie-break: when B inserts at the exact same position as A's insert, place Bp's insertion after A's newly inserted block.

Report Bp in exactly one of these forms:
  - "insert P"       (the new insertion position P)
  - "delete A B"     (the new range [a, b))
  - "no-op"          (B has no surviving effect after A)

buffer length N = 8
base edit A (priority, applied first): delete [4, 8)
incoming edit B (to rebase onto A): delete [5, 8)

What is the rebased edit Bp?

Answer: no-op

You are rebasing one concurrent edit onto another over an indexed buffer.

A buffer has N items with indices 0..N-1. An edit is one of:
  - "insert k before index i": inserts k new items immediately before the current item i (i=N appends at the end);
  - "delete [a, b)": removes the current items a, a+1, ..., b-1.

Two edits A and B are each specified against the ORIGINAL buffer, before either is applied. Edit A has priority and is applied first. Rebase B onto A: produce the edit Bp against the post-A buffer so that applying A and then Bp yields the same document as both edits taking effect.

Tie-break: when B inserts at the exact same position as A's insert, place Bp's insertion after A's newly inserted block.

Report Bp in exactly one of these forms:
  - "insert P"       (the new insertion position P)
  - "delete A B"     (the new range [a, b))
  - "no-op"          (B has no surviving effect after A)

buffer length N = 8
base edit A (priority, applied first): delete [7, 8)
incoming edit B (to rebase onto A): delete [3, 6)

What is the rebased edit Bp?

Answer: delete 3 6

## Level 5

You are rebasing one concurrent edit onto another over an indexed buffer.

A buffer has N items with indices 0..N-1. An edit is one of:
  - "insert k before index i": inserts k new items immediately before the current item i (i=N appends at the end);
  - "delete [a, b)": removes the current items a, a+1, ..., b-1.

Two edits A and B are each specified against the ORIGINAL buffer, before either is applied. Edit A has priority and is applied first. Rebase B onto A: produce the edit Bp against the post-A buffer so that applying A and then Bp yields the same document as both edits taking effect.

Tie-break: when B inserts at the exact same position as A's insert, place Bp's insertion after A's newly inserted block.

Report Bp in exactly one of these forms:
  - "insert P"       (the new insertion position P)
  - "delete A B"     (the new range [a, b))
  - "no-op"          (B has no surviving effect after A)

buffer length N = 11
base edit A (priority, applied first): delete [7, 9)
incoming edit B (to rebase onto A): delete [2, 9)

What is the rebased edit Bp?

Answer: delete 2 7

You are rebasing one concurrent edit onto another over an indexed buffer.

A buffer has N items with indices 0..N-1. An edit is one of:
  - "insert k before index i": inserts k new items immediately before the current item i (i=N appends at the end);
  - "delete [a, b)": removes the current items a, a+1, ..., b-1.

Two edits A and B are each specified against the ORIGINAL buffer, before either is applied. Edit A has priority and is applied first. Rebase B onto A: produce the edit Bp against the post-A buffer so that applying A and then Bp yields the same document as both edits taking effect.

Tie-break: when B inserts at the exact same position as A's insert, place Bp's insertion after A's newly inserted block.

Report Bp in exactly one of these forms:
  - "insert P"       (the new insertion position P)
  - "delete A B"     (the new range [a, b))
  - "no-op"          (B has no surviving effect after A)

buffer length N = 15
base edit A (priority, applied first): insert 1 before index 3
incoming edit B (to rebase onto A): delete [9, 10)

What is the rebased edit Bp?

Answer: delete 10 11

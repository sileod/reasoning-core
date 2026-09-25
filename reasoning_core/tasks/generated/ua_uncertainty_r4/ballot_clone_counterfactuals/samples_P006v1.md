# Samples P006v1

## Level 0

**Prompt:**

    An election uses instant-runoff voting (IRV): repeatedly eliminate the candidate with the fewest first-choice votes among those still running, retallying each eliminated candidate's second (then third, ...) choice on that ballot; ties for fewest first-choice votes are broken by eliminating the alphabetically earliest label. Stop when one candidate remains.
    The candidates are A, B, C1,C2 over original identities A, B, C.
    - C is a clone block with two clones C1 and C2
    In every ballot, the two clones of a clone block are placed in two adjacent ranks, but the internal order of the two clones within a block may differ from voter to voter. We range over every possible assignment of internal clone orders across voters and blocks.
    The ballots (each voter's full ranking, highest rank first) are (A > C > B), (B > C > A), (A > B > C).
    After a clone is elected we collapse its identity to its original. Determine the set of ORIGINAL candidate labels that can end up as the winner under some assignment of the internal clone orders. Answer as the sorted hyphen-joined labels, e.g. 'A-B' or 'NONE'.

**Answer:**

    A

**Prompt:**

    An election uses instant-runoff voting (IRV): repeatedly eliminate the candidate with the fewest first-choice votes among those still running, retallying each eliminated candidate's second (then third, ...) choice on that ballot; ties for fewest first-choice votes are broken by eliminating the alphabetically earliest label. Stop when one candidate remains.
    The candidates are A, B, C1,C2 over original identities A, B, C.
    - C is a clone block with two clones C1 and C2
    In every ballot, the two clones of a clone block are placed in two adjacent ranks, but the internal order of the two clones within a block may differ from voter to voter. We range over every possible assignment of internal clone orders across voters and blocks.
    The ballots (each voter's full ranking, highest rank first) are (A > B > C), (B > A > C), (C > B > A).
    After a clone is elected we collapse its identity to its original. Determine the set of ORIGINAL candidate labels that can end up as the winner under some assignment of the internal clone orders. Answer as the sorted hyphen-joined labels, e.g. 'A-B' or 'NONE'.

**Answer:**

    B

## Level 2

**Prompt:**

    An election uses instant-runoff voting (IRV): repeatedly eliminate the candidate with the fewest first-choice votes among those still running, retallying each eliminated candidate's second (then third, ...) choice on that ballot; ties for fewest first-choice votes are broken by eliminating the alphabetically earliest label. Stop when one candidate remains.
    The candidates are A, B1,B2, C1,C2, D over original identities A, B, C, D.
    - C is a clone block with two clones C1 and C2
    - B is a clone block with two clones B1 and B2
    In every ballot, the two clones of a clone block are placed in two adjacent ranks, but the internal order of the two clones within a block may differ from voter to voter. We range over every possible assignment of internal clone orders across voters and blocks.
    The ballots (each voter's full ranking, highest rank first) are (A > C > B > D), (B > A > C > D), (B > D > C > A), (A > D > C > B).
    After a clone is elected we collapse its identity to its original. Determine the set of ORIGINAL candidate labels that can end up as the winner under some assignment of the internal clone orders. Answer as the sorted hyphen-joined labels, e.g. 'A-B' or 'NONE'.

**Answer:**

    B

**Prompt:**

    An election uses instant-runoff voting (IRV): repeatedly eliminate the candidate with the fewest first-choice votes among those still running, retallying each eliminated candidate's second (then third, ...) choice on that ballot; ties for fewest first-choice votes are broken by eliminating the alphabetically earliest label. Stop when one candidate remains.
    The candidates are A1,A2, B1,B2, C, D over original identities A, B, C, D.
    - A is a clone block with two clones A1 and A2
    - B is a clone block with two clones B1 and B2
    In every ballot, the two clones of a clone block are placed in two adjacent ranks, but the internal order of the two clones within a block may differ from voter to voter. We range over every possible assignment of internal clone orders across voters and blocks.
    The ballots (each voter's full ranking, highest rank first) are (C > B > A > D), (A > C > B > D), (D > B > C > A), (A > D > B > C).
    After a clone is elected we collapse its identity to its original. Determine the set of ORIGINAL candidate labels that can end up as the winner under some assignment of the internal clone orders. Answer as the sorted hyphen-joined labels, e.g. 'A-B' or 'NONE'.

**Answer:**

    A

## Level 5

**Prompt:**

    An election uses instant-runoff voting (IRV): repeatedly eliminate the candidate with the fewest first-choice votes among those still running, retallying each eliminated candidate's second (then third, ...) choice on that ballot; ties for fewest first-choice votes are broken by eliminating the alphabetically earliest label. Stop when one candidate remains.
    The candidates are A1,A2, B, C, D1,D2, E over original identities A, B, C, D, E.
    - A is a clone block with two clones A1 and A2
    - D is a clone block with two clones D1 and D2
    In every ballot, the two clones of a clone block are placed in two adjacent ranks, but the internal order of the two clones within a block may differ from voter to voter. We range over every possible assignment of internal clone orders across voters and blocks.
    The ballots (each voter's full ranking, highest rank first) are (C > E > B > D > A), (E > B > A > C > D), (E > B > C > A > D), (E > B > A > C > D), (C > E > D > A > B).
    After a clone is elected we collapse its identity to its original. Determine the set of ORIGINAL candidate labels that can end up as the winner under some assignment of the internal clone orders. Answer as the sorted hyphen-joined labels, e.g. 'A-B' or 'NONE'.

**Answer:**

    E

**Prompt:**

    An election uses instant-runoff voting (IRV): repeatedly eliminate the candidate with the fewest first-choice votes among those still running, retallying each eliminated candidate's second (then third, ...) choice on that ballot; ties for fewest first-choice votes are broken by eliminating the alphabetically earliest label. Stop when one candidate remains.
    The candidates are A, B, C1,C2, D, E1,E2 over original identities A, B, C, D, E.
    - E is a clone block with two clones E1 and E2
    - C is a clone block with two clones C1 and C2
    In every ballot, the two clones of a clone block are placed in two adjacent ranks, but the internal order of the two clones within a block may differ from voter to voter. We range over every possible assignment of internal clone orders across voters and blocks.
    The ballots (each voter's full ranking, highest rank first) are (C > A > D > E > B), (B > A > E > C > D), (E > A > B > C > D), (D > B > E > C > A), (C > D > A > B > E).
    After a clone is elected we collapse its identity to its original. Determine the set of ORIGINAL candidate labels that can end up as the winner under some assignment of the internal clone orders. Answer as the sorted hyphen-joined labels, e.g. 'A-B' or 'NONE'.

**Answer:**

    E


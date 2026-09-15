# Samples: window_function_execution

Random seed: 2342189148

## Level 0

### Prompt

A table has one column for each attribute below, ordered top to bottom by row.
Columns: sales, rank, q
     sales |     rank |        q
        44 |       60 |       42
        58 |       10 |       28
        40 |        5 |       45
        66 |       30 |       82
        95 |       93 |       33
        51 |       67 |       89

Consider the rank (smallest value ranks 1, ties share the same rank) computed on the column 'sales' for row 4 (the 4th row).
Answer 'yes' if that computed value equals exactly 5 and 'no' otherwise.
Your answer is exactly one word: 'yes' for a match, 'no' for a mismatch.

### Answer

yes

### Prompt

A table has one column for each attribute below, ordered top to bottom by row.
Columns: q, sales, cnt
         q |    sales |      cnt
        92 |       70 |       80
         2 |       97 |       59
        86 |       74 |        5
        34 |        2 |       80
         7 |       60 |       17
        25 |       68 |        3

Consider the rank (smallest value ranks 1, ties share the same rank) computed on the column 'q' for row 3 (the 3rd row).
Answer 'yes' if that computed value equals exactly 6 and 'no' otherwise.
Your answer is exactly one word: 'yes' for a match, 'no' for a mismatch.

### Answer

no

## Level 2

### Prompt

A table has one column for each attribute below, ordered top to bottom by row.
Columns: price, val, amount, score, rank
     price |      val |   amount |    score |     rank
        78 |       26 |       71 |       99 |       73
        56 |       35 |       53 |       38 |       13
        39 |       65 |       85 |       47 |       41
        40 |       29 |       33 |       74 |       41
        36 |       22 |       10 |       56 |       31
         8 |       84 |       40 |       44 |       25
        54 |       53 |        0 |       58 |       51
        99 |       53 |       16 |       22 |       61
         4 |       12 |       32 |        1 |       15
        59 |       88 |       49 |       23 |       39

Consider the running total (ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) computed on the column 'amount' for row 10 (the 10th row).
Answer 'yes' if that computed value equals exactly 390 and 'no' otherwise.
Your answer is exactly one word: 'yes' for a match, 'no' for a mismatch.

### Answer

no

### Prompt

A table has one column for each attribute below, ordered top to bottom by row.
Columns: id, n, price, cnt, score
        id |        n |    price |      cnt |    score
        25 |       53 |       58 |       60 |       52
        28 |       99 |       87 |       52 |       99
        87 |       20 |       95 |       15 |       28
        85 |       11 |       60 |       53 |       77
        49 |       69 |       96 |       65 |       61
        34 |       15 |       27 |       44 |        3
        91 |        6 |       37 |        3 |       90
        16 |       16 |      100 |       32 |       50
        39 |       54 |       91 |       97 |       26
        72 |       16 |       77 |       61 |        2

Consider the rank (smallest value ranks 1, ties share the same rank) computed on the column 'price' for row 2 (the 2nd row).
Answer 'yes' if that computed value equals exactly 3 and 'no' otherwise.
Your answer is exactly one word: 'yes' for a match, 'no' for a mismatch.

### Answer

no

## Level 5

### Prompt

A table has one column for each attribute below, ordered top to bottom by row.
Columns: rank, amount, n, score, id, val, sales, q
      rank |   amount |        n |    score |       id |      val |    sales |        q
       100 |       30 |       10 |       48 |       40 |        9 |       39 |       80
        40 |       74 |        4 |       50 |       53 |       67 |       11 |       83
        45 |       11 |       87 |       87 |       14 |       54 |       55 |       62
        77 |       59 |       84 |       10 |        3 |       72 |        5 |       94
        68 |       36 |       34 |       67 |       73 |       38 |       92 |       37
        62 |       64 |       94 |       43 |       47 |       17 |       20 |       83
        80 |       40 |       59 |       53 |        9 |       91 |        7 |        5
        26 |       86 |       87 |       87 |       18 |       48 |       28 |       68
        53 |       18 |       82 |       74 |       16 |        5 |       69 |       20
        80 |       84 |       91 |        3 |       78 |        1 |       89 |       95
        12 |       84 |       23 |       77 |       76 |       99 |       28 |       58
        99 |       30 |       12 |       77 |       95 |       43 |       82 |       92
        91 |       92 |       74 |       92 |       67 |       83 |       26 |       98
        94 |       16 |       48 |       83 |       77 |       40 |       77 |       14
        20 |       37 |       66 |       32 |       90 |       30 |        8 |       59
        44 |       28 |       12 |       99 |       51 |       73 |       73 |       69

Consider the running average over all rows up to and including the current row computed on the column 'score' for row 10 (the 10th row).
Answer 'yes' if that computed value equals exactly 56.2 and 'no' otherwise.
Your answer is exactly one word: 'yes' for a match, 'no' for a mismatch.

### Answer

no

### Prompt

A table has one column for each attribute below, ordered top to bottom by row.
Columns: q, val, price, amount, id, n, cnt, score
         q |      val |    price |   amount |       id |        n |      cnt |    score
        77 |        9 |       85 |       46 |       43 |       57 |        6 |        5
        37 |       80 |       61 |       16 |       87 |       94 |       45 |       88
        70 |       76 |       53 |       99 |       11 |       62 |       76 |       66
        94 |       49 |       98 |        2 |       77 |       81 |       19 |       62
        11 |       76 |       47 |       40 |       15 |       80 |       77 |       35
        57 |       55 |       38 |       19 |       73 |       96 |       50 |       35
        75 |      100 |       22 |       79 |        3 |       80 |       39 |       21
        60 |       81 |        3 |       74 |       45 |       84 |       35 |       30
        13 |       98 |       40 |       29 |        5 |       13 |       80 |       16
        80 |       63 |       24 |       64 |       90 |       89 |       90 |        1
        48 |       17 |        0 |       75 |       92 |       73 |       67 |       97
        34 |        6 |       67 |       33 |       87 |       48 |       87 |       86
         3 |        1 |       96 |       77 |       26 |       56 |       17 |       33
        21 |       77 |       79 |       33 |       49 |       17 |       41 |       78
        15 |       12 |       71 |       27 |       40 |       14 |      100 |       62
         3 |       94 |       32 |       39 |       27 |       51 |      100 |       13

Consider the 1-lead value, taken from the immediately following row computed on the column 'n' for row 7 (the 7th row).
Answer 'yes' if that computed value equals exactly 91 and 'no' otherwise.
Your answer is exactly one word: 'yes' for a match, 'no' for a mismatch.

### Answer

no


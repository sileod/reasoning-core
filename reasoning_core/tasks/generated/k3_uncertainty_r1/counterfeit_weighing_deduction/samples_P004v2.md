# samples_P004v2 - counterfeit_weighing_deduction

## Level 0

### Example 1

**Prompt:**

There are 4 coins, numbered 0 to 3. Exactly one coin is counterfeit: it weighs either slightly more or slightly less than a normal coin. We ran balance-scale weighings comparing the coins on the left pan against the coins on the right pan; 'L' means the left pan was heavier, 'R' means the right pan was heavier, and '=' means they balanced.
Weighings recorded:
  Weighing 0: left pan [0, 1], right pan [2, 3] -> L
  Weighing 1: left pan [3], right pan [0, 1, 2] -> L
Give every hypothesis (coin, sense) that is consistent with ALL recorded weighings. Write each candidate as 'cH' for coin c heavier or 'cL' for coin c lighter, separated by spaces, sorted by coin number then sense with 'H' before 'L'. If only one hypothesis remains, output just that one.

**Answer:**

`2L`

### Example 2

**Prompt:**

There are 4 coins, numbered 0 to 3. Exactly one coin is counterfeit: it weighs either slightly more or slightly less than a normal coin. We ran balance-scale weighings comparing the coins on the left pan against the coins on the right pan; 'L' means the left pan was heavier, 'R' means the right pan was heavier, and '=' means they balanced.
Weighings recorded:
  Weighing 0: left pan [2], right pan [0, 1, 3] -> L
  Weighing 1: left pan [1, 3], right pan [0, 2] -> L
Give every hypothesis (coin, sense) that is consistent with ALL recorded weighings. Write each candidate as 'cH' for coin c heavier or 'cL' for coin c lighter, separated by spaces, sorted by coin number then sense with 'H' before 'L'. If only one hypothesis remains, output just that one.

**Answer:**

`0L`

## Level 2

### Example 1

**Prompt:**

There are 6 coins, numbered 0 to 5. Exactly one coin is counterfeit: it weighs either slightly more or slightly less than a normal coin. We ran balance-scale weighings comparing the coins on the left pan against the coins on the right pan; 'L' means the left pan was heavier, 'R' means the right pan was heavier, and '=' means they balanced.
Weighings recorded:
  Weighing 0: left pan [4, 5], right pan [0, 1, 2] -> R
  Weighing 1: left pan [0, 1, 2, 3, 5], right pan [4] -> L
  Weighing 2: left pan [0, 1, 3], right pan [2, 4, 5] -> L
Give every hypothesis (coin, sense) that is consistent with ALL recorded weighings. Write each candidate as 'cH' for coin c heavier or 'cL' for coin c lighter, separated by spaces, sorted by coin number then sense with 'H' before 'L'. If only one hypothesis remains, output just that one.

**Answer:**

`0H 1H 4L`

### Example 2

**Prompt:**

There are 6 coins, numbered 0 to 5. Exactly one coin is counterfeit: it weighs either slightly more or slightly less than a normal coin. We ran balance-scale weighings comparing the coins on the left pan against the coins on the right pan; 'L' means the left pan was heavier, 'R' means the right pan was heavier, and '=' means they balanced.
Weighings recorded:
  Weighing 0: left pan [0, 1, 3], right pan [4] -> =
  Weighing 1: left pan [3], right pan [4] -> =
  Weighing 2: left pan [0, 1, 2, 4, 5], right pan [3] -> L
Give every hypothesis (coin, sense) that is consistent with ALL recorded weighings. Write each candidate as 'cH' for coin c heavier or 'cL' for coin c lighter, separated by spaces, sorted by coin number then sense with 'H' before 'L'. If only one hypothesis remains, output just that one.

**Answer:**

`2H 5H`

## Level 5

### Example 1

**Prompt:**

There are 9 coins, numbered 0 to 8. Exactly one coin is counterfeit: it weighs either slightly more or slightly less than a normal coin. We ran balance-scale weighings comparing the coins on the left pan against the coins on the right pan; 'L' means the left pan was heavier, 'R' means the right pan was heavier, and '=' means they balanced.
Weighings recorded:
  Weighing 0: left pan [0, 1, 2, 3, 5, 6, 7, 8], right pan [4] -> R
  Weighing 1: left pan [1, 3], right pan [2, 4, 6, 7, 8] -> R
  Weighing 2: left pan [1, 2, 3, 4, 7, 8], right pan [5] -> R
  Weighing 3: left pan [2, 4, 5], right pan [0, 1, 3, 6, 7, 8] -> L
Give every hypothesis (coin, sense) that is consistent with ALL recorded weighings. Write each candidate as 'cH' for coin c heavier or 'cL' for coin c lighter, separated by spaces, sorted by coin number then sense with 'H' before 'L'. If only one hypothesis remains, output just that one.

**Answer:**

`1L 3L`

### Example 2

**Prompt:**

There are 9 coins, numbered 0 to 8. Exactly one coin is counterfeit: it weighs either slightly more or slightly less than a normal coin. We ran balance-scale weighings comparing the coins on the left pan against the coins on the right pan; 'L' means the left pan was heavier, 'R' means the right pan was heavier, and '=' means they balanced.
Weighings recorded:
  Weighing 0: left pan [3], right pan [0, 1, 4, 6] -> =
  Weighing 1: left pan [5], right pan [1, 7] -> =
  Weighing 2: left pan [1, 4, 6, 7, 8], right pan [0, 3] -> =
  Weighing 3: left pan [6, 7], right pan [2, 4, 8] -> L
Give every hypothesis (coin, sense) that is consistent with ALL recorded weighings. Write each candidate as 'cH' for coin c heavier or 'cL' for coin c lighter, separated by spaces, sorted by coin number then sense with 'H' before 'L'. If only one hypothesis remains, output just that one.

**Answer:**

`2L`

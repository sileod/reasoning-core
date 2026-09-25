## Level 0
### Example 1
**Prompt**

```
The table below is a multiplicative row-by-column weight table: every entry equals a row value times a column value, so the interaction contrast across any 2 rows and 2 columns is invariant (equal to 1). One single entry was corrupted: it alone was multiplied by an unknown positive integer factor, breaking that invariance, while every other entry kept its row-value-times-column-value form. The uncorrupted entry at row 2, column 1 still holds its true multiplicative value, and the corrupted entry is at row 0, column 2.

The interaction contrast of the 2x2 block spanned by the two rows 2 and 0 and the two columns 1 and 2 equals the corrupted entry's multiplier: this is the positive integer you are looking for.

Table (entry value = row value * column value):
15 9 12
20 12 8
15 9 6

Compute the 2x2 interaction contrast (the cross-ratio (12 * 9) / (9 * 6)), its value is the smallest positive integer (a prime between 2 and 97) that restores the table's multiplicative structure. Answer with that prime integer alone.
```

**Answer**

2

### Example 2
**Prompt**

```
The table below is a multiplicative row-by-column weight table: every entry equals a row value times a column value, so the interaction contrast across any 2 rows and 2 columns is invariant (equal to 1). One single entry was corrupted: it alone was multiplied by an unknown positive integer factor, breaking that invariance, while every other entry kept its row-value-times-column-value form. The uncorrupted entry at row 0, column 2 still holds its true multiplicative value, and the corrupted entry is at row 1, column 0.

The interaction contrast of the 2x2 block spanned by the two rows 0 and 1 and the two columns 2 and 0 equals the corrupted entry's multiplier: this is the positive integer you are looking for.

Table (entry value = row value * column value):
20 12 12
50 6 6
20 12 12

Compute the 2x2 interaction contrast (the cross-ratio (50 * 12) / (6 * 20)), its value is the smallest positive integer (a prime between 2 and 97) that restores the table's multiplicative structure. Answer with that prime integer alone.
```

**Answer**

5

## Level 2
### Example 1
**Prompt**

```
The table below is a multiplicative row-by-column weight table: every entry equals a row value times a column value, so the interaction contrast across any 2 rows and 2 columns is invariant (equal to 1). One single entry was corrupted: it alone was multiplied by an unknown positive integer factor, breaking that invariance, while every other entry kept its row-value-times-column-value form. The uncorrupted entry at row 4, column 2 still holds its true multiplicative value, and the corrupted entry is at row 3, column 0.

The interaction contrast of the 2x2 block spanned by the two rows 4 and 3 and the two columns 2 and 0 equals the corrupted entry's multiplier: this is the positive integer you are looking for.

Table (entry value = row value * column value):
33 110 55 22 77
24 80 40 16 56
12 40 20 8 28
66 20 10 4 14
9 30 15 6 21

Compute the 2x2 interaction contrast (the cross-ratio (66 * 15) / (10 * 9)), its value is the smallest positive integer (a prime between 2 and 97) that restores the table's multiplicative structure. Answer with that prime integer alone.
```

**Answer**

11

### Example 2
**Prompt**

```
The table below is a multiplicative row-by-column weight table: every entry equals a row value times a column value, so the interaction contrast across any 2 rows and 2 columns is invariant (equal to 1). One single entry was corrupted: it alone was multiplied by an unknown positive integer factor, breaking that invariance, while every other entry kept its row-value-times-column-value form. The uncorrupted entry at row 0, column 3 still holds its true multiplicative value, and the corrupted entry is at row 3, column 0.

The interaction contrast of the 2x2 block spanned by the two rows 0 and 3 and the two columns 3 and 0 equals the corrupted entry's multiplier: this is the positive integer you are looking for.

Table (entry value = row value * column value):
24 30 27 21 9
88 110 99 77 33
48 60 54 42 18
72 30 27 21 9
64 80 72 56 24

Compute the 2x2 interaction contrast (the cross-ratio (72 * 21) / (21 * 24)), its value is the smallest positive integer (a prime between 2 and 97) that restores the table's multiplicative structure. Answer with that prime integer alone.
```

**Answer**

3

## Level 5
### Example 1
**Prompt**

```
The table below is a multiplicative row-by-column weight table: every entry equals a row value times a column value, so the interaction contrast across any 2 rows and 2 columns is invariant (equal to 1). One single entry was corrupted: it alone was multiplied by an unknown positive integer factor, breaking that invariance, while every other entry kept its row-value-times-column-value form. The uncorrupted entry at row 3, column 3 still holds its true multiplicative value, and the corrupted entry is at row 2, column 0.

The interaction contrast of the 2x2 block spanned by the two rows 3 and 2 and the two columns 3 and 0 equals the corrupted entry's multiplier: this is the positive integer you are looking for.

Table (entry value = row value * column value):
30 70 190 160 200 80 80 160
57 133 361 304 380 152 152 304
570 70 190 160 200 80 80 160
36 84 228 192 240 96 96 192
36 84 228 192 240 96 96 192
42 98 266 224 280 112 112 224
57 133 361 304 380 152 152 304
27 63 171 144 180 72 72 144

Compute the 2x2 interaction contrast (the cross-ratio (570 * 192) / (160 * 36)), its value is the smallest positive integer (a prime between 2 and 97) that restores the table's multiplicative structure. Answer with that prime integer alone.
```

**Answer**

19

### Example 2
**Prompt**

```
The table below is a multiplicative row-by-column weight table: every entry equals a row value times a column value, so the interaction contrast across any 2 rows and 2 columns is invariant (equal to 1). One single entry was corrupted: it alone was multiplied by an unknown positive integer factor, breaking that invariance, while every other entry kept its row-value-times-column-value form. The uncorrupted entry at row 4, column 0 still holds its true multiplicative value, and the corrupted entry is at row 5, column 6.

The interaction contrast of the 2x2 block spanned by the two rows 4 and 5 and the two columns 0 and 6 equals the corrupted entry's multiplier: this is the positive integer you are looking for.

Table (entry value = row value * column value):
117 91 247 234 26 195 247 221
27 21 57 54 6 45 57 51
126 98 266 252 28 210 266 238
99 77 209 198 22 165 209 187
108 84 228 216 24 180 228 204
36 28 76 72 8 60 836 68
81 63 171 162 18 135 171 153
27 21 57 54 6 45 57 51

Compute the 2x2 interaction contrast (the cross-ratio (836 * 108) / (36 * 228)), its value is the smallest positive integer (a prime between 2 and 97) that restores the table's multiplicative structure. Answer with that prime integer alone.
```

**Answer**

11


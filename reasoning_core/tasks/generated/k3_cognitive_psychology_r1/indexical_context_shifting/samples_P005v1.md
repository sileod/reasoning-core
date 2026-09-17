# P005v1 samples

## Level 0

### Example 1

**Prompt:**
```
In a staged diary, a context has two coordinates, day and city, each coded 0, 1, 2 or 3. The indexical I denotes the character in the table at the current day row and city column. S[utterance] rewrites the context using S before interpreting the utterance inside it. Use sequential context substitution: evaluate shifts from the outermost bracket inward, each exactly once. Every right-hand side uses the context entering that shift, not the original context. 'mod 4' means the remainder in 0..3, including for negative numbers. There is no additional shift when reading I.

Character Table:
day \ city | 0 | 1 | 2 | 3
0 | Mira | Tomas | Adele | Rashid
1 | Yuki | Paulo | Ingrid | Samir
2 | Lena | Omar | Nadia | Felix
3 | Zora | Hugo | Elif | Dario

Starting Context:
day=0, city=1

Shift Definitions:
S1: day <- (day + city + 3) mod 4; city unchanged
S2: city <- (city - day + 3) mod 4; day unchanged
S3: swap day and city simultaneously
S4: day <- (day + 3) mod 4; city unchanged

Embedded Utterance:
S1[S2[S3[S4[I]]]]

Who does the innermost I denote at its resulting coordinate? Return only the exact character name; for example, if the lookup yields Mira, write Mira. Do not return coordinates or an explanation.
```

**Answer:**
```
Zora
```

### Example 2

**Prompt:**
```
In a staged diary, a context has two coordinates, day and city, each coded 0, 1, 2 or 3. The indexical I denotes the character in the table at the current day row and city column. S[utterance] rewrites the context using S before interpreting the utterance inside it. Use sequential context substitution: evaluate shifts from the outermost bracket inward, each exactly once. Every right-hand side uses the context entering that shift, not the original context. 'mod 4' means the remainder in 0..3, including for negative numbers. There is no additional shift when reading I.

Character Table:
day \ city | 0 | 1 | 2 | 3
0 | Mira | Tomas | Adele | Rashid
1 | Yuki | Paulo | Ingrid | Samir
2 | Lena | Omar | Nadia | Felix
3 | Zora | Hugo | Elif | Dario

Starting Context:
day=0, city=0

Shift Definitions:
S1: swap day and city simultaneously
S2: day <- (day - city + 2) mod 4; city unchanged

Embedded Utterance:
S1[S2[I]]

Who does the innermost I denote at its resulting coordinate? Return only the exact character name; for example, if the lookup yields Mira, write Mira. Do not return coordinates or an explanation.
```

**Answer:**
```
Lena
```

## Level 2

### Example 1

**Prompt:**
```
In a staged diary, a context has two coordinates, day and city, each coded 0, 1, 2 or 3. The indexical I denotes the character in the table at the current day row and city column. S[utterance] rewrites the context using S before interpreting the utterance inside it. Use sequential context substitution: evaluate shifts from the outermost bracket inward, each exactly once. Every right-hand side uses the context entering that shift, not the original context. 'mod 4' means the remainder in 0..3, including for negative numbers. There is no additional shift when reading I.

Character Table:
day \ city | 0 | 1 | 2 | 3
0 | Mira | Tomas | Adele | Rashid
1 | Yuki | Paulo | Ingrid | Samir
2 | Lena | Omar | Nadia | Felix
3 | Zora | Hugo | Elif | Dario

Starting Context:
day=3, city=1

Shift Definitions:
S1: day <- (day + 3) mod 4; city unchanged
S2: city <- (city + day + 3) mod 4; day unchanged
S3: swap day and city simultaneously
S4: day <- (day + 3) mod 4; city unchanged
S5: swap day and city simultaneously
S6: day <- (day - city + 1) mod 4; city unchanged

Embedded Utterance:
S1[S2[S3[S4[S5[S6[I]]]]]]

Who does the innermost I denote at its resulting coordinate? Return only the exact character name; for example, if the lookup yields Mira, write Mira. Do not return coordinates or an explanation.
```

**Answer:**
```
Omar
```

### Example 2

**Prompt:**
```
In a staged diary, a context has two coordinates, day and city, each coded 0, 1, 2 or 3. The indexical I denotes the character in the table at the current day row and city column. S[utterance] rewrites the context using S before interpreting the utterance inside it. Use sequential context substitution: evaluate shifts from the outermost bracket inward, each exactly once. Every right-hand side uses the context entering that shift, not the original context. 'mod 4' means the remainder in 0..3, including for negative numbers. There is no additional shift when reading I.

Character Table:
day \ city | 0 | 1 | 2 | 3
0 | Mira | Tomas | Adele | Rashid
1 | Yuki | Paulo | Ingrid | Samir
2 | Lena | Omar | Nadia | Felix
3 | Zora | Hugo | Elif | Dario

Starting Context:
day=0, city=3

Shift Definitions:
S1: city <- (city - day + 3) mod 4; day unchanged
S2: day <- (day + city + 3) mod 4; city unchanged
S3: swap day and city simultaneously
S4: day <- (day + 3) mod 4; city unchanged
S5: city <- (city + 2) mod 4; day unchanged
S6: day <- (day - city + 1) mod 4; city unchanged

Embedded Utterance:
S1[S2[S3[S4[S5[S6[I]]]]]]

Who does the innermost I denote at its resulting coordinate? Return only the exact character name; for example, if the lookup yields Mira, write Mira. Do not return coordinates or an explanation.
```

**Answer:**
```
Dario
```

## Level 5

### Example 1

**Prompt:**
```
In a staged diary, a context has two coordinates, day and city, each coded 0, 1, 2 or 3. The indexical I denotes the character in the table at the current day row and city column. S[utterance] rewrites the context using S before interpreting the utterance inside it. Use sequential context substitution: evaluate shifts from the outermost bracket inward, each exactly once. Every right-hand side uses the context entering that shift, not the original context. 'mod 4' means the remainder in 0..3, including for negative numbers. There is no additional shift when reading I.

Character Table:
day \ city | 0 | 1 | 2 | 3
0 | Mira | Tomas | Adele | Rashid
1 | Yuki | Paulo | Ingrid | Samir
2 | Lena | Omar | Nadia | Felix
3 | Zora | Hugo | Elif | Dario

Starting Context:
day=1, city=2

Shift Definitions:
S1: swap day and city simultaneously
S2: day <- (day - city + 3) mod 4; city unchanged
S3: swap day and city simultaneously
S4: day <- (day - city + 1) mod 4; city unchanged
S5: city <- (city - day + 1) mod 4; day unchanged
S6: day <- (day + city + 2) mod 4; city unchanged
S7: city <- (city + day + 2) mod 4; day unchanged
S8: day <- (day - city + 2) mod 4; city unchanged
S9: swap day and city simultaneously
S10: city <- (city + 2) mod 4; day unchanged

Embedded Utterance:
S1[S2[S3[S4[S5[S6[S7[S8[S9[S10[I]]]]]]]]]]

Who does the innermost I denote at its resulting coordinate? Return only the exact character name; for example, if the lookup yields Mira, write Mira. Do not return coordinates or an explanation.
```

**Answer:**
```
Rashid
```

### Example 2

**Prompt:**
```
In a staged diary, a context has two coordinates, day and city, each coded 0, 1, 2 or 3. The indexical I denotes the character in the table at the current day row and city column. S[utterance] rewrites the context using S before interpreting the utterance inside it. Use sequential context substitution: evaluate shifts from the outermost bracket inward, each exactly once. Every right-hand side uses the context entering that shift, not the original context. 'mod 4' means the remainder in 0..3, including for negative numbers. There is no additional shift when reading I.

Character Table:
day \ city | 0 | 1 | 2 | 3
0 | Mira | Tomas | Adele | Rashid
1 | Yuki | Paulo | Ingrid | Samir
2 | Lena | Omar | Nadia | Felix
3 | Zora | Hugo | Elif | Dario

Starting Context:
day=0, city=0

Shift Definitions:
S1: day <- (day + 1) mod 4; city unchanged
S2: swap day and city simultaneously
S3: day <- (day + 2) mod 4; city unchanged
S4: swap day and city simultaneously
S5: day <- (day + city + 1) mod 4; city unchanged
S6: swap day and city simultaneously
S7: day <- (day + city + 2) mod 4; city unchanged
S8: city <- (city - day + 0) mod 4; day unchanged
S9: swap day and city simultaneously
S10: day <- (day + 1) mod 4; city unchanged
S11: swap day and city simultaneously

Embedded Utterance:
S1[S2[S3[S4[S5[S6[S7[S8[S9[S10[S11[I]]]]]]]]]]]

Who does the innermost I denote at its resulting coordinate? Return only the exact character name; for example, if the lookup yields Mira, write Mira. Do not return coordinates or an explanation.
```

**Answer:**
```
Tomas
```

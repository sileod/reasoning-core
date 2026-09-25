# Samples for P007v1: settlement_departure_consistency

Seed: 1139467751

## Level 0

### Prompt

```
An estate (an integer) is divided among claimants, each of whom is entitled to a stated integer share.

A has share 7, B has share 13, C has share 15.
The estate is paid in proportion to each claimant's share.
The estate to divide is 17.
Claimants C immediately depart and take their full stated share out of the estate.

The remaining estate is then redistributed among the claimants who stayed, using the same rule. Determine which of the REMAINING claimants ends up receiving a different amount than they received before the departures.

Answer with the labels of the affected claimants, separated by commas in alphabetical order (for example 'B, C'); if no remaining claimant's amount changes, answer exactly 'none'.
```

### Answer

```
A, B
```

### Prompt

```
An estate (an integer) is divided among claimants, each of whom is entitled to a stated integer share.

A has share 13, B has share 21, C has share 6.
The estate is paid by priority (water-filling): claimants are processed in the order B, A, C and each receives up to their share until the estate runs out.
The estate to divide is 23.
Claimants C immediately depart and take their full stated share out of the estate.

The remaining estate is then redistributed among the claimants who stayed, using the same rule. Determine which of the REMAINING claimants ends up receiving a different amount than they received before the departures.

Answer with the labels of the affected claimants, separated by commas in alphabetical order (for example 'B, C'); if no remaining claimant's amount changes, answer exactly 'none'.
```

### Answer

```
A, B
```

## Level 2

### Prompt

```
An estate (an integer) is divided among claimants, each of whom is entitled to a stated integer share.

A has share 29, B has share 6, C has share 24.
The estate is paid in proportion to each claimant's share.
The estate to divide is 108.
Claimants C immediately depart and take their full stated share out of the estate.

The remaining estate is then redistributed among the claimants who stayed, using the same rule. Determine which of the REMAINING claimants ends up receiving a different amount than they received before the departures.

Answer with the labels of the affected claimants, separated by commas in alphabetical order (for example 'B, C'); if no remaining claimant's amount changes, answer exactly 'none'.
```

### Answer

```
A, B
```

### Prompt

```
An estate (an integer) is divided among claimants, each of whom is entitled to a stated integer share.

A has share 13, B has share 14.
The estate is paid by priority (water-filling): claimants are processed in the order B, A and each receives up to their share until the estate runs out.
The estate to divide is 218.
Claimants B immediately depart and take their full stated share out of the estate.

The remaining estate is then redistributed among the claimants who stayed, using the same rule. Determine which of the REMAINING claimants ends up receiving a different amount than they received before the departures.

Answer with the labels of the affected claimants, separated by commas in alphabetical order (for example 'B, C'); if no remaining claimant's amount changes, answer exactly 'none'.
```

### Answer

```
none
```

## Level 5

### Prompt

```
An estate (an integer) is divided among claimants, each of whom is entitled to a stated integer share.

A has share 19, B has share 27, C has share 28, D has share 9, E has share 22, F has share 16, G has share 11, H has share 2.
The estate is paid by priority (water-filling): claimants are processed in the order B, H, F, E, G, D, C, A and each receives up to their share until the estate runs out.
The estate to divide is 44.
Claimants A, H immediately depart and take their full stated share out of the estate.

The remaining estate is then redistributed among the claimants who stayed, using the same rule. Determine which of the REMAINING claimants ends up receiving a different amount than they received before the departures.

Answer with the labels of the affected claimants, separated by commas in alphabetical order (for example 'B, C'); if no remaining claimant's amount changes, answer exactly 'none'.
```

### Answer

```
B, F
```

### Prompt

```
An estate (an integer) is divided among claimants, each of whom is entitled to a stated integer share.

A has share 13, B has share 5.
The estate is paid in proportion to each claimant's share.
The estate to divide is 18.
Claimants B immediately depart and take their full stated share out of the estate.

The remaining estate is then redistributed among the claimants who stayed, using the same rule. Determine which of the REMAINING claimants ends up receiving a different amount than they received before the departures.

Answer with the labels of the affected claimants, separated by commas in alphabetical order (for example 'B, C'); if no remaining claimant's amount changes, answer exactly 'none'.
```

### Answer

```
none
```

# Samples for capstan_holding_bounds

## Level 0

### Example 1

**Prompt:**

```
A rope runs through the following fixed rough drums in series; each drum is described by its wrap factor, which is how much friction alone lets the tension ratio across it grow. Tension can therefore differ across a drum by any factor between its wrap factor and one over it, before slipping.
Drum 1: wrap factor 4.
At the load end the rope carries a suspended block of 1 N, an assisting driven hoist of 3 N.
The holding end is where tension is applied to keep the assembly still. If the load tends to slip the rope downward the holding tension must be at least the total end tension divided by the product of all wrap factors; if the holding force is too large the rope lifts the load, giving an upper bound equal to the total end tension times the product of all wrap factors.
Return the holding-force interval [min, max] in newtons as an exact pair of fractions, for example [9/4, 36]. Give min and max as reduced fractions; a whole number may be written as an integer.
```

**Answer:**

[1, 16]

### Example 2

**Prompt:**

```
A rope runs through the following fixed rough drums in series; each drum is described by its wrap factor, which is how much friction alone lets the tension ratio across it grow. Tension can therefore differ across a drum by any factor between its wrap factor and one over it, before slipping.
Drum 1: wrap factor 2.
At the load end the rope carries a suspended block of 1 N, an assisting driven hoist of 2 N.
The holding end is where tension is applied to keep the assembly still. If the load tends to slip the rope downward the holding tension must be at least the total end tension divided by the product of all wrap factors; if the holding force is too large the rope lifts the load, giving an upper bound equal to the total end tension times the product of all wrap factors.
Return the holding-force interval [min, max] in newtons as an exact pair of fractions, for example [9/4, 36]. Give min and max as reduced fractions; a whole number may be written as an integer.
```

**Answer:**

[3/2, 6]

## Level 2

### Example 1

**Prompt:**

```
A rope runs through the following fixed rough drums in series; each drum is described by its wrap factor, which is how much friction alone lets the tension ratio across it grow. Tension can therefore differ across a drum by any factor between its wrap factor and one over it, before slipping.
Drum 1: wrap factor 7/2.
Drum 2: wrap factor 2.
At the load end the rope carries a suspended block of 2 N, a suspended block of 6 N, an assisting driven hoist of 8/7 N.
The holding end is where tension is applied to keep the assembly still. If the load tends to slip the rope downward the holding tension must be at least the total end tension divided by the product of all wrap factors; if the holding force is too large the rope lifts the load, giving an upper bound equal to the total end tension times the product of all wrap factors.
Return the holding-force interval [min, max] in newtons as an exact pair of fractions, for example [9/4, 36]. Give min and max as reduced fractions; a whole number may be written as an integer.
```

**Answer:**

[64/49, 64]

### Example 2

**Prompt:**

```
A rope runs through the following fixed rough drums in series; each drum is described by its wrap factor, which is how much friction alone lets the tension ratio across it grow. Tension can therefore differ across a drum by any factor between its wrap factor and one over it, before slipping.
Drum 1: wrap factor 3.
Drum 2: wrap factor 3/2.
At the load end the rope carries a suspended block of 2 N, a suspended block of 7/6 N.
The holding end is where tension is applied to keep the assembly still. If the load tends to slip the rope downward the holding tension must be at least the total end tension divided by the product of all wrap factors; if the holding force is too large the rope lifts the load, giving an upper bound equal to the total end tension times the product of all wrap factors.
Return the holding-force interval [min, max] in newtons as an exact pair of fractions, for example [9/4, 36]. Give min and max as reduced fractions; a whole number may be written as an integer.
```

**Answer:**

[19/27, 57/4]

## Level 5

### Example 1

**Prompt:**

```
A rope runs through the following fixed rough drums in series; each drum is described by its wrap factor, which is how much friction alone lets the tension ratio across it grow. Tension can therefore differ across a drum by any factor between its wrap factor and one over it, before slipping.
Drum 1: wrap factor 2.
Drum 2: wrap factor 3.
Drum 3: wrap factor 2.
At the load end the rope carries a suspended block of 3/2 N, a suspended block of 4/3 N, a suspended block of 1 N.
The holding end is where tension is applied to keep the assembly still. If the load tends to slip the rope downward the holding tension must be at least the total end tension divided by the product of all wrap factors; if the holding force is too large the rope lifts the load, giving an upper bound equal to the total end tension times the product of all wrap factors.
Return the holding-force interval [min, max] in newtons as an exact pair of fractions, for example [9/4, 36]. Give min and max as reduced fractions; a whole number may be written as an integer.
```

**Answer:**

[23/72, 46]

### Example 2

**Prompt:**

```
A rope runs through the following fixed rough drums in series; each drum is described by its wrap factor, which is how much friction alone lets the tension ratio across it grow. Tension can therefore differ across a drum by any factor between its wrap factor and one over it, before slipping.
Drum 1: wrap factor 11/5.
Drum 2: wrap factor 7.
Drum 3: wrap factor 2.
At the load end the rope carries a suspended block of 4/3 N, a suspended block of 8/3 N, a suspended block of 13/2 N.
The holding end is where tension is applied to keep the assembly still. If the load tends to slip the rope downward the holding tension must be at least the total end tension divided by the product of all wrap factors; if the holding force is too large the rope lifts the load, giving an upper bound equal to the total end tension times the product of all wrap factors.
Return the holding-force interval [min, max] in newtons as an exact pair of fractions, for example [9/4, 36]. Give min and max as reduced fractions; a whole number may be written as an integer.
```

**Answer:**

[15/44, 1617/5]

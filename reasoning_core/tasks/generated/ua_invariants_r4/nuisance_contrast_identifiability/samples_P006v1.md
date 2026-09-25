# Samples for nuisance_contrast_identifiability (P006v1)

## Level 0

**Prompt**
```
The following linear equations relate a set of unknown parameters (shared offsets, drift terms, calibration nuisances):
1*p0- 2*p1 = 0; 2*p1- 1*p2 = -1; -1*p0- 2*p2 = 3
Consider the linear contrast -4*p1+ 2*p2. State whether this contrast is 'identifiable' — that is, whether its value is uniquely determined by the equations after eliminating all nuisance directions. If it is identifiable, output 'identifiable <value>' where <value> is the rational number, reduced, e.g. 'identifiable -3/2' or 'identifiable 5'. If it is not identifiable, output exactly 'not identifiable'.
```

**Answer**
```
identifiable 2
```

**Prompt**
```
The following linear equations relate a set of unknown parameters (shared offsets, drift terms, calibration nuisances):
2*p0- 1*p1 = -2; 1*p1- 2*p2 = -1
Consider the linear contrast 1*p1+ 1*p2. State whether this contrast is 'identifiable' — that is, whether its value is uniquely determined by the equations after eliminating all nuisance directions. If it is identifiable, output 'identifiable <value>' where <value> is the rational number, reduced, e.g. 'identifiable -3/2' or 'identifiable 5'. If it is not identifiable, output exactly 'not identifiable'.
```

**Answer**
```
not identifiable
```

## Level 2

**Prompt**
```
The following linear equations relate a set of unknown parameters (shared offsets, drift terms, calibration nuisances):
1*p0- 2*p1 = -8; 3*p1- 3*p2 = 6; 1*p2- 1*p3 = -6; 3*p3- 1*p4 = 5
Consider the linear contrast 1*p3+ 3*p4. State whether this contrast is 'identifiable' — that is, whether its value is uniquely determined by the equations after eliminating all nuisance directions. If it is identifiable, output 'identifiable <value>' where <value> is the rational number, reduced, e.g. 'identifiable -3/2' or 'identifiable 5'. If it is not identifiable, output exactly 'not identifiable'.
```

**Answer**
```
not identifiable
```

**Prompt**
```
The following linear equations relate a set of unknown parameters (shared offsets, drift terms, calibration nuisances):
4*p0- 4*p1 = -8; 4*p1- 3*p2 = 0; 3*p2- 3*p3 = 4; 2*p3- 1*p4 = -3
Consider the linear contrast 4*p1- 3*p2. State whether this contrast is 'identifiable' — that is, whether its value is uniquely determined by the equations after eliminating all nuisance directions. If it is identifiable, output 'identifiable <value>' where <value> is the rational number, reduced, e.g. 'identifiable -3/2' or 'identifiable 5'. If it is not identifiable, output exactly 'not identifiable'.
```

**Answer**
```
identifiable 0
```

## Level 5

**Prompt**
```
The following linear equations relate a set of unknown parameters (shared offsets, drift terms, calibration nuisances):
2*p0- 6*p1 = -10; 1*p1- 3*p2 = -3; 6*p2- 7*p3 = -13; 4*p3- 5*p4 = -5; 3*p4- 1*p5 = -7; 1*p5- 2*p6 = -9; 5*p6- 5*p7 = -14
Consider the linear contrast 6*p4- 2*p5. State whether this contrast is 'identifiable' — that is, whether its value is uniquely determined by the equations after eliminating all nuisance directions. If it is identifiable, output 'identifiable <value>' where <value> is the rational number, reduced, e.g. 'identifiable -3/2' or 'identifiable 5'. If it is not identifiable, output exactly 'not identifiable'.
```

**Answer**
```
identifiable -14
```

**Prompt**
```
The following linear equations relate a set of unknown parameters (shared offsets, drift terms, calibration nuisances):
6*p0- 5*p1 = -1; 4*p1- 4*p2 = 13; 2*p2- 4*p3 = 3; 4*p3- 1*p4 = 12; 7*p4- 3*p5 = 0; 7*p5- 1*p6 = -6; 2*p6- 4*p7 = -12
Consider the linear contrast -4*p2+ 8*p3. State whether this contrast is 'identifiable' — that is, whether its value is uniquely determined by the equations after eliminating all nuisance directions. If it is identifiable, output 'identifiable <value>' where <value> is the rational number, reduced, e.g. 'identifiable -3/2' or 'identifiable 5'. If it is not identifiable, output exactly 'not identifiable'.
```

**Answer**
```
identifiable -6
```

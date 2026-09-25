# P002v3 samples - boolean_circuit_fault_diagnosis

## Level 0

### Example 1

A combinational circuit with primary inputs (I) and internal gates (g) is given below; its primary outputs are O. Each internal gate may be stuck-at-faulty, forcing its output to a fixed value. When a set of internal gates is faulty the observed outputs differ from the fault-free expected outputs. (The primary outputs are observation pins, never faulty gates themselves.)

g3 = NOT(I1)
g4 = XNOR(I2, I0)
g5 = NAND(I2, I1)
g6 = XOR(I1, g4)
g7 = OR(I1, g5)
g8 = NOT(g7)

I0=1, I1=0, I2=1

Expected outputs: O0=1, O1=0
Observed outputs: O0=0, O1=1

Which internal gates are stuck-at-faulty, i.e. the minimal set of internal gates whose stuck values fully explain the observed outputs? Answer as the space-separated gate indices in ascending order.

Answer: 5

### Example 2

A combinational circuit with primary inputs is given below. A single gate is stuck-at-faulty: its output is forced to a fixed value.

g3 = XNOR(I2, I1)
g4 = XOR(I0, I1)
g5 = NAND(I2, g3)
g6 = OR(g3, I0)
g7 = XNOR(I2, g3)
g8 = XNOR(g3, I0)

I0=0, I1=0, I2=0

Fault: g7 is stuck-at 0
Fault-free expected outputs: O0=0, O1=0

Is this fault detectable, i.e. does it change at least one observed output compared to the fault-free circuit? Answer with YES or NO as the only content.

Answer: NO

## Level 2

### Example 1

A combinational circuit with primary inputs (I) and internal gates (g) is given below; its primary outputs are O. Each internal gate may be stuck-at-faulty, forcing its output to a fixed value. When a set of internal gates is faulty the observed outputs differ from the fault-free expected outputs. (The primary outputs are observation pins, never faulty gates themselves.)

g3 = NOR(I1, I2)
g4 = AND(I2, I0)
g5 = NOR(I2, I1)
g6 = XNOR(I1, g4)
g7 = XNOR(g6, g5)
g8 = AND(g4, I1)
g9 = NOR(I2, g3)
g10 = XNOR(g6, I1)
g11 = XOR(I0, g6)
g12 = XOR(g3, I2)

I0=0, I1=1, I2=1

Expected outputs: O0=0, O1=1
Observed outputs: O0=0, O1=0

Which internal gates are stuck-at-faulty, i.e. the minimal set of internal gates whose stuck values fully explain the observed outputs? Answer as the space-separated gate indices in ascending order.

Answer: 3

### Example 2

A combinational circuit with primary inputs is given below. A single gate is stuck-at-faulty: its output is forced to a fixed value.

g3 = OR(I0, I2)
g4 = XNOR(I0, I1)
g5 = OR(g3, I2)
g6 = XOR(g5, I2)
g7 = NAND(I1, g6)
g8 = XOR(g5, g6)
g9 = AND(g3, g6)
g10 = OR(I1, g4)
g11 = AND(I2, g9)
g12 = AND(g3, g6)

I0=1, I1=0, I2=1

Fault: g5 is stuck-at 1
Fault-free expected outputs: O0=0, O1=0

Is this fault detectable, i.e. does it change at least one observed output compared to the fault-free circuit? Answer with YES or NO as the only content.

Answer: NO

## Level 5

### Example 1

A combinational circuit with primary inputs (I) and internal gates (g) is given below; its primary outputs are O. Each internal gate may be stuck-at-faulty, forcing its output to a fixed value. When a set of internal gates is faulty the observed outputs differ from the fault-free expected outputs. (The primary outputs are observation pins, never faulty gates themselves.)

g3 = NAND(I1, I2)
g4 = NOT(I1)
g5 = XNOR(g3, g4)
g6 = AND(I0, I2)
g7 = NOR(g5, I0)
g8 = XNOR(g5, I0)
g9 = NOT(g4)
g10 = XNOR(g9, g7)
g11 = NOR(g7, g4)
g12 = NOR(g4, g3)
g13 = NAND(g5, g4)
g14 = NOR(g8, g5)
g15 = NAND(g9, g10)
g16 = XOR(g8, I2)
g17 = NAND(I2, g4)
g18 = XNOR(g11, g14)

I0=1, I1=1, I2=0

Expected outputs: O0=0, O1=1, O2=1
Observed outputs: O0=1, O1=1, O2=1

Which internal gates are stuck-at-faulty, i.e. the minimal set of internal gates whose stuck values fully explain the observed outputs? Answer as the space-separated gate indices in ascending order.

Answer: 4

### Example 2

A combinational circuit with primary inputs (I) and internal gates (g) is given below; its primary outputs are O. Each internal gate may be stuck-at-faulty, forcing its output to a fixed value. When a set of internal gates is faulty the observed outputs differ from the fault-free expected outputs. (The primary outputs are observation pins, never faulty gates themselves.)

g3 = NOR(I2, I1)
g4 = NOR(g3, I0)
g5 = XOR(I1, g3)
g6 = NOT(I1)
g7 = NOT(I0)
g8 = AND(g3, I1)
g9 = NOR(g7, g6)
g10 = AND(g5, g9)
g11 = NOR(g7, I0)
g12 = OR(I2, g8)
g13 = XOR(I0, g7)
g14 = XNOR(g6, g8)
g15 = OR(g12, g13)
g16 = NOT(g5)
g17 = NOR(I1, g6)
g18 = XOR(I0, g4)

I0=0, I1=1, I2=0

Expected outputs: O0=0, O1=0, O2=1
Observed outputs: O0=0, O1=0, O2=0

Which internal gates are stuck-at-faulty, i.e. the minimal set of internal gates whose stuck values fully explain the observed outputs? Answer as the space-separated gate indices in ascending order.

Answer: 4

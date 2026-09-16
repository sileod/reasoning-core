## Level 0

**Example 1**

**Prompt**

```
A combinational netlist of digital gates is simulated as an event-driven system over integer time, starting at t=0. Every node holds a boolean value; the only given inputs are the input waveforms below. At t=0 every node already has its steady-state value from the initial levels.
Input waveforms (value@time transitions; held until the next one):
  i0: 0@0,1@3,0@6
Gates (inputs, then delay, then mode). Modes: "transport" passes every pulse through unchanged (just shifted by the gate delay); "inertial" cancels any output pulse narrower than the gate delay, so such pulses never appear on that gate's output (stale pulses are dropped).
  g0 = NOT(i0) delay 1, inertial
  g1 = NOT(i0) delay 1, transport
The netlist is fanout-free to a single final output node: g1.
A glitch interval [a,b] is a maximal pulse on the final output whose width (b-a) is strictly less than the delay of the final output gate; list glitches in chronological order as [a,b] pairs, or [] if there are none.
Answer on one line as the final output waveform "v@t,..." with the initial value first at t=0, then ";", then the glitch list. Example: "0@0,1@3,0@5,1@7; [3,5]".
```

**Answer**

```
1@0,0@4,1@7; []
```

**Example 2**

**Prompt**

```
A combinational netlist of digital gates is simulated as an event-driven system over integer time, starting at t=0. Every node holds a boolean value; the only given inputs are the input waveforms below. At t=0 every node already has its steady-state value from the initial levels.
Input waveforms (value@time transitions; held until the next one):
  i0: 0@0,1@1
Gates (inputs, then delay, then mode). Modes: "transport" passes every pulse through unchanged (just shifted by the gate delay); "inertial" cancels any output pulse narrower than the gate delay, so such pulses never appear on that gate's output (stale pulses are dropped).
  g0 = OR(i0) delay 1, inertial
  g1 = NOT(i0) delay 1, transport
The netlist is fanout-free to a single final output node: g1.
A glitch interval [a,b] is a maximal pulse on the final output whose width (b-a) is strictly less than the delay of the final output gate; list glitches in chronological order as [a,b] pairs, or [] if there are none.
Answer on one line as the final output waveform "v@t,..." with the initial value first at t=0, then ";", then the glitch list. Example: "0@0,1@3,0@5,1@7; [3,5]".
```

**Answer**

```
1@0,0@2; []
```

## Level 2

**Example 1**

**Prompt**

```
A combinational netlist of digital gates is simulated as an event-driven system over integer time, starting at t=0. Every node holds a boolean value; the only given inputs are the input waveforms below. At t=0 every node already has its steady-state value from the initial levels.
Input waveforms (value@time transitions; held until the next one):
  i0: 1@0,0@5,1@6,0@14,1@16
  i1: 1@0,0@3,1@5,0@9,1@10
Gates (inputs, then delay, then mode). Modes: "transport" passes every pulse through unchanged (just shifted by the gate delay); "inertial" cancels any output pulse narrower than the gate delay, so such pulses never appear on that gate's output (stale pulses are dropped).
  g0 = NAND(i1,i0) delay 3, inertial
  g1 = OR(g0,i0) delay 3, inertial
  g2 = XOR(i0,i1) delay 1, inertial
  g3 = NOT(g2) delay 1, transport
  g4 = XOR(g3,g2) delay 3, transport
  g5 = NAND(g4,g3) delay 1, transport
The netlist is fanout-free to a single final output node: g5.
A glitch interval [a,b] is a maximal pulse on the final output whose width (b-a) is strictly less than the delay of the final output gate; list glitches in chronological order as [a,b] pairs, or [] if there are none.
Answer on one line as the final output waveform "v@t,..." with the initial value first at t=0, then ";", then the glitch list. Example: "0@0,1@3,0@5,1@7; [3,5]".
```

**Answer**

```
0@0,1@6,0@9,1@11,0@13,1@14,0@16,1@17,0@20,1@21,0@22; []
```

**Example 2**

**Prompt**

```
A combinational netlist of digital gates is simulated as an event-driven system over integer time, starting at t=0. Every node holds a boolean value; the only given inputs are the input waveforms below. At t=0 every node already has its steady-state value from the initial levels.
Input waveforms (value@time transitions; held until the next one):
  i0: 0@0,1@5,0@9
  i1: 0@0,1@5,0@6,1@13,0@14
Gates (inputs, then delay, then mode). Modes: "transport" passes every pulse through unchanged (just shifted by the gate delay); "inertial" cancels any output pulse narrower than the gate delay, so such pulses never appear on that gate's output (stale pulses are dropped).
  g0 = NOR(i0,i1) delay 1, transport
  g1 = XNOR(g0,i1) delay 1, transport
  g2 = OR(g0,i0,i1) delay 3, inertial
  g3 = NAND(g2,i0) delay 2, transport
  g4 = NOR(i1,g0,i0) delay 1, transport
  g5 = NOR(i1,g3,g1) delay 2, transport
The netlist is fanout-free to a single final output node: g5.
A glitch interval [a,b] is a maximal pulse on the final output whose width (b-a) is strictly less than the delay of the final output gate; list glitches in chronological order as [a,b] pairs, or [] if there are none.
Answer on one line as the final output waveform "v@t,..." with the initial value first at t=0, then ";", then the glitch list. Example: "0@0,1@3,0@5,1@7; [3,5]".
```

**Answer**

```
0@0; []
```

## Level 5

**Example 1**

**Prompt**

```
A combinational netlist of digital gates is simulated as an event-driven system over integer time, starting at t=0. Every node holds a boolean value; the only given inputs are the input waveforms below. At t=0 every node already has its steady-state value from the initial levels.
Input waveforms (value@time transitions; held until the next one):
  i0: 1@0,0@9,1@12,0@16,1@17,0@18,1@19,0@24
  i1: 0@0,1@1,0@18
  i2: 1@0,0@4,1@17,0@19,1@21,0@25,1@26
Gates (inputs, then delay, then mode). Modes: "transport" passes every pulse through unchanged (just shifted by the gate delay); "inertial" cancels any output pulse narrower than the gate delay, so such pulses never appear on that gate's output (stale pulses are dropped).
  g0 = XNOR(i0,i2) delay 6, transport
  g1 = AND(g0,i2) delay 4, inertial
  g2 = NOT(i0) delay 3, transport
  g3 = NOT(i0) delay 6, transport
  g4 = NOR(i1,g3,g1) delay 4, transport
  g5 = XNOR(g1,i2) delay 6, inertial
  g6 = NOR(g5,i2) delay 4, transport
  g7 = AND(g5,g0,g6) delay 2, inertial
  g8 = AND(g7,g6) delay 1, inertial
  g9 = NAND(g5,g8) delay 5, inertial
  g10 = NOT(g9) delay 3, transport
  g11 = XOR(g3,i0) delay 2, transport
The netlist is fanout-free to a single final output node: g11.
A glitch interval [a,b] is a maximal pulse on the final output whose width (b-a) is strictly less than the delay of the final output gate; list glitches in chronological order as [a,b] pairs, or [] if there are none.
Answer on one line as the final output waveform "v@t,..." with the initial value first at t=0, then ";", then the glitch list. Example: "0@0,1@3,0@5,1@7; [3,5]".
```

**Answer**

```
1@0,0@11,1@14,0@17,1@18,0@19,1@21,0@24,1@25,0@27,1@32; [17,18],[18,19],[24,25]
```

**Example 2**

**Prompt**

```
A combinational netlist of digital gates is simulated as an event-driven system over integer time, starting at t=0. Every node holds a boolean value; the only given inputs are the input waveforms below. At t=0 every node already has its steady-state value from the initial levels.
Input waveforms (value@time transitions; held until the next one):
  i0: 0@0,1@4,0@8,1@9,0@14,1@17,0@27
  i1: 1@0,0@22
  i2: 1@0,0@6,1@15,0@19,1@22
Gates (inputs, then delay, then mode). Modes: "transport" passes every pulse through unchanged (just shifted by the gate delay); "inertial" cancels any output pulse narrower than the gate delay, so such pulses never appear on that gate's output (stale pulses are dropped).
  g0 = XOR(i2,i1,i0) delay 4, transport
  g1 = XNOR(g0,i2) delay 5, transport
  g2 = XNOR(g1,g0) delay 5, inertial
  g3 = XNOR(g2,g0) delay 1, transport
  g4 = NOR(g3,g2) delay 6, transport
  g5 = XOR(i2,g3,g1) delay 5, transport
  g6 = AND(g1,g4) delay 4, transport
  g7 = NOR(i2,g1) delay 2, inertial
  g8 = AND(g7,g1) delay 3, transport
  g9 = NOR(g8,g7) delay 1, inertial
  g10 = NAND(g9,g7) delay 4, transport
  g11 = XNOR(g10,g7) delay 4, transport
The netlist is fanout-free to a single final output node: g11.
A glitch interval [a,b] is a maximal pulse on the final output whose width (b-a) is strictly less than the delay of the final output gate; list glitches in chronological order as [a,b] pairs, or [] if there are none.
Answer on one line as the final output waveform "v@t,..." with the initial value first at t=0, then ";", then the glitch list. Example: "0@0,1@3,0@5,1@7; [3,5]".
```

**Answer**

```
0@0,1@12,0@16,1@19,0@21,1@26,0@28,1@30,0@31; [16,19],[19,21],[26,28],[28,30],[30,31]
```

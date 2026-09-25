# P010v1 samples - switched_capacitor_charge_tracking

Seed: 2409743872

## Level 0

### Example 1

Prompt:

```
Electric state tracking problem. A capacitor's plates hold equal and opposite charge; each conductor (a set of plates wired together) stays at a single voltage and conserves its total charge when it is a floating conductor.
Conductors present at the start: P, Q. Ground conductor G is always at voltage 0 and can supply or absorb any charge.
Capacitances:
capacitor G-P has capacitance 1; capacitor G-Q has capacitance 1.
Initial floated charges: P carries charge 0; Q carries charge 3.
Then, in order: ground conductor P.
You are asked for the charge on the G plate of capacitor G-Q after all operations resolve.
Charge is conserved and the network reaches electrostatic equilibrium. Report that plate's charge as an integer number of elementary charges.
```

Answer: 3

### Example 2

Prompt:

```
Electric state tracking problem. A capacitor's plates hold equal and opposite charge; each conductor (a set of plates wired together) stays at a single voltage and conserves its total charge when it is a floating conductor.
Conductors present at the start: P, Q. Ground conductor G is always at voltage 0 and can supply or absorb any charge.
Capacitances:
capacitor G-P has capacitance 2; capacitor P-Q has capacitance 2.
Initial floated charges: P carries charge -3; Q carries charge 2.
Then, in order: clamp conductor P to voltage 3.
You are asked for the charge on the P plate of capacitor G-P after all operations resolve.
Charge is conserved and the network reaches electrostatic equilibrium. Report that plate's charge as an integer number of elementary charges.
```

Answer: 6

### Example 3

Prompt:

```
Electric state tracking problem. A capacitor's plates hold equal and opposite charge; each conductor (a set of plates wired together) stays at a single voltage and conserves its total charge when it is a floating conductor.
Conductors present at the start: P, Q. Ground conductor G is always at voltage 0 and can supply or absorb any charge.
Capacitances:
capacitor G-P has capacitance 2; capacitor P-Q has capacitance 1.
Initial floated charges: P carries charge -1; Q carries charge 1.
Then, in order: clamp conductor Q to voltage 2.
You are asked for the charge on the G plate of capacitor G-P after all operations resolve.
Charge is conserved and the network reaches electrostatic equilibrium. Report that plate's charge as an integer number of elementary charges.
```

Answer: -2

## Level 2

### Example 1

Prompt:

```
Electric state tracking problem. A capacitor's plates hold equal and opposite charge; each conductor (a set of plates wired together) stays at a single voltage and conserves its total charge when it is a floating conductor.
Conductors present at the start: P, Q, R, S. Ground conductor G is always at voltage 0 and can supply or absorb any charge.
Capacitances:
capacitor G-P has capacitance 1; capacitor G-Q has capacitance 2; capacitor P-R has capacitance 2.
Initial floated charges: P carries charge 2; Q carries charge -1; R carries charge -1; S carries charge 4.
Then, in order: ground conductor Q; ground conductor S; reconnect conductors P and R.
You are asked for the charge on the R plate of capacitor G-R after all operations resolve.
Charge is conserved and the network reaches electrostatic equilibrium. Report that plate's charge as an integer number of elementary charges.
```

Answer: 1

### Example 2

Prompt:

```
Electric state tracking problem. A capacitor's plates hold equal and opposite charge; each conductor (a set of plates wired together) stays at a single voltage and conserves its total charge when it is a floating conductor.
Conductors present at the start: P, Q, R, S. Ground conductor G is always at voltage 0 and can supply or absorb any charge.
Capacitances:
capacitor G-Q has capacitance 3; capacitor P-Q has capacitance 2; capacitor Q-S has capacitance 1.
Initial floated charges: P carries charge 4; Q carries charge 4; R carries charge 1; S carries charge 6.
Then, in order: reconnect conductors Q and S; reconnect conductors R and S; reconnect conductors P and S.
You are asked for the charge on the S plate of capacitor G-S after all operations resolve.
Charge is conserved and the network reaches electrostatic equilibrium. Report that plate's charge as an integer number of elementary charges.
```

Answer: -6

### Example 3

Prompt:

```
Electric state tracking problem. A capacitor's plates hold equal and opposite charge; each conductor (a set of plates wired together) stays at a single voltage and conserves its total charge when it is a floating conductor.
Conductors present at the start: P, Q, R, S. Ground conductor G is always at voltage 0 and can supply or absorb any charge.
Capacitances:
capacitor G-S has capacitance 1; capacitor P-S has capacitance 1; capacitor R-S has capacitance 3.
Initial floated charges: P carries charge -3; Q carries charge -3; R carries charge -5; S carries charge -4.
Then, in order: ground conductor P; clamp conductor Q to voltage 1; clamp conductor S to voltage 4.
You are asked for the charge on the S plate of capacitor G-S after all operations resolve.
Charge is conserved and the network reaches electrostatic equilibrium. Report that plate's charge as an integer number of elementary charges.
```

Answer: 4

## Level 5

### Example 1

Prompt:

```
Electric state tracking problem. A capacitor's plates hold equal and opposite charge; each conductor (a set of plates wired together) stays at a single voltage and conserves its total charge when it is a floating conductor.
Conductors present at the start: P, Q, R, S, T, U, V. Ground conductor G is always at voltage 0 and can supply or absorb any charge.
Capacitances:
capacitor G-T has capacitance 2; capacitor P-R has capacitance 1; capacitor Q-S has capacitance 3; capacitor R-T has capacitance 3.
Initial floated charges: P carries charge -2; Q carries charge -2; R carries charge -8; S carries charge 4; T carries charge -5; U carries charge 5; V carries charge 4.
Then, in order: clamp conductor T to voltage -2; ground conductor S; ground conductor V; ground conductor R; ground conductor Q; reconnect conductors P and U.
You are asked for the charge on the R plate of capacitor R-U after all operations resolve.
Charge is conserved and the network reaches electrostatic equilibrium. Report that plate's charge as an integer number of elementary charges.
```

Answer: 5

### Example 2

Prompt:

```
Electric state tracking problem. A capacitor's plates hold equal and opposite charge; each conductor (a set of plates wired together) stays at a single voltage and conserves its total charge when it is a floating conductor.
Conductors present at the start: P, Q, R, S, T, U, V. Ground conductor G is always at voltage 0 and can supply or absorb any charge.
Capacitances:
capacitor P-V has capacitance 2; capacitor R-U has capacitance 2; capacitor S-T has capacitance 1; capacitor T-U has capacitance 4.
Initial floated charges: P carries charge 7; Q carries charge -2; R carries charge 2; S carries charge 7; T carries charge 5; U carries charge 8; V carries charge 0.
Then, in order: clamp conductor P to voltage -3; reconnect conductors S and R; clamp conductor R to voltage -2; reconnect conductors T and U; ground conductor Q; reconnect conductors V and U.
You are asked for the charge on the U plate of capacitor P-U after all operations resolve.
Charge is conserved and the network reaches electrostatic equilibrium. Report that plate's charge as an integer number of elementary charges.
```

Answer: -2

### Example 3

Prompt:

```
Electric state tracking problem. A capacitor's plates hold equal and opposite charge; each conductor (a set of plates wired together) stays at a single voltage and conserves its total charge when it is a floating conductor.
Conductors present at the start: P, Q, R, S, T, U, V. Ground conductor G is always at voltage 0 and can supply or absorb any charge.
Capacitances:
capacitor P-R has capacitance 1; capacitor R-V has capacitance 4; capacitor S-V has capacitance 4; capacitor T-V has capacitance 1.
Initial floated charges: P carries charge -1; Q carries charge 4; R carries charge 6; S carries charge -8; T carries charge 4; U carries charge 2; V carries charge 5.
Then, in order: ground conductor U; reconnect conductors V and Q; reconnect conductors P and T; clamp conductor S to voltage 1; ground conductor R; clamp conductor Q to voltage -4.
You are asked for the charge on the Q plate of capacitor Q-S after all operations resolve.
Charge is conserved and the network reaches electrostatic equilibrium. Report that plate's charge as an integer number of elementary charges.
```

Answer: -20


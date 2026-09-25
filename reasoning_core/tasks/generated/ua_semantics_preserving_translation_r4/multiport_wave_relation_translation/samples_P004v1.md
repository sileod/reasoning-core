## Level 0

### Example 1

Prompt:

```
Each port i carries voltage V_i and current I_i related to incident wave a_i and reflected wave b_i by V_i = sqrt(Z_i)*(a_i + b_i) and I_i = (1/sqrt(Z_i))*(a_i - b_i).
Ports and their terminations:
  Port 1: reference impedance Z_1 = 4, terminated by a matched load equal to Z_i = 4 (V = 4 I)
  Port 2: reference impedance Z_2 = 3, terminated by a load of Z_L = 4 (V = 4 I)
Write the incident/reflected wave constraint produced by each termination, one equation per port, in the exact form  b_<i> = c*a_<i>  where c is the reflection coefficient as an exact rational fraction (an integer like 1 or -1 is a valid c; use 0 for a matched load). Example of the exact format:  b_1 = -1*a_1; b_2 = 1/2*a_2
Answer only the relations, ports in order, separated by "; ".
```


Answer:

```
b_1 = 0*a_1; b_2 = 1/7*a_2
```


### Example 2

Prompt:

```
Each port i carries voltage V_i and current I_i related to incident wave a_i and reflected wave b_i by V_i = sqrt(Z_i)*(a_i + b_i) and I_i = (1/sqrt(Z_i))*(a_i - b_i).
Ports and their terminations:
  Port 1: reference impedance Z_1 = 5, terminated by a load of Z_L = 2 (V = 2 I)
  Port 2: reference impedance Z_2 = 5, terminated by an open (I = 0)
Write the incident/reflected wave constraint produced by each termination, one equation per port, in the exact form  b_<i> = c*a_<i>  where c is the reflection coefficient as an exact rational fraction (an integer like 1 or -1 is a valid c; use 0 for a matched load). Example of the exact format:  b_1 = -1*a_1; b_2 = 1/2*a_2
Answer only the relations, ports in order, separated by "; ".
```


Answer:

```
b_1 = -3/7*a_1; b_2 = 1*a_2
```


## Level 2

### Example 1

Prompt:

```
Each port i carries voltage V_i and current I_i related to incident wave a_i and reflected wave b_i by V_i = sqrt(Z_i)*(a_i + b_i) and I_i = (1/sqrt(Z_i))*(a_i - b_i).
Ports and their terminations:
  Port 1: reference impedance Z_1 = 4, terminated by a matched load equal to Z_i = 4 (V = 4 I)
  Port 2: reference impedance Z_2 = 5, terminated by a matched load equal to Z_i = 5 (V = 5 I)
  Port 3: reference impedance Z_3 = 8, terminated by a load of Z_L = 3 (V = 3 I)
  Port 4: reference impedance Z_4 = 8, terminated by a short (V = 0)
Write the incident/reflected wave constraint produced by each termination, one equation per port, in the exact form  b_<i> = c*a_<i>  where c is the reflection coefficient as an exact rational fraction (an integer like 1 or -1 is a valid c; use 0 for a matched load). Example of the exact format:  b_1 = -1*a_1; b_2 = 1/2*a_2
Answer only the relations, ports in order, separated by "; ".
```


Answer:

```
b_1 = 0*a_1; b_2 = 0*a_2; b_3 = -5/11*a_3; b_4 = -1*a_4
```


### Example 2

Prompt:

```
Each port i carries voltage V_i and current I_i related to incident wave a_i and reflected wave b_i by V_i = sqrt(Z_i)*(a_i + b_i) and I_i = (1/sqrt(Z_i))*(a_i - b_i).
Ports and their terminations:
  Port 1: reference impedance Z_1 = 5, terminated by a matched load equal to Z_i = 5 (V = 5 I)
  Port 2: reference impedance Z_2 = 1, terminated by an open (I = 0)
  Port 3: reference impedance Z_3 = 2, terminated by a load of Z_L = 1/4 (V = 1/4 I)
  Port 4: reference impedance Z_4 = 8, terminated by a load of Z_L = 2 (V = 2 I)
Write the incident/reflected wave constraint produced by each termination, one equation per port, in the exact form  b_<i> = c*a_<i>  where c is the reflection coefficient as an exact rational fraction (an integer like 1 or -1 is a valid c; use 0 for a matched load). Example of the exact format:  b_1 = -1*a_1; b_2 = 1/2*a_2
Answer only the relations, ports in order, separated by "; ".
```


Answer:

```
b_1 = 0*a_1; b_2 = 1*a_2; b_3 = -7/9*a_3; b_4 = -3/5*a_4
```


## Level 5

### Example 1

Prompt:

```
Each port i carries voltage V_i and current I_i related to incident wave a_i and reflected wave b_i by V_i = sqrt(Z_i)*(a_i + b_i) and I_i = (1/sqrt(Z_i))*(a_i - b_i).
Ports and their terminations:
  Port 1: reference impedance Z_1 = 5, terminated by a load of Z_L = 6 (V = 6 I)
  Port 2: reference impedance Z_2 = 2, terminated by a load of Z_L = 4 (V = 4 I)
  Port 3: reference impedance Z_3 = 3, terminated by a matched load equal to Z_i = 3 (V = 3 I)
  Port 4: reference impedance Z_4 = 8, terminated by a matched load equal to Z_i = 8 (V = 8 I)
  Port 5: reference impedance Z_5 = 2, terminated by a matched load equal to Z_i = 2 (V = 2 I)
  Port 6: reference impedance Z_6 = 4, terminated by an open (I = 0)
  Port 7: reference impedance Z_7 = 4, terminated by a matched load equal to Z_i = 4 (V = 4 I)
Write the incident/reflected wave constraint produced by each termination, one equation per port, in the exact form  b_<i> = c*a_<i>  where c is the reflection coefficient as an exact rational fraction (an integer like 1 or -1 is a valid c; use 0 for a matched load). Example of the exact format:  b_1 = -1*a_1; b_2 = 1/2*a_2
Answer only the relations, ports in order, separated by "; ".
```


Answer:

```
b_1 = 1/11*a_1; b_2 = 1/3*a_2; b_3 = 0*a_3; b_4 = 0*a_4; b_5 = 0*a_5; b_6 = 1*a_6; b_7 = 0*a_7
```


### Example 2

Prompt:

```
Each port i carries voltage V_i and current I_i related to incident wave a_i and reflected wave b_i by V_i = sqrt(Z_i)*(a_i + b_i) and I_i = (1/sqrt(Z_i))*(a_i - b_i).
Ports and their terminations:
  Port 1: reference impedance Z_1 = 5, terminated by a load of Z_L = 2 (V = 2 I)
  Port 2: reference impedance Z_2 = 1, terminated by a short (V = 0)
  Port 3: reference impedance Z_3 = 7, terminated by a load of Z_L = 6 (V = 6 I)
  Port 4: reference impedance Z_4 = 5, terminated by a load of Z_L = 8/3 (V = 8/3 I)
  Port 5: reference impedance Z_5 = 8, terminated by a matched load equal to Z_i = 8 (V = 8 I)
  Port 6: reference impedance Z_6 = 4, terminated by a load of Z_L = 4 (V = 4 I)
  Port 7: reference impedance Z_7 = 2, terminated by an open (I = 0)
Write the incident/reflected wave constraint produced by each termination, one equation per port, in the exact form  b_<i> = c*a_<i>  where c is the reflection coefficient as an exact rational fraction (an integer like 1 or -1 is a valid c; use 0 for a matched load). Example of the exact format:  b_1 = -1*a_1; b_2 = 1/2*a_2
Answer only the relations, ports in order, separated by "; ".
```


Answer:

```
b_1 = -3/7*a_1; b_2 = -1*a_2; b_3 = -1/13*a_3; b_4 = -7/23*a_4; b_5 = 0*a_5; b_6 = 0*a_6; b_7 = 1*a_7
```


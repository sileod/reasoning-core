## Level 0

Prompt:
A counter machine has registers a, b holding non-negative integers, initially a = 0, b = 1. Its program is the following labeled list of lines. On each line, INC r adds 1 to register r, DEC r subtracts 1 from register r (capped at 0), and 'JZ r L' jumps to the line labeled L when register r is 0, otherwise it continues to the next line. Execution starts at line 1 and runs one instruction at a time, continuing to the next line unless a jump is taken; it halts when control passes beyond the last line (a 'JZ r END' jump also halts).

Program:
1: JZ a 6
2: INC b
3: INC b
4: DEC a
5: JZ a 1
6: JZ b END
7: DEC b
8: DEC b
9: DEC b
10: JZ b 6

What is the value of register b when the program halts?
The answer is a single integer.

Answer:
0

Prompt:
A counter machine has registers a, b holding non-negative integers, initially a = 1, b = 2. Its program is the following labeled list of lines. On each line, INC r adds 1 to register r, DEC r subtracts 1 from register r (capped at 0), and 'JZ r L' jumps to the line labeled L when register r is 0, otherwise it continues to the next line. Execution starts at line 1 and runs one instruction at a time, continuing to the next line unless a jump is taken; it halts when control passes beyond the last line (a 'JZ r END' jump also halts).

Program:
1: JZ a 5
2: INC a
3: DEC a
4: JZ a 1
5: JZ a END
6: INC a
7: INC a
8: DEC a
9: JZ a 5

How many instructions are executed in total from the first line until the program halts?
The answer is a single integer.

Answer:
9
## Level 2

Prompt:
A counter machine has registers a, b, c holding non-negative integers, initially a = 1, b = 1, c = 2. Its program is the following labeled list of lines. On each line, INC r adds 1 to register r, DEC r subtracts 1 from register r (capped at 0), and 'JZ r L' jumps to the line labeled L when register r is 0, otherwise it continues to the next line. Execution starts at line 1 and runs one instruction at a time, continuing to the next line unless a jump is taken; it halts when control passes beyond the last line (a 'JZ r END' jump also halts).

Program:
1: JZ b 14
2: JZ c 7
3: INC a
4: DEC a
5: DEC c
6: JZ c 2
7: DEC c
8: JZ a 12
9: INC c
10: DEC a
11: JZ a 8
12: DEC b
13: JZ b 1
14: JZ b 20
15: DEC b
16: DEC b
17: INC b
18: DEC b
19: JZ b 14
20: JZ c END
21: JZ a 25
22: INC c
23: DEC a
24: JZ a 21
25: DEC c
26: JZ c 20

Give the value of register c after each executed instruction, in the order they execute. The first entry is its value after the first instruction, and so on.
The answer is a comma-separated list of integers.

Answer:
2,2,2,2,1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0

Prompt:
A counter machine has registers a, b, c holding non-negative integers, initially a = 3, b = 3, c = 2. Its program is the following labeled list of lines. On each line, INC r adds 1 to register r, DEC r subtracts 1 from register r (capped at 0), and 'JZ r L' jumps to the line labeled L when register r is 0, otherwise it continues to the next line. Execution starts at line 1 and runs one instruction at a time, continuing to the next line unless a jump is taken; it halts when control passes beyond the last line (a 'JZ r END' jump also halts).

Program:
1: JZ c 12
2: DEC b
3: INC c
4: INC c
5: JZ a 10
6: INC c
7: DEC b
8: DEC a
9: JZ a 5
10: DEC c
11: JZ c 1
12: JZ b 26
13: INC a
14: INC c
15: JZ b 20
16: DEC a
17: INC a
18: DEC b
19: JZ b 15
20: JZ c 24
21: INC b
22: DEC c
23: JZ c 20
24: DEC b
25: JZ b 12
26: JZ b END
27: JZ c 31
28: DEC a
29: DEC c
30: JZ c 27
31: INC c
32: INC b
33: DEC b
34: DEC b
35: JZ b 26

Give the value of register b after each executed instruction, in the order they execute. The first entry is its value after the first instruction, and so on.
The answer is a comma-separated list of integers.

Answer:
3,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,0,0,0,0
## Level 5

Prompt:
A counter machine has registers a, b, c, d holding non-negative integers, initially a = 1, b = 0, c = 3, d = 7. Its program is the following labeled list of lines. On each line, INC r adds 1 to register r, DEC r subtracts 1 from register r (capped at 0), and 'JZ r L' jumps to the line labeled L when register r is 0, otherwise it continues to the next line. Execution starts at line 1 and runs one instruction at a time, continuing to the next line unless a jump is taken; it halts when control passes beyond the last line (a 'JZ r END' jump also halts).

Program:
1: JZ c 21
2: JZ d 9
3: INC a
4: INC a
5: INC c
6: DEC b
7: DEC d
8: JZ d 2
9: JZ d 13
10: DEC b
11: DEC d
12: JZ d 9
13: DEC b
14: JZ b 19
15: INC a
16: INC a
17: DEC b
18: JZ b 14
19: DEC c
20: JZ c 1
21: JZ a 50
22: JZ c 26
23: INC a
24: DEC c
25: JZ c 22
26: DEC b
27: DEC d
28: JZ d 34
29: INC b
30: DEC b
31: DEC b
32: DEC d
33: JZ d 28
34: JZ c 40
35: INC d
36: DEC a
37: INC b
38: DEC c
39: JZ c 34
40: DEC a
41: JZ c 48
42: DEC b
43: DEC b
44: INC d
45: INC d
46: DEC c
47: JZ c 41
48: DEC a
49: JZ a 21
50: JZ d 75
51: JZ d 56
52: INC c
53: INC c
54: DEC d
55: JZ d 51
56: JZ a 65
57: INC c
58: INC d
59: INC b
60: DEC d
61: DEC c
62: DEC c
63: DEC a
64: JZ a 56
65: JZ a 71
66: INC c
67: DEC b
68: DEC b
69: DEC a
70: JZ a 65
71: INC c
72: DEC c
73: DEC d
74: JZ d 50
75: JZ a END
76: INC b
77: JZ c 83
78: DEC d
79: INC b
80: INC d
81: DEC c
82: JZ c 77
83: DEC a
84: JZ a 75

How many instructions are executed in total from the first line until the program halts?
The answer is a single integer.

Answer:
68

Prompt:
A counter machine has registers a, b, c, d holding non-negative integers, initially a = 3, b = 3, c = 1, d = 4. Its program is the following labeled list of lines. On each line, INC r adds 1 to register r, DEC r subtracts 1 from register r (capped at 0), and 'JZ r L' jumps to the line labeled L when register r is 0, otherwise it continues to the next line. Execution starts at line 1 and runs one instruction at a time, continuing to the next line unless a jump is taken; it halts when control passes beyond the last line (a 'JZ r END' jump also halts).

Program:
1: JZ a 21
2: INC c
3: DEC a
4: DEC c
5: JZ b 9
6: INC a
7: DEC b
8: JZ b 5
9: INC c
10: JZ d 18
11: INC c
12: INC a
13: DEC a
14: DEC a
15: INC a
16: DEC d
17: JZ d 10
18: DEC b
19: DEC a
20: JZ a 1
21: JZ c 48
22: JZ b 31
23: DEC d
24: INC a
25: INC c
26: DEC a
27: INC d
28: INC a
29: DEC b
30: JZ b 22
31: JZ d 39
32: INC b
33: DEC b
34: INC a
35: DEC c
36: DEC c
37: DEC d
38: JZ d 31
39: INC c
40: DEC c
41: DEC a
42: JZ c 46
43: INC b
44: DEC c
45: JZ c 42
46: DEC c
47: JZ c 21
48: JZ c 65
49: JZ d 54
50: DEC b
51: DEC a
52: DEC d
53: JZ d 49
54: JZ a 61
55: INC d
56: INC d
57: DEC c
58: DEC c
59: DEC a
60: JZ a 54
61: DEC d
62: INC a
63: DEC c
64: JZ c 48
65: JZ b END
66: JZ d 71
67: DEC a
68: DEC b
69: DEC d
70: JZ d 66
71: DEC a
72: DEC b
73: JZ a 78
74: DEC b
75: INC b
76: DEC a
77: JZ a 73
78: JZ a 83
79: INC b
80: INC c
81: DEC a
82: JZ a 78
83: DEC b
84: JZ b 65

Give the value of register a after each executed instruction, in the order they execute. The first entry is its value after the first instruction, and so on.
The answer is a comma-separated list of integers.

Answer:
3,3,2,2,2,3,3,3,3,3,3,4,3,2,3,3,3,3,2,2,2,2,2,3,3,2,2,3,3,3,3,3,3,3,4,4,4,4,4,4,4,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,1,1,1,1,1,0,0,0,0,0,0,0

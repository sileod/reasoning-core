## Level 0
### Example 1
Prompt:
Cells hold values from the alphabet 0..1; '?' marks a missing state. Several spatial slices (runs) were produced by a single unknown update rule that maps every length-3 neighborhood (this position plus 1 left and 1 right) to the next value of the center cell, acting identically on every run. Each run advances one row per time step; edge columns never update.

Run 1:
1???1?1
1?1?101
0?0010?
?111??1
0???1?1

Run 2:
1?1?001
100?110
0111?11
?1010?0
?101011

Recover the rule entries that the data forces: every entry whose length-3 neighborhood and center successor are both fully visible (no '?') in at least one run. Write each as INDEX:VALUE, where INDEX is the neighborhood read left-to-right as a base-2 number (all-zero window has INDEX 0), and VALUE is the forced successor. List the entries in ascending INDEX, separated by spaces (format: '2:1 5:0').
Answer:
1:1 2:1 3:1 4:1 5:0 6:1 7:0

### Example 2
Prompt:
Cells hold values from the alphabet 0..1; '?' marks a missing state. Several spatial slices (runs) were produced by a single unknown update rule that maps every length-3 neighborhood (this position plus 1 left and 1 right) to the next value of the center cell, acting identically on every run. Each run advances one row per time step; edge columns never update.

Run 1:
00?0???
1010010
?010?11
00??00?
00?0?11

Run 2:
1?10101
0?10101
0010101
??10101
00101?1

Recover the rule entries that the data forces: every entry whose length-3 neighborhood and center successor are both fully visible (no '?') in at least one run. Write each as INDEX:VALUE, where INDEX is the neighborhood read left-to-right as a base-2 number (all-zero window has INDEX 0), and VALUE is the forced successor. List the entries in ascending INDEX, separated by spaces (format: '2:1 5:0').
Answer:
1:0 2:1 5:0

## Level 2
### Example 1
Prompt:
Cells hold values from the alphabet 0..1; '?' marks a missing state. Several spatial slices (runs) were produced by a single unknown update rule that maps every length-3 neighborhood (this position plus 1 left and 1 right) to the next value of the center cell, acting identically on every run. Each run advances one row per time step; edge columns never update.

Run 1:
0?0?1?011
111111111
0111???11
1111?111?
111?11?0?
?11?110?1
1?1???0?1

Run 2:
00000010?
00?001100
10?011010
??0110010
1?01??110
10010?10?
11?10?011

Run 3:
????0??1?
0000?10?0
00??1??1?
10110??1?
0?1001111
111111111
1?1?1111?

Recover the rule entries that the data forces: every entry whose length-3 neighborhood and center successor are both fully visible (no '?') in at least one run. Write each as INDEX:VALUE, where INDEX is the neighborhood read left-to-right as a base-2 number (all-zero window has INDEX 0), and VALUE is the forced successor. List the entries in ascending INDEX, separated by spaces (format: '2:1 5:0').
Answer:
0:0 1:1 2:1 3:0 4:1 5:0 6:1 7:1

### Example 2
Prompt:
Cells hold values from the alphabet 0..1; '?' marks a missing state. Several spatial slices (runs) were produced by a single unknown update rule that maps every length-3 neighborhood (this position plus 1 left and 1 right) to the next value of the center cell, acting identically on every run. Each run advances one row per time step; edge columns never update.

Run 1:
11?00010?
01000?111
11?01?11?
?00??1101
00111?0??
??1110110
011??110?

Run 2:
?01100??0
111???100
010?1100?
0?01100??
1?110?11?
011001111
?10011110

Run 3:
?1000000?
?1?000001
?10?0?01?
00?0??110
000?????1
1?00110?1
0??11011?

Recover the rule entries that the data forces: every entry whose length-3 neighborhood and center successor are both fully visible (no '?') in at least one run. Write each as INDEX:VALUE, where INDEX is the neighborhood read left-to-right as a base-2 number (all-zero window has INDEX 0), and VALUE is the forced successor. List the entries in ascending INDEX, separated by spaces (format: '2:1 5:0').
Answer:
0:0 1:0 2:1 3:0 4:1 5:1 6:1 7:1

## Level 5
### Example 1
Prompt:
Cells hold values from the alphabet 0..2; '?' marks a missing state. Several spatial slices (runs) were produced by a single unknown update rule that maps every length-5 neighborhood (this position plus 2 left and 2 right) to the next value of the center cell, acting identically on every run. Each run advances one row per time step; edge columns never update.

Run 1:
??0??102?002
010?0????011
?200?0211?01
?1??020?0010
002?00?1002?
?1????00??21
021?020??201
2???020???00
11?22?020???
00??2?00??1?

Run 2:
00????1??2?1
??2010??1??0
?2???211?2??
?212022?0???
?01000?21???
??0?21?0??2?
2?00?2210?20
?1?01?020??0
21??????0000
12221?2?10?2

Run 3:
?11?????011?
1?212201200?
0?1??211110?
000?01000??1
?100??210??0
?2??201???02
2??1???100??
?100???0211?
2?01??1011?0
??10??120??1

Run 4:
0?2?0002??10
2????0???211
010???2??2?2
?1???1?2??21
?12?111?2???
2??200????01
??00?1??11?2
12?021??220?
?????0?00??2
???2220?01?2

Run 5:
21?0?121??00
2?10??121200
122010?121?2
0?2122?11?12
??21?21?2?10
2122???11???
???2??22?10?
?121?20?1?2?
11?11?200201
?22?02?00?0?

Recover the rule entries that the data forces: every entry whose length-5 neighborhood and center successor are both fully visible (no '?') in at least one run. Write each as INDEX:VALUE, where INDEX is the neighborhood read left-to-right as a base-3 number (all-zero window has INDEX 0), and VALUE is the forced successor. List the entries in ascending INDEX, separated by spaces (format: '2:1 5:0').
Answer:
3:2 21:1 23:1 35:1 40:0 56:0 65:1 70:2 106:2 122:0 185:0 197:1 223:0

### Example 2
Prompt:
Cells hold values from the alphabet 0..2; '?' marks a missing state. Several spatial slices (runs) were produced by a single unknown update rule that maps every length-5 neighborhood (this position plus 2 left and 2 right) to the next value of the center cell, acting identically on every run. Each run advances one row per time step; edge columns never update.

Run 1:
2??11??0?22?
?2?221?00100
?1?1??1???12
002???2?112?
?1???2?0?1?1
0010??2?0??1
22??01??00??
?112??2?2?0?
10??0?1?????
01210?10?0??

Run 2:
?1?1???00?22
2???1?2?2012
20????012101
101?011?02?2
???2221?1112
???2??2?0?0?
2?0?1?0?????
?202?2?120??
0???0011?2??
???010?22??1

Run 3:
21?1221?1???
??12??2?0???
11?0??0022??
121??0?01?2?
?10??0111112
110?1????100
0??112?1???2
122?101?010?
0??1?0?1????
01?12?21????

Run 4:
122?01?12120
221??11111?1
?1???1???12?
2?201?1?122?
22?22?1?2?11
?110001??21?
???0?0??2?00
?20?0010200?
2????0???20?
?021????21?2

Run 5:
??111?2?0?1?
1??1?020?2??
??1?2?011???
???11022012?
0?2?11???2??
???2?2?0?21?
0???02?221??
02?0??210?1?
??0122?22??1
1?1102??1?1?

Recover the rule entries that the data forces: every entry whose length-5 neighborhood and center successor are both fully visible (no '?') in at least one run. Write each as INDEX:VALUE, where INDEX is the neighborhood read left-to-right as a base-3 number (all-zero window has INDEX 0), and VALUE is the forced successor. List the entries in ascending INDEX, separated by spaces (format: '2:1 5:0').
Answer:
4:0 48:0 70:1 97:2 202:1 220:1

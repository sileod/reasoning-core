# Samples: evidential_felicity_verdicts (P003v1)


## Level 0

### Prompt

An archive tracks warrants for evidential forms, not whether claims are true. All timestamps are archive times; each P names one fixed past event.
Use these stipulated felicity rules (DAG dependency evaluation): seeing or hearing the event itself supplies direct evidence; being told supplies reportative evidence, never direct; a logged inference supplies inferential evidence. Accept every logged inference rule, but require all its cited premises.
At a clause's time, a record is active iff it has occurred, has not been withdrawn by then, and every cited record is recursively active. Withdrawal is globally known and permanent: even earlier reports/inferences lose their warrant when a cited ancestor is withdrawn. Other records persist. No unlogged evidence or transfers count. The recipient's type is the record's own type, not its source's type. A type is licensed iff at least one active record of that type belongs to the clause's speaker for that exact P.
In set clauses list all licensed types. In clash clauses only the highest-priority licensed type survives; unlicensed types cannot win. Each clause has at least one licensed type.
Return one line per numbered clause, in order, without numbering. Each line is a comma-separated alphabetical list of lowercase type names, without duplicates; a clash line is a single name. Format example for two clauses:
direct,reportative
inferential

P1: the lamp flashed at noon.
P2: the pump stopped at noon.
P3: the gate opened at noon.

t=1, E1: Selma heard the event P2 itself firsthand.
t=3, E2: Selma heard the event P1 itself firsthand.
t=5, E3: Mara heard the event P1 itself firsthand.
t=7, E4: Mara inferred P2 using all of E3.
t=9, E5: Selma was told P2 by Mara, citing E4.
t=11, E6: Mara was told P2 by Selma, citing E1.
t=13, E7: Owen saw the event P3 itself firsthand.
t=14: E7 was withdrawn.
t=15, E8: Selma inferred P2 using all of E1,E2.
t=17, E9: Selma was told P2 by Mara, citing E6.
t=19, E10: Mara was told P3 by Owen, citing E7.

Clauses:
1. At t=20, Selma asserts P2; list every licensed type.
2. At t=17, Selma asserts P2; list every licensed type.
Return only the verdict lines.


### Answer

direct,inferential,reportative
direct,inferential,reportative

### Prompt

An archive tracks warrants for evidential forms, not whether claims are true. All timestamps are archive times; each P names one fixed past event.
Use these stipulated felicity rules (DAG dependency evaluation): seeing or hearing the event itself supplies direct evidence; being told supplies reportative evidence, never direct; a logged inference supplies inferential evidence. Accept every logged inference rule, but require all its cited premises.
At a clause's time, a record is active iff it has occurred, has not been withdrawn by then, and every cited record is recursively active. Withdrawal is globally known and permanent: even earlier reports/inferences lose their warrant when a cited ancestor is withdrawn. Other records persist. No unlogged evidence or transfers count. The recipient's type is the record's own type, not its source's type. A type is licensed iff at least one active record of that type belongs to the clause's speaker for that exact P.
In set clauses list all licensed types. In clash clauses only the highest-priority licensed type survives; unlicensed types cannot win. Each clause has at least one licensed type.
Return one line per numbered clause, in order, without numbering. Each line is a comma-separated alphabetical list of lowercase type names, without duplicates; a clash line is a single name. Format example for two clauses:
direct,reportative
inferential

P1: the pump stopped at noon.
P2: the lamp flashed at noon.
P3: the gate opened at noon.

t=1, E1: Selma saw the event P1 itself firsthand.
t=3, E2: Bruno heard the event P2 itself firsthand.
t=5, E3: Owen heard the event P1 itself firsthand.
t=7, E4: Owen inferred P2 using all of E3.
t=9, E5: Owen inferred P3 using all of E4.
t=11, E6: Bruno heard the event P2 itself firsthand.
t=13, E7: Bruno inferred P1 using all of E6.
t=15, E8: Owen saw the event P1 itself firsthand.
t=16: E3 was withdrawn.
t=17, E9: Owen was told P2 by Bruno, citing E6.
t=19, E10: Selma was told P1 by Owen, citing E8.

Clauses:
1. At t=21, Owen asserts P2; list every licensed type.
2. At t=12, Owen asserts P1; list every licensed type.
Return only the verdict lines.


### Answer

reportative
direct


## Level 2

### Prompt

An archive tracks warrants for evidential forms, not whether claims are true. All timestamps are archive times; each P names one fixed past event.
Use these stipulated felicity rules (DAG dependency evaluation): seeing or hearing the event itself supplies direct evidence; being told supplies reportative evidence, never direct; a logged inference supplies inferential evidence. Accept every logged inference rule, but require all its cited premises.
At a clause's time, a record is active iff it has occurred, has not been withdrawn by then, and every cited record is recursively active. Withdrawal is globally known and permanent: even earlier reports/inferences lose their warrant when a cited ancestor is withdrawn. Other records persist. No unlogged evidence or transfers count. The recipient's type is the record's own type, not its source's type. A type is licensed iff at least one active record of that type belongs to the clause's speaker for that exact P.
In set clauses list all licensed types. In clash clauses only the highest-priority licensed type survives; unlicensed types cannot win. Each clause has at least one licensed type.
Return one line per numbered clause, in order, without numbering. Each line is a comma-separated alphabetical list of lowercase type names, without duplicates; a clash line is a single name. Format example for two clauses:
direct,reportative
inferential

P1: the pump stopped at noon.
P2: the bell rang at noon.
P3: the gate opened at noon.

t=1, E1: Ines saw the event P3 itself firsthand.
t=3, E2: Bruno heard the event P3 itself firsthand.
t=5, E3: Bruno saw the event P1 itself firsthand.
t=7, E4: Ines inferred P2 using all of E1.
t=9, E5: Tilo heard the event P1 itself firsthand.
t=11, E6: Bruno was told P1 by Tilo, citing E5.
t=13, E7: Bruno heard the event P3 itself firsthand.
t=15, E8: Tilo was told P3 by Bruno, citing E7.
t=17, E9: Bruno heard the event P1 itself firsthand.
t=19, E10: Ines was told P3 by Bruno, citing E7.
t=21, E11: Tilo inferred P3 using all of E5,E8.
t=23, E12: Tilo was told P1 by Bruno, citing E9.
t=24: E6 was withdrawn.
t=25, E13: Bruno inferred P3 using all of E9.
t=27, E14: Tilo inferred P1 using all of E5,E11.
t=29, E15: Ines was told P3 by Bruno, citing E13.
t=32: E12 was withdrawn.

Clauses:
1. At t=22, Ines asserts P3; list every licensed type.
2. At t=16, Tilo asserts P3; forms clash; priority inferential > direct > reportative (highest first).
Return only the verdict lines.


### Answer

direct,reportative
reportative

### Prompt

An archive tracks warrants for evidential forms, not whether claims are true. All timestamps are archive times; each P names one fixed past event.
Use these stipulated felicity rules (DAG dependency evaluation): seeing or hearing the event itself supplies direct evidence; being told supplies reportative evidence, never direct; a logged inference supplies inferential evidence. Accept every logged inference rule, but require all its cited premises.
At a clause's time, a record is active iff it has occurred, has not been withdrawn by then, and every cited record is recursively active. Withdrawal is globally known and permanent: even earlier reports/inferences lose their warrant when a cited ancestor is withdrawn. Other records persist. No unlogged evidence or transfers count. The recipient's type is the record's own type, not its source's type. A type is licensed iff at least one active record of that type belongs to the clause's speaker for that exact P.
In set clauses list all licensed types. In clash clauses only the highest-priority licensed type survives; unlicensed types cannot win. Each clause has at least one licensed type.
Return one line per numbered clause, in order, without numbering. Each line is a comma-separated alphabetical list of lowercase type names, without duplicates; a clash line is a single name. Format example for two clauses:
direct,reportative
inferential

P1: the lamp flashed at noon.
P2: the pump stopped at noon.
P3: the gate opened at noon.

t=1, E1: Ines heard the event P1 itself firsthand.
t=3, E2: Tilo saw the event P2 itself firsthand.
t=5, E3: Tilo saw the event P1 itself firsthand.
t=7, E4: Owen was told P1 by Tilo, citing E3.
t=9, E5: Tilo was told P1 by Owen, citing E4.
t=11, E6: Owen inferred P3 using all of E4.
t=13, E7: Tilo inferred P3 using all of E2.
t=15, E8: Owen inferred P3 using all of E4.
t=17, E9: Tilo was told P3 by Owen, citing E6.
t=19, E10: Ines saw the event P1 itself firsthand.
t=21, E11: Owen heard the event P2 itself firsthand.
t=23, E12: Ines was told P2 by Tilo, citing E2.
t=25, E13: Owen was told P3 by Tilo, citing E9.
t=27, E14: Tilo was told P1 by Ines, citing E10.
t=29, E15: Owen inferred P2 using all of E4,E8.
t=30: E5 was withdrawn.
t=32: E14 was withdrawn.

Clauses:
1. At t=24, Owen asserts P1; forms clash; priority direct > inferential > reportative (highest first).
2. At t=31, Owen asserts P2; list every licensed type.
Return only the verdict lines.


### Answer

reportative
direct,inferential


## Level 5

### Prompt

An archive tracks warrants for evidential forms, not whether claims are true. All timestamps are archive times; each P names one fixed past event.
Use these stipulated felicity rules (DAG dependency evaluation): seeing or hearing the event itself supplies direct evidence; being told supplies reportative evidence, never direct; a logged inference supplies inferential evidence. Accept every logged inference rule, but require all its cited premises.
At a clause's time, a record is active iff it has occurred, has not been withdrawn by then, and every cited record is recursively active. Withdrawal is globally known and permanent: even earlier reports/inferences lose their warrant when a cited ancestor is withdrawn. Other records persist. No unlogged evidence or transfers count. The recipient's type is the record's own type, not its source's type. A type is licensed iff at least one active record of that type belongs to the clause's speaker for that exact P.
In set clauses list all licensed types. In clash clauses only the highest-priority licensed type survives; unlicensed types cannot win. Each clause has at least one licensed type.
Return one line per numbered clause, in order, without numbering. Each line is a comma-separated alphabetical list of lowercase type names, without duplicates; a clash line is a single name. Format example for two clauses:
direct,reportative
inferential

P1: the bell rang at noon.
P2: the pump stopped at noon.
P3: the lamp flashed at noon.

t=1, E1: Selma saw the event P1 itself firsthand.
t=3, E2: Tilo heard the event P1 itself firsthand.
t=5, E3: Owen heard the event P1 itself firsthand.
t=7, E4: Tilo was told P1 by Selma, citing E1.
t=9, E5: Tilo was told P1 by Selma, citing E1.
t=11, E6: Selma heard the event P3 itself firsthand.
t=13, E7: Mara heard the event P3 itself firsthand.
t=15, E8: Mara inferred P1 using all of E7.
t=17, E9: Tilo inferred P2 using all of E5.
t=19, E10: Owen was told P3 by Mara, citing E7.
t=21, E11: Owen inferred P2 using all of E10.
t=23, E12: Mara was told P3 by Owen, citing E10.
t=25, E13: Owen was told P3 by Mara, citing E12.
t=27, E14: Owen inferred P2 using all of E10,E13.
t=28: E6 was withdrawn.
t=29, E15: Mara was told P3 by Owen, citing E10.
t=31, E16: Owen heard the event P1 itself firsthand.
t=33, E17: Mara inferred P2 using all of E12.
t=35, E18: Owen inferred P3 using all of E3,E16.
t=36: E14 was withdrawn.
t=37, E19: Mara was told P3 by Owen, citing E10.
t=39, E20: Mara inferred P2 using all of E8,E19.
t=41, E21: Owen inferred P2 using all of E11,E16.
t=43, E22: Owen was told P2 by Mara, citing E20.
t=44: E22 was withdrawn.

Clauses:
1. At t=42, Owen asserts P3; forms clash; priority inferential > direct > reportative (highest first).
2. At t=40, Owen asserts P3; forms clash; priority reportative > direct > inferential (highest first).
3. At t=23, Mara asserts P1; forms clash; priority reportative > direct > inferential (highest first).
Return only the verdict lines.


### Answer

inferential
reportative
inferential

### Prompt

An archive tracks warrants for evidential forms, not whether claims are true. All timestamps are archive times; each P names one fixed past event.
Use these stipulated felicity rules (DAG dependency evaluation): seeing or hearing the event itself supplies direct evidence; being told supplies reportative evidence, never direct; a logged inference supplies inferential evidence. Accept every logged inference rule, but require all its cited premises.
At a clause's time, a record is active iff it has occurred, has not been withdrawn by then, and every cited record is recursively active. Withdrawal is globally known and permanent: even earlier reports/inferences lose their warrant when a cited ancestor is withdrawn. Other records persist. No unlogged evidence or transfers count. The recipient's type is the record's own type, not its source's type. A type is licensed iff at least one active record of that type belongs to the clause's speaker for that exact P.
In set clauses list all licensed types. In clash clauses only the highest-priority licensed type survives; unlicensed types cannot win. Each clause has at least one licensed type.
Return one line per numbered clause, in order, without numbering. Each line is a comma-separated alphabetical list of lowercase type names, without duplicates; a clash line is a single name. Format example for two clauses:
direct,reportative
inferential

P1: the pump stopped at noon.
P2: the lamp flashed at noon.
P3: the gate opened at noon.

t=1, E1: Owen heard the event P3 itself firsthand.
t=3, E2: Selma heard the event P2 itself firsthand.
t=5, E3: Mara saw the event P2 itself firsthand.
t=7, E4: Mara was told P3 by Owen, citing E1.
t=9, E5: Bruno was told P3 by Mara, citing E4.
t=11, E6: Owen inferred P2 using all of E1.
t=13, E7: Bruno was told P2 by Owen, citing E6.
t=15, E8: Owen was told P2 by Mara, citing E3.
t=17, E9: Bruno was told P2 by Selma, citing E2.
t=19, E10: Bruno heard the event P1 itself firsthand.
t=21, E11: Mara inferred P1 using all of E3.
t=23, E12: Selma was told P2 by Owen, citing E8.
t=25, E13: Mara saw the event P3 itself firsthand.
t=26: E5 was withdrawn.
t=27, E14: Mara was told P1 by Bruno, citing E10.
t=29, E15: Selma was told P1 by Mara, citing E11.
t=31, E16: Bruno inferred P3 using all of E7.
t=33, E17: Selma inferred P3 using all of E12.
t=35, E18: Owen was told P3 by Mara, citing E13.
t=36: E6 was withdrawn.
t=37, E19: Selma was told P3 by Bruno, citing E16.
t=39, E20: Owen was told P3 by Bruno, citing E16.
t=40: E19 was withdrawn.
t=41, E21: Selma inferred P2 using all of E17.
t=43, E22: Bruno was told P3 by Owen, citing E18.

Clauses:
1. At t=42, Selma asserts P3; list every licensed type.
2. At t=29, Bruno asserts P2; forms clash; priority reportative > inferential > direct (highest first).
3. At t=34, Owen asserts P2; forms clash; priority reportative > inferential > direct (highest first).
Return only the verdict lines.


### Answer

inferential
reportative
reportative

# samples_P001v1

## Level 0

### Example 1

A featural word is realized as a surface string by choosing exponents for its adjacent features. Spell the word out with the greedy algorithm described below and give the surface word.

The word has 2 adjacent features in this fixed order: PP=III, PN=Pl.

Single-feature exponents (used only when the feature is not merged into a portmanteau): P1 spells 'io'; P2 spells 'e'.

A portmanteau may merge features P1 and P2 for the listed value pairs: [II, Sg]->'non', [I, Sg]->'ram'.
There are no blocking boundaries.

Greedy spell-out: process the merge candidates in the precedence order pair12. A merge is usable if it crosses no blocking boundary and its value pair/triple has a portmanteau entry, and if none of its positions is already covered by a taken merge; take it, then take remaining merges in order. Finally realize every still-uncovered feature singly (with its contextual allomorph if flagged).

Give the surface word only.

Answer: ioe

### Example 2

A featural word is realized as a surface string by choosing exponents for its adjacent features. Spell the word out with the greedy algorithm described below and give the surface word.

The word has 2 adjacent features in this fixed order: PP=I, PN=Sg.

Single-feature exponents (used only when the feature is not merged into a portmanteau): P1 spells 'au'; P2 spells 'ei'.

A portmanteau may merge features P1 and P2 for the listed value pairs: [II, Sg]->'kun'.
There are no blocking boundaries.

Greedy spell-out: process the merge candidates in the precedence order pair12. A merge is usable if it crosses no blocking boundary and its value pair/triple has a portmanteau entry, and if none of its positions is already covered by a taken merge; take it, then take remaining merges in order. Finally realize every still-uncovered feature singly (with its contextual allomorph if flagged).

Give the surface word only.

Answer: auei

## Level 2

### Example 1

A featural word is realized as a surface string by choosing exponents for its adjacent features. Spell the word out with the greedy algorithm described below and give the surface word.

The word has 2 adjacent features in this fixed order: PP=III, PN=Sg.

Single-feature exponents (used only when the feature is not merged into a portmanteau): P1 is CONTEXTUAL; P2 is CONTEXTUAL.
P1 spells its contextual allomorph by the NEXT feature's value: 'Pl'->'ex', 'Sg'->'a1'
P2 spells its contextual allomorph by the PREVIOUS feature's value: 'I'->'a3', 'II'->'uea', 'III'->'uw'

A portmanteau may merge features P1 and P2 for the listed value pairs: [III, Pl]->'mos', [III, Sg]->'sel', [II, Pl]->'vor', [II, Sg]->'mos', [I, Pl]->'dil'.
There are no blocking boundaries.

Greedy spell-out: process the merge candidates in the precedence order pair12. A merge is usable if it crosses no blocking boundary and its value pair/triple has a portmanteau entry, and if none of its positions is already covered by a taken merge; take it, then take remaining merges in order. Finally realize every still-uncovered feature singly (with its contextual allomorph if flagged).

Give the surface word only.

Answer: sel

### Example 2

A featural word is realized as a surface string by choosing exponents for its adjacent features. Spell the word out with the greedy algorithm described below and give the surface word.

The word has 2 adjacent features in this fixed order: PP=III, PN=Pl.

Single-feature exponents (used only when the feature is not merged into a portmanteau): P1 spells 'au'; P2 is CONTEXTUAL.
P2 spells its contextual allomorph by the PREVIOUS feature's value: 'I'->'a1', 'II'->'auw', 'III'->'ua'

A portmanteau may merge features P1 and P2 for the listed value pairs: [III, Pl]->'tis', [II, Pl]->'non', [II, Sg]->'ram', [I, Sg]->'mos'.
Blocking boundaries: between P1 and P2 are blocked, so no portmanteau may cross them.

Greedy spell-out: process the merge candidates in the precedence order pair12. A merge is usable if it crosses no blocking boundary and its value pair/triple has a portmanteau entry, and if none of its positions is already covered by a taken merge; take it, then take remaining merges in order. Finally realize every still-uncovered feature singly (with its contextual allomorph if flagged).

Give the surface word only.

Answer: auua

## Level 5

### Example 1

A featural word is realized as a surface string by choosing exponents for its adjacent features. Spell the word out with the greedy algorithm described below and give the surface word.

The word has 3 adjacent features in this fixed order: PP=III, PN=Sg, PG=M.

Single-feature exponents (used only when the feature is not merged into a portmanteau): P1 spells 'a'; P2 spells 'u'; P3 is CONTEXTUAL.
P3 spells its contextual allomorph by the PREVIOUS feature's value: 'Pl'->'ue1', 'Sg'->'aux'

A portmanteau may merge features P1 and P2 for the listed value pairs: [III, Pl]->'sel', [III, Sg]->'sel', [II, Sg]->'non', [I, Sg]->'vor'.
A portmanteau may merge features P2 and P3 for the listed value pairs: [Pl, F]->'sel', [Sg, F]->'mos', [Sg, M]->'sel'.
A portmanteau may merge all three features for the listed value triples: [III, Sg, F]->'valdo', [II, Pl, F]->'lunra', [II, Pl, M]->'serpo', [II, Sg, F]->'mixto', [I, Pl, M]->'kador', [I, Sg, F]->'serpo'.
Blocking boundaries: between P1 and P2 are blocked, so no portmanteau may cross them.

Greedy spell-out: process the merge candidates in the precedence order triple123, pair23, pair12. A merge is usable if it crosses no blocking boundary and its value pair/triple has a portmanteau entry, and if none of its positions is already covered by a taken merge; take it, then take remaining merges in order. Finally realize every still-uncovered feature singly (with its contextual allomorph if flagged).

Give the surface word only.

Answer: asel

### Example 2

A featural word is realized as a surface string by choosing exponents for its adjacent features. Spell the word out with the greedy algorithm described below and give the surface word.

The word has 3 adjacent features in this fixed order: PP=I, PN=Pl, PG=F.

Single-feature exponents (used only when the feature is not merged into a portmanteau): P1 is CONTEXTUAL; P2 spells 'oy'; P3 is CONTEXTUAL.
P1 spells its contextual allomorph by the NEXT feature's value: 'Pl'->'ia', 'Sg'->'ei2'
P3 spells its contextual allomorph by the PREVIOUS feature's value: 'Pl'->'ua', 'Sg'->'au3'

A portmanteau may merge features P1 and P2 for the listed value pairs: [III, Pl]->'dil', [II, Sg]->'dil', [I, Pl]->'mos', [I, Sg]->'vor'.
A portmanteau may merge features P2 and P3 for the listed value pairs: [Sg, M]->'tis'.
A portmanteau may merge all three features for the listed value triples: [III, Sg, M]->'mixto', [II, Pl, F]->'valdo', [II, Pl, M]->'kador', [II, Sg, M]->'mixto', [I, Pl, M]->'kador', [I, Sg, F]->'lunra', [I, Sg, M]->'kador'.
Blocking boundaries: between P1 and P2; between P2 and P3 are blocked, so no portmanteau may cross them.

Greedy spell-out: process the merge candidates in the precedence order pair12, pair23, triple123. A merge is usable if it crosses no blocking boundary and its value pair/triple has a portmanteau entry, and if none of its positions is already covered by a taken merge; take it, then take remaining merges in order. Finally realize every still-uncovered feature singly (with its contextual allomorph if flagged).

Give the surface word only.

Answer: iaoyua

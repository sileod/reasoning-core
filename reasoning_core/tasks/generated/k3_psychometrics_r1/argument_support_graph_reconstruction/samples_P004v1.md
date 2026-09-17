# Samples: argument_support_graph_reconstruction (P004v1)

## Level 0

### Example 1

Prompt:

An editor replaced each claim by a single token. The claim index is fixed, but this token list is shuffled: 2=harbor; 4=sediment; 1=cinder; 3=siphon.

Reconstruct the direct support links in the argument below by bottom-up parsing. A bare token denotes that claim. In (X because P) or (X since P), each premise in P supports X. In (given that P, X) or (P; therefore X), each premise in P also supports X. All four forms conclude X. The word "and" separates premises; a parenthesized argument used as a premise contributes only its conclusion to the enclosing link, while retaining its own internal links. Parentheses fix scope. Record only these explicit links, not transitive links.

(harbor because (siphon; therefore cinder) and sediment)

Output each edge as supporter->supported using claim indices. Sort by the supporter index numerically, then by the supported index numerically; include each edge once. Join with semicolons and no spaces. Example format: 1->3;2->3;4->5. Output only the adjacency string.

Answer: 1->2;3->1;4->2

### Example 2

Prompt:

An editor replaced each claim by a single token. The claim index is fixed, but this token list is shuffled: 1=frost; 5=reagent; 2=ledger; 4=harbor; 3=rampart.

Reconstruct the direct support links in the argument below by bottom-up parsing. A bare token denotes that claim. In (X because P) or (X since P), each premise in P supports X. In (given that P, X) or (P; therefore X), each premise in P also supports X. All four forms conclude X. The word "and" separates premises; a parenthesized argument used as a premise contributes only its conclusion to the enclosing link, while retaining its own internal links. Parentheses fix scope. Record only these explicit links, not transitive links.

(given that (given that reagent, frost) and (ledger; therefore rampart), harbor)

Output each edge as supporter->supported using claim indices. Sort by the supporter index numerically, then by the supported index numerically; include each edge once. Join with semicolons and no spaces. Example format: 1->3;2->3;4->5. Output only the adjacency string.

Answer: 1->4;2->3;3->4;5->1

## Level 2

### Example 1

Prompt:

An editor replaced each claim by a single token. The claim index is fixed, but this token list is shuffled: 8=reagent; 6=ember; 1=quartz; 7=rampart; 4=beacon; 2=harbor; 3=vent; 5=delta; 9=fathom.

Reconstruct the direct support links in the argument below by bottom-up parsing. A bare token denotes that claim. In (X because P) or (X since P), each premise in P supports X. In (given that P, X) or (P; therefore X), each premise in P also supports X. All four forms conclude X. The word "and" separates premises; a parenthesized argument used as a premise contributes only its conclusion to the enclosing link, while retaining its own internal links. Parentheses fix scope. Record only these explicit links, not transitive links.

((reagent since harbor) and (rampart since (given that delta, beacon)) and (given that vent, fathom) and quartz; therefore ember)

Output each edge as supporter->supported using claim indices. Sort by the supporter index numerically, then by the supported index numerically; include each edge once. Join with semicolons and no spaces. Example format: 1->3;2->3;4->5. Output only the adjacency string.

Answer: 1->6;2->8;3->9;4->7;5->4;7->6;8->6;9->6

### Example 2

Prompt:

An editor replaced each claim by a single token. The claim index is fixed, but this token list is shuffled: 1=rampart; 2=moss; 6=delta; 3=tide; 5=cinder; 7=vent; 4=quartz; 8=orchard.

Reconstruct the direct support links in the argument below by bottom-up parsing. A bare token denotes that claim. In (X because P) or (X since P), each premise in P supports X. In (given that P, X) or (P; therefore X), each premise in P also supports X. All four forms conclude X. The word "and" separates premises; a parenthesized argument used as a premise contributes only its conclusion to the enclosing link, while retaining its own internal links. Parentheses fix scope. Record only these explicit links, not transitive links.

(quartz because ((rampart because delta); therefore tide) and (vent because (moss because orchard)) and cinder)

Output each edge as supporter->supported using claim indices. Sort by the supporter index numerically, then by the supported index numerically; include each edge once. Join with semicolons and no spaces. Example format: 1->3;2->3;4->5. Output only the adjacency string.

Answer: 1->3;2->7;3->4;5->4;6->1;7->4;8->2

## Level 5

### Example 1

Prompt:

An editor replaced each claim by a single token. The claim index is fixed, but this token list is shuffled: 1=ember; 9=moss; 13=canopy; 10=ledger; 3=sediment; 12=tide; 8=granite; 6=cinder; 2=harbor; 7=rampart; 4=orchard; 11=lantern; 5=fathom.

Reconstruct the direct support links in the argument below by bottom-up parsing. A bare token denotes that claim. In (X because P) or (X since P), each premise in P supports X. In (given that P, X) or (P; therefore X), each premise in P also supports X. All four forms conclude X. The word "and" separates premises; a parenthesized argument used as a premise contributes only its conclusion to the enclosing link, while retaining its own internal links. Parentheses fix scope. Record only these explicit links, not transitive links.

(canopy since (tide because (ledger since (lantern because sediment))) and (cinder since moss and rampart and ember and (granite because harbor and fathom) and orchard))

Output each edge as supporter->supported using claim indices. Sort by the supporter index numerically, then by the supported index numerically; include each edge once. Join with semicolons and no spaces. Example format: 1->3;2->3;4->5. Output only the adjacency string.

Answer: 1->6;2->8;3->11;4->6;5->8;6->13;7->6;8->6;9->6;10->12;11->10;12->13

### Example 2

Prompt:

An editor replaced each claim by a single token. The claim index is fixed, but this token list is shuffled: 5=granite; 6=lantern; 15=siphon; 13=orchard; 3=delta; 14=harbor; 8=quartz; 9=rampart; 4=reagent; 10=canopy; 2=beacon; 12=vent; 7=fathom; 1=sediment; 11=ledger.

Reconstruct the direct support links in the argument below by bottom-up parsing. A bare token denotes that claim. In (X because P) or (X since P), each premise in P supports X. In (given that P, X) or (P; therefore X), each premise in P also supports X. All four forms conclude X. The word "and" separates premises; a parenthesized argument used as a premise contributes only its conclusion to the enclosing link, while retaining its own internal links. Parentheses fix scope. Record only these explicit links, not transitive links.

(lantern because (orchard because canopy) and (given that (beacon since (delta because (sediment since ledger))), rampart) and (reagent; therefore siphon) and (given that (quartz; therefore vent), granite) and (given that harbor, fathom))

Output each edge as supporter->supported using claim indices. Sort by the supporter index numerically, then by the supported index numerically; include each edge once. Join with semicolons and no spaces. Example format: 1->3;2->3;4->5. Output only the adjacency string.

Answer: 1->3;2->9;3->2;4->15;5->6;7->6;8->12;9->6;10->13;11->1;12->5;13->6;14->7;15->6

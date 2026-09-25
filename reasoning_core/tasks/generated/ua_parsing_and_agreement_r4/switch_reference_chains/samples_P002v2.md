# Samples for switch_reference_chains (P002v2)
## Level 0

Prompt:
A short story about Cora and Eve is written in a style, common in many languages, where predicate subjects are omitted and a linker marks whether each clause's subject is the same person as the previous clause's subject ('same-subject') or a different person ('different-subject'). You must recover those linkers. Note that the very first clause names its subject explicitly.

Story: Cora forgot the tickets; Eve closed the door; Cora closed the door.

Give the 2 linkers as a comma-separated list in story order, one for each clause after the first, using only the words same-subject or different-subject. Example (for two gaps): different-subject,same-subject

Answer: different-subject,different-subject

Prompt:
A short story about Cora and Alice is written in a style, common in many languages, where predicate subjects are omitted and a linker marks whether each clause's subject is the same person as the previous clause's subject ('same-subject') or a different person ('different-subject'). You must recover those linkers. Note that the very first clause names its subject explicitly.

Story: Cora forgot the tickets; Alice packed a bag; Alice closed the door.

Give the 2 linkers as a comma-separated list in story order, one for each clause after the first, using only the words same-subject or different-subject. Example (for two gaps): different-subject,same-subject

Answer: different-subject,same-subject

## Level 2

Prompt:
A short story about Finn and Dan is written in a style, common in many languages, where predicate subjects are omitted and a linker marks whether each clause's subject is the same person as the previous clause's subject ('same-subject') or a different person ('different-subject'). You must recover those linkers. Note that the very first clause names its subject explicitly.

Story: Finn left the keys; Dan packed a bag; Dan packed a bag; Dan forgot the tickets; Finn packed a bag.

Give the 4 linkers as a comma-separated list in story order, one for each clause after the first, using only the words same-subject or different-subject. Example (for two gaps): different-subject,same-subject

Answer: different-subject,same-subject,same-subject,different-subject

Prompt:
A short story about Alice and Finn is written in a style, common in many languages, where predicate subjects are omitted and a linker marks whether each clause's subject is the same person as the previous clause's subject ('same-subject') or a different person ('different-subject'). You must recover those linkers. Note that the very first clause names its subject explicitly.

Story: Finn bought a snack; Alice closed the door; Alice bought a snack; Finn left the keys; Finn packed a bag.

Give the 4 linkers as a comma-separated list in story order, one for each clause after the first, using only the words same-subject or different-subject. Example (for two gaps): different-subject,same-subject

Answer: different-subject,same-subject,different-subject,same-subject

## Level 5

Prompt:
A short story about Cora and Ben is written in a style, common in many languages, where predicate subjects are omitted and a linker marks whether each clause's subject is the same person as the previous clause's subject ('same-subject') or a different person ('different-subject'). You must recover those linkers. Note that the very first clause names its subject explicitly.

Story: Ben bought a snack; Ben packed a bag; Cora forgot the tickets; Ben forgot the tickets; Cora closed the door; Ben bought a snack; Ben packed a bag; Ben left the keys.

Give the 7 linkers as a comma-separated list in story order, one for each clause after the first, using only the words same-subject or different-subject. Example (for two gaps): different-subject,same-subject

Answer: same-subject,different-subject,different-subject,different-subject,different-subject,same-subject,same-subject

Prompt:
A short story about Ben and Finn is written in a style, common in many languages, where predicate subjects are omitted and a linker marks whether each clause's subject is the same person as the previous clause's subject ('same-subject') or a different person ('different-subject'). You must recover those linkers. Note that the very first clause names its subject explicitly.

Story: Finn forgot the tickets; Ben left the keys; Ben bought a snack; Ben bought a snack; Ben forgot the tickets; Ben packed a bag; Ben forgot the tickets; Finn locked the window.

Give the 7 linkers as a comma-separated list in story order, one for each clause after the first, using only the words same-subject or different-subject. Example (for two gaps): different-subject,same-subject

Answer: different-subject,same-subject,same-subject,same-subject,same-subject,same-subject,different-subject

## Level 0


**Prompt:**

Use greedy LZ77 parsing to tokenize the string below into (offset, length, next-symbol) triples, then list the full token stream.
At each step find the longest prefix of the remaining input that matches a substring starting anywhere in the most recent 3 characters of the already encoded text; if several sources tie for the longest match, use the one closest to the current position (smallest offset). The next symbol is the character immediately after the matched run (an unmatched character is encoded as offset 0, length 0). The string ends with the special symbol '#' which is not part of the alphabet and is encoded with the rest.

String: acbaccdbbd#
Answer each triple as offset:length:char and join the triples with semicolons, e.g. '0:0:a;1:2:b;0:0:c'.

**Answer:**

0:0:a;0:0:c;0:0:b;3:2:c;0:0:d;0:0:b;1:1:d;0:0:#


**Prompt:**

Use greedy LZ77 parsing to tokenize the string below into (offset, length, next-symbol) triples, then list the full token stream.
At each step find the longest prefix of the remaining input that matches a substring starting anywhere in the most recent 3 characters of the already encoded text; if several sources tie for the longest match, use the one closest to the current position (smallest offset). The next symbol is the character immediately after the matched run (an unmatched character is encoded as offset 0, length 0). The string ends with the special symbol '#' which is not part of the alphabet and is encoded with the rest.

String: bdadcaacbc#
Answer each triple as offset:length:char and join the triples with semicolons, e.g. '0:0:a;1:2:b;0:0:c'.

**Answer:**

0:0:b;0:0:d;0:0:a;2:1:c;3:1:a;3:1:b;2:1:#

## Level 2


**Prompt:**

Use greedy LZ77 parsing to tokenize the string below into (offset, length, next-symbol) triples, then list the full token stream.
At each step find the longest prefix of the remaining input that matches a substring starting anywhere in the most recent 5 characters of the already encoded text; if several sources tie for the longest match, use the one closest to the current position (smallest offset). The next symbol is the character immediately after the matched run (an unmatched character is encoded as offset 0, length 0). The string ends with the special symbol '#' which is not part of the alphabet and is encoded with the rest.

String: abdddcddccabbacbbd#
Answer each triple as offset:length:char and join the triples with semicolons, e.g. '0:0:a;1:2:b;0:0:c'.

**Answer:**

0:0:a;0:0:b;0:0:d;1:2:c;3:3:c;0:0:a;0:0:b;1:1:a;5:1:b;1:1:d;0:0:#


**Prompt:**

Use greedy LZ77 parsing to tokenize the string below into (offset, length, next-symbol) triples, then list the full token stream.
At each step find the longest prefix of the remaining input that matches a substring starting anywhere in the most recent 5 characters of the already encoded text; if several sources tie for the longest match, use the one closest to the current position (smallest offset). The next symbol is the character immediately after the matched run (an unmatched character is encoded as offset 0, length 0). The string ends with the special symbol '#' which is not part of the alphabet and is encoded with the rest.

String: cbcbcbabdbbddccabb#
Answer each triple as offset:length:char and join the triples with semicolons, e.g. '0:0:a;1:2:b;0:0:c'.

**Answer:**

0:0:c;0:0:b;2:4:a;2:1:d;2:1:b;3:1:d;0:0:c;1:1:a;0:0:b;1:1:#

## Level 5


**Prompt:**

Use greedy LZ77 parsing to tokenize the string below into (offset, length, next-symbol) triples, then list the full token stream.
At each step find the longest prefix of the remaining input that matches a substring starting anywhere in the most recent 8 characters of the already encoded text; if several sources tie for the longest match, use the one closest to the current position (smallest offset). The next symbol is the character immediately after the matched run (an unmatched character is encoded as offset 0, length 0). The string ends with the special symbol '#' which is not part of the alphabet and is encoded with the rest.

String: aaccaedaceeaeceabbceddbbedecaa#
Answer each triple as offset:length:char and join the triples with semicolons, e.g. '0:0:a;1:2:b;0:0:c'.

**Answer:**

0:0:a;1:1:c;1:1:a;0:0:e;0:0:d;6:2:e;1:1:a;2:1:c;4:2:b;1:1:c;5:1:d;1:1:b;1:1:e;4:1:e;0:0:c;0:0:a;1:1:#


**Prompt:**

Use greedy LZ77 parsing to tokenize the string below into (offset, length, next-symbol) triples, then list the full token stream.
At each step find the longest prefix of the remaining input that matches a substring starting anywhere in the most recent 8 characters of the already encoded text; if several sources tie for the longest match, use the one closest to the current position (smallest offset). The next symbol is the character immediately after the matched run (an unmatched character is encoded as offset 0, length 0). The string ends with the special symbol '#' which is not part of the alphabet and is encoded with the rest.

String: eaebecbddcbcccacaabcedbdcceeca#
Answer each triple as offset:length:char and join the triples with semicolons, e.g. '0:0:a;1:2:b;0:0:c'.

**Answer:**

0:0:e;0:0:a;2:1:b;2:1:c;3:1:d;1:1:c;4:1:c;1:2:a;2:2:a;8:2:e;0:0:d;4:1:d;5:1:c;6:1:e;3:1:a;0:0:#


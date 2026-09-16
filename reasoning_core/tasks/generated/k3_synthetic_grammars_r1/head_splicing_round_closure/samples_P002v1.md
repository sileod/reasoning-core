# Samples for head_splicing_round_closure (P002v1)
Trial seed: 1475571465

## Level 0

### Prompt

Head splicing acts on a pool of strings over the alphabet 0/1 plus two single-character palindromic pairing sites: a donor site D and an acceptor site A. One splice takes any string X containing a D and any string Y containing an A. Choose a D inside X and an A inside Y, writing X = P·D·Q and Y = R·A·S. The recombinant is P·D·A·S: the prefix of X up to and including its D, followed by the suffix of Y beginning at its A. One round applies every possible such splice within the current pool in parallel, and the new pool is the old pool plus all recombinants produced. Starting from the starter strings below, run exactly 1 rounds, then list the distinct recombinant strings: every string present after the rounds that was not one of the starters. Give your answer as a single list in lexicographic order using character order 0 < 1 < A < D, formatted like [s1, s2, s3].

Starters:
S1 = AD01
S2 = A1D1
S3 = 01DA

### Answer

[01DA1D1, 01DAD01, A1DA, A1DA1D1, A1DAD01, ADA, ADA1D1, ADAD01]

### Prompt

Head splicing acts on a pool of strings over the alphabet 0/1 plus two single-character palindromic pairing sites: a donor site D and an acceptor site A. One splice takes any string X containing a D and any string Y containing an A. Choose a D inside X and an A inside Y, writing X = P·D·Q and Y = R·A·S. The recombinant is P·D·A·S: the prefix of X up to and including its D, followed by the suffix of Y beginning at its A. One round applies every possible such splice within the current pool in parallel, and the new pool is the old pool plus all recombinants produced. Starting from the starter strings below, run exactly 1 rounds, then list the distinct recombinant strings: every string present after the rounds that was not one of the starters. Give your answer as a single list in lexicographic order using character order 0 < 1 < A < D, formatted like [s1, s2, s3].

Starters:
S1 = DA00
S2 = AD00
S3 = AD01

### Answer

[ADA00, ADAD00, ADAD01, DAD00, DAD01]

## Level 2

### Prompt

Head splicing acts on a pool of strings over the alphabet 0/1 plus two single-character palindromic pairing sites: a donor site D and an acceptor site A. One splice takes any string X containing a D and any string Y containing an A. Choose a D inside X and an A inside Y, writing X = P·D·Q and Y = R·A·S. The recombinant is P·D·A·S: the prefix of X up to and including its D, followed by the suffix of Y beginning at its A. One round applies every possible such splice within the current pool in parallel, and the new pool is the old pool plus all recombinants produced. Starting from the starter strings below, run exactly 1 rounds, then list the distinct recombinant strings: every string present after the rounds that was not one of the starters. Give your answer as a single list in lexicographic order using character order 0 < 1 < A < D, formatted like [s1, s2, s3].

Starters:
S1 = 00AD1
S2 = 0AD01
S3 = 0AD11

### Answer

[00ADAD01, 00ADAD1, 00ADAD11, 0ADAD01, 0ADAD1, 0ADAD11]

### Prompt

Head splicing acts on a pool of strings over the alphabet 0/1 plus two single-character palindromic pairing sites: a donor site D and an acceptor site A. One splice takes any string X containing a D and any string Y containing an A. Choose a D inside X and an A inside Y, writing X = P·D·Q and Y = R·A·S. The recombinant is P·D·A·S: the prefix of X up to and including its D, followed by the suffix of Y beginning at its A. One round applies every possible such splice within the current pool in parallel, and the new pool is the old pool plus all recombinants produced. Starting from the starter strings below, run exactly 1 rounds, then list the distinct recombinant strings: every string present after the rounds that was not one of the starters. Give your answer as a single list in lexicographic order using character order 0 < 1 < A < D, formatted like [s1, s2, s3].

Starters:
S1 = 1AD00
S2 = 00AD1
S3 = A11D0

### Answer

[00ADA11D0, 00ADAD00, 00ADAD1, 1ADA11D0, 1ADAD00, 1ADAD1, A11DA11D0, A11DAD00, A11DAD1]

## Level 5

### Prompt

Head splicing acts on a pool of strings over the alphabet 0/1 plus two single-character palindromic pairing sites: a donor site D and an acceptor site A. One splice takes any string X containing a D and any string Y containing an A. Choose a D inside X and an A inside Y, writing X = P·D·Q and Y = R·A·S. The recombinant is P·D·A·S: the prefix of X up to and including its D, followed by the suffix of Y beginning at its A. One round applies every possible such splice within the current pool in parallel, and the new pool is the old pool plus all recombinants produced. Starting from the starter strings below, run exactly 2 rounds, then list the distinct recombinant strings: every string present after the rounds that was not one of the starters. Give your answer as a single list in lexicographic order using character order 0 < 1 < A < D, formatted like [s1, s2, s3].

Starters:
S1 = 00DA11
S2 = 11A0D0
S3 = 1A0D11
S4 = A0D101

### Answer

[00DA0D0, 00DA0D101, 00DA0D11, 00DA0DA0D0, 00DA0DA0D101, 00DA0DA0D11, 00DA0DA0DA0D0, 00DA0DA0DA0D101, 00DA0DA0DA0D11, 00DA0DA0DA11, 00DA0DA11, 11A0DA0D0, 11A0DA0D101, 11A0DA0D11, 11A0DA0DA0D0, 11A0DA0DA0D101, 11A0DA0DA0D11, 11A0DA0DA0DA0D0, 11A0DA0DA0DA0D101, 11A0DA0DA0DA0D11, 11A0DA0DA0DA11, 11A0DA0DA11, 11A0DA11, 1A0DA0D0, 1A0DA0D101, 1A0DA0D11, 1A0DA0DA0D0, 1A0DA0DA0D101, 1A0DA0DA0D11, 1A0DA0DA0DA0D0, 1A0DA0DA0DA0D101, 1A0DA0DA0DA0D11, 1A0DA0DA0DA11, 1A0DA0DA11, 1A0DA11, A0DA0D0, A0DA0D101, A0DA0D11, A0DA0DA0D0, A0DA0DA0D101, A0DA0DA0D11, A0DA0DA0DA0D0, A0DA0DA0DA0D101, A0DA0DA0DA0D11, A0DA0DA0DA11, A0DA0DA11, A0DA11]

### Prompt

Head splicing acts on a pool of strings over the alphabet 0/1 plus two single-character palindromic pairing sites: a donor site D and an acceptor site A. One splice takes any string X containing a D and any string Y containing an A. Choose a D inside X and an A inside Y, writing X = P·D·Q and Y = R·A·S. The recombinant is P·D·A·S: the prefix of X up to and including its D, followed by the suffix of Y beginning at its A. One round applies every possible such splice within the current pool in parallel, and the new pool is the old pool plus all recombinants produced. Starting from the starter strings below, run exactly 2 rounds, then list the distinct recombinant strings: every string present after the rounds that was not one of the starters. Give your answer as a single list in lexicographic order using character order 0 < 1 < A < D, formatted like [s1, s2, s3].

Starters:
S1 = 10AD10
S2 = 10DA00
S3 = 11AD11
S4 = 0AD010

### Answer

[0ADA00, 0ADAD010, 0ADAD10, 0ADAD11, 0ADADA00, 0ADADAD010, 0ADADAD10, 0ADADAD11, 0ADADADA00, 0ADADADAD010, 0ADADADAD10, 0ADADADAD11, 10ADA00, 10ADAD010, 10ADAD10, 10ADAD11, 10ADADA00, 10ADADAD010, 10ADADAD10, 10ADADAD11, 10ADADADA00, 10ADADADAD010, 10ADADADAD10, 10ADADADAD11, 10DAD010, 10DAD10, 10DAD11, 10DADA00, 10DADAD010, 10DADAD10, 10DADAD11, 10DADADA00, 10DADADAD010, 10DADADAD10, 10DADADAD11, 11ADA00, 11ADAD010, 11ADAD10, 11ADAD11, 11ADADA00, 11ADADAD010, 11ADADAD10, 11ADADAD11, 11ADADADA00, 11ADADADAD010, 11ADADADAD10, 11ADADADAD11]

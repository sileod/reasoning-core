# samples_P003v1

Query a chromatid's full ordered haplotype (0/1 string) after reciprocal crossovers and directed gene-conversion tracts.

## Level 0

### Example 1

**Prompt:**

Replication of two homologous chromosomes produces four chromatids: chromatids A and B are sister chromatids on the paternal homolog whose ancestor label is 1, and chromatids C and D are sisters on the maternal homolog whose ancestor label is 0. The chromosome consists of 6 ordered markers at positions 0 through 5.
A directed gene-conversion tract copies the allele at positions 3 through 4 from chromatid D into chromatid A, overwriting A's maternal-paternal ancestor labels there.
A reciprocal crossover occurs between chromatids A and C at position 3, exchanging the segment from position 3 through the rightmost marker.
A directed gene-conversion tract copies the allele at positions 5 through 5 from chromatid A into chromatid B, overwriting B's maternal-paternal ancestor labels there.
After all events, give the full ordered haplotype of chromatid A: a single string of 6 characters, each '0' or '1', in order from position 0 to 5. Segment boundaries are implicit in runs; no separators.

**Answer:** 111000

### Example 2

**Prompt:**

Replication of two homologous chromosomes produces four chromatids: chromatids A and B are sister chromatids on the paternal homolog whose ancestor label is 1, and chromatids C and D are sisters on the maternal homolog whose ancestor label is 0. The chromosome consists of 6 ordered markers at positions 0 through 5.
A reciprocal crossover occurs between chromatids C and A at position 5, exchanging the segment from position 5 through the rightmost marker.
A reciprocal crossover occurs between chromatids C and B at position 0, exchanging the segment from position 0 through the rightmost marker.
A reciprocal crossover occurs between chromatids C and A at position 4, exchanging the segment from position 4 through the rightmost marker.
After all events, give the full ordered haplotype of chromatid C: a single string of 6 characters, each '0' or '1', in order from position 0 to 5. Segment boundaries are implicit in runs; no separators.

**Answer:** 111110

## Level 2

### Example 1

**Prompt:**

Replication of two homologous chromosomes produces four chromatids: chromatids A and B are sister chromatids on the paternal homolog whose ancestor label is 1, and chromatids C and D are sisters on the maternal homolog whose ancestor label is 0. The chromosome consists of 10 ordered markers at positions 0 through 9.
A directed gene-conversion tract copies the allele at positions 9 through 9 from chromatid A into chromatid B, overwriting B's maternal-paternal ancestor labels there.
A reciprocal crossover occurs between chromatids A and D at position 5, exchanging the segment from position 5 through the rightmost marker.
A directed gene-conversion tract copies the allele at positions 3 through 9 from chromatid A into chromatid B, overwriting B's maternal-paternal ancestor labels there.
A reciprocal crossover occurs between chromatids A and C at position 5, exchanging the segment from position 5 through the rightmost marker.
A directed gene-conversion tract copies the allele at positions 7 through 8 from chromatid A into chromatid D, overwriting D's maternal-paternal ancestor labels there.
After all events, give the full ordered haplotype of chromatid A: a single string of 10 characters, each '0' or '1', in order from position 0 to 9. Segment boundaries are implicit in runs; no separators.

**Answer:** 1111100000

### Example 2

**Prompt:**

Replication of two homologous chromosomes produces four chromatids: chromatids A and B are sister chromatids on the paternal homolog whose ancestor label is 1, and chromatids C and D are sisters on the maternal homolog whose ancestor label is 0. The chromosome consists of 10 ordered markers at positions 0 through 9.
A directed gene-conversion tract copies the allele at positions 7 through 9 from chromatid D into chromatid A, overwriting A's maternal-paternal ancestor labels there.
A directed gene-conversion tract copies the allele at positions 1 through 2 from chromatid D into chromatid B, overwriting B's maternal-paternal ancestor labels there.
A reciprocal crossover occurs between chromatids D and C at position 1, exchanging the segment from position 1 through the rightmost marker.
A reciprocal crossover occurs between chromatids D and B at position 8, exchanging the segment from position 8 through the rightmost marker.
A reciprocal crossover occurs between chromatids D and B at position 5, exchanging the segment from position 5 through the rightmost marker.
After all events, give the full ordered haplotype of chromatid D: a single string of 10 characters, each '0' or '1', in order from position 0 to 9. Segment boundaries are implicit in runs; no separators.

**Answer:** 0000011100

## Level 5

### Example 1

**Prompt:**

Replication of two homologous chromosomes produces four chromatids: chromatids A and B are sister chromatids on the paternal homolog whose ancestor label is 1, and chromatids C and D are sisters on the maternal homolog whose ancestor label is 0. The chromosome consists of 16 ordered markers at positions 0 through 15.
A reciprocal crossover occurs between chromatids A and D at position 11, exchanging the segment from position 11 through the rightmost marker.
A reciprocal crossover occurs between chromatids A and B at position 6, exchanging the segment from position 6 through the rightmost marker.
A reciprocal crossover occurs between chromatids A and B at position 9, exchanging the segment from position 9 through the rightmost marker.
A reciprocal crossover occurs between chromatids A and B at position 13, exchanging the segment from position 13 through the rightmost marker.
A reciprocal crossover occurs between chromatids A and C at position 10, exchanging the segment from position 10 through the rightmost marker.
A reciprocal crossover occurs between chromatids A and C at position 8, exchanging the segment from position 8 through the rightmost marker.
A directed gene-conversion tract copies the allele at positions 12 through 15 from chromatid A into chromatid B, overwriting B's maternal-paternal ancestor labels there.
A reciprocal crossover occurs between chromatids A and D at position 10, exchanging the segment from position 10 through the rightmost marker.
After all events, give the full ordered haplotype of chromatid A: a single string of 16 characters, each '0' or '1', in order from position 0 to 15. Segment boundaries are implicit in runs; no separators.

**Answer:** 1111111100011111

### Example 2

**Prompt:**

Replication of two homologous chromosomes produces four chromatids: chromatids A and B are sister chromatids on the paternal homolog whose ancestor label is 1, and chromatids C and D are sisters on the maternal homolog whose ancestor label is 0. The chromosome consists of 16 ordered markers at positions 0 through 15.
A directed gene-conversion tract copies the allele at positions 11 through 12 from chromatid C into chromatid A, overwriting A's maternal-paternal ancestor labels there.
A reciprocal crossover occurs between chromatids C and A at position 8, exchanging the segment from position 8 through the rightmost marker.
A reciprocal crossover occurs between chromatids C and B at position 11, exchanging the segment from position 11 through the rightmost marker.
A reciprocal crossover occurs between chromatids C and D at position 13, exchanging the segment from position 13 through the rightmost marker.
A directed gene-conversion tract copies the allele at positions 5 through 10 from chromatid A into chromatid C, overwriting C's maternal-paternal ancestor labels there.
A directed gene-conversion tract copies the allele at positions 12 through 14 from chromatid C into chromatid A, overwriting A's maternal-paternal ancestor labels there.
A directed gene-conversion tract copies the allele at positions 9 through 13 from chromatid A into chromatid C, overwriting C's maternal-paternal ancestor labels there.
A directed gene-conversion tract copies the allele at positions 6 through 11 from chromatid D into chromatid C, overwriting C's maternal-paternal ancestor labels there.
After all events, give the full ordered haplotype of chromatid C: a single string of 16 characters, each '0' or '1', in order from position 0 to 15. Segment boundaries are implicit in runs; no separators.

**Answer:** 0000010000001000


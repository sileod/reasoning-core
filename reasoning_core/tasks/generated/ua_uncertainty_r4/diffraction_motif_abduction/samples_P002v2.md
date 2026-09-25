# Diffraction Motif Abduction v2 (P002v2) Samples

## Level 0

**Prompt**

A repeating motif is a cyclic sequence of P phase signs (weights), each entry one of +, - or 0. Its diffraction gives a reflection at angular shift k of S(k) = sum_{(i=0)}^{P-1} w[i] * w[(i+k) mod P]. A reflection is ALLOWED when S(k) is nonzero and EXTINGUISHED when S(k)=0.

Observed reflection mask (length P=10): allowed '1', extinguished '0', unobserved '?':
1 1 0 1 1 1 1 1 0 1

Name a motif string over {+, -, 0} of exactly this length that is compatible with every observed reflection, i.e. whose S(k) is nonzero wherever the mask reads '1' and zero wherever it reads '0'. Any translated (rotated) copy of a compatible motif is accepted. Print only the motif string.

**Answer**

0+-0--+--0

**Prompt**

A repeating motif is a cyclic sequence of P phase signs (weights), each entry one of +, - or 0. Its diffraction gives a reflection at angular shift k of S(k) = sum_{(i=0)}^{P-1} w[i] * w[(i+k) mod P]. A reflection is ALLOWED when S(k) is nonzero and EXTINGUISHED when S(k)=0.

Observed reflection mask (length P=8): allowed '1', extinguished '0', unobserved '?':
1 1 0 0 1 0 0 1

Name a motif string over {+, -, 0} of exactly this length that is compatible with every observed reflection, i.e. whose S(k) is nonzero wherever the mask reads '1' and zero wherever it reads '0'. Any translated (rotated) copy of a compatible motif is accepted. Print only the motif string.

**Answer**

-00+0-0-

## Level 2

**Prompt**

A repeating motif is a cyclic sequence of P phase signs (weights), each entry one of +, - or 0. Its diffraction gives a reflection at angular shift k of S(k) = sum_{(i=0)}^{P-1} w[i] * w[(i+k) mod P]. A reflection is ALLOWED when S(k) is nonzero and EXTINGUISHED when S(k)=0.

Observed reflection mask (length P=11): allowed '1', extinguished '0', unobserved '?':
1 1 1 ? 1 1 1 1 0 1 1

Name a motif string over {+, -, 0} of exactly this length that is compatible with every observed reflection, i.e. whose S(k) is nonzero wherever the mask reads '1' and zero wherever it reads '0'. Any translated (rotated) copy of a compatible motif is accepted. Print only the motif string.

**Answer**

0+00+00--++

**Prompt**

A repeating motif is a cyclic sequence of P phase signs (weights), each entry one of +, - or 0. Its diffraction gives a reflection at angular shift k of S(k) = sum_{(i=0)}^{P-1} w[i] * w[(i+k) mod P]. A reflection is ALLOWED when S(k) is nonzero and EXTINGUISHED when S(k)=0.

Observed reflection mask (length P=11): allowed '1', extinguished '0', unobserved '?':
1 0 1 1 1 1 1 ? 1 ? 0

Name a motif string over {+, -, 0} of exactly this length that is compatible with every observed reflection, i.e. whose S(k) is nonzero wherever the mask reads '1' and zero wherever it reads '0'. Any translated (rotated) copy of a compatible motif is accepted. Print only the motif string.

**Answer**

00+++0-0-+-

## Level 5

**Prompt**

A repeating motif is a cyclic sequence of P phase signs (weights), each entry one of +, - or 0. Its diffraction gives a reflection at angular shift k of S(k) = sum_{(i=0)}^{P-1} w[i] * w[(i+k) mod P]. A reflection is ALLOWED when S(k) is nonzero and EXTINGUISHED when S(k)=0.

Observed reflection mask (length P=13): allowed '1', extinguished '0', unobserved '?':
? 1 ? ? ? 1 0 0 1 1 1 1 ?

Name a motif string over {+, -, 0} of exactly this length that is compatible with every observed reflection, i.e. whose S(k) is nonzero wherever the mask reads '1' and zero wherever it reads '0'. Any translated (rotated) copy of a compatible motif is accepted. Print only the motif string.

**Answer**

0+---0++-+-+0

**Prompt**

A repeating motif is a cyclic sequence of P phase signs (weights), each entry one of +, - or 0. Its diffraction gives a reflection at angular shift k of S(k) = sum_{(i=0)}^{P-1} w[i] * w[(i+k) mod P]. A reflection is ALLOWED when S(k) is nonzero and EXTINGUISHED when S(k)=0.

Observed reflection mask (length P=13): allowed '1', extinguished '0', unobserved '?':
1 1 1 ? 1 ? 1 1 0 1 ? ? 1

Name a motif string over {+, -, 0} of exactly this length that is compatible with every observed reflection, i.e. whose S(k) is nonzero wherever the mask reads '1' and zero wherever it reads '0'. Any translated (rotated) copy of a compatible motif is accepted. Print only the motif string.

**Answer**

-0+-0-000-+++

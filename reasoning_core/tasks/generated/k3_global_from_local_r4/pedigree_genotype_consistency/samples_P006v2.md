# Level 0
## Example 1
Prompt:
The condition follows autosomal recessive inheritance. Under this mode, affected persons are aa (two disease alleles); unaffected persons are AA or Aa. A disease allele is recessive: an affected person inherits one from each parent.

The family members (sex and phenotype):
  m0: f, unaffected
  m1: m, affected
  m2: f, unaffected
  m3: m, unaffected

Matings (a family lists the two parents then their children):
  m2 and m1 are parents of m3.

A member's genotype is forced when every genotype assignment consistent with the pedigree and the mode gives that member the same genotype. Give the forced genotype (AA, Aa or aa) of, in this exact order, m1, m3.

Answer with 2 space-separated genotype tokens in that order, for example `Aa Aa`.
Answer: aa Aa
## Example 2
Prompt:
The condition follows autosomal dominant inheritance. Under this mode, affected persons are AA or Aa; unaffected persons are aa. A single disease allele is enough to cause the disorder, so an affected child must have an affected parent.

The family members (sex and phenotype):
  m0: f, unaffected
  m1: m, affected
  m2: f, affected
  m3: m, affected

Matings (a family lists the two parents then their children):
  m0 and m1 are parents of m3.

A member's genotype is forced when every genotype assignment consistent with the pedigree and the mode gives that member the same genotype. Give the forced genotype (AA, Aa or aa) of, in this exact order, m0, m3.

Answer with 2 space-separated genotype tokens in that order, for example `Aa Aa`.
Answer: aa Aa

# Level 2
## Example 1
Prompt:
The condition follows autosomal dominant inheritance. Under this mode, affected persons are AA or Aa; unaffected persons are aa. A single disease allele is enough to cause the disorder, so an affected child must have an affected parent.

The family members (sex and phenotype):
  m0: f, unaffected
  m1: m, affected
  m2: f, unaffected
  m3: m, affected
  m4: m, affected
  m5: f, affected

Matings (a family lists the two parents then their children):
  m2 and m1 are parents of m3, m4.
  m2 and m3 are parents of m5.

A member's genotype is forced when every genotype assignment consistent with the pedigree and the mode gives that member the same genotype. Give the forced genotype (AA, Aa or aa) of, in this exact order, m0, m2, m5.

Answer with 3 space-separated genotype tokens in that order, for example `Aa Aa Aa`.
Answer: aa aa Aa
## Example 2
Prompt:
The condition follows autosomal dominant inheritance. Under this mode, affected persons are AA or Aa; unaffected persons are aa. A single disease allele is enough to cause the disorder, so an affected child must have an affected parent.

The family members (sex and phenotype):
  m0: f, affected
  m1: m, affected
  m2: f, unaffected
  m3: f, unaffected
  m4: m, affected
  m5: f, unaffected

Matings (a family lists the two parents then their children):
  m2 and m1 are parents of m3, m4.
  m2 and m1 are parents of m5.

A member's genotype is forced when every genotype assignment consistent with the pedigree and the mode gives that member the same genotype. Give the forced genotype (AA, Aa or aa) of, in this exact order, m2, m3, m4.

Answer with 3 space-separated genotype tokens in that order, for example `Aa Aa Aa`.
Answer: aa aa Aa

# Level 5
## Example 1
Prompt:
The condition follows X-linked recessive inheritance. Under this mode, for females affected are aa and unaffected are AA or Aa; for males (one X, no homologue) affected are a and unaffected are A. A male gets his X from his mother.

The family members (sex and phenotype):
  m0: f, unaffected
  m1: m, affected
  m2: f, unaffected
  m3: m, unaffected
  m4: m, unaffected
  m5: f, unaffected
  m6: f, unaffected
  m7: f, unaffected
  m8: f, unaffected

Matings (a family lists the two parents then their children):
  m2 and m1 are parents of m3, m4, m5.
  m0 and m4 are parents of m6, m7.
  m6 and m3 are parents of m8.

A member's genotype is forced when every genotype assignment consistent with the pedigree and the mode gives that member the same genotype. Give the forced genotype (AA, Aa or aa) of, in this exact order, m5, m6, m7, m8.

Answer with 4 space-separated genotype tokens in that order, for example `Aa Aa Aa Aa`.
Answer: Aa Aa Aa Aa
## Example 2
Prompt:
The condition follows X-linked recessive inheritance. Under this mode, for females affected are aa and unaffected are AA or Aa; for males (one X, no homologue) affected are a and unaffected are A. A male gets his X from his mother.

The family members (sex and phenotype):
  m0: f, unaffected
  m1: m, affected
  m2: f, unaffected
  m3: m, affected
  m4: m, unaffected
  m5: f, unaffected
  m6: f, unaffected
  m7: f, unaffected
  m8: f, unaffected

Matings (a family lists the two parents then their children):
  m2 and m1 are parents of m3, m4.
  m0 and m1 are parents of m5.
  m0 and m4 are parents of m6, m7.
  m7 and m1 are parents of m8.

A member's genotype is forced when every genotype assignment consistent with the pedigree and the mode gives that member the same genotype. Give the forced genotype (AA, Aa or aa) of, in this exact order, m0, m5, m6, m7.

Answer with 4 space-separated genotype tokens in that order, for example `Aa Aa Aa Aa`.
Answer: Aa Aa Aa Aa


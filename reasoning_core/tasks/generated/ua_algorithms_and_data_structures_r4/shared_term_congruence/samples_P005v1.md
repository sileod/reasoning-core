## Level 0

### Example
**Prompt:**
We reason about terms built from constant symbols c, b, d, a and operator symbols p/1 g/1 k/2 m/2, where each operator is applied to a fixed number of child terms (unary/binary as shown). Two terms are considered equal if they can be derived from the following given equalities by congruence closure: constants merge only when an equality says they merge, and two function terms f(c1,...,cn) and g(d1,...,dm) merge exactly when f == g, n == m, and every corresponding child ci merges with di. Given equalities: c == b. Decide, for each query pair, whether congruence closure forces the two terms to be equal. Query pairs (term1, term2): (k(c,b), k(b,b)); (p(d), p(a)); (d, a); (p(c), p(b)). Answer with one T (forced equal) or F (not forced) per query pair, in the order given, written as a single string of T/F characters (e.g. TFTF).

**Answer:**
TFFT

### Example
**Prompt:**
We reason about terms built from constant symbols b, c, a, d and operator symbols f/1 g/1 k/2 h/2, where each operator is applied to a fixed number of child terms (unary/binary as shown). Two terms are considered equal if they can be derived from the following given equalities by congruence closure: constants merge only when an equality says they merge, and two function terms f(c1,...,cn) and g(d1,...,dm) merge exactly when f == g, n == m, and every corresponding child ci merges with di. Given equalities: b == c. Decide, for each query pair, whether congruence closure forces the two terms to be equal. Query pairs (term1, term2): (k(b,c), k(c,c)); (h(b,c), h(c,c)); (b, a); (k(a,d), k(b,d)). Answer with one T (forced equal) or F (not forced) per query pair, in the order given, written as a single string of T/F characters (e.g. TFTF).

**Answer:**
TTFF

## Level 2

### Example
**Prompt:**
We reason about terms built from constant symbols b, c, a, e, d and operator symbols p/1 f/1 h/2 k/2, where each operator is applied to a fixed number of child terms (unary/binary as shown). Two terms are considered equal if they can be derived from the following given equalities by congruence closure: constants merge only when an equality says they merge, and two function terms f(c1,...,cn) and g(d1,...,dm) merge exactly when f == g, n == m, and every corresponding child ci merges with di. Given equalities: b == c. Decide, for each query pair, whether congruence closure forces the two terms to be equal. Query pairs (term1, term2): (p(b), p(c)); (k(b,c), k(c,c)); (f(b), f(a)); (h(b,c), h(c,c)); (e, d); (p(e), p(d)). Answer with one T (forced equal) or F (not forced) per query pair, in the order given, written as a single string of T/F characters (e.g. TFTF).

**Answer:**
TTFTFF

### Example
**Prompt:**
We reason about terms built from constant symbols e, a, d, c, b and operator symbols g/1 p/1 k/2 m/2, where each operator is applied to a fixed number of child terms (unary/binary as shown). Two terms are considered equal if they can be derived from the following given equalities by congruence closure: constants merge only when an equality says they merge, and two function terms f(c1,...,cn) and g(d1,...,dm) merge exactly when f == g, n == m, and every corresponding child ci merges with di. Given equalities: e == a. Decide, for each query pair, whether congruence closure forces the two terms to be equal. Query pairs (term1, term2): (p(c), p(b)); (p(e), p(a)); (k(e,a), k(a,a)); (m(e,a), m(a,a)); (e, c); (k(e,c), k(b,c)). Answer with one T (forced equal) or F (not forced) per query pair, in the order given, written as a single string of T/F characters (e.g. TFTF).

**Answer:**
FTTTFF

## Level 5

### Example
**Prompt:**
We reason about terms built from constant symbols b, g, e, c, a, d, f and operator symbols p/1 g/1 h/2 m/2, where each operator is applied to a fixed number of child terms (unary/binary as shown). Two terms are considered equal if they can be derived from the following given equalities by congruence closure: constants merge only when an equality says they merge, and two function terms f(c1,...,cn) and g(d1,...,dm) merge exactly when f == g, n == m, and every corresponding child ci merges with di. Given equalities: b == g; e == c; a == d. Decide, for each query pair, whether congruence closure forces the two terms to be equal. Query pairs (term1, term2): (g(b), g(a)); (h(b,e), h(g,c)); (h(b,b), h(g,b)); (b, f); (h(e,b), h(c,b)); (g(a), g(f)); (m(a,c), m(d,c)); (g(e), g(a)). Answer with one T (forced equal) or F (not forced) per query pair, in the order given, written as a single string of T/F characters (e.g. TFTF).

**Answer:**
FTTFTFTF

### Example
**Prompt:**
We reason about terms built from constant symbols d, f, e, c, a, g, b and operator symbols f/1 p/1 m/2 h/2, where each operator is applied to a fixed number of child terms (unary/binary as shown). Two terms are considered equal if they can be derived from the following given equalities by congruence closure: constants merge only when an equality says they merge, and two function terms f(c1,...,cn) and g(d1,...,dm) merge exactly when f == g, n == m, and every corresponding child ci merges with di. Given equalities: d == f; e == c; a == g. Decide, for each query pair, whether congruence closure forces the two terms to be equal. Query pairs (term1, term2): (d, b); (a, b); (m(a,d), m(g,d)); (h(d,e), h(f,e)); (h(d,a), h(f,g)); (f(f(d)), f(f(f))); (p(d), p(a)); (f(p(a)), f(p(b))). Answer with one T (forced equal) or F (not forced) per query pair, in the order given, written as a single string of T/F characters (e.g. TFTF).

**Answer:**
FFTTTTFF


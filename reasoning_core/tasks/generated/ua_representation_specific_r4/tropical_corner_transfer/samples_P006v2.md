## Level 0

A univariate min-plus (tropical) polynomial is f(x)=min over i of (c_i + i*x) for degrees i=0..n. It is given in coefficient-list form, listing c_0,c_1,...,c_n in order, some terms possibly inactive (never touching the lower envelope): [2,2,2,1,2,2]. Output its equivalent breakpoint (corner) form as a single canonical string. Give the active terms as comma-separated 'degree:coefficient' pairs in order of increasing degree, then a semicolon, then 'bp:' followed by the comma-separated breakpoints between consecutive active terms, where the breakpoint between active degrees a and b of coefficients c_a and c_b is (c_a-c_b)/(b-a). Only terms that are true corners (vertices of the concave lower envelope) belong in the active list; on-hull and below-hull terms are omitted. Example: the coefficient list [0,1,2,1,0] has active terms 0:0,2:2,4:0 with breakpoints -1,1, so the answer is 0:0,2:2,4:0;bp:-1,1.

**Answer:** 0:2,5:2;bp:0

A univariate min-plus (tropical) polynomial is f(x)=min over i of (c_i + i*x) for degrees i=0..n. It is given in coefficient-list form, listing c_0,c_1,...,c_n in order, some terms possibly inactive (never touching the lower envelope): [-4,-4,-4,-4,-4,-4]. Output its equivalent breakpoint (corner) form as a single canonical string. Give the active terms as comma-separated 'degree:coefficient' pairs in order of increasing degree, then a semicolon, then 'bp:' followed by the comma-separated breakpoints between consecutive active terms, where the breakpoint between active degrees a and b of coefficients c_a and c_b is (c_a-c_b)/(b-a). Only terms that are true corners (vertices of the concave lower envelope) belong in the active list; on-hull and below-hull terms are omitted. Example: the coefficient list [0,1,2,1,0] has active terms 0:0,2:2,4:0 with breakpoints -1,1, so the answer is 0:0,2:2,4:0;bp:-1,1.

**Answer:** 0:-4,5:-4;bp:0

## Level 2

A univariate min-plus (tropical) polynomial with degrees 0..6 is f(x)=min over i of (c_i + i*x). It is given in breakpoint (corner) form as comma-separated 'degree:coefficient' active terms followed by ';bp:' and the comma-separated breakpoints between consecutive active terms: 0:5,5:25,6:25;bp:-4,0. The coefficient list is concave with these corners; every non-corner degree j has coefficient c_j lying on the straight segment between its two neighboring corners (equal to c_a + s*(j-a) where the slope between neighboring corners a,b is s=(c_b-c_a)/(b-a), equivalently s=-bp). Output the full equivalent coefficient list c_0,c_1,...,c_6 as a single canonical string, a bracket-enclosed comma-separated list. Example: corners 0:0,2:2,4:0 with breakpoints -1,1 for degrees 0..4 give the answer [0,1,2,1,0].

**Answer:** [5,9,13,17,21,25,25]

A univariate min-plus (tropical) polynomial is f(x)=min over i of (c_i + i*x) for degrees i=0..n. It is given in coefficient-list form, listing c_0,c_1,...,c_n in order, some terms possibly inactive (never touching the lower envelope): [-8,-10,-8,-10,-8,-9,-10]. Output its equivalent breakpoint (corner) form as a single canonical string. Give the active terms as comma-separated 'degree:coefficient' pairs in order of increasing degree, then a semicolon, then 'bp:' followed by the comma-separated breakpoints between consecutive active terms, where the breakpoint between active degrees a and b of coefficients c_a and c_b is (c_a-c_b)/(b-a). Only terms that are true corners (vertices of the concave lower envelope) belong in the active list; on-hull and below-hull terms are omitted. Example: the coefficient list [0,1,2,1,0] has active terms 0:0,2:2,4:0 with breakpoints -1,1, so the answer is 0:0,2:2,4:0;bp:-1,1.

**Answer:** 0:-8,4:-8,6:-10;bp:0,1

## Level 5

A univariate min-plus (tropical) polynomial with degrees 0..15 is f(x)=min over i of (c_i + i*x). It is given in breakpoint (corner) form as comma-separated 'degree:coefficient' active terms followed by ';bp:' and the comma-separated breakpoints between consecutive active terms: 0:-11,4:-19,15:-74;bp:2,5. The coefficient list is concave with these corners; every non-corner degree j has coefficient c_j lying on the straight segment between its two neighboring corners (equal to c_a + s*(j-a) where the slope between neighboring corners a,b is s=(c_b-c_a)/(b-a), equivalently s=-bp). Output the full equivalent coefficient list c_0,c_1,...,c_15 as a single canonical string, a bracket-enclosed comma-separated list. Example: corners 0:0,2:2,4:0 with breakpoints -1,1 for degrees 0..4 give the answer [0,1,2,1,0].

**Answer:** [-11,-13,-15,-17,-19,-24,-29,-34,-39,-44,-49,-54,-59,-64,-69,-74]

A univariate min-plus (tropical) polynomial is f(x)=min over i of (c_i + i*x) for degrees i=0..n. It is given in coefficient-list form, listing c_0,c_1,...,c_n in order, some terms possibly inactive (never touching the lower envelope): [-2,-1,2,4,0,-4,-8,-16,-16,-20,-25,-28]. Output its equivalent breakpoint (corner) form as a single canonical string. Give the active terms as comma-separated 'degree:coefficient' pairs in order of increasing degree, then a semicolon, then 'bp:' followed by the comma-separated breakpoints between consecutive active terms, where the breakpoint between active degrees a and b of coefficients c_a and c_b is (c_a-c_b)/(b-a). Only terms that are true corners (vertices of the concave lower envelope) belong in the active list; on-hull and below-hull terms are omitted. Example: the coefficient list [0,1,2,1,0] has active terms 0:0,2:2,4:0 with breakpoints -1,1, so the answer is 0:0,2:2,4:0;bp:-1,1.

**Answer:** 0:-2,3:4,11:-28;bp:-2,4


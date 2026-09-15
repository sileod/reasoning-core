# Samples P007v1

## Level 0

### Example 1

Prompt:

Two rewrite rules over first-order terms are given in prefix notation.
  A: G(Q(e),P(M(N(1)))) -> p
  B: M(N(x)) -> T(x,3)
Form the critical pair by overlapping rule B into a proper (non-root) subterm of rule A's left-hand side: the unique occurrence in A's left-hand side whose head function symbol is M. Unify that subterm with B's left-hand side to obtain the most general unifier, apply it to both right-hand sides, and rewrite A's left-hand side at the overlap with rule B. If B's left-hand side overlaps no proper subterm of A's left-hand side, the empty result is returned as the single token NONE.
Give the answer as the two resulting terms in prefix notation, A-side first, then the overlap-rewritten side, separated by ' ; '.

Answer:

p ; G(Q(e),P(T(1,3)))

### Example 2

Prompt:

Two rewrite rules over first-order terms are given in prefix notation.
  A: D(1,L(V(0,1),Y(A(G(n,m)),T(G(1,r))))) -> E(0)
  B: Y(A(x),T(v)) -> x
Form the critical pair by overlapping rule B into a proper (non-root) subterm of rule A's left-hand side: the unique occurrence in A's left-hand side whose head function symbol is Y. Unify that subterm with B's left-hand side to obtain the most general unifier, apply it to both right-hand sides, and rewrite A's left-hand side at the overlap with rule B. If B's left-hand side overlaps no proper subterm of A's left-hand side, the empty result is returned as the single token NONE.
Give the answer as the two resulting terms in prefix notation, A-side first, then the overlap-rewritten side, separated by ' ; '.

Answer:

E(0) ; D(1,L(V(0,1),G(n,m)))

## Level 2

### Example 1

Prompt:

Two rewrite rules over first-order terms are given in prefix notation.
  A: N(q,f) -> M(Y(f,n))
  B: T(y,y) -> P(1)
Form the critical pair by overlapping rule B into a proper (non-root) subterm of rule A's left-hand side: the unique occurrence in A's left-hand side whose head function symbol is T. Unify that subterm with B's left-hand side to obtain the most general unifier, apply it to both right-hand sides, and rewrite A's left-hand side at the overlap with rule B. If B's left-hand side overlaps no proper subterm of A's left-hand side, the empty result is returned as the single token NONE.
Give the answer as the two resulting terms in prefix notation, A-side first, then the overlap-rewritten side, separated by ' ; '.

Answer:

NONE

### Example 2

Prompt:

Two rewrite rules over first-order terms are given in prefix notation.
  A: N(C(K(M(L(1,2),P(n,m)),M(L(1,2),P(n,m)))),c) -> n
  B: C(K(x,x)) -> x
Form the critical pair by overlapping rule B into a proper (non-root) subterm of rule A's left-hand side: the unique occurrence in A's left-hand side whose head function symbol is C. Unify that subterm with B's left-hand side to obtain the most general unifier, apply it to both right-hand sides, and rewrite A's left-hand side at the overlap with rule B. If B's left-hand side overlaps no proper subterm of A's left-hand side, the empty result is returned as the single token NONE.
Give the answer as the two resulting terms in prefix notation, A-side first, then the overlap-rewritten side, separated by ' ; '.

Answer:

n ; N(M(L(1,2),P(n,m)),c)

## Level 5

### Example 1

Prompt:

Two rewrite rules over first-order terms are given in prefix notation.
  A: Z(Z(J(k,2),k)) -> V(X(q,R(2,k)),E(A(k),D(n,n),G(2,p,0)),M(P(2)))
  B: T(Q(x,u,u),u,A(P(u,X(x,x,x),u))) -> A(2)
Form the critical pair by overlapping rule B into a proper (non-root) subterm of rule A's left-hand side: the unique occurrence in A's left-hand side whose head function symbol is T. Unify that subterm with B's left-hand side to obtain the most general unifier, apply it to both right-hand sides, and rewrite A's left-hand side at the overlap with rule B. If B's left-hand side overlaps no proper subterm of A's left-hand side, the empty result is returned as the single token NONE.
Give the answer as the two resulting terms in prefix notation, A-side first, then the overlap-rewritten side, separated by ' ; '.

Answer:

NONE

### Example 2

Prompt:

Two rewrite rules over first-order terms are given in prefix notation.
  A: C(f,E(C(X(D(N(B(T(1,q,m),T(3),Z(3)),C(U(1,q)),J(G(0))),G(D(W(V(N(m,p)),n,T(S(0),K(p,p,p))),W(V(N(m,p)),n,T(S(0),K(p,p,p)))),N(B(T(1,q,m),T(3),Z(3)),C(U(1,q)),J(G(0))),Q(N(B(T(1,q,m),T(3),Z(3)),C(U(1,q)),J(G(0)))))),K(K(H(W(V(N(m,p)),n,T(S(0),K(p,p,p))),n)),Q(Z(n))),C(W(V(N(m,p)),n,T(S(0),K(p,p,p))),N(B(T(1,q,m),T(3),Z(3)),C(U(1,q)),J(G(0))),P(N(N(B(T(1,q,m),T(3),Z(3)),C(U(1,q)),J(G(0))))))),k),c,e),f) -> Y(V(Q(1,e,e),D(0)),3,P(K(f,p)))
  B: X(D(z,G(D(v,v),z,Q(z))),K(K(H(v,x)),Q(Z(x))),C(v,z,P(N(z)))) -> 1
Form the critical pair by overlapping rule B into a proper (non-root) subterm of rule A's left-hand side: the unique occurrence in A's left-hand side whose head function symbol is X. Unify that subterm with B's left-hand side to obtain the most general unifier, apply it to both right-hand sides, and rewrite A's left-hand side at the overlap with rule B. If B's left-hand side overlaps no proper subterm of A's left-hand side, the empty result is returned as the single token NONE.
Give the answer as the two resulting terms in prefix notation, A-side first, then the overlap-rewritten side, separated by ' ; '.

Answer:

Y(V(Q(1,e,e),D(0)),3,P(K(f,p))) ; C(f,E(C(1,k),c,e),f)

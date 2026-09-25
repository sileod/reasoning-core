## Level 0

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  h(W)  ==  h([b].Z,a)
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: inconsistent

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  X  ==  c
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{X = c}; fresh{none}

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  f(c)  ==  f(b,[d].[c].e)
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: inconsistent

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  X  ==  Z
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{X = Z}; fresh{none}

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  swap(c<->d,d<->c).X  ==  b
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{X = b}; fresh{none}

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  f(U)  ==  f(g(g(U)),a)
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: inconsistent

## Level 2

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  swap(a<->b,b<->a).X  ==  b
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{X = a}; fresh{none}

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  Z  ==  c
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{Z = c}; fresh{none}

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  Z  ==  b
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{Z = b}; fresh{none}

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  Y  ==  f(U,[a].X)
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{Y = f(U,[a].X)}; fresh{none}

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  X  ==  d
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{X = d}; fresh{none}

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  swap(a<->d,d<->a).Y  ==  [a].h([b].X,d)
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{Y = [d].h([b].X,a)}; fresh{a # Y}

## Level 5

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  X  ==  d
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{X = d}; fresh{none}

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  Z  ==  swap(c<->d,d<->c).Y
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{Y = swap(c<->d,d<->c).Z}; fresh{c # Z, d # Z}

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  [a].[b].swap(a<->e,e<->a).Y  ==  c
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: inconsistent

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  Y  ==  d
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{Y = d}; fresh{none}

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  h(b)  ==  h(swap(a<->d,d<->a).Y,c)
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: inconsistent

In nominal syntax: a..e are atom constants, X..Z unification variables, swap(a<->b).X a suspended permutation, [a].t a binder where the binder atom is alpha-renamable, and f(t) an application. Two terms are equated modulo alpha-equivalence of their binders. Solve the nominal equation:
  Y  ==  a
If the equation has no unifier (is inconsistent), answer the single word  inconsistent.
Otherwise give the principal substitution and the residual freshness conditions in exactly this format:
  subst{X = t, ...}; fresh{a # X, ...}
use  fresh{none}  when there are no residual freshness conditions. Write only that one line.
Answer: subst{Y = a}; fresh{none}


## Level 0

Objects A, B, C, D are the live heap of a program. The garbage-collection roots are A.
Strong reference D -> A.
Strong reference A -> C.
Weak reference C -> A.
Ephemeron in C: key B, value B.
A strong reference keeps its target alive. A weak reference does not keep its target alive. An ephemeron's value stays alive only while both its container and its key are alive.
Which objects survive garbage collection? Answer with the surviving object labels concatenated in alphabetical order (for example, "ABE"); answer "none" if no object survives.

**Answer:** AC

Objects A, B, C, D are the live heap of a program. The garbage-collection roots are A.
Strong reference C -> D.
Strong reference B -> A.
Weak reference D -> A.
Ephemeron in A: key D, value D.
A strong reference keeps its target alive. A weak reference does not keep its target alive. An ephemeron's value stays alive only while both its container and its key are alive.
Which objects survive garbage collection? Answer with the surviving object labels concatenated in alphabetical order (for example, "ABE"); answer "none" if no object survives.

**Answer:** A

## Level 2

Objects A, B, C, D, E, F are the live heap of a program. The garbage-collection roots are F.
Strong reference F -> A.
Strong reference A -> D.
Strong reference C -> F.
Strong reference A -> F.
Weak reference F -> A.
Weak reference A -> D.
Weak reference A -> E.
Ephemeron in C: key A, value D.
Ephemeron in B: key A, value A.
Ephemeron in A: key F, value B.
A strong reference keeps its target alive. A weak reference does not keep its target alive. An ephemeron's value stays alive only while both its container and its key are alive.
Which objects survive garbage collection? Answer with the surviving object labels concatenated in alphabetical order (for example, "ABE"); answer "none" if no object survives.

**Answer:** ABDF

Objects A, B, C, D, E, F are the live heap of a program. The garbage-collection roots are C.
Strong reference E -> D.
Strong reference C -> A.
Strong reference F -> A.
Strong reference D -> B.
Weak reference E -> A.
Weak reference C -> A.
Weak reference F -> E.
Ephemeron in D: key E, value E.
Ephemeron in C: key B, value A.
Ephemeron in D: key D, value E.
A strong reference keeps its target alive. A weak reference does not keep its target alive. An ephemeron's value stays alive only while both its container and its key are alive.
Which objects survive garbage collection? Answer with the surviving object labels concatenated in alphabetical order (for example, "ABE"); answer "none" if no object survives.

**Answer:** AC

## Level 5

Objects A, B, C, D, E, F, G, H, I are the live heap of a program. The garbage-collection roots are H, E.
Strong reference G -> H.
Strong reference A -> E.
Strong reference A -> D.
Strong reference D -> A.
Strong reference H -> E.
Strong reference H -> A.
Strong reference E -> G.
Weak reference E -> A.
Weak reference B -> F.
Weak reference I -> C.
Weak reference I -> D.
Weak reference H -> B.
Weak reference C -> H.
Ephemeron in D: key B, value F.
Ephemeron in D: key E, value G.
Ephemeron in G: key F, value F.
Ephemeron in H: key B, value G.
Ephemeron in B: key E, value G.
Ephemeron in D: key B, value E.
A strong reference keeps its target alive. A weak reference does not keep its target alive. An ephemeron's value stays alive only while both its container and its key are alive.
Which objects survive garbage collection? Answer with the surviving object labels concatenated in alphabetical order (for example, "ABE"); answer "none" if no object survives.

**Answer:** ADEGH

Objects A, B, C, D, E, F, G, H, I are the live heap of a program. The garbage-collection roots are D, G.
Strong reference E -> I.
Strong reference E -> G.
Strong reference A -> H.
Strong reference E -> I.
Strong reference H -> I.
Strong reference G -> I.
Strong reference C -> I.
Weak reference B -> G.
Weak reference D -> B.
Weak reference F -> D.
Weak reference G -> E.
Weak reference F -> E.
Weak reference I -> C.
Ephemeron in G: key D, value E.
Ephemeron in H: key D, value A.
Ephemeron in E: key G, value H.
Ephemeron in E: key E, value G.
Ephemeron in F: key D, value I.
Ephemeron in H: key F, value D.
A strong reference keeps its target alive. A weak reference does not keep its target alive. An ephemeron's value stays alive only while both its container and its key are alive.
Which objects survive garbage collection? Answer with the surviving object labels concatenated in alphabetical order (for example, "ABE"); answer "none" if no object survives.

**Answer:** ADEGHI

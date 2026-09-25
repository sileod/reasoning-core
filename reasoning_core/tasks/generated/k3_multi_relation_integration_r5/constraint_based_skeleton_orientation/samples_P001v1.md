## Level 0

### Prompt

We run a constraint-based (PC) skeleton and orientation search on the node set {V0, V1, V2, V3}. The observed conditional independencies are:
  I(V0;V2 | none)
  I(V1;V2 | none)
Each I(X;Y | S) states X and Y are conditionally independent given the separating set S, so the undirected edge X--Y is removed from the full skeleton and S is recorded as its separating set. Orient every v-structure X -> Z <- Y (non-adjacent X and Y with a common neighbor Z that is not in the separating set of X,Y), then complete the orientation with the Meek rules (R1: X->Y, Y--W, X and W non-adjacent => Y->W; R2: X->Z, Y->Z, X and Y adjacent => X->Y; R3: X->Y, X->Z, Y--Z, Z->W, Y and W non-adjacent => Z->W). List every directed edge of the final DAG as SRC->DST, separated by semicolons, sorted by source then destination. Answer: none if no directed edge remains.

### Answer

V0->V1;V0->V3;V1->V3;V2->V3

### Prompt

We run a constraint-based (PC) skeleton and orientation search on the node set {V0, V1, V2, V3}. The observed conditional independencies are:
  I(V0;V3 | V1,V2)
  I(V1;V2 | none)
Each I(X;Y | S) states X and Y are conditionally independent given the separating set S, so the undirected edge X--Y is removed from the full skeleton and S is recorded as its separating set. Orient every v-structure X -> Z <- Y (non-adjacent X and Y with a common neighbor Z that is not in the separating set of X,Y), then complete the orientation with the Meek rules (R1: X->Y, Y--W, X and W non-adjacent => Y->W; R2: X->Z, Y->Z, X and Y adjacent => X->Y; R3: X->Y, X->Z, Y--Z, Z->W, Y and W non-adjacent => Z->W). List every directed edge of the final DAG as SRC->DST, separated by semicolons, sorted by source then destination. Answer: none if no directed edge remains.

### Answer

V1->V0;V1->V3;V2->V0;V2->V3



## Level 2

### Prompt

We run a constraint-based (PC) skeleton and orientation search on the node set {V0, V1, V2, V3, V4}. The observed conditional independencies are:
  I(V0;V2 | V1)
  I(V0;V3 | V1,V2)
  I(V0;V4 | V1)
  I(V2;V3 | none)
Each I(X;Y | S) states X and Y are conditionally independent given the separating set S, so the undirected edge X--Y is removed from the full skeleton and S is recorded as its separating set. Orient every v-structure X -> Z <- Y (non-adjacent X and Y with a common neighbor Z that is not in the separating set of X,Y), then complete the orientation with the Meek rules (R1: X->Y, Y--W, X and W non-adjacent => Y->W; R2: X->Z, Y->Z, X and Y adjacent => X->Y; R3: X->Y, X->Z, Y--Z, Z->W, Y and W non-adjacent => Z->W). List every directed edge of the final DAG as SRC->DST, separated by semicolons, sorted by source then destination. Answer: none if no directed edge remains.

### Answer

V1->V0;V2->V1;V2->V4;V3->V1;V3->V4

### Prompt

We run a constraint-based (PC) skeleton and orientation search on the node set {V0, V1, V2, V3, V4}. The observed conditional independencies are:
  I(V0;V2 | V1,V4)
  I(V1;V4 | V2)
  I(V2;V3 | none)
  I(V3;V4 | none)
Each I(X;Y | S) states X and Y are conditionally independent given the separating set S, so the undirected edge X--Y is removed from the full skeleton and S is recorded as its separating set. Orient every v-structure X -> Z <- Y (non-adjacent X and Y with a common neighbor Z that is not in the separating set of X,Y), then complete the orientation with the Meek rules (R1: X->Y, Y--W, X and W non-adjacent => Y->W; R2: X->Z, Y->Z, X and Y adjacent => X->Y; R3: X->Y, X->Z, Y--Z, Z->W, Y and W non-adjacent => Z->W). List every directed edge of the final DAG as SRC->DST, separated by semicolons, sorted by source then destination. Answer: none if no directed edge remains.

### Answer

V1->V0;V2->V1;V3->V0;V3->V1;V4->V0



## Level 5

### Prompt

We run a constraint-based (PC) skeleton and orientation search on the node set {V0, V1, V2, V3, V4, V5}. The observed conditional independencies are:
  I(V0;V1 | V2,V3,V4)
  I(V0;V5 | none)
  I(V1;V4 | V0,V2,V3,V5)
  I(V1;V5 | V0,V2)
  I(V2;V3 | V0,V1,V4)
  I(V2;V5 | V0,V1)
  I(V3;V5 | V0,V2,V4)
Each I(X;Y | S) states X and Y are conditionally independent given the separating set S, so the undirected edge X--Y is removed from the full skeleton and S is recorded as its separating set. Orient every v-structure X -> Z <- Y (non-adjacent X and Y with a common neighbor Z that is not in the separating set of X,Y), then complete the orientation with the Meek rules (R1: X->Y, Y--W, X and W non-adjacent => Y->W; R2: X->Z, Y->Z, X and Y adjacent => X->Y; R3: X->Y, X->Z, Y--Z, Z->W, Y and W non-adjacent => Z->W). List every directed edge of the final DAG as SRC->DST, separated by semicolons, sorted by source then destination. Answer: none if no directed edge remains.

### Answer

V0->V2;V0->V4;V2->V1;V2->V4;V3->V1;V4->V3;V5->V4

### Prompt

We run a constraint-based (PC) skeleton and orientation search on the node set {V0, V1, V2, V3, V4, V5}. The observed conditional independencies are:
  I(V0;V1 | none)
  I(V0;V3 | V1)
  I(V1;V4 | V0,V3,V5)
  I(V1;V5 | V2,V3,V4)
  I(V2;V4 | V0)
  I(V2;V5 | V0,V1,V3,V4)
  I(V3;V4 | V0,V1,V2,V5)
Each I(X;Y | S) states X and Y are conditionally independent given the separating set S, so the undirected edge X--Y is removed from the full skeleton and S is recorded as its separating set. Orient every v-structure X -> Z <- Y (non-adjacent X and Y with a common neighbor Z that is not in the separating set of X,Y), then complete the orientation with the Meek rules (R1: X->Y, Y--W, X and W non-adjacent => Y->W; R2: X->Z, Y->Z, X and Y adjacent => X->Y; R3: X->Y, X->Z, Y--Z, Z->W, Y and W non-adjacent => Z->W). List every directed edge of the final DAG as SRC->DST, separated by semicolons, sorted by source then destination. Answer: none if no directed edge remains.

### Answer

V0->V2;V0->V5;V1->V2;V1->V3;V3->V2;V3->V5;V5->V4



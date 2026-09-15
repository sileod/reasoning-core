# Samples for gnfa_state_elimination (P010v3)

## Level 0

Consider a generalized nondeterministic finite automaton over alphabet {a, b, c}. Its states are q0, q1, q2; q0 is the start state and q2 is the only accept state. The transition labels are:
  q0 -> q0 : c
  q0 -> q1 : a
  q0 -> q2 : c
  q1 -> q0 : {}
  q1 -> q1 : a|b
  q1 -> q2 : {}
  q2 -> q0 : b|c
  q2 -> q1 : b|c
  q2 -> q2 : a
Eliminate the states in this order: q1. Each elimination rewrites every remaining edge's label as R1 R2* R3 | R4, dropping any term with no edge. After all non-start non-accept states are eliminated, give the regex on the final edge q0 -> q2. Use eps for epsilon and {} if the edge does not exist. Answer with only the regex.

Answer: c

Consider a generalized nondeterministic finite automaton over alphabet {a, b}. Its states are q0, q1, q2; q0 is the start state and q2 is the only accept state. The transition labels are:
  q0 -> q0 : {}
  q0 -> q1 : a
  q0 -> q2 : a
  q1 -> q0 : b
  q1 -> q1 : b
  q1 -> q2 : a|b
  q2 -> q0 : a
  q2 -> q1 : {}
  q2 -> q2 : b
Eliminate the states in this order: q1. Each elimination rewrites every remaining edge's label as R1 R2* R3 | R4, dropping any term with no edge. After eliminating exactly these states, give the label on the edge q0 -> q0. Use eps for epsilon and {} if that edge does not exist. Answer with only the regex.

Answer: ab*b

## Level 2

Consider a generalized nondeterministic finite automaton over alphabet {a, b, c}. Its states are q0, q1, q2, q3, q4; q0 is the start state and q4 is the only accept state. The transition labels are:
  q0 -> q0 : b|c
  q0 -> q1 : b
  q0 -> q2 : {}
  q0 -> q3 : {}
  q0 -> q4 : c
  q1 -> q0 : b
  q1 -> q1 : b
  q1 -> q2 : b
  q1 -> q3 : b
  q1 -> q4 : a|c
  q2 -> q0 : b
  q2 -> q1 : c
  q2 -> q2 : {}
  q2 -> q3 : c
  q2 -> q4 : b
  q3 -> q0 : a
  q3 -> q1 : b|c
  q3 -> q2 : b
  q3 -> q3 : b|c
  q3 -> q4 : c
  q4 -> q0 : a
  q4 -> q1 : b
  q4 -> q2 : c
  q4 -> q3 : {}
  q4 -> q4 : {}
Eliminate the states in this order: q3 -> q1 -> q2. Each elimination rewrites every remaining edge's label as R1 R2* R3 | R4, dropping any term with no edge. After eliminating exactly these states, give the label on the edge q4 -> q4. Use eps for epsilon and {} if that edge does not exist. Answer with only the regex.

Answer: (b((b)|(b(b|c)*b|c))*(a|c)|(b(b|c)*c))|((c)|(b((b)|(b(b|c)*b|c))*(b)|(b(b|c)*b))((c(b|c)*b)|((c)|(c(b|c)*b|c)((b)|(b(b|c)*b|c))*(b)|(b(b|c)*b)))*((b)|(c(b|c)*c))|((c)|(c(b|c)*b|c)((b)|(b(b|c)*b|c))*(a|c)|(b(b|c)*c)))

Consider a generalized nondeterministic finite automaton over alphabet {a, b, c}. Its states are q0, q1, q2, q3, q4; q0 is the start state and q4 is the only accept state. The transition labels are:
  q0 -> q0 : c
  q0 -> q1 : a
  q0 -> q2 : c
  q0 -> q3 : {}
  q0 -> q4 : b
  q1 -> q0 : c
  q1 -> q1 : b|c
  q1 -> q2 : a
  q1 -> q3 : a|c
  q1 -> q4 : c
  q2 -> q0 : c
  q2 -> q1 : b
  q2 -> q2 : a
  q2 -> q3 : b|c
  q2 -> q4 : a
  q3 -> q0 : a
  q3 -> q1 : a
  q3 -> q2 : c
  q3 -> q3 : a
  q3 -> q4 : {}
  q4 -> q0 : c
  q4 -> q1 : a
  q4 -> q2 : a
  q4 -> q3 : b
  q4 -> q4 : a
Eliminate the states in this order: q2 -> q1 -> q3. Each elimination rewrites every remaining edge's label as R1 R2* R3 | R4, dropping any term with no edge. After all non-start non-accept states are eliminated, give the regex on the final edge q0 -> q4. Use eps for epsilon and {} if the edge does not exist. Answer with only the regex.

Answer: (((b)|(ca*a))|((a)|(ca*b)((b|c)|(aa*b))*(c)|(aa*a)))|((ca*b|c)|((a)|(ca*b)((b|c)|(aa*b))*(a|c)|(aa*b|c))(((a)|(ca*b|c))|((a)|(ca*b)((b|c)|(aa*b))*(a|c)|(aa*b|c)))*(ca*a)|((a)|(ca*b)((b|c)|(aa*b))*(c)|(aa*a)))

## Level 5

Consider a generalized nondeterministic finite automaton over alphabet {a, b}. Its states are q0, q1, q2, q3, q4, q5, q6, q7; q0 is the start state and q7 is the only accept state. The transition labels are:
  q0 -> q0 : {}
  q0 -> q1 : a
  q0 -> q2 : {}
  q0 -> q3 : b
  q0 -> q4 : b
  q0 -> q5 : a|b
  q0 -> q6 : a
  q0 -> q7 : b
  q1 -> q0 : b
  q1 -> q1 : a
  q1 -> q2 : a
  q1 -> q3 : a
  q1 -> q4 : a
  q1 -> q5 : a
  q1 -> q6 : b
  q1 -> q7 : b
  q2 -> q0 : b
  q2 -> q1 : b
  q2 -> q2 : {}
  q2 -> q3 : a|b
  q2 -> q4 : b
  q2 -> q5 : b
  q2 -> q6 : a|b
  q2 -> q7 : a
  q3 -> q0 : b
  q3 -> q1 : {}
  q3 -> q2 : a
  q3 -> q3 : {}
  q3 -> q4 : b
  q3 -> q5 : a
  q3 -> q6 : b
  q3 -> q7 : b
  q4 -> q0 : a|b
  q4 -> q1 : a
  q4 -> q2 : b
  q4 -> q3 : {}
  q4 -> q4 : b
  q4 -> q5 : a
  q4 -> q6 : a|b
  q4 -> q7 : b
  q5 -> q0 : b
  q5 -> q1 : a|b
  q5 -> q2 : a
  q5 -> q3 : b
  q5 -> q4 : b
  q5 -> q5 : b
  q5 -> q6 : {}
  q5 -> q7 : {}
  q6 -> q0 : a
  q6 -> q1 : b
  q6 -> q2 : {}
  q6 -> q3 : {}
  q6 -> q4 : b
  q6 -> q5 : a|b
  q6 -> q6 : b
  q6 -> q7 : {}
  q7 -> q0 : b
  q7 -> q1 : b
  q7 -> q2 : b
  q7 -> q3 : a
  q7 -> q4 : b
  q7 -> q5 : a
  q7 -> q6 : a
  q7 -> q7 : a
Eliminate the states in this order: q1 -> q2 -> q6 -> q4 -> q3 -> q5. Each elimination rewrites every remaining edge's label as R1 R2* R3 | R4, dropping any term with no edge. After all non-start non-accept states are eliminated, give the regex on the final edge q0 -> q7. Use eps for epsilon and {} if the edge does not exist. Answer with only the regex.

Answer: ((((((b)|(aa*b))|(aa*a(ba*a)*(a)|(ba*b)))|(((a)|(aa*b))|(aa*a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*b)|(ba*a(ba*a)*(a)|(ba*b))))|((((b)|(aa*a))|(aa*a(ba*a)*(b)|(ba*a)))|(((a)|(aa*b))|(aa*a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*(((b)|(aa*b))|((b)|(aa*a)(ba*a)*(a)|(ba*b)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*b)|(ba*a(ba*a)*(a)|(ba*b)))))|(((((b)|(aa*a))|(aa*a(ba*a)*(a|b)|(ba*a)))|(((a)|(aa*b))|(aa*a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))|((((b)|(aa*a))|(aa*a(ba*a)*(b)|(ba*a)))|(((a)|(aa*b))|(aa*a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*((aa*a)|((b)|(aa*a)(ba*a)*(a|b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))(((a(ba*a)*(a|b)|(ba*a))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))|(((b)|(a(ba*a)*(b)|(ba*a)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*((aa*a)|((b)|(aa*a)(ba*a)*(a|b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a)))))*(((b)|(a(ba*a)*(a)|(ba*b)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*b)|(ba*a(ba*a)*(a)|(ba*b))))|(((b)|(a(ba*a)*(b)|(ba*a)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*(((b)|(aa*b))|((b)|(aa*a)(ba*a)*(a)|(ba*b)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*b)|(ba*a(ba*a)*(a)|(ba*b))))))|((((((a|b)|(aa*a))|(aa*a(ba*a)*(b)|(ba*a)))|(((a)|(aa*b))|(aa*a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((a|b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))|((((b)|(aa*a))|(aa*a(ba*a)*(b)|(ba*a)))|(((a)|(aa*b))|(aa*a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*(((a)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((a|b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))))|(((((b)|(aa*a))|(aa*a(ba*a)*(a|b)|(ba*a)))|(((a)|(aa*b))|(aa*a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))|((((b)|(aa*a))|(aa*a(ba*a)*(b)|(ba*a)))|(((a)|(aa*b))|(aa*a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*((aa*a)|((b)|(aa*a)(ba*a)*(a|b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))(((a(ba*a)*(a|b)|(ba*a))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))|(((b)|(a(ba*a)*(b)|(ba*a)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*((aa*a)|((b)|(aa*a)(ba*a)*(a|b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a)))))*(((a)|(a(ba*a)*(b)|(ba*a)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((a|b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))|(((b)|(a(ba*a)*(b)|(ba*a)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*(((a)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((a|b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))))((((((b)|(a|ba*a))|((a)|(a|ba*a)(ba*a)*(b)|(ba*a)))|((a|ba*b)|((a)|(a|ba*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((a|b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))|((((b)|(a|ba*a))|((a)|(a|ba*a)(ba*a)*(b)|(ba*a)))|((a|ba*b)|((a)|(a|ba*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*(((a)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((a|b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))))|(((((b)|(a|ba*a))|((a)|(a|ba*a)(ba*a)*(a|b)|(ba*a)))|((a|ba*b)|((a)|(a|ba*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))|((((b)|(a|ba*a))|((a)|(a|ba*a)(ba*a)*(b)|(ba*a)))|((a|ba*b)|((a)|(a|ba*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*((aa*a)|((b)|(aa*a)(ba*a)*(a|b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))(((a(ba*a)*(a|b)|(ba*a))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))|(((b)|(a(ba*a)*(b)|(ba*a)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*((aa*a)|((b)|(aa*a)(ba*a)*(a|b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a)))))*(((a)|(a(ba*a)*(b)|(ba*a)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((a|b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))|(((b)|(a(ba*a)*(b)|(ba*a)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*(((a)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((a|b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))))*((((a|ba*b)|((a)|(a|ba*a)(ba*a)*(a)|(ba*b)))|((a|ba*b)|((a)|(a|ba*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*b)|(ba*a(ba*a)*(a)|(ba*b))))|((((b)|(a|ba*a))|((a)|(a|ba*a)(ba*a)*(b)|(ba*a)))|((a|ba*b)|((a)|(a|ba*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*(((b)|(aa*b))|((b)|(aa*a)(ba*a)*(a)|(ba*b)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*b)|(ba*a(ba*a)*(a)|(ba*b)))))|(((((b)|(a|ba*a))|((a)|(a|ba*a)(ba*a)*(a|b)|(ba*a)))|((a|ba*b)|((a)|(a|ba*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))|((((b)|(a|ba*a))|((a)|(a|ba*a)(ba*a)*(b)|(ba*a)))|((a|ba*b)|((a)|(a|ba*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*((aa*a)|((b)|(aa*a)(ba*a)*(a|b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))(((a(ba*a)*(a|b)|(ba*a))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a))))|(((b)|(a(ba*a)*(b)|(ba*a)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*((aa*a)|((b)|(aa*a)(ba*a)*(a|b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*a)|(ba*a(ba*a)*(a|b)|(ba*a)))))*(((b)|(a(ba*a)*(a)|(ba*b)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*b)|(ba*a(ba*a)*(a)|(ba*b))))|(((b)|(a(ba*a)*(b)|(ba*a)))|((b)|(a(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a)))((((b)|(aa*a))|((b)|(aa*a)(ba*a)*(b)|(ba*a)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*((b)|(ba*a))|(ba*a(ba*a)*(b)|(ba*a))))*(((b)|(aa*b))|((b)|(aa*a)(ba*a)*(a)|(ba*b)))|(((a|b)|(aa*b))|((b)|(aa*a)(ba*a)*(a|b)|(ba*b))(((b)|(ba*b))|(ba*a(ba*a)*(a|b)|(ba*b)))*(ba*b)|(ba*a(ba*a)*(a)|(ba*b))))))

Consider a generalized nondeterministic finite automaton over alphabet {a, b, c}. Its states are q0, q1, q2, q3, q4, q5, q6, q7; q0 is the start state and q7 is the only accept state. The transition labels are:
  q0 -> q0 : b
  q0 -> q1 : a|c
  q0 -> q2 : b|c
  q0 -> q3 : c
  q0 -> q4 : {}
  q0 -> q5 : a
  q0 -> q6 : b|c
  q0 -> q7 : a
  q1 -> q0 : a
  q1 -> q1 : b
  q1 -> q2 : c
  q1 -> q3 : b
  q1 -> q4 : a
  q1 -> q5 : a
  q1 -> q6 : c
  q1 -> q7 : c
  q2 -> q0 : a
  q2 -> q1 : a
  q2 -> q2 : c
  q2 -> q3 : a
  q2 -> q4 : b|c
  q2 -> q5 : b
  q2 -> q6 : b
  q2 -> q7 : {}
  q3 -> q0 : {}
  q3 -> q1 : c
  q3 -> q2 : c
  q3 -> q3 : b
  q3 -> q4 : {}
  q3 -> q5 : c
  q3 -> q6 : a
  q3 -> q7 : a|b
  q4 -> q0 : c
  q4 -> q1 : {}
  q4 -> q2 : a
  q4 -> q3 : a
  q4 -> q4 : b|c
  q4 -> q5 : b
  q4 -> q6 : b|c
  q4 -> q7 : c
  q5 -> q0 : b|c
  q5 -> q1 : {}
  q5 -> q2 : c
  q5 -> q3 : a
  q5 -> q4 : {}
  q5 -> q5 : c
  q5 -> q6 : b|c
  q5 -> q7 : c
  q6 -> q0 : c
  q6 -> q1 : a|b
  q6 -> q2 : c
  q6 -> q3 : a
  q6 -> q4 : {}
  q6 -> q5 : {}
  q6 -> q6 : {}
  q6 -> q7 : c
  q7 -> q0 : a
  q7 -> q1 : a
  q7 -> q2 : b
  q7 -> q3 : b
  q7 -> q4 : {}
  q7 -> q5 : a|b
  q7 -> q6 : a
  q7 -> q7 : a|c
Eliminate the states in this order: q4 -> q3 -> q5 -> q6. Each elimination rewrites every remaining edge's label as R1 R2* R3 | R4, dropping any term with no edge. After eliminating exactly these states, give the label on the edge q7 -> q7. Use eps for epsilon and {} if that edge does not exist. Answer with only the regex.

Answer: (((a|c)|(bb*a|b))|((a|b)|(bb*c)((c)|(ab*c))*(c)|(ab*a|b)))|(((a)|(bb*a))|((a|b)|(bb*c)((c)|(ab*c))*(b|c)|(ab*a))((ab*a)|(ab*c((c)|(ab*c))*(b|c)|(ab*a)))*((c)|(ab*a|b))|(ab*c((c)|(ab*c))*(c)|(ab*a|b)))

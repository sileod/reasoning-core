# Samples for suffix_automaton_growth_trace (P007v1)

## Level 0

### Example 1

**Prompt:**

We build a suffix automaton (SAM) over the string "bbabab" by extending it one character at a time, reading the string from left to right and appending each next character at each step. States are numbered in creation order: state 0 is the initial state with len 0 and link -1, and every new state (including clones) is added with the next unused integer id. For each appended character, apply the standard online SAM construction: create a new state for the extended string, walk suffix links from the previous last state adding the new transition, and when a transition already exists, either set the link if the target's len matches, or split by creating a clone state and redirecting the conflicting transitions.

Give the final state table of the completed automaton, one line per state in creation order (so line i is state i), each line exactly:
i:(len,link,transitions)
where len is that state's longest-string length, link is its suffix link id (-1 only for state 0), and transitions is a comma-separated list of c->to entries for that state's outgoing transitions sorted by character, empty if the state has no outgoing transitions. Nothing else.
Format example for two states:
0:(0,-1,a->1)
1:(1,0,)
Answer with only the state table lines.

**Answer:**

0:(0,-1,a->6,b->1)
1:(1,0,a->6,b->2)
2:(2,1,a->3)
3:(3,6,b->4)
4:(4,8,a->5)
5:(5,6,b->7)
6:(2,0,b->8)
7:(6,8,)
8:(3,1,a->5)

### Example 2

**Prompt:**

We build a suffix automaton (SAM) over the string "babaaa" by extending it one character at a time, reading the string from left to right and appending each next character at each step. States are numbered in creation order: state 0 is the initial state with len 0 and link -1, and every new state (including clones) is added with the next unused integer id. For each appended character, apply the standard online SAM construction: create a new state for the extended string, walk suffix links from the previous last state adding the new transition, and when a transition already exists, either set the link if the target's len matches, or split by creating a clone state and redirecting the conflicting transitions.

Give the final state table of the completed automaton, one line per state in creation order (so line i is state i), each line exactly:
i:(len,link,transitions)
where len is that state's longest-string length, link is its suffix link id (-1 only for state 0), and transitions is a comma-separated list of c->to entries for that state's outgoing transitions sorted by character, empty if the state has no outgoing transitions. Nothing else.
Format example for two states:
0:(0,-1,a->1)
1:(1,0,)
Answer with only the state table lines.

**Answer:**

0:(0,-1,a->6,b->1)
1:(1,0,a->2)
2:(2,6,a->5,b->3)
3:(3,1,a->4)
4:(4,2,a->5)
5:(5,8,a->7)
6:(1,0,a->8,b->3)
7:(6,8,)
8:(2,6,a->7)

## Level 2

### Example 1

**Prompt:**

We build a suffix automaton (SAM) over the string "cbcabacbac" by extending it one character at a time, reading the string from left to right and appending each next character at each step. States are numbered in creation order: state 0 is the initial state with len 0 and link -1, and every new state (including clones) is added with the next unused integer id. For each appended character, apply the standard online SAM construction: create a new state for the extended string, walk suffix links from the previous last state adding the new transition, and when a transition already exists, either set the link if the target's len matches, or split by creating a clone state and redirecting the conflicting transitions.

Give the final state table of the completed automaton, one line per state in creation order (so line i is state i), each line exactly:
i:(len,link,transitions)
where len is that state's longest-string length, link is its suffix link id (-1 only for state 0), and transitions is a comma-separated list of c->to entries for that state's outgoing transitions sorted by character, empty if the state has no outgoing transitions. Nothing else.
Format example for two states:
0:(0,-1,a->1)
1:(1,0,)
Answer with only the state table lines.

**Answer:**

0:(0,-1,a->8,b->6,c->1)
1:(1,0,a->4,b->2)
2:(2,6,a->11,c->3)
3:(3,1,a->4)
4:(4,8,b->5)
5:(5,6,a->7)
6:(1,0,a->12,c->3)
7:(6,12,c->9)
8:(1,0,b->5,c->14)
9:(7,14,b->10)
10:(8,2,a->11)
11:(9,12,c->13)
12:(2,8,c->14)
13:(10,14,)
14:(3,1,b->10)

### Example 2

**Prompt:**

We build a suffix automaton (SAM) over the string "ccccbcbbca" by extending it one character at a time, reading the string from left to right and appending each next character at each step. States are numbered in creation order: state 0 is the initial state with len 0 and link -1, and every new state (including clones) is added with the next unused integer id. For each appended character, apply the standard online SAM construction: create a new state for the extended string, walk suffix links from the previous last state adding the new transition, and when a transition already exists, either set the link if the target's len matches, or split by creating a clone state and redirecting the conflicting transitions.

Give the final state table of the completed automaton, one line per state in creation order (so line i is state i), each line exactly:
i:(len,link,transitions)
where len is that state's longest-string length, link is its suffix link id (-1 only for state 0), and transitions is a comma-separated list of c->to entries for that state's outgoing transitions sorted by character, empty if the state has no outgoing transitions. Nothing else.
Format example for two states:
0:(0,-1,a->1)
1:(1,0,)
Answer with only the state table lines.

**Answer:**

0:(0,-1,a->13,b->10,c->1)
1:(1,0,a->13,b->8,c->2)
2:(2,1,b->5,c->3)
3:(3,2,b->5,c->4)
4:(4,3,b->5)
5:(5,8,c->6)
6:(6,12,b->7)
7:(7,8,b->9)
8:(2,10,b->9,c->6)
9:(8,10,c->11)
10:(1,0,b->9,c->12)
11:(9,12,a->13)
12:(2,1,a->13,b->7)
13:(10,0,)

## Level 5

### Example 1

**Prompt:**

We build a suffix automaton (SAM) over the string "cbdbdbbbcbcdadcc" by extending it one character at a time, reading the string from left to right and appending each next character at each step. States are numbered in creation order: state 0 is the initial state with len 0 and link -1, and every new state (including clones) is added with the next unused integer id. For each appended character, apply the standard online SAM construction: create a new state for the extended string, walk suffix links from the previous last state adding the new transition, and when a transition already exists, either set the link if the target's len matches, or split by creating a clone state and redirecting the conflicting transitions.

Give the final state table of the completed automaton, one line per state in creation order (so line i is state i), each line exactly:
i:(len,link,transitions)
where len is that state's longest-string length, link is its suffix link id (-1 only for state 0), and transitions is a comma-separated list of c->to entries for that state's outgoing transitions sorted by character, empty if the state has no outgoing transitions. Nothing else.
Format example for two states:
0:(0,-1,a->1)
1:(1,0,)
Answer with only the state table lines.

**Answer:**

0:(0,-1,a->19,b->5,c->1,d->18)
1:(1,0,b->2,c->22,d->17)
2:(2,5,c->15,d->3)
3:(3,7,b->4)
4:(4,9,d->6)
5:(1,0,b->12,c->16,d->7)
6:(5,7,b->8)
7:(2,18,b->9)
8:(6,9,b->10)
9:(3,5,b->10,d->6)
10:(7,12,b->11)
11:(8,12,c->13)
12:(2,5,b->11,c->13)
13:(9,16,b->14)
14:(10,2,c->15)
15:(11,16,d->17)
16:(2,1,b->14,d->17)
17:(12,18,a->19)
18:(1,0,a->19,b->9,c->21)
19:(13,0,d->20)
20:(14,18,c->21)
21:(15,1,c->22)
22:(16,1,)

### Example 2

**Prompt:**

We build a suffix automaton (SAM) over the string "adbcdaacbaaddbbb" by extending it one character at a time, reading the string from left to right and appending each next character at each step. States are numbered in creation order: state 0 is the initial state with len 0 and link -1, and every new state (including clones) is added with the next unused integer id. For each appended character, apply the standard online SAM construction: create a new state for the extended string, walk suffix links from the previous last state adding the new transition, and when a transition already exists, either set the link if the target's len matches, or split by creating a clone state and redirecting the conflicting transitions.

Give the final state table of the completed automaton, one line per state in creation order (so line i is state i), each line exactly:
i:(len,link,transitions)
where len is that state's longest-string length, link is its suffix link id (-1 only for state 0), and transitions is a comma-separated list of c->to entries for that state's outgoing transitions sorted by character, empty if the state has no outgoing transitions. Nothing else.
Format example for two states:
0:(0,-1,a->1)
1:(1,0,)
Answer with only the state table lines.

**Answer:**

0:(0,-1,a->1,b->12,c->10,d->6)
1:(1,0,a->15,c->9,d->2)
2:(2,6,b->3,d->17)
3:(3,19,c->4)
4:(4,10,d->5)
5:(5,6,a->7)
6:(1,0,a->7,b->19,d->17)
7:(6,1,a->8)
8:(7,15,c->9)
9:(8,10,b->11)
10:(1,0,b->11,d->5)
11:(9,12,a->13)
12:(1,0,a->13,b->22,c->4)
13:(10,1,a->14)
14:(11,15,d->16)
15:(2,1,c->9,d->16)
16:(12,2,d->17)
17:(13,6,b->18)
18:(14,19,b->20)
19:(2,12,b->20,c->4)
20:(15,22,b->21)
21:(16,22,)
22:(2,12,b->21)

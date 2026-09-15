## Level 0
### Example 1
Prompt:
In a tiny heap language with points-to facts (c->v), separating conjunction (*), and a read command that only dereferences the location it names, consider the separation logic triple {1->2 * 2->3 * 3->1} read 2 {2->3}. The postcondition shows that only 2 is read; no other location is touched, so the minimal frame F satisfies {P * F} read 2 {Q * F} with F as small as possible. Give the minimal frame as an explicit list of points-to facts separated by ' * ' (all cells of F).

Answer:
1->2 * 3->1

### Example 2
Prompt:
In a tiny heap language with points-to facts (c->v), separating conjunction (*), and a read command that only dereferences the location it names, consider the separation logic triple {1->3 * 2->1 * 3->1} read 3 {3->1}. The postcondition shows that only 3 is read; no other location is touched, so the minimal frame F satisfies {P * F} read 3 {Q * F} with F as small as possible. Give the minimal frame as an explicit list of points-to facts separated by ' * ' (all cells of F).

Answer:
1->3 * 2->1

## Level 2
### Example 1
Prompt:
In a tiny heap language with points-to facts (c->v), separating conjunction (*), and a read command that only dereferences the location it names, consider the separation logic triple {1->4 * 2->1 * 3->2 * 4->1 * 6->1} read 2 {2->1}. The postcondition shows that only 2 is read; no other location is touched, so the minimal frame F satisfies {P * F} read 2 {Q * F} with F as small as possible. Give the minimal frame as an explicit list of points-to facts separated by ' * ' (all cells of F).

Answer:
1->4 * 3->2 * 4->1 * 6->1

### Example 2
Prompt:
In a tiny heap language with points-to facts (c->v), separating conjunction (*), and a read command that only dereferences the location it names, consider the separation logic triple {1->2 * 3->5 * 4->4 * 5->1 * 6->1} read 1 {1->2}. The postcondition shows that only 1 is read; no other location is touched, so the minimal frame F satisfies {P * F} read 1 {Q * F} with F as small as possible. Give the minimal frame as an explicit list of points-to facts separated by ' * ' (all cells of F).

Answer:
3->5 * 4->4 * 5->1 * 6->1

## Level 5
### Example 1
Prompt:
In a tiny heap language with points-to facts (c->v), separating conjunction (*), and a read command that only dereferences the location it names, consider the separation logic triple {2->7 * 3->8 * 4->2 * 5->4 * 6->8 * 7->3 * 8->4 * 9->2} read 3 {3->8}. The postcondition shows that only 3 is read; no other location is touched, so the minimal frame F satisfies {P * F} read 3 {Q * F} with F as small as possible. Give the minimal frame as an explicit list of points-to facts separated by ' * ' (all cells of F).

Answer:
2->7 * 4->2 * 5->4 * 6->8 * 7->3 * 8->4 * 9->2

### Example 2
Prompt:
In a tiny heap language with points-to facts (c->v), separating conjunction (*), and a read command that only dereferences the location it names, consider the separation logic triple {1->6 * 2->4 * 3->1 * 4->5 * 5->1 * 6->1 * 7->6 * 8->3} read 5 {5->1}. The postcondition shows that only 5 is read; no other location is touched, so the minimal frame F satisfies {P * F} read 5 {Q * F} with F as small as possible. Give the minimal frame as an explicit list of points-to facts separated by ' * ' (all cells of F).

Answer:
1->6 * 2->4 * 3->1 * 4->5 * 6->1 * 7->6 * 8->3


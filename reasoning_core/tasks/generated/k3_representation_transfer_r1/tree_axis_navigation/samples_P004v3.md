# Level 0

## Example

Use the ordered rooted tree below, written in parenthesized notation where a node lists its children left-to-right and a group with no children is a leaf.

Tree: 0(1(2(3(4(5)))))
Context node: 2

Apply each axis step below in order; each step's result becomes the context for the next. The axes child, parent, descendant, ancestor, following-sibling and preceding-sibling act on the current context node, and the bracketed 1-based number selects that element of the axis result in document order (preorder, left to right).

Steps:
1. descendant[2]
2. descendant[1]

Report the ids of every distinct node visited as a context, including the starting node, sorted ascending as a comma-separated list inside square brackets, e.g. [2, 5, 9].

Answer: [2, 4, 5]

## Example

Use the ordered rooted tree below, written in parenthesized notation where a node lists its children left-to-right and a group with no children is a leaf.

Tree: 0(1(4(5),2(3)))
Context node: 0

Apply each axis step below in order; each step's result becomes the context for the next. The axes child, parent, descendant, ancestor, following-sibling and preceding-sibling act on the current context node, and the bracketed 1-based number selects that element of the axis result in document order (preorder, left to right).

Steps:
1. descendant[1]
2. child[2]

Report the ids of every distinct node visited as a context, including the starting node, sorted ascending as a comma-separated list inside square brackets, e.g. [2, 5, 9].

Answer: [0, 1, 2]


# Level 2

## Example

Use the ordered rooted tree below, written in parenthesized notation where a node lists its children left-to-right and a group with no children is a leaf.

Tree: 0(6(8(9)),1(7),2(4),3,5)
Context node: 0

Apply each axis step below in order; each step's result becomes the context for the next. The axes child, parent, descendant, ancestor, following-sibling and preceding-sibling act on the current context node, and the bracketed 1-based number selects that element of the axis result in document order (preorder, left to right).

Steps:
1. descendant[5]
2. ancestor[2]
3. parent[1]

Report the ids of every distinct node visited as a context, including the starting node, sorted ascending as a comma-separated list inside square brackets, e.g. [2, 5, 9].

Answer: [0, 1, 7]

## Example

Use the ordered rooted tree below, written in parenthesized notation where a node lists its children left-to-right and a group with no children is a leaf.

Tree: 0(2(3(5)),6(9,7),1,4(8))
Context node: 8

Apply each axis step below in order; each step's result becomes the context for the next. The axes child, parent, descendant, ancestor, following-sibling and preceding-sibling act on the current context node, and the bracketed 1-based number selects that element of the axis result in document order (preorder, left to right).

Steps:
1. ancestor[1]
2. descendant[4]
3. ancestor[1]

Report the ids of every distinct node visited as a context, including the starting node, sorted ascending as a comma-separated list inside square brackets, e.g. [2, 5, 9].

Answer: [0, 6, 8]


# Level 5

## Example

Use the ordered rooted tree below, written in parenthesized notation where a node lists its children left-to-right and a group with no children is a leaf.

Tree: 0(1(6,2(3,7(12,13,8),9),14,4(11)),10(15),5)
Context node: 8

Apply each axis step below in order; each step's result becomes the context for the next. The axes child, parent, descendant, ancestor, following-sibling and preceding-sibling act on the current context node, and the bracketed 1-based number selects that element of the axis result in document order (preorder, left to right).

Steps:
1. preceding-sibling[1]
2. following-sibling[2]
3. preceding-sibling[2]
4. preceding-sibling[1]

Report the ids of every distinct node visited as a context, including the starting node, sorted ascending as a comma-separated list inside square brackets, e.g. [2, 5, 9].

Answer: [8, 12, 13]

## Example

Use the ordered rooted tree below, written in parenthesized notation where a node lists its children left-to-right and a group with no children is a leaf.

Tree: 0(14,10,1(4(9),2(3)),5(6(7,8(13,15)),11(12)))
Context node: 4

Apply each axis step below in order; each step's result becomes the context for the next. The axes child, parent, descendant, ancestor, following-sibling and preceding-sibling act on the current context node, and the bracketed 1-based number selects that element of the axis result in document order (preorder, left to right).

Steps:
1. ancestor[1]
2. child[3]
3. descendant[2]
4. ancestor[1]

Report the ids of every distinct node visited as a context, including the starting node, sorted ascending as a comma-separated list inside square brackets, e.g. [2, 5, 9].

Answer: [0, 1, 4, 9]

# samples_P003v2 — affine_view_aliasing

## Level 0

**Prompt:**

In a numerical library everything is a strided view over a flat buffer. A buffer holds an implicitly indexed group of elements; here that group has shape (3), which we write with index tuple (i0). Two views both span this whole shape. View1 is anchored at flat address 5 and maps each index tuple to 5 + i0. View2 is a transposition of view1, so its stride vector (1) is a permutation of view1's; view2 is anchored at flat address 7 and maps each tuple to 7 + i0. An element is said to be aliased when the same flat address can arise from both views. Count the number of distinct flat addresses that belong to both view1's and view2's sets of produced addresses. Two views that share no flat address produce a count of zero. Give that integer count as the answer.

**Answer:**

1

**Prompt:**

In a numerical library everything is a strided view over a flat buffer. A buffer holds an implicitly indexed group of elements; here that group has shape (2, 2), which we write with index tuple (i0, i1). Two views both span this whole shape. View1 is anchored at flat address 6 and maps each index tuple to 6 + 2*i0 + 2*i1. View2 has an independently chosen stride vector (2, 2); view2 is anchored at flat address 7 and maps each tuple to 7 + 2*i0 + 2*i1. An element is said to be aliased when the same flat address can arise from both views. Count the number of distinct flat addresses that belong to both view1's and view2's sets of produced addresses. Two views that share no flat address produce a count of zero. Give that integer count as the answer.

**Answer:**

0

## Level 2

**Prompt:**

In a numerical library everything is a strided view over a flat buffer. A buffer holds an implicitly indexed group of elements; here that group has shape (3, 2), which we write with index tuple (i0, i1). Two views both span this whole shape. View1 is anchored at flat address 0 and maps each index tuple to 0 + 3*i0 + 2*i1. View2 broadcasts its leading axes, so an initial block of its stride vector (0, 0) is 0; view2 is anchored at flat address -1 and maps each tuple to -1 + 0*i0 + 0*i1. An element is said to be aliased when the same flat address can arise from both views. Count the number of distinct flat addresses that belong to both view1's and view2's sets of produced addresses. Two views that share no flat address produce a count of zero. Give that integer count as the answer.

**Answer:**

0

**Prompt:**

In a numerical library everything is a strided view over a flat buffer. A buffer holds an implicitly indexed group of elements; here that group has shape (4, 4), which we write with index tuple (i0, i1). Two views both span this whole shape. View1 is anchored at flat address 4 and maps each index tuple to 4 + 3*i0 + 2*i1. View2 has an independently chosen stride vector (3, 1); view2 is anchored at flat address 6 and maps each tuple to 6 + 3*i0 + i1. An element is said to be aliased when the same flat address can arise from both views. Count the number of distinct flat addresses that belong to both view1's and view2's sets of produced addresses. Two views that share no flat address produce a count of zero. Give that integer count as the answer.

**Answer:**

12

## Level 5

**Prompt:**

In a numerical library everything is a strided view over a flat buffer. A buffer holds an implicitly indexed group of elements; here that group has shape (3), which we write with index tuple (i0). Two views both span this whole shape. View1 is anchored at flat address 8 and maps each index tuple to 8 + 3*i0. View2 is a transposition of view1, so its stride vector (3) is a permutation of view1's; view2 is anchored at flat address 2 and maps each tuple to 2 + 3*i0. An element is said to be aliased when the same flat address can arise from both views. Count the number of distinct flat addresses that belong to both view1's and view2's sets of produced addresses. Two views that share no flat address produce a count of zero. Give that integer count as the answer.

**Answer:**

1

**Prompt:**

In a numerical library everything is a strided view over a flat buffer. A buffer holds an implicitly indexed group of elements; here that group has shape (2, 4, 2), which we write with index tuple (i0, i1, i2). Two views both span this whole shape. View1 is anchored at flat address 4 and maps each index tuple to 4 + i0 + 2*i1 + 3*i2. View2 is view1 reversed along every axis, so its stride vector (-1, -2, -3) is the elementwise negation of view1's; view2 is anchored at flat address 4 and maps each tuple to 4 + -i0 + -2*i1 + -3*i2. An element is said to be aliased when the same flat address can arise from both views. Count the number of distinct flat addresses that belong to both view1's and view2's sets of produced addresses. Two views that share no flat address produce a count of zero. Give that integer count as the answer.

**Answer:**

1

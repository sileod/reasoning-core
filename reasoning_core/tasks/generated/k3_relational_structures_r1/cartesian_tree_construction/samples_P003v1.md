# Level 0

## Example 1

**Prompt:** Given the array [4, 0, 3, 4, 2], build the max-Cartesian tree using a monotone stack with a strict comparison, so among equal values the earlier (left) element becomes the parent. The inorder traversal of the resulting tree equals the array itself. Answer with each element's parent index (0-indexed, -1 if none) in array order, then the root index, all space-separated.

**Answer:** -1 2 3 0 3 0

## Example 2

**Prompt:** Given the array [3, 3, 1, 2, 1], build the max-Cartesian tree using a monotone stack with a strict comparison, so among equal values the earlier (left) element becomes the parent. The inorder traversal of the resulting tree equals the array itself. Answer with each element's parent index (0-indexed, -1 if none) in array order, then the root index, all space-separated.

**Answer:** -1 0 3 1 3 0

# Level 2

## Example 1

**Prompt:** Given the array [1, 5, 6, 3, 5, 4, 5, 9, 2], build the max-Cartesian tree using a monotone stack with a non-strict comparison, so among equal values the later (right) element becomes the parent. The inorder traversal of the resulting tree equals the array itself. Answer with each element's parent index (0-indexed, -1 if none) in array order, then the root index, all space-separated.

**Answer:** 1 2 7 4 6 4 2 -1 7 7

## Example 2

**Prompt:** Given the array [5, 9, 5, 9, 0, 6, 10, 1, 7], build the min-Cartesian tree using a monotone stack with a non-strict comparison, so among equal values the later (right) element becomes the parent. The inorder traversal of the resulting tree equals the array itself. Answer with each element's parent index (0-indexed, -1 if none) in array order, then the root index, all space-separated.

**Answer:** 2 0 4 2 -1 7 5 4 7 4

# Level 5

## Example 1

**Prompt:** Given the array [0, 0, 14, 19, 19, 18, 7, 1, 2, 0, 16, 1, 9, 16, 13], build the max-Cartesian tree using a monotone stack with a strict comparison, so among equal values the earlier (left) element becomes the parent. The inorder traversal of the resulting tree equals the array itself. Answer with each element's parent index (0-indexed, -1 if none) in array order, then the root index, all space-separated.

**Answer:** 2 0 3 -1 3 4 10 8 6 8 5 12 13 10 13 3

## Example 2

**Prompt:** Given the array [11, 10, 6, 19, 5, 6, 2, 7, 13, 10, 16, 14, 11, 0, 7], build the max-Cartesian tree using a monotone stack with a non-strict comparison, so among equal values the later (right) element becomes the parent. The inorder traversal of the resulting tree equals the array itself. Answer with each element's parent index (0-indexed, -1 if none) in array order, then the root index, all space-separated.

**Answer:** 3 0 1 -1 5 7 5 8 10 8 3 10 11 14 12 3

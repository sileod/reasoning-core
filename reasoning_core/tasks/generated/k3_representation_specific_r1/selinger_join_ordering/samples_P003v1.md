# Samples P003v1: Selinger join ordering

## Level 0

### Example 1

**Prompt:**

We have 4 relations in a join query. Each relation has base cardinality given in order: [6, 2, 5, 6]. An edge (v:card) in the adjacency list of a relation u denotes an equi-join between u and v with that row-cardinality. The adjacency list is: 0: 2:5; 1: 2:4; 2: 0:5, 1:4, 3:3; 3: 2:3. Using Selinger dynamic programming over all subsets (the intermediate result of a set of joined relations has cardinality equal to the product of the base cardinalities of those relations), find the minimum total cost of assembling all relations into a single join tree, where the cost of each join step is the cardinality of the intermediate result it produces. Answer only the minimum total cost as an integer.

**Answer:**

430

### Example 2

**Prompt:**

We have 4 relations in a join query. Each relation has base cardinality given in order: [4, 6, 4, 6]. An edge (v:card) in the adjacency list of a relation u denotes an equi-join between u and v with that row-cardinality. The adjacency list is: 0: 3:2; 1: 2:2, 3:2; 2: 1:2, 3:6; 3: 0:2, 1:2, 2:6. Using Selinger dynamic programming over all subsets (the intermediate result of a set of joined relations has cardinality equal to the product of the base cardinalities of those relations), find the minimum total cost of assembling all relations into a single join tree, where the cost of each join step is the cardinality of the intermediate result it produces. Answer only the minimum total cost as an integer.

**Answer:**

624

## Level 2

### Example 1

**Prompt:**

We have 6 relations in a join query. Each relation has base cardinality given in order: [5, 2, 3, 2, 10, 2]. An edge (v:card) in the adjacency list of a relation u denotes an equi-join between u and v with that row-cardinality. The adjacency list is: 0: 2:8, 3:7, 4:4, 5:5; 1: 2:10, 5:5; 2: 0:8, 1:10, 5:3; 3: 0:7, 4:4, 5:4; 4: 0:4, 3:4, 5:10; 5: 0:5, 1:5, 2:3, 3:4, 4:10. Using Selinger dynamic programming over all subsets (the intermediate result of a set of joined relations has cardinality equal to the product of the base cardinalities of those relations), find the minimum total cost of assembling all relations into a single join tree, where the cost of each join step is the cardinality of the intermediate result it produces. Answer only the minimum total cost as an integer.

**Answer:**

1280

### Example 2

**Prompt:**

We have 6 relations in a join query. Each relation has base cardinality given in order: [8, 7, 6, 7, 2, 3]. An edge (v:card) in the adjacency list of a relation u denotes an equi-join between u and v with that row-cardinality. The adjacency list is: 0: 2:5, 3:9, 5:9; 1: 2:10, 3:7; 2: 0:5, 1:10, 3:9, 5:9; 3: 0:9, 1:7, 2:9, 4:9, 5:6; 4: 3:9, 5:4; 5: 0:9, 2:9, 3:6, 4:4. Using Selinger dynamic programming over all subsets (the intermediate result of a set of joined relations has cardinality equal to the product of the base cardinalities of those relations), find the minimum total cost of assembling all relations into a single join tree, where the cost of each join step is the cardinality of the intermediate result it produces. Answer only the minimum total cost as an integer.

**Answer:**

14382

## Level 5

### Example 1

**Prompt:**

We have 7 relations in a join query. Each relation has base cardinality given in order: [10, 4, 8, 11, 3, 10, 7]. An edge (v:card) in the adjacency list of a relation u denotes an equi-join between u and v with that row-cardinality. The adjacency list is: 0: 1:16, 2:3, 4:13, 5:10, 6:4; 1: 0:16, 2:12, 4:8, 5:5; 2: 0:3, 1:12, 3:15, 4:16, 5:9, 6:10; 3: 2:15, 5:9, 6:3; 4: 0:13, 1:8, 2:16, 5:5, 6:13; 5: 0:10, 1:5, 2:9, 3:9, 4:5, 6:3; 6: 0:4, 2:10, 3:3, 4:13, 5:3. Using Selinger dynamic programming over all subsets (the intermediate result of a set of joined relations has cardinality equal to the product of the base cardinalities of those relations), find the minimum total cost of assembling all relations into a single join tree, where the cost of each join step is the cardinality of the intermediate result it produces. Answer only the minimum total cost as an integer.

**Answer:**

741061

### Example 2

**Prompt:**

We have 7 relations in a join query. Each relation has base cardinality given in order: [14, 6, 13, 4, 12, 13, 13]. An edge (v:card) in the adjacency list of a relation u denotes an equi-join between u and v with that row-cardinality. The adjacency list is: 0: 1:10, 2:15, 3:15, 5:10; 1: 0:10, 3:12, 4:13, 6:5; 2: 0:15, 3:3, 4:2, 5:13, 6:3; 3: 0:15, 1:12, 2:3, 4:16, 5:12, 6:12; 4: 1:13, 2:2, 3:16, 5:12, 6:13; 5: 0:10, 2:13, 3:12, 4:12, 6:10; 6: 1:5, 2:3, 3:12, 4:13, 5:10. Using Selinger dynamic programming over all subsets (the intermediate result of a set of joined relations has cardinality equal to the product of the base cardinalities of those relations), find the minimum total cost of assembling all relations into a single join tree, where the cost of each join step is the cardinality of the intermediate result it produces. Answer only the minimum total cost as an integer.

**Answer:**

8864707


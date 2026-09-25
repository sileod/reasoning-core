## Level 0
### Example 1
Prompt:

> A quantum which-path network is a DAG with source 0 and sink 3. Edges with integer phase weights: 0->1 w=2; 0->2 w=1; 1->3 w=2; 2->1 w=2. Each path's amplitude is 2^-W where W is the sum of its edge weights. Counterfactual intervention: block edge(s) 2->1, removing any path using them. Tag 0 of the remaining indistinguishable paths as distinguishable (so all paths remain one coherent group). Combine indistinguishable paths coherently (amplitudes add, then square) and distinguishable paths incoherently (squared amplitudes add). What is the detector probability at the sink after the intervention, as a reduced fraction a/b? Answer only the fraction a/b.

Answer:

> 1/256

### Example 2
Prompt:

> A quantum which-path network is a DAG with source 0 and sink 3. Edges with integer phase weights: 0->2 w=2; 0->3 w=1; 1->2 w=2; 1->3 w=2; 2->3 w=1. Each path's amplitude is 2^-W where W is the sum of its edge weights. Counterfactual intervention: block edge(s) 0->2, removing any path using them. Tag 0 of the remaining indistinguishable paths as distinguishable (so all paths remain one coherent group). Combine indistinguishable paths coherently (amplitudes add, then square) and distinguishable paths incoherently (squared amplitudes add). What is the detector probability at the sink after the intervention, as a reduced fraction a/b? Answer only the fraction a/b.

Answer:

> 1/4

## Level 2
### Example 1
Prompt:

> A quantum which-path network is a DAG with source 5 and sink 2. Edges with integer phase weights: 1->2 w=3; 3->2 w=4; 4->0 w=3; 4->2 w=1; 4->3 w=3; 5->1 w=3; 5->2 w=1; 5->3 w=1; 5->4 w=4. Each path's amplitude is 2^-W where W is the sum of its edge weights. Counterfactual intervention: block edge(s) 5->3, removing any path using them. Tag exactly 1 of the remaining indistinguishable paths as distinguishable; the others stay one coherent group. Combine indistinguishable paths coherently (amplitudes add, then square) and distinguishable paths incoherently (squared amplitudes add). What is the detector probability at the sink after the intervention, as a reduced fraction a/b? Answer only the fraction a/b.

Answer:

> 1121345/4194304

### Example 2
Prompt:

> A quantum which-path network is a DAG with source 1 and sink 3. Edges with integer phase weights: 0->3 w=1; 1->2 w=4; 1->3 w=3; 2->0 w=3; 2->3 w=2; 4->3 w=2; 5->2 w=3; 5->3 w=4. Each path's amplitude is 2^-W where W is the sum of its edge weights. Counterfactual intervention: block edge(s) 2->0, removing any path using them. Tag exactly 1 of the remaining indistinguishable paths as distinguishable; the others stay one coherent group. Combine indistinguishable paths coherently (amplitudes add, then square) and distinguishable paths incoherently (squared amplitudes add). What is the detector probability at the sink after the intervention, as a reduced fraction a/b? Answer only the fraction a/b.

Answer:

> 65/4096

## Level 5
### Example 1
Prompt:

> A quantum which-path network is a DAG with source 3 and sink 1. Edges with integer phase weights: 0->1 w=6; 0->4 w=1; 2->0 w=3; 2->1 w=2; 2->4 w=5; 2->5 w=3; 2->8 w=3; 3->0 w=6; 3->5 w=7; 3->7 w=4; 4->1 w=3; 4->8 w=7; 5->1 w=6; 5->8 w=3; 6->0 w=2; 6->5 w=7; 6->8 w=7; 7->0 w=1; 7->1 w=1; 7->4 w=7; 7->5 w=6; 7->8 w=2. Each path's amplitude is 2^-W where W is the sum of its edge weights. Counterfactual intervention: block edge(s) 7->1; 7->5, removing any path using them. Tag 0 of the remaining indistinguishable paths as distinguishable (so all paths remain one coherent group). Combine indistinguishable paths coherently (amplitudes add, then square) and distinguishable paths incoherently (squared amplitudes add). What is the detector probability at the sink after the intervention, as a reduced fraction a/b? Answer only the fraction a/b.

Answer:

> 3969/268435456

### Example 2
Prompt:

> A quantum which-path network is a DAG with source 4 and sink 6. Edges with integer phase weights: 1->5 w=1; 1->8 w=1; 2->0 w=1; 2->5 w=1; 3->0 w=2; 3->1 w=2; 3->2 w=4; 4->1 w=7; 4->2 w=2; 4->5 w=3; 4->6 w=2; 5->0 w=5; 5->6 w=3; 7->0 w=5; 7->6 w=1; 8->2 w=2; 8->5 w=4. Each path's amplitude is 2^-W where W is the sum of its edge weights. Counterfactual intervention: block edge(s) 4->2; 4->5, removing any path using them. Tag 0 of the remaining indistinguishable paths as distinguishable (so all paths remain one coherent group). Combine indistinguishable paths coherently (amplitudes add, then square) and distinguishable paths incoherently (squared amplitudes add). What is the detector probability at the sink after the intervention, as a reduced fraction a/b? Answer only the fraction a/b.

Answer:

> 67420521/1073741824

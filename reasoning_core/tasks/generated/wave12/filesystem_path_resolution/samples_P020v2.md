## Level 0

**Prompt:** The filesystem root contains directories d0/d1/d2 and symbolic links l0->d2/d2/d0/d2; l1->d0/d0/d1. Resolve the relative path 'd1' through dot segments and links. Write one of RESOLVED, LOOP, or ESCAPE as your final answer.

**Answer:** RESOLVED


**Prompt:** The filesystem root contains directories d0/d1/d2 and symbolic links l0->d0/d0/d0/d2; l1->d0/d1. Resolve the relative path '../../..' through dot segments and links. Write one of RESOLVED, LOOP, or ESCAPE as your final answer.

**Answer:** ESCAPE


## Level 2

**Prompt:** The filesystem root contains directories d0/d1/d2/d3/d4 and symbolic links l0->l0/x; l1->d3/d0/d2; l2->d4/d3/d0/d1; l3->d3/d2/d3/d1. Resolve the relative path 'l0' through dot segments and links. Write one of RESOLVED, LOOP, or ESCAPE as your final answer.

**Answer:** LOOP


**Prompt:** The filesystem root contains directories d0/d1/d2/d3/d4 and symbolic links l0->d4/d4/d1/d1/d2; l1->d4/d0/d1/d4/d2; l2->d1/d1/d4; l3->d1/d4/d2/d0/d4. Resolve the relative path '../../..' through dot segments and links. Write one of RESOLVED, LOOP, or ESCAPE as your final answer.

**Answer:** ESCAPE


## Level 5

**Prompt:** The filesystem root contains directories d0/d1/d2/d3/d4/d5/d6/d7 and symbolic links l0->d4/d3/d3/d5/d7; l1->d2/d0/d7/d4/d1; l2->d5/d1/d0/d0/d6/d4/d5/d7; l3->d4/d3/d3/d3/d0/d0; l4->d4/d6/d1/d6; l5->d0/d1/d6/d0/d6; l6->d3/d4/d3/d2/d0/d3/d2. Resolve the relative path 'd7/d6/d2/d5' through dot segments and links. Write one of RESOLVED, LOOP, or ESCAPE as your final answer.

**Answer:** RESOLVED


**Prompt:** The filesystem root contains directories d0/d1/d2/d3/d4/d5/d6/d7 and symbolic links l0->l0/x; l1->d2/d0/d3/d1; l2->d7/d4/d5/d5/d0/d7; l3->d2/d4; l4->d5/d3; l5->d0/d2/d3/d7/d7; l6->d2/d2/d3/d5/d0/d3. Resolve the relative path 'l0' through dot segments and links. Write one of RESOLVED, LOOP, or ESCAPE as your final answer.

**Answer:** LOOP


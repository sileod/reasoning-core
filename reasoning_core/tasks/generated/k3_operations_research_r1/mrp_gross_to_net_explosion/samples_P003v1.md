# P003v1 samples

## Level 0

### Example 1

**Prompt:**
```
A factory needs its complete MRP planned-order release schedule for periods 1 through 10. Use standard gross-to-net BOM explosion, processing parents before components.
Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum requirements from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption. Carry surplus forward. For each item, work chronologically: net gross demand against carried stock plus scheduled receipts; if there is a shortage, plan a receipt in that period. LFL means exactly the shortage; multiple of k means round the shortage up to the next multiple of k. Otherwise plan nothing. A planned receipt in period t requires a release in period t minus that item's lead time.
There is no safety stock, scrap, capacity limit, backlog, or other demand/receipt. Scheduled receipts are existing commitments: do not output their releases or explode them into component demand. All necessary new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 5 | 2 | multiple of 8
B | 6 | 2 | multiple of 5
C | 3 | 1 | LFL
D | 5 | 2 | multiple of 7

Bill Of Materials:
A -> B: 2
B -> C: 1
B -> D: 1

Independent Demand:
(7,A,22);(7,C,9);(8,A,20);(8,B,3)

Scheduled Receipts:
(1,A,2);(1,B,5);(6,D,6);(7,C,7)

Return all positive planned releases for every item as (period,item,quantity) triples, ordered by increasing period then alphabetically by item, separated by semicolons with no spaces. Combine each period-item into one triple. Format example: (1,A,12);(1,C,6);(3,B,9). If there are no planned releases, return none.
```

**Answer:**
```
(1,D,21);(2,C,22);(2,D,49);(3,B,25);(3,C,45);(4,B,45);(5,A,16);(5,C,5);(6,A,24);(6,B,5);(6,C,2)
```

### Example 2

**Prompt:**
```
A factory needs its complete MRP planned-order release schedule for periods 1 through 10. Use standard gross-to-net BOM explosion, processing parents before components.
Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum requirements from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption. Carry surplus forward. For each item, work chronologically: net gross demand against carried stock plus scheduled receipts; if there is a shortage, plan a receipt in that period. LFL means exactly the shortage; multiple of k means round the shortage up to the next multiple of k. Otherwise plan nothing. A planned receipt in period t requires a release in period t minus that item's lead time.
There is no safety stock, scrap, capacity limit, backlog, or other demand/receipt. Scheduled receipts are existing commitments: do not output their releases or explode them into component demand. All necessary new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 0 | 1 | multiple of 4
B | 0 | 1 | multiple of 9
C | 1 | 1 | LFL
D | 0 | 1 | multiple of 7

Bill Of Materials:
C -> A: 3
D -> B: 3
D -> C: 2

Independent Demand:
(8,D,10);(9,A,9);(9,D,20);(10,B,8);(10,C,7)

Scheduled Receipts:
(4,A,6)

Return all positive planned releases for every item as (period,item,quantity) triples, ordered by increasing period then alphabetically by item, separated by semicolons with no spaces. Combine each period-item into one triple. Format example: (1,A,12);(1,C,6);(3,B,9). If there are no planned releases, return none.
```

**Answer:**
```
(5,A,76);(6,A,128);(6,B,45);(6,C,27);(7,B,63);(7,C,42);(7,D,14);(8,A,28);(8,D,21);(9,B,9);(9,C,7)
```

## Level 2

### Example 1

**Prompt:**
```
A factory needs its complete MRP planned-order release schedule for periods 1 through 13. Use standard gross-to-net BOM explosion, processing parents before components.
Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum requirements from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption. Carry surplus forward. For each item, work chronologically: net gross demand against carried stock plus scheduled receipts; if there is a shortage, plan a receipt in that period. LFL means exactly the shortage; multiple of k means round the shortage up to the next multiple of k. Otherwise plan nothing. A planned receipt in period t requires a release in period t minus that item's lead time.
There is no safety stock, scrap, capacity limit, backlog, or other demand/receipt. Scheduled receipts are existing commitments: do not output their releases or explode them into component demand. All necessary new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 0 | 1 | multiple of 7
B | 4 | 2 | LFL
C | 7 | 2 | LFL
D | 6 | 1 | multiple of 7
E | 3 | 2 | multiple of 8
F | 0 | 2 | LFL

Bill Of Materials:
A -> E: 3
A -> F: 2
B -> A: 2
B -> D: 2
B -> E: 1
C -> B: 1
C -> D: 3

Independent Demand:
(10,C,21);(11,C,21);(11,E,2);(13,C,22)

Scheduled Receipts:
(1,C,4);(2,A,12);(2,E,11)

Return all positive planned releases for every item as (period,item,quantity) triples, ordered by increasing period then alphabetically by item, separated by semicolons with no spaces. Combine each period-item into one triple. Format example: (1,A,12);(1,C,6);(3,B,9). If there are no planned releases, return none.
```

**Answer:**
```
(4,E,120);(4,F,84);(5,D,7);(5,E,24);(6,A,42);(6,B,6);(6,D,42);(6,E,144);(6,F,98);(7,B,21);(7,D,35);(7,E,24);(8,A,49);(8,C,10);(8,D,105);(9,B,22);(9,C,21);(10,D,63);(11,C,22)
```

### Example 2

**Prompt:**
```
A factory needs its complete MRP planned-order release schedule for periods 1 through 13. Use standard gross-to-net BOM explosion, processing parents before components.
Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum requirements from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption. Carry surplus forward. For each item, work chronologically: net gross demand against carried stock plus scheduled receipts; if there is a shortage, plan a receipt in that period. LFL means exactly the shortage; multiple of k means round the shortage up to the next multiple of k. Otherwise plan nothing. A planned receipt in period t requires a release in period t minus that item's lead time.
There is no safety stock, scrap, capacity limit, backlog, or other demand/receipt. Scheduled receipts are existing commitments: do not output their releases or explode them into component demand. All necessary new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 5 | 2 | LFL
B | 2 | 2 | LFL
C | 4 | 2 | LFL
D | 3 | 1 | LFL
E | 2 | 2 | LFL
F | 4 | 1 | LFL

Bill Of Materials:
B -> E: 1
B -> F: 2
C -> A: 2
C -> D: 2
D -> B: 1

Independent Demand:
(10,C,20);(12,C,13);(13,C,16)

Scheduled Receipts:
(4,A,6);(8,E,6)

Return all positive planned releases for every item as (period,item,quantity) triples, ordered by increasing period then alphabetically by item, separated by semicolons with no spaces. Combine each period-item into one triple. Format example: (1,A,12);(1,C,6);(3,B,9). If there are no planned releases, return none.
```

**Answer:**
```
(3,E,25);(4,F,50);(5,B,27);(5,E,26);(6,A,21);(6,E,26);(6,F,52);(7,B,26);(7,D,29);(7,F,64);(8,A,26);(8,B,32);(8,C,16);(9,A,32);(9,D,26);(10,C,13);(10,D,32);(11,C,16)
```

## Level 5

### Example 1

**Prompt:**
```
A factory needs its complete MRP planned-order release schedule for periods 1 through 16. Use standard gross-to-net BOM explosion, processing parents before components.
Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum requirements from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption. Carry surplus forward. For each item, work chronologically: net gross demand against carried stock plus scheduled receipts; if there is a shortage, plan a receipt in that period. LFL means exactly the shortage; multiple of k means round the shortage up to the next multiple of k. Otherwise plan nothing. A planned receipt in period t requires a release in period t minus that item's lead time.
There is no safety stock, scrap, capacity limit, backlog, or other demand/receipt. Scheduled receipts are existing commitments: do not output their releases or explode them into component demand. All necessary new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 2 | 2 | LFL
B | 7 | 2 | LFL
C | 0 | 2 | multiple of 7
D | 0 | 1 | LFL
E | 6 | 2 | LFL
F | 8 | 2 | multiple of 6

Bill Of Materials:
B -> A: 3
B -> D: 3
B -> E: 2
C -> A: 1
C -> B: 3
C -> D: 2
D -> A: 1
D -> F: 2
E -> A: 1
E -> D: 2

Independent Demand:
(12,C,10);(12,D,10);(13,A,12);(13,C,15);(14,C,20);(15,C,15);(16,B,8);(16,E,3)

Scheduled Receipts:
(3,E,11);(16,D,2)

Return all positive planned releases for every item as (period,item,quantity) triples, ordered by increasing period then alphabetically by item, separated by semicolons with no spaces. Combine each period-item into one triple. Format example: (1,A,12);(1,C,6);(3,B,9). If there are no planned releases, return none.
```

**Answer:**
```
(3,A,104);(3,F,204);(4,A,221);(4,F,336);(5,A,441);(5,D,106);(5,F,714);(6,A,525);(6,D,168);(6,E,53);(6,F,588);(7,A,427);(7,D,357);(7,E,84);(7,F,438);(8,A,357);(8,B,35);(8,D,294);(8,E,126);(8,F,306);(9,A,224);(9,B,42);(9,D,217);(9,E,84);(9,F,168);(10,A,65);(10,B,63);(10,C,14);(10,D,154);(10,F,54);(11,A,56);(11,B,42);(11,C,14);(11,D,84);(11,F,60);(12,A,27);(12,C,21);(12,D,28);(12,E,16);(13,C,14);(13,D,30);(14,B,8);(14,E,3)
```

### Example 2

**Prompt:**
```
A factory needs its complete MRP planned-order release schedule for periods 1 through 16. Use standard gross-to-net BOM explosion, processing parents before components.
Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum requirements from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption. Carry surplus forward. For each item, work chronologically: net gross demand against carried stock plus scheduled receipts; if there is a shortage, plan a receipt in that period. LFL means exactly the shortage; multiple of k means round the shortage up to the next multiple of k. Otherwise plan nothing. A planned receipt in period t requires a release in period t minus that item's lead time.
There is no safety stock, scrap, capacity limit, backlog, or other demand/receipt. Scheduled receipts are existing commitments: do not output their releases or explode them into component demand. All necessary new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 2 | 1 | LFL
B | 1 | 2 | LFL
C | 8 | 1 | multiple of 9
D | 4 | 1 | multiple of 6
E | 3 | 1 | LFL
F | 7 | 2 | multiple of 6
G | 2 | 1 | LFL

Bill Of Materials:
A -> C: 1
A -> D: 3
A -> E: 1
A -> G: 3
B -> D: 1
B -> F: 3
C -> B: 3
C -> E: 1
C -> F: 1
D -> F: 3
E -> F: 1
G -> E: 1
G -> F: 3

Independent Demand:
(11,A,11);(13,A,18);(14,A,16);(15,A,19)

Scheduled Receipts:
(7,A,8);(9,B,10);(9,G,7);(14,F,5)

Return all positive planned releases for every item as (period,item,quantity) triples, ordered by increasing period then alphabetically by item, separated by semicolons with no spaces. Combine each period-item into one triple. Format example: (1,A,12);(1,C,6);(3,B,9). If there are no planned releases, return none.
```

**Answer:**
```
(6,F,120);(7,F,222);(8,D,42);(8,F,378);(9,B,43);(9,D,30);(9,F,642);(10,A,1);(10,B,27);(10,D,78);(10,E,64);(10,F,396);(11,B,81);(11,C,18);(11,D,54);(11,E,75);(11,F,396);(11,G,48);(12,A,18);(12,C,9);(12,D,48);(12,E,100);(12,G,48);(13,A,16);(13,C,27);(13,D,60);(13,E,19);(13,G,57);(14,A,19)
```

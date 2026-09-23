# P008v1 samples

## Level 0

### Example 1

**Prompt:**
```
A factory runs its MRP over periods 1 through 9. Explode the bill of materials gross-to-net, processing each parent item before the components it uses. Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum component need from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption and are existing commitments (do not output their releases or explode them). Carry surplus forward. For each item work chronologically: net gross demand against carried stock plus scheduled receipts; when a net requirement exceeds zero in a period you must schedule a planned-order receipt in that period. Lot rules set only the ORDER size: LFL orders exactly the net requirement; a fixed multiple of k rounds the order up to the next multiple of k; a period quantity covering P periods orders the net requirement plus the gross requirements of the following P-1 periods. A planned receipt in period t needs a release in period t minus that item's lead time. There is no safety stock, scrap, backlog, or capacity limit.
All new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 13 | 1 | fixed multiple of 7
B | 18 | 1 | period quantity covering 3 periods
C | 3 | 1 | fixed multiple of 3

Bill Of Materials:
C -> A: 2
C -> B: 2

Independent Demand:
(6,B,2);(6,C,12);(9,C,6)

Scheduled Receipts:
(5,A,2);(8,B,1)

State the FIRST SHORTAGE PERIOD: the smallest period number between 1 and the horizon at which any item's net requirement exceeds zero, that is, the earliest period at which any planned-order receipt must be scheduled. Answer is exactly that single integer.
```

**Answer:**
```
5
```

### Example 2

**Prompt:**
```
A factory runs its MRP over periods 1 through 9. Explode the bill of materials gross-to-net, processing each parent item before the components it uses. Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum component need from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption and are existing commitments (do not output their releases or explode them). Carry surplus forward. For each item work chronologically: net gross demand against carried stock plus scheduled receipts; when a net requirement exceeds zero in a period you must schedule a planned-order receipt in that period. Lot rules set only the ORDER size: LFL orders exactly the net requirement; a fixed multiple of k rounds the order up to the next multiple of k; a period quantity covering P periods orders the net requirement plus the gross requirements of the following P-1 periods. A planned receipt in period t needs a release in period t minus that item's lead time. There is no safety stock, scrap, backlog, or capacity limit.
All new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 18 | 2 | period quantity covering 2 periods
B | 0 | 1 | fixed multiple of 5
C | 7 | 1 | period quantity covering 3 periods
D | 9 | 1 | fixed multiple of 6

Bill Of Materials:
B -> A: 2
B -> C: 2
B -> D: 2

Independent Demand:
(5,D,5);(8,A,9);(8,B,5);(9,B,13);(9,C,5)

Scheduled Receipts:
(7,C,2);(8,A,7)

State the FIRST SHORTAGE PERIOD: the smallest period number between 1 and the horizon at which any item's net requirement exceeds zero, that is, the earliest period at which any planned-order receipt must be scheduled. Answer is exactly that single integer.
```

**Answer:**
```
7
```

## Level 2

### Example 1

**Prompt:**
```
A factory runs its MRP over periods 1 through 12. Explode the bill of materials gross-to-net, processing each parent item before the components it uses. Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum component need from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption and are existing commitments (do not output their releases or explode them). Carry surplus forward. For each item work chronologically: net gross demand against carried stock plus scheduled receipts; when a net requirement exceeds zero in a period you must schedule a planned-order receipt in that period. Lot rules set only the ORDER size: LFL orders exactly the net requirement; a fixed multiple of k rounds the order up to the next multiple of k; a period quantity covering P periods orders the net requirement plus the gross requirements of the following P-1 periods. A planned receipt in period t needs a release in period t minus that item's lead time. There is no safety stock, scrap, backlog, or capacity limit.
All new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 15 | 1 | fixed multiple of 9
B | 3 | 2 | LFL
C | 11 | 2 | fixed multiple of 4
D | 12 | 1 | period quantity covering 2 periods
E | 6 | 1 | period quantity covering 2 periods

Bill Of Materials:
C -> B: 2
C -> D: 3
E -> A: 3
E -> C: 2

Independent Demand:
(7,E,12);(9,A,10);(9,E,11);(11,E,12)

Scheduled Receipts:
(11,E,7);(12,B,1)

State the FIRST SHORTAGE PERIOD: the smallest period number between 1 and the horizon at which any item's net requirement exceeds zero, that is, the earliest period at which any planned-order receipt must be scheduled. Answer is exactly that single integer.
```

**Answer:**
```
4
```

### Example 2

**Prompt:**
```
A factory runs its MRP over periods 1 through 12. Explode the bill of materials gross-to-net, processing each parent item before the components it uses. Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum component need from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption and are existing commitments (do not output their releases or explode them). Carry surplus forward. For each item work chronologically: net gross demand against carried stock plus scheduled receipts; when a net requirement exceeds zero in a period you must schedule a planned-order receipt in that period. Lot rules set only the ORDER size: LFL orders exactly the net requirement; a fixed multiple of k rounds the order up to the next multiple of k; a period quantity covering P periods orders the net requirement plus the gross requirements of the following P-1 periods. A planned receipt in period t needs a release in period t minus that item's lead time. There is no safety stock, scrap, backlog, or capacity limit.
All new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 0 | 2 | LFL
B | 8 | 2 | fixed multiple of 7
C | 13 | 1 | period quantity covering 3 periods
D | 14 | 1 | fixed multiple of 5

Bill Of Materials:
A -> B: 2
A -> C: 2
C -> D: 3

Independent Demand:
(7,A,6);(9,A,12);(11,C,8);(12,A,7)

Scheduled Receipts:
(6,B,6);(10,A,3)

State the FIRST SHORTAGE PERIOD: the smallest period number between 1 and the horizon at which any item's net requirement exceeds zero, that is, the earliest period at which any planned-order receipt must be scheduled. Answer is exactly that single integer.
```

**Answer:**
```
5
```

## Level 5

### Example 1

**Prompt:**
```
A factory runs its MRP over periods 1 through 15. Explode the bill of materials gross-to-net, processing each parent item before the components it uses. Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum component need from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption and are existing commitments (do not output their releases or explode them). Carry surplus forward. For each item work chronologically: net gross demand against carried stock plus scheduled receipts; when a net requirement exceeds zero in a period you must schedule a planned-order receipt in that period. Lot rules set only the ORDER size: LFL orders exactly the net requirement; a fixed multiple of k rounds the order up to the next multiple of k; a period quantity covering P periods orders the net requirement plus the gross requirements of the following P-1 periods. A planned receipt in period t needs a release in period t minus that item's lead time. There is no safety stock, scrap, backlog, or capacity limit.
All new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 6 | 1 | fixed multiple of 5
B | 14 | 2 | LFL
C | 13 | 2 | fixed multiple of 8
D | 13 | 2 | fixed multiple of 5
E | 18 | 1 | LFL

Bill Of Materials:
B -> C: 1
B -> D: 1
D -> A: 1
E -> B: 2

Independent Demand:
(9,B,7);(9,E,8);(11,E,12);(12,E,10);(14,E,9)

Scheduled Receipts:
(10,B,5);(13,D,8);(14,E,5)

State the FIRST SHORTAGE PERIOD: the smallest period number between 1 and the horizon at which any item's net requirement exceeds zero, that is, the earliest period at which any planned-order receipt must be scheduled. Answer is exactly that single integer.
```

**Answer:**
```
9
```

### Example 2

**Prompt:**
```
A factory runs its MRP over periods 1 through 15. Explode the bill of materials gross-to-net, processing each parent item before the components it uses. Each BOM row parent -> component: k means k units of that component are consumed per unit of parent, in the parent's planned RELEASE period, not its receipt period. Sum component need from all parents and add the listed independent demand.
On-hand is stock at the start of period 1. Scheduled receipts arrive before that period's consumption and are existing commitments (do not output their releases or explode them). Carry surplus forward. For each item work chronologically: net gross demand against carried stock plus scheduled receipts; when a net requirement exceeds zero in a period you must schedule a planned-order receipt in that period. Lot rules set only the ORDER size: LFL orders exactly the net requirement; a fixed multiple of k rounds the order up to the next multiple of k; a period quantity covering P periods orders the net requirement plus the gross requirements of the following P-1 periods. A planned receipt in period t needs a release in period t minus that item's lead time. There is no safety stock, scrap, backlog, or capacity limit.
All new releases fall within the horizon. Demand and receipt lists use (period,item,quantity).

Item Records:
item | on-hand | lead time | lot rule
A | 1 | 1 | LFL
B | 16 | 1 | LFL
C | 9 | 1 | period quantity covering 3 periods
D | 17 | 1 | fixed multiple of 5
E | 13 | 1 | period quantity covering 2 periods

Bill Of Materials:
B -> A: 2
C -> D: 1
C -> E: 1
E -> B: 2

Independent Demand:
(10,C,5);(11,A,7);(11,C,13);(12,C,10);(13,C,11)

Scheduled Receipts:
(13,B,6);(14,C,7);(14,D,2);(15,E,4)

State the FIRST SHORTAGE PERIOD: the smallest period number between 1 and the horizon at which any item's net requirement exceeds zero, that is, the earliest period at which any planned-order receipt must be scheduled. Answer is exactly that single integer.
```

**Answer:**
```
8
```

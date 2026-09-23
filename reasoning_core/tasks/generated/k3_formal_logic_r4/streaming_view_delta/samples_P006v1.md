## Level 0
### Example 1 (delta)
A streaming bag-join view joins A with B on key; an A tuple contributes to key k's sum only if k is present in B. As A tuples are inserted and retracted, the per-key sum changes. Each time a key's sum changes, emit one delta line: '+k,v' when it rises to new value v, or '-k,v' when it falls. Emit lines in event order, one per change, separated by newlines. When a key's sum becomes 0, emit '-k,0'.
B = {0, 1, 3, 4}
1. insert A(t3, key=2, qty=3, attr=2)
2. insert A(t2, key=0, qty=1, attr=0)
3. insert A(t0, key=2, qty=3, attr=1)
4. retract A(t0, key=2, qty=3, attr=1)
5. insert A(t1, key=0, qty=3, attr=1)
6. retract A(t3, key=2, qty=3, attr=2)

Deltas:

Answer:
+0,1
+0,4

### Example 2 (delta)
A streaming bag-join view joins A with B on key; an A tuple contributes to key k's sum only if k is present in B. As A tuples are inserted and retracted, the per-key sum changes. Each time a key's sum changes, emit one delta line: '+k,v' when it rises to new value v, or '-k,v' when it falls. Emit lines in event order, one per change, separated by newlines. When a key's sum becomes 0, emit '-k,0'.
B = {0, 1, 2, 3}
1. insert A(t7, key=0, qty=2, attr=2)
2. insert A(t4, key=2, qty=2, attr=1)
3. retract A(t7, key=0, qty=2, attr=2)
4. insert A(t8, key=3, qty=3, attr=2)
5. retract A(t4, key=2, qty=2, attr=1)
6. insert A(t3, key=1, qty=3, attr=0)

Deltas:

Answer:
+0,2
+2,2
-0,0
+3,3
-2,0
+1,3

## Level 2
### Example 1 (query)
A streaming bag-join view joins A with B on key; an A tuple contributes to key k's sum only if k is in B. As tuples are inserted and retracted (in event order), each key's sum changes; a later insert with a new key is a key replacement but each key keeps its own independent running sum. After processing every event, report the final corrected value (a non-negative integer) for the queried key.
B = {0, 1, 2, 4}
1. insert A(t3, key=0, qty=1, attr=0)
2. insert A(t8, key=0, qty=2, attr=2)
3. retract A(t8, key=0, qty=2, attr=2)
4. insert A(t8, key=2, qty=3, attr=2)
5. insert A(t11, key=4, qty=2, attr=1)
6. retract A(t3, key=0, qty=1, attr=0)
7. insert A(t3, key=3, qty=3, attr=1)
8. insert A(t12, key=2, qty=2, attr=0)
9. insert A(t7, key=0, qty=2, attr=2)
10. insert A(t4, key=0, qty=1, attr=1)
11. retract A(t3, key=3, qty=3, attr=1)
12. retract A(t8, key=2, qty=3, attr=2)

Query: final corrected value for key 0?

Answer:
3

### Example 2 (delta)
A streaming bag-join view joins A with B on key and then aggregates per key the sum of qty of live A tuples whose attr equals 2 (other A tuples are filtered out entirely). A key also must be present in B. Each time a key's grouped sum changes emit a delta line '+k,v' (rise) or '-k,v' (fall), in event order, one per change, newline-separated. When a key's sum becomes 0 emit '-k,0'.
B = {1, 3}
1. insert A(t2, key=4, qty=2, attr=2)
2. insert A(t0, key=3, qty=2, attr=2)
3. insert A(t8, key=2, qty=3, attr=0)
4. insert A(t7, key=4, qty=2, attr=2)
5. retract A(t7, key=4, qty=2, attr=2)
6. insert A(t7, key=3, qty=1, attr=0)
7. insert A(t6, key=0, qty=1, attr=0)
8. retract A(t2, key=4, qty=2, attr=2)
9. insert A(t3, key=2, qty=2, attr=0)
10. retract A(t0, key=3, qty=2, attr=2)
11. retract A(t3, key=2, qty=2, attr=0)
12. insert A(t3, key=0, qty=3, attr=0)

Deltas:

Answer:
+3,2
-3,0

## Level 5
### Example 1 (delta)
A streaming bag-join view joins A with B on key and then aggregates per key the sum of qty of live A tuples whose attr equals 1 (other A tuples are filtered out entirely). A key also must be present in B. Each time a key's grouped sum changes emit a delta line '+k,v' (rise) or '-k,v' (fall), in event order, one per change, newline-separated. When a key's sum becomes 0 emit '-k,0'.
B = {0, 1, 3, 4}
1. insert A(t12, key=2, qty=2, attr=0)
2. insert A(t14, key=4, qty=3, attr=1)
3. retract A(t12, key=2, qty=2, attr=0)
4. insert A(t12, key=1, qty=1, attr=2)
5. retract A(t12, key=1, qty=1, attr=2)
6. insert A(t10, key=3, qty=1, attr=1)
7. insert A(t18, key=2, qty=1, attr=0)
8. retract A(t18, key=2, qty=1, attr=0)
9. insert A(t6, key=3, qty=2, attr=1)
10. retract A(t10, key=3, qty=1, attr=1)
11. retract A(t14, key=4, qty=3, attr=1)
12. retract A(t6, key=3, qty=2, attr=1)
13. insert A(t15, key=3, qty=3, attr=2)
14. retract A(t15, key=3, qty=3, attr=2)
15. insert A(t19, key=2, qty=1, attr=0)
16. retract A(t19, key=2, qty=1, attr=0)
17. insert A(t16, key=3, qty=3, attr=1)

Deltas:

Answer:
+4,3
+3,1
+3,3
-3,2
-4,0
-3,0
+3,3

### Example 2 (query)
A streaming bag-join view joins A with B on key; an A tuple contributes to key k's sum only if k is in B. As tuples are inserted and retracted (in event order), each key's sum changes; a later insert with a new key is a key replacement but each key keeps its own independent running sum. After processing every event, report the final corrected value (a non-negative integer) for the queried key.
B = {1, 2}
1. insert A(t8, key=4, qty=1, attr=1)
2. insert A(t18, key=2, qty=2, attr=0)
3. insert A(t3, key=4, qty=1, attr=0)
4. retract A(t8, key=4, qty=1, attr=1)
5. retract A(t18, key=2, qty=2, attr=0)
6. insert A(t11, key=4, qty=1, attr=0)
7. insert A(t2, key=2, qty=3, attr=1)
8. insert A(t18, key=3, qty=2, attr=0)
9. retract A(t3, key=4, qty=1, attr=0)
10. insert A(t3, key=2, qty=1, attr=1)
11. insert A(t6, key=4, qty=3, attr=0)
12. insert A(t9, key=0, qty=2, attr=2)
13. retract A(t11, key=4, qty=1, attr=0)
14. retract A(t6, key=4, qty=3, attr=0)
15. retract A(t9, key=0, qty=2, attr=2)
16. retract A(t2, key=2, qty=3, attr=1)
17. insert A(t2, key=3, qty=3, attr=0)

Query: final corrected value for key 2?

Answer:
1


## Level 0

Prompt:
FK fk1: t1.ref1 references t0.id0 on-restrict
FK fk2: t2.ref2 references t1.id1 on-restrict
FK fk_back: t0.reflast references t2.id2 on-restrict
Initial rows:
  t0: id0=t0#0,reflast=t2#0; id0=t0#1,reflast=t2#0
  t1: id1=t1#0,ref1=t0#1; id1=t1#1,ref1=t0#0
  t2: id2=t2#0,ref2=t1#0; id2=t2#1,ref2=t1#1
Statements (0-indexed, run in order):
  0: delete from t2 where id2=t2#1
  1: insert into t2 (id2=nx819258842, ref2=t1#0)
  2: insert into t2 (id2=nx89456032, ref2=t1#0)
  3: update t2 set ref2=t1#0 where id2=nx819258842
  4: insert into t1 (id1=nx832214158, ref1=__dangling__908483947)
Execute the statements in order under the foreign-key constraints. If a statement is rejected as the first referential-integrity violation at index i by a constraint of action a (restrict, cascade, set-null, set-default), answer exactly 'i:a' (for example '3:restrict'). If no statement is rejected, answer exactly 'accepted'.

Answer: 4:restrict

Prompt:
FK fk1: t1.ref1 references t0.id0 on-restrict
FK fk2: t2.ref2 references t1.id1 on-set-null
FK fk_back: t0.reflast references t2.id2 on-set-null
Initial rows:
  t0: id0=t0#0,reflast=t2#0; id0=t0#1,reflast=t2#1
  t1: id1=t1#0,ref1=t0#1; id1=t1#1,ref1=t0#0
  t2: id2=t2#0,ref2=t1#0; id2=t2#1,ref2=t1#0
Statements (0-indexed, run in order):
  0: delete from t2 where id2=t2#1
  1: insert into t2 (id2=nx757443286, ref2=t1#0)
  2: insert into t0 (id0=nx344008720, reflast=__dangling__441465553)
  3: insert into t1 (id1=nx52507582, ref1=t0#0)
  4: update t2 set ref2=nx52507582 where id2=nx757443286
Execute the statements in order under the foreign-key constraints. If a statement is rejected as the first referential-integrity violation at index i by a constraint of action a (restrict, cascade, set-null, set-default), answer exactly 'i:a' (for example '3:restrict'). If no statement is rejected, answer exactly 'accepted'.

Answer: 2:set-null

## Level 2

Prompt:
FK fk1: t1.ref1 references t0.id0 on-restrict
FK fk2: t2.ref2 references t1.id1 on-set-null
FK fk3: t3.ref3 references t2.id2 on-set-null
FK fk_back: t0.reflast references t3.id3 on-set-default
Initial rows:
  t0: id0=t0#0,reflast=t3#1; id0=t0#1,reflast=t3#0
  t1: id1=t1#0,ref1=t0#1; id1=t1#1,ref1=t0#0
  t2: id2=t2#0,ref2=t1#0; id2=t2#1,ref2=t1#0
  t3: id3=t3#0,ref3=t2#1; id3=t3#1,ref3=t2#0
Statements (0-indexed, run in order):
  0: insert into t0 (id0=nx422864989, reflast=t3#0)
  1: update t2 set ref2=t1#1 where id2=t2#0
  2: insert into t0 (id0=nx102586916, reflast=__dangling__398202137)
  3: insert into t0 (id0=nx734266671, reflast=t3#0)
  4: update t1 set ref1=nx422864989 where id1=t1#0
  5: update t1 set ref1=nx422864989 where id1=t1#1
  6: insert into t1 (id1=nx586418700, ref1=nx734266671)
Execute the statements in order under the foreign-key constraints. If a statement is rejected as the first referential-integrity violation at index i by a constraint of action a (restrict, cascade, set-null, set-default), answer exactly 'i:a' (for example '3:restrict'). If no statement is rejected, answer exactly 'accepted'.

Answer: 2:set-default

Prompt:
FK fk1: t1.ref1 references t0.id0 on-set-null
FK fk2: t2.ref2 references t1.id1 on-set-null
FK fk3: t3.ref3 references t2.id2 on-cascade
FK fk_back: t0.reflast references t3.id3 on-set-default
Initial rows:
  t0: id0=t0#0,reflast=t3#1; id0=t0#1,reflast=t3#1
  t1: id1=t1#0,ref1=t0#1; id1=t1#1,ref1=t0#0
  t2: id2=t2#0,ref2=t1#1; id2=t2#1,ref2=t1#1
  t3: id3=t3#0,ref3=t2#0; id3=t3#1,ref3=t2#1
Statements (0-indexed, run in order):
  0: delete from t0 where id0=t0#1
  1: insert into t2 (id2=nx781819564, ref2=__dangling__893110522)
  2: delete from t3 where id3=t3#0
  3: update t1 set id1=nx865219121 where id1=t1#1
  4: update t1 set id1=nx175775640 where id1=nx865219121
  5: insert into t2 (id2=nx358642243, ref2=t1#0)
  6: insert into t1 (id1=nx418549830, ref1=t0#0)
Execute the statements in order under the foreign-key constraints. If a statement is rejected as the first referential-integrity violation at index i by a constraint of action a (restrict, cascade, set-null, set-default), answer exactly 'i:a' (for example '3:restrict'). If no statement is rejected, answer exactly 'accepted'.

Answer: 1:set-null

## Level 5

Prompt:
FK fk1: t1.ref1 references t0.id0 on-set-default
FK fk2: t2.ref2 references t1.id1 on-cascade
FK fk3: t3.ref3 references t2.id2 on-set-default
FK fk4: t4.ref4 references t3.id3 on-set-null
FK fk_back: t0.reflast references t4.id4 on-set-null
Initial rows:
  t0: id0=t0#0,reflast=t4#0; id0=t0#1,reflast=t4#1
  t1: id1=t1#0,ref1=t0#0; id1=t1#1,ref1=t0#0
  t2: id2=t2#0,ref2=t1#0; id2=t2#1,ref2=t1#0
  t3: id3=t3#0,ref3=t2#0; id3=t3#1,ref3=t2#1
  t4: id4=t4#0,ref4=t3#1; id4=t4#1,ref4=t3#0
Statements (0-indexed, run in order):
  0: update t4 set id4=nx430314163 where id4=t4#0
  1: update t0 set reflast=nx430314163 where id0=t0#0
  2: update t3 set id3=nx988467292 where id3=t3#1
  3: update t4 set ref4=t3#0 where id4=t4#1
  4: update t0 set id0=nx304025100 where id0=t0#1
  5: update t4 set ref4=t3#0 where id4=t4#1
  6: insert into t4 (id4=nx639515724, ref4=__dangling__785481226)
  7: insert into t1 (id1=nx8832948, ref1=nx304025100)
  8: insert into t0 (id0=nx741268608, reflast=t4#1)
  9: insert into t4 (id4=nx14146017, ref4=t3#0)
Execute the statements in order under the foreign-key constraints. If a statement is rejected as the first referential-integrity violation at index i by a constraint of action a (restrict, cascade, set-null, set-default), answer exactly 'i:a' (for example '3:restrict'). If no statement is rejected, answer exactly 'accepted'.

Answer: 6:set-null

Prompt:
FK fk1: t1.ref1 references t0.id0 on-set-null
FK fk2: t2.ref2 references t1.id1 on-set-null
FK fk3: t3.ref3 references t2.id2 on-set-default
FK fk4: t4.ref4 references t3.id3 on-set-null
FK fk_back: t0.reflast references t4.id4 on-restrict
Initial rows:
  t0: id0=t0#0,reflast=t4#1; id0=t0#1,reflast=t4#0
  t1: id1=t1#0,ref1=t0#1; id1=t1#1,ref1=t0#0
  t2: id2=t2#0,ref2=t1#1; id2=t2#1,ref2=t1#1
  t3: id3=t3#0,ref3=t2#1; id3=t3#1,ref3=t2#0
  t4: id4=t4#0,ref4=t3#0; id4=t4#1,ref4=t3#0
Statements (0-indexed, run in order):
  0: delete from t1 where id1=t1#1
  1: insert into t4 (id4=nx391158351, ref4=t3#1)
  2: insert into t3 (id3=nx678366109, ref3=t2#1)
  3: update t4 set ref4=t3#0 where id4=nx391158351
  4: insert into t2 (id2=nx438929028, ref2=t1#0)
  5: update t0 set reflast=t4#0 where id0=t0#0
  6: insert into t4 (id4=nx396546012, ref4=t3#1)
  7: insert into t4 (id4=nx382402807, ref4=t3#1)
  8: update t2 set ref2=t1#0 where id2=nx438929028
  9: insert into t2 (id2=nx527823249, ref2=t1#0)
Execute the statements in order under the foreign-key constraints. If a statement is rejected as the first referential-integrity violation at index i by a constraint of action a (restrict, cascade, set-null, set-default), answer exactly 'i:a' (for example '3:restrict'). If no statement is rejected, answer exactly 'accepted'.

Answer: accepted


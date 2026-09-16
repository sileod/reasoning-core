## Level 0

An LSM store processes a sequence of writes, each carrying an increasing sequence number. A put is written as `key = value`; a delete is written as `del key`. Writes are buffered in a memtable; whenever 2 writes accumulate, the memtable flushes into a sorted run that keeps, for every key touched in that batch, only its latest operation (highest sequence number). The store uses 4 distinct keys. The following sorted runs were produced by successive flushes, in chronological batch order (deletes show the plain key with `del`):
Run 0: key 17 = 11 (seq 0); key 22 = 44 (seq 1)
Run 1: key 7 = 91 (seq 2); del key 22 (seq 3)
Run 2: key 7 = 22 (seq 4); key 17 = 12 (seq 5)
Then a size-tiered full compaction merges all runs into a single final run. Merging keeps, for every key present in any run, only the operation with the highest sequence number across all runs. If that newest operation is a put, the key stays live with that value; if it is a delete (tombstone), the key is dropped, because the compaction covers all data so nothing older can resurrect it. This final run also gives the result of looking up any key: a key is present iff it appears here.
What is the final content of the compacted run? Give only the live key=value entries in increasing key order, space-separated (e.g. `3=40 8=11`). Write `empty` if no key remains.

Answer: 7=22 17=12

An LSM store processes a sequence of writes, each carrying an increasing sequence number. A put is written as `key = value`; a delete is written as `del key`. Writes are buffered in a memtable; whenever 2 writes accumulate, the memtable flushes into a sorted run that keeps, for every key touched in that batch, only its latest operation (highest sequence number). The store uses 4 distinct keys. The following sorted runs were produced by successive flushes, in chronological batch order (deletes show the plain key with `del`):
Run 0: key 24 = 58 (seq 0); key 25 = 9 (seq 1)
Run 1: key 20 = 36 (seq 3)
Run 2: key 20 = 70 (seq 5)
Then a size-tiered full compaction merges all runs into a single final run. Merging keeps, for every key present in any run, only the operation with the highest sequence number across all runs. If that newest operation is a put, the key stays live with that value; if it is a delete (tombstone), the key is dropped, because the compaction covers all data so nothing older can resurrect it. This final run also gives the result of looking up any key: a key is present iff it appears here.
What is the final content of the compacted run? Give only the live key=value entries in increasing key order, space-separated (e.g. `3=40 8=11`). Write `empty` if no key remains.

Answer: 20=70 24=58 25=9

## Level 2

An LSM store processes a sequence of writes, each carrying an increasing sequence number. A put is written as `key = value`; a delete is written as `del key`. Writes are buffered in a memtable; whenever 2 writes accumulate, the memtable flushes into a sorted run that keeps, for every key touched in that batch, only its latest operation (highest sequence number). The store uses 6 distinct keys. The following sorted runs were produced by successive flushes, in chronological batch order (deletes show the plain key with `del`):
Run 0: del key 33 (seq 0); key 35 = 49 (seq 1)
Run 1: key 37 = 28 (seq 3)
Run 2: key 35 = 63 (seq 5); del key 37 (seq 4)
Run 3: key 16 = 57 (seq 7); del key 35 (seq 6)
Run 4: key 14 = 76 (seq 9); del key 21 (seq 8)
Run 5: del key 21 (seq 10); key 35 = 39 (seq 11)
Run 6: key 35 = 76 (seq 13); key 37 = 42 (seq 12)
Then a size-tiered full compaction merges all runs into a single final run. Merging keeps, for every key present in any run, only the operation with the highest sequence number across all runs. If that newest operation is a put, the key stays live with that value; if it is a delete (tombstone), the key is dropped, because the compaction covers all data so nothing older can resurrect it. This final run also gives the result of looking up any key: a key is present iff it appears here.
What is the final content of the compacted run? Give only the live key=value entries in increasing key order, space-separated (e.g. `3=40 8=11`). Write `empty` if no key remains.

Answer: 14=76 16=57 35=76 37=42

An LSM store processes a sequence of writes, each carrying an increasing sequence number. A put is written as `key = value`; a delete is written as `del key`. Writes are buffered in a memtable; whenever 2 writes accumulate, the memtable flushes into a sorted run that keeps, for every key touched in that batch, only its latest operation (highest sequence number). The store uses 6 distinct keys. The following sorted runs were produced by successive flushes, in chronological batch order (deletes show the plain key with `del`):
Run 0: del key 19 (seq 0); del key 35 (seq 1)
Run 1: key 14 = 48 (seq 2); key 19 = 80 (seq 3)
Run 2: key 6 = 13 (seq 4); key 35 = 94 (seq 5)
Run 3: key 6 = 22 (seq 6); key 37 = 18 (seq 7)
Run 4: key 10 = 55 (seq 8); key 19 = 70 (seq 9)
Run 5: key 35 = 22 (seq 10); del key 37 (seq 11)
Run 6: del key 14 (seq 12); key 19 = 3 (seq 13)
Then a size-tiered full compaction merges all runs into a single final run. Merging keeps, for every key present in any run, only the operation with the highest sequence number across all runs. If that newest operation is a put, the key stays live with that value; if it is a delete (tombstone), the key is dropped, because the compaction covers all data so nothing older can resurrect it. This final run also gives the result of looking up any key: a key is present iff it appears here.
What is the final content of the compacted run? Give only the live key=value entries in increasing key order, space-separated (e.g. `3=40 8=11`). Write `empty` if no key remains.

Answer: 6=22 10=55 19=3 35=22

## Level 5

An LSM store processes a sequence of writes, each carrying an increasing sequence number. A put is written as `key = value`; a delete is written as `del key`. Writes are buffered in a memtable; whenever 3 writes accumulate, the memtable flushes into a sorted run that keeps, for every key touched in that batch, only its latest operation (highest sequence number). The store uses 9 distinct keys. The following sorted runs were produced by successive flushes, in chronological batch order (deletes show the plain key with `del`):
Run 0: key 8 = 68 (seq 2); key 13 = 17 (seq 1); key 51 = 27 (seq 0)
Run 1: key 13 = 49 (seq 3); key 37 = 3 (seq 5); key 50 = 90 (seq 4)
Run 2: key 8 = 56 (seq 7); key 37 = 68 (seq 6); key 51 = 73 (seq 8)
Run 3: key 33 = 45 (seq 11); key 50 = 58 (seq 10); del key 51 (seq 9)
Run 4: key 33 = 50 (seq 13); key 37 = 62 (seq 14)
Run 5: del key 33 (seq 15); key 47 = 36 (seq 17)
Run 6: del key 13 (seq 19); del key 47 (seq 20); del key 51 (seq 18)
Run 7: key 33 = 46 (seq 23); key 47 = 70 (seq 22); key 49 = 46 (seq 21)
Run 8: del key 13 (seq 25); key 37 = 97 (seq 24)
Then a size-tiered full compaction merges all runs into a single final run. Merging keeps, for every key present in any run, only the operation with the highest sequence number across all runs. If that newest operation is a put, the key stays live with that value; if it is a delete (tombstone), the key is dropped, because the compaction covers all data so nothing older can resurrect it. This final run also gives the result of looking up any key: a key is present iff it appears here.
What is the final content of the compacted run? Give only the live key=value entries in increasing key order, space-separated (e.g. `3=40 8=11`). Write `empty` if no key remains.

Answer: 8=56 33=46 37=97 47=70 49=46 50=58

An LSM store processes a sequence of writes, each carrying an increasing sequence number. A put is written as `key = value`; a delete is written as `del key`. Writes are buffered in a memtable; whenever 3 writes accumulate, the memtable flushes into a sorted run that keeps, for every key touched in that batch, only its latest operation (highest sequence number). The store uses 9 distinct keys. The following sorted runs were produced by successive flushes, in chronological batch order (deletes show the plain key with `del`):
Run 0: del key 6 (seq 2); key 12 = 97 (seq 0); del key 23 (seq 1)
Run 1: key 6 = 66 (seq 5); key 15 = 47 (seq 3)
Run 2: key 15 = 81 (seq 8); del key 23 (seq 7)
Run 3: del key 10 (seq 9); key 12 = 15 (seq 10); key 14 = 36 (seq 11)
Run 4: key 35 = 54 (seq 12); del key 43 (seq 14); key 51 = 68 (seq 13)
Run 5: key 10 = 81 (seq 17); key 15 = 91 (seq 16)
Run 6: del key 43 (seq 20)
Run 7: del key 14 (seq 23); key 43 = 77 (seq 21)
Run 8: key 23 = 28 (seq 25); key 35 = 36 (seq 24)
Then a size-tiered full compaction merges all runs into a single final run. Merging keeps, for every key present in any run, only the operation with the highest sequence number across all runs. If that newest operation is a put, the key stays live with that value; if it is a delete (tombstone), the key is dropped, because the compaction covers all data so nothing older can resurrect it. This final run also gives the result of looking up any key: a key is present iff it appears here.
What is the final content of the compacted run? Give only the live key=value entries in increasing key order, space-separated (e.g. `3=40 8=11`). Write `empty` if no key remains.

Answer: 6=66 10=81 12=15 15=91 23=28 35=36 43=77 51=68

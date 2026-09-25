## Level 0
### Example 1
**Prompt**
A bitemporal record stores history as (valid_from, valid_to) segments, each with a single value still in force over the transaction interval 2024-07-01 to 2024-12-31 (until further notice). Its current valid-time partition is:
- [2024-01-01 to 2024-03-04, value 0]
- [2024-03-04 to 2024-03-31, value 2]
At transaction time 2024-07-01 a retroactive correction is applied: the record's value becomes 0 over the valid-time interval [2024-02-15 to 2024-03-11). Slicing the affected valid-time region against the existing segment boundaries (earlier as-of views are preserved; only the currently-in-force layer changes).
Return the changed history rectangles: every maximal valid-time interval inside [2024-02-15 to 2024-03-11) whose value changes from its previous value to 0, expressed as rectangles in the format [V<valid_from>/<valid_to>,T<tz>/<frontier>], sorted ascending by valid_from and joined with ';'. Here tz=2024-07-01 and frontier=2024-12-31.
Format example: [V2024-01-01/2024-03-01,T2024-06-01/2024-06-15]

**Answer**
[V2024-03-04/2024-03-11,T2024-07-01/2024-12-31]

### Example 2
**Prompt**
A bitemporal record stores history as (valid_from, valid_to) segments, each with a single value still in force over the transaction interval 2024-07-01 to 2024-12-31 (until further notice). Its current valid-time partition is:
- [2024-01-01 to 2024-02-02, value 0]
- [2024-02-02 to 2024-03-31, value 2]
At transaction time 2024-07-01 a retroactive correction is applied: the record's value becomes 0 over the valid-time interval [2024-01-16 to 2024-02-10). Slicing the affected valid-time region against the existing segment boundaries (earlier as-of views are preserved; only the currently-in-force layer changes).
Return the changed history rectangles: every maximal valid-time interval inside [2024-01-16 to 2024-02-10) whose value changes from its previous value to 0, expressed as rectangles in the format [V<valid_from>/<valid_to>,T<tz>/<frontier>], sorted ascending by valid_from and joined with ';'. Here tz=2024-07-01 and frontier=2024-12-31.
Format example: [V2024-01-01/2024-03-01,T2024-06-01/2024-06-15]

**Answer**
[V2024-02-02/2024-02-10,T2024-07-01/2024-12-31]

## Level 2
### Example 1
**Prompt**
A bitemporal record stores history as (valid_from, valid_to) segments, each with a single value still in force over the transaction interval 2024-07-01 to 2024-12-31 (until further notice). Its current valid-time partition is:
- [2024-01-01 to 2024-01-19, value 2]
- [2024-01-19 to 2024-03-14, value 1]
- [2024-03-14 to 2024-04-25, value 2]
- [2024-04-25 to 2024-06-19, value 2]
At transaction time 2024-07-01 a retroactive correction is applied: the record's value becomes 1 over the valid-time interval [2024-01-22 to 2024-03-17). Slicing the affected valid-time region against the existing segment boundaries (earlier as-of views are preserved; only the currently-in-force layer changes).
Return the changed history rectangles: every maximal valid-time interval inside [2024-01-22 to 2024-03-17) whose value changes from its previous value to 1, expressed as rectangles in the format [V<valid_from>/<valid_to>,T<tz>/<frontier>], sorted ascending by valid_from and joined with ';'. Here tz=2024-07-01 and frontier=2024-12-31.
Format example: [V2024-01-01/2024-03-01,T2024-06-01/2024-06-15]

**Answer**
[V2024-03-14/2024-03-17,T2024-07-01/2024-12-31]

### Example 2
**Prompt**
A bitemporal record stores history as (valid_from, valid_to) segments, each with a single value still in force over the transaction interval 2024-07-01 to 2024-12-31 (until further notice). Its current valid-time partition is:
- [2024-01-01 to 2024-01-26, value 1]
- [2024-01-26 to 2024-03-31, value 2]
- [2024-03-31 to 2024-05-05, value 0]
- [2024-05-05 to 2024-06-19, value 1]
At transaction time 2024-07-01 a retroactive correction is applied: the record's value becomes 1 over the valid-time interval [2024-01-07 to 2024-03-02). Slicing the affected valid-time region against the existing segment boundaries (earlier as-of views are preserved; only the currently-in-force layer changes).
Return the changed history rectangles: every maximal valid-time interval inside [2024-01-07 to 2024-03-02) whose value changes from its previous value to 1, expressed as rectangles in the format [V<valid_from>/<valid_to>,T<tz>/<frontier>], sorted ascending by valid_from and joined with ';'. Here tz=2024-07-01 and frontier=2024-12-31.
Format example: [V2024-01-01/2024-03-01,T2024-06-01/2024-06-15]

**Answer**
[V2024-01-26/2024-03-02,T2024-07-01/2024-12-31]

## Level 5
### Example 1
**Prompt**
A bitemporal record stores history as (valid_from, valid_to) segments, each with a single value still in force over the transaction interval 2024-07-01 to 2024-12-31 (until further notice). Its current valid-time partition is:
- [2024-01-01 to 2024-01-30, value 2]
- [2024-01-30 to 2024-03-14, value 3]
- [2024-03-14 to 2024-05-21, value 2]
- [2024-05-21 to 2024-06-20, value 2]
- [2024-06-20 to 2024-07-22, value 1]
- [2024-07-22 to 2024-09-09, value 2]
- [2024-09-09 to 2024-10-17, value 1]
At transaction time 2024-07-01 a retroactive correction is applied: the record's value becomes 2 over the valid-time interval [2024-05-29 to 2024-09-06). Slicing the affected valid-time region against the existing segment boundaries (earlier as-of views are preserved; only the currently-in-force layer changes).
Return the changed history rectangles: every maximal valid-time interval inside [2024-05-29 to 2024-09-06) whose value changes from its previous value to 2, expressed as rectangles in the format [V<valid_from>/<valid_to>,T<tz>/<frontier>], sorted ascending by valid_from and joined with ';'. Here tz=2024-07-01 and frontier=2024-12-31.
Format example: [V2024-01-01/2024-03-01,T2024-06-01/2024-06-15]

**Answer**
[V2024-06-20/2024-07-22,T2024-07-01/2024-12-31]

### Example 2
**Prompt**
A bitemporal record stores history as (valid_from, valid_to) segments, each with a single value still in force over the transaction interval 2024-07-01 to 2024-12-31 (until further notice). Its current valid-time partition is:
- [2024-01-01 to 2024-02-21, value 3]
- [2024-02-21 to 2024-03-20, value 1]
- [2024-03-20 to 2024-05-09, value 0]
- [2024-05-09 to 2024-06-27, value 2]
- [2024-06-27 to 2024-08-07, value 1]
- [2024-08-07 to 2024-09-09, value 2]
- [2024-09-09 to 2024-10-17, value 3]
At transaction time 2024-07-01 a retroactive correction is applied: the record's value becomes 2 over the valid-time interval [2024-09-06 to 2024-09-10). Slicing the affected valid-time region against the existing segment boundaries (earlier as-of views are preserved; only the currently-in-force layer changes).
Return the changed history rectangles: every maximal valid-time interval inside [2024-09-06 to 2024-09-10) whose value changes from its previous value to 2, expressed as rectangles in the format [V<valid_from>/<valid_to>,T<tz>/<frontier>], sorted ascending by valid_from and joined with ';'. Here tz=2024-07-01 and frontier=2024-12-31.
Format example: [V2024-01-01/2024-03-01,T2024-06-01/2024-06-15]

**Answer**
[V2024-09-09/2024-09-10,T2024-07-01/2024-12-31]


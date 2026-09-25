# Samples for nested_port_wiring_substitution (P005v1)

## Level 0

**Prompt:**

A nested wiring template has 6 terminals indexed 0..5, arranged in ordered port boundaries; each terminal feeds exactly one other terminal, so following wires travels through repeated grafted instances. terminal 0 feeds terminal 4. terminal 1 feeds terminal 2. terminal 2 feeds terminal 0. terminal 3 feeds terminal 5. terminal 4 feeds terminal 3. terminal 5 feeds terminal 1. Starting at terminal 1, follow the feed chain hop by hop until it returns to the start (feedback). Give the mate-path: the comma-separated terminal indices visited before closing the loop, with R inserted right after a label whose next hop goes to a smaller index.

**Answer:**

1,2,0,4,3,5

---

**Prompt:**

A nested wiring template has 6 terminals indexed 0..5, arranged in ordered port boundaries; each terminal feeds exactly one other terminal, so following wires travels through repeated grafted instances. terminal 0 feeds terminal 3. terminal 1 feeds terminal 4. terminal 2 feeds terminal 5. terminal 3 feeds terminal 0. terminal 4 feeds terminal 1. terminal 5 feeds terminal 2. Starting at terminal 1, follow the feed chain hop by hop until it returns to the start (feedback). Give the mate-path: the comma-separated terminal indices visited before closing the loop, with R inserted right after a label whose next hop goes to a smaller index.

**Answer:**

1,4

---

## Level 2

**Prompt:**

A nested wiring template has 10 terminals indexed 0..9, arranged in ordered port boundaries; each terminal feeds exactly one other terminal, so following wires travels through repeated grafted instances. terminal 0 feeds terminal 1. terminal 1 feeds terminal 6. terminal 2 feeds terminal 7. terminal 3 feeds terminal 9. terminal 4 feeds terminal 3. terminal 5 feeds terminal 0. terminal 6 feeds terminal 2. terminal 7 feeds terminal 5. terminal 8 feeds terminal 4. terminal 9 feeds terminal 8. Where a hop goes leftward to a smaller index, it crosses a reversed port and is marked R. Starting at terminal 7, follow the feed chain hop by hop until it returns to the start (feedback). Give the mate-path: the comma-separated terminal indices visited before closing the loop, with R inserted right after a label whose next hop goes to a smaller index.

**Answer:**

7,R,5,R,0,1,6,R,2

---

**Prompt:**

A nested wiring template has 10 terminals indexed 0..9, arranged in ordered port boundaries; each terminal feeds exactly one other terminal, so following wires travels through repeated grafted instances. terminal 0 feeds terminal 5. terminal 1 feeds terminal 9. terminal 2 feeds terminal 4. terminal 3 feeds terminal 8. terminal 4 feeds terminal 7. terminal 5 feeds terminal 2. terminal 6 feeds terminal 1. terminal 7 feeds terminal 0. terminal 8 feeds terminal 6. terminal 9 feeds terminal 3. Where a hop goes leftward to a smaller index, it crosses a reversed port and is marked R. Starting at terminal 1, follow the feed chain hop by hop until it returns to the start (feedback). Give the mate-path: the comma-separated terminal indices visited before closing the loop, with R inserted right after a label whose next hop goes to a smaller index.

**Answer:**

1,9,R,3,8,R,6,R

---

## Level 5

**Prompt:**

A nested wiring template has 16 terminals indexed 0..15, arranged in ordered port boundaries; each terminal feeds exactly one other terminal, so following wires travels through repeated grafted instances. terminal 0 feeds terminal 13. terminal 1 feeds terminal 4. terminal 2 feeds terminal 14. terminal 3 feeds terminal 2. terminal 4 feeds terminal 12. terminal 5 feeds terminal 3. terminal 6 feeds terminal 8. terminal 7 feeds terminal 10. terminal 8 feeds terminal 15. terminal 9 feeds terminal 11. terminal 10 feeds terminal 6. terminal 11 feeds terminal 1. terminal 12 feeds terminal 7. terminal 13 feeds terminal 0. terminal 14 feeds terminal 5. terminal 15 feeds terminal 9. Where a hop goes leftward to a smaller index, it crosses a reversed port and is marked R. Starting at terminal 11, follow the feed chain hop by hop until it returns to the start (feedback). Give the mate-path: the comma-separated terminal indices visited before closing the loop, with R inserted right after a label whose next hop goes to a smaller index.

**Answer:**

11,R,1,4,12,R,7,10,R,6,8,15,R,9

---

**Prompt:**

A nested wiring template has 16 terminals indexed 0..15, arranged in ordered port boundaries; each terminal feeds exactly one other terminal, so following wires travels through repeated grafted instances. terminal 0 feeds terminal 5. terminal 1 feeds terminal 0. terminal 2 feeds terminal 6. terminal 3 feeds terminal 14. terminal 4 feeds terminal 12. terminal 5 feeds terminal 10. terminal 6 feeds terminal 3. terminal 7 feeds terminal 8. terminal 8 feeds terminal 4. terminal 9 feeds terminal 7. terminal 10 feeds terminal 2. terminal 11 feeds terminal 1. terminal 12 feeds terminal 11. terminal 13 feeds terminal 9. terminal 14 feeds terminal 15. terminal 15 feeds terminal 13. Where a hop goes leftward to a smaller index, it crosses a reversed port and is marked R. Starting at terminal 0, follow the feed chain hop by hop until it returns to the start (feedback). Give the mate-path: the comma-separated terminal indices visited before closing the loop, with R inserted right after a label whose next hop goes to a smaller index.

**Answer:**

0,5,10,R,2,6,R,3,14,15,R,13,R,9,R,7,8,R,4,12,R,11,R,1,R

---

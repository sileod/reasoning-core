# Samples for P023v1 (truth_maintenance_revision)

## Level 0

### Example 1
Prompt:
There are 6 facts with IDs 1 through 6. Each fact has a justification set: a list of fact IDs that support it. A fact is supported exactly when its justification set is non-empty and empty otherwise. Initial justification sets: {'1': [1], '2': [], '3': [3], '4': [4], '5': [], '6': [6]}. Revision 1: add a supporting premise to fact 3. After this, fact 3 is supported if its justification set is non-empty, empty otherwise. Revision 2: add a supporting premise to fact 6. After this, fact 6 is supported if its justification set is non-empty, empty otherwise. After all revisions, list the IDs of the facts still supported, in increasing order, separated by commas (e.g. '1,4,5').

Answer:
1,3,4,6

---

### Example 2
Prompt:
There are 6 facts with IDs 1 through 6. Each fact has a justification set: a list of fact IDs that support it. A fact is supported exactly when its justification set is non-empty and empty otherwise. Initial justification sets: {'1': [], '2': [], '3': [], '4': [4], '5': [5], '6': []}. Revision 1: retract (withdraw) the supporting premises from fact 1. After this, fact 1 is supported if its justification set is non-empty, empty otherwise. Revision 2: retract (withdraw) the supporting premises from fact 2. After this, fact 2 is supported if its justification set is non-empty, empty otherwise. After all revisions, list the IDs of the facts still supported, in increasing order, separated by commas (e.g. '1,4,5').

Answer:
4,5

---

## Level 2

### Example 1
Prompt:
There are 8 facts with IDs 1 through 8. Each fact has a justification set: a list of fact IDs that support it. A fact is supported exactly when its justification set is non-empty and empty otherwise. Initial justification sets: {'1': [1], '2': [2], '3': [3], '4': [], '5': [], '6': [], '7': [7], '8': [8]}. Revision 1: retract (withdraw) the supporting premises from fact 5. After this, fact 5 is supported if its justification set is non-empty, empty otherwise. Revision 2: add a supporting premise to fact 3. After this, fact 3 is supported if its justification set is non-empty, empty otherwise. Revision 3: retract (withdraw) the supporting premises from fact 7. After this, fact 7 is supported if its justification set is non-empty, empty otherwise. Revision 4: add a supporting premise to fact 7. After this, fact 7 is supported if its justification set is non-empty, empty otherwise. After all revisions, list the IDs of the facts still supported, in increasing order, separated by commas (e.g. '1,4,5').

Answer:
1,2,3,7,8

---

### Example 2
Prompt:
There are 8 facts with IDs 1 through 8. Each fact has a justification set: a list of fact IDs that support it. A fact is supported exactly when its justification set is non-empty and empty otherwise. Initial justification sets: {'1': [1], '2': [], '3': [3], '4': [], '5': [], '6': [], '7': [], '8': [8]}. Revision 1: retract (withdraw) the supporting premises from fact 2. After this, fact 2 is supported if its justification set is non-empty, empty otherwise. Revision 2: add a supporting premise to fact 3. After this, fact 3 is supported if its justification set is non-empty, empty otherwise. Revision 3: retract (withdraw) the supporting premises from fact 5. After this, fact 5 is supported if its justification set is non-empty, empty otherwise. Revision 4: retract (withdraw) the supporting premises from fact 5. After this, fact 5 is supported if its justification set is non-empty, empty otherwise. After all revisions, list the IDs of the facts still supported, in increasing order, separated by commas (e.g. '1,4,5').

Answer:
1,3,8

---

## Level 5

### Example 1
Prompt:
There are 11 facts with IDs 1 through 11. Each fact has a justification set: a list of fact IDs that support it. A fact is supported exactly when its justification set is non-empty and empty otherwise. Initial justification sets: {'1': [1], '2': [2], '3': [], '4': [4], '5': [5], '6': [6], '7': [], '8': [8], '9': [9], '10': [], '11': []}. Revision 1: retract (withdraw) the supporting premises from fact 7. After this, fact 7 is supported if its justification set is non-empty, empty otherwise. Revision 2: add a supporting premise to fact 6. After this, fact 6 is supported if its justification set is non-empty, empty otherwise. Revision 3: add a supporting premise to fact 5. After this, fact 5 is supported if its justification set is non-empty, empty otherwise. Revision 4: add a supporting premise to fact 2. After this, fact 2 is supported if its justification set is non-empty, empty otherwise. Revision 5: add a supporting premise to fact 1. After this, fact 1 is supported if its justification set is non-empty, empty otherwise. Revision 6: add a supporting premise to fact 1. After this, fact 1 is supported if its justification set is non-empty, empty otherwise. Revision 7: retract (withdraw) the supporting premises from fact 11. After this, fact 11 is supported if its justification set is non-empty, empty otherwise. After all revisions, list the IDs of the facts still supported, in increasing order, separated by commas (e.g. '1,4,5').

Answer:
1,2,4,5,6,8,9

---

### Example 2
Prompt:
There are 11 facts with IDs 1 through 11. Each fact has a justification set: a list of fact IDs that support it. A fact is supported exactly when its justification set is non-empty and empty otherwise. Initial justification sets: {'1': [], '2': [], '3': [], '4': [], '5': [5], '6': [], '7': [7], '8': [], '9': [9], '10': [], '11': [11]}. Revision 1: add a supporting premise to fact 11. After this, fact 11 is supported if its justification set is non-empty, empty otherwise. Revision 2: retract (withdraw) the supporting premises from fact 3. After this, fact 3 is supported if its justification set is non-empty, empty otherwise. Revision 3: add a supporting premise to fact 5. After this, fact 5 is supported if its justification set is non-empty, empty otherwise. Revision 4: add a supporting premise to fact 11. After this, fact 11 is supported if its justification set is non-empty, empty otherwise. Revision 5: retract (withdraw) the supporting premises from fact 8. After this, fact 8 is supported if its justification set is non-empty, empty otherwise. Revision 6: add a supporting premise to fact 1. After this, fact 1 is supported if its justification set is non-empty, empty otherwise. Revision 7: retract (withdraw) the supporting premises from fact 1. After this, fact 1 is supported if its justification set is non-empty, empty otherwise. After all revisions, list the IDs of the facts still supported, in increasing order, separated by commas (e.g. '1,4,5').

Answer:
5,7,9,11

---

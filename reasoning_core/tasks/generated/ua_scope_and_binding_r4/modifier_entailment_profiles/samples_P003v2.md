# Samples for modifier_entailment_profiles (P003v2)

Fixed predicate lexicon order: animate, concrete, material, liquid, container, edible, sharp.

## Level 0

### Example 1

**Prompt:** Each modifier has a stated denotation. 'dead', 'fresh', 'blank', 'fake', 'past', 'former' negate (privative). 'probably', 'possibly', 'allegedly', 'likely' make only possible (modal, unsettled). Other modifiers add their property (intersective). Modifier order sets scope: the LEFTmost modifier is outermost (widest scope); the modifier nearest the noun is innermost (narrowest). Base predicates are: animate, concrete, material, liquid, container, edible, sharp. A privative or modal at an outer scope nullifies all inner modifiers and the noun's base predicates. Given the phrase 'glassy fresh object', list the base predicates ENTAILED. Omit contradicted and unsettled. Answer as comma-separated atoms in the fixed order.

**Answer:** liquid

### Example 2

**Prompt:** Each modifier has a stated denotation. 'dead', 'fresh', 'blank', 'fake', 'past', 'former' negate (privative). 'probably', 'possibly', 'allegedly', 'likely' make only possible (modal, unsettled). Other modifiers add their property (intersective). Modifier order sets scope: the LEFTmost modifier is outermost (widest scope); the modifier nearest the noun is innermost (narrowest). Base predicates are: animate, concrete, material, liquid, container, edible, sharp. A privative or modal at an outer scope nullifies all inner modifiers and the noun's base predicates. Given the phrase 'tiny dead object', list the base predicates ENTAILED. Omit contradicted and unsettled. Answer as comma-separated atoms in the fixed order.

**Answer:** concrete

## Level 2

### Example 1

**Prompt:** Each modifier has a stated denotation. 'dead', 'fresh', 'blank', 'fake', 'past', 'former' negate (privative). 'probably', 'possibly', 'allegedly', 'likely' make only possible (modal, unsettled). Other modifiers add their property (intersective). Modifier order sets scope: the LEFTmost modifier is outermost (widest scope); the modifier nearest the noun is innermost (narrowest). Base predicates are: animate, concrete, material, liquid, container, edible, sharp. A privative or modal at an outer scope nullifies all inner modifiers and the noun's base predicates. Given the phrase 'wooden former cement possibly object', list the base predicates ENTAILED. Omit contradicted and unsettled. Answer as comma-separated atoms in the fixed order.

**Answer:** material

### Example 2

**Prompt:** Each modifier has a stated denotation. 'dead', 'fresh', 'blank', 'fake', 'past', 'former' negate (privative). 'probably', 'possibly', 'allegedly', 'likely' make only possible (modal, unsettled). Other modifiers add their property (intersective). Modifier order sets scope: the LEFTmost modifier is outermost (widest scope); the modifier nearest the noun is innermost (narrowest). Base predicates are: animate, concrete, material, liquid, container, edible, sharp. A privative or modal at an outer scope nullifies all inner modifiers and the noun's base predicates. Given the phrase 'hollow bright likely probably object', list the base predicates ENTAILED. Omit contradicted and unsettled. Answer as comma-separated atoms in the fixed order.

**Answer:** container,sharp

## Level 5

### Example 1

**Prompt:** Each modifier has a stated denotation. 'dead', 'fresh', 'blank', 'fake', 'past', 'former' negate (privative). 'probably', 'possibly', 'allegedly', 'likely' make only possible (modal, unsettled). Other modifiers add their property (intersective). Modifier order sets scope: the LEFTmost modifier is outermost (widest scope); the modifier nearest the noun is innermost (narrowest). Base predicates are: animate, concrete, material, liquid, container, edible, sharp. A privative or modal at an outer scope nullifies all inner modifiers and the noun's base predicates. Given the phrase 'red fake fresh allegedly possibly object', list the base predicates ENTAILED. Omit contradicted and unsettled. Answer as comma-separated atoms in the fixed order.

**Answer:** concrete

### Example 2

**Prompt:** Each modifier has a stated denotation. 'dead', 'fresh', 'blank', 'fake', 'past', 'former' negate (privative). 'probably', 'possibly', 'allegedly', 'likely' make only possible (modal, unsettled). Other modifiers add their property (intersective). Modifier order sets scope: the LEFTmost modifier is outermost (widest scope); the modifier nearest the noun is innermost (narrowest). Base predicates are: animate, concrete, material, liquid, container, edible, sharp. A privative or modal at an outer scope nullifies all inner modifiers and the noun's base predicates. Given the phrase 'wooden glass former metal hollow object', list the base predicates ENTAILED. Omit contradicted and unsettled. Answer as comma-separated atoms in the fixed order.

**Answer:** material

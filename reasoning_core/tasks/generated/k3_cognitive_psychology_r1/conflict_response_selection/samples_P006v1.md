# Samples for conflict_response_selection (P006v1)

## Level 0

### Example

In a stroop response-conflict trial, use this block's arbitrary response rule.
The word BLUE is printed in GREEN ink.
The cue is INK; the other dimension is the distractor.
Use sequential table lookup: translate a symbol at stage 1, then translate its code once at each later stage in order, then look up its key. Arrow direction has no additional meaning.
Stage 1: RED -> A; BLUE -> B; GREEN -> C; YELLOW -> D
Final keys: A -> LEFT; B -> LEFT; C -> RIGHT; D -> RIGHT
Map only the cued dimension and report its required keypress, LEFT or RIGHT. Example answer format: LEFT.
Return only the single label, without explanation.

Answer: RIGHT

### Example

In a stroop response-conflict trial, use this block's arbitrary response rule.
The word GREEN is printed in RED ink.
The cue is INK; the other dimension is the distractor.
Use sequential table lookup: translate a symbol at stage 1, then translate its code once at each later stage in order, then look up its key. Arrow direction has no additional meaning.
Stage 1: RED -> D; BLUE -> A; GREEN -> B; YELLOW -> C
Final keys: A -> LEFT; B -> RIGHT; C -> LEFT; D -> RIGHT
Map only the cued dimension and report its required keypress, LEFT or RIGHT. Example answer format: LEFT.
Return only the single label, without explanation.

Answer: RIGHT

## Level 2

### Example

In a simon response-conflict trial, use this block's arbitrary response rule.
A YELLOW square appears on the LEFT side of the screen.
The cue is COLOR. The distractor is screen side: left side means LEFT key, right side means RIGHT key, without using the code tables.
Use sequential table lookup: translate a symbol at stage 1, then translate its code once at each later stage in order, then look up its key. Arrow direction has no additional meaning.
Stage 1: RED -> D; BLUE -> C; GREEN -> A; YELLOW -> B
Stage 2: A -> A; B -> D; C -> C; D -> B
Stage 3: A -> C; B -> D; C -> B; D -> A
Final keys: A -> LEFT; B -> RIGHT; C -> RIGHT; D -> LEFT
Map both the cued and distractor dimensions to keys independently. Report CONGRUENT if their keys agree, otherwise INCONGRUENT; compare keys, not raw symbols. Example answer format: CONGRUENT.
Return only the single label, without explanation.

Answer: CONGRUENT

### Example

In a global-local response-conflict trial, use this block's arbitrary response rule.
A large F is formed entirely from small E letters.
The cue is GLOBAL (global = large letter, local = small letter); the other scale is the distractor.
Use sequential table lookup: translate a symbol at stage 1, then translate its code once at each later stage in order, then look up its key. Arrow direction has no additional meaning.
Stage 1: H -> C; S -> A; E -> D; F -> B
Stage 2: A -> D; B -> A; C -> B; D -> C
Stage 3: A -> C; B -> B; C -> D; D -> A
Final keys: A -> LEFT; B -> LEFT; C -> RIGHT; D -> RIGHT
Map only the cued dimension and report its required keypress, LEFT or RIGHT. Example answer format: LEFT.
Return only the single label, without explanation.

Answer: RIGHT

## Level 5

### Example

In a flanker response-conflict trial, use this block's arbitrary response rule.
The arrow row is < < < v < < <.
The cue is the CENTER arrow; the identical flanking arrows supply one distractor symbol.
Use sequential table lookup: translate a symbol at stage 1, then translate its code once at each later stage in order, then look up its key. Arrow direction has no additional meaning.
Stage 1: < -> A; > -> B; ^ -> C; v -> D
Stage 2: A -> D; B -> C; C -> B; D -> A
Stage 3: A -> A; B -> D; C -> C; D -> B
Stage 4: A -> B; B -> C; C -> A; D -> D
Stage 5: A -> D; B -> C; C -> B; D -> A
Stage 6: A -> C; B -> D; C -> B; D -> A
Final keys: A -> RIGHT; B -> LEFT; C -> LEFT; D -> RIGHT
Map only the cued dimension and report its required keypress, LEFT or RIGHT. Example answer format: LEFT.
Return only the single label, without explanation.

Answer: LEFT

### Example

In a flanker response-conflict trial, use this block's arbitrary response rule.
The arrow row is v v v v v v v v v.
The cue is the CENTER arrow; the identical flanking arrows supply one distractor symbol.
Use sequential table lookup: translate a symbol at stage 1, then translate its code once at each later stage in order, then look up its key. Arrow direction has no additional meaning.
Stage 1: < -> D; > -> A; ^ -> B; v -> C
Stage 2: A -> C; B -> A; C -> D; D -> B
Stage 3: A -> C; B -> D; C -> A; D -> B
Stage 4: A -> B; B -> C; C -> D; D -> A
Stage 5: A -> B; B -> C; C -> D; D -> A
Stage 6: A -> D; B -> A; C -> B; D -> C
Final keys: A -> LEFT; B -> RIGHT; C -> RIGHT; D -> LEFT
Map both the cued and distractor dimensions to keys independently. Report CONGRUENT if their keys agree, otherwise INCONGRUENT; compare keys, not raw symbols. Example answer format: CONGRUENT.
Return only the single label, without explanation.

Answer: CONGRUENT

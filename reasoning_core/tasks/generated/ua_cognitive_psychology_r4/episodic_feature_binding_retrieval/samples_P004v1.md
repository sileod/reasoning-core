# Samples for episodic_feature_binding_retrieval (P004v1)

## Level 0

### Example

Episode 1: shape = round (response Hotel)
Episode 2: texture = shiny (response Delta)
Using the recency rule that the most recent episode containing a feature overrides all earlier bindings of that feature, which response is bound to the feature 'texture' in its latest episode? Distractors appear in older episodes.
Answer with the single response token only.

Answer: Delta

### Example

Episode 1: texture = spiky (response Delta)
Episode 2: texture = cold (response Echo)
Using the recency rule that the most recent episode containing a feature overrides all earlier bindings of that feature, which response is bound to the feature 'texture' in its latest episode? Distractors appear in older episodes.
Answer with the single response token only.

Answer: Echo

## Level 2

### Example

Episode 1: shape = red (response Echo); material = loud (response India)
Episode 2: shape = shiny (response Bravo)
Episode 3: texture = cold (response India); color = shiny (response Alpha)
Episode 4: motion = loud (response Charlie); color = slow (response Delta)
Using the recency rule that the most recent episode containing a feature overrides all earlier bindings of that feature, which response is bound to the feature 'color' in its latest episode? Distractors appear in older episodes.
Answer with the single response token only.

Answer: Delta

### Example

Episode 1: shape = loud (response Hotel); motion = soft (response Echo)
Episode 2: texture = smooth (response Delta)
Episode 3: texture = slow (response Echo)
Episode 4: color = red (response Bravo); motion = fast (response India)
Using the recency rule that the most recent episode containing a feature overrides all earlier bindings of that feature, which response is bound to the feature 'shape' in its latest episode? Distractors appear in older episodes.
Answer with the single response token only.

Answer: Hotel

## Level 5

### Example

Episode 1: motion = round (response Echo); material = heavy (response Juliett); texture = large (response Hotel)
Episode 2: material = blue (response Delta); motion = blue (response Delta)
Episode 3: material = loud (response Hotel); motion = fast (response Echo)
Episode 4: speed = soft (response Alpha); temperature = hot (response Delta); texture = large (response India)
Episode 5: texture = round (response Foxtrot); shape = heavy (response Hotel)
Episode 6: color = shiny (response Golf); shape = cold (response Juliett); texture = heavy (response Alpha)
Episode 7: material = spiky (response Juliett); temperature = heavy (response Alpha)
Using the recency rule that the most recent episode containing a feature overrides all earlier bindings of that feature, which response is bound to the feature 'color' in its latest episode? Distractors appear in older episodes.
Answer with the single response token only.

Answer: Golf

### Example

Episode 1: shape = blue (response Alpha); material = spiky (response Alpha)
Episode 2: material = heavy (response Juliett)
Episode 3: temperature = heavy (response Bravo)
Episode 4: shape = shiny (response Charlie)
Episode 5: texture = hot (response Foxtrot); temperature = heavy (response Delta)
Episode 6: speed = fast (response India); temperature = shiny (response Hotel)
Episode 7: color = smooth (response Hotel)
Using the recency rule that the most recent episode containing a feature overrides all earlier bindings of that feature, which response is bound to the feature 'shape' in its latest episode? Distractors appear in older episodes.
Answer with the single response token only.

Answer: Charlie

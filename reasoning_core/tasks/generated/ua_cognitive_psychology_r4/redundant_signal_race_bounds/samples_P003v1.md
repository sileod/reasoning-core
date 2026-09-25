# Samples for P003v1: redundant_signal_race_bounds

## Level 0

### Level 0 example 1

**Prompt**

Redundant-target racing: k separate channels race to signal an onset, observed independently at fixed time points. Each channel either never finishes (is missing) or completes after a stated continuous delay. The channels are NOT assumed independent of one another. Listed per channel: channel 1: if not missing, its completion time is uniform on 1 to 7 seconds; it is missing with probability 0.21; channel 2: if not missing, its completion time is uniform on 1 to 6 seconds; it is missing with probability 0.29. Every channel is observed at the time points 2, 5 respectively, where the time point indexes seconds after onset. Let p be the probability that ALL channels remain unfinished at their listed time. Compute the feasible interval [lower, upper] for p consistent with the per-channel survival probabilities, without assuming channel independence or any particular positive correlation between them. Use the worst-case min and max consistent with only these marginals (Fréchet bounds). Answer as [lower, upper] with values as decimals, e.g. [0.12, 0.85].

**Answer**

[0.3003, 0.432]

### Level 0 example 2

**Prompt**

Redundant-target racing: k separate channels race to signal an onset, observed independently at fixed time points. Each channel either never finishes (is missing) or completes after a stated continuous delay. The channels are NOT assumed independent of one another. Listed per channel: channel 1: if not missing, its completion time is uniform on 1 to 6 seconds; it is missing with probability 0.08; channel 2: if not missing, its completion time is uniform on 1 to 6 seconds; it is missing with probability 0.28. Every channel is observed at the time points 7, 4 respectively, where the time point indexes seconds after onset. Let p be the probability that ALL channels remain unfinished at their listed time. Compute the feasible interval [lower, upper] for p consistent with the per-channel survival probabilities, without assuming channel independence or any particular positive correlation between them. Use the worst-case min and max consistent with only these marginals (Fréchet bounds). Answer as [lower, upper] with values as decimals, e.g. [0.12, 0.85].

**Answer**

[0, 0.08]

## Level 2

### Level 2 example 1

**Prompt**

Redundant-target racing: k separate channels race to signal an onset, observed independently at fixed time points. Each channel either never finishes (is missing) or completes after a stated continuous delay. The channels are NOT assumed independent of one another. Listed per channel: channel 1: if not missing, its completion time is uniform on 1 to 5 seconds; it is missing with probability 0.27; channel 2: if not missing, its completion time is uniform on 1 to 4 seconds; it is missing with probability 0.13; channel 3: if not missing, its completion time is uniform on 1 to 6 seconds; it is missing with probability 0.11; channel 4: if not missing, its completion time is uniform on 1 to 5 seconds; it is missing with probability 0.23. Every channel is observed at the time points 3, 2, 4, 5 respectively, where the time point indexes seconds after onset. Let p be the probability that ALL channels remain unfinished at their listed time. Compute the feasible interval [lower, upper] for p consistent with the per-channel survival probabilities, without assuming channel independence or any particular positive correlation between them. Use the worst-case min and max consistent with only these marginals (Fréchet bounds). Answer as [lower, upper] with values as decimals, e.g. [0.12, 0.85].

**Answer**

[0, 0.23]

### Level 2 example 2

**Prompt**

Redundant-target racing: k separate channels race to signal an onset, observed independently at fixed time points. Each channel either never finishes (is missing) or completes after a stated continuous delay. The channels are NOT assumed independent of one another. Listed per channel: channel 1: if not missing, its completion time is uniform on 1 to 5 seconds; it is missing with probability 0.24; channel 2: if not missing, its completion time is uniform on 1 to 6 seconds; it is missing with probability 0.18; channel 3: if not missing, its completion time is uniform on 1 to 5 seconds; it is missing with probability 0.19; channel 4: if not missing, its completion time is uniform on 1 to 3 seconds; it is missing with probability 0.12. Every channel is observed at the time points 3, 6, 1, 8 respectively, where the time point indexes seconds after onset. Let p be the probability that ALL channels remain unfinished at their listed time. Compute the feasible interval [lower, upper] for p consistent with the per-channel survival probabilities, without assuming channel independence or any particular positive correlation between them. Use the worst-case min and max consistent with only these marginals (Fréchet bounds). Answer as [lower, upper] with values as decimals, e.g. [0.12, 0.85].

**Answer**

[0, 0.12]

## Level 5

### Level 5 example 1

**Prompt**

Redundant-target racing: k separate channels race to signal an onset, observed independently at fixed time points. Each channel either never finishes (is missing) or completes after a stated continuous delay. The channels are NOT assumed independent of one another. Listed per channel: channel 1: if not missing, its completion time is uniform on 1 to 3 seconds; it is missing with probability 0.06; channel 2: if not missing, its completion time is uniform on 1 to 3 seconds; it is missing with probability 0.23; channel 3: if not missing, its completion time is uniform on 1 to 7 seconds; it is missing with probability 0.19; channel 4: if not missing, its completion time is uniform on 1 to 3 seconds; it is missing with probability 0.01; channel 5: if not missing, its completion time is uniform on 1 to 3 seconds; it is missing with probability 0.16; channel 6: if not missing, its completion time is uniform on 1 to 6 seconds; it is missing with probability 0.16; channel 7: if not missing, its completion time is uniform on 1 to 5 seconds; it is missing with probability 0.02. Every channel is observed at the time points 1, 8, 4, 1, 5, 7, 6 respectively, where the time point indexes seconds after onset. Let p be the probability that ALL channels remain unfinished at their listed time. Compute the feasible interval [lower, upper] for p consistent with the per-channel survival probabilities, without assuming channel independence or any particular positive correlation between them. Use the worst-case min and max consistent with only these marginals (Fréchet bounds). Answer as [lower, upper] with values as decimals, e.g. [0.12, 0.85].

**Answer**

[0, 0.02]

### Level 5 example 2

**Prompt**

Redundant-target racing: k separate channels race to signal an onset, observed independently at fixed time points. Each channel either never finishes (is missing) or completes after a stated continuous delay. The channels are NOT assumed independent of one another. Listed per channel: channel 1: if not missing, its completion time is uniform on 1 to 7 seconds; it is missing with probability 0.06; channel 2: if not missing, its completion time is uniform on 1 to 3 seconds; it is missing with probability 0.06; channel 3: if not missing, its completion time is uniform on 1 to 5 seconds; it is missing with probability 0.13; channel 4: if not missing, its completion time is uniform on 1 to 5 seconds; it is missing with probability 0.29; channel 5: if not missing, its completion time is uniform on 1 to 4 seconds; it is missing with probability 0.21; channel 6: if not missing, its completion time is uniform on 1 to 3 seconds; it is missing with probability 0.23; channel 7: if not missing, its completion time is uniform on 1 to 3 seconds; it is missing with probability 0.03. Every channel is observed at the time points 3, 4, 8, 1, 6, 1, 4 respectively, where the time point indexes seconds after onset. Let p be the probability that ALL channels remain unfinished at their listed time. Compute the feasible interval [lower, upper] for p consistent with the per-channel survival probabilities, without assuming channel independence or any particular positive correlation between them. Use the worst-case min and max consistent with only these marginals (Fréchet bounds). Answer as [lower, upper] with values as decimals, e.g. [0.12, 0.85].

**Answer**

[0, 0.03]

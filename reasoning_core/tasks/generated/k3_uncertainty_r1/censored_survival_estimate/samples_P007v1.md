## Level 0

### Example 1

Prompt:
```
A study follows 6 subjects over a 14-day horizon. Subjects who do not fail by their recorded day are censored (withdrawn); a subject withdrawn on day c is removed from risk from the start of that day. Event and withdrawal days are all distinct, so each recorded day has exactly one subject affected.

Event (failure) days, one subject each:
day 1, day 4, day 7, day 10, day 13.

Withdrawal (censoring) days, one subject each:
day 3.

Compute the product-limit (Kaplan-Meier) estimate of the probability of surviving to day 13. Walk the ordered timeline: the at-risk count at an event day is the number of subjects not yet failed and not yet withdrawn before that day, and each event multiplies the running estimate by the fraction that survived (subjects at risk minus the one who failed, over subjects at risk). Give the survival probability at day 13 as a reduced fraction, written numerator/denominator, for example 3/5.
```

Answer:
```
0/1
```

### Example 2

Prompt:
```
A study follows 6 subjects over a 14-day horizon. Subjects who do not fail by their recorded day are censored (withdrawn); a subject withdrawn on day c is removed from risk from the start of that day. Event and withdrawal days are all distinct, so each recorded day has exactly one subject affected.

Event (failure) days, one subject each:
day 3, day 11.

Withdrawal (censoring) days, one subject each:
day 10, day 12, day 13, day 14.

Compute the product-limit (Kaplan-Meier) estimate of the probability of surviving to day 9. Walk the ordered timeline: the at-risk count at an event day is the number of subjects not yet failed and not yet withdrawn before that day, and each event multiplies the running estimate by the fraction that survived (subjects at risk minus the one who failed, over subjects at risk). Give the survival probability at day 9 as a reduced fraction, written numerator/denominator, for example 3/5.
```

Answer:
```
5/6
```

## Level 2

### Example 1

Prompt:
```
A study follows 8 subjects over a 20-day horizon. Subjects who do not fail by their recorded day are censored (withdrawn); a subject withdrawn on day c is removed from risk from the start of that day. Event and withdrawal days are all distinct, so each recorded day has exactly one subject affected.

Event (failure) days, one subject each:
day 3, day 5, day 7, day 8, day 11, day 16, day 20.

Withdrawal (censoring) days, one subject each:
day 10.

Compute the product-limit (Kaplan-Meier) estimate of the probability of surviving to day 16. Walk the ordered timeline: the at-risk count at an event day is the number of subjects not yet failed and not yet withdrawn before that day, and each event multiplies the running estimate by the fraction that survived (subjects at risk minus the one who failed, over subjects at risk). Give the survival probability at day 16 as a reduced fraction, written numerator/denominator, for example 3/5.
```

Answer:
```
1/6
```

### Example 2

Prompt:
```
A study follows 8 subjects over a 20-day horizon. Subjects who do not fail by their recorded day are censored (withdrawn); a subject withdrawn on day c is removed from risk from the start of that day. Event and withdrawal days are all distinct, so each recorded day has exactly one subject affected.

Event (failure) days, one subject each:
day 3, day 4, day 20.

Withdrawal (censoring) days, one subject each:
day 1, day 2, day 7, day 10, day 12.

Compute the product-limit (Kaplan-Meier) estimate of the probability of surviving to day 18. Walk the ordered timeline: the at-risk count at an event day is the number of subjects not yet failed and not yet withdrawn before that day, and each event multiplies the running estimate by the fraction that survived (subjects at risk minus the one who failed, over subjects at risk). Give the survival probability at day 18 as a reduced fraction, written numerator/denominator, for example 3/5.
```

Answer:
```
2/3
```

## Level 5

### Example 1

Prompt:
```
A study follows 11 subjects over a 29-day horizon. Subjects who do not fail by their recorded day are censored (withdrawn); a subject withdrawn on day c is removed from risk from the start of that day. Event and withdrawal days are all distinct, so each recorded day has exactly one subject affected.

Event (failure) days, one subject each:
day 5, day 6, day 10, day 16, day 28, day 29.

Withdrawal (censoring) days, one subject each:
day 2, day 9, day 23, day 24, day 25.

Compute the product-limit (Kaplan-Meier) estimate of the probability of surviving to day 13. Walk the ordered timeline: the at-risk count at an event day is the number of subjects not yet failed and not yet withdrawn before that day, and each event multiplies the running estimate by the fraction that survived (subjects at risk minus the one who failed, over subjects at risk). Give the survival probability at day 13 as a reduced fraction, written numerator/denominator, for example 3/5.
```

Answer:
```
24/35
```

### Example 2

Prompt:
```
A study follows 11 subjects over a 29-day horizon. Subjects who do not fail by their recorded day are censored (withdrawn); a subject withdrawn on day c is removed from risk from the start of that day. Event and withdrawal days are all distinct, so each recorded day has exactly one subject affected.

Event (failure) days, one subject each:
day 2, day 9, day 18, day 19, day 22, day 27.

Withdrawal (censoring) days, one subject each:
day 1, day 10, day 11, day 16, day 23.

Compute the product-limit (Kaplan-Meier) estimate of the probability of surviving to day 13. Walk the ordered timeline: the at-risk count at an event day is the number of subjects not yet failed and not yet withdrawn before that day, and each event multiplies the running estimate by the fraction that survived (subjects at risk minus the one who failed, over subjects at risk). Give the survival probability at day 13 as a reduced fraction, written numerator/denominator, for example 3/5.
```

Answer:
```
4/5
```

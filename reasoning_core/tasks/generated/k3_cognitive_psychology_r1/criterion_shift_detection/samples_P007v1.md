# Samples for criterion_shift_detection (P007v1)

## Level 0

### Example 1

Prompt:

An observer classifies stimuli by sequential threshold simulation. Process trials in numbered order with no resets. Say signal if strength >= the current criterion, otherwise noise; equality always means signal. The listed truth is revealed AFTER each decision. A hit is signal truth answered signal; a miss is signal truth answered noise; a false alarm is noise truth answered signal; a correct rejection is noise truth answered noise. After a miss, subtract the step from the criterion. After a false alarm, add the step. Hits and correct rejections leave it unchanged. Each update applies to the next trial; there is no clipping or other change.
Initial criterion: 9; step: 1.
Trials (truth, strength):
1. signal, 7
2. noise, 10
3. noise, 11
4. signal, 12
5. noise, 10
6. noise, 9
Give the responses to ALL trials in order: yes means signal, no means noise. Answer only space-separated lowercase words, e.g. yes no yes for three trials.

Answer: no yes yes yes yes no

### Example 2

Prompt:

An observer classifies stimuli by sequential threshold simulation. Process trials in numbered order with no resets. Say signal if strength >= the current criterion, otherwise noise; equality always means signal. The listed truth is revealed AFTER each decision. A hit is signal truth answered signal; a miss is signal truth answered noise; a false alarm is noise truth answered signal; a correct rejection is noise truth answered noise. After a miss, subtract the step from the criterion. After a false alarm, add the step. Hits and correct rejections leave it unchanged. Each update applies to the next trial; there is no clipping or other change.
Initial criterion: 11; step: 3.
Trials (truth, strength):
1. signal, 7
2. signal, 12
3. noise, 10
4. noise, 9
5. noise, 14
6. signal, 10
Give the total hits and false alarms over ALL trials. Answer in the format H=3 FA=2 (format example only).

Answer: H=1 FA=2

### Example 3

Prompt:

An observer classifies stimuli by sequential threshold simulation. Process trials in numbered order with no resets. Say signal if strength >= the current criterion, otherwise noise; equality always means signal. The listed truth is revealed AFTER each decision. A hit is signal truth answered signal; a miss is signal truth answered noise; a false alarm is noise truth answered signal; a correct rejection is noise truth answered noise. After a miss, subtract the step from the criterion. After a false alarm, add the step. Hits and correct rejections leave it unchanged. Each update applies to the next trial; there is no clipping or other change.
Initial criterion: 0; step: 5.
Trials (truth, strength):
1. signal, 1
2. noise, 2
3. signal, 6
4. signal, -1
5. signal, -4
6. noise, -2
What criterion is used BEFORE deciding trial 6? Answer with one integer, e.g. -4.

Answer: -5

## Level 2

### Example 1

Prompt:

An observer classifies stimuli by sequential threshold simulation. Process trials in numbered order with no resets. Say signal if strength >= the current criterion, otherwise noise; equality always means signal. The listed truth is revealed AFTER each decision. A hit is signal truth answered signal; a miss is signal truth answered noise; a false alarm is noise truth answered signal; a correct rejection is noise truth answered noise. After a miss, subtract the step from the criterion. After a false alarm, add the step. Hits and correct rejections leave it unchanged. Each update applies to the next trial; there is no clipping or other change.
Initial criterion: -9; step: 3.
Trials (truth, strength):
1. noise, -3
2. noise, -12
3. noise, -13
4. signal, -10
5. noise, -4
6. signal, -8
7. noise, -14
8. signal, -8
9. signal, -7
10. signal, -6
11. noise, -7
12. noise, -4
13. signal, 3
14. noise, 1
Give the responses to ALL trials in order: yes means signal, no means noise. Answer only space-separated lowercase words, e.g. yes no yes for three trials.

Answer: yes no no no yes no no yes yes yes yes yes yes yes

### Example 2

Prompt:

An observer classifies stimuli by sequential threshold simulation. Process trials in numbered order with no resets. Say signal if strength >= the current criterion, otherwise noise; equality always means signal. The listed truth is revealed AFTER each decision. A hit is signal truth answered signal; a miss is signal truth answered noise; a false alarm is noise truth answered signal; a correct rejection is noise truth answered noise. After a miss, subtract the step from the criterion. After a false alarm, add the step. Hits and correct rejections leave it unchanged. Each update applies to the next trial; there is no clipping or other change.
Initial criterion: -1; step: 2.
Trials (truth, strength):
1. noise, 2
2. signal, 4
3. signal, 0
4. signal, -1
5. signal, 2
6. noise, -5
7. noise, -1
8. noise, -3
9. noise, -3
10. signal, 1
11. signal, 2
12. signal, -1
13. signal, -4
14. signal, -3
Give the total hits and false alarms over ALL trials. Answer in the format H=3 FA=2 (format example only).

Answer: H=6 FA=2

### Example 3

Prompt:

An observer classifies stimuli by sequential threshold simulation. Process trials in numbered order with no resets. Say signal if strength >= the current criterion, otherwise noise; equality always means signal. The listed truth is revealed AFTER each decision. A hit is signal truth answered signal; a miss is signal truth answered noise; a false alarm is noise truth answered signal; a correct rejection is noise truth answered noise. After a miss, subtract the step from the criterion. After a false alarm, add the step. Hits and correct rejections leave it unchanged. Each update applies to the next trial; there is no clipping or other change.
Initial criterion: -1; step: 5.
Trials (truth, strength):
1. signal, 6
2. signal, -9
3. noise, 2
4. signal, 0
5. noise, 5
6. noise, 6
7. signal, 12
8. signal, 14
9. signal, 16
10. signal, 8
11. noise, 4
12. noise, 9
13. noise, 2
14. noise, 6
What criterion is used BEFORE deciding trial 12? Answer with one integer, e.g. -4.

Answer: 9

## Level 5

### Example 1

Prompt:

An observer classifies stimuli by sequential threshold simulation. Process trials in numbered order with no resets. Say signal if strength >= the current criterion, otherwise noise; equality always means signal. The listed truth is revealed AFTER each decision. A hit is signal truth answered signal; a miss is signal truth answered noise; a false alarm is noise truth answered signal; a correct rejection is noise truth answered noise. After a miss, subtract the step from the criterion. After a false alarm, add the step. Hits and correct rejections leave it unchanged. Each update applies to the next trial; there is no clipping or other change.
Initial criterion: -4; step: 2.
Trials (truth, strength):
1. signal, -7
2. noise, -6
3. signal, -6
4. noise, -10
5. noise, -8
6. signal, -8
7. noise, -6
8. noise, -3
9. noise, -1
10. signal, -1
11. signal, -1
12. signal, -5
13. signal, -5
14. signal, -9
15. noise, -2
16. signal, -6
17. noise, -2
18. noise, -8
19. noise, -1
20. noise, -5
21. signal, 1
22. noise, 2
23. signal, -1
24. signal, -1
25. noise, -6
26. signal, -2
Give the responses to ALL trials in order: yes means signal, no means noise. Answer only space-separated lowercase words, e.g. yes no yes for three trials.

Answer: no yes no no no no yes yes yes yes yes no no no yes yes yes no yes no yes yes no yes no yes

### Example 2

Prompt:

An observer classifies stimuli by sequential threshold simulation. Process trials in numbered order with no resets. Say signal if strength >= the current criterion, otherwise noise; equality always means signal. The listed truth is revealed AFTER each decision. A hit is signal truth answered signal; a miss is signal truth answered noise; a false alarm is noise truth answered signal; a correct rejection is noise truth answered noise. After a miss, subtract the step from the criterion. After a false alarm, add the step. Hits and correct rejections leave it unchanged. Each update applies to the next trial; there is no clipping or other change.
Initial criterion: -7; step: 4.
Trials (truth, strength):
1. noise, 1
2. signal, -4
3. noise, -15
4. noise, -10
5. signal, -4
6. signal, -11
7. signal, -6
8. signal, -19
9. noise, -21
10. noise, -13
11. signal, -3
12. signal, -15
13. signal, -6
14. signal, -19
15. signal, -20
16. noise, -21
17. signal, -7
18. noise, -27
19. noise, -3
20. signal, -10
21. signal, -19
22. signal, -14
23. signal, -18
24. signal, -20
25. noise, -27
26. signal, -29
Give the total hits and false alarms over ALL trials. Answer in the format H=3 FA=2 (format example only).

Answer: H=8 FA=4

### Example 3

Prompt:

An observer classifies stimuli by sequential threshold simulation. Process trials in numbered order with no resets. Say signal if strength >= the current criterion, otherwise noise; equality always means signal. The listed truth is revealed AFTER each decision. A hit is signal truth answered signal; a miss is signal truth answered noise; a false alarm is noise truth answered signal; a correct rejection is noise truth answered noise. After a miss, subtract the step from the criterion. After a false alarm, add the step. Hits and correct rejections leave it unchanged. Each update applies to the next trial; there is no clipping or other change.
Initial criterion: -7; step: 4.
Trials (truth, strength):
1. noise, -6
2. noise, -11
3. signal, -2
4. noise, -15
5. noise, 3
6. noise, 2
7. noise, -2
8. noise, 3
9. signal, 1
10. noise, -4
11. signal, -5
12. signal, -2
13. noise, -9
14. signal, -10
15. noise, -9
16. signal, -9
17. signal, -13
18. noise, -12
19. noise, -11
20. signal, 1
21. noise, 1
22. signal, -7
23. noise, -8
24. noise, -10
25. signal, -13
26. noise, -9
What criterion is used BEFORE deciding trial 23? Answer with one integer, e.g. -4.

Answer: -7

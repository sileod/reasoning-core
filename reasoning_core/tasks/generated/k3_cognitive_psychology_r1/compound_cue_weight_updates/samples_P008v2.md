# Samples: compound_cue_weight_updates

## Level 0

### Example 1

Prompt:

A conditioning model uses the Rescorla-Wagner error-correction rule. All cue weights start at 0. On each training trial, prediction is the sum of the weights of the shown cues. Compute error = outcome - prediction once, then simultaneously add rate(cue) * error to each shown cue's weight. Absent cues do not change. Weights remain signed, without clipping or rounding.
Cue learning rates: A=1/3, B=1/6.
Read the schedule left to right: + means outcome 1, - means outcome 0; letters together mean simultaneous cues. For example, AB- x2 means two successive trials with A and B together and outcome 0, recomputing error each time.
Schedule: AB+ x2; B+ x2; B+ x1; A+ x2; AB+ x2.
The next trial is an unreinforced probe showing A and B together, with no other cues. Before any probe update, which cue predicts the stronger response? Compare their learned signed weights, not absolute magnitudes: the larger weight wins. There is no tie. Answer with a single letter, A or B (for example: A).

Answer: A

### Example 2

Prompt:

A conditioning model uses the Rescorla-Wagner error-correction rule. All cue weights start at 0. On each training trial, prediction is the sum of the weights of the shown cues. Compute error = outcome - prediction once, then simultaneously add rate(cue) * error to each shown cue's weight. Absent cues do not change. Weights remain signed, without clipping or rounding.
Cue learning rates: A=1/6, B=1/6.
Read the schedule left to right: + means outcome 1, - means outcome 0; letters together mean simultaneous cues. For example, AB- x2 means two successive trials with A and B together and outcome 0, recomputing error each time.
Schedule: AB- x2; B- x2; A+ x1; AB- x2; A+ x1.
The next trial is an unreinforced probe showing A and B together, with no other cues. Before any probe update, which cue predicts the stronger response? Compare their learned signed weights, not absolute magnitudes: the larger weight wins. There is no tie. Answer with a single letter, A or B (for example: A).

Answer: A

## Level 2

### Example 1

Prompt:

A conditioning model uses the Rescorla-Wagner error-correction rule. All cue weights start at 0. On each training trial, prediction is the sum of the weights of the shown cues. Compute error = outcome - prediction once, then simultaneously add rate(cue) * error to each shown cue's weight. Absent cues do not change. Weights remain signed, without clipping or rounding.
Cue learning rates: A=1/6, B=1/3, C=1/3.
Read the schedule left to right: + means outcome 1, - means outcome 0; letters together mean simultaneous cues. For example, AB- x2 means two successive trials with A and B together and outcome 0, recomputing error each time.
Schedule: AB- x2; C+ x3; AB- x1; ABC- x1; B- x2; ABC- x3; AB+ x1; B- x3; C- x2.
The next trial is an unreinforced probe showing A and B together, with no other cues. Before any probe update, which cue predicts the stronger response? Compare their learned signed weights, not absolute magnitudes: the larger weight wins. There is no tie. Answer with a single letter, A or B (for example: A).

Answer: B

### Example 2

Prompt:

A conditioning model uses the Rescorla-Wagner error-correction rule. All cue weights start at 0. On each training trial, prediction is the sum of the weights of the shown cues. Compute error = outcome - prediction once, then simultaneously add rate(cue) * error to each shown cue's weight. Absent cues do not change. Weights remain signed, without clipping or rounding.
Cue learning rates: A=1/4, B=1/6, C=1/3.
Read the schedule left to right: + means outcome 1, - means outcome 0; letters together mean simultaneous cues. For example, AB- x2 means two successive trials with A and B together and outcome 0, recomputing error each time.
Schedule: B- x3; A- x2; ABC+ x1; C+ x2; AC- x3; C+ x3; BC- x2; ABC+ x3; C+ x2.
The next trial is an unreinforced probe showing A and B together, with no other cues. Before any probe update, which cue predicts the stronger response? Compare their learned signed weights, not absolute magnitudes: the larger weight wins. There is no tie. Answer with a single letter, A or B (for example: A).

Answer: A

## Level 5

### Example 1

Prompt:

A conditioning model uses the Rescorla-Wagner error-correction rule. All cue weights start at 0. On each training trial, prediction is the sum of the weights of the shown cues. Compute error = outcome - prediction once, then simultaneously add rate(cue) * error to each shown cue's weight. Absent cues do not change. Weights remain signed, without clipping or rounding.
Cue learning rates: A=1/4, B=1/3, C=1/6, D=1/3.
Read the schedule left to right: + means outcome 1, - means outcome 0; letters together mean simultaneous cues. For example, AB- x2 means two successive trials with A and B together and outcome 0, recomputing error each time.
Schedule: C+ x3; ACD+ x4; BCD- x2; BCD- x2; BCD+ x4; AD- x4; A+ x4; AD+ x3; A- x2; A+ x4; BC- x4; BCD- x2; BD+ x1; ABC- x2; B+ x4.
The next trial is an unreinforced probe showing A and B together, with no other cues. Before any probe update, which cue predicts the stronger response? Compare their learned signed weights, not absolute magnitudes: the larger weight wins. There is no tie. Answer with a single letter, A or B (for example: A).

Answer: B

### Example 2

Prompt:

A conditioning model uses the Rescorla-Wagner error-correction rule. All cue weights start at 0. On each training trial, prediction is the sum of the weights of the shown cues. Compute error = outcome - prediction once, then simultaneously add rate(cue) * error to each shown cue's weight. Absent cues do not change. Weights remain signed, without clipping or rounding.
Cue learning rates: A=1/4, B=1/6, C=1/6, D=1/6.
Read the schedule left to right: + means outcome 1, - means outcome 0; letters together mean simultaneous cues. For example, AB- x2 means two successive trials with A and B together and outcome 0, recomputing error each time.
Schedule: ACD+ x3; CD- x4; A+ x4; AD+ x2; AD+ x3; ABC- x3; AB+ x4; B- x3; AD- x3; AB+ x1; BC- x2; AD+ x4; AD- x4; C+ x1; A+ x3.
The next trial is an unreinforced probe showing A and B together, with no other cues. Before any probe update, which cue predicts the stronger response? Compare their learned signed weights, not absolute magnitudes: the larger weight wins. There is no tie. Answer with a single letter, A or B (for example: A).

Answer: A

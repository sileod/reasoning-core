## Level 0
### Example 1
Prompt:
A vessel is refilled through a sequence of guarded, resetting legs in a piecewise-affine flow. The level x(t) starts at x0 = 2.
   Leg 1: level rises at rate 8; the sensor level starts at 5 and rises at rate 2; when the sensor fires the level resets to 2*(level at that instant) + 2.
   Leg 2: level rises at rate 7; the sensor level starts at 15 and rises at rate 5; when the sensor fires the level resets to 1*(level at that instant) + 2.
Each leg k runs from the moment the previous sensor fired until this leg's sensor fires; it lasts tau_k = (l_k - x)/(a_k - s_k) and, when it fires, the level is reset as above. The final event time T is the absolute time at which the last (Leg 2) sensor fires, i.e. T = tau_1 + ... + tau_2.
What is the exact one-sided sensitivity dT/dx0, i.e. how much the final event time moves per unit increase in the initial level x0?
Answer as an exact reduced fraction such as 3/5 or -7/2 (it may be negative, zero, or an integer).
Answer:
1/6

### Example 2
Prompt:
A vessel is refilled through a sequence of guarded, resetting legs in a piecewise-affine flow. The level x(t) starts at x0 = 3.
   Leg 1: level rises at rate 8; the sensor level starts at 11 and rises at rate 7; when the sensor fires the level resets to 1*(level at that instant) + 4.
   Leg 2: level rises at rate 6; the sensor level starts at 73 and rises at rate 1; when the sensor fires the level resets to 1*(level at that instant) + 0.
Each leg k runs from the moment the previous sensor fired until this leg's sensor fires; it lasts tau_k = (l_k - x)/(a_k - s_k) and, when it fires, the level is reset as above. The final event time T is the absolute time at which the last (Leg 2) sensor fires, i.e. T = tau_1 + ... + tau_2.
What is the exact one-sided sensitivity dT/dx0, i.e. how much the final event time moves per unit increase in the initial level x0?
Answer as an exact reduced fraction such as 3/5 or -7/2 (it may be negative, zero, or an integer).
Answer:
2/5

## Level 2
### Example 1
Prompt:
A vessel is refilled through a sequence of guarded, resetting legs in a piecewise-affine flow. The level x(t) starts at x0 = 4.
   Leg 1: level rises at rate 6; the sensor level starts at 11 and rises at rate 4; when the sensor fires the level resets to 2*(level at that instant) + 4.
Each leg k runs from the moment the previous sensor fired until this leg's sensor fires; it lasts tau_k = (l_k - x)/(a_k - s_k) and, when it fires, the level is reset as above. The final event time T is the absolute time at which the last (Leg 1) sensor fires, i.e. T = tau_1 + ... + tau_1.
What is the exact one-sided sensitivity dT/dx0, i.e. how much the final event time moves per unit increase in the initial level x0?
Answer as an exact reduced fraction such as 3/5 or -7/2 (it may be negative, zero, or an integer).
Answer:
-1/2

### Example 2
Prompt:
A vessel is refilled through a sequence of guarded, resetting legs in a piecewise-affine flow. The level x(t) starts at x0 = 5.
   Leg 1: level rises at rate 8; the sensor level starts at 7 and rises at rate 7; when the sensor fires the level resets to 1*(level at that instant) + 2.
Each leg k runs from the moment the previous sensor fired until this leg's sensor fires; it lasts tau_k = (l_k - x)/(a_k - s_k) and, when it fires, the level is reset as above. The final event time T is the absolute time at which the last (Leg 1) sensor fires, i.e. T = tau_1 + ... + tau_1.
What is the exact one-sided sensitivity dT/dx0, i.e. how much the final event time moves per unit increase in the initial level x0?
Answer as an exact reduced fraction such as 3/5 or -7/2 (it may be negative, zero, or an integer).
Answer:
-1

## Level 5
### Example 1
Prompt:
A vessel is refilled through a sequence of guarded, resetting legs in a piecewise-affine flow. The level x(t) starts at x0 = 2.
   Leg 1: level rises at rate 5; the sensor level starts at 7 and rises at rate 1; when the sensor fires the level resets to 1*(level at that instant) + 4.
   Leg 2: level rises at rate 6; the sensor level starts at 18 and rises at rate 5; when the sensor fires the level resets to 2*(level at that instant) + 4.
   Leg 3: level rises at rate 8; the sensor level starts at 98 and rises at rate 5; when the sensor fires the level resets to 1*(level at that instant) + 1.
Each leg k runs from the moment the previous sensor fired until this leg's sensor fires; it lasts tau_k = (l_k - x)/(a_k - s_k) and, when it fires, the level is reset as above. The final event time T is the absolute time at which the last (Leg 3) sensor fires, i.e. T = tau_1 + ... + tau_3.
What is the exact one-sided sensitivity dT/dx0, i.e. how much the final event time moves per unit increase in the initial level x0?
Answer as an exact reduced fraction such as 3/5 or -7/2 (it may be negative, zero, or an integer).
Answer:
-5/6

### Example 2
Prompt:
A vessel is refilled through a sequence of guarded, resetting legs in a piecewise-affine flow. The level x(t) starts at x0 = 4.
   Leg 1: level rises at rate 5; the sensor level starts at 8 and rises at rate 1; when the sensor fires the level resets to 2*(level at that instant) + 3.
Each leg k runs from the moment the previous sensor fired until this leg's sensor fires; it lasts tau_k = (l_k - x)/(a_k - s_k) and, when it fires, the level is reset as above. The final event time T is the absolute time at which the last (Leg 1) sensor fires, i.e. T = tau_1 + ... + tau_1.
What is the exact one-sided sensitivity dT/dx0, i.e. how much the final event time moves per unit increase in the initial level x0?
Answer as an exact reduced fraction such as 3/5 or -7/2 (it may be negative, zero, or an integer).
Answer:
-1/4


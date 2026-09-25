# Level 0
## Example 1
Prompt:
Points of a single-input scalar trace, in order: 9, 27, -3, -3, -11, 37, -3, 27, 15, 16.
The trace is confined between bounds -11 and 43.
In the return-point memory model, an excursion that returns to a point already visited is closed and the extrema between them are erased. Saturate at the stated bounds.
After fully reducing the reversal history, list every surviving turning-point value (still-confined extrema) in chronological order, as comma-separated integers. If none survive, answer `none`.

Answer:
9, 15, 16

---

## Example 2
Prompt:
Points of a single-input scalar trace, in order: -13, -53, 18, -53, -53, -7, -13, -53, 18, 24.
The trace is confined between bounds -53 and 27.
In the return-point memory model, an excursion that returns to a point already visited is closed and the extrema between them are erased. Saturate at the stated bounds.
After fully reducing the reversal history, list every surviving turning-point value (still-confined extrema) in chronological order, as comma-separated integers. If none survive, answer `none`.

Answer:
-13, -53, 18, 24

---

# Level 2
## Example 1
Prompt:
Points of a single-input scalar trace, in order: 1, 39, -36, 24, 39, 11, 39, 27, 39, 39, 6, -29, 39, 39, 2, -6, 37.
The trace is confined between bounds -43 and 39.
In the return-point memory model, an excursion that returns to a point already visited is closed and the extrema between them are erased. Saturate at the stated bounds.
After fully reducing the reversal history, list every surviving turning-point value (still-confined extrema) in chronological order, as comma-separated integers. If none survive, answer `none`.

Answer:
1, 24, 27, 39, 6, 2, -6, 37

---

## Example 2
Prompt:
Points of a single-input scalar trace, in order: -3, -53, 39, -53, 41, -17, -53, 41, 57, 24, 57, 6, 57, 23, -30, -29, 11, 57, 57, 57, 57, 45.
The trace is confined between bounds -53 and 57.
In the return-point memory model, an excursion that returns to a point already visited is closed and the extrema between them are erased. Saturate at the stated bounds.
After fully reducing the reversal history, list every surviving turning-point value (still-confined extrema) in chronological order, as comma-separated integers. If none survive, answer `none`.

Answer:
-3, -17, -53, 41, 57, 23, 11, 45

---

# Level 5
## Example 1
Prompt:
Points of a single-input scalar trace, in order: 11, 31, 46, 20, 46, 27, -23, 39, -19, -23, 10, -23, 9, 39, -23, 23, 46, 23, -23, -23, 24, 3, -19, 3, -6, 0, 11, 23, -23, -23, 3, 19.
The trace is confined between bounds -23 and 46.
In the return-point memory model, an excursion that returns to a point already visited is closed and the extrema between them are erased. The trace alternates drives; at the end the active drive is rising.
What is the output value? Answer with the single integer value the active rising drive emanates from (the rising branch's endpoint under saturation).

Answer:
46

---

## Example 2
Prompt:
Points of a single-input scalar trace, in order: -2, -14, -16, 15, -4, 16, 17, -16, -5, 11, -8, 17, 8, 11, 17, -5, -6, -2, 15, 17, 2, 1, 8, 17, -14, 12, -13, 11, 7, -11, -14, -11, 17, -6.
The trace is confined between bounds -16 and 17.
In the return-point memory model, an excursion that returns to a point already visited is closed and the extrema between them are erased. The trace alternates drives; at the end the active drive is rising.
What is the output value? Answer with the single integer value the active rising drive emanates from (the rising branch's endpoint under saturation).

Answer:
17

---


# Level 0

## Example 1

A laminated beam cross-section is built from rectangular regions, each with its own bending stiffness E (units are consistent so only relative values matter). Bending is about the horizontal x-axis, so within any region the flexural stress is sigma(y) = E * (y - y0), linear in the vertical coordinate y, with y0 the neutral axis height where stress is zero. Region 0: a rectangle centred at x=5.0, y=8.0 with half-width 3.0 and half-height 3.0; it is a material patch with stiffness E = 6.6. Region 1: a rectangle centred at x=0.0, y=1.0 with half-width 2.0 and half-height 5.0; it is a material patch with stiffness E = 9.6. Region 2: a rectangle centred at x=0.0, y=7.0 with half-width 5.0 and half-height 3.0; it is a material patch with stiffness E = 6.1. Compute the stiffness-weighted neutral axis location y0 of the whole section. Give a single integer, rounding any non-integer result to the nearest whole number.

Answer: 5

## Example 2

A laminated beam cross-section is built from rectangular regions, each with its own bending stiffness E (units are consistent so only relative values matter). Bending is about the horizontal x-axis, so within any region the flexural stress is sigma(y) = E * (y - y0), linear in the vertical coordinate y, with y0 the neutral axis height where stress is zero. Region 0: a rectangle centred at x=-6.0, y=-7.0 with half-width 3.0 and half-height 1.0; it is a material patch with stiffness E = 9.3. Region 1: a rectangle centred at x=-1.0, y=4.0 with half-width 2.0 and half-height 2.0; it is a material patch with stiffness E = 4.3. Region 2: a rectangle centred at x=1.0, y=-6.0 with half-width 1.0 and half-height 2.0; it is a material patch with stiffness E = 7.2. Compute the effective bending stiffness EI = integral of E (y - y0)^2 dA of the whole section, weighted by stiffness. Give a single integer, rounding any non-integer result to the nearest whole number.

Answer: 5803

# Level 2

## Example 1

A laminated beam cross-section is built from rectangular regions, each with its own bending stiffness E (units are consistent so only relative values matter). Bending is about the horizontal x-axis, so within any region the flexural stress is sigma(y) = E * (y - y0), linear in the vertical coordinate y, with y0 the neutral axis height where stress is zero. Region 0: a rectangle centred at x=3.0, y=-1.0 with half-width 5.0 and half-height 1.0; it is a material patch with stiffness E = 9.6. Region 1: a rectangle centred at x=-5.0, y=6.0 with half-width 3.0 and half-height 6.0; it is a material patch with stiffness E = 11.6. Region 2: a rectangle centred at x=-5.0, y=-3.0 with half-width 3.0 and half-height 4.0, rotated by 60 degrees; it is a rotated stiff insert with stiffness E = 9.4. Region 3: a rectangle centred at x=0.0, y=6.0 with half-width 4.0 and half-height 1.0; it is a material patch with stiffness E = 9.5. Compute the ratio of flexural stress at height y=6 in region 3 to flexural stress at height y=-1 in region 0: sigma(yA) / sigma(yB). Give a single integer, rounding any non-integer result to the nearest whole number.

Answer: -1

## Example 2

A laminated beam cross-section is built from rectangular regions, each with its own bending stiffness E (units are consistent so only relative values matter). Bending is about the horizontal x-axis, so within any region the flexural stress is sigma(y) = E * (y - y0), linear in the vertical coordinate y, with y0 the neutral axis height where stress is zero. Region 0: a rectangle centred at x=-2.0, y=-4.0 with half-width 3.0 and half-height 6.0; it is a material patch with stiffness E = 4.7. Region 1: a rectangle centred at x=4.0, y=2.0 with half-width 3.0 and half-height 6.0; it is a material patch with stiffness E = 6.0. Region 2: a rectangle centred at x=4.0, y=5.0 with half-width 2.0 and half-height 2.0; it is a material patch with stiffness E = 8.1. Region 3: a rectangle centred at x=-3.0, y=-7.0 with half-width 6.0 and half-height 6.0, rotated by 30 degrees; it is a rotated stiff insert with stiffness E = 10.2. Compute the effective bending stiffness EI = integral of E (y - y0)^2 dA of the whole section, weighted by stiffness. Give a single integer, rounding any non-integer result to the nearest whole number.

Answer: 66248

# Level 5

## Example 1

A laminated beam cross-section is built from rectangular regions, each with its own bending stiffness E (units are consistent so only relative values matter). Bending is about the horizontal x-axis, so within any region the flexural stress is sigma(y) = E * (y - y0), linear in the vertical coordinate y, with y0 the neutral axis height where stress is zero. Region 0: a rectangle centred at x=-2.0, y=8.0 with half-width 5.0 and half-height 1.0; it is a material patch with stiffness E = 4.6. Region 1: a rectangle centred at x=1.0, y=0.0 with half-width 2.0 and half-height 3.0, rotated by -60 degrees; it is a rotated stiff insert with stiffness E = 14.2. Region 2: a rectangle centred at x=-7.0, y=-2.0 with half-width 6.0 and half-height 3.0; it is a hole with stiffness E = 0.9. Region 3: a rectangle centred at x=1.0, y=-1.0 with half-width 1.0 and half-height 5.0; it is a material patch with stiffness E = 5.7. Region 4: a rectangle centred at x=-5.0, y=-5.0 with half-width 1.0 and half-height 1.0, rotated by 30 degrees; it is a rotated stiff insert with stiffness E = 11.6. Compute the effective bending stiffness EI = integral of E (y - y0)^2 dA of the whole section, weighted by stiffness. Give a single integer, rounding any non-integer result to the nearest whole number.

Answer: 9100

## Example 2

A laminated beam cross-section is built from rectangular regions, each with its own bending stiffness E (units are consistent so only relative values matter). Bending is about the horizontal x-axis, so within any region the flexural stress is sigma(y) = E * (y - y0), linear in the vertical coordinate y, with y0 the neutral axis height where stress is zero. Region 0: a rectangle centred at x=-8.0, y=-7.0 with half-width 5.0 and half-height 3.0; it is a material patch with stiffness E = 5.5. Region 1: a rectangle centred at x=-4.0, y=-7.0 with half-width 3.0 and half-height 6.0, rotated by -30 degrees; it is a rotated stiff insert with stiffness E = 11.7. Region 2: a rectangle centred at x=8.0, y=-7.0 with half-width 1.0 and half-height 6.0; it is a material patch with stiffness E = 10.5. Region 3: a rectangle centred at x=-2.0, y=-5.0 with half-width 1.0 and half-height 1.0, rotated by 45 degrees; it is a rotated stiff insert with stiffness E = 14.8. Region 4: a rectangle centred at x=-6.0, y=-4.0 with half-width 5.0 and half-height 3.0; it is a hole with stiffness E = 0.4. Compute the effective bending stiffness EI = integral of E (y - y0)^2 dA of the whole section, weighted by stiffness. Give a single integer, rounding any non-integer result to the nearest whole number.

Answer: 12767


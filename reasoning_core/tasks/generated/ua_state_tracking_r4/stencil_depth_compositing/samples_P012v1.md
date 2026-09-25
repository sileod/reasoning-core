# Stencil/depth compositing samples

Each example simulates a fragment compositing pipeline (stencil test, depth test, masked writes, integer blending) and asks for the final color/depth/stencil of a compact list of queried pixels.

## Level 0

### Example

Simulate a graphics compositing pipeline over an 5x5 framebuffer of pixels. Each pixel carries a color (r,g,b,a channels, each 0-255), a depth (integer 0-1023), and a stencil value (integer 0-255). The buffer starts cleared to a single color, depth, and stencil.

A sequence of fragments is then applied in order. A fragment covers a rectangular region of pixels, coordinates inclusive. For each pixel the fragment covers, it applies in this order:
1. Stencil test: compare (pixel_stencil & mask) with (ref & mask) using its comparison. If the test fails, apply the stencil-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
2. Depth test: compare the fragment depth with the pixel's current depth using its comparison. If the test fails, apply the stencil depth-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
3. If depth write is on, set the pixel depth to the fragment depth.
4. Apply the stencil pass operation to the pixel stencil.
5. Color: either overwrite the pixel color with the fragment color, or blend it. Blending computes, per channel, result = clamp(fragment_channel * src_factor + pixel_channel * dst_factor) to 0-255, where SRC_COLOR means the fragment's same channel, DST_COLOR the pixel's same channel, ONE_MINUS_* uses 255 minus that value, and ZERO/ONE are constants 0/1. Then apply the color write mask: only masked channels are replaced, others keep their previous value.

Comparisons (stencil and depth): NEVER (never passes), LESS, LEQUAL, GREATER, GEQUAL, EQUAL, NOTEQUAL, ALWAYS.
Stencil operations: KEEP, ZERO (set to 0), REPLACE (set to ref), INCR (add 1, saturating at 255), DECR (subtract 1, saturating at 0), INCR_WRAP (add 1, wrapping 255 to 0), DECR_WRAP (subtract 1, wrapping 0 to 255), INVERT (255 minus value).

Only the queried pixels below are scored.

Clear:
color=[32, 81, 186, 111] depth=888 stencil=246

Fragments in order:
F0: rect (0,4)-(2,4); stencil GREATER ref=163 mask=0 [fail=KEEP depthfail=REPLACE pass=INCR]; depth 417 LESS write; color (34,150,34,153) RGB overwrite
F1: rect (0,0)-(4,1); stencil LESS ref=229 mask=3 [fail=DECR_WRAP depthfail=INCR pass=INCR_WRAP]; depth 434 EQUAL no-write; color (54,217,183,21) color_mask=1101 overwrite

Queried pixels (x,y):
(1,1) (4,1)

For each queried pixel in the order listed above, give its final color channels, depth, and stencil as r,g,b,a,d,s with no spaces, and join the pixels with a semicolon and no spaces. Example for two pixels: 10,20,30,255,512,7;40,50,60,255,0,3

Answer:

**Answer:**

32,81,186,111,888,245;32,81,186,111,888,245


### Example

Simulate a graphics compositing pipeline over an 5x5 framebuffer of pixels. Each pixel carries a color (r,g,b,a channels, each 0-255), a depth (integer 0-1023), and a stencil value (integer 0-255). The buffer starts cleared to a single color, depth, and stencil.

A sequence of fragments is then applied in order. A fragment covers a rectangular region of pixels, coordinates inclusive. For each pixel the fragment covers, it applies in this order:
1. Stencil test: compare (pixel_stencil & mask) with (ref & mask) using its comparison. If the test fails, apply the stencil-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
2. Depth test: compare the fragment depth with the pixel's current depth using its comparison. If the test fails, apply the stencil depth-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
3. If depth write is on, set the pixel depth to the fragment depth.
4. Apply the stencil pass operation to the pixel stencil.
5. Color: either overwrite the pixel color with the fragment color, or blend it. Blending computes, per channel, result = clamp(fragment_channel * src_factor + pixel_channel * dst_factor) to 0-255, where SRC_COLOR means the fragment's same channel, DST_COLOR the pixel's same channel, ONE_MINUS_* uses 255 minus that value, and ZERO/ONE are constants 0/1. Then apply the color write mask: only masked channels are replaced, others keep their previous value.

Comparisons (stencil and depth): NEVER (never passes), LESS, LEQUAL, GREATER, GEQUAL, EQUAL, NOTEQUAL, ALWAYS.
Stencil operations: KEEP, ZERO (set to 0), REPLACE (set to ref), INCR (add 1, saturating at 255), DECR (subtract 1, saturating at 0), INCR_WRAP (add 1, wrapping 255 to 0), DECR_WRAP (subtract 1, wrapping 0 to 255), INVERT (255 minus value).

Only the queried pixels below are scored.

Clear:
color=[255, 96, 185, 45] depth=1013 stencil=168

Fragments in order:
F0: rect (0,3)-(4,3); stencil GREATER ref=242 mask=31 [fail=INCR depthfail=REPLACE pass=INVERT]; depth 425 ALWAYS write; color (31,24,66,171) color_mask=1001 overwrite
F1: rect (1,1)-(1,2); stencil ALWAYS ref=246 mask=3 [fail=DECR depthfail=INCR pass=ZERO]; depth 882 GREATER write; color (17,205,96,156) color_mask=0110 overwrite

Queried pixels (x,y):
(4,3) (0,3)

For each queried pixel in the order listed above, give its final color channels, depth, and stencil as r,g,b,a,d,s with no spaces, and join the pixels with a semicolon and no spaces. Example for two pixels: 10,20,30,255,512,7;40,50,60,255,0,3

Answer:

**Answer:**

255,96,185,45,1013,169;255,96,185,45,1013,169


## Level 2

### Example

Simulate a graphics compositing pipeline over an 7x7 framebuffer of pixels. Each pixel carries a color (r,g,b,a channels, each 0-255), a depth (integer 0-1023), and a stencil value (integer 0-255). The buffer starts cleared to a single color, depth, and stencil.

A sequence of fragments is then applied in order. A fragment covers a rectangular region of pixels, coordinates inclusive. For each pixel the fragment covers, it applies in this order:
1. Stencil test: compare (pixel_stencil & mask) with (ref & mask) using its comparison. If the test fails, apply the stencil-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
2. Depth test: compare the fragment depth with the pixel's current depth using its comparison. If the test fails, apply the stencil depth-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
3. If depth write is on, set the pixel depth to the fragment depth.
4. Apply the stencil pass operation to the pixel stencil.
5. Color: either overwrite the pixel color with the fragment color, or blend it. Blending computes, per channel, result = clamp(fragment_channel * src_factor + pixel_channel * dst_factor) to 0-255, where SRC_COLOR means the fragment's same channel, DST_COLOR the pixel's same channel, ONE_MINUS_* uses 255 minus that value, and ZERO/ONE are constants 0/1. Then apply the color write mask: only masked channels are replaced, others keep their previous value.

Comparisons (stencil and depth): NEVER (never passes), LESS, LEQUAL, GREATER, GEQUAL, EQUAL, NOTEQUAL, ALWAYS.
Stencil operations: KEEP, ZERO (set to 0), REPLACE (set to ref), INCR (add 1, saturating at 255), DECR (subtract 1, saturating at 0), INCR_WRAP (add 1, wrapping 255 to 0), DECR_WRAP (subtract 1, wrapping 0 to 255), INVERT (255 minus value).

Only the queried pixels below are scored.

Clear:
color=[250, 67, 152, 173] depth=924 stencil=112

Fragments in order:
F0: rect (4,4)-(6,4); stencil EQUAL ref=81 mask=1 [fail=INCR_WRAP depthfail=REPLACE pass=DECR_WRAP]; depth 995 NOTEQUAL write; color (20,108,76,42) color_mask=1100 blend src=ONE dst=ONE
F1: rect (1,4)-(4,6); stencil LEQUAL ref=209 mask=15 [fail=DECR depthfail=DECR_WRAP pass=DECR_WRAP]; depth 203 LEQUAL write; color (128,49,95,23) color_mask=1100 blend src=ONE_MINUS_SRC_COLOR dst=ONE
F2: rect (1,3)-(5,5); stencil ALWAYS ref=45 mask=3 [fail=KEEP depthfail=ZERO pass=INCR]; depth 67 EQUAL write; color (137,100,202,252) color_mask=1110 overwrite
F3: rect (1,4)-(2,4); stencil EQUAL ref=84 mask=3 [fail=INCR depthfail=INCR pass=REPLACE]; depth 144 GREATER write; color (148,90,60,221) RGB overwrite

Queried pixels (x,y):
(0,0) (2,4) (5,3)

For each queried pixel in the order listed above, give its final color channels, depth, and stencil as r,g,b,a,d,s with no spaces, and join the pixels with a semicolon and no spaces. Example for two pixels: 10,20,30,255,512,7;40,50,60,255,0,3

Answer:

**Answer:**

250,67,152,173,924,112;255,255,152,173,203,1;250,67,152,173,924,0


### Example

Simulate a graphics compositing pipeline over an 7x7 framebuffer of pixels. Each pixel carries a color (r,g,b,a channels, each 0-255), a depth (integer 0-1023), and a stencil value (integer 0-255). The buffer starts cleared to a single color, depth, and stencil.

A sequence of fragments is then applied in order. A fragment covers a rectangular region of pixels, coordinates inclusive. For each pixel the fragment covers, it applies in this order:
1. Stencil test: compare (pixel_stencil & mask) with (ref & mask) using its comparison. If the test fails, apply the stencil-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
2. Depth test: compare the fragment depth with the pixel's current depth using its comparison. If the test fails, apply the stencil depth-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
3. If depth write is on, set the pixel depth to the fragment depth.
4. Apply the stencil pass operation to the pixel stencil.
5. Color: either overwrite the pixel color with the fragment color, or blend it. Blending computes, per channel, result = clamp(fragment_channel * src_factor + pixel_channel * dst_factor) to 0-255, where SRC_COLOR means the fragment's same channel, DST_COLOR the pixel's same channel, ONE_MINUS_* uses 255 minus that value, and ZERO/ONE are constants 0/1. Then apply the color write mask: only masked channels are replaced, others keep their previous value.

Comparisons (stencil and depth): NEVER (never passes), LESS, LEQUAL, GREATER, GEQUAL, EQUAL, NOTEQUAL, ALWAYS.
Stencil operations: KEEP, ZERO (set to 0), REPLACE (set to ref), INCR (add 1, saturating at 255), DECR (subtract 1, saturating at 0), INCR_WRAP (add 1, wrapping 255 to 0), DECR_WRAP (subtract 1, wrapping 0 to 255), INVERT (255 minus value).

Only the queried pixels below are scored.

Clear:
color=[65, 90, 145, 225] depth=933 stencil=243

Fragments in order:
F0: rect (4,0)-(5,1); stencil NOTEQUAL ref=200 mask=127 [fail=ZERO depthfail=ZERO pass=REPLACE]; depth 390 EQUAL write; color (244,50,28,65) color_mask=1001 overwrite
F1: rect (6,1)-(6,2); stencil NEVER ref=191 mask=1 [fail=INCR_WRAP depthfail=INCR_WRAP pass=DECR]; depth 559 NOTEQUAL write; color (213,39,93,144) color_mask=1100 overwrite
F2: rect (2,6)-(3,6); stencil EQUAL ref=48 mask=127 [fail=DECR depthfail=INCR pass=DECR_WRAP]; depth 529 LEQUAL write; color (244,55,235,28) color_mask=1101 blend src=ZERO dst=ONE_MINUS_SRC_COLOR
F3: rect (4,6)-(5,6); stencil NOTEQUAL ref=242 mask=31 [fail=KEEP depthfail=INCR_WRAP pass=KEEP]; depth 950 LEQUAL write; color (137,131,25,196) color_mask=0111 overwrite

Queried pixels (x,y):
(2,2) (1,0) (4,1)

For each queried pixel in the order listed above, give its final color channels, depth, and stencil as r,g,b,a,d,s with no spaces, and join the pixels with a semicolon and no spaces. Example for two pixels: 10,20,30,255,512,7;40,50,60,255,0,3

Answer:

**Answer:**

65,90,145,225,933,243;65,90,145,225,933,243;65,90,145,225,933,0


## Level 5

### Example

Simulate a graphics compositing pipeline over an 10x10 framebuffer of pixels. Each pixel carries a color (r,g,b,a channels, each 0-255), a depth (integer 0-1023), and a stencil value (integer 0-255). The buffer starts cleared to a single color, depth, and stencil.

A sequence of fragments is then applied in order. A fragment covers a rectangular region of pixels, coordinates inclusive. For each pixel the fragment covers, it applies in this order:
1. Stencil test: compare (pixel_stencil & mask) with (ref & mask) using its comparison. If the test fails, apply the stencil-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
2. Depth test: compare the fragment depth with the pixel's current depth using its comparison. If the test fails, apply the stencil depth-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
3. If depth write is on, set the pixel depth to the fragment depth.
4. Apply the stencil pass operation to the pixel stencil.
5. Color: either overwrite the pixel color with the fragment color, or blend it. Blending computes, per channel, result = clamp(fragment_channel * src_factor + pixel_channel * dst_factor) to 0-255, where SRC_COLOR means the fragment's same channel, DST_COLOR the pixel's same channel, ONE_MINUS_* uses 255 minus that value, and ZERO/ONE are constants 0/1. Then apply the color write mask: only masked channels are replaced, others keep their previous value.

Comparisons (stencil and depth): NEVER (never passes), LESS, LEQUAL, GREATER, GEQUAL, EQUAL, NOTEQUAL, ALWAYS.
Stencil operations: KEEP, ZERO (set to 0), REPLACE (set to ref), INCR (add 1, saturating at 255), DECR (subtract 1, saturating at 0), INCR_WRAP (add 1, wrapping 255 to 0), DECR_WRAP (subtract 1, wrapping 0 to 255), INVERT (255 minus value).

Only the queried pixels below are scored.

Clear:
color=[87, 16, 185, 116] depth=823 stencil=24

Fragments in order:
F0: rect (1,6)-(8,9); stencil NEVER ref=141 mask=15 [fail=INVERT depthfail=DECR pass=ZERO]; depth 1009 NOTEQUAL write; color (150,68,53,96) RGB overwrite
F1: rect (0,6)-(4,9); stencil ALWAYS ref=91 mask=31 [fail=REPLACE depthfail=DECR pass=DECR]; depth 592 EQUAL write; color (177,151,10,190) color_mask=1110 blend src=ONE_MINUS_SRC_COLOR dst=ONE
F2: rect (8,4)-(8,7); stencil NOTEQUAL ref=103 mask=15 [fail=DECR_WRAP depthfail=INVERT pass=DECR]; depth 338 LEQUAL write; color (208,133,154,112) color_mask=0011 overwrite
F3: rect (3,6)-(7,6); stencil LEQUAL ref=147 mask=0 [fail=INVERT depthfail=KEEP pass=REPLACE]; depth 31 EQUAL write; color (48,169,129,158) color_mask=0100 blend src=ZERO dst=ONE
F4: rect (2,3)-(5,9); stencil GEQUAL ref=9 mask=3 [fail=INVERT depthfail=KEEP pass=ZERO]; depth 722 LEQUAL write; color (165,253,236,124) color_mask=1001 overwrite
F5: rect (4,3)-(6,7); stencil LEQUAL ref=241 mask=127 [fail=KEEP depthfail=KEEP pass=KEEP]; depth 396 LEQUAL no-write; color (161,54,242,186) color_mask=1101 blend src=DST_COLOR dst=ZERO
F6: rect (3,2)-(3,9); stencil GREATER ref=68 mask=15 [fail=INVERT depthfail=INCR pass=REPLACE]; depth 188 NOTEQUAL write; color (6,0,195,246) RGB overwrite

Queried pixels (x,y):
(2,4) (3,0) (2,6) (8,7)

For each queried pixel in the order listed above, give its final color channels, depth, and stencil as r,g,b,a,d,s with no spaces, and join the pixels with a semicolon and no spaces. Example for two pixels: 10,20,30,255,512,7;40,50,60,255,0,3

Answer:

**Answer:**

87,16,185,116,823,231;87,16,185,116,823,24;165,16,185,124,722,0;87,16,185,116,823,230


### Example

Simulate a graphics compositing pipeline over an 10x10 framebuffer of pixels. Each pixel carries a color (r,g,b,a channels, each 0-255), a depth (integer 0-1023), and a stencil value (integer 0-255). The buffer starts cleared to a single color, depth, and stencil.

A sequence of fragments is then applied in order. A fragment covers a rectangular region of pixels, coordinates inclusive. For each pixel the fragment covers, it applies in this order:
1. Stencil test: compare (pixel_stencil & mask) with (ref & mask) using its comparison. If the test fails, apply the stencil-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
2. Depth test: compare the fragment depth with the pixel's current depth using its comparison. If the test fails, apply the stencil depth-fail operation to the pixel stencil and the fragment has no further effect on the pixel.
3. If depth write is on, set the pixel depth to the fragment depth.
4. Apply the stencil pass operation to the pixel stencil.
5. Color: either overwrite the pixel color with the fragment color, or blend it. Blending computes, per channel, result = clamp(fragment_channel * src_factor + pixel_channel * dst_factor) to 0-255, where SRC_COLOR means the fragment's same channel, DST_COLOR the pixel's same channel, ONE_MINUS_* uses 255 minus that value, and ZERO/ONE are constants 0/1. Then apply the color write mask: only masked channels are replaced, others keep their previous value.

Comparisons (stencil and depth): NEVER (never passes), LESS, LEQUAL, GREATER, GEQUAL, EQUAL, NOTEQUAL, ALWAYS.
Stencil operations: KEEP, ZERO (set to 0), REPLACE (set to ref), INCR (add 1, saturating at 255), DECR (subtract 1, saturating at 0), INCR_WRAP (add 1, wrapping 255 to 0), DECR_WRAP (subtract 1, wrapping 0 to 255), INVERT (255 minus value).

Only the queried pixels below are scored.

Clear:
color=[73, 225, 111, 87] depth=311 stencil=54

Fragments in order:
F0: rect (9,9)-(9,9); stencil ALWAYS ref=224 mask=1 [fail=KEEP depthfail=INVERT pass=DECR_WRAP]; depth 756 NOTEQUAL write; color (217,2,35,9) color_mask=1010 overwrite
F1: rect (4,8)-(9,8); stencil LEQUAL ref=245 mask=127 [fail=KEEP depthfail=DECR pass=ZERO]; depth 483 GREATER no-write; color (218,157,182,249) color_mask=1110 blend src=DST_COLOR dst=ONE_MINUS_DST_COLOR
F2: rect (2,5)-(8,6); stencil NOTEQUAL ref=164 mask=15 [fail=INCR_WRAP depthfail=DECR pass=INCR_WRAP]; depth 403 NOTEQUAL write; color (100,229,37,182) color_mask=1100 blend src=SRC_COLOR dst=ONE_MINUS_SRC_COLOR
F3: rect (8,0)-(9,9); stencil NEVER ref=150 mask=255 [fail=INCR_WRAP depthfail=REPLACE pass=INCR_WRAP]; depth 524 LESS write; color (88,30,212,155) color_mask=1010 blend src=ONE_MINUS_SRC_COLOR dst=ONE
F4: rect (3,4)-(7,7); stencil ALWAYS ref=17 mask=0 [fail=REPLACE depthfail=DECR_WRAP pass=INVERT]; depth 651 GREATER write; color (72,132,5,165) RGB overwrite
F5: rect (0,8)-(7,9); stencil LESS ref=72 mask=7 [fail=DECR_WRAP depthfail=INCR_WRAP pass=INCR]; depth 16 GEQUAL write; color (236,178,23,51) color_mask=0100 blend src=SRC_COLOR dst=ONE_MINUS_DST_COLOR
F6: rect (3,4)-(8,8); stencil ALWAYS ref=238 mask=255 [fail=DECR depthfail=DECR_WRAP pass=ZERO]; depth 604 GEQUAL write; color (94,98,4,85) RGB blend src=ONE_MINUS_SRC_COLOR dst=ONE_MINUS_SRC_COLOR

Queried pixels (x,y):
(4,8) (7,8) (8,0) (4,7)

For each queried pixel in the order listed above, give its final color channels, depth, and stencil as r,g,b,a,d,s with no spaces, and join the pixels with a semicolon and no spaces. Example for two pixels: 10,20,30,255,512,7;40,50,60,255,0,3

Answer:

**Answer:**

255,255,255,255,604,0;255,255,255,255,604,0;73,225,111,87,311,55;72,132,5,165,651,200


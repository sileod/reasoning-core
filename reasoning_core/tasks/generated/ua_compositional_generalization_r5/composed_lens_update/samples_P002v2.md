# samples_P002v2 — composed lens update v2

## Level 0

### Example 1

**Prompt:**

A source record has fields udnsj=4, ljw=9, liz=3. A composed lens runs these steps in order on the currently reachable view: "rename ljw to zqw; keep liz; keep liz". A rename relabels one reachable element to a new name; a pair merges two reachable elements into one tuple (both source fields stay referenced); keep leaves an element unchanged; select keeps the first element and drops the second, hiding its source fields unless referenced elsewhere. Then push an identity update backward through the lens. If a rename would give an element a name that another reachable element already holds, or if running the steps hides every source field, the lens rejects the update: answer exactly the word rejected. Otherwise the revised source keeps every field still referenced, drops hidden fields, and lists them as semicolon-separated name=value pairs in the original source order. The final reachable elements are: liz, udnsj, zqw.

**Answer:**

udnsj=4; ljw=9; liz=3

### Example 2

**Prompt:**

A source record has fields bgj=1, nxq=1, ixkyp=5. A composed lens runs these steps in order on the currently reachable view: "keep ixkyp; select ixkyp and drop bgj; keep ixkyp". A rename relabels one reachable element to a new name; a pair merges two reachable elements into one tuple (both source fields stay referenced); keep leaves an element unchanged; select keeps the first element and drops the second, hiding its source fields unless referenced elsewhere. Then push an identity update backward through the lens. If a rename would give an element a name that another reachable element already holds, or if running the steps hides every source field, the lens rejects the update: answer exactly the word rejected. Otherwise the revised source keeps every field still referenced, drops hidden fields, and lists them as semicolon-separated name=value pairs in the original source order. The final reachable elements are: ixkyp, nxq.

**Answer:**

nxq=1; ixkyp=5


## Level 2

### Example 1

**Prompt:**

A source record has fields hgdh=7, dasod=2, apqq=1, buj=6, ljo=9. A composed lens runs these steps in order on the currently reachable view: "rename dasod to ucdl; rename hgdh to lgiex; rename apqq to epxyk; pair lgiex and ljo into a tuple; rename ucdl to lxquh". A rename relabels one reachable element to a new name; a pair merges two reachable elements into one tuple (both source fields stay referenced); keep leaves an element unchanged; select keeps the first element and drops the second, hiding its source fields unless referenced elsewhere. Then push an identity update backward through the lens. If a rename would give an element a name that another reachable element already holds, or if running the steps hides every source field, the lens rejects the update: answer exactly the word rejected. Otherwise the revised source keeps every field still referenced, drops hidden fields, and lists them as semicolon-separated name=value pairs in the original source order. The final reachable elements are: (lgiex,ljo), buj, epxyk, lxquh.

**Answer:**

hgdh=7; dasod=2; apqq=1; buj=6; ljo=9

### Example 2

**Prompt:**

A source record has fields dpqh=3, siwtt=8, efb=6, xcgcr=3, aqu=8. A composed lens runs these steps in order on the currently reachable view: "pair xcgcr and aqu into a tuple; rename (xcgcr,aqu) to azg; keep siwtt; select siwtt and drop azg; rename siwtt to audrk". A rename relabels one reachable element to a new name; a pair merges two reachable elements into one tuple (both source fields stay referenced); keep leaves an element unchanged; select keeps the first element and drops the second, hiding its source fields unless referenced elsewhere. Then push an identity update backward through the lens. If a rename would give an element a name that another reachable element already holds, or if running the steps hides every source field, the lens rejects the update: answer exactly the word rejected. Otherwise the revised source keeps every field still referenced, drops hidden fields, and lists them as semicolon-separated name=value pairs in the original source order. The final reachable elements are: audrk, dpqh, efb.

**Answer:**

dpqh=3; siwtt=8; efb=6


## Level 5

### Example 1

**Prompt:**

A source record has fields wyx=8, jad=6, ypm=7, mshde=8, kause=6, ukmhz=8, jftkx=8, fjdf=7. A composed lens runs these steps in order on the currently reachable view: "select kause and drop jftkx; rename mshde to erjyh; select kause and drop fjdf; keep kause; select wyx and drop ukmhz; select wyx and drop erjyh; keep kause; keep ypm". A rename relabels one reachable element to a new name; a pair merges two reachable elements into one tuple (both source fields stay referenced); keep leaves an element unchanged; select keeps the first element and drops the second, hiding its source fields unless referenced elsewhere. Then push an identity update backward through the lens. If a rename would give an element a name that another reachable element already holds, or if running the steps hides every source field, the lens rejects the update: answer exactly the word rejected. Otherwise the revised source keeps every field still referenced, drops hidden fields, and lists them as semicolon-separated name=value pairs in the original source order. The final reachable elements are: jad, kause, wyx, ypm.

**Answer:**

wyx=8; jad=6; ypm=7; kause=6

### Example 2

**Prompt:**

A source record has fields cfl=6, hpq=4, egk=9, ycbe=3, ruwf=8, yuy=2, inor=7, vib=2. A composed lens runs these steps in order on the currently reachable view: "pair ruwf and egk into a tuple; select inor and drop yuy; rename vib to bav; select ycbe and drop bav; select cfl and drop hpq; rename (ruwf,egk) to ulvi; select ulvi and drop cfl; rename ulvi to reyoi". A rename relabels one reachable element to a new name; a pair merges two reachable elements into one tuple (both source fields stay referenced); keep leaves an element unchanged; select keeps the first element and drops the second, hiding its source fields unless referenced elsewhere. Then push an identity update backward through the lens. If a rename would give an element a name that another reachable element already holds, or if running the steps hides every source field, the lens rejects the update: answer exactly the word rejected. Otherwise the revised source keeps every field still referenced, drops hidden fields, and lists them as semicolon-separated name=value pairs in the original source order. The final reachable elements are: inor, reyoi, ycbe.

**Answer:**

egk=9; ycbe=3; ruwf=8; inor=7


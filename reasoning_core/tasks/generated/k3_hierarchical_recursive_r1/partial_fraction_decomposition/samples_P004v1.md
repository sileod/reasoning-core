# Level 0
## Example 1
**Prompt:**
Express the proper rational function (9x^3 - 5 + 9x - 4x^2)/((x+3)*(x+1)*x^2-5x+16) as a sum of partial fractions, where a term (x-r)^k contributes C_k/(x-r)^k and a term (x^2+bx+c)^k contributes (A_k x + B_k)/(x^2+bx+c)^k. The irreducible factors and their ordered coefficient slots are:
  1. (x+3) with multiplicity 1: C_1/(x+3)
  2. (x+1) with multiplicity 1: C_1/(x+1)
  3. (x^2-5x+16) with multiplicity 1: sum over k of (A_k x + B_k)/(x^2-5x+16)^k

In this order, the coefficient slots are: C_1/(x+3); C_1/(x+1); A_1 (coefficient of 1/x^2-5x+16); B_1 (coefficient of x/x^2-5x+16).
Give the exact rational value of each coefficient, in the same order, comma-separated (a fraction as n/d or an integer), one value per slot.

**Answer:**
311/80,-27/44,-692/55,5039/880

## Example 2
**Prompt:**
Express the proper rational function (- 10x^3 - 10 - 2x - x^2)/((x-10)*(x+2)*x^2-2x+15) as a sum of partial fractions, where a term (x-r)^k contributes C_k/(x-r)^k and a term (x^2+bx+c)^k contributes (A_k x + B_k)/(x^2+bx+c)^k. The irreducible factors and their ordered coefficient slots are:
  1. (x-10) with multiplicity 1: C_1/(x-10)
  2. (x+2) with multiplicity 1: C_1/(x+2)
  3. (x^2-2x+15) with multiplicity 1: sum over k of (A_k x + B_k)/(x^2-2x+15)^k

In this order, the coefficient slots are: C_1/(x-10); C_1/(x+2); A_1 (coefficient of 1/x^2-2x+15); B_1 (coefficient of x/x^2-2x+15).
Give the exact rational value of each coefficient, in the same order, comma-separated (a fraction as n/d or an integer), one value per slot.

**Answer:**
-1013/114,-35/138,-4775/437,-376/437

# Level 2
## Example 1
**Prompt:**
Express the proper rational function (- 10x^14 + 26 + 19x + 22x^2 - 13x^3 + 12x^4 - 21x^5 - 11x^6 - 21x^7 - 11x^8 - 4x^9 - 13x^10 + 9x^11 - 8x^12 + 4x^13)/((x+13)^2*(x+10)*(x-19)^2*(x+7)^2*(x^2+33)^2*(x^2-10x+32)^2) as a sum of partial fractions, where a term (x-r)^k contributes C_k/(x-r)^k and a term (x^2+bx+c)^k contributes (A_k x + B_k)/(x^2+bx+c)^k. The irreducible factors and their ordered coefficient slots are:
  1. (x+13) with multiplicity 2: C_1/(x+13) + ... + C_2/(x+13)^2
  2. (x+10) with multiplicity 1: C_1/(x+10)
  3. (x-19) with multiplicity 2: C_1/(x-19) + ... + C_2/(x-19)^2
  4. (x+7) with multiplicity 2: C_1/(x+7) + ... + C_2/(x+7)^2
  5. (x^2+33) with multiplicity 2: sum over k of (A_k x + B_k)/(x^2+33)^k
  6. (x^2-10x+32) with multiplicity 2: sum over k of (A_k x + B_k)/(x^2-10x+32)^k

In this order, the coefficient slots are: C_1/(x+13); C_2/(x+13)^2; C_1/(x+10); C_1/(x-19); C_2/(x-19)^2; C_1/(x+7); C_2/(x+7)^2; A_1 (coefficient of 1/x^2+33); B_1 (coefficient of x/x^2+33); A_2 (coefficient of 1/(x^2+33)^2); B_2 (coefficient of x/(x^2+33)^2); A_1 (coefficient of 1/x^2-10x+32); B_1 (coefficient of x/x^2-10x+32); A_2 (coefficient of 1/(x^2-10x+32)^2); B_2 (coefficient of x/(x^2-10x+32)^2).
Give the exact rational value of each coefficient, in the same order, comma-separated (a fraction as n/d or an integer), one value per slot.

**Answer:**
4263840505483568828941/396682505690974912512,20394767925263329/247202263425024,-37465246384463/2316339616752,-442870706526183442157787/76300385698146141995008,-559899587983780039/9172783311118336,3380014738969088291/2702573175368035008,-1825467699395/2798285740848,-84080416538205635803994026793965/789543690971337186720585611345456,-30453368260413298761784540756981/789543690971337186720585611345456,836624158498390016497/1102243508856633339608,287467913290656359229/1102243508856633339608,90050677685108517160424642789131/622586155698488055423916184594116,44313277311679510357440570675681/2490344622793952221695664738376464,-6292516081194274299245/4647217132092155220803,1811743171492145544363/9294434264184310441606

## Example 2
**Prompt:**
Express the proper rational function (3x^9 + 22 - 17x - 5x^2 + 19x^3 + 9x^4 + 19x^5 - 16x^6 + 24x^7 - 6x^8)/((x+4)*(x-16)^2*(x-22)^2*(x+14)*x^2+11x+40*x^2+5x+40) as a sum of partial fractions, where a term (x-r)^k contributes C_k/(x-r)^k and a term (x^2+bx+c)^k contributes (A_k x + B_k)/(x^2+bx+c)^k. The irreducible factors and their ordered coefficient slots are:
  1. (x+4) with multiplicity 1: C_1/(x+4)
  2. (x-16) with multiplicity 2: C_1/(x-16) + ... + C_2/(x-16)^2
  3. (x-22) with multiplicity 2: C_1/(x-22) + ... + C_2/(x-22)^2
  4. (x+14) with multiplicity 1: C_1/(x+14)
  5. (x^2+11x+40) with multiplicity 1: sum over k of (A_k x + B_k)/(x^2+11x+40)^k
  6. (x^2+5x+40) with multiplicity 1: sum over k of (A_k x + B_k)/(x^2+5x+40)^k

In this order, the coefficient slots are: C_1/(x+4); C_1/(x-16); C_2/(x-16)^2; C_1/(x-22); C_2/(x-22)^2; C_1/(x+14); A_1 (coefficient of 1/x^2+11x+40); B_1 (coefficient of x/x^2+11x+40); A_1 (coefficient of 1/x^2+5x+40); B_1 (coefficient of x/x^2+5x+40).
Give the exact rational value of each coefficient, in the same order, comma-separated (a fraction as n/d or an integer), one value per slot.

**Answer:**
-828379/584064000,649384950919763/21260009779200,93291615491/1916697600,-1626148429203595009/58113935043139872,837675787465/4091065056,9187274641/19846296000,-4380559585752521/15435399734968320,-412130538966131/15435399734968320,-539217201328841/8150345817145344,96482465774351/40751729085726720

# Level 5
## Example 1
**Prompt:**
Express the proper rational function (- 3x^15 + 17 - 8x^2 + 12x^3 - 16x^4 - 29x^5 - 14x^6 - 28x^7 - 14x^8 - 25x^9 - 7x^10 - 19x^11 + 4x^12 - 3x^13 - 19x^14)/((x+3)^3*(x-1)^2*(x-22)^3*(x-17)^2*(x^2-10x+52)^2*x^2-3x+48) as a sum of partial fractions, where a term (x-r)^k contributes C_k/(x-r)^k and a term (x^2+bx+c)^k contributes (A_k x + B_k)/(x^2+bx+c)^k. The irreducible factors and their ordered coefficient slots are:
  1. (x+3) with multiplicity 3: C_1/(x+3) + ... + C_3/(x+3)^3
  2. (x-1) with multiplicity 2: C_1/(x-1) + ... + C_2/(x-1)^2
  3. (x-22) with multiplicity 3: C_1/(x-22) + ... + C_3/(x-22)^3
  4. (x-17) with multiplicity 2: C_1/(x-17) + ... + C_2/(x-17)^2
  5. (x^2-10x+52) with multiplicity 2: sum over k of (A_k x + B_k)/(x^2-10x+52)^k
  6. (x^2-3x+48) with multiplicity 1: sum over k of (A_k x + B_k)/(x^2-3x+48)^k

In this order, the coefficient slots are: C_1/(x+3); C_2/(x+3)^2; C_3/(x+3)^3; C_1/(x-1); C_2/(x-1)^2; C_1/(x-22); C_2/(x-22)^2; C_3/(x-22)^3; C_1/(x-17); C_2/(x-17)^2; A_1 (coefficient of 1/x^2-10x+52); B_1 (coefficient of x/x^2-10x+52); A_2 (coefficient of 1/(x^2-10x+52)^2); B_2 (coefficient of x/(x^2-10x+52)^2); A_1 (coefficient of 1/x^2-3x+48); B_1 (coefficient of x/x^2-3x+48).
Give the exact rational value of each coefficient, in the same order, comma-separated (a fraction as n/d or an integer), one value per slot.

**Answer:**
19633518749139947/6417652014210937500000,-3052685221463/1367731365000000000,9377971/13663650000000,1188659/11168038719000576,19/1613179072512,-1105254563756538275781574647497597/249529607119376528273437500000,2527243661947309836902657473/154928393464831875000000,-529663137393251246159/8016018412500000,48273774983687799369193/10906593572160000000,1476812432065299113/267613632000000,223453550758234042167877973953063/142034950574863112905285222294128,3582561063970891519846095949463195/14771634859785763742149663118589312,-139937069253840694369435/4705719831595074159504,232664009071536031754413/122348715621471928147104,20934188781353635193503/188448044876298572247168,333066719445839465351/565344134628895716741504

## Example 2
**Prompt:**
Express the proper rational function (- 13x^12 + 7 - 14x + 16x^2 - 26x^3 + 13x^4 - 7x^5 - 20x^6 + 7x^7 - 3x^8 - 28x^9 + 13x^10 - 10x^11)/((x-10)^2*(x+13)*(x+33)*(x+16)*(x^2+5x+25)^2*(x^2+16)^2) as a sum of partial fractions, where a term (x-r)^k contributes C_k/(x-r)^k and a term (x^2+bx+c)^k contributes (A_k x + B_k)/(x^2+bx+c)^k. The irreducible factors and their ordered coefficient slots are:
  1. (x-10) with multiplicity 2: C_1/(x-10) + ... + C_2/(x-10)^2
  2. (x+13) with multiplicity 1: C_1/(x+13)
  3. (x+33) with multiplicity 1: C_1/(x+33)
  4. (x+16) with multiplicity 1: C_1/(x+16)
  5. (x^2+5x+25) with multiplicity 2: sum over k of (A_k x + B_k)/(x^2+5x+25)^k
  6. (x^2+16) with multiplicity 2: sum over k of (A_k x + B_k)/(x^2+16)^k

In this order, the coefficient slots are: C_1/(x-10); C_2/(x-10)^2; C_1/(x+13); C_1/(x+33); C_1/(x+16); A_1 (coefficient of 1/x^2+5x+25); B_1 (coefficient of x/x^2+5x+25); A_2 (coefficient of 1/(x^2+5x+25)^2); B_2 (coefficient of x/(x^2+5x+25)^2); A_1 (coefficient of 1/x^2+16); B_1 (coefficient of x/x^2+16); A_2 (coefficient of 1/(x^2+16)^2); B_2 (coefficient of x/(x^2+16)^2).
Give the exact rational value of each coefficient, in the same order, comma-separated (a fraction as n/d or an integer), one value per slot.

**Answer:**
-33250714025228813117/55313022801228920000,-13898250594533/10596482260000,-56573479242601/3615428652300,-4231187424794768353/138261990441095300,3467050131476249/103049714985984,-1131239467646908842793702/3165649717428080561713125,2168614285076475921257453/9496949152284241685139375,7332173927012443/2324646746815575,-164641906562387/154976449787705,-48987391492969980269/277357121812818049600,-93991841663909666307/4437713949005088793600,288411636284/731016775957,4703791876573/46785073661248

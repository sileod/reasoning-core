# Samples: weight_sensitive_stress_parse (P006v2)

## Level 0

### Example 1

Prompt:

A linguist is testing this artificial prosodic grammar on the segment string suufuefiersuruemi.
Use these rules, not any natural language's conventions. Sonority increases as t=k=s=f < m=n < l=r < i=u < e=o < a. Only a,e,i,o,u are vowels.
Scan each vowel run left to right: consume two vowels as one diphthong nucleus if the first has strictly higher sonority than the second; otherwise consume one vowel as a nucleus. Repeat on unconsumed vowels. A nucleus never exceeds two vowels.
Use the maximal-onset algorithm: between successive nuclei, give the next syllable the longest consonant suffix with strictly rising sonority (a single consonant qualifies); the rest is the preceding syllable's coda. Empty runs give empty onsets. Initial consonants belong to the first onset; final consonants to the last coda.
A syllable is heavy exactly when it has a diphthong or a nonempty coda; otherwise light. Build feet greedily from the right edge: a heavy syllable is a singleton; pair a light syllable with the next unconsumed syllable in the scan only if that syllable is also light; otherwise make the light syllable a singleton. Consume and repeat. Stress the right syllable of every pair and every singleton. Left/right always refers to written order. Index syllables from one, left to right.
Return the stressed syllable index in the foot closest to the right edge. Use one integer, e.g. 7, with no explanation.

Answer: 10

### Example 2

Prompt:

A linguist is testing this artificial prosodic grammar on the segment string kutisteirkafu.
Use these rules, not any natural language's conventions. Sonority increases as t=k=s=f < m=n < l=r < i=u < e=o < a. Only a,e,i,o,u are vowels.
Scan each vowel run left to right: consume two vowels as one diphthong nucleus if the first has strictly higher sonority than the second; otherwise consume one vowel as a nucleus. Repeat on unconsumed vowels. A nucleus never exceeds two vowels.
Use the maximal-onset algorithm: between successive nuclei, give the next syllable the longest consonant suffix with strictly rising sonority (a single consonant qualifies); the rest is the preceding syllable's coda. Empty runs give empty onsets. Initial consonants belong to the first onset; final consonants to the last coda.
A syllable is heavy exactly when it has a diphthong or a nonempty coda; otherwise light. Build feet greedily from the right edge: a heavy syllable is a singleton; pair a light syllable with the next unconsumed syllable in the scan only if that syllable is also light; otherwise make the light syllable a singleton. Consume and repeat. Stress the right syllable of every pair and every singleton. Left/right always refers to written order. Index syllables from one, left to right.
Return the stressed syllable index in the foot closest to the left edge. Use one integer, e.g. 7, with no explanation.

Answer: 1

## Level 2

### Example 1

Prompt:

A linguist is testing this artificial prosodic grammar on the segment string fulioruitutoektaekiis.
Use these rules, not any natural language's conventions. Sonority increases as t=k=s=f < m=n < l=r < i=u < e=o < a. Only a,e,i,o,u are vowels.
Scan each vowel run left to right: consume two vowels as one diphthong nucleus if the first has strictly higher sonority than the second; otherwise consume one vowel as a nucleus. Repeat on unconsumed vowels. A nucleus never exceeds two vowels.
Use the maximal-onset algorithm: between successive nuclei, give the next syllable the longest consonant suffix with strictly rising sonority (a single consonant qualifies); the rest is the preceding syllable's coda. Empty runs give empty onsets. Initial consonants belong to the first onset; final consonants to the last coda.
A syllable is heavy exactly when it has a diphthong or a nonempty coda; otherwise light. Build feet greedily from the left edge: a heavy syllable is a singleton; pair a light syllable with the next unconsumed syllable in the scan only if that syllable is also light; otherwise make the light syllable a singleton. Consume and repeat. Stress the right syllable of every pair and every singleton. Left/right always refers to written order. Index syllables from one, left to right.
A clash is two adjacent stressed syllables, even across feet. Return the index of the LEFT member of the leftmost clash, or none if absent. Format examples: 7 or none. No explanation.

Answer: 6

### Example 2

Prompt:

A linguist is testing this artificial prosodic grammar on the segment string soamineomaislrurkat.
Use these rules, not any natural language's conventions. Sonority increases as t=k=s=f < m=n < l=r < i=u < e=o < a. Only a,e,i,o,u are vowels.
Scan each vowel run left to right: consume two vowels as one diphthong nucleus if the first has strictly higher sonority than the second; otherwise consume one vowel as a nucleus. Repeat on unconsumed vowels. A nucleus never exceeds two vowels.
Use the maximal-onset algorithm: between successive nuclei, give the next syllable the longest consonant suffix with strictly rising sonority (a single consonant qualifies); the rest is the preceding syllable's coda. Empty runs give empty onsets. Initial consonants belong to the first onset; final consonants to the last coda.
A syllable is heavy exactly when it has a diphthong or a nonempty coda; otherwise light. Build feet greedily from the left edge: a heavy syllable is a singleton; pair a light syllable with the next unconsumed syllable in the scan only if that syllable is also light; otherwise make the light syllable a singleton. Consume and repeat. Stress the right syllable of every pair and every singleton. Left/right always refers to written order. Index syllables from one, left to right.
A clash is two adjacent stressed syllables, even across feet. Return the index of the LEFT member of the leftmost clash, or none if absent. Format examples: 7 or none. No explanation.

Answer: 4

## Level 5

### Example 1

Prompt:

A linguist is testing this artificial prosodic grammar on the segment string looaruluoelamiuutalalimtinsssuueftmnuiet.
Use these rules, not any natural language's conventions. Sonority increases as t=k=s=f < m=n < l=r < i=u < e=o < a. Only a,e,i,o,u are vowels.
Scan each vowel run left to right: consume two vowels as one diphthong nucleus if the first has strictly higher sonority than the second; otherwise consume one vowel as a nucleus. Repeat on unconsumed vowels. A nucleus never exceeds two vowels.
Use the maximal-onset algorithm: between successive nuclei, give the next syllable the longest consonant suffix with strictly rising sonority (a single consonant qualifies); the rest is the preceding syllable's coda. Empty runs give empty onsets. Initial consonants belong to the first onset; final consonants to the last coda.
A syllable is heavy exactly when it has a diphthong or a nonempty coda; otherwise light. Build feet greedily from the left edge: a heavy syllable is a singleton; pair a light syllable with the next unconsumed syllable in the scan only if that syllable is also light; otherwise make the light syllable a singleton. Consume and repeat. Stress the left syllable of every pair and every singleton. Left/right always refers to written order. Index syllables from one, left to right.
Return the full footed parse in written order: join syllables within feet with '.', feet with '-', and prefix each stressed syllable with an apostrophe. Format example: 'ka.mi-'tu (a left-headed pair followed by a singleton). Copy all segments exactly; no spaces or explanation.

Answer: 'lo.o-'a.ru-'lu.o-'e.la-'mi.u-'u.ta-'la-'lim-'tinss-'su.u-'eftm-'nu.i-'et

### Example 2

Prompt:

A linguist is testing this artificial prosodic grammar on the segment string litlrrokunesnskuearkmtauiftsmoaartntiftouiftntaiimum.
Use these rules, not any natural language's conventions. Sonority increases as t=k=s=f < m=n < l=r < i=u < e=o < a. Only a,e,i,o,u are vowels.
Scan each vowel run left to right: consume two vowels as one diphthong nucleus if the first has strictly higher sonority than the second; otherwise consume one vowel as a nucleus. Repeat on unconsumed vowels. A nucleus never exceeds two vowels.
Use the maximal-onset algorithm: between successive nuclei, give the next syllable the longest consonant suffix with strictly rising sonority (a single consonant qualifies); the rest is the preceding syllable's coda. Empty runs give empty onsets. Initial consonants belong to the first onset; final consonants to the last coda.
A syllable is heavy exactly when it has a diphthong or a nonempty coda; otherwise light. Build feet greedily from the left edge: a heavy syllable is a singleton; pair a light syllable with the next unconsumed syllable in the scan only if that syllable is also light; otherwise make the light syllable a singleton. Consume and repeat. Stress the right syllable of every pair and every singleton. Left/right always refers to written order. Index syllables from one, left to right.
Return the full footed parse in written order: join syllables within feet with '.', feet with '-', and prefix each stressed syllable with an apostrophe. Format example: 'ka.mi-'tu (a left-headed pair followed by a singleton). Copy all segments exactly; no spaces or explanation.

Answer: 'litlr-ro.'ku-'nesns-ku.'e-'arkm-'tau-'ift-smo.'a-'artn-'tif-'tou-'iftn-'tai-'i-'mum

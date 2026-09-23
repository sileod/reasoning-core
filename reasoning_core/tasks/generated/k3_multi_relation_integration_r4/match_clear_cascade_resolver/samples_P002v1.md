# Samples for match_clear_cascade_resolution (P002v1)

## Level 0

### Example 1

Prompt:

A match-3 board has 5 rows and 4 columns; each tile is a single uppercase letter and rows shown below are separated by '/'. First, the tiles at position (row 4, col 2) and (row 3, col 2), counting from 0, are swapped. Then repeat: clear every cell that belongs to a run of three or more identical tiles in a row or a column, all at once; let the remaining tiles fall straight down within their columns to fill gaps; and refill the empty cells at the tops of columns, left to right, each column top to bottom, one tile at a time from the front of the refill stream below, using tiles only as needed. Stop when no run of three or more remains anywhere. Initial board: FFAF / BEEC / DDCF / EFAA / BABA. Refill stream: EEFEABBCFABBECEEEAEFACEDABFACEBDDAECEDFBACFAAFBAABFADCBBECBDAFDDAAFDDFBFCFDCDDAB. State the final board after everything stabilizes as a single string with the first row then the second and so on, uppercase letters for tiles and '.' for an empty cell.

Answer:

FEEFBFAFDEECEDCFBFBA

### Example 2

Prompt:

A match-3 board has 5 rows and 4 columns; each tile is a single uppercase letter and rows shown below are separated by '/'. First, the tiles at position (row 1, col 2) and (row 1, col 3), counting from 0, are swapped. Then repeat: clear every cell that belongs to a run of three or more identical tiles in a row or a column, all at once; let the remaining tiles fall straight down within their columns to fill gaps; and refill the empty cells at the tops of columns, left to right, each column top to bottom, one tile at a time from the front of the refill stream below, using tiles only as needed. Stop when no run of three or more remains anywhere. Initial board: EABA / CABE / FFEA / EFED / FBCB. Refill stream: CBCCBFFAABEECDACCFCDDDBBBEDBDFEDBEFBEDBAAEEEECCBBBABBDADADCAEEBCCAAFCFDBADFEFFCF. State the final board after everything stabilizes as a single string with the first row then the second and so on, uppercase letters for tiles and '.' for an empty cell.

Answer:

EACACABBFFCAEFBDFBCB


## Level 2

### Example 1

Prompt:

A match-3 board has 7 rows and 6 columns; each tile is a single uppercase letter and rows shown below are separated by '/'. First, the tiles at position (row 5, col 0) and (row 6, col 0), counting from 0, are swapped. Then repeat: clear every cell that belongs to a run of three or more identical tiles in a row or a column, all at once; let the remaining tiles fall straight down within their columns to fill gaps; and refill the empty cells at the tops of columns, left to right, each column top to bottom, one tile at a time from the front of the refill stream below, using tiles only as needed. Stop when no run of three or more remains anywhere. Initial board: BADBDB / EADEBA / AEACBC / ADBAEC / BAEDBA / DCCACA / EDDAEC. Refill stream: BBDBACBBCAEEEDCCBCCDCEACADBACDEDEBEACCADDAEEDACDECBAEBCCCECDEEDCDBBCBBCDABEAEACADCDDCAEDCBCABEECBBEAEBCABACDAADBABACABAEECBBCDCBCCCDABAEEBEEEEBBABCABAEABCCDBEDDACEEEACB. State the final board after everything stabilizes as a single string with the first row then the second and so on, uppercase letters for tiles and '.' for an empty cell.

Answer:

BBCADBBAAEBAEACCBCAEAAECADBDBABAEACAECCAEC

### Example 2

Prompt:

A match-3 board has 7 rows and 6 columns; each tile is a single uppercase letter and rows shown below are separated by '/'. First, the tiles at position (row 2, col 4) and (row 3, col 4), counting from 0, are swapped. Then repeat: clear every cell that belongs to a run of three or more identical tiles in a row or a column, all at once; let the remaining tiles fall straight down within their columns to fill gaps; and refill the empty cells at the tops of columns, left to right, each column top to bottom, one tile at a time from the front of the refill stream below, using tiles only as needed. Stop when no run of three or more remains anywhere. Initial board: DCDCEC / CBDDEB / BDADAB / EDBCEE / AADBAB / EECAEE / CBCDDA. Refill stream: BDCCDDADACDEDBACABAEBCAEBADDCBEBCCDAABCABEACBBBAABBDACADEABCDECECABDADAADBEABBCECEBACAADAEDCBDEACBBBDEBADBCDDDACDEBBBDEBBABBDCACDCEACBABBAECBEACDCAEDCDEEAEBDBCCCEECCEBA. State the final board after everything stabilizes as a single string with the first row then the second and so on, uppercase letters for tiles and '.' for an empty cell.

Answer:

DCCDDCCBDCBBBDADCBEDBCAEAADBABEECAEECBCDDA


## Level 5

### Example 1

Prompt:

A match-3 board has 10 rows and 9 columns; each tile is a single uppercase letter and rows shown below are separated by '/'. First, the tiles at position (row 7, col 3) and (row 7, col 4), counting from 0, are swapped. Then repeat: clear every cell that belongs to a run of three or more identical tiles in a row or a column, all at once; let the remaining tiles fall straight down within their columns to fill gaps; and refill the empty cells at the tops of columns, left to right, each column top to bottom, one tile at a time from the front of the refill stream below, using tiles only as needed. Stop when no run of three or more remains anywhere. Initial board: DCBADDBCD / ADCCDDBAA / CCBBAADBD / CCBABCDCA / BBCBCDABD / BCCDCCBBA / DDABADACC / ADACABCDD / DCCACDCDD / AADABBDAA. Refill stream: AACADCAACDCAADBDDDBABCCDDDAACBDCBAABADACCABCBDABBBBBCBBADADAABDDCACBCCCBDABDABDCBDABDADBACBCBDDDBCABBDDACDBAADACDADCBCBBDABDDBABCCADCBCCACACAADCBBBDDDBAAADBBCCACBDAAACBAABABCCDCCAAACABBDBBDBAADDCCABCBCDDBDCCCBCACBCDDAACABDAADCAADABAAACCCBBDACAADDBDBBDBBBCDDABDCCAACCAACCAACBABBADBACDDDCAADAABBDCDDBDADCDACAACADCCBDCCDDCBBDABABAAACCDCBDACAADBDCBCDDCBBCDCADCDCCC. State the final board after everything stabilizes as a single string with the first row then the second and so on, uppercase letters for tiles and '.' for an empty cell.

Answer:

DDACCAACDABDCABBAADCABBABBDADDBBADCACCBADCABDBCBBCDBBADDCADCACCADABDDCDDDCCBABCDDAADDBDDAA

### Example 2

Prompt:

A match-3 board has 10 rows and 9 columns; each tile is a single uppercase letter and rows shown below are separated by '/'. First, the tiles at position (row 1, col 1) and (row 2, col 1), counting from 0, are swapped. Then repeat: clear every cell that belongs to a run of three or more identical tiles in a row or a column, all at once; let the remaining tiles fall straight down within their columns to fill gaps; and refill the empty cells at the tops of columns, left to right, each column top to bottom, one tile at a time from the front of the refill stream below, using tiles only as needed. Stop when no run of three or more remains anywhere. Initial board: AADCDDAAC / DBCBCABAC / AACCDCBDA / DBDCDDADA / ABCDACDCC / DCDDABDAD / AABBDDBAA / CADDABCBD / CBCCDDAAC / ACDADDBDC. Refill stream: CBDDACADAAAADCBBABBCBDCADDCCABCDDCBBDABBDDCBCBDCDABCDBDBCDDCCAAACDCDCABBCCBCAADCACBBDDDACBDDBDBDADBABBACABBAADDCCDAAACABDABBBBADCACDAACBDCBCDCCCBCCADADAADDACDBADAADCACDCBCACDDDDABCBBDABCBCCADBCDBBBCCBDADCBBDDDAACCAABBADAABACCDCCABBDADACCCBDDCADBBAADBDAAAAADAADBAABBBBCBDDCACDBBDACDBCACACABDBCACDADAABBADADAABADBABBADDBCADCADCDCBADACCBBCADABDDCADBCABCACBDDDCACB. State the final board after everything stabilizes as a single string with the first row then the second and so on, uppercase letters for tiles and '.' for an empty cell.

Answer:

ACDCDDAACDBCBCABACADCCDCBDADADCDDADAAACDACDCCDCDDABDADAABBDDBAACADDABCBDCBCCDDAACACDADDBDC


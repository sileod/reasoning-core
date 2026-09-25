## Level 0
### Example 1
Prompt:
Each of the 3 sites takes an integer value from the set [1, 2]. The total energy is the sum of:
- a unary bias term per listed site, indexed by that site's value
  bias terms: b[0]=[5, -1]
- a pairwise table for each listed pair, indexed by the two sites' values
  pair tables: p(2,0)=[[-5, 3], [4, -2]], p(1,0)=[[2, 2], [-2, 3]]
Find the minimum possible total energy over all assignments that respect any pinned site. The answer is that minimum energy, a single integer. Write only the integer.
Answer:
-2

### Example 2
Prompt:
Each of the 3 sites takes an integer value from the set [1, 2]. The total energy is the sum of:
- a unary bias term per listed site, indexed by that site's value
  bias terms: b[2]=[2, -1]
- a pairwise table for each listed pair, indexed by the two sites' values
  pair tables: p(0,2)=[[3, 5], [-1, 1]], p(0,2)=[[-6, 5], [1, -6]]
Find the minimum possible total energy over all assignments that respect any pinned site. The answer is that minimum energy, a single integer. Write only the integer.
Answer:
-6

## Level 2
### Example 1
Prompt:
Each of the 4 sites takes an integer value from the set [1, 2, 3]. The total energy is the sum of:
- a unary bias term per listed site, indexed by that site's value
  bias terms: b[0]=[4, 6, 3], b[0]=[-3, 2, 0]
- a pairwise table for each listed pair, indexed by the two sites' values
  pair tables: p(0,3)=[[1, -5, 3], [-1, -6, 1], [-3, -5, -3]], p(0,3)=[[4, -3, -1], [3, 1, -2], [-6, 5, -6]], p(3,1)=[[-3, 6, 3], [-6, -1, -5], [4, 3, 0]], p(2,0)=[[6, -6, 0], [1, 3, 1], [-2, 4, 0]]
Find the minimum possible total energy over all assignments that respect any pinned site. The answer is that minimum energy, a single integer. Write only the integer.
Answer:
-15

### Example 2
Prompt:
Each of the 4 sites takes an integer value from the set [1, 2, 3]. The total energy is the sum of:
- a unary bias term per listed site, indexed by that site's value
  bias terms: b[3]=[-1, 5, -3], b[1]=[-4, 5, 6]
- a pairwise table for each listed pair, indexed by the two sites' values
  pair tables: p(2,1)=[[-6, -2, 0], [-2, -6, -5], [-1, 2, -4]], p(1,3)=[[6, -5, -4], [1, 3, 6], [6, -3, -5]], p(2,0)=[[5, -2, 4], [0, 4, 3], [6, 6, 5]], p(3,1)=[[5, -1, 5], [1, 5, 3], [-5, 0, -5]]
Find the minimum possible total energy over all assignments that respect any pinned site. The answer is that minimum energy, a single integer. Write only the integer.
Answer:
-24

## Level 5
### Example 1
Prompt:
Each of the 5 sites takes an integer value from the set [1, 2, 3, 4, 5]. The total energy is the sum of:
- a unary bias term per listed site, indexed by that site's value
  bias terms: b[0]=[4, 2, -5, -2, -1], b[2]=[2, 6, 0, 0, 3], b[2]=[4, 3, 2, 1, 4]
- a pairwise table for each listed pair, indexed by the two sites' values
  pair tables: p(0,3)=[[-3, -5, -1, -3, 0], [-2, -1, 4, -2, 5], [4, 3, 2, -4, 3], [0, -3, -2, 1, -3], [-6, -2, 5, 6, 0]], p(3,2)=[[-2, 0, -1, -3, 2], [1, -1, 4, -3, -4], [6, 0, -4, -4, 1], [1, -1, -2, 0, -1], [-2, -3, -2, -6, -2]], p(3,2)=[[-6, -6, -6, 1, 6], [5, 2, -2, 1, 2], [6, -5, 3, 1, -1], [0, -4, 5, -4, -2], [0, 6, -2, -3, 3]], p(1,0)=[[-5, 2, 4, -6, 3], [0, -4, -3, -3, 6], [3, 1, -6, 0, 6], [-2, 4, 1, -5, 3], [3, -1, -3, 0, -5]], p(3,2)=[[5, 5, 4, -6, -3], [4, 4, -6, -4, -6], [6, -2, 6, -1, -5], [-5, -5, 2, 5, 5], [-1, 5, 5, 4, -5]]
- a higher-order table for each listed triple, indexed by the three sites' values
  triple tables: h(0, 2, 4)={000: 0, 001: 5, 002: -4, 003: -8, 004: 8, 010: 5, 011: 3, 012: 0, 013: -6, 014: 2, 020: -1, 021: -8, 022: 7, 023: 4, 024: 1, 030: 5, 031: -1, 032: 5, 033: -7, 034: 5, 040: 8, 041: 7, 042: 2, 043: 0, 044: 6, 100: 7, 101: -2, 102: -6, 103: 8, 104: 2, 110: -3, 111: 3, 112: -3, 113: 2, 114: 2, 120: 8, 121: 8, 122: -2, 123: -5, 124: 0, 130: -4, 131: -6, 132: 7, 133: -3, 134: 5, 140: 0, 141: -4, 142: 8, 143: 8, 144: 2, 200: -7, 201: 8, 202: 0, 203: -6, 204: 8, 210: 6, 211: 7, 212: 7, 213: -4, 214: 6, 220: -4, 221: 5, 222: 1, 223: -5, 224: -1, 230: 8, 231: -1, 232: 3, 233: -4, 234: -1, 240: 5, 241: 8, 242: -7, 243: 3, 244: 0, 300: 3, 301: -6, 302: -8, 303: -8, 304: 6, 310: 7, 311: -6, 312: -4, 313: -2, 314: -7, 320: -6, 321: -6, 322: -6, 323: -5, 324: 7, 330: -6, 331: -6, 332: 5, 333: 7, 334: -6, 340: 1, 341: 2, 342: -1, 343: 1, 344: -3, 400: 7, 401: -5, 402: 2, 403: -7, 404: -3, 410: 2, 411: -8, 412: -5, 413: 2, 414: 7, 420: 1, 421: -6, 422: -1, 423: -3, 424: 8, 430: -4, 431: 4, 432: -4, 433: 0, 434: 0, 440: 4, 441: -5, 442: 8, 443: -1, 444: -1}
Site 2 is pinned to value 1 (it must equal that value).
Find the minimum possible total energy over all assignments that respect any pinned site. The answer is that minimum energy, a single integer. Write only the integer.
Answer:
-20

### Example 2
Prompt:
Each of the 5 sites takes an integer value from the set [1, 2, 3, 4, 5]. The total energy is the sum of:
- a unary bias term per listed site, indexed by that site's value
  bias terms: b[4]=[3, 1, 7, -4, 0], b[4]=[5, 1, -6, 3, 3], b[1]=[-1, 2, -2, 5, 5]
- a pairwise table for each listed pair, indexed by the two sites' values
  pair tables: p(2,3)=[[6, -6, -6, -1, -6], [2, -2, -2, -4, -6], [5, 0, -1, 4, 5], [1, -2, 5, -2, -2], [3, 6, -5, 1, -3]], p(2,1)=[[2, 2, 4, 6, 5], [0, -3, 1, 0, 6], [-6, 6, -4, -3, -5], [4, -4, -2, 3, 6], [5, -5, -4, 1, 0]], p(1,3)=[[3, -4, 2, -3, 4], [-4, -4, -5, -4, -6], [1, 4, -6, 3, -3], [3, 5, 1, -1, 1], [-6, 4, 1, -1, 5]], p(3,4)=[[-4, 6, -6, -4, -2], [0, 3, 2, 2, -3], [0, -3, 6, 2, -1], [3, -6, 6, 3, -5], [-4, -2, 0, -3, -1]], p(3,0)=[[3, -3, -2, -1, 1], [2, -1, -4, 1, -1], [1, -3, -2, -3, 2], [0, -1, -1, 2, -1], [-6, 3, -4, -3, 0]]
- a higher-order table for each listed triple, indexed by the three sites' values
  triple tables: h(1, 2, 4)={000: -6, 001: -2, 002: -1, 003: 3, 004: -8, 010: 3, 011: 1, 012: -2, 013: 1, 014: 7, 020: 7, 021: 4, 022: -7, 023: 1, 024: 2, 030: -4, 031: -5, 032: -4, 033: -1, 034: 7, 040: 0, 041: 5, 042: 4, 043: -2, 044: 8, 100: -3, 101: 5, 102: 8, 103: 2, 104: 8, 110: -4, 111: -3, 112: -7, 113: -2, 114: -6, 120: 5, 121: -5, 122: 8, 123: -1, 124: -4, 130: -6, 131: 8, 132: 1, 133: 1, 134: -1, 140: 8, 141: 2, 142: -4, 143: 5, 144: -7, 200: -3, 201: -3, 202: -8, 203: -8, 204: 0, 210: -1, 211: 7, 212: 3, 213: -8, 214: -2, 220: 0, 221: 7, 222: -1, 223: 5, 224: 1, 230: 8, 231: -8, 232: -3, 233: -2, 234: -2, 240: 2, 241: -7, 242: 6, 243: -8, 244: 5, 300: 3, 301: 3, 302: 3, 303: -3, 304: 4, 310: -7, 311: 0, 312: -6, 313: 0, 314: -4, 320: 6, 321: 5, 322: -1, 323: -4, 324: 2, 330: 3, 331: -4, 332: -7, 333: 4, 334: 4, 340: 8, 341: -4, 342: 5, 343: -2, 344: 0, 400: 2, 401: 1, 402: 3, 403: -3, 404: 1, 410: 5, 411: -5, 412: 5, 413: -6, 414: 4, 420: 4, 421: -2, 422: 6, 423: 6, 424: -5, 430: 0, 431: 6, 432: 5, 433: 2, 434: -3, 440: 8, 441: -4, 442: -1, 443: 2, 444: 2}
Site 4 is pinned to value 5 (it must equal that value).
Find the minimum possible total energy over all assignments that respect any pinned site. The answer is that minimum energy, a single integer. Write only the integer.
Answer:
-23


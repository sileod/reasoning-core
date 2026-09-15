## Level 0

Prompt:
```
The leaves of an unknown edge-weighted tree are labelled 0 through 3. Every internal node has degree 3, every edge has a positive length, and the distance between two leaves equals the sum of the lengths of the edges on the unique path between them. Below is the additive distance matrix: row i lists the distances from leaf i to leaves i+1 ... 3 (in order).
  0: 5 4 7
  1: 5 8
  2: 5
  3: 
Reconstruct the unique edge-weighted tree realizing this matrix (the additive phylogeny reconstruction). Emit every edge as 'parent-child:weight', with the tree rooted at leaf 0, edges sorted by parent then child, and each weight an irreducible fraction. The answer is 5 space-separated edges.
```

Answer: 0-4:2 4-1:3 4-5:1 5-2:1 5-3:4

Prompt:
```
The leaves of an unknown edge-weighted tree are labelled 0 through 3. Every internal node has degree 3, every edge has a positive length, and the distance between two leaves equals the sum of the lengths of the edges on the unique path between them. Below is the additive distance matrix: row i lists the distances from leaf i to leaves i+1 ... 3 (in order).
  0: 8 9 11
  1: 5 9
  2: 10
  3: 
Reconstruct the unique edge-weighted tree realizing this matrix (the additive phylogeny reconstruction). Emit every edge as 'parent-child:weight', with the tree rooted at leaf 0, edges sorted by parent then child, and each weight an irreducible fraction. The answer is 5 space-separated edges.
```

Answer: 0-5:5 4-1:2 4-2:3 5-3:6 5-4:1

## Level 2

Prompt:
```
The leaves of an unknown edge-weighted tree are labelled 0 through 7. Every internal node has degree 3, every edge has a positive length, and the distance between two leaves equals the sum of the lengths of the edges on the unique path between them. Below is the additive distance matrix: row i lists the distances from leaf i to leaves i+1 ... 7 (in order).
  0: 11 15 23 26 21 26 32
  1: 8 16 19 14 19 25
  2: 14 17 10 15 23
  3: 9 20 25 11
  4: 23 28 18
  5: 19 29
  6: 34
  7: 
Reconstruct the unique edge-weighted tree realizing this matrix (the additive phylogeny reconstruction). Emit every edge as 'parent-child:weight', with the tree rooted at leaf 0, edges sorted by parent then child, and each weight an irreducible fraction. The answer is 13 space-separated edges.
```

Answer: 0-8:9 8-1:2 8-9:3 9-10:8 9-11:1 10-4:6 10-13:2 11-2:2 11-12:1 12-5:7 12-6:12 13-3:1 13-7:10

Prompt:
```
The leaves of an unknown edge-weighted tree are labelled 0 through 7. Every internal node has degree 3, every edge has a positive length, and the distance between two leaves equals the sum of the lengths of the edges on the unique path between them. Below is the additive distance matrix: row i lists the distances from leaf i to leaves i+1 ... 7 (in order).
  0: 6 8 9 14 19 9 14
  1: 6 5 10 15 9 10
  2: 9 14 19 11 14
  3: 9 14 12 9
  4: 11 17 8
  5: 22 13
  6: 17
  7: 
Reconstruct the unique edge-weighted tree realizing this matrix (the additive phylogeny reconstruction). Emit every edge as 'parent-child:weight', with the tree rooted at leaf 0, edges sorted by parent then child, and each weight an irreducible fraction. The answer is 13 space-separated edges.
```

Answer: 0-12:3 8-2:4 8-9:1 9-1:1 9-10:2 10-3:2 10-13:3 11-4:3 11-5:8 12-6:6 12-8:1 13-7:4 13-11:1

## Level 5

Prompt:
```
The leaves of an unknown edge-weighted tree are labelled 0 through 13. Every internal node has degree 3, every edge has a positive length, and the distance between two leaves equals the sum of the lengths of the edges on the unique path between them. Below is the additive distance matrix: row i lists the distances from leaf i to leaves i+1 ... 13 (in order).
  0: 28 23 18 29 37 29 33 23 20 16 11 22 31
  1: 17 22 33 33 23 33 29 22 40 35 16 11
  2: 17 28 28 14 28 24 17 35 30 5 20
  3: 21 31 23 27 19 14 30 25 16 25
  4: 42 34 38 30 25 41 36 27 36
  5: 34 42 38 31 49 44 27 36
  6: 34 30 23 41 36 13 26
  7: 34 27 45 40 27 36
  8: 21 35 30 23 32
  9: 32 27 16 25
  10: 11 34 43
  11: 29 38
  12: 19
  13: 
Reconstruct the unique edge-weighted tree realizing this matrix (the additive phylogeny reconstruction). Emit every edge as 'parent-child:weight', with the tree rooted at leaf 0, edges sorted by parent then child, and each weight an irreducible fraction. The answer is 25 space-separated edges.
```

Answer: 0-22:2 14-18:2 14-25:7 15-16:1 15-21:1 16-3:5 16-4:16 17-5:21 17-14:1 18-6:10 18-24:1 19-7:19 19-17:2 20-8:12 20-15:1 21-9:7 21-19:1 22-20:9 22-23:6 23-10:8 23-11:3 24-2:3 24-12:2 25-1:4 25-13:7

Prompt:
```
The leaves of an unknown edge-weighted tree are labelled 0 through 13. Every internal node has degree 3, every edge has a positive length, and the distance between two leaves equals the sum of the lengths of the edges on the unique path between them. Below is the additive distance matrix: row i lists the distances from leaf i to leaves i+1 ... 13 (in order).
  0: 24 26 19 25 25 36 14 43 30 29 45 16 28
  1: 34 39 45 35 56 34 51 40 39 53 36 38
  2: 41 47 37 58 36 23 42 41 23 38 40
  3: 24 40 23 17 58 45 44 60 27 43
  4: 46 41 23 64 51 50 66 33 49
  5: 57 35 54 35 34 56 37 31
  6: 34 75 62 61 77 44 60
  7: 53 40 39 55 22 38
  8: 59 58 42 55 57
  9: 13 61 42 38
  10: 60 41 37
  11: 57 59
  12: 40
  13: 
Reconstruct the unique edge-weighted tree realizing this matrix (the additive phylogeny reconstruction). Emit every edge as 'parent-child:weight', with the tree rooted at leaf 0, edges sorted by parent then child, and each weight an irreducible fraction. The answer is 25 space-separated edges.
```

Answer: 0-15:2 14-1:16 14-20:15 15-17:5 15-24:2 16-4:15 16-18:6 17-14:1 17-21:3 18-3:3 18-6:20 19-7:6 19-16:2 20-8:20 20-23:1 21-22:13 21-25:1 22-9:7 22-10:6 23-2:2 23-11:21 24-12:12 24-19:4 25-5:14 25-13:17

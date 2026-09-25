## Level 0

### Prompt
```
Original buffer: ibbee
Edits (positions are 0-indexed within the buffer at that step):
  1. delete the range [3, 4)
  2. replace the range [4, 4) with 'w'
What is the provenance of the character currently at final position 2? Give its source buffer ('original' or 'added') and its offset within that buffer as one line in the form 'original:k' or 'added:k', where k is the 0-indexed character index inside the original buffer or the k-th appended character.
```

### Answer
```
original:2
```

### Prompt
```
Original buffer: dhcaj
Edits (positions are 0-indexed within the buffer at that step):
  1. delete the range [1, 4)
What is the provenance of the character currently at final position 1? Give its source buffer ('original' or 'added') and its offset within that buffer as one line in the form 'original:k' or 'added:k', where k is the 0-indexed character index inside the original buffer or the k-th appended character.
```

### Answer
```
original:4
```

## Level 2

### Prompt
```
Original buffer: hdcdigd
Edits (positions are 0-indexed within the buffer at that step):
  1. insert 'x' at position 0
  2. replace the range [6, 7) with 'vvw'
  3. replace the range [3, 4) with 'wvv'
What is the provenance of the character currently at final position 11? Give its source buffer ('original' or 'added') and its offset within that buffer as one line in the form 'original:k' or 'added:k', where k is the 0-indexed character index inside the original buffer or the k-th appended character.
```

### Answer
```
original:6
```

### Prompt
```
Original buffer: ihfbbhh
Edits (positions are 0-indexed within the buffer at that step):
  1. insert 'zyy' at position 7
  2. insert 'zy' at position 0
  3. replace the range [6, 9) with 'vw'
What is the provenance of the character currently at final position 3? Give its source buffer ('original' or 'added') and its offset within that buffer as one line in the form 'original:k' or 'added:k', where k is the 0-indexed character index inside the original buffer or the k-th appended character.
```

### Answer
```
original:1
```

## Level 5

### Prompt
```
Original buffer: caefagjefb
Edits (positions are 0-indexed within the buffer at that step):
  1. insert 'xz' at position 1
  2. replace the range [0, 2) with 'vvwvv'
  3. delete the range [14, 15)
  4. insert 'xyxy' at position 11
  5. insert 'xyxxy' at position 11
  6. replace the range [11, 14) with 'wwwvww'
What is the provenance of the character currently at final position 16? Give its source buffer ('original' or 'added') and its offset within that buffer as one line in the form 'original:k' or 'added:k', where k is the 0-indexed character index inside the original buffer or the k-th appended character.
```

### Answer
```
added:21
```

### Prompt
```
Original buffer: ghgageicif
Edits (positions are 0-indexed within the buffer at that step):
  1. replace the range [0, 3) with 'vvv'
  2. insert 'y' at position 9
  3. insert 'yx' at position 0
  4. replace the range [10, 11) with 'vww'
  5. insert 'xz' at position 7
  6. insert 'xzzzzyx' at position 7
What is the provenance of the character currently at final position 7? Give its source buffer ('original' or 'added') and its offset within that buffer as one line in the form 'original:k' or 'added:k', where k is the 0-indexed character index inside the original buffer or the k-th appended character.
```

### Answer
```
added:11
```

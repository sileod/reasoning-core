# Samples for P001v1 (ManacherPalindromeRadii)

## Level 0

### Example 1

Prompt:

```
Consider the string "abaabba" of length 7. Using Manacher's algorithm (mirror reuse against a moving right boundary), compute the palindrome radius around every center. There are 7 character centers and 6 gap centers, for 13 centers total. As the radius around a center report the full length of the longest palindrome centered there: for a character center this is an odd length, and for a gap center an even length. List, in order (character centers 0..6 first, then gaps), all 13 radii separated by single spaces. Example: for the string "aa" the character radii are 1 1 and the gap radius is 2, so the answer is "1 1 2". Give only the space-separated list.
```

Answer:

```
1 3 1 1 1 1 1 0 0 0 4 0 4
```

### Example 2

Prompt:

```
Consider the string "baababa" of length 7. Using Manacher's algorithm (mirror reuse against a moving right boundary), compute the palindrome radius around every center. There are 7 character centers and 6 gap centers, for 13 centers total. As the radius around a center report the full length of the longest palindrome centered there: for a character center this is an odd length, and for a gap center an even length. List, in order (character centers 0..6 first, then gaps), all 13 radii separated by single spaces. Example: for the string "aa" the character radii are 1 1 and the gap radius is 2, so the answer is "1 1 2". Give only the space-separated list.
```

Answer:

```
1 1 1 3 5 3 1 0 0 4 0 0 0
```

## Level 2

### Example 1

Prompt:

```
Consider the string "bbdddddaaab" of length 11. Using Manacher's algorithm (mirror reuse against a moving right boundary), compute the palindrome radius around every center. There are 11 character centers and 10 gap centers, for 21 centers total. As the radius around a center report the full length of the longest palindrome centered there: for a character center this is an odd length, and for a gap center an even length. List, in order (character centers 0..10 first, then gaps), all 21 radii separated by single spaces. Example: for the string "aa" the character radii are 1 1 and the gap radius is 2, so the answer is "1 1 2". Give only the space-separated list.
```

Answer:

```
1 1 1 3 5 3 1 1 3 1 1 0 2 0 2 4 4 2 0 2 2
```

### Example 2

Prompt:

```
Consider the string "ddbabcabdac" of length 11. Using Manacher's algorithm (mirror reuse against a moving right boundary), compute the palindrome radius around every center. There are 11 character centers and 10 gap centers, for 21 centers total. As the radius around a center report the full length of the longest palindrome centered there: for a character center this is an odd length, and for a gap center an even length. List, in order (character centers 0..10 first, then gaps), all 21 radii separated by single spaces. Example: for the string "aa" the character radii are 1 1 and the gap radius is 2, so the answer is "1 1 2". Give only the space-separated list.
```

Answer:

```
1 1 1 3 1 1 1 1 1 1 1 0 2 0 0 0 0 0 0 0 0
```

## Level 5

### Example 1

Prompt:

```
Consider the string "cbccffbbfgefaffbb" of length 17. Using Manacher's algorithm (mirror reuse against a moving right boundary), compute the palindrome radius around every center. There are 17 character centers and 16 gap centers, for 33 centers total. As the radius around a center report the full length of the longest palindrome centered there: for a character center this is an odd length, and for a gap center an even length. List, in order (character centers 0..16 first, then gaps), all 33 radii separated by single spaces. Example: for the string "aa" the character radii are 1 1 and the gap radius is 2, so the answer is "1 1 2". Give only the space-separated list.
```

Answer:

```
1 3 1 1 1 1 1 1 1 1 1 1 3 1 1 1 1 0 0 0 2 0 2 0 4 0 0 0 0 0 0 2 0
```

### Example 2

Prompt:

```
Consider the string "dedcfabeaagafeggb" of length 17. Using Manacher's algorithm (mirror reuse against a moving right boundary), compute the palindrome radius around every center. There are 17 character centers and 16 gap centers, for 33 centers total. As the radius around a center report the full length of the longest palindrome centered there: for a character center this is an odd length, and for a gap center an even length. List, in order (character centers 0..16 first, then gaps), all 33 radii separated by single spaces. Example: for the string "aa" the character radii are 1 1 and the gap radius is 2, so the answer is "1 1 2". Give only the space-separated list.
```

Answer:

```
1 3 1 1 1 1 1 1 1 1 3 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 2
```

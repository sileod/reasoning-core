# Samples P003v1

## Level 0

### Example 1

Prompt:

```
Translate the lambda term below from named-variable syntax into de Bruijn index form. Rules: a bound variable becomes the number of binders standing between it and the binder that captures it (the innermost binder gives 0, the next 1, and so on); a free variable becomes #k where k is its rank when all distinct free variables are sorted alphabetically (so the alphabetically first free variable is #0); an abstraction \x.M becomes \ followed by the conversion of M; an application (M N) stays (M N) with a single space. Give only the converted term.

Lambda term: \h. \h. (h k)

Example: \a. a b converts to \(0 #0).
Answer:
```

Answer:

```
\\(0 #0)
```

### Example 2

Prompt:

```
Translate the lambda term below from named-variable syntax into de Bruijn index form. Rules: a bound variable becomes the number of binders standing between it and the binder that captures it (the innermost binder gives 0, the next 1, and so on); a free variable becomes #k where k is its rank when all distinct free variables are sorted alphabetically (so the alphabetically first free variable is #0); an abstraction \x.M becomes \ followed by the conversion of M; an application (M N) stays (M N) with a single space. Give only the converted term.

Lambda term: (\g. \f. c (\k. k \j. g))

Example: \a. a b converts to \(0 #0).
Answer:
```

Answer:

```
(\\#0 (\0 \#1))
```

## Level 2

### Example 1

Prompt:

```
Translate the lambda term below from named-variable syntax into de Bruijn index form. Rules: a bound variable becomes the number of binders standing between it and the binder that captures it (the innermost binder gives 0, the next 1, and so on); a free variable becomes #k where k is its rank when all distinct free variables are sorted alphabetically (so the alphabetically first free variable is #0); an abstraction \x.M becomes \ followed by the conversion of M; an application (M N) stays (M N) with a single space. Give only the converted term.

Lambda term: (\a. \d. \b. d \g. \f. \c. f)

Example: \a. a b converts to \(0 #0).
Answer:
```

Answer:

```
(\\\1 \\\1)
```

### Example 2

Prompt:

```
Translate the lambda term below from named-variable syntax into de Bruijn index form. Rules: a bound variable becomes the number of binders standing between it and the binder that captures it (the innermost binder gives 0, the next 1, and so on); a free variable becomes #k where k is its rank when all distinct free variables are sorted alphabetically (so the alphabetically first free variable is #0); an abstraction \x.M becomes \ followed by the conversion of M; an application (M N) stays (M N) with a single space. Give only the converted term.

Lambda term: (((\b. b \i. i) \k. \h. a) (\h. \f. (a a) \h. \j. \i. h))

Example: \a. a b converts to \(0 #0).
Answer:
```

Answer:

```
(((\0 \0) \\#0) (\\(#0 #0) \\\2))
```

## Level 5

### Example 1

Prompt:

```
Translate the lambda term below from named-variable syntax into de Bruijn index form. Rules: a bound variable becomes the number of binders standing between it and the binder that captures it (the innermost binder gives 0, the next 1, and so on); a free variable becomes #k where k is its rank when all distinct free variables are sorted alphabetically (so the alphabetically first free variable is #0); an abstraction \x.M becomes \ followed by the conversion of M; an application (M N) stays (M N) with a single space. Give only the converted term.

Lambda term: ((((\f. (\f. f ((f f) \f. f)) \e. (((h f) f) \b. (b b))) \b. (\a. (j (g a)) (\b. b (\k. b b)))) (\c. \c. \c. (\b. b c) (\g. ((g \g. g) ((g g) g)) ((\e. \e. f \c. c) (\i. f (\h. h h)))))) \k. \f. (\k. (\f. (h j) (f \k. k)) \f. (((a f) (f a)) (j \k. j))))

Example: \a. a b converts to \(0 #0).
Answer:
```

Answer:

```
((((\(\0 ((0 0) \0)) \(((#3 #1) #1) \(0 0))) \(\(#4 (#2 0)) (\0 (\1 0)))) (\\\(\0 0) (\((0 \0) ((0 0) 0)) ((\\#1 \0) (\#1 (\0 #3)))))) \\(\(\(#3 #4) (1 \0)) \(((#0 0) (0 #0)) (#4 \#4))))
```

### Example 2

Prompt:

```
Translate the lambda term below from named-variable syntax into de Bruijn index form. Rules: a bound variable becomes the number of binders standing between it and the binder that captures it (the innermost binder gives 0, the next 1, and so on); a free variable becomes #k where k is its rank when all distinct free variables are sorted alphabetically (so the alphabetically first free variable is #0); an abstraction \x.M becomes \ followed by the conversion of M; an application (M N) stays (M N) with a single space. Give only the converted term.

Lambda term: ((\c. (((\c. c \c. e) (\c. b \c. (c c))) \c. \c. \c. d) ((\h. (\h. (f e) \h. \h. h) ((\j. h \e. e) (((c d) \h. d) (\i. b d)))) ((\h. \e. \e. k \b. (\b. b e)) \c. (\c. \c. b (c h))))) ((\d. ((\e. b \f. \d. d) ((d \k. d) \d. d)) ((\k. \d. d \g. \h. f) \d. ((\d. c d) \j. \c. j))) ((((((k b) k) ((h e) c)) ((\b. b \b. f) (d \a. a))) \k. \k. (e \k. c)) \k. \k. \k. \k. (k k))))

Example: \a. a b converts to \(0 #0).
Answer:
```

Answer:

```
((\(((\0 \#3) (\#0 \(0 0))) \\\#2) ((\(\(#4 #3) \\0) ((\#5 \0) (((#1 #2) \#2) (\#0 #2)))) ((\\\#6 \(\0 #3)) \(\\#0 (0 #5))))) ((\((\#0 \\0) ((0 \1) \0)) ((\\0 \\#4) \((\#1 0) \\1))) ((((((#6 #0) #6) ((#5 #3) #1)) ((\0 \#4) (#2 \0))) \\(#3 \#1)) \\\\(0 0))))
```

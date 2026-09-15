## Level 0

### Example

Prompt:

```

Let R = (a U ((a a) ((a b))*)) be a regular expression over the alphabet (a, b), where 1 denotes the empty string and 0 the empty set. Using Brzozowski derivatives, compute the (left) derivative of R with respect to the symbol 'a', then simplify the result with the identity laws. If the simplified derivative is nullable (accepts the empty string), answer exactly true; otherwise answer the fully simplified derivative expression, writing 1 for the empty string, 0 for the empty set, U for union, juxtaposition for concatenation, and * for star.
```

Answer:

```
true
```



### Example

Prompt:

```

Let R = b be a regular expression over the alphabet (a, b), where 1 denotes the empty string and 0 the empty set. Using Brzozowski derivatives, compute the (left) derivative of R with respect to the symbol 'b', then simplify the result with the identity laws. If the simplified derivative is nullable (accepts the empty string), answer exactly true; otherwise answer the fully simplified derivative expression, writing 1 for the empty string, 0 for the empty set, U for union, juxtaposition for concatenation, and * for star.
```

Answer:

```
true
```



## Level 2

### Example

Prompt:

```

Let R = a be a regular expression over the alphabet (a, b), where 1 denotes the empty string and 0 the empty set. Using Brzozowski derivatives, compute the (left) derivative of R with respect to the symbol 'a', then simplify the result with the identity laws. If the simplified derivative is nullable (accepts the empty string), answer exactly true; otherwise answer the fully simplified derivative expression, writing 1 for the empty string, 0 for the empty set, U for union, juxtaposition for concatenation, and * for star.
```

Answer:

```
true
```



### Example

Prompt:

```

Let R = ((((b U a) a*) (((a a) (b a)) ((a a) (a U b)))) (((b (b a)) (b U a)) ((b a) U b))) be a regular expression over the alphabet (a, b), where 1 denotes the empty string and 0 the empty set. Using Brzozowski derivatives, compute the (left) derivative of R with respect to the symbol 'a', then simplify the result with the identity laws. If the simplified derivative is nullable (accepts the empty string), answer exactly true; otherwise answer the fully simplified derivative expression, writing 1 for the empty string, 0 for the empty set, U for union, juxtaposition for concatenation, and * for star.
```

Answer:

```
((a* (((a a) (b a)) ((a a) (a U b)))) (((b (b a)) (b U a)) ((b a) U b)))
```



## Level 5

### Example

Prompt:

```

Let R = (((((b* (a a)))* ((a b) (b*)*)) U ((((b a) b))* (((b U a) (b b)) U ((b U a) (b a))))) (((b*)* (((b a) b) U ((a a) ((b a) U b)))) b)) be a regular expression over the alphabet (a, b), where 1 denotes the empty string and 0 the empty set. Using Brzozowski derivatives, compute the (left) derivative of R with respect to the symbol 'b', then simplify the result with the identity laws. If the simplified derivative is nullable (accepts the empty string), answer exactly true; otherwise answer the fully simplified derivative expression, writing 1 for the empty string, 0 for the empty set, U for union, juxtaposition for concatenation, and * for star.
```

Answer:

```
(((((b* (a a)) ((b* (a a)))*) ((a b) (b*)*)) U ((((a b) (((b a) b))*) (((b U a) (b b)) U ((b U a) (b a)))) U ((b b) U (b a)))) (((b*)* (((b a) b) U ((a a) ((b a) U b)))) b))
```



### Example

Prompt:

```

Let R = ((((((b b) b*) ((a* b))*) (((b a) (a a)) ((a b))*)))* ((((b (a b)) U (b a)) ((b a) a)) (a ((a ((b b) (b a))) U (a (a (b a))))))) be a regular expression over the alphabet (a, b), where 1 denotes the empty string and 0 the empty set. Using Brzozowski derivatives, compute the (left) derivative of R with respect to the symbol 'b', then simplify the result with the identity laws. If the simplified derivative is nullable (accepts the empty string), answer exactly true; otherwise answer the fully simplified derivative expression, writing 1 for the empty string, 0 for the empty set, U for union, juxtaposition for concatenation, and * for star.
```

Answer:

```
((((((b b*) ((a* b))*) (((b a) (a a)) ((a b))*)) (((((b b) b*) ((a* b))*) (((b a) (a a)) ((a b))*)))*) ((((b (a b)) U (b a)) ((b a) a)) (a ((a ((b b) (b a))) U (a (a (b a))))))) U ((((a b) U a) ((b a) a)) (a ((a ((b b) (b a))) U (a (a (b a)))))))
```



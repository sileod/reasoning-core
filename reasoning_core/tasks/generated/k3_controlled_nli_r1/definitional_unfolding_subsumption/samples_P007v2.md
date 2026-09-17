# Samples for P007v2

## Level 0

### Example 1

**Prompt:**

```
An ontology catalog needs the tightest shared description of two queries, using only the eligible defined names. Definitions are equivalences and acyclic. Primitive concepts are independent sets; roles are arbitrary binary relations, with no other axioms. X & Y is intersection; exists r.(X) means having at least one r-successor in X. Different restrictions may use different successors. TOP contains every individual.
Use definitional unfolding and the EL structural subsumption algorithm: S is subsumed by T when every root atom of T occurs in S and each restriction of T is matched by a same-role restriction of S whose filler is recursively subsumed by the filler of that restriction of T.
Vocabulary:
Primitive concepts: Blue, Bright, Light, Rigid, Round, Smooth. Roles: part, link, cover.

Definitions:
H0 := Rigid & exists link.(Light & Smooth)
H1 := Round & exists link.(H0)
Fern := Bright & H1
Laurel := exists link.(H1) & Fern
Oak := H1 & Laurel
Juniper := Blue & exists link.(H1)
Aster := Blue & Juniper
Reed := exists link.(H1)

Eligible Names:
Aster, Fern, Juniper, Laurel, Oak, Reed

Queries:
Q := Blue & exists link.(H1) & H1 & Blue & exists link.(exists link.(H0) & Round) & Bright & H1 & Bright
R := Blue & Blue & exists link.(H1) & Round & Blue & exists link.(H0) & Juniper & Bright
Find the least defined common subsumer: a conjunction of eligible names containing both Q and R in every model, and contained in every other such conjunction. Among equivalent conjunctions choose the fewest distinct names, then the lexicographically smallest sorted name list. Output only those case-sensitive names joined by ' & ', for example 'Aster & Cedar'; output TOP for the empty conjunction.
```

**Answer:**

```
Aster & Fern
```

### Example 2

**Prompt:**

```
An ontology catalog needs the tightest shared description of two queries, using only the eligible defined names. Definitions are equivalences and acyclic. Primitive concepts are independent sets; roles are arbitrary binary relations, with no other axioms. X & Y is intersection; exists r.(X) means having at least one r-successor in X. Different restrictions may use different successors. TOP contains every individual.
Use definitional unfolding and the EL structural subsumption algorithm: S is subsumed by T when every root atom of T occurs in S and each restriction of T is matched by a same-role restriction of S whose filler is recursively subsumed by the filler of that restriction of T.
Vocabulary:
Primitive concepts: Blue, Bright, Light, Rigid, Round, Smooth. Roles: part, link, cover.

Definitions:
H0 := Smooth & Light & exists link.(Bright & Rigid)
H1 := Blue & Bright & exists link.(H0)
Willow := Light
Birch := exists part.(H1)
Hazel := exists part.(H1) & H0
Fern := H0 & Birch
Reed := exists link.(H1)
Elm := exists link.(H1) & H1 & Reed

Eligible Names:
Birch, Elm, Fern, Hazel, Reed, Willow

Queries:
Q := Bright & exists link.(H0) & Blue & Light & Light & exists link.(H1) & Reed & exists link.(H1)
R := exists link.(H1) & Light & Light & Smooth
Find the least defined common subsumer: a conjunction of eligible names containing both Q and R in every model, and contained in every other such conjunction. Among equivalent conjunctions choose the fewest distinct names, then the lexicographically smallest sorted name list. Output only those case-sensitive names joined by ' & ', for example 'Aster & Cedar'; output TOP for the empty conjunction.
```

**Answer:**

```
Reed & Willow
```

## Level 2

### Example 1

**Prompt:**

```
An ontology catalog needs the tightest shared description of two queries, using only the eligible defined names. Definitions are equivalences and acyclic. Primitive concepts are independent sets; roles are arbitrary binary relations, with no other axioms. X & Y is intersection; exists r.(X) means having at least one r-successor in X. Different restrictions may use different successors. TOP contains every individual.
Use definitional unfolding and the EL structural subsumption algorithm: S is subsumed by T when every root atom of T occurs in S and each restriction of T is matched by a same-role restriction of S whose filler is recursively subsumed by the filler of that restriction of T.
Vocabulary:
Primitive concepts: Blue, Bright, Light, Rigid, Round, Smooth. Roles: part, link, cover.

Definitions:
H0 := Smooth & Bright & exists cover.(Round & Blue)
H1 := Rigid & Round & exists link.(H0)
H2 := Rigid & Light & exists cover.(H1)
Juniper := exists part.(H2) & exists link.(H0)
Oak := exists link.(H0) & H2
Dahlia := Blue & Juniper
Hazel := exists cover.(H1) & exists part.(H2) & Juniper
Grove := exists cover.(H1)
Iris := H1 & Round
Aster := H0 & exists link.(H0) & Oak
Birch := exists link.(H0)

Eligible Names:
Aster, Birch, Dahlia, Grove, Hazel, Iris, Juniper, Oak

Queries:
Q := exists link.(H0) & exists part.(H2) & exists cover.(Round & Blue) & exists part.(H2) & Blue & exists cover.(exists link.(H0) & Round & Rigid) & exists link.(H0) & exists part.(Rigid & Light & exists cover.(H1)) & exists cover.(H1) & Round & Juniper & Bright & exists link.(exists cover.(Round & Blue) & Smooth & Bright) & Oak & exists part.(Rigid & Light & exists cover.(H1)) & Smooth
R := exists link.(H0) & Bright & Smooth & exists part.(Light & Rigid & exists cover.(Round & Rigid & exists link.(H0))) & Juniper & Smooth & exists cover.(Round & Blue) & Oak & exists cover.(exists link.(exists cover.(Blue & Round) & Bright & Smooth) & Round & Rigid) & Light
Find the least defined common subsumer: a conjunction of eligible names containing both Q and R in every model, and contained in every other such conjunction. Among equivalent conjunctions choose the fewest distinct names, then the lexicographically smallest sorted name list. Output only those case-sensitive names joined by ' & ', for example 'Aster & Cedar'; output TOP for the empty conjunction.
```

**Answer:**

```
Aster & Hazel
```

### Example 2

**Prompt:**

```
An ontology catalog needs the tightest shared description of two queries, using only the eligible defined names. Definitions are equivalences and acyclic. Primitive concepts are independent sets; roles are arbitrary binary relations, with no other axioms. X & Y is intersection; exists r.(X) means having at least one r-successor in X. Different restrictions may use different successors. TOP contains every individual.
Use definitional unfolding and the EL structural subsumption algorithm: S is subsumed by T when every root atom of T occurs in S and each restriction of T is matched by a same-role restriction of S whose filler is recursively subsumed by the filler of that restriction of T.
Vocabulary:
Primitive concepts: Blue, Bright, Light, Rigid, Round, Smooth. Roles: part, link, cover.

Definitions:
H0 := Light & Rigid & exists cover.(Light & Rigid)
H1 := Round & exists part.(H0)
H2 := Light & exists cover.(H1)
Pine := Round
Maple := H1 & exists cover.(H0)
Willow := exists cover.(H0) & exists part.(H2)
Aster := exists cover.(H0) & H1 & Willow
Cedar := exists cover.(H0) & H2
Hazel := exists part.(H2)
Iris := exists link.(H1) & exists cover.(H0) & Maple
Fern := Blue & exists cover.(H0)

Eligible Names:
Aster, Cedar, Fern, Hazel, Iris, Maple, Pine, Willow

Queries:
Q := exists cover.(Rigid & exists cover.(Light & Rigid) & Light) & exists part.(H2) & Blue
R := Round & Bright & exists part.(Light & exists cover.(H1))
Find the least defined common subsumer: a conjunction of eligible names containing both Q and R in every model, and contained in every other such conjunction. Among equivalent conjunctions choose the fewest distinct names, then the lexicographically smallest sorted name list. Output only those case-sensitive names joined by ' & ', for example 'Aster & Cedar'; output TOP for the empty conjunction.
```

**Answer:**

```
Hazel
```

## Level 5

### Example 1

**Prompt:**

```
An ontology catalog needs the tightest shared description of two queries, using only the eligible defined names. Definitions are equivalences and acyclic. Primitive concepts are independent sets; roles are arbitrary binary relations, with no other axioms. X & Y is intersection; exists r.(X) means having at least one r-successor in X. Different restrictions may use different successors. TOP contains every individual.
Use definitional unfolding and the EL structural subsumption algorithm: S is subsumed by T when every root atom of T occurs in S and each restriction of T is matched by a same-role restriction of S whose filler is recursively subsumed by the filler of that restriction of T.
Vocabulary:
Primitive concepts: Blue, Bright, Light, Rigid, Round, Smooth. Roles: part, link, cover.

Definitions:
H0 := Blue & Bright & exists link.(Round & Smooth)
H1 := Bright & exists link.(H0)
H2 := Rigid & exists cover.(H0)
H3 := Blue & exists cover.(H0)
Iris := H0
Oak := exists link.(H3) & Rigid
Dahlia := exists part.(H2) & exists link.(H3)
Cedar := Bright & exists link.(H3)
Pine := H2 & H1 & exists part.(H2)
Grove := H3 & exists part.(H2) & Dahlia
Birch := H3 & exists link.(H3) & Dahlia
Juniper := Bright
Fern := H1 & exists part.(H2) & exists link.(H3)
Willow := Bright

Eligible Names:
Birch, Cedar, Dahlia, Fern, Grove, Iris, Juniper, Oak, Pine, Willow

Queries:
Q := exists link.(H3) & exists part.(exists cover.(H0) & Rigid) & Bright & exists link.(Blue & exists cover.(H0))
R := exists link.(H3) & exists part.(H2)
Find the least defined common subsumer: a conjunction of eligible names containing both Q and R in every model, and contained in every other such conjunction. Among equivalent conjunctions choose the fewest distinct names, then the lexicographically smallest sorted name list. Output only those case-sensitive names joined by ' & ', for example 'Aster & Cedar'; output TOP for the empty conjunction.
```

**Answer:**

```
Dahlia
```

### Example 2

**Prompt:**

```
An ontology catalog needs the tightest shared description of two queries, using only the eligible defined names. Definitions are equivalences and acyclic. Primitive concepts are independent sets; roles are arbitrary binary relations, with no other axioms. X & Y is intersection; exists r.(X) means having at least one r-successor in X. Different restrictions may use different successors. TOP contains every individual.
Use definitional unfolding and the EL structural subsumption algorithm: S is subsumed by T when every root atom of T occurs in S and each restriction of T is matched by a same-role restriction of S whose filler is recursively subsumed by the filler of that restriction of T.
Vocabulary:
Primitive concepts: Blue, Bright, Light, Rigid, Round, Smooth. Roles: part, link, cover.

Definitions:
H0 := Round & exists link.(Bright & Blue)
H1 := Rigid & exists cover.(H0)
H2 := Smooth & exists link.(H1)
H3 := Smooth & Bright & Blue & exists cover.(H1)
Hazel := H0 & Blue
Grove := exists part.(H1) & Hazel
Iris := Light & Round & Grove
Elm := H0 & exists part.(H1) & exists link.(H1) & Iris
Oak := H0 & H3 & Iris
Cedar := Blue & exists link.(H1) & H0 & Iris
Birch := Light & Round & Iris
Dahlia := Round & exists link.(H1) & H3
Pine := exists link.(H1) & H3 & Elm
Juniper := H2 & H3 & Blue & Oak

Eligible Names:
Birch, Cedar, Dahlia, Elm, Grove, Hazel, Iris, Juniper, Oak, Pine

Queries:
Q := Iris & Light & Light & H0 & Round & Grove & exists link.(H1) & Blue & Round
R := Bright & exists link.(H1) & Round & Iris & Elm & Blue & Light & exists link.(H1) & Round & exists cover.(H1) & Smooth & H3 & Bright
Find the least defined common subsumer: a conjunction of eligible names containing both Q and R in every model, and contained in every other such conjunction. Among equivalent conjunctions choose the fewest distinct names, then the lexicographically smallest sorted name list. Output only those case-sensitive names joined by ' & ', for example 'Aster & Cedar'; output TOP for the empty conjunction.
```

**Answer:**

```
Cedar
```

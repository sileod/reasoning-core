# samples_P007v1

## Level 0

### Example 1

Prompt:

```
A craft orbits a point central body with a fixed gravitational parameter (mu). We consider an instantaneous rebaselining of its orbit and want the resulting orbit's invariants. For a two-body orbit the specific angular momentum is h = r * v_t where v_t is the tangential speed, the specific orbital energy is eps = v^2/2 - mu/r, and the eccentricity satisfies e^2 = 1 + 2*eps*h^2/mu^2. The orbit type follows from e: e=0 circular, 0<e<1 elliptic, e=1 parabolic, e>1 hyperbolic.

The craft is a distance r = 6 from the central body, moving purely tangentially with speed v = 2.0000. The central body's mass suddenly changes so its gravitational parameter goes from mu1 = 5 to mu2 = 2; the craft's position and velocity vector are unchanged at that instant.

Report the specific angular momentum h of the resulting orbit, rounded to 3 decimal places, as 'h=<value>' (for example 'h=12.500').
```

Answer:

```
h=12.000
```

### Example 2

Prompt:

```
A craft orbits a point central body with a fixed gravitational parameter (mu). We consider an instantaneous rebaselining of its orbit and want the resulting orbit's invariants. For a two-body orbit the specific angular momentum is h = r * v_t where v_t is the tangential speed, the specific orbital energy is eps = v^2/2 - mu/r, and the eccentricity satisfies e^2 = 1 + 2*eps*h^2/mu^2. The orbit type follows from e: e=0 circular, 0<e<1 elliptic, e=1 parabolic, e>1 hyperbolic.

The craft is a distance r = 4 from the central body, moving purely tangentially with speed v = 2.0000. The central body's mass suddenly changes so its gravitational parameter goes from mu1 = 2 to mu2 = 7; the craft's position and velocity vector are unchanged at that instant.

Report the type of the resulting orbit and its periapsis (and, for a bound orbit, apoapsis) radius, rounded to 3 decimal places. Use exactly: 'circular r=<r>' for e=0; 'elliptic rp=<rp> ra=<ra>' for an ellipse; 'parabolic rp=<rp>' for e=1; 'hyperbolic rp=<rp>' for e>1. For example 'elliptic rp=1.500 ra=3.200'.
```

Answer:

```
hyperbolic rp=4.000
```

## Level 2

### Example 1

Prompt:

```
A craft orbits a point central body with a fixed gravitational parameter (mu). We consider an instantaneous rebaselining of its orbit and want the resulting orbit's invariants. For a two-body orbit the specific angular momentum is h = r * v_t where v_t is the tangential speed, the specific orbital energy is eps = v^2/2 - mu/r, and the eccentricity satisfies e^2 = 1 + 2*eps*h^2/mu^2. The orbit type follows from e: e=0 circular, 0<e<1 elliptic, e=1 parabolic, e>1 hyperbolic.

At its current apside the craft is a distance r = 7.5 from the central body, moving purely tangentially with speed v = 2.2763. A retrograde impulse of magnitude 0.4874 immediately alters its tangential speed (prograde adds to v, retrograde subtracts), while r and the gravitational parameter stay the same. mu = 15.

Report the specific angular momentum h of the resulting orbit, rounded to 3 decimal places, as 'h=<value>' (for example 'h=12.500').
```

Answer:

```
h=13.417
```

### Example 2

Prompt:

```
A craft orbits a point central body with a fixed gravitational parameter (mu). We consider an instantaneous rebaselining of its orbit and want the resulting orbit's invariants. For a two-body orbit the specific angular momentum is h = r * v_t where v_t is the tangential speed, the specific orbital energy is eps = v^2/2 - mu/r, and the eccentricity satisfies e^2 = 1 + 2*eps*h^2/mu^2. The orbit type follows from e: e=0 circular, 0<e<1 elliptic, e=1 parabolic, e>1 hyperbolic.

At its current apside the craft is a distance r = 4.615 from the central body, moving purely tangentially with speed v = 2.8381. A prograde impulse of magnitude 1.4735 immediately alters its tangential speed (prograde adds to v, retrograde subtracts), while r and the gravitational parameter stay the same. mu = 33.

Report the specific angular momentum h of the resulting orbit, rounded to 3 decimal places, as 'h=<value>' (for example 'h=12.500').
```

Answer:

```
h=19.900
```

## Level 5

### Example 1

Prompt:

```
A craft orbits a point central body with a fixed gravitational parameter (mu). We consider an instantaneous rebaselining of its orbit and want the resulting orbit's invariants. For a two-body orbit the specific angular momentum is h = r * v_t where v_t is the tangential speed, the specific orbital energy is eps = v^2/2 - mu/r, and the eccentricity satisfies e^2 = 1 + 2*eps*h^2/mu^2. The orbit type follows from e: e=0 circular, 0<e<1 elliptic, e=1 parabolic, e>1 hyperbolic.

The craft coasts between two specified apsides of its elliptic orbit: periapsis radius rp = 18 and apoapsis radius ra = 48. At each apside its velocity is purely tangential. The central body's gravitational parameter is mu = 42.

Report the type of the resulting orbit and its periapsis (and, for a bound orbit, apoapsis) radius, rounded to 3 decimal places. Use exactly: 'circular r=<r>' for e=0; 'elliptic rp=<rp> ra=<ra>' for an ellipse; 'parabolic rp=<rp>' for e=1; 'hyperbolic rp=<rp>' for e>1. For example 'elliptic rp=1.500 ra=3.200'.
```

Answer:

```
h=33.161
```

### Example 2

Prompt:

```
A craft orbits a point central body with a fixed gravitational parameter (mu). We consider an instantaneous rebaselining of its orbit and want the resulting orbit's invariants. For a two-body orbit the specific angular momentum is h = r * v_t where v_t is the tangential speed, the specific orbital energy is eps = v^2/2 - mu/r, and the eccentricity satisfies e^2 = 1 + 2*eps*h^2/mu^2. The orbit type follows from e: e=0 circular, 0<e<1 elliptic, e=1 parabolic, e>1 hyperbolic.

At its current apside the craft is a distance r = 9.231 from the central body, moving purely tangentially with speed v = 2.0935. A prograde impulse of magnitude 0.9553 immediately alters its tangential speed (prograde adds to v, retrograde subtracts), while r and the gravitational parameter stay the same. mu = 66.

Report the type of the resulting orbit and its periapsis (and, for a bound orbit, apoapsis) radius, rounded to 3 decimal places. Use exactly: 'circular r=<r>' for e=0; 'elliptic rp=<rp> ra=<ra>' for an ellipse; 'parabolic rp=<rp>' for e=1; 'hyperbolic rp=<rp>' for e>1. For example 'elliptic rp=1.500 ra=3.200'.
```

Answer:

```
elliptic rp=9.231 ra=17.144
```

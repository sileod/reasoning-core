## Level 0

### Example 1

Prompt:

```
class Base:
    def __init__(self, b0, b1):
        self.beta = b0
        self.mu = b1

class Widget(Base):
    def __init__(self):
        self.core = 20
        super().__init__(60, self.core)
        self.odds = 49

The class is built and Widget() is instantiated, running __init__. List every self.<field>=<value> assignment that executes during construction, in the exact order they run. Note that super().__init__(...) writes the base class fields at the point it is called, between any earlier and later assignments in the derived constructor. Report the full ordered sequence of writes as 'field=value' entries separated by commas, e.g. size=3, alpha=7. A field written more than once appears more than once, in order.
```

**Answer:** core=20, beta=60, mu=20, odds=49

### Example 2

Prompt:

```
class Base:
    def __init__(self, b0, b1):
        self.delta = b0
        self.theta = b1

class Widget(Base):
    def __init__(self):
        self.peak = 2
        super().__init__(30, 50)
        self.edge = 22

The class is built and Widget() is instantiated, running __init__. List every self.<field>=<value> assignment that executes during construction, in the exact order they run. Note that super().__init__(...) writes the base class fields at the point it is called, between any earlier and later assignments in the derived constructor. Report the full ordered sequence of writes as 'field=value' entries separated by commas, e.g. size=3, alpha=7. A field written more than once appears more than once, in order.
```

**Answer:** peak=2, delta=30, theta=50, edge=22

## Level 2

### Example 1

Prompt:

```
class Base:
    def __init__(self, b0, b1, b2):
        self.delta = b0
        self.gamma = b1
        self.mu = b2

class Widget(Base):
    def __init__(self):
        self.peak = 15
        self.base_len = 20
        super().__init__(27, 10, self.peak)
        self.margin = 34
        self.drift = self.gamma

The class is built and Widget() is instantiated, running __init__. List every self.<field>=<value> assignment that executes during construction, in the exact order they run. Note that super().__init__(...) writes the base class fields at the point it is called, between any earlier and later assignments in the derived constructor. Report the full ordered sequence of writes as 'field=value' entries separated by commas, e.g. size=3, alpha=7. A field written more than once appears more than once, in order.
```

**Answer:** peak=15, base_len=20, delta=27, gamma=10, mu=15, margin=34, drift=10

### Example 2

Prompt:

```
class Base:
    def __init__(self, b0, b1, b2):
        self.kappa = b0
        self.beta = b1
        self.lambda = b2

class Widget(Base):
    def __init__(self):
        self.base_len = 52
        self.size = 5
        super().__init__(47, 21, 7)
        self.leeway = self.lambda
        self.odds = 2

The class is built and Widget() is instantiated, running __init__. List every self.<field>=<value> assignment that executes during construction, in the exact order they run. Note that super().__init__(...) writes the base class fields at the point it is called, between any earlier and later assignments in the derived constructor. Report the full ordered sequence of writes as 'field=value' entries separated by commas, e.g. size=3, alpha=7. A field written more than once appears more than once, in order.
```

**Answer:** base_len=52, size=5, kappa=47, beta=21, lambda=7, leeway=7, odds=2

## Level 5

### Example 1

Prompt:

```
class Base:
    def __init__(self, b0, b1, b2, b3, b4):
        self.zeta = b0
        self.eta = b1
        self.iota = b2
        self.delta = b3
        self.alpha = b4

class Widget(Base):
    def __init__(self):
        self.peak = 38
        self.core = 44
        self.stride = 13
        self.reach = 48
        super().__init__(self.core, self.core, self.stride, 4, self.stride)
        self.edge = self.eta
        self.margin = self.delta
        self.offset = self.reach
        self.rank = self.margin

The class is built and Widget() is instantiated, running __init__. List every self.<field>=<value> assignment that executes during construction, in the exact order they run. Note that super().__init__(...) writes the base class fields at the point it is called, between any earlier and later assignments in the derived constructor. Report the full ordered sequence of writes as 'field=value' entries separated by commas, e.g. size=3, alpha=7. A field written more than once appears more than once, in order.
```

**Answer:** peak=38, core=44, stride=13, reach=48, zeta=44, eta=44, iota=13, delta=4, alpha=13, edge=44, margin=4, offset=48, rank=4

### Example 2

Prompt:

```
class Base:
    def __init__(self, b0, b1, b2, b3, b4):
        self.mu = b0
        self.iota = b1
        self.eta = b2
        self.theta = b3
        self.lambda = b4

class Widget(Base):
    def __init__(self):
        self.core = 54
        self.peak = 58
        self.size = 50
        self.reach = 57
        super().__init__(self.core, self.reach, 23, self.size, self.reach)
        self.merit = 24
        self.drift = self.eta
        self.margin = self.eta
        self.gain = 50

The class is built and Widget() is instantiated, running __init__. List every self.<field>=<value> assignment that executes during construction, in the exact order they run. Note that super().__init__(...) writes the base class fields at the point it is called, between any earlier and later assignments in the derived constructor. Report the full ordered sequence of writes as 'field=value' entries separated by commas, e.g. size=3, alpha=7. A field written more than once appears more than once, in order.
```

**Answer:** core=54, peak=58, size=50, reach=57, mu=54, iota=57, eta=23, theta=50, lambda=57, merit=24, drift=23, margin=23, gain=50

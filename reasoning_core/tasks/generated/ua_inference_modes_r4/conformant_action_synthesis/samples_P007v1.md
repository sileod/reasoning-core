## Level 0

### Example 1

Prompt:

You control a system with flags a, b, c. Each flag is either set or clear, and you get no observations, so you must act blind. The system starts in exactly one of these hidden states (the listed flags are set, the rest are clear):
  - {}
  - {a, b, c}

Each available action is guarded by its 'requires' (flags that must be set) and 'forbids' (flags that must be clear) conditions, and does nothing if its guards are not met. The listed possible outcomes are nondeterministic: exactly one occurs whenever the action applies, and clearing a flag is irreversible.
  A (cost 1, requires none, forbids b): possible outcomes are {a, b, c set, nothing clear}
  B (cost 2, requires none, forbids none): possible outcomes are {nothing set, a clear}
  C (cost 2, requires none, forbids none): possible outcomes are {nothing set, nothing clear}

Your total action cost may not exceed the resource budget of 4.

Find the shortest action sequence (fewest actions) that, no matter which hidden start state or which nondeterministic outcome occurs, guarantees that flags b, c are all set. Answer as a semicolon-separated list of action names with no spaces; for example 'A;B;C' means do A, then B, then C.


Answer: A



### Example 2

Prompt:

You control a system with flags a, b, c. Each flag is either set or clear, and you get no observations, so you must act blind. The system starts in exactly one of these hidden states (the listed flags are set, the rest are clear):
  - {}
  - {a, c}

Each available action is guarded by its 'requires' (flags that must be set) and 'forbids' (flags that must be clear) conditions, and does nothing if its guards are not met. The listed possible outcomes are nondeterministic: exactly one occurs whenever the action applies, and clearing a flag is irreversible.
  A (cost 1, requires b, c, forbids none): possible outcomes are {nothing set, nothing clear}
  B (cost 1, requires c, forbids none): possible outcomes are {c set, nothing clear}
  C (cost 2, requires none, forbids none): possible outcomes are {a, b, c set, nothing clear}

Your total action cost may not exceed the resource budget of 4.

Find the shortest action sequence (fewest actions) that, no matter which hidden start state or which nondeterministic outcome occurs, guarantees that flags a, b are all set. Answer as a semicolon-separated list of action names with no spaces; for example 'A;B;C' means do A, then B, then C.


Answer: C



## Level 2

### Example 1

Prompt:

You control a system with flags a, b, c. Each flag is either set or clear, and you get no observations, so you must act blind. The system starts in exactly one of these hidden states (the listed flags are set, the rest are clear):
  - {a, c}
  - {b}
  - {}

Each available action is guarded by its 'requires' (flags that must be set) and 'forbids' (flags that must be clear) conditions, and does nothing if its guards are not met. The listed possible outcomes are nondeterministic: exactly one occurs whenever the action applies, and clearing a flag is irreversible.
  A (cost 2, requires a, b, c, forbids a, b, c): possible outcomes are {nothing set, nothing clear}
  B (cost 2, requires none, forbids none): possible outcomes are {a, c set, nothing clear}
  C (cost 1, requires none, forbids none): possible outcomes are {b set, nothing clear}
  D (cost 1, requires none, forbids none): possible outcomes are {nothing set, nothing clear}

Your total action cost may not exceed the resource budget of 6.

Find the shortest action sequence (fewest actions) that, no matter which hidden start state or which nondeterministic outcome occurs, guarantees that flags b, c are all set. Answer as a semicolon-separated list of action names with no spaces; for example 'A;B;C' means do A, then B, then C.


Answer: B;C



### Example 2

Prompt:

You control a system with flags a, b, c. Each flag is either set or clear, and you get no observations, so you must act blind. The system starts in exactly one of these hidden states (the listed flags are set, the rest are clear):
  - {c}
  - {a, b, c}
  - {}

Each available action is guarded by its 'requires' (flags that must be set) and 'forbids' (flags that must be clear) conditions, and does nothing if its guards are not met. The listed possible outcomes are nondeterministic: exactly one occurs whenever the action applies, and clearing a flag is irreversible.
  A (cost 1, requires none, forbids a, c): possible outcomes are {a, b set, nothing clear}
  B (cost 1, requires none, forbids a): possible outcomes are {b, c set, nothing clear}
  C (cost 1, requires none, forbids none): possible outcomes are {nothing set, a, b, c clear}
  D (cost 2, requires none, forbids c): possible outcomes are {c set, nothing clear}

Your total action cost may not exceed the resource budget of 6.

Find the shortest action sequence (fewest actions) that, no matter which hidden start state or which nondeterministic outcome occurs, guarantees that flags a, b are all set. Answer as a semicolon-separated list of action names with no spaces; for example 'A;B;C' means do A, then B, then C.


Answer: C;A



## Level 5

### Example 1

Prompt:

You control a system with flags a, b, c, d. Each flag is either set or clear, and you get no observations, so you must act blind. The system starts in exactly one of these hidden states (the listed flags are set, the rest are clear):
  - {d}
  - {a, b, c, d}
  - {b, c, d}
  - {a, b, d}

Each available action is guarded by its 'requires' (flags that must be set) and 'forbids' (flags that must be clear) conditions, and does nothing if its guards are not met. The listed possible outcomes are nondeterministic: exactly one occurs whenever the action applies, and clearing a flag is irreversible.
  A (cost 1, requires none, forbids none): possible outcomes are {nothing set, a, b, d clear}
  B (cost 2, requires none, forbids a, b, c, d): possible outcomes are {a, b, c, d set, nothing clear} | {a, b, c, d set, nothing clear}
  C (cost 1, requires none, forbids none): possible outcomes are {nothing set, nothing clear}
  D (cost 2, requires none, forbids none): possible outcomes are {nothing set, b, c clear}
  E (cost 1, requires none, forbids none): possible outcomes are {c, d set, nothing clear} | {nothing set, nothing clear}

Your total action cost may not exceed the resource budget of 9.

Find the shortest action sequence (fewest actions) that, no matter which hidden start state or which nondeterministic outcome occurs, guarantees that flags a, d are all set. Answer as a semicolon-separated list of action names with no spaces; for example 'A;B;C' means do A, then B, then C.


Answer: A;D;B



### Example 2

Prompt:

You control a system with flags a, b, c, d. Each flag is either set or clear, and you get no observations, so you must act blind. The system starts in exactly one of these hidden states (the listed flags are set, the rest are clear):
  - {}
  - {d}
  - {a, b, c, d}
  - {b}

Each available action is guarded by its 'requires' (flags that must be set) and 'forbids' (flags that must be clear) conditions, and does nothing if its guards are not met. The listed possible outcomes are nondeterministic: exactly one occurs whenever the action applies, and clearing a flag is irreversible.
  A (cost 2, requires c, d, forbids none): possible outcomes are {a, b, c, d set, nothing clear}
  B (cost 1, requires none, forbids none): possible outcomes are {a, b set, a, d clear} | {nothing set, c clear}
  C (cost 1, requires none, forbids none): possible outcomes are {nothing set, a, b clear} | {d set, nothing clear}
  D (cost 1, requires a, b, c, forbids none): possible outcomes are {nothing set, d clear} | {a, c, d set, nothing clear}
  E (cost 1, requires none, forbids none): possible outcomes are {c, d set, nothing clear}

Your total action cost may not exceed the resource budget of 9.

Find the shortest action sequence (fewest actions) that, no matter which hidden start state or which nondeterministic outcome occurs, guarantees that flags a are all set. Answer as a semicolon-separated list of action names with no spaces; for example 'A;B;C' means do A, then B, then C.


Answer: E;A



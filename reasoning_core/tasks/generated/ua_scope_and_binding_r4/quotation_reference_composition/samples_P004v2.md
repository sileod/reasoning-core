## Level 0

### Example 1

Prompt:

We evaluate a tiny list language. Bare symbols (like red) and integers (like 17) denote themselves. A capital-letter variable denotes the value it is bound to. A quote ' u1 u2 ... un treats each unit as syntax rather than as a value: quoting a symbol yields that symbol, and quoting a variable yields its name as a symbol. An unquote ,X inside a quote inserts the value that X is bound to. A single quoted unit stands alone; two or more quoted units form a list.

Bindings: E = snow, F = bloom

Expression 1: ' bloom wheat
Expression 2: ' ,F wheat

Do Expression 1 and Expression 2 denote the same object? Answer with a single word: "yes" if they denote the same object, "no" otherwise.

Answer: yes

### Example 2

Prompt:

We evaluate a tiny list language. Bare symbols (like red) and integers (like 17) denote themselves. A capital-letter variable denotes the value it is bound to. A quote ' u1 u2 ... un treats each unit as syntax rather than as a value: quoting a symbol yields that symbol, and quoting a variable yields its name as a symbol. An unquote ,X inside a quote inserts the value that X is bound to. A single quoted unit stands alone; two or more quoted units form a list.

Bindings: D = red, E = horse

Expression 1: ' pine
Expression 2: ' lake

Do Expression 1 and Expression 2 denote the same object? Answer with a single word: "yes" if they denote the same object, "no" otherwise.

Answer: no

## Level 2

### Example 1

Prompt:

We evaluate a tiny list language. Bare symbols (like red) and integers (like 17) denote themselves. A capital-letter variable denotes the value it is bound to. A quote ' u1 u2 ... un treats each unit as syntax rather than as a value: quoting a symbol yields that symbol, and quoting a variable yields its name as a symbol. An unquote ,X inside a quote inserts the value that X is bound to. A single quoted unit stands alone; two or more quoted units form a list.

Bindings: C = red, E = snow, F = wheat

Expression 1: ' wine snow wine
Expression 2: ' wine ,E wine

Do Expression 1 and Expression 2 denote the same object? Answer with a single word: "yes" if they denote the same object, "no" otherwise.

Answer: yes

### Example 2

Prompt:

We evaluate a tiny list language. Bare symbols (like red) and integers (like 17) denote themselves. A capital-letter variable denotes the value it is bound to. A quote ' u1 u2 ... un treats each unit as syntax rather than as a value: quoting a symbol yields that symbol, and quoting a variable yields its name as a symbol. An unquote ,X inside a quote inserts the value that X is bound to. A single quoted unit stands alone; two or more quoted units form a list.

Bindings: F = horse, B = pine, D = snow

Expression 1: ' snow wheat snow
Expression 2: ' ,D wheat snow

Do Expression 1 and Expression 2 denote the same object? Answer with a single word: "yes" if they denote the same object, "no" otherwise.

Answer: yes

## Level 5

### Example 1

Prompt:

We evaluate a tiny list language. Bare symbols (like red) and integers (like 17) denote themselves. A capital-letter variable denotes the value it is bound to. A quote ' u1 u2 ... un treats each unit as syntax rather than as a value: quoting a symbol yields that symbol, and quoting a variable yields its name as a symbol. An unquote ,X inside a quote inserts the value that X is bound to. A single quoted unit stands alone; two or more quoted units form a list.

Bindings: B = cinder, A = cinder, D = reed, E = horse

Expression 1: A
Expression 2: ' cinder

Do Expression 1 and Expression 2 denote the same object? Answer with a single word: "yes" if they denote the same object, "no" otherwise.

Answer: yes

### Example 2

Prompt:

We evaluate a tiny list language. Bare symbols (like red) and integers (like 17) denote themselves. A capital-letter variable denotes the value it is bound to. A quote ' u1 u2 ... un treats each unit as syntax rather than as a value: quoting a symbol yields that symbol, and quoting a variable yields its name as a symbol. An unquote ,X inside a quote inserts the value that X is bound to. A single quoted unit stands alone; two or more quoted units form a list.

Bindings: D = reed, F = wheat, C = fog, A = wheat

Expression 1: ' ,F ,A wheat wheat ,F
Expression 2: ' ,F ,A wheat ,A ,F

Do Expression 1 and Expression 2 denote the same object? Answer with a single word: "yes" if they denote the same object, "no" otherwise.

Answer: yes


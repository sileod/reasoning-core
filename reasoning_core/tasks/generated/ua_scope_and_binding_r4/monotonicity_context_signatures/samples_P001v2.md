# Level 0

## Example 1

Prompt:

Displayed below is a fragment of a logical-form tree, written as leaves indexed left to right from 0.
Nesting: when both leaf[i] and leaf[i+1] exist, leaf[i] lies inside the scope (restrictor/nuclear scope) of the operator at leaf[i+1]; the outermost operator is at the highest index.
Every leaf also carries its own polarity sign: + means upward monotone, - means downward monotone, 0 means nonmonotone.
The polarity context at the marked leaf (*) is computed by threading the outermost operator inward, starting from a positive position, and applying, in order:
  - restrictor of an upward-monotone quantifier (every/all/each/at least two): context unchanged;
  - restrictor of a downward-monotone quantifier (no/few/not every): context sign reversed;
  - negation 'not': context sign reversed;
  - conjunction 'and': context becomes nonmonotone 0.
The sign at the marked constituent is its own polarity multiplied onto that context: equal signs give +, opposite signs give -, and a 0 anywhere gives 0.

leaf[0]: no operator; inherent polarity upward
leaf[1]: no operator; inherent polarity downward  <-- marked (*)

State just the sign of the marked constituent.


Answer: -

## Example 2

Prompt:

Displayed below is a fragment of a logical-form tree, written as leaves indexed left to right from 0.
Nesting: when both leaf[i] and leaf[i+1] exist, leaf[i] lies inside the scope (restrictor/nuclear scope) of the operator at leaf[i+1]; the outermost operator is at the highest index.
Every leaf also carries its own polarity sign: + means upward monotone, - means downward monotone, 0 means nonmonotone.
The polarity context at the marked leaf (*) is computed by threading the outermost operator inward, starting from a positive position, and applying, in order:
  - restrictor of an upward-monotone quantifier (every/all/each/at least two): context unchanged;
  - restrictor of a downward-monotone quantifier (no/few/not every): context sign reversed;
  - negation 'not': context sign reversed;
  - conjunction 'and': context becomes nonmonotone 0.
The sign at the marked constituent is its own polarity multiplied onto that context: equal signs give +, opposite signs give -, and a 0 anywhere gives 0.

leaf[0]: no operator; inherent polarity upward
leaf[1]: no operator; inherent polarity downward  <-- marked (*)

State just the sign of the marked constituent.


Answer: -

# Level 2

## Example 1

Prompt:

Displayed below is a fragment of a logical-form tree, written as leaves indexed left to right from 0.
Nesting: when both leaf[i] and leaf[i+1] exist, leaf[i] lies inside the scope (restrictor/nuclear scope) of the operator at leaf[i+1]; the outermost operator is at the highest index.
Every leaf also carries its own polarity sign: + means upward monotone, - means downward monotone, 0 means nonmonotone.
The polarity context at the marked leaf (*) is computed by threading the outermost operator inward, starting from a positive position, and applying, in order:
  - restrictor of an upward-monotone quantifier (every/all/each/at least two): context unchanged;
  - restrictor of a downward-monotone quantifier (no/few/not every): context sign reversed;
  - negation 'not': context sign reversed;
  - conjunction 'and': context becomes nonmonotone 0.
The sign at the marked constituent is its own polarity multiplied onto that context: equal signs give +, opposite signs give -, and a 0 anywhere gives 0.

leaf[0]: its restrictor is the upward-monotone quantifier 'every'; inherent polarity upward
leaf[1]: no operator; inherent polarity upward  <-- marked (*)
leaf[2]: its restrictor is the downward-monotone quantifier 'not every'; inherent polarity upward
leaf[3]: its restrictor is the upward-monotone quantifier 'at least two'; inherent polarity upward

State just the sign of the marked constituent.


Answer: -

## Example 2

Prompt:

Displayed below is a fragment of a logical-form tree, written as leaves indexed left to right from 0.
Nesting: when both leaf[i] and leaf[i+1] exist, leaf[i] lies inside the scope (restrictor/nuclear scope) of the operator at leaf[i+1]; the outermost operator is at the highest index.
Every leaf also carries its own polarity sign: + means upward monotone, - means downward monotone, 0 means nonmonotone.
The polarity context at the marked leaf (*) is computed by threading the outermost operator inward, starting from a positive position, and applying, in order:
  - restrictor of an upward-monotone quantifier (every/all/each/at least two): context unchanged;
  - restrictor of a downward-monotone quantifier (no/few/not every): context sign reversed;
  - negation 'not': context sign reversed;
  - conjunction 'and': context becomes nonmonotone 0.
The sign at the marked constituent is its own polarity multiplied onto that context: equal signs give +, opposite signs give -, and a 0 anywhere gives 0.

leaf[0]: negation, "not"; inherent polarity downward
leaf[1]: no operator; inherent polarity upward
leaf[2]: its restrictor is the downward-monotone quantifier 'not every'; inherent polarity downward
leaf[3]: no operator; inherent polarity downward  <-- marked (*)

State just the sign of the marked constituent.


Answer: -

# Level 5

## Example 1

Prompt:

Displayed below is a fragment of a logical-form tree, written as leaves indexed left to right from 0.
Nesting: when both leaf[i] and leaf[i+1] exist, leaf[i] lies inside the scope (restrictor/nuclear scope) of the operator at leaf[i+1]; the outermost operator is at the highest index.
Every leaf also carries its own polarity sign: + means upward monotone, - means downward monotone, 0 means nonmonotone.
The polarity context at the marked leaf (*) is computed by threading the outermost operator inward, starting from a positive position, and applying, in order:
  - restrictor of an upward-monotone quantifier (every/all/each/at least two): context unchanged;
  - restrictor of a downward-monotone quantifier (no/few/not every): context sign reversed;
  - negation 'not': context sign reversed;
  - conjunction 'and': context becomes nonmonotone 0.
The sign at the marked constituent is its own polarity multiplied onto that context: equal signs give +, opposite signs give -, and a 0 anywhere gives 0.

leaf[0]: negation, "not"; inherent polarity downward
leaf[1]: its restrictor is the downward-monotone quantifier 'few'; inherent polarity downward
leaf[2]: its restrictor is the upward-monotone quantifier 'every'; inherent polarity downward
leaf[3]: no operator; inherent polarity downward
leaf[4]: its restrictor is the upward-monotone quantifier 'every'; inherent polarity upward
leaf[5]: its restrictor is the upward-monotone quantifier 'at least two'; inherent polarity upward
leaf[6]: its restrictor is the downward-monotone quantifier 'few'; inherent polarity upward  <-- marked (*)
leaf[7]: its restrictor is the downward-monotone quantifier 'not every'; inherent polarity upward

State just the sign of the marked constituent.


Answer: -

## Example 2

Prompt:

Displayed below is a fragment of a logical-form tree, written as leaves indexed left to right from 0.
Nesting: when both leaf[i] and leaf[i+1] exist, leaf[i] lies inside the scope (restrictor/nuclear scope) of the operator at leaf[i+1]; the outermost operator is at the highest index.
Every leaf also carries its own polarity sign: + means upward monotone, - means downward monotone, 0 means nonmonotone.
The polarity context at the marked leaf (*) is computed by threading the outermost operator inward, starting from a positive position, and applying, in order:
  - restrictor of an upward-monotone quantifier (every/all/each/at least two): context unchanged;
  - restrictor of a downward-monotone quantifier (no/few/not every): context sign reversed;
  - negation 'not': context sign reversed;
  - conjunction 'and': context becomes nonmonotone 0.
The sign at the marked constituent is its own polarity multiplied onto that context: equal signs give +, opposite signs give -, and a 0 anywhere gives 0.

leaf[0]: conjunction, "and"; inherent polarity upward  <-- marked (*)
leaf[1]: its restrictor is the downward-monotone quantifier 'no'; inherent polarity downward
leaf[2]: conjunction, "and"; inherent polarity upward
leaf[3]: its restrictor is the upward-monotone quantifier 'all'; inherent polarity upward
leaf[4]: its restrictor is the upward-monotone quantifier 'at least two'; inherent polarity downward
leaf[5]: its restrictor is the upward-monotone quantifier 'at least two'; inherent polarity upward
leaf[6]: its restrictor is the upward-monotone quantifier 'all'; inherent polarity upward
leaf[7]: no operator; inherent polarity upward

State just the sign of the marked constituent.


Answer: 0


Generated deterministically with seed 2302342651.

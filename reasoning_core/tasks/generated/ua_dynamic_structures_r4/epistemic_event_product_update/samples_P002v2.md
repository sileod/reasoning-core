## Level 0
### Example 1
**Prompt:**
We model knowledge over possible worlds. Agents: {ann, ben}. Facts: {f1, f2, f3}.

Initial model, actual world marked *:
  w0*: f1=T f2=F f3=T
  w1 : f1=F f2=F f3=T
  w2 : f1=F f2=T f3=F
  w3 : f1=F f2=F f3=F
Observability (worlds an agent cannot distinguish):
  ann: {w0}, {w1}, {w2}, {w3}
  ben: {w0,w1,w2}, {w3}

Event sequence:
Event 1:
  e0* [f2->T, f3->F]; possible in {w1,w2,w3,w0}
  Observability of event worlds:
    ann: {e0}
    ben: {e0}

An agent knows a fact if the fact is true in every world the agent considers possible after all events.

Queried facts in order: f1, f3.
For each queried fact, give the sorted, comma-separated list of agents that know the fact, facts separated by ' | '. Use '-' if no agent knows that fact.
Example format: 'ann,ben | -'.
**Answer:**
ann | -

### Example 2
**Prompt:**
We model knowledge over possible worlds. Agents: {ann, ben}. Facts: {f1, f2, f3}.

Initial model, actual world marked *:
  w0*: f1=T f2=F f3=T
  w1 : f1=F f2=T f3=T
  w2 : f1=T f2=T f3=T
  w3 : f1=F f2=T f3=F
Observability (worlds an agent cannot distinguish):
  ann: {w0,w2}, {w1,w3}
  ben: {w0,w1,w2,w3}

Event sequence:
Event 1:
  e0* [f3->T]; possible in {w3,w1,w0,w2}
  Observability of event worlds:
    ann: {e0}
    ben: {e0}

An agent knows a fact if the fact is true in every world the agent considers possible after all events.

Queried facts in order: f1, f3.
For each queried fact, give the sorted, comma-separated list of agents that know the fact, facts separated by ' | '. Use '-' if no agent knows that fact.
Example format: 'ann,ben | -'.
**Answer:**
ann | ann,ben

## Level 2
### Example 1
**Prompt:**
We model knowledge over possible worlds. Agents: {ann, ben, cara}. Facts: {f1, f2, f3, f4}.

Initial model, actual world marked *:
  w0*: f1=F f2=F f3=F f4=T
  w1 : f1=T f2=F f3=F f4=T
  w2 : f1=F f2=F f3=F f4=F
  w3 : f1=F f2=T f3=T f4=T
  w4 : f1=T f2=T f3=F f4=T
  w5 : f1=F f2=T f3=T f4=F
  w6 : f1=F f2=F f3=F f4=T
  w7 : f1=F f2=F f3=F f4=F
Observability (worlds an agent cannot distinguish):
  ann: {w0,w1,w2,w3}, {w4,w5,w6,w7}
  ben: {w0,w1,w2,w5}, {w3,w4}, {w6}, {w7}
  cara: {w0,w1}, {w2}, {w3,w4}, {w5,w6}, {w7}

Event sequence:
Event 1:
  e0* [f3->T]; possible in {w3,w7,w6,w4,w0,w2,w1,w5}
  Observability of event worlds:
    ann: {e0}
    ben: {e0}
    cara: {e0}
Event 2:
  e0* [no change]; possible in {w0,w1,w2,w3,w5,w7}
  Observability of event worlds:
    ann: {e0}
    ben: {e0}
    cara: {e0}

An agent knows a fact if the fact is true in every world the agent considers possible after all events.

Queried facts in order: f2, f4.
For each queried fact, give the sorted, comma-separated list of agents that know the fact, facts separated by ' | '. Use '-' if no agent knows that fact.
Example format: 'ann,ben | -'.
**Answer:**
- | cara

### Example 2
**Prompt:**
We model knowledge over possible worlds. Agents: {ann, ben, cara}. Facts: {f1, f2, f3, f4}.

Initial model, actual world marked *:
  w0*: f1=T f2=T f3=F f4=F
  w1 : f1=T f2=F f3=F f4=F
  w2 : f1=F f2=F f3=T f4=F
  w3 : f1=T f2=F f3=T f4=T
  w4 : f1=F f2=F f3=T f4=T
  w5 : f1=T f2=F f3=T f4=F
  w6 : f1=F f2=F f3=T f4=T
  w7 : f1=F f2=F f3=F f4=T
Observability (worlds an agent cannot distinguish):
  ann: {w0,w1,w2,w3,w4}, {w5,w7}, {w6}
  ben: {w0,w1,w3}, {w2}, {w4,w6}, {w5}, {w7}
  cara: {w0,w1,w2,w3,w4,w5,w6,w7}

Event sequence:
Event 1:
  e0* [no change]; possible in {w2,w1,w3,w0,w7,w6,w4}
  Observability of event worlds:
    ann: {e0}
    ben: {e0}
    cara: {e0}
Event 2:
  e0* [f3->F]; possible in {w2,w5,w3,w1,w6,w0,w7}
  Observability of event worlds:
    ann: {e0}
    ben: {e0}
    cara: {e0}

An agent knows a fact if the fact is true in every world the agent considers possible after all events.

Queried facts in order: f1, f3.
For each queried fact, give the sorted, comma-separated list of agents that know the fact, facts separated by ' | '. Use '-' if no agent knows that fact.
Example format: 'ann,ben | -'.
**Answer:**
ben | -

## Level 5
### Example 1
**Prompt:**
We model knowledge over possible worlds. Agents: {ann, ben, cara, dan}. Facts: {f1, f2, f3, f4, f5, f6}.

Initial model, actual world marked *:
  w0*: f1=T f2=T f3=T f4=F f5=T f6=F
  w1 : f1=T f2=F f3=T f4=T f5=T f6=F
  w2 : f1=T f2=F f3=T f4=T f5=T f6=T
  w3 : f1=F f2=T f3=F f4=T f5=T f6=T
  w4 : f1=F f2=F f3=F f4=T f5=T f6=F
  w5 : f1=T f2=T f3=T f4=F f5=T f6=T
  w6 : f1=T f2=F f3=F f4=F f5=T f6=F
  w7 : f1=T f2=F f3=T f4=T f5=F f6=T
  w8 : f1=T f2=F f3=F f4=F f5=T f6=T
  w9 : f1=F f2=T f3=F f4=F f5=T f6=T
  w10 : f1=T f2=T f3=F f4=T f5=F f6=T
  w11 : f1=F f2=F f3=F f4=T f5=T f6=F
  w12 : f1=F f2=F f3=T f4=T f5=F f6=F
  w13 : f1=T f2=T f3=T f4=T f5=F f6=T
Observability (worlds an agent cannot distinguish):
  ann: {w0,w3}, {w1,w2,w12}, {w4,w5,w7,w8}, {w6,w9,w10}, {w11}, {w13}
  ben: {w0,w1,w2,w3,w4,w6,w8,w10,w13}, {w5,w7,w11}, {w9}, {w12}
  cara: {w0,w2,w4}, {w1,w3,w5,w10,w12}, {w6}, {w7,w8}, {w9}, {w11,w13}
  dan: {w0,w1,w4,w11,w12}, {w2,w5,w6,w10}, {w3}, {w7,w8,w9,w13}

Event sequence:
Event 1:
  e0  [no change]; possible in {w10,w9,w1,w8,w7,w6,w13,w3,w0,w4,w2}
  e1* [f6->F]; possible in {w0,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13}
  Observability of event worlds:
    ann: {e0}, {e1}
    ben: {e0,e1}
    cara: {e0,e1}
    dan: {e0}, {e1}
Event 2:
  e0* [f2->T, f4->F]; possible in {w11,w12,w13,w0,w8,w9,w10,w5,w7,w6}
  e1  [f5->F, f4->F]; possible in {w4,w7,w13,w11,w8,w0,w9,w2,w5}
  Observability of event worlds:
    ann: {e0}, {e1}
    ben: {e0}, {e1}
    cara: {e0}, {e1}
    dan: {e0}, {e1}
Event 3:
  e0  [f1->T]; possible in {w0,w1,w2,w12,w5,w3,w8,w7,w13,w4,w6,w9}
  e1* [f6->F]; possible in {w13,w3,w11,w0,w6,w2,w7,w1,w9,w5}
  Observability of event worlds:
    ann: {e0}, {e1}
    ben: {e0}, {e1}
    cara: {e0,e1}
    dan: {e0}, {e1}

An agent knows a fact if the fact is true in every world the agent considers possible after all events.

Queried facts in order: f3, f5.
For each queried fact, give the sorted, comma-separated list of agents that know the fact, facts separated by ' | '. Use '-' if no agent knows that fact.
Example format: 'ann,ben | -'.
**Answer:**
ann,cara | ann,cara,dan

### Example 2
**Prompt:**
We model knowledge over possible worlds. Agents: {ann, ben, cara, dan}. Facts: {f1, f2, f3, f4, f5, f6}.

Initial model, actual world marked *:
  w0*: f1=F f2=T f3=T f4=F f5=F f6=T
  w1 : f1=F f2=T f3=T f4=F f5=T f6=T
  w2 : f1=F f2=T f3=T f4=F f5=T f6=T
  w3 : f1=F f2=T f3=T f4=F f5=T f6=T
  w4 : f1=F f2=F f3=T f4=F f5=T f6=F
  w5 : f1=F f2=T f3=F f4=T f5=T f6=F
  w6 : f1=T f2=F f3=T f4=T f5=F f6=T
  w7 : f1=F f2=F f3=T f4=F f5=F f6=F
  w8 : f1=F f2=F f3=F f4=T f5=F f6=F
  w9 : f1=T f2=T f3=F f4=T f5=F f6=F
  w10 : f1=F f2=F f3=T f4=F f5=T f6=T
  w11 : f1=F f2=T f3=F f4=T f5=F f6=T
  w12 : f1=T f2=T f3=F f4=F f5=F f6=F
  w13 : f1=T f2=F f3=F f4=T f5=F f6=T
Observability (worlds an agent cannot distinguish):
  ann: {w0,w1,w2,w3,w8}, {w4,w6,w10}, {w5}, {w7,w9}, {w11}, {w12}, {w13}
  ben: {w0,w1,w2,w3,w4,w5,w6,w7,w8,w11,w12}, {w9,w10}, {w13}
  cara: {w0,w1,w2,w4,w5}, {w3,w9,w10}, {w6,w7}, {w8,w13}, {w11}, {w12}
  dan: {w0,w1,w2,w3,w5}, {w4,w6}, {w7,w10,w13}, {w8,w11}, {w9}, {w12}

Event sequence:
Event 1:
  e0  [f4->T, f1->F]; possible in {w3,w13,w7,w5,w4,w0,w1,w6,w11,w10,w2,w9,w12,w8}
  e1* [f2->F]; possible in {w5,w7,w6,w0,w9,w11,w4,w2,w10,w3,w8}
  Observability of event worlds:
    ann: {e0,e1}
    ben: {e0,e1}
    cara: {e0}, {e1}
    dan: {e0}, {e1}
Event 2:
  e0  [f2->T, f5->F]; possible in {w10,w2,w13,w4,w11,w5,w1,w6,w8,w3,w12,w0,w7,w9}
  e1* [f6->T, f2->F]; possible in {w0,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13}
  Observability of event worlds:
    ann: {e0,e1}
    ben: {e0}, {e1}
    cara: {e0}, {e1}
    dan: {e0}, {e1}
Event 3:
  e0* [f1->T]; possible in {w7,w9,w8,w1,w5,w10,w0,w2,w4}
  e1  [no change]; possible in {w6,w1,w7,w8,w12,w3,w0,w11}
  Observability of event worlds:
    ann: {e0,e1}
    ben: {e0}, {e1}
    cara: {e0}, {e1}
    dan: {e0}, {e1}

An agent knows a fact if the fact is true in every world the agent considers possible after all events.

Queried facts in order: f1, f5.
For each queried fact, give the sorted, comma-separated list of agents that know the fact, facts separated by ' | '. Use '-' if no agent knows that fact.
Example format: 'ann,ben | -'.
**Answer:**
ben,cara,dan | -


## Level 0
### Example 1
Prompt:
In a short dialogue each utterance mentions one or both of two people. Rank the people mentioned in an utterance by obliqueness: the subject ranks above the direct object (a lone subject is the only mention). The backward-looking center of an utterance is the highest-ranked person of the previous utterance that is also mentioned in the current one.
For every utterance from the second onward, label its transition:
- continue: the backward-looking center is the highest-ranked person of the current utterance and equals the backward-looking center of the previous utterance;
- retain: it is the highest-ranked person of the current utterance but differs from the previous backward-looking center (the second utterance, having no previous center, is labeled retain in this case);
- shift otherwise.
Pronouns refer to exactly one person and resolve by gender.

Dialogue:
1. she warned Tomas.
2. Tomas congratulated Ingrid.
3. she arrived.

Give one label per utterance from the second onward, in order, as a comma-separated sequence. Example format: continue,shift,retain
Answer:
shift,continue

### Example 2
Prompt:
In a short dialogue each utterance mentions one or both of two people. Rank the people mentioned in an utterance by obliqueness: the subject ranks above the direct object (a lone subject is the only mention). The backward-looking center of an utterance is the highest-ranked person of the previous utterance that is also mentioned in the current one.
For every utterance from the second onward, label its transition:
- continue: the backward-looking center is the highest-ranked person of the current utterance and equals the backward-looking center of the previous utterance;
- retain: it is the highest-ranked person of the current utterance but differs from the previous backward-looking center (the second utterance, having no previous center, is labeled retain in this case);
- shift otherwise.
Pronouns refer to exactly one person and resolve by gender.

Dialogue:
1. he called Sofia.
2. she warned Rashid.
3. he paused.

Give one label per utterance from the second onward, in order, as a comma-separated sequence. Example format: continue,shift,retain
Answer:
shift,continue

## Level 2
### Example 1
Prompt:
In a short dialogue each utterance mentions one or both of two people. Rank the people mentioned in an utterance by obliqueness: the subject ranks above the direct object (a lone subject is the only mention). The backward-looking center of an utterance is the highest-ranked person of the previous utterance that is also mentioned in the current one.
For every utterance from the second onward, label its transition:
- continue: the backward-looking center is the highest-ranked person of the current utterance and equals the backward-looking center of the previous utterance;
- retain: it is the highest-ranked person of the current utterance but differs from the previous backward-looking center (the second utterance, having no previous center, is labeled retain in this case);
- shift otherwise.
Pronouns refer to exactly one person and resolve by gender.

Dialogue:
1. he praised her.
2. Priya warned Victor.
3. she praised Victor.
4. Priya thanked him.
5. he left.

Give one label per utterance from the second onward, in order, as a comma-separated sequence. Example format: continue,shift,retain
Answer:
shift,retain,continue,retain

### Example 2
Prompt:
In a short dialogue each utterance mentions one or both of two people. Rank the people mentioned in an utterance by obliqueness: the subject ranks above the direct object (a lone subject is the only mention). The backward-looking center of an utterance is the highest-ranked person of the previous utterance that is also mentioned in the current one.
For every utterance from the second onward, label its transition:
- continue: the backward-looking center is the highest-ranked person of the current utterance and equals the backward-looking center of the previous utterance;
- retain: it is the highest-ranked person of the current utterance but differs from the previous backward-looking center (the second utterance, having no previous center, is labeled retain in this case);
- shift otherwise.
Pronouns refer to exactly one person and resolve by gender.

Dialogue:
1. she praised Victor.
2. he congratulated her.
3. Victor waved.
4. Victor called Priya.
5. Victor phoned her.

Give one label per utterance from the second onward, in order, as a comma-separated sequence. Example format: continue,shift,retain
Answer:
shift,retain,continue,continue

## Level 5
### Example 1
Prompt:
In a short dialogue each utterance mentions one or both of two people. Rank the people mentioned in an utterance by obliqueness: the subject ranks above the direct object (a lone subject is the only mention). The backward-looking center of an utterance is the highest-ranked person of the previous utterance that is also mentioned in the current one.
For every utterance from the second onward, label its transition:
- continue: the backward-looking center is the highest-ranked person of the current utterance and equals the backward-looking center of the previous utterance;
- retain: it is the highest-ranked person of the current utterance but differs from the previous backward-looking center (the second utterance, having no previous center, is labeled retain in this case);
- shift otherwise.
Pronouns refer to exactly one person and resolve by gender.

Dialogue:
1. he invited her.
2. she visited him.
3. Priya phoned him.
4. she arrived.
5. she warned him.
6. she phoned him.
7. he arrived.
8. Priya called Victor.

Give one label per utterance from the second onward, in order, as a comma-separated sequence. Example format: continue,shift,retain
Answer:
shift,retain,continue,continue,continue,retain,shift

### Example 2
Prompt:
In a short dialogue each utterance mentions one or both of two people. Rank the people mentioned in an utterance by obliqueness: the subject ranks above the direct object (a lone subject is the only mention). The backward-looking center of an utterance is the highest-ranked person of the previous utterance that is also mentioned in the current one.
For every utterance from the second onward, label its transition:
- continue: the backward-looking center is the highest-ranked person of the current utterance and equals the backward-looking center of the previous utterance;
- retain: it is the highest-ranked person of the current utterance but differs from the previous backward-looking center (the second utterance, having no previous center, is labeled retain in this case);
- shift otherwise.
Pronouns refer to exactly one person and resolve by gender.

Dialogue:
1. she praised him.
2. she invited him.
3. Ivan warned her.
4. he paused.
5. he waited.
6. he left.
7. she invited him.
8. she congratulated him.

Give one label per utterance from the second onward, in order, as a comma-separated sequence. Example format: continue,shift,retain
Answer:
retain,shift,retain,continue,continue,shift,retain


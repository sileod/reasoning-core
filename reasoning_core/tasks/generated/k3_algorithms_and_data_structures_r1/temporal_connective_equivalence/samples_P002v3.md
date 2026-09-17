# Samples: temporal_connective_equivalence (P002v3)


## Level 0


### Example 1

Prompt:

An editor is restructuring a timing report. Do the original and rewrite permit exactly the same timelines?
Each named event occurs once on a real-valued timeline. A punctual event has start=end; a durative event has start<end and occupies its entire closed interval. Events: the alarm: punctual; the rainfall: durative.
Use these precise editorial conventions (also for punctual events): before means end(A)<start(B); after reverses before. Until means end(A)=start(B); since means start(A)=end(B), with no requirement about the present. No sooner A than B means end(A)=start(B), not a positive delay. While/overlap means the closed intervals intersect, even at one endpoint. The phrases 'just as' and 'the instant' mean equality. Negation denies only its parenthesized claim, never event existence. 'Both' is conjunction; 'at least one' is inclusive disjunction. No other temporal facts or implications from narrative order are assumed. Compare all endpoint orderings, allowing ties, rather than just one plausible timeline.
Original: before the alarm, the rainfall had finished.
Rewrite: the alarm was after the rainfall.
Reply yes if equivalent and no otherwise. Format example: yes. Give only the label.

Answer:

yes

### Example 2

Prompt:

An editor is restructuring a timing report. Do the original and rewrite permit exactly the same timelines?
Each named event occurs once on a real-valued timeline. A punctual event has start=end; a durative event has start<end and occupies its entire closed interval. Events: the click: punctual; the rainfall: durative.
Use these precise editorial conventions (also for punctual events): before means end(A)<start(B); after reverses before. Until means end(A)=start(B); since means start(A)=end(B), with no requirement about the present. No sooner A than B means end(A)=start(B), not a positive delay. While/overlap means the closed intervals intersect, even at one endpoint. The phrases 'just as' and 'the instant' mean equality. Negation denies only its parenthesized claim, never event existence. 'Both' is conjunction; 'at least one' is inclusive disjunction. No other temporal facts or implications from narrative order are assumed. Compare all endpoint orderings, allowing ties, rather than just one plausible timeline.
Original: after the click, the rainfall began.
Rewrite: the click ended just as the rainfall began.
Reply yes if equivalent and no otherwise. Format example: yes. Give only the label.

Answer:

no

## Level 2


### Example 1

Prompt:

An editor is restructuring a timing report. Do the original and rewrite permit exactly the same timelines?
Each named event occurs once on a real-valued timeline. A punctual event has start=end; a durative event has start<end and occupies its entire closed interval. Events: the signal: punctual; the broadcast: durative.
Use these precise editorial conventions (also for punctual events): before means end(A)<start(B); after reverses before. Until means end(A)=start(B); since means start(A)=end(B), with no requirement about the present. No sooner A than B means end(A)=start(B), not a positive delay. While/overlap means the closed intervals intersect, even at one endpoint. The phrases 'just as' and 'the instant' mean equality. Negation denies only its parenthesized claim, never event existence. 'Both' is conjunction; 'at least one' is inclusive disjunction. No other temporal facts or implications from narrative order are assumed. Compare all endpoint orderings, allowing ties, rather than just one plausible timeline.
Original: at least one holds: (the broadcast was after the signal) or (the signal occurred while the broadcast occurred).
Rewrite: at least one holds: (both (it is not true that (before the broadcast, the signal had finished)) and (it is not true that (after the broadcast, the signal began))) or (before the broadcast, the signal had finished).
Reply yes if equivalent and no otherwise. Format example: yes. Give only the label.

Answer:

yes

### Example 2

Prompt:

An editor is restructuring a timing report. Do the original and rewrite permit exactly the same timelines?
Each named event occurs once on a real-valued timeline. A punctual event has start=end; a durative event has start<end and occupies its entire closed interval. Events: the signal: punctual; the rehearsal: durative.
Use these precise editorial conventions (also for punctual events): before means end(A)<start(B); after reverses before. Until means end(A)=start(B); since means start(A)=end(B), with no requirement about the present. No sooner A than B means end(A)=start(B), not a positive delay. While/overlap means the closed intervals intersect, even at one endpoint. The phrases 'just as' and 'the instant' mean equality. Negation denies only its parenthesized claim, never event existence. 'Both' is conjunction; 'at least one' is inclusive disjunction. No other temporal facts or implications from narrative order are assumed. Compare all endpoint orderings, allowing ties, rather than just one plausible timeline.
Original: it is not true that (at least one holds: (before the rehearsal, the signal had finished) or (after the signal, the rehearsal began)).
Rewrite: both (it is not true that (the rehearsal was after the signal)) and (it is not true that (the signal was after the rehearsal)).
Reply yes if equivalent and no otherwise. Format example: yes. Give only the label.

Answer:

no

## Level 5


### Example 1

Prompt:

An editor is restructuring a timing report. Do the original and rewrite permit exactly the same timelines?
Each named event occurs once on a real-valued timeline. A punctual event has start=end; a durative event has start<end and occupies its entire closed interval. Events: the alarm: punctual; the repair: durative; the bell: punctual.
Use these precise editorial conventions (also for punctual events): before means end(A)<start(B); after reverses before. Until means end(A)=start(B); since means start(A)=end(B), with no requirement about the present. No sooner A than B means end(A)=start(B), not a positive delay. While/overlap means the closed intervals intersect, even at one endpoint. The phrases 'just as' and 'the instant' mean equality. Negation denies only its parenthesized claim, never event existence. 'Both' is conjunction; 'at least one' is inclusive disjunction. No other temporal facts or implications from narrative order are assumed. Compare all endpoint orderings, allowing ties, rather than just one plausible timeline.
Original: it is not true that (at least one holds: (it is not true that (at least one holds: (it is not true that (the bell was before the repair)) or (it is not true that (the alarm was before the bell)))) or (both (no sooner had the bell ended than the alarm began) and (the bell was after the repair))).
Rewrite: both (at least one holds: (it is not true that (after the alarm, the bell began)) or (it is not true that (after the bell, the repair began))) and (at least one holds: (it is not true that (the alarm began just as the bell ended)) or (it is not true that (before the bell, the repair had finished))).
Reply yes if equivalent and no otherwise. Format example: yes. Give only the label.

Answer:

yes

### Example 2

Prompt:

An editor is restructuring a timing report. Do the original and rewrite permit exactly the same timelines?
Each named event occurs once on a real-valued timeline. A punctual event has start=end; a durative event has start<end and occupies its entire closed interval. Events: the flash: punctual; the click: punctual; the rehearsal: durative.
Use these precise editorial conventions (also for punctual events): before means end(A)<start(B); after reverses before. Until means end(A)=start(B); since means start(A)=end(B), with no requirement about the present. No sooner A than B means end(A)=start(B), not a positive delay. While/overlap means the closed intervals intersect, even at one endpoint. The phrases 'just as' and 'the instant' mean equality. Negation denies only its parenthesized claim, never event existence. 'Both' is conjunction; 'at least one' is inclusive disjunction. No other temporal facts or implications from narrative order are assumed. Compare all endpoint orderings, allowing ties, rather than just one plausible timeline.
Original: it is not true that (at least one holds: (at least one holds: (it is not true that (no sooner had the rehearsal ended than the flash began)) or (it is not true that (the rehearsal was before the click))) or (both (the click occurred while the rehearsal occurred) and (it is not true that (the flash was after the click)))).
Rewrite: at least one holds: (both (the flash began just as the rehearsal ended) and (after the rehearsal, the click began)) or (at least one holds: (it is not true that (the rehearsal overlapped the click)) or (before the flash, the click had finished)).
Reply yes if equivalent and no otherwise. Format example: yes. Give only the label.

Answer:

no

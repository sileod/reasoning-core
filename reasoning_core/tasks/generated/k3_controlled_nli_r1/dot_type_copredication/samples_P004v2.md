## Level 0

Check a sentence in a toy semantic lexicon; use only the listed meanings, not everyday usage. Each noun has the two starting facets A and B shown below. A predicate demands at least one of its listed types (or means alternatives).
A starting facet meets a demand when it can reach a demanded type through zero or more listed directed coercion arrows. Arrows compose but cannot be reversed; there are no other coercions. All coordinated predicates must be supported by the SAME starting facet. Test each predicate independently from that facet: their paths need not be the same and one predicate does not change the starting facet for another. Use graph reachability followed by intersection of the predicates' allowed starting facets.

Lexicon:
newspaper: A = record; B = performance
exhibition: A = service; B = performance

Coercions:
record -> service; performance -> collection; record -> collection

Predicate Demands:
'is original': performance or sound
'is heavy': process

Sentence:
The newspaper is heavy and is original.

Which starting facets of the sentence's noun support the whole coordination? Options: A (only A), B (only B), both (each works separately), neither (infelicitous). For example, if only B supports every predicate, reply B. Output exactly one option without explanation.

Answer: neither

## Level 0

Check a sentence in a toy semantic lexicon; use only the listed meanings, not everyday usage. Each noun has the two starting facets A and B shown below. A predicate demands at least one of its listed types (or means alternatives).
A starting facet meets a demand when it can reach a demanded type through zero or more listed directed coercion arrows. Arrows compose but cannot be reversed; there are no other coercions. All coordinated predicates must be supported by the SAME starting facet. Test each predicate independently from that facet: their paths need not be the same and one predicate does not change the starting facet for another. Use graph reachability followed by intersection of the predicates' allowed starting facets.

Lexicon:
book: A = artifact; B = record
report: A = food; B = performance

Coercions:
food -> image; food -> institution; performance -> image

Predicate Demands:
'is available': performance or record
'is popular': performance

Sentence:
The report is popular and is available.

Which starting facets of the sentence's noun support the whole coordination? Options: A (only A), B (only B), both (each works separately), neither (infelicitous). For example, if only B supports every predicate, reply B. Output exactly one option without explanation.

Answer: B

## Level 2

Check a sentence in a toy semantic lexicon; use only the listed meanings, not everyday usage. Each noun has the two starting facets A and B shown below. A predicate demands at least one of its listed types (or means alternatives).
A starting facet meets a demand when it can reach a demanded type through zero or more listed directed coercion arrows. Arrows compose but cannot be reversed; there are no other coercions. All coordinated predicates must be supported by the SAME starting facet. Test each predicate independently from that facet: their paths need not be the same and one predicate does not change the starting facet for another. Use graph reachability followed by intersection of the predicates' allowed starting facets.

Lexicon:
newspaper: A = process; B = record
report: A = service; B = content

Coercions:
service -> value; value -> record; content -> person; person -> event; event -> image; record -> institution; event -> institution

Predicate Demands:
'is original': institution
'is unusual': person or role or value
'is informative': institution

Sentence:
The report is informative and is unusual and is original.

Which starting facets of the sentence's noun support the whole coordination? Options: A (only A), B (only B), both (each works separately), neither (infelicitous). For example, if only B supports every predicate, reply B. Output exactly one option without explanation.

Answer: both

## Level 2

Check a sentence in a toy semantic lexicon; use only the listed meanings, not everyday usage. Each noun has the two starting facets A and B shown below. A predicate demands at least one of its listed types (or means alternatives).
A starting facet meets a demand when it can reach a demanded type through zero or more listed directed coercion arrows. Arrows compose but cannot be reversed; there are no other coercions. All coordinated predicates must be supported by the SAME starting facet. Test each predicate independently from that facet: their paths need not be the same and one predicate does not change the starting facet for another. Use graph reachability followed by intersection of the predicates' allowed starting facets.

Lexicon:
book: A = performance; B = value
film: A = content; B = image

Coercions:
food -> sound; institution -> image; physical -> institution; performance -> physical; sound -> design; value -> food

Predicate Demands:
'is unusual': design or image or record
'is original': food
'is lengthy': image

Sentence:
The book is lengthy and is original and is unusual.

Which starting facets of the sentence's noun support the whole coordination? Options: A (only A), B (only B), both (each works separately), neither (infelicitous). For example, if only B supports every predicate, reply B. Output exactly one option without explanation.

Answer: neither

## Level 5

Check a sentence in a toy semantic lexicon; use only the listed meanings, not everyday usage. Each noun has the two starting facets A and B shown below. A predicate demands at least one of its listed types (or means alternatives).
A starting facet meets a demand when it can reach a demanded type through zero or more listed directed coercion arrows. Arrows compose but cannot be reversed; there are no other coercions. All coordinated predicates must be supported by the SAME starting facet. Test each predicate independently from that facet: their paths need not be the same and one predicate does not change the starting facet for another. Use graph reachability followed by intersection of the predicates' allowed starting facets.

Lexicon:
exhibition: A = value; B = location
school: A = value; B = material

Coercions:
process -> performance; service -> content; location -> process; material -> location; physical -> process; performance -> role; performance -> person; collection -> record; event -> record; content -> food; collection -> event; location -> physical; value -> service; food -> collection; physical -> performance; person -> role; food -> event; value -> content

Predicate Demands:
'is popular': process
'is unusual': image or physical
'is informative': collection or location
'is old': artifact or person or role

Sentence:
The school is old and is informative and is popular and is unusual.

Which starting facets of the sentence's noun support the whole coordination? Options: A (only A), B (only B), both (each works separately), neither (infelicitous). For example, if only B supports every predicate, reply B. Output exactly one option without explanation.

Answer: B

## Level 5

Check a sentence in a toy semantic lexicon; use only the listed meanings, not everyday usage. Each noun has the two starting facets A and B shown below. A predicate demands at least one of its listed types (or means alternatives).
A starting facet meets a demand when it can reach a demanded type through zero or more listed directed coercion arrows. Arrows compose but cannot be reversed; there are no other coercions. All coordinated predicates must be supported by the SAME starting facet. Test each predicate independently from that facet: their paths need not be the same and one predicate does not change the starting facet for another. Use graph reachability followed by intersection of the predicates' allowed starting facets.

Lexicon:
school: A = location; B = value
exhibition: A = event; B = value

Coercions:
event -> message; collection -> food; person -> image; material -> person; value -> design; design -> collection; message -> role; service -> performance; role -> service; performance -> content; food -> material; content -> institution

Predicate Demands:
'is unusual': image or role
'is popular': performance or person
'is lengthy': content or institution
'is available': institution

Sentence:
The exhibition is unusual and is available and is lengthy and is popular.

Which starting facets of the sentence's noun support the whole coordination? Options: A (only A), B (only B), both (each works separately), neither (infelicitous). For example, if only B supports every predicate, reply B. Output exactly one option without explanation.

Answer: A

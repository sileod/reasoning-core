# Samples for trick_taking_adjudication (P002v2)

## Level 0

### Legal example

Adjudicate this club's trick-taking round. Cards use suit C=clubs, D=diamonds, H=hearts, S=spades followed by rank (T means ten). Every card is unique; only the dealt cards are in play. No cards are drawn or returned.
The announced leader of each trick is chosen independently, NOT by the previous winner. Play proceeds North, East, South, West cyclically from that leader. The first card sets the lead suit. Follow that suit if held immediately before playing; otherwise any card is legal. The leader may play any held card.
Playing off-suit while able to follow is a revoke: subtract 5 points from that player, and their card cannot win this trick. It is still removed from their hand and captured by the winner. Other cards remain eligible. No other penalty applies.
Use the standard maximum-card scan: among eligible cards, any trump beats any non-trump; if none is trump, only the lead suit can win. The strongest card in that suit wins. Each trick gives NEW, independent strongest-to-weakest rank strings for each suit; ordinary card ranks do not apply. Trump=none means no trump.
Initially North holds CT, DT, HT, SJ.
Initially East holds CA, HA, S9, SA.
Initially South holds CJ, DA, SQ, ST.
Initially West holds D9, DQ, H9, HJ.
Trick 1: trump=none; C:TQ9AKJ; D:KJQT9A; H:JTKQ9A; S:JTAK9Q. Plays in order: West=DQ, North=DT, East=CA, South=CJ.
Trick 2: trump=S; C:QJATK9; D:K9TJQA; H:AKTJ9Q; S:9KQTJA. Plays in order: West=HJ.
The last trick is unfinished. List all legal plays for North now, suits in C,D,H,S order and ranks strongest first under this trick's own suit orders. Answer as a bracketed list, for example [CQ, C9, HA].

Answer: [HT]

### Winner example

Adjudicate this club's trick-taking round. Cards use suit C=clubs, D=diamonds, H=hearts, S=spades followed by rank (T means ten). Every card is unique; only the dealt cards are in play. No cards are drawn or returned.
The announced leader of each trick is chosen independently, NOT by the previous winner. Play proceeds North, East, South, West cyclically from that leader. The first card sets the lead suit. Follow that suit if held immediately before playing; otherwise any card is legal. The leader may play any held card.
Playing off-suit while able to follow is a revoke: subtract 8 points from that player, and their card cannot win this trick. It is still removed from their hand and captured by the winner. Other cards remain eligible. No other penalty applies.
Use the standard maximum-card scan: among eligible cards, any trump beats any non-trump; if none is trump, only the lead suit can win. The strongest card in that suit wins. Each trick gives NEW, independent strongest-to-weakest rank strings for each suit; ordinary card ranks do not apply. Trump=none means no trump.
Initially North holds CK, DT, HQ, S9.
Initially East holds C9, DK, SK, SQ.
Initially South holds CT, HK, SA, ST.
Initially West holds H9, HA, HJ, HT.
Trick 1: trump=S; C:JKA9TQ; D:QT9AKJ; H:A9TKJQ; S:AK9QTJ. Plays in order: West=HA, North=DT, East=SQ, South=HK.
Trick 2: trump=S; C:ATQKJ9; D:KA9TQJ; H:JK9QAT; S:TK9AJQ. Plays in order: South=CT, West=HJ, North=CK, East=C9.
List every trick's winner in chronological order. Answer as a bracketed list of names, for example [East, South].

Answer: [East, South]

### Points example

Adjudicate this club's trick-taking round. Cards use suit C=clubs, D=diamonds, H=hearts, S=spades followed by rank (T means ten). Every card is unique; only the dealt cards are in play. No cards are drawn or returned.
The announced leader of each trick is chosen independently, NOT by the previous winner. Play proceeds North, East, South, West cyclically from that leader. The first card sets the lead suit. Follow that suit if held immediately before playing; otherwise any card is legal. The leader may play any held card.
Playing off-suit while able to follow is a revoke: subtract 11 points from that player, and their card cannot win this trick. It is still removed from their hand and captured by the winner. Other cards remain eligible. No other penalty applies.
Use the standard maximum-card scan: among eligible cards, any trump beats any non-trump; if none is trump, only the lead suit can win. The strongest card in that suit wins. Each trick gives NEW, independent strongest-to-weakest rank strings for each suit; ordinary card ranks do not apply. Trump=none means no trump.
All players start at zero. The winner captures all four cards. Each card is worth its position counted from weakest in its OWN suit's order FOR THAT TRICK: weakest=1, next=2, etc. Add captured values and subtract that player's revoke penalties. Negative totals are allowed. Unplayed cards score nothing.
Initially North holds DJ, H9, HA, HJ.
Initially East holds C9, DQ, DT, SQ.
Initially South holds CA, CQ, DA, S9.
Initially West holds CJ, D9, HQ, HT.
Trick 1: trump=none; C:9ATKQJ; D:JTAK9Q; H:QTKA9J; S:TQJ9KA. Plays in order: West=CJ, North=HA, East=C9, South=CQ.
Trick 2: trump=S; C:JTAK9Q; D:QTK9AJ; H:TA9JKQ; S:QAKJ9T. Plays in order: West=D9, North=DJ, East=DQ, South=CA.
Total each player's points for the shown round. Answer as a bracketed list of integers in North, East, South, West order, for example [12, -3, 8, 0].

Answer: [0, 26, -11, 0]

## Level 2

### Legal example

Adjudicate this club's trick-taking round. Cards use suit C=clubs, D=diamonds, H=hearts, S=spades followed by rank (T means ten). Every card is unique; only the dealt cards are in play. No cards are drawn or returned.
The announced leader of each trick is chosen independently, NOT by the previous winner. Play proceeds North, East, South, West cyclically from that leader. The first card sets the lead suit. Follow that suit if held immediately before playing; otherwise any card is legal. The leader may play any held card.
Playing off-suit while able to follow is a revoke: subtract 4 points from that player, and their card cannot win this trick. It is still removed from their hand and captured by the winner. Other cards remain eligible. No other penalty applies.
Use the standard maximum-card scan: among eligible cards, any trump beats any non-trump; if none is trump, only the lead suit can win. The strongest card in that suit wins. Each trick gives NEW, independent strongest-to-weakest rank strings for each suit; ordinary card ranks do not apply. Trump=none means no trump.
Initially North holds C9, H9, HA, HJ, ST.
Initially East holds CJ, DA, DT, SJ, SQ.
Initially South holds CQ, HK, HQ, S9, SA.
Initially West holds CA, CT, D9, DK, HT.
Trick 1: trump=H; C:AQ9TJK; D:QT9JKA; H:TAQJ9K; S:ATQJ9K. Plays in order: South=HK, West=HT, North=C9, East=SQ.
Trick 2: trump=D; C:9JTAKQ; D:TAJQK9; H:TJQ9AK; S:TAKJ9Q. Plays in order: South=CQ, West=CA, North=ST, East=DA.
Trick 3: trump=none; C:9JTKAQ; D:QAJKT9; H:9AQJKT; S:JTQKA9. Plays in order: West=DK.
The last trick is unfinished. List all legal plays for North now, suits in C,D,H,S order and ranks strongest first under this trick's own suit orders. Answer as a bracketed list, for example [CQ, C9, HA].

Answer: [H9, HA, HJ]

### Winner example

Adjudicate this club's trick-taking round. Cards use suit C=clubs, D=diamonds, H=hearts, S=spades followed by rank (T means ten). Every card is unique; only the dealt cards are in play. No cards are drawn or returned.
The announced leader of each trick is chosen independently, NOT by the previous winner. Play proceeds North, East, South, West cyclically from that leader. The first card sets the lead suit. Follow that suit if held immediately before playing; otherwise any card is legal. The leader may play any held card.
Playing off-suit while able to follow is a revoke: subtract 11 points from that player, and their card cannot win this trick. It is still removed from their hand and captured by the winner. Other cards remain eligible. No other penalty applies.
Use the standard maximum-card scan: among eligible cards, any trump beats any non-trump; if none is trump, only the lead suit can win. The strongest card in that suit wins. Each trick gives NEW, independent strongest-to-weakest rank strings for each suit; ordinary card ranks do not apply. Trump=none means no trump.
Initially North holds C9, CT, D9, DQ, HK.
Initially East holds DT, H9, HA, SJ, ST.
Initially South holds CJ, DA, DK, HQ, HT.
Initially West holds CQ, DJ, HJ, SA, SQ.
Trick 1: trump=S; C:9TJAQK; D:QTAK9J; H:9TAQJK; S:AKJ9TQ. Plays in order: East=HA, South=DK, West=HJ, North=C9.
Trick 2: trump=C; C:JAKQT9; D:KTQAJ9; H:KTA9JQ; S:TQ9KJA. Plays in order: South=HQ, West=CQ, North=CT, East=H9.
Trick 3: trump=S; C:JT9QKA; D:AQ9KJT; H:KQJAT9; S:J9AKTQ. Plays in order: North=D9, East=DT, South=CJ, West=SA.
List every trick's winner in chronological order. Answer as a bracketed list of names, for example [East, South].

Answer: [East, West, North]

### Points example

Adjudicate this club's trick-taking round. Cards use suit C=clubs, D=diamonds, H=hearts, S=spades followed by rank (T means ten). Every card is unique; only the dealt cards are in play. No cards are drawn or returned.
The announced leader of each trick is chosen independently, NOT by the previous winner. Play proceeds North, East, South, West cyclically from that leader. The first card sets the lead suit. Follow that suit if held immediately before playing; otherwise any card is legal. The leader may play any held card.
Playing off-suit while able to follow is a revoke: subtract 12 points from that player, and their card cannot win this trick. It is still removed from their hand and captured by the winner. Other cards remain eligible. No other penalty applies.
Use the standard maximum-card scan: among eligible cards, any trump beats any non-trump; if none is trump, only the lead suit can win. The strongest card in that suit wins. Each trick gives NEW, independent strongest-to-weakest rank strings for each suit; ordinary card ranks do not apply. Trump=none means no trump.
All players start at zero. The winner captures all four cards. Each card is worth its position counted from weakest in its OWN suit's order FOR THAT TRICK: weakest=1, next=2, etc. Add captured values and subtract that player's revoke penalties. Negative totals are allowed. Unplayed cards score nothing.
Initially North holds CQ, DA, DJ, DT, SA.
Initially East holds CK, D9, DQ, HT, SJ.
Initially South holds CA, DK, HA, S9, SQ.
Initially West holds H9, HJ, HK, HQ, SK.
Trick 1: trump=C; C:K9QJAT; D:K9AQJT; H:AJ9QKT; S:Q9KJTA. Plays in order: West=SK, North=DA, East=SJ, South=CA.
Trick 2: trump=S; C:9AQTKJ; D:TQAK9J; H:TQJKA9; S:JT9QKA. Plays in order: North=SA, East=CK, South=SQ, West=HQ.
Trick 3: trump=C; C:AQ9JKT; D:JKA9TQ; H:9KQATJ; S:QTJA9K. Plays in order: North=DJ, East=DQ, South=DK, West=H9.
Total each player's points for the shown round. Answer as a bracketed list of integers in North, East, South, West order, for example [12, -3, 8, 0].

Answer: [6, 0, -1, 13]

## Level 5

### Legal example

Adjudicate this club's trick-taking round. Cards use suit C=clubs, D=diamonds, H=hearts, S=spades followed by rank (T means ten). Every card is unique; only the dealt cards are in play. No cards are drawn or returned.
The announced leader of each trick is chosen independently, NOT by the previous winner. Play proceeds North, East, South, West cyclically from that leader. The first card sets the lead suit. Follow that suit if held immediately before playing; otherwise any card is legal. The leader may play any held card.
Playing off-suit while able to follow is a revoke: subtract 9 points from that player, and their card cannot win this trick. It is still removed from their hand and captured by the winner. Other cards remain eligible. No other penalty applies.
Use the standard maximum-card scan: among eligible cards, any trump beats any non-trump; if none is trump, only the lead suit can win. The strongest card in that suit wins. Each trick gives NEW, independent strongest-to-weakest rank strings for each suit; ordinary card ranks do not apply. Trump=none means no trump.
Initially North holds C9, CK, CT, H8, H9, SJ.
Initially East holds C8, D8, DT, HK, S9, ST.
Initially South holds DA, DJ, DQ, HA, S8, SQ.
Initially West holds CJ, D9, HJ, HT, SA, SK.
Trick 1: trump=S; C:8ATKQ9J; D:8JK9QAT; H:9TAJKQ8; S:ATQJK89. Plays in order: South=SQ, West=SK, North=CK, East=ST.
Trick 2: trump=none; C:J9QTK8A; D:TKJAQ89; H:9JQAT8K; S:AKQJ9T8. Plays in order: South=S8, West=SA, North=SJ, East=HK.
Trick 3: trump=none; C:J9TA8QK; D:QKT9JA8; H:AQK8TJ9; S:K89QJAT. Plays in order: South=DQ, West=D9, North=H8, East=DT.
Trick 4: trump=S; C:K8TAQJ9; D:KAQ9JT8; H:TQKA98J; S:K98TJAQ. Plays in order: South=DJ, West=HJ.
The last trick is unfinished. List all legal plays for North now, suits in C,D,H,S order and ranks strongest first under this trick's own suit orders. Answer as a bracketed list, for example [CQ, C9, HA].

Answer: [CT, C9, H9]

### Winner example

Adjudicate this club's trick-taking round. Cards use suit C=clubs, D=diamonds, H=hearts, S=spades followed by rank (T means ten). Every card is unique; only the dealt cards are in play. No cards are drawn or returned.
The announced leader of each trick is chosen independently, NOT by the previous winner. Play proceeds North, East, South, West cyclically from that leader. The first card sets the lead suit. Follow that suit if held immediately before playing; otherwise any card is legal. The leader may play any held card.
Playing off-suit while able to follow is a revoke: subtract 4 points from that player, and their card cannot win this trick. It is still removed from their hand and captured by the winner. Other cards remain eligible. No other penalty applies.
Use the standard maximum-card scan: among eligible cards, any trump beats any non-trump; if none is trump, only the lead suit can win. The strongest card in that suit wins. Each trick gives NEW, independent strongest-to-weakest rank strings for each suit; ordinary card ranks do not apply. Trump=none means no trump.
Initially North holds C9, CJ, DJ, DK, DQ, S9.
Initially East holds C8, CQ, DT, H9, HK, SJ.
Initially South holds CT, D8, D9, H8, HT, S8.
Initially West holds HA, HJ, SA, SK, SQ, ST.
Trick 1: trump=C; C:8J9ATKQ; D:T89QJAK; H:AT8J9QK; S:AQ9K8JT. Plays in order: East=CQ, South=CT, West=HJ, North=C9.
Trick 2: trump=D; C:Q9AJKT8; D:K89TJAQ; H:TQ8JK9A; S:KQ8JA9T. Plays in order: South=D8, West=SQ, North=DQ, East=DT.
Trick 3: trump=S; C:TQ89KAJ; D:QA8JKT9; H:KQJ8T9A; S:J9QTKA8. Plays in order: North=CJ, East=SJ, South=HT, West=SK.
Trick 4: trump=S; C:A9QTKJ8; D:TJQKA89; H:JK8T9AQ; S:AQ8TK9J. Plays in order: West=HA, North=DJ, East=H9, South=H8.
List every trick's winner in chronological order. Answer as a bracketed list of names, for example [East, South].

Answer: [North, South, West, South]

### Points example

Adjudicate this club's trick-taking round. Cards use suit C=clubs, D=diamonds, H=hearts, S=spades followed by rank (T means ten). Every card is unique; only the dealt cards are in play. No cards are drawn or returned.
The announced leader of each trick is chosen independently, NOT by the previous winner. Play proceeds North, East, South, West cyclically from that leader. The first card sets the lead suit. Follow that suit if held immediately before playing; otherwise any card is legal. The leader may play any held card.
Playing off-suit while able to follow is a revoke: subtract 3 points from that player, and their card cannot win this trick. It is still removed from their hand and captured by the winner. Other cards remain eligible. No other penalty applies.
Use the standard maximum-card scan: among eligible cards, any trump beats any non-trump; if none is trump, only the lead suit can win. The strongest card in that suit wins. Each trick gives NEW, independent strongest-to-weakest rank strings for each suit; ordinary card ranks do not apply. Trump=none means no trump.
All players start at zero. The winner captures all four cards. Each card is worth its position counted from weakest in its OWN suit's order FOR THAT TRICK: weakest=1, next=2, etc. Add captured values and subtract that player's revoke penalties. Negative totals are allowed. Unplayed cards score nothing.
Initially North holds CT, D9, DT, HK, S8, ST.
Initially East holds C8, CA, DA, DK, S9, SJ.
Initially South holds CJ, CQ, H8, H9, SK, SQ.
Initially West holds C9, D8, DQ, HA, HT, SA.
Trick 1: trump=H; C:TJQ8AK9; D:QAJT8K9; H:T8KQAJ9; S:KJ8QT9A. Plays in order: South=CJ, West=C9, North=CT, East=C8.
Trick 2: trump=D; C:8AJTKQ9; D:JQA89TK; H:QA9KT8J; S:T8AQJ9K. Plays in order: North=S8, East=DA, South=SK, West=DQ.
Trick 3: trump=C; C:J8KTQA9; D:AK8J9TQ; H:QK89AJT; S:9KQJT8A. Plays in order: North=DT, East=S9, South=H9, West=D8.
Trick 4: trump=H; C:9QJKTA8; D:QJ9ATK8; H:8KT9QJA; S:TKQ9AJ8. Plays in order: East=SJ, South=SQ, West=HT, North=D9.
Total each player's points for the shown round. Answer as a bracketed list of integers in North, East, South, West order, for example [12, -3, 8, 0].

Answer: [33, -6, 17, 12]

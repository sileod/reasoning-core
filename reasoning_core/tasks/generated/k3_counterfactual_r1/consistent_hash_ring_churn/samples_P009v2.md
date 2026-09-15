## Level 0
### Example 1
**Prompt:**

A consistent hash ring has positions 0..23. Each position is owned by the first node at or after it, wrapping around to the lowest node if none exists.
Initial node positions: [2, 6, 11].
Then these churn events happen, in order, updating the node set: join node 17; failure node 17.
Keys occupy contiguous ranges: [0,21); [21,23); [23,24).
For each range, report which positions change owner (as '[lo,hi)@position:old->new,...' where positions in the range are comma-separated) grouped under 'moved=...', and list ranges with no ownership change (as '[lo,hi): owner') under 'unchanged=...'. Ranges that stay put are explicitly listed under unchanged. Use format: moved=<list> unchanged=<list>; write 'none' for either if empty.

**Answer:**

moved=none unchanged=[0,3): 2; [3,7): 6; [7,12): 11; [12,21): 2; [21,23): 2; [23,24): 2

### Example 2
**Prompt:**

A consistent hash ring has positions 0..23. Each position is owned by the first node at or after it, wrapping around to the lowest node if none exists.
Initial node positions: [14, 18, 19].
Then these churn events happen, in order, updating the node set: join node 2; join node 12.
Keys occupy contiguous ranges: [0,7); [7,13); [13,16); [16,24).
For each range, report which positions change owner (as '[lo,hi)@position:old->new,...' where positions in the range are comma-separated) grouped under 'moved=...', and list ranges with no ownership change (as '[lo,hi): owner') under 'unchanged=...'. Ranges that stay put are explicitly listed under unchanged. Use format: moved=<list> unchanged=<list>; write 'none' for either if empty.

**Answer:**

moved=[0,7)@0:14->2,1:14->2,2:14->2,3:14->12,4:14->12,5:14->12,6:14->12; [7,13)@7:14->12,8:14->12,9:14->12,10:14->12,11:14->12,12:14->12; [20,24)@20:14->2,21:14->2,22:14->2,23:14->2 unchanged=[13,15): 14; [15,16): 18; [16,19): 18; [19,20): 19

## Level 2
### Example 1
**Prompt:**

A consistent hash ring has positions 0..39. Each position is owned by the first node at or after it, wrapping around to the lowest node if none exists.
Initial node positions: [4, 13, 27, 29, 32].
Then these churn events happen, in order, updating the node set: join node 17; failure node 13; failure node 27; failure node 4; failure node 17; join node 30.
Keys occupy contiguous ranges: [0,9); [9,35); [35,36); [36,39); [39,40).
For each range, report which positions change owner (as '[lo,hi)@position:old->new,...' where positions in the range are comma-separated) grouped under 'moved=...', and list ranges with no ownership change (as '[lo,hi): owner') under 'unchanged=...'. Ranges that stay put are explicitly listed under unchanged. Use format: moved=<list> unchanged=<list>; write 'none' for either if empty.

**Answer:**

moved=[0,9)@0:4->29,1:4->29,2:4->29,3:4->29,4:4->29,5:13->29,6:13->29,7:13->29,8:13->29; [9,28)@9:13->29,10:13->29,11:13->29,12:13->29,13:13->29,14:27->29,15:27->29,16:27->29,17:27->29,18:27->29,19:27->29,20:27->29,21:27->29,22:27->29,23:27->29,24:27->29,25:27->29,26:27->29,27:27->29; [30,31)@30:32->30; [33,35)@33:4->29,34:4->29; [35,36)@35:4->29; [36,39)@36:4->29,37:4->29,38:4->29; [39,40)@39:4->29 unchanged=[28,30): 29; [31,33): 32

### Example 2
**Prompt:**

A consistent hash ring has positions 0..39. Each position is owned by the first node at or after it, wrapping around to the lowest node if none exists.
Initial node positions: [3, 4, 7, 15, 31].
Then these churn events happen, in order, updating the node set: join node 14; failure node 15; failure node 31; failure node 3; join node 11; join node 24.
Keys occupy contiguous ranges: [0,33); [33,39); [39,40).
For each range, report which positions change owner (as '[lo,hi)@position:old->new,...' where positions in the range are comma-separated) grouped under 'moved=...', and list ranges with no ownership change (as '[lo,hi): owner') under 'unchanged=...'. Ranges that stay put are explicitly listed under unchanged. Use format: moved=<list> unchanged=<list>; write 'none' for either if empty.

**Answer:**

moved=[0,4)@0:3->4,1:3->4,2:3->4,3:3->4; [8,33)@8:15->11,9:15->11,10:15->11,11:15->11,12:15->14,13:15->14,14:15->14,15:15->24,16:31->24,17:31->24,18:31->24,19:31->24,20:31->24,21:31->24,22:31->24,23:31->24,24:31->24,25:31->4,26:31->4,27:31->4,28:31->4,29:31->4,30:31->4,31:31->4,32:3->4; [33,39)@33:3->4,34:3->4,35:3->4,36:3->4,37:3->4,38:3->4; [39,40)@39:3->4 unchanged=[4,5): 4; [5,8): 7

## Level 5
### Example 1
**Prompt:**

A consistent hash ring has positions 0..63. Each position is owned by the first node at or after it, wrapping around to the lowest node if none exists.
Initial node positions: [9, 10, 19, 22, 45, 52, 55, 58].
Then these churn events happen, in order, updating the node set: failure node 55; failure node 10; join node 14; join node 10; failure node 10; failure node 52; failure node 9; failure node 19; join node 7; failure node 14; join node 20; join node 31.
Keys occupy contiguous ranges: [0,2); [2,39); [39,56); [56,61); [61,62); [62,63); [63,64).
For each range, report which positions change owner (as '[lo,hi)@position:old->new,...' where positions in the range are comma-separated) grouped under 'moved=...', and list ranges with no ownership change (as '[lo,hi): owner') under 'unchanged=...'. Ranges that stay put are explicitly listed under unchanged. Use format: moved=<list> unchanged=<list>; write 'none' for either if empty.

**Answer:**

moved=[0,2)@0:9->7,1:9->7; [2,21)@2:9->7,3:9->7,4:9->7,5:9->7,6:9->7,7:9->7,8:9->20,9:9->20,10:10->20,11:19->20,12:19->20,13:19->20,14:19->20,15:19->20,16:19->20,17:19->20,18:19->20,19:19->20,20:22->20; [23,32)@23:45->31,24:45->31,25:45->31,26:45->31,27:45->31,28:45->31,29:45->31,30:45->31,31:45->31; [46,56)@46:52->58,47:52->58,48:52->58,49:52->58,50:52->58,51:52->58,52:52->58,53:55->58,54:55->58,55:55->58; [59,61)@59:9->7,60:9->7; [61,62)@61:9->7; [62,63)@62:9->7; [63,64)@63:9->7 unchanged=[21,23): 22; [32,39): 45; [39,46): 45; [56,59): 58

### Example 2
**Prompt:**

A consistent hash ring has positions 0..63. Each position is owned by the first node at or after it, wrapping around to the lowest node if none exists.
Initial node positions: [4, 13, 27, 30, 35, 48, 50, 59].
Then these churn events happen, in order, updating the node set: join node 61; join node 9; failure node 27; failure node 48; join node 28; join node 60; failure node 13; join node 18; failure node 61; join node 57; failure node 57; failure node 4.
Keys occupy contiguous ranges: [0,38); [38,50); [50,55); [55,59); [59,60); [60,63); [63,64).
For each range, report which positions change owner (as '[lo,hi)@position:old->new,...' where positions in the range are comma-separated) grouped under 'moved=...', and list ranges with no ownership change (as '[lo,hi): owner') under 'unchanged=...'. Ranges that stay put are explicitly listed under unchanged. Use format: moved=<list> unchanged=<list>; write 'none' for either if empty.

**Answer:**

moved=[0,29)@0:4->9,1:4->9,2:4->9,3:4->9,4:4->9,5:13->9,6:13->9,7:13->9,8:13->9,9:13->9,10:13->18,11:13->18,12:13->18,13:13->18,14:27->18,15:27->18,16:27->18,17:27->18,18:27->18,19:27->28,20:27->28,21:27->28,22:27->28,23:27->28,24:27->28,25:27->28,26:27->28,27:27->28,28:30->28; [36,38)@36:48->50,37:48->50; [38,49)@38:48->50,39:48->50,40:48->50,41:48->50,42:48->50,43:48->50,44:48->50,45:48->50,46:48->50,47:48->50,48:48->50; [60,63)@60:4->60,61:4->9,62:4->9; [63,64)@63:4->9 unchanged=[29,31): 30; [31,36): 35; [49,50): 50; [50,51): 50; [51,55): 59; [55,59): 59; [59,60): 59


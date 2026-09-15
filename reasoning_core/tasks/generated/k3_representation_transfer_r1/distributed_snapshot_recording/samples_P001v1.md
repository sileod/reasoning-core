## Level 0
### Example 1
**Prompt:**
A distributed system has 3 processes indexed 0..2 with directed channels between them. Each process's local state is a counter equal to the number of messages it has received. Each channel carries an ordered list of messages (indexed 0,1,2,... in send order). A Chandy-Lamport marker is sent on every channel and each process records its state when the marker reaches it. In the resulting consistent cut: a message sent before the sender recorded its state AND delivered to the receiver before the receiver recorded its state is recorded as received; a message sent before the sender recorded its state but delivered to the receiver after the receiver recorded its state is in-flight and is recorded as the channel's content. No message is both recorded as received and in-flight. Channels: 2->1 carrying 1 message(s); 0->1 carrying 3 message(s). Give the recorded snapshot as: each process's received-message counter, then each channel's in-flight message indexes. Answer format: p0:c0; p1:c1; ... | (s0->t0):[i,..] (s1->t1):[...] ... — processes in increasing index order, channels in the listed order, each channel's in-flight indexes as a bracketed list in increasing index order.

**Answer:**
0:0; 1:2; 2:0 | (2->1):[0] (0->1):[]

### Example 2
**Prompt:**
A distributed system has 3 processes indexed 0..2 with directed channels between them. Each process's local state is a counter equal to the number of messages it has received. Each channel carries an ordered list of messages (indexed 0,1,2,... in send order). A Chandy-Lamport marker is sent on every channel and each process records its state when the marker reaches it. In the resulting consistent cut: a message sent before the sender recorded its state AND delivered to the receiver before the receiver recorded its state is recorded as received; a message sent before the sender recorded its state but delivered to the receiver after the receiver recorded its state is in-flight and is recorded as the channel's content. No message is both recorded as received and in-flight. Channels: 2->0 carrying 3 message(s); 1->2 carrying 3 message(s); 0->1 carrying 2 message(s). Give the recorded snapshot as: each process's received-message counter, then each channel's in-flight message indexes. Answer format: p0:c0; p1:c1; ... | (s0->t0):[i,..] (s1->t1):[...] ... — processes in increasing index order, channels in the listed order, each channel's in-flight indexes as a bracketed list in increasing index order.

**Answer:**
0:0; 1:0; 2:1 | (2->0):[0, 1, 2] (1->2):[] (0->1):[]

## Level 2
### Example 1
**Prompt:**
A distributed system has 7 processes indexed 0..6 with directed channels between them. Each process's local state is a counter equal to the number of messages it has received. Each channel carries an ordered list of messages (indexed 0,1,2,... in send order). A Chandy-Lamport marker is sent on every channel and each process records its state when the marker reaches it. In the resulting consistent cut: a message sent before the sender recorded its state AND delivered to the receiver before the receiver recorded its state is recorded as received; a message sent before the sender recorded its state but delivered to the receiver after the receiver recorded its state is in-flight and is recorded as the channel's content. No message is both recorded as received and in-flight. Channels: 5->3 carrying 4 message(s); 4->5 carrying 6 message(s). Give the recorded snapshot as: each process's received-message counter, then each channel's in-flight message indexes. Answer format: p0:c0; p1:c1; ... | (s0->t0):[i,..] (s1->t1):[...] ... — processes in increasing index order, channels in the listed order, each channel's in-flight indexes as a bracketed list in increasing index order.

**Answer:**
0:0; 1:0; 2:0; 3:0; 4:0; 5:0; 6:0 | (5->3):[] (4->5):[]

### Example 2
**Prompt:**
A distributed system has 7 processes indexed 0..6 with directed channels between them. Each process's local state is a counter equal to the number of messages it has received. Each channel carries an ordered list of messages (indexed 0,1,2,... in send order). A Chandy-Lamport marker is sent on every channel and each process records its state when the marker reaches it. In the resulting consistent cut: a message sent before the sender recorded its state AND delivered to the receiver before the receiver recorded its state is recorded as received; a message sent before the sender recorded its state but delivered to the receiver after the receiver recorded its state is in-flight and is recorded as the channel's content. No message is both recorded as received and in-flight. Channels: 0->6 carrying 2 message(s); 5->6 carrying 1 message(s); 0->1 carrying 1 message(s); 3->0 carrying 6 message(s); 4->2 carrying 2 message(s); 0->4 carrying 3 message(s); 1->0 carrying 5 message(s). Give the recorded snapshot as: each process's received-message counter, then each channel's in-flight message indexes. Answer format: p0:c0; p1:c1; ... | (s0->t0):[i,..] (s1->t1):[...] ... — processes in increasing index order, channels in the listed order, each channel's in-flight indexes as a bracketed list in increasing index order.

**Answer:**
0:1; 1:0; 2:0; 3:0; 4:2; 5:0; 6:0 | (0->6):[0] (5->6):[0] (0->1):[] (3->0):[0, 1, 2, 3, 4] (4->2):[] (0->4):[2] (1->0):[1, 2]

## Level 5
### Example 1
**Prompt:**
A distributed system has 13 processes indexed 0..12 with directed channels between them. Each process's local state is a counter equal to the number of messages it has received. Each channel carries an ordered list of messages (indexed 0,1,2,... in send order). A Chandy-Lamport marker is sent on every channel and each process records its state when the marker reaches it. In the resulting consistent cut: a message sent before the sender recorded its state AND delivered to the receiver before the receiver recorded its state is recorded as received; a message sent before the sender recorded its state but delivered to the receiver after the receiver recorded its state is in-flight and is recorded as the channel's content. No message is both recorded as received and in-flight. Channels: 6->8 carrying 5 message(s); 9->7 carrying 11 message(s). Give the recorded snapshot as: each process's received-message counter, then each channel's in-flight message indexes. Answer format: p0:c0; p1:c1; ... | (s0->t0):[i,..] (s1->t1):[...] ... — processes in increasing index order, channels in the listed order, each channel's in-flight indexes as a bracketed list in increasing index order.

**Answer:**
0:0; 1:0; 2:0; 3:0; 4:0; 5:0; 6:0; 7:4; 8:0; 9:0; 10:0; 11:0; 12:0 | (6->8):[0, 1, 2] (9->7):[4, 5, 6]

### Example 2
**Prompt:**
A distributed system has 13 processes indexed 0..12 with directed channels between them. Each process's local state is a counter equal to the number of messages it has received. Each channel carries an ordered list of messages (indexed 0,1,2,... in send order). A Chandy-Lamport marker is sent on every channel and each process records its state when the marker reaches it. In the resulting consistent cut: a message sent before the sender recorded its state AND delivered to the receiver before the receiver recorded its state is recorded as received; a message sent before the sender recorded its state but delivered to the receiver after the receiver recorded its state is in-flight and is recorded as the channel's content. No message is both recorded as received and in-flight. Channels: 3->4 carrying 13 message(s); 0->8 carrying 11 message(s). Give the recorded snapshot as: each process's received-message counter, then each channel's in-flight message indexes. Answer format: p0:c0; p1:c1; ... | (s0->t0):[i,..] (s1->t1):[...] ... — processes in increasing index order, channels in the listed order, each channel's in-flight indexes as a bracketed list in increasing index order.

**Answer:**
0:0; 1:0; 2:0; 3:0; 4:7; 5:0; 6:0; 7:0; 8:0; 9:0; 10:0; 11:0; 12:0 | (3->4):[7, 8, 9, 10] (0->8):[0, 1, 2, 3]


## Level 0
### Example 1
Prompt:
We maintain a line of positions 0..6. There are 2 interval layers. layer X is [lo,hi] inclusive and has priority P; a higher priority covers a lower one. The visible value at a position is the id of the highest-priority active layer covering it, or empty if none.
layer 0 is [4,5] at priority 7.
layer 1 is [3,4] at priority 6.
After the operations, the final visible value across the line is grouped into maximal constant spans where the visible value is that of a single layer. Report those spans in ascending order, each as [start,end] followed by the layer id, segments separated by ';'. If the whole line is empty, answer exactly 'none'.
Answer:
[3,3]:1;[4,5]:0

### Example 2
Prompt:
We maintain a line of positions 0..6. There are 2 interval layers. layer X is [lo,hi] inclusive and has priority P; a higher priority covers a lower one. The visible value at a position is the id of the highest-priority active layer covering it, or empty if none.
layer 0 is [1,2] at priority 10.
layer 1 is [2,5] at priority 4.
remove layer 0.
After the operations, the final visible value across the line is grouped into maximal constant spans where the visible value is that of a single layer. Report those spans in ascending order, each as [start,end] followed by the layer id, segments separated by ';'. If the whole line is empty, answer exactly 'none'.
Answer:
[2,5]:1

## Level 2
### Example 1
Prompt:
We maintain a line of positions 0..10. There are 4 interval layers. layer X is [lo,hi] inclusive and has priority P; a higher priority covers a lower one. The visible value at a position is the id of the highest-priority active layer covering it, or empty if none.
layer 0 is [1,5] at priority 4.
layer 1 is [4,5] at priority 1.
layer 2 is [8,9] at priority 7.
layer 3 is [3,5] at priority 10.
remove layer 2.
activate layer 2.
remove layer 1.
After the operations, the final visible value across the line is grouped into maximal constant spans where the visible value is that of a single layer. Report those spans in ascending order, each as [start,end] followed by the layer id, segments separated by ';'. If the whole line is empty, answer exactly 'none'.
Answer:
[1,2]:0;[3,5]:3;[8,9]:2

### Example 2
Prompt:
We maintain a line of positions 0..10. There are 4 interval layers. layer X is [lo,hi] inclusive and has priority P; a higher priority covers a lower one. The visible value at a position is the id of the highest-priority active layer covering it, or empty if none.
layer 0 is [8,9] at priority 4.
layer 1 is [5,7] at priority 7.
layer 2 is [4,7] at priority 10.
layer 3 is [3,6] at priority 2.
remove layer 2.
layer 0 changes priority to 4.
remove layer 1.
After the operations, the final visible value across the line is grouped into maximal constant spans where the visible value is that of a single layer. Report those spans in ascending order, each as [start,end] followed by the layer id, segments separated by ';'. If the whole line is empty, answer exactly 'none'.
Answer:
[3,6]:3;[8,9]:0

## Level 5
### Example 1
Prompt:
We maintain a line of positions 0..16. There are 7 interval layers. layer X is [lo,hi] inclusive and has priority P; a higher priority covers a lower one. The visible value at a position is the id of the highest-priority active layer covering it, or empty if none.
layer 0 is [10,15] at priority 10.
layer 1 is [7,13] at priority 5.
layer 2 is [6,7] at priority 8.
layer 3 is [6,15] at priority 9.
layer 4 is [0,2] at priority 6.
layer 5 is [10,12] at priority 10.
layer 6 is [13,15] at priority 10.
layer 6 changes priority to 10.
remove layer 1.
layer 2 changes priority to 6.
remove layer 0.
activate layer 0.
layer 2 changes priority to 8.
After the operations, the final visible value across the line is grouped into maximal constant spans where the visible value is that of a single layer. Report those spans in ascending order, each as [start,end] followed by the layer id, segments separated by ';'. If the whole line is empty, answer exactly 'none'.
Answer:
[0,2]:4;[6,9]:3;[10,15]:0

### Example 2
Prompt:
We maintain a line of positions 0..16. There are 7 interval layers. layer X is [lo,hi] inclusive and has priority P; a higher priority covers a lower one. The visible value at a position is the id of the highest-priority active layer covering it, or empty if none.
layer 0 is [9,13] at priority 3.
layer 1 is [0,13] at priority 1.
layer 2 is [7,9] at priority 7.
layer 3 is [13,14] at priority 7.
layer 4 is [6,15] at priority 7.
layer 5 is [6,9] at priority 3.
layer 6 is [10,14] at priority 3.
remove layer 5.
layer 4 changes priority to 7.
remove layer 1.
activate layer 5.
activate layer 1.
layer 1 changes priority to 1.
After the operations, the final visible value across the line is grouped into maximal constant spans where the visible value is that of a single layer. Report those spans in ascending order, each as [start,end] followed by the layer id, segments separated by ';'. If the whole line is empty, answer exactly 'none'.
Answer:
[0,5]:1;[6,6]:4;[7,9]:2;[10,12]:4;[13,14]:3;[15,15]:4


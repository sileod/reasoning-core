# Samples for misra_gries_summary (P007v2)

## Level 0

### Example 1

**Prompt:**

Run the Misra-Gries summary algorithm with a budget of k=2 counters over the symbol stream [1, 0, 1, 1, 1, 1, 1, 1, 1, 2]. The rules are: to add a symbol, if it has a counter increment that counter; else if fewer than k counters are in use, open a new counter set to 1 for it; else decrement every existing counter by 1 and evict any counter that reaches 0. Report the final counter table as 'symbol=count' pairs in ascending symbol order separated by spaces (empty table is written 'none'), then state whether the queried symbol 1 can be the majority (appears more than half the time) of the stream, 'yes' or 'no'. Write them on one line as <table>|<yes|no>, for example 'a=2 b=1|no'. Final table and majority determination:

**Answer:**

1=7|yes

### Example 2

**Prompt:**

Run the Misra-Gries summary algorithm with a budget of k=2 counters over the symbol stream [4, 4, 1, 4, 3, 4, 4, 4, 4, 4]. The rules are: to add a symbol, if it has a counter increment that counter; else if fewer than k counters are in use, open a new counter set to 1 for it; else decrement every existing counter by 1 and evict any counter that reaches 0. Report the final counter table as 'symbol=count' pairs in ascending symbol order separated by spaces (empty table is written 'none'), then state whether the queried symbol 4 can be the majority (appears more than half the time) of the stream, 'yes' or 'no'. Write them on one line as <table>|<yes|no>, for example 'a=2 b=1|no'. Final table and majority determination:

**Answer:**

4=7|yes

## Level 2

### Example 1

**Prompt:**

Run the Misra-Gries summary algorithm with a budget of k=3 counters over the symbol stream [2, 2, 2, 8, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 8]. The rules are: to add a symbol, if it has a counter increment that counter; else if fewer than k counters are in use, open a new counter set to 1 for it; else decrement every existing counter by 1 and evict any counter that reaches 0. Report the final counter table as 'symbol=count' pairs in ascending symbol order separated by spaces (empty table is written 'none'), then state whether the queried symbol 4 can be the majority (appears more than half the time) of the stream, 'yes' or 'no'. Write them on one line as <table>|<yes|no>, for example 'a=2 b=1|no'. Final table and majority determination:

**Answer:**

2=11 8=1|no

### Example 2

**Prompt:**

Run the Misra-Gries summary algorithm with a budget of k=3 counters over the symbol stream [3, 8, 1, 5, 4, 4, 4, 4, 6, 4, 5, 4, 8, 4, 4, 4]. The rules are: to add a symbol, if it has a counter increment that counter; else if fewer than k counters are in use, open a new counter set to 1 for it; else decrement every existing counter by 1 and evict any counter that reaches 0. Report the final counter table as 'symbol=count' pairs in ascending symbol order separated by spaces (empty table is written 'none'), then state whether the queried symbol 3 can be the majority (appears more than half the time) of the stream, 'yes' or 'no'. Write them on one line as <table>|<yes|no>, for example 'a=2 b=1|no'. Final table and majority determination:

**Answer:**

4=8|no

## Level 5

### Example 1

**Prompt:**

Run the Misra-Gries summary algorithm with a budget of k=4 counters over the symbol stream [6, 3, 3, 3, 3, 3, 3, 14, 3, 1, 3, 3, 3, 3, 3, 6, 3, 3, 3, 3, 3, 3, 3, 3, 10]. The rules are: to add a symbol, if it has a counter increment that counter; else if fewer than k counters are in use, open a new counter set to 1 for it; else decrement every existing counter by 1 and evict any counter that reaches 0. Report the final counter table as 'symbol=count' pairs in ascending symbol order separated by spaces (empty table is written 'none'), then state whether the queried symbol 3 can be the majority (appears more than half the time) of the stream, 'yes' or 'no'. Write them on one line as <table>|<yes|no>, for example 'a=2 b=1|no'. Final table and majority determination:

**Answer:**

3=19 6=1|yes

### Example 2

**Prompt:**

Run the Misra-Gries summary algorithm with a budget of k=4 counters over the symbol stream [11, 11, 11, 3, 11, 11, 11, 9, 11, 6, 10, 12, 12, 7, 11, 11, 11, 11, 14, 11, 7, 11, 9, 0, 11]. The rules are: to add a symbol, if it has a counter increment that counter; else if fewer than k counters are in use, open a new counter set to 1 for it; else decrement every existing counter by 1 and evict any counter that reaches 0. Report the final counter table as 'symbol=count' pairs in ascending symbol order separated by spaces (empty table is written 'none'), then state whether the queried symbol 11 can be the majority (appears more than half the time) of the stream, 'yes' or 'no'. Write them on one line as <table>|<yes|no>, for example 'a=2 b=1|no'. Final table and majority determination:

**Answer:**

0=1 7=1 11=12 12=1|yes

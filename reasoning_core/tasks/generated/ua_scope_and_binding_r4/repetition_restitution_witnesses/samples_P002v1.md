## Level 0
**Prompt:**
```
A chronologically ordered sequence of events E0, E1, ... occurs. Each event lists who performed what action on which object and the resulting state of that object.
E0: Cara empty the door; afterwards the door is empty.
E1: Cara start the box; afterwards the box is running.
E2: Cara empty the window; afterwards the window is empty.
E3: Cara empty the door; afterwards the door is empty.
E4: Ben empty the tank; afterwards the tank is empty.

A repetitive reading needs an earlier event by the SAME subject performing the SAME action; its witness is the most recent such earlier event. A restitutive reading needs the object to already be in that state: it is witnessed by the most recent earlier event that touched the SAME object and left it in that SAME state (an intermediate change would have interrupted it). Use 'None' when no earlier event witnesses the reading.

R0: Repetitive reading of E3: Cara empty the door again.
R1: Restitutive reading of E3: the door is empty again.
R2: Repetitive reading of E4: Ben empty the tank again.
R3: Restitutive reading of E4: the tank is empty again.

Give each reading's most recent appropriate earlier-witness event, in reading order R0, R1, ..., as a space-separated list of event IDs (like E2) or the word None for an unwitnessed reading.
```
**Answer:**
```
E2 E0 None None
```

**Prompt:**
```
A chronologically ordered sequence of events E0, E1, ... occurs. Each event lists who performed what action on which object and the resulting state of that object.
E0: Dan close the tank; afterwards the tank is closed.
E1: Ben start the door; afterwards the door is running.
E2: Ben start the door; afterwards the door is running.
E3: Ben start the door; afterwards the door is running.
E4: Dan unlock the tank; afterwards the tank is unlocked.

A repetitive reading needs an earlier event by the SAME subject performing the SAME action; its witness is the most recent such earlier event. A restitutive reading needs the object to already be in that state: it is witnessed by the most recent earlier event that touched the SAME object and left it in that SAME state (an intermediate change would have interrupted it). Use 'None' when no earlier event witnesses the reading.

R0: Repetitive reading of E3: Ben start the door again.
R1: Restitutive reading of E3: the door is running again.
R2: Repetitive reading of E4: Dan unlock the tank again.
R3: Restitutive reading of E4: the tank is unlocked again.

Give each reading's most recent appropriate earlier-witness event, in reading order R0, R1, ..., as a space-separated list of event IDs (like E2) or the word None for an unwitnessed reading.
```
**Answer:**
```
E2 E2 None None
```

## Level 2
**Prompt:**
```
A chronologically ordered sequence of events E0, E1, ... occurs. Each event lists who performed what action on which object and the resulting state of that object.
E0: Ben stop the door; afterwards the door is stopped.
E1: Ada fill the box; afterwards the box is full.
E2: Finn close the box; afterwards the box is closed.
E3: Ada unlock the window; afterwards the window is unlocked.
E4: Ben stop the gate; afterwards the gate is stopped.
E5: Ada empty the window; afterwards the window is empty.
E6: Ben stop the gate; afterwards the gate is stopped.

A repetitive reading needs an earlier event by the SAME subject performing the SAME action; its witness is the most recent such earlier event. A restitutive reading needs the object to already be in that state: it is witnessed by the most recent earlier event that touched the SAME object and left it in that SAME state (an intermediate change would have interrupted it). Use 'None' when no earlier event witnesses the reading.

R0: Repetitive reading of E4: Ben stop the gate again.
R1: Restitutive reading of E4: the gate is stopped again.
R2: Repetitive reading of E5: Ada empty the window again.
R3: Restitutive reading of E5: the window is empty again.
R4: Repetitive reading of E6: Ben stop the gate again.
R5: Restitutive reading of E6: the gate is stopped again.

Give each reading's most recent appropriate earlier-witness event, in reading order R0, R1, ..., as a space-separated list of event IDs (like E2) or the word None for an unwitnessed reading.
```
**Answer:**
```
E0 None None None E4 E4
```

**Prompt:**
```
A chronologically ordered sequence of events E0, E1, ... occurs. Each event lists who performed what action on which object and the resulting state of that object.
E0: Dan fill the tank; afterwards the tank is full.
E1: Finn start the door; afterwards the door is running.
E2: Eve fill the tank; afterwards the tank is full.
E3: Eve fill the tank; afterwards the tank is full.
E4: Ben fill the box; afterwards the box is full.
E5: Eve stop the gate; afterwards the gate is stopped.
E6: Dan fill the box; afterwards the box is full.

A repetitive reading needs an earlier event by the SAME subject performing the SAME action; its witness is the most recent such earlier event. A restitutive reading needs the object to already be in that state: it is witnessed by the most recent earlier event that touched the SAME object and left it in that SAME state (an intermediate change would have interrupted it). Use 'None' when no earlier event witnesses the reading.

R0: Repetitive reading of E4: Ben fill the box again.
R1: Restitutive reading of E4: the box is full again.
R2: Repetitive reading of E5: Eve stop the gate again.
R3: Restitutive reading of E5: the gate is stopped again.
R4: Repetitive reading of E6: Dan fill the box again.
R5: Restitutive reading of E6: the box is full again.

Give each reading's most recent appropriate earlier-witness event, in reading order R0, R1, ..., as a space-separated list of event IDs (like E2) or the word None for an unwitnessed reading.
```
**Answer:**
```
None None None None E0 E4
```

## Level 5
**Prompt:**
```
A chronologically ordered sequence of events E0, E1, ... occurs. Each event lists who performed what action on which object and the resulting state of that object.
E0: Cara unlock the shutter; afterwards the shutter is unlocked.
E1: Cara open the shutter; afterwards the shutter is open.
E2: Finn empty the well; afterwards the well is empty.
E3: Dan close the door; afterwards the door is closed.
E4: Jon lock the gate; afterwards the gate is locked.
E5: Kay open the well; afterwards the well is open.
E6: Eve close the gate; afterwards the gate is closed.
E7: Ben stop the door; afterwards the door is stopped.
E8: Eve close the gate; afterwards the gate is closed.
E9: Ida empty the shutter; afterwards the shutter is empty.

A repetitive reading needs an earlier event by the SAME subject performing the SAME action; its witness is the most recent such earlier event. A restitutive reading needs the object to already be in that state: it is witnessed by the most recent earlier event that touched the SAME object and left it in that SAME state (an intermediate change would have interrupted it). Use 'None' when no earlier event witnesses the reading.

R0: Repetitive reading of E6: Eve close the gate again.
R1: Restitutive reading of E6: the gate is closed again.
R2: Repetitive reading of E7: Ben stop the door again.
R3: Restitutive reading of E7: the door is stopped again.
R4: Repetitive reading of E8: Eve close the gate again.
R5: Restitutive reading of E8: the gate is closed again.
R6: Repetitive reading of E9: Ida empty the shutter again.
R7: Restitutive reading of E9: the shutter is empty again.

Give each reading's most recent appropriate earlier-witness event, in reading order R0, R1, ..., as a space-separated list of event IDs (like E2) or the word None for an unwitnessed reading.
```
**Answer:**
```
None None None None E6 E6 None None
```

**Prompt:**
```
A chronologically ordered sequence of events E0, E1, ... occurs. Each event lists who performed what action on which object and the resulting state of that object.
E0: Ben stop the gate; afterwards the gate is stopped.
E1: Kay lock the shutter; afterwards the shutter is locked.
E2: Dan start the window; afterwards the window is running.
E3: Ben unlock the window; afterwards the window is unlocked.
E4: Ben empty the window; afterwards the window is empty.
E5: Ada empty the tank; afterwards the tank is empty.
E6: Dan lock the door; afterwards the door is locked.
E7: Dan lock the shutter; afterwards the shutter is locked.
E8: Ada start the well; afterwards the well is running.
E9: Ida start the window; afterwards the window is running.

A repetitive reading needs an earlier event by the SAME subject performing the SAME action; its witness is the most recent such earlier event. A restitutive reading needs the object to already be in that state: it is witnessed by the most recent earlier event that touched the SAME object and left it in that SAME state (an intermediate change would have interrupted it). Use 'None' when no earlier event witnesses the reading.

R0: Repetitive reading of E6: Dan lock the door again.
R1: Restitutive reading of E6: the door is locked again.
R2: Repetitive reading of E7: Dan lock the shutter again.
R3: Restitutive reading of E7: the shutter is locked again.
R4: Repetitive reading of E8: Ada start the well again.
R5: Restitutive reading of E8: the well is running again.
R6: Repetitive reading of E9: Ida start the window again.
R7: Restitutive reading of E9: the window is running again.

Give each reading's most recent appropriate earlier-witness event, in reading order R0, R1, ..., as a space-separated list of event IDs (like E2) or the word None for an unwitnessed reading.
```
**Answer:**
```
None None E6 E1 None None None None
```

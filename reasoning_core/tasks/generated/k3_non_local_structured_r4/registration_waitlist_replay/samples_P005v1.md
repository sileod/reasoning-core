# Level 0

### Example

A university runs a course-registration system. Each section has a fixed number of seats. A student who cannot get a seat is placed at the back of that section's FIFO waitlist in arrival order; when a seated student is dropped, the freed seat goes to the front student on that section's waitlist. A swap exchanges the two chosen students' enrollments: each moves to the other's section with the other's seated-or-waiting status, joining the back of any waitlist.

Sections and seat caps:
A: 3 seats
B: 1 seats

Enrollments at the start:
A: roster ['s0'], waitlist []
B: roster ['s3'], waitlist []

All other listed students are not enrolled: s1, s2

Registration requests, applied in order:
1. swap s0 (in section A) with s3 (in section B)
2. add s2 to section B
3. swap s3 (in section A) with s2 (in section B)

What is the length of the FIFO waitlist for section A after all requests? Answer as a single integer.


**Answer:** 0

### Example

A university runs a course-registration system. Each section has a fixed number of seats. A student who cannot get a seat is placed at the back of that section's FIFO waitlist in arrival order; when a seated student is dropped, the freed seat goes to the front student on that section's waitlist. A swap exchanges the two chosen students' enrollments: each moves to the other's section with the other's seated-or-waiting status, joining the back of any waitlist.

Sections and seat caps:
A: 3 seats
B: 2 seats

Enrollments at the start:
A: roster [], waitlist []
B: roster ['s1', 's2'], waitlist []

All other listed students are not enrolled: s0, s3

Registration requests, applied in order:
1. add s3 to section A
2. drop s3 from section A
3. drop s1 from section B

What is the length of the FIFO waitlist for section B after all requests? Answer as a single integer.


**Answer:** 0



# Level 2

### Example

A university runs a course-registration system. Each section has a fixed number of seats. A student who cannot get a seat is placed at the back of that section's FIFO waitlist in arrival order; when a seated student is dropped, the freed seat goes to the front student on that section's waitlist. A swap exchanges the two chosen students' enrollments: each moves to the other's section with the other's seated-or-waiting status, joining the back of any waitlist.

Sections and seat caps:
A: 5 seats
B: 4 seats
C: 3 seats
D: 4 seats

Enrollments at the start:
A: roster ['s0'], waitlist []
B: roster [], waitlist []
C: roster [], waitlist []
D: roster ['s4'], waitlist []

All other listed students are not enrolled: s1, s2, s3, s5, s6, s7

Registration requests, applied in order:
1. swap s0 (in section A) with s4 (in section D)
2. add s1 to section C
3. drop s1 from section C
4. swap s4 (in section A) with s0 (in section D)
5. swap s0 (in section A) with s4 (in section D)
6. add s6 to section C
7. swap s4 (in section A) with s6 (in section C)

What is the final enrollment status of student s0? Answer `seated in <Letter>`, `waiting in <Letter>`, or `not enrolled`.


**Answer:** seated in D

### Example

A university runs a course-registration system. Each section has a fixed number of seats. A student who cannot get a seat is placed at the back of that section's FIFO waitlist in arrival order; when a seated student is dropped, the freed seat goes to the front student on that section's waitlist. A swap exchanges the two chosen students' enrollments: each moves to the other's section with the other's seated-or-waiting status, joining the back of any waitlist.

Sections and seat caps:
A: 3 seats
B: 2 seats
C: 6 seats
D: 6 seats

Enrollments at the start:
A: roster ['s4', 's6'], waitlist []
B: roster ['s0', 's1'], waitlist []
C: roster ['s2'], waitlist []
D: roster ['s7'], waitlist []

All other listed students are not enrolled: s3, s5

Registration requests, applied in order:
1. add s3 to section B
2. drop s3 from section B
3. drop s6 from section A
4. swap s4 (in section A) with s7 (in section D)
5. swap s7 (in section A) with s4 (in section D)
6. add s3 to section B
7. add s5 to section B

Give the final seated roster for every section. Format: for each non-empty section in alphabetical order, `Letter:[comma-separated sorted student IDs]`, empty sections omitted, sections joined by `; `, e.g. `A:[s1,s3]; B:[s2]`.


**Answer:** A:[s4]; B:[s0,s1]; C:[s2]; D:[s7]



# Level 5

### Example

A university runs a course-registration system. Each section has a fixed number of seats. A student who cannot get a seat is placed at the back of that section's FIFO waitlist in arrival order; when a seated student is dropped, the freed seat goes to the front student on that section's waitlist. A swap exchanges the two chosen students' enrollments: each moves to the other's section with the other's seated-or-waiting status, joining the back of any waitlist.

Sections and seat caps:
A: 4 seats
B: 6 seats
C: 7 seats
D: 10 seats
E: 4 seats
F: 4 seats
G: 3 seats

Enrollments at the start:
A: roster ['s0', 's12'], waitlist []
B: roster ['s1', 's11'], waitlist []
C: roster ['s2'], waitlist []
D: roster ['s3', 's5', 's10'], waitlist []
E: roster ['s9'], waitlist []
F: roster ['s6'], waitlist []
G: roster ['s7', 's8'], waitlist []

All other listed students are not enrolled: s13, s4

Registration requests, applied in order:
1. add s4 to section C
2. drop s7 from section G
3. add s13 to section C
4. add s7 to section D
5. drop s1 from section B
6. swap s11 (in section B) with s4 (in section C)
7. add s1 to section G
8. swap s9 (in section E) with s6 (in section F)
9. drop s12 from section A
10. add s12 to section A
11. swap s2 (in section C) with s7 (in section D)
12. drop s6 from section E
13. add s6 to section G

Give the final seated roster for every section. Format: for each non-empty section in alphabetical order, `Letter:[comma-separated sorted student IDs]`, empty sections omitted, sections joined by `; `, e.g. `A:[s1,s3]; B:[s2]`.


**Answer:** A:[s0,s12]; B:[s4]; C:[s11,s13,s7]; D:[s10,s2,s3,s5]; F:[s9]; G:[s1,s6,s8]

### Example

A university runs a course-registration system. Each section has a fixed number of seats. A student who cannot get a seat is placed at the back of that section's FIFO waitlist in arrival order; when a seated student is dropped, the freed seat goes to the front student on that section's waitlist. A swap exchanges the two chosen students' enrollments: each moves to the other's section with the other's seated-or-waiting status, joining the back of any waitlist.

Sections and seat caps:
A: 10 seats
B: 5 seats
C: 5 seats
D: 4 seats
E: 7 seats
F: 4 seats
G: 8 seats

Enrollments at the start:
A: roster [], waitlist []
B: roster ['s11'], waitlist []
C: roster ['s5', 's6', 's7'], waitlist []
D: roster ['s8', 's9', 's10'], waitlist []
E: roster [], waitlist []
F: roster ['s2', 's3', 's13'], waitlist []
G: roster ['s1'], waitlist []

All other listed students are not enrolled: s0, s12, s4

Registration requests, applied in order:
1. add s0 to section D
2. swap s7 (in section C) with s13 (in section F)
3. drop s10 from section D
4. add s10 to section F
5. drop s11 from section B
6. add s12 to section C
7. swap s0 (in section D) with s1 (in section G)
8. add s4 to section E
9. swap s5 (in section C) with s9 (in section D)
10. swap s4 (in section E) with s0 (in section G)
11. add s11 to section D
12. drop s9 from section C
13. swap s1 (in section D) with s10 (in section F)

What is the final enrollment status of student s1? Answer `seated in <Letter>`, `waiting in <Letter>`, or `not enrolled`.


**Answer:** seated in F




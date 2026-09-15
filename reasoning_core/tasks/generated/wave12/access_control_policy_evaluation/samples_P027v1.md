# Samples for access_control_policy_evaluation

## Level 0

### Example 1

**Prompt:**

```
A subject belongs to the following groups, each with allow/deny rules.
Precedence policy: deny-overrides.
Group group0: act0:allow.
Group group2: act2:allow.
Respond with the exact word allow or deny.
Question 1: What is the effective decision for action act1?
```

**Answer:**

deny

### Example 2

**Prompt:**

```
A subject belongs to the following groups, each with allow/deny rules.
Precedence policy: first-match.
Group group0: act1:allow.
Group group1: act1:deny.
Group group2: act0:deny.
Respond with the exact word allow or deny.
Question 1: What is the effective decision for action act1?
```

**Answer:**

allow

## Level 2

### Example 1

**Prompt:**

```
A subject belongs to the following groups, each with allow/deny rules.
Precedence policy: first-match.
Group group0: act4:deny.
Group group1: act3:allow, act0:deny, act1:allow.
Group group2: act3:deny.
Group group3: act0:allow, act4:deny, act2:allow.
Group group4: act0:deny, act2:allow, act1:allow.
Respond with the exact word allow or deny.
Question 1: What is the effective decision for action act3?
```

**Answer:**

allow

### Example 2

**Prompt:**

```
A subject belongs to the following groups, each with allow/deny rules.
Precedence policy: deny-overrides.
Group group0: act0:allow, act3:deny, act4:deny.
Group group1: act4:allow, act2:allow.
Group group2: act2:allow, act3:allow.
Group group3: act2:allow, act3:allow.
Group group4: act2:allow, act1:deny, act0:allow.
Respond with the exact word allow or deny.
Question 1: What is the effective decision for action act4?
```

**Answer:**

deny

## Level 5

### Example 1

**Prompt:**

```
A subject belongs to the following groups, each with allow/deny rules.
Precedence policy: first-match.
Group group1: act4:deny, act3:allow, act1:allow.
Group group3: act3:deny, act2:allow, act0:allow, act4:allow.
Group group4: act0:allow, act3:deny, act4:allow, act1:deny.
Group group5: act4:allow, act3:allow, act2:allow.
For each question respond with allow or deny, listed in question order and separated by semicolons, e.g. 'allow;deny'.
Question 1: What is the effective decision for action act3?
Question 2: What is the effective decision for action act4?
```

**Answer:**

allow;deny

### Example 2

**Prompt:**

```
A subject belongs to the following groups, each with allow/deny rules.
Precedence policy: first-match.
Group group0: act4:allow, act2:deny, act3:allow.
Group group1: act4:deny, act3:deny, act0:allow.
Group group2: act1:deny, act2:allow, act0:allow.
Group group3: act3:deny, act0:deny.
Group group5: act1:allow, act0:deny.
Group group6: act1:allow, act3:allow, act2:deny.
For each question respond with allow or deny, listed in question order and separated by semicolons, e.g. 'allow;deny'.
Question 1: What is the effective decision for action act4?
Question 2: What is the effective decision for action act2?
```

**Answer:**

allow;deny

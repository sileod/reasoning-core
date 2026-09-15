## Level 0
### Example 1
**Prompt:**
Apply these migration operations, in the given order, to the flat record { 'd': y, 'a': x, 'e': True }:
1. if field 'f4' is absent, set it to 0
2. if field 'f8' is absent, set it to 0
Report the final value of each of the fields in the fixed order 'f4', 'f8', as 'path=value' pairs separated by '; ' (booleans as true/false).

**Answer:** f4=0; f8=0

### Example 2
**Prompt:**
Apply these migration operations, in the given order, to the flat record { 'd': y, 'a': 8,3, 'c': 7,3 }:
1. if field 'f2' is absent, set it to 0
2. split field 'a' on commas into fields ['f17', 'f19']
Report the final value of each of the fields in the fixed order 'f17', 'f19', 'f2', as 'path=value' pairs separated by '; ' (booleans as true/false).

**Answer:** f17=8; f19=3; f2=0

## Level 2
### Example 1
**Prompt:**
Apply these migration operations, in the given order, to the flat record { 'a': -2, 'd': 8, 'e': x, 'b': z, 'c': 10 }:
1. rename field 'a' to 'f13'
2. if field 'f3' is absent, set it to 1
3. rename field 'd' to 'f0'
4. if field 'f18' is absent, set it to 0
Report the final value of each of the fields in the fixed order 'f0', 'f13', 'f18', 'f3', as 'path=value' pairs separated by '; ' (booleans as true/false).

**Answer:** f0=8; f13=-2; f18=0; f3=1

### Example 2
**Prompt:**
Apply these migration operations, in the given order, to the flat record { 'b': -1,1,2, 'c': True, 'e': x, 'd': x, 'a': -8,0 }:
1. rename field 'd' to 'f14'
2. split field 'a' on commas into fields ['f9', 'f8']
3. split field 'b' on commas into fields ['f5', 'f16', 'f15']
4. if field 'f11' is absent, set it to null
Report the final value of each of the fields in the fixed order 'f11', 'f14', 'f15', 'f16', 'f5', 'f8', 'f9', as 'path=value' pairs separated by '; ' (booleans as true/false).

**Answer:** f11=null; f14=x; f15=2; f16=1; f5=-1; f8=0; f9=-8

## Level 5
### Example 1
**Prompt:**
Apply these migration operations, in the given order, to the flat record { 'd': -8, 'b': 10, 'a': -1, 'e': 15, 'c': x }:
1. rename field 'e' to 'f9'
2. if field 'f18' is absent, set it to null
3. if field 'f8' is absent, set it to 0
4. if field 'f11' is absent, set it to 0
5. if field 'f4' is absent, set it to 0
6. if field 'f16' is absent, set it to 0
7. if field 'f1' is absent, set it to 0
Report the final value of each of the fields in the fixed order 'f1', 'f11', 'f16', 'f18', 'f4', 'f8', 'f9', as 'path=value' pairs separated by '; ' (booleans as true/false).

**Answer:** f1=0; f11=0; f16=0; f18=null; f4=0; f8=0; f9=15

### Example 2
**Prompt:**
Apply these migration operations, in the given order, to the flat record { 'b': 15, 'c': x, 'e': z, 'd': 4,5,9, 'a': x }:
1. rename field 'a' to 'f19'
2. rename field 'c' to 'f6'
3. rename field 'e' to 'f11'
4. if field 'f0' is absent, set it to null
5. split field 'd' on commas into fields ['f1', 'f10', 'f3']
6. if field 'f15' is absent, set it to null
7. if field 'f5' is absent, set it to 1
Report the final value of each of the fields in the fixed order 'f0', 'f1', 'f10', 'f11', 'f15', 'f19', 'f3', 'f5', 'f6', as 'path=value' pairs separated by '; ' (booleans as true/false).

**Answer:** f0=null; f1=4; f10=5; f11=z; f15=null; f19=x; f3=9; f5=1; f6=x

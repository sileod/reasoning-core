# Level 0
## Example 1
**Answer**:
Extracted: m1
Bindings: kappa=C zeta=S

<details><summary>Prompt</summary>

```
Commands (in order):
object: defines kappa=C | uses zeta
archive:
  member m1: defines zeta=S | uses zeta
  member m2: defines zeta=S | uses omega

Object files are always loaded. An archive member is extracted only if it defines a symbol currently referenced by an already-loaded unit and not yet defined; extracted members load at that point and may satisfy or add needs.
Def strengths: S=strong, W=weak, C=common, I=internal(local). I never binds an external symbol. When several definitions of one symbol load, S beats C beats W; among equal strength the earliest in link order wins.
Report two lines: 'Extracted:' then the extracted members in link order (or 'none' if none), then 'Bindings:' then name=strength for every symbol bound by a loaded strong/weak/common definition or left unresolved, sorted by name; unresolved symbols get strength U.
Example format:
Extracted: m1 m2
Bindings: alpha=S beta=U
```
</details>

## Example 2
**Answer**:
Extracted: none
Bindings: alpha=U kappa=S

<details><summary>Prompt</summary>

```
Commands (in order):
object: defines kappa=S, iota=I | uses alpha
archive:
  member m1: defines chi=C | uses iota
  member m2: defines chi=S | uses chi

Object files are always loaded. An archive member is extracted only if it defines a symbol currently referenced by an already-loaded unit and not yet defined; extracted members load at that point and may satisfy or add needs.
Def strengths: S=strong, W=weak, C=common, I=internal(local). I never binds an external symbol. When several definitions of one symbol load, S beats C beats W; among equal strength the earliest in link order wins.
Report two lines: 'Extracted:' then the extracted members in link order (or 'none' if none), then 'Bindings:' then name=strength for every symbol bound by a loaded strong/weak/common definition or left unresolved, sorted by name; unresolved symbols get strength U.
Example format:
Extracted: m1 m2
Bindings: alpha=S beta=U
```
</details>

# Level 2
## Example 1
**Answer**:
Extracted: m1
Bindings: chi=S gamma=W kappa=C phi=S tau=W upsilon=U

<details><summary>Prompt</summary>

```
Commands (in order):
object: defines gamma=W | uses kappa phi
object: defines phi=S | uses upsilon tau
object: defines kappa=C | uses chi tau
archive:
  member m1: defines chi=S, tau=W, iota=I | uses kappa phi
  member m2: defines tau=W, chi=S, iota=I | uses chi upsilon
  member m3: defines chi=S | uses iota eta
archive:
  member m4: defines tau=S, chi=C, eta=I | uses iota tau
  member m5: defines chi=W, tau=S | uses iota kappa
  member m6: defines chi=S | uses tau phi

Object files are always loaded. An archive member is extracted only if it defines a symbol currently referenced by an already-loaded unit and not yet defined; extracted members load at that point and may satisfy or add needs.
Def strengths: S=strong, W=weak, C=common, I=internal(local). I never binds an external symbol. When several definitions of one symbol load, S beats C beats W; among equal strength the earliest in link order wins.
Report two lines: 'Extracted:' then the extracted members in link order (or 'none' if none), then 'Bindings:' then name=strength for every symbol bound by a loaded strong/weak/common definition or left unresolved, sorted by name; unresolved symbols get strength U.
Example format:
Extracted: m1 m2
Bindings: alpha=S beta=U
```
</details>

## Example 2
**Answer**:
Extracted: none
Bindings: delta=W epsilon=W lambda=U phi=U sigma=S zeta=U

<details><summary>Prompt</summary>

```
Commands (in order):
object: defines epsilon=W | uses zeta phi
object: defines sigma=S, zeta=I | uses sigma lambda
object: defines delta=W | uses epsilon zeta
archive:
  member m1: defines gamma=S, theta=W, zeta=I | uses gamma phi
  member m2: defines theta=C, gamma=S, phi=I | uses phi gamma
  member m3: defines gamma=S, zeta=I | uses sigma theta
archive:
  member m4: defines gamma=W | uses epsilon delta
  member m5: defines theta=C, gamma=C, zeta=I | uses delta lambda
  member m6: defines theta=S, gamma=S | uses delta lambda

Object files are always loaded. An archive member is extracted only if it defines a symbol currently referenced by an already-loaded unit and not yet defined; extracted members load at that point and may satisfy or add needs.
Def strengths: S=strong, W=weak, C=common, I=internal(local). I never binds an external symbol. When several definitions of one symbol load, S beats C beats W; among equal strength the earliest in link order wins.
Report two lines: 'Extracted:' then the extracted members in link order (or 'none' if none), then 'Bindings:' then name=strength for every symbol bound by a loaded strong/weak/common definition or left unresolved, sorted by name; unresolved symbols get strength U.
Example format:
Extracted: m1 m2
Bindings: alpha=S beta=U
```
</details>

# Level 5
## Example 1
**Answer**:
Extracted: m1 m2
Bindings: alpha=U chi=S kappa=U lambda=U mu=U omega=W omicron=S psi=W rho=U sigma=C tau=C theta=S upsilon=W xi=S

<details><summary>Prompt</summary>

```
Commands (in order):
object: defines omicron=S | uses kappa psi tau
object: defines upsilon=W, lambda=I | uses alpha theta omicron
object: defines sigma=C, lambda=I | uses omega xi chi
object: defines omega=W, lambda=I | uses lambda upsilon chi
object: defines psi=W, kappa=I | uses sigma tau rho
object: defines xi=S | uses omega alpha theta
archive:
  member m1: defines tau=C, theta=C, lambda=I | uses sigma mu kappa
  member m2: defines tau=C, chi=S, theta=S, kappa=I | uses psi omicron theta
  member m3: defines theta=S, lambda=I | uses mu alpha omega
  member m4: defines chi=S | uses sigma chi theta
archive:
  member m5: defines tau=S, theta=W, chi=W, lambda=I | uses psi omicron alpha
  member m6: defines tau=W | uses tau lambda kappa
  member m7: defines tau=S, theta=W, chi=W, lambda=I | uses psi kappa alpha
  member m8: defines tau=S, chi=W, theta=S | uses upsilon lambda omicron
archive:
  member m9: defines theta=S, chi=S, tau=S | uses sigma tau alpha
  member m10: defines theta=W, tau=S, chi=C | uses sigma rho upsilon
  member m11: defines theta=S | uses xi kappa omicron
  member m12: defines theta=C, tau=S, chi=S | uses kappa alpha omicron

Object files are always loaded. An archive member is extracted only if it defines a symbol currently referenced by an already-loaded unit and not yet defined; extracted members load at that point and may satisfy or add needs.
Def strengths: S=strong, W=weak, C=common, I=internal(local). I never binds an external symbol. When several definitions of one symbol load, S beats C beats W; among equal strength the earliest in link order wins.
Report two lines: 'Extracted:' then the extracted members in link order (or 'none' if none), then 'Bindings:' then name=strength for every symbol bound by a loaded strong/weak/common definition or left unresolved, sorted by name; unresolved symbols get strength U.
Example format:
Extracted: m1 m2
Bindings: alpha=S beta=U
```
</details>

## Example 2
**Answer**:
Extracted: m1 m2
Bindings: beta=S chi=U delta=C eta=U gamma=S iota=W kappa=U omega=U pi=C psi=C rho=W tau=U upsilon=W xi=W

<details><summary>Prompt</summary>

```
Commands (in order):
object: defines xi=W, tau=I | uses iota kappa eta
object: defines iota=W, chi=I | uses gamma tau iota
object: defines upsilon=W | uses iota psi chi
object: defines psi=C, tau=I | uses beta iota upsilon
object: defines delta=C | uses omega kappa rho
object: defines beta=S, chi=I | uses tau iota pi
archive:
  member m1: defines pi=C | uses iota xi chi
  member m2: defines pi=C, gamma=S, rho=W | uses beta rho eta
  member m3: defines pi=S, chi=I | uses omega eta pi
  member m4: defines gamma=C, pi=S, rho=S | uses beta kappa eta
archive:
  member m5: defines rho=S, gamma=S | uses upsilon omega gamma
  member m6: defines gamma=C | uses xi gamma kappa
  member m7: defines pi=S, gamma=C | uses eta beta upsilon
  member m8: defines gamma=C, pi=S, tau=I | uses omega iota rho
archive:
  member m9: defines gamma=W, rho=S, pi=C, tau=I | uses omega upsilon gamma
  member m10: defines gamma=S, pi=S, rho=S | uses chi xi rho
  member m11: defines rho=C, gamma=C | uses delta psi beta
  member m12: defines rho=S, tau=I | uses xi chi omega

Object files are always loaded. An archive member is extracted only if it defines a symbol currently referenced by an already-loaded unit and not yet defined; extracted members load at that point and may satisfy or add needs.
Def strengths: S=strong, W=weak, C=common, I=internal(local). I never binds an external symbol. When several definitions of one symbol load, S beats C beats W; among equal strength the earliest in link order wins.
Report two lines: 'Extracted:' then the extracted members in link order (or 'none' if none), then 'Bindings:' then name=strength for every symbol bound by a loaded strong/weak/common definition or left unresolved, sorted by name; unresolved symbols get strength U.
Example format:
Extracted: m1 m2
Bindings: alpha=S beta=U
```
</details>


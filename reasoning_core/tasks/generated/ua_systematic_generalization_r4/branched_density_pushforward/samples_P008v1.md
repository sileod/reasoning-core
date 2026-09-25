# samples_P008v1

Transport piecewise probability densities through noninjective maps by combining inverse-branch contributions and Jacobian factors; vary folds, flat regions, and composition, returning a density or atom mass.

(design_choice: Answer as a canonical piecewise-linear density string over fixed bins, with each bin's value a rational computed from summed inverse branches.)

## Level 0

**Prompt:**

A piecewise-constant probability density on [0,1] is pushed forward through piecewise-affine maps. Its total mass is 8/15.

Source density p (positive, piecewise-constant, total mass 8/15):
p(x) = 4/5 on [0,1/3), p(x) = 2/5 on [1/3,1)

Map f (piecewise affine, surjective onto [0,1], with a fold and no flat region):
on [0,1/3): f(x)=9/4*x+0 , on [1/3,2/3): f(x)=-1/4*x+5/6 , on [2/3,1): f(x)=1*x+0 

Map g (piecewise affine, surjective onto [0,1]):
on [0,1): g(x)=1*x+0 

Push p forward through f to get an intermediate density, then push that density forward through g, obtaining the distribution T on [0,1]. Partition [0,1] into the 4 equal bins [0,1/4), [1/4,1/2), [1/2,3/4), [3/4,1].

For each bin give the average density of the continuous part of T in the bin: (mass of the continuous part of T lying in the bin)/(bin width). A flat region of a map gathers the p-mass it receives into an atom at the flat region's value; list any atoms of T as location:mass.

Answer as the N bin densities -- a comma-separated list of reduced fractions -- then, if there are atoms, a vertical bar then the atoms (comma-separated, each location:mass, sorted by location). Example: "1/2,0,3/4,1|1/3:2/5".

**Answer:**

16/45,16/45,46/45,2/5

---

**Prompt:**

A piecewise-constant probability density on [0,1] is pushed forward through piecewise-affine maps. Its total mass is 47/60.

Source density p (positive, piecewise-constant, total mass 47/60):
p(x) = 4/5 on [0,11/12), p(x) = 3/5 on [11/12,1)

Map f (piecewise affine, surjective onto [0,1], with a fold and no flat region):
on [0,1/3): f(x)=5/2*x+0 , on [1/3,2/3): f(x)=-2*x+3/2 , on [2/3,1): f(x)=5/2*x+-3/2 

Map g (piecewise affine, surjective onto [0,1]):
on [0,1): g(x)=1*x+0 

Push p forward through f to get an intermediate density, then push that density forward through g, obtaining the distribution T on [0,1]. Partition [0,1] into the 4 equal bins [0,1/4), [1/4,1/2), [1/2,3/4), [3/4,1].

For each bin give the average density of the continuous part of T in the bin: (mass of the continuous part of T lying in the bin)/(bin width). A flat region of a map gathers the p-mass it receives into an atom at the flat region's value; list any atoms of T as location:mass.

Answer as the N bin densities -- a comma-separated list of reduced fractions -- then, if there are atoms, a vertical bar then the atoms (comma-separated, each location:mass, sorted by location). Example: "1/2,0,3/4,1|1/3:2/5".

**Answer:**

14/25,26/25,26/25,37/75

---

## Level 2

**Prompt:**

A piecewise-constant probability density on [0,1] is pushed forward through piecewise-affine maps. Its total mass is 3/4.

Source density p (positive, piecewise-constant, total mass 3/4):
p(x) = 2/5 on [0,1/4), p(x) = 4/5 on [1/4,1/3), p(x) = 4/5 on [1/3,3/4), p(x) = 1 on [3/4,1)

Map f (piecewise affine, surjective onto [0,1], with a fold and no flat region):
on [0,1/4): f(x)=13/4*x+0 , on [1/4,1/2): f(x)=-2*x+21/16 , on [1/2,3/4): f(x)=1*x+-3/16 , on [3/4,1): f(x)=7/4*x+-3/4 

Map g (piecewise affine, surjective onto [0,1]):
on [0,1): g(x)=1*x+0 

Push p forward through f to get an intermediate density, then push that density forward through g, obtaining the distribution T on [0,1]. Partition [0,1] into the 8 equal bins [0,1/8), [1/8,1/4), [1/4,3/8), [3/8,1/2), [1/2,5/8), [5/8,3/4), [3/4,7/8), [7/8,1].

For each bin give the average density of the continuous part of T in the bin: (mass of the continuous part of T lying in the bin)/(bin width). A flat region of a map gathers the p-mass it receives into an atom at the flat region's value; list any atoms of T as location:mass.

Answer as the N bin densities -- a comma-separated list of reduced fractions -- then, if there are atoms, a vertical bar then the atoms (comma-separated, each location:mass, sorted by location). Example: "1/2,0,3/4,1|1/3:2/5".

**Answer:**

8/65,8/65,47/65,86/65,110/91,498/455,379/455,4/7

---

**Prompt:**

A piecewise-constant probability density on [0,1] is pushed forward through piecewise-affine maps. Its total mass is 13/20.

Source density p (positive, piecewise-constant, total mass 13/20):
p(x) = 2/5 on [0,1/12), p(x) = 2/5 on [1/12,1/2), p(x) = 1 on [1/2,11/12), p(x) = 2/5 on [11/12,1)

Map f (piecewise affine, surjective onto [0,1], with a fold and no flat region):
on [0,1/4): f(x)=7/2*x+0 , on [1/4,1/2): f(x)=-1/4*x+15/16 , on [1/2,3/4): f(x)=-3/4*x+19/16 , on [3/4,1): f(x)=3/2*x+-1/2 

Map g (piecewise affine, surjective onto [0,1]):
on [0,1): g(x)=1*x+0 

Push p forward through f to get an intermediate density, then push that density forward through g, obtaining the distribution T on [0,1]. Partition [0,1] into the 8 equal bins [0,1/8), [1/8,1/4), [1/4,3/8), [3/8,1/2), [1/2,5/8), [5/8,3/4), [3/4,7/8), [7/8,1].

For each bin give the average density of the continuous part of T in the bin: (mass of the continuous part of T lying in the bin)/(bin width). A flat region of a map gathers the p-mass it receives into an atom at the flat region's value; list any atoms of T as location:mass.

Answer as the N bin densities -- a comma-separated list of reduced fractions -- then, if there are atoms, a vertical bar then the atoms (comma-separated, each location:mass, sorted by location). Example: "1/2,0,3/4,1|1/3:2/5".

**Answer:**

4/35,4/35,4/35,4/35,4/35,74/35,236/105,4/15

---

## Level 5

**Prompt:**

A piecewise-constant probability density on [0,1] is pushed forward through piecewise-affine maps. Its total mass is 17/30.

Source density p (positive, piecewise-constant, total mass 17/30):
p(x) = 1/5 on [0,1/12), p(x) = 2/5 on [1/12,5/12), p(x) = 4/5 on [5/12,1/2), p(x) = 4/5 on [1/2,3/4), p(x) = 2/5 on [3/4,11/12), p(x) = 1 on [11/12,1)

Map f (piecewise affine, surjective onto [0,1], with a fold and no flat region):
on [0,1/4): f(x)=5/2*x+0 , on [1/4,1/2): f(x)=-7/4*x+17/16 , on [1/2,3/4): f(x)=5/2*x+-17/16 , on [3/4,1): f(x)=3/4*x+1/4 

Map g (piecewise affine, surjective onto [0,1]):
on [0,1/4): g(x)=2*x+0 , on [1/4,1/2): g(x)=-3/4*x+11/16 , on [1/2,3/4): g(x)=1/4*x+3/16 , on [3/4,1): g(x)=5/2*x+-3/2 

Push p forward through f to get an intermediate density, then push that density forward through g, obtaining the distribution T on [0,1]. Partition [0,1] into the 14 equal bins [0,1/14), [1/14,1/7), [1/7,3/14), [3/14,2/7), [2/7,5/14), [5/14,3/7), [3/7,1/2), [1/2,4/7), [4/7,9/14), [9/14,5/7), [5/7,11/14), [11/14,6/7), [6/7,13/14), [13/14,1].

For each bin give the average density of the continuous part of T in the bin: (mass of the continuous part of T lying in the bin)/(bin width). A flat region of a map gathers the p-mass it receives into an atom at the flat region's value; list any atoms of T as location:mass.

Answer as the N bin densities -- a comma-separated list of reduced fractions -- then, if there are atoms, a vertical bar then the atoms (comma-separated, each location:mass, sorted by location). Example: "1/2,0,3/4,1|1/3:2/5".

**Answer:**

1/25,1/25,1/25,1/25,1108/525,2973/1750,226/125,22/125,16/75,16/75,16/75,41/150,8/15,8/15

---

**Prompt:**

A piecewise-constant probability density on [0,1] is pushed forward through piecewise-affine maps. Its total mass is 29/60.

Source density p (positive, piecewise-constant, total mass 29/60):
p(x) = 2/5 on [0,1/6), p(x) = 1 on [1/6,1/4), p(x) = 3/5 on [1/4,1/3), p(x) = 3/5 on [1/3,5/12), p(x) = 2/5 on [5/12,1)

Map f (piecewise affine, surjective onto [0,1], with a fold and no flat region):
on [0,1/4): f(x)=3/2*x+0 , on [1/4,1/2): f(x)=5/4*x+1/16 , on [1/2,3/4): f(x)=-3/4*x+17/16 , on [3/4,1): f(x)=2*x+-1 

Map g (piecewise affine, surjective onto [0,1]):
on [0,1/4): g(x)=1/4*x+0 , on [1/4,1/2): g(x)=9/4*x+-1/2 , on [1/2,3/4): g(x)=-3/4*x+1 , on [3/4,1): g(x)=9/4*x+-5/4 

Push p forward through f to get an intermediate density, then push that density forward through g, obtaining the distribution T on [0,1]. Partition [0,1] into the 14 equal bins [0,1/14), [1/14,1/7), [1/7,3/14), [3/14,2/7), [2/7,5/14), [5/14,3/7), [3/7,1/2), [1/2,4/7), [4/7,9/14), [9/14,5/7), [5/7,11/14), [11/14,6/7), [6/7,13/14), [13/14,1].

For each bin give the average density of the continuous part of T in the bin: (mass of the continuous part of T lying in the bin)/(bin width). A flat region of a map gathers the p-mass it receives into an atom at the flat region's value; list any atoms of T as location:mass.

Answer as the N bin densities -- a comma-separated list of reduced fractions -- then, if there are atoms, a vertical bar then the atoms (comma-separated, each location:mass, sorted by location). Example: "1/2,0,3/4,1|1/3:2/5".

**Answer:**

131/135,8/27,8/27,8/27,379/1350,16/75,58/75,26/15,329/225,4/45,4/45,4/45,4/45,4/45

---

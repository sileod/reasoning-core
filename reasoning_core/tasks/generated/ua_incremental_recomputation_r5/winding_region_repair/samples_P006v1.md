# Samples for P006v1: winding_region_repair

## Level 0

### Example 1

**Prompt**

An oriented closed polygonal path with vertices (x,y) = [0.509307,2.21473;-2.4624,4.96079;4.82199,4.30235;-2.53928,0.050717;1.89426,2.60642] has winding regions. Give each closed region a unique integer id by its winding number around the path. Then the path is edited: vertex index 2 is moved (the others stay fixed), making the new vertex list [0.509307,2.21473;-2.4624,4.96079;3.79874,5.02479;-2.53928,0.050717;1.89426,2.60642]. Recompute the winding regions of the new path. List, as 'region_id:new_label' pairs separated by ';', ONLY the regions whose winding label changed due to this single edit, sorted by region_id. Region ids and labels are integers. Do not list regions whose label stayed the same.

**Answer**

0:-1;8:-1;39:0;46:0;47:0;48:0;52:1;53:1;54:1;55:1;56:1;57:1;58:1

### Example 2

**Prompt**

An oriented closed polygonal path with vertices (x,y) = [-4.70968,4.10964;4.48217,2.74457;-2.21839,4.35201;1.52371,-0.271336;-2.90666,-2.62687] has winding regions. Give each closed region a unique integer id by its winding number around the path. Then the path is edited: the vertex at index 3 is deleted, making the new vertex list [-4.70968,4.10964;4.48217,2.74457;-2.21839,4.35201;-2.90666,-2.62687]. Recompute the winding regions of the new path. List, as 'region_id:new_label' pairs separated by ';', ONLY the regions whose winding label changed due to this single edit, sorted by region_id. Region ids and labels are integers. Do not list regions whose label stayed the same.

**Answer**

57:0

## Level 2

### Example 1

**Prompt**

An oriented closed polygonal path with vertices (x,y) = [-2.69072,2.44748;-0.840901,2.4865;-4.87845,-4.25723;-4.2223,-2.99903;-1.83557,-1.86239;-0.605824,-4.87634;4.92329,2.51833] has winding regions. Give each closed region a unique integer id by its winding number around the path. Then the path is edited: the vertex at index 6 is deleted, making the new vertex list [-2.69072,2.44748;-0.840901,2.4865;-4.87845,-4.25723;-4.2223,-2.99903;-1.83557,-1.86239;-0.605824,-4.87634]. Recompute the winding regions of the new path. List, as 'region_id:new_label' pairs separated by ';', ONLY the regions whose winding label changed due to this single edit, sorted by region_id. Region ids and labels are integers. Do not list regions whose label stayed the same.

**Answer**

0:-1;1:-1;2:-1;3:-1;4:-1;35:0;36:0;37:0;38:0;39:0;40:0;41:0;42:0;43:0;44:0;45:0;46:0;47:0;48:0;49:0;50:0;51:0

### Example 2

**Prompt**

An oriented closed polygonal path with vertices (x,y) = [-2.25399,4.74974;-0.767193,2.27458;-0.16665,2.89299;-4.06164,3.84839;3.14661,-4.80336;1.98439,0.32955;-2.46357,-1.64045] has winding regions. Give each closed region a unique integer id by its winding number around the path. Then the path is edited: the vertex at index 1 is deleted, making the new vertex list [-2.25399,4.74974;-0.16665,2.89299;-4.06164,3.84839;3.14661,-4.80336;1.98439,0.32955;-2.46357,-1.64045]. Recompute the winding regions of the new path. List, as 'region_id:new_label' pairs separated by ';', ONLY the regions whose winding label changed due to this single edit, sorted by region_id. Region ids and labels are integers. Do not list regions whose label stayed the same.

**Answer**

9:-1

## Level 5

### Example 1

**Prompt**

An oriented closed polygonal path with vertices (x,y) = [-4.41751,0.484385;-0.61818,0.935686;-3.12325,-2.93225;0.927294,-3.05387;-3.68821,-2.44261;2.22322,-4.40137;0.94238,-1.84609;-2.65363,-2.70617;0.419712,0.0452711;4.28723,3.74015] has winding regions. Give each closed region a unique integer id by its winding number around the path. Then the path is edited: the vertex at index 7 is deleted, making the new vertex list [-4.41751,0.484385;-0.61818,0.935686;-3.12325,-2.93225;0.927294,-3.05387;-3.68821,-2.44261;2.22322,-4.40137;0.94238,-1.84609;0.419712,0.0452711;4.28723,3.74015]. Recompute the winding regions of the new path. List, as 'region_id:new_label' pairs separated by ';', ONLY the regions whose winding label changed due to this single edit, sorted by region_id. Region ids and labels are integers. Do not list regions whose label stayed the same.

**Answer**

47:1;50:1;51:1;53:1;66:2

### Example 2

**Prompt**

An oriented closed polygonal path with vertices (x,y) = [2.6496,3.11053;2.24639,-4.80088;4.57501,0.466855;-0.408588,3.49362;-0.667239,-0.708513;3.37827,2.73364;-1.53334,3.37648;-4.27633,-2.95311;4.32157,-1.44746;-3.72378,-2.22245] has winding regions. Give each closed region a unique integer id by its winding number around the path. Then the path is edited: vertex index 6 is moved (the others stay fixed), making the new vertex list [2.6496,3.11053;2.24639,-4.80088;4.57501,0.466855;-0.408588,3.49362;-0.667239,-0.708513;3.37827,2.73364;-0.827626,2.85034;-4.27633,-2.95311;4.32157,-1.44746;-3.72378,-2.22245]. Recompute the winding regions of the new path. List, as 'region_id:new_label' pairs separated by ';', ONLY the regions whose winding label changed due to this single edit, sorted by region_id. Region ids and labels are integers. Do not list regions whose label stayed the same.

**Answer**

37:0;79:1

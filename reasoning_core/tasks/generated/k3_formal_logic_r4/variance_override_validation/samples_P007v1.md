## Level 0

Aliases:
A0 = List<Dict<String,Int>>

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type Set<A0>. Follow the 0-indexed child path 1 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

Aliases:
A0 = Dict<Int,Seq<String>>
A1 = ((Bool -> String) -> (Bool -> Float))

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type (A0 -> A1). Follow the 0-indexed child path 2 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

Aliases:
A0 = Dict<Bool,Dict<Bool,Float>>

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type Dict<Bool,A0>. Follow the 0-indexed child path 2 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

Aliases:
A0 = Dict<String,Dict<Float,String>>

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type Set<A0>. Follow the 0-indexed child path 1.1 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: invariant

Aliases:
A0 = (Dict<Int,Int> -> Dict<String,Bool>)

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type List<A0>. Follow the 0-indexed child path 1.1.2 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: invariant

Aliases:
A0 = Dict<Bool,(Float -> Bool)>

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type List<A0>. Follow the 0-indexed child path 1.2 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

## Level 2

Aliases:
A0 = List<List<Dict<String,(String -> Bool)>>>

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type Set<A0>. Follow the 0-indexed child path 1.1.1 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

Aliases:
A0 = Set<(((Int -> Bool) -> Seq<String>) -> Seq<Seq<Int>>)>
A1 = (Seq<(Set<String> -> (Int -> Float))> -> Seq<((Float -> Int) -> Dict<String,Bool>)>)

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type (A0 -> A1). Follow the 0-indexed child path 1 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: contravariant

Aliases:
A0 = Dict<String,Set<Dict<Float,Dict<Bool,String>>>>
A1 = (List<(Set<String> -> List<Int>)> -> (List<(Bool -> String)> -> Dict<String,(Float -> Float)>))

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type (A0 -> A1). Follow the 0-indexed child path 2 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

Aliases:
A0 = Set<(List<Set<String>> -> Seq<(String -> Int)>)>

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type Seq<A0>. Follow the 0-indexed child path 1 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

Aliases:
A0 = Seq<((Set<Int> -> Dict<String,Bool>) -> Dict<String,Dict<Int,Float>>)>

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type List<A0>. Follow the 0-indexed child path 1 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

Aliases:
A0 = Dict<Float,List<Seq<List<Int>>>>
A1 = Set<Seq<List<Dict<Float,String>>>>

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type (A0 -> A1). Follow the 0-indexed child path 1 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: contravariant

## Level 5

Aliases:
A0 = List<Set<List<(Set<Dict<String,List<String>>> -> (Seq<(String -> Float)> -> (Set<Int> -> List<Bool>)))>>>

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type Seq<A0>. Follow the 0-indexed child path 1 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

Aliases:
A0 = List<Set<Dict<String,Set<(((String -> String) -> Seq<Int>) -> Dict<Int,Seq<String>>)>>>>
A1 = (Dict<String,List<Seq<Dict<String,Dict<Int,Dict<Bool,Int>>>>>> -> Set<List<(Seq<Set<Dict<Bool,Bool>>> -> (Set<(Int -> String)> -> ((Float -> Bool) -> (String -> Int))))>>)

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type (A0 -> A1). Follow the 0-indexed child path 2.1 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: invariant

Aliases:
A0 = Seq<(((Set<Set<List<Bool>>> -> Dict<Float,Set<(String -> String)>>) -> Seq<(((String -> Float) -> Set<Bool>) -> Seq<Set<Bool>>)>) -> Seq<Dict<Float,List<Seq<Seq<Int>>>>>)>
A1 = (List<List<Set<List<List<Seq<String>>>>>> -> (Dict<Int,((Dict<String,Dict<String,Int>> -> Set<Set<Float>>) -> Seq<Seq<(Int -> Float)>>)> -> ((Dict<Bool,Seq<Dict<Float,Int>>> -> (Dict<Bool,(Float -> Bool)> -> Dict<Float,(Int -> Bool)>)) -> Dict<Float,Dict<Bool,Set<Dict<Bool,Int>>>>)))

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type (A0 -> A1). Follow the 0-indexed child path 2.2 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

Aliases:
A0 = (List<Seq<Dict<Int,Set<Dict<Bool,(Float -> Int)>>>>> -> Seq<List<Set<Set<Seq<(Int -> Float)>>>>>)

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type Set<A0>. Follow the 0-indexed child path 1.2 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

Aliases:
A0 = Seq<List<Seq<List<Seq<Dict<Float,Set<Int>>>>>>>

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type List<A0>. Follow the 0-indexed child path 1 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant

Aliases:
A0 = List<Seq<Set<(Dict<Float,((Float -> Bool) -> (String -> Int))> -> Dict<String,((String -> String) -> Seq<Int>)>)>>>

We define variance rules: List, Set and Seq keep their parameter covariant; Dict keeps its key invariant and its value covariant; in a function A -> B, A is contravariant and B is covariant. Combining polarities on one position: any invariant makes it invariant, and a mix of covariant and contravariant is invariant.
Consider the type List<A0>. Follow the 0-indexed child path 1.1 from the root, expanding any named alias you meet as the type it stands for. Report the effectively allowed polarity at the reached parameter using exactly one of the words covariant, contravariant, or invariant; write only that single word.
Answer: covariant


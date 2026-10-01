/-
Random rewrite walks over Mathlib, for `mathlib_rewrite` (mathlib_rewrite.py).

`rcEqLemmas path` lists Mathlib's equational theorems (one-time scan). `rcWalk lem steps seed` starts
from the left-hand side of `lem`, with its binders as context, and repeatedly applies a random rewrite
found by the `rw?` engine (`Lean.Meta.Rewrites.findRewrites`). Generic filters keep the walk readable
and its steps unambiguous: no revisits, each lemma at most once, bounded growth, no definitional
plumbing, no padding (a simplification used backwards), at most one pure reordering, no class-axiom
projections, a vocabulary budget, and the rewritten pattern must match exactly one subterm.
-/
open Lean Meta Rewrites

def rcPP (e : Expr) : MetaM String := return toString (← ppExpr e)

/-- Fully parenthesized print, used to check the Python term normalizer against Lean's parser. -/
def rcPPParens (e : Expr) : MetaM String :=
  return toString (← withOptions (·.setBool `pp.parens true) (ppExpr e))

def rcSub (k : Nat) : String := String.map (fun c => if c.isDigit then Char.ofNat (0x2080 + (c.toNat - '0'.toNat)) else c) (toString k)

/-- Canonical binder names: a bound variable at nesting depth k is `xₖ`, so the printed answer is unique. -/
partial def rcCanon (e : Expr) (depth : Nat := 0) : Expr :=
  let nm := Name.mkSimple s!"x{rcSub (depth + 1)}"
  match e with
  | .lam _ d b bi => .lam nm (rcCanon d depth) (rcCanon b (depth + 1)) bi
  | .forallE _ d b bi => .forallE nm (rcCanon d depth) (rcCanon b (depth + 1)) bi
  | .letE _ t v b nd => .letE nm (rcCanon t depth) (rcCanon v depth) (rcCanon b (depth + 1)) nd
  | .app f a => .app (rcCanon f depth) (rcCanon a depth)
  | .mdata m b => .mdata m (rcCanon b depth)
  | .proj n i b => .proj n i (rcCanon b depth)
  | e => e

/-- Distinct subterms of `t` that the `symm`-side of lemma `n` matches, as `rw` would (reducible). -/
def rcMatches (n : Name) (symm : Bool) (t : Expr) : MetaM Nat := do
  let mut found : Array Expr := #[]
  let mut todo : Array Expr := #[t]
  while h : todo.size > 0 do
    let s := todo.back; todo := todo.pop
    if !s.hasLooseBVars && !found.contains s then
      let c ← mkConstWithFreshMVarLevels n
      let (_, _, ty) ← forallMetaTelescopeReducing (← inferType c)
      if let some (_, l, r) := ty.eq? then
        if ← withoutModifyingState (withReducible (isDefEq (if symm then r else l) s)) then
          found := found.push s
    match s with
    | .app f a => todo := todo.push f |>.push a
    | .lam _ d b _ | .forallE _ d b _ => todo := todo.push d |>.push b
    | .mdata _ e | .proj _ _ e => todo := todo.push e
    | _ => pure ()
  return found.size

/-- Can lemma `n`, in direction `symm`, make a step? The produced side must be determined by the matched side
(no variable that appears only in the result), and must not contain the matched side: that is padding, a
simplification used backwards (`← compl_compl_compl : aᶜ ↦ aᶜᶜᶜ`, `← sup_left_idem`, `← mul_one`).
Class axioms (`AddCommMagma.add_comm`) are skipped: `rw?` also finds their theorem form (`add_comm`). -/
def rcUsable (n : Name) (symm : Bool) : MetaM Bool := do
  if (← getEnv).isProjectionFn n then return false
  let (xs, bis, ty) ← forallMetaTelescopeReducing (← inferType (← mkConstWithFreshMVarLevels n))
  let some (_, l, r) := ty.eq? | return false
  let (src, tgt) := if symm then (r, l) else (l, r)
  let (src, tgt) := (← instantiateMVars src, ← instantiateMVars tgt)
  if src.occurs tgt then return false
  let srcM := src.collectMVars {} |>.result
  let tgtM := tgt.collectMVars {} |>.result
  return (xs.zip bis).all fun (x, bi) =>
    bi.isInstImplicit || !tgtM.contains x.mvarId! || srcM.contains x.mvarId!

/-- Non-instance constants of `e`: its mathematical vocabulary. -/
def rcVocab (e : Expr) : MetaM NameSet := do
  let mut out : NameSet := {}
  for c in e.getUsedConstants do
    unless ← isInstance c do out := out.insert c
  return out

/-- A local as a Lean binder, so the context can be pasted back into Lean. -/
def rcBinder (x : Expr) : MetaM (Option String) := do
  let d ← x.fvarId!.getDecl
  let ty ← rcPP d.type
  match d.binderInfo with
  | .instImplicit => return some s!"[{ty}]"
  | bi =>
    if d.userName.hasMacroScopes then return none
    return some (if bi.isExplicit then s!"({d.userName} : {ty})" else s!"\{{d.userName} : {ty}}")

/-- Elaborate `s` against the local context; the same term as `e` up to instances? -/
def rcSame (s : String) (e : Expr) : MetaM Bool := do
  let .ok stx := Parser.runParserCategory (← getEnv) `term s | return false
  try
    let a ← (Elab.Term.withoutErrToSorry (Elab.Term.elabTermEnsuringType stx (← inferType e) <* Elab.Term.synthesizeSyntheticMVarsNoPostponing)).run'
    let a ← instantiateMVars a
    if a.hasMVar then return false
    withoutModifyingState (withReducibleAndInstances (isDefEq a e))
  catch _ => return false

def rcShuffle (a : Array α) : IO (Array α) := do
  let mut a := a
  for i in [0:a.size] do
    let j ← IO.rand i (a.size - 1)
    a := a.swapIfInBounds i j
  return a

def rcSize (e : Expr) : MetaM Nat := return (← rcPP e).length

/-- The leaves of `e` (constants, locals, literals), sorted: equal for two terms that differ only by reordering. -/
partial def rcLeaves (e : Expr) : Array String :=
  let rec go (e : Expr) (acc : Array String) : Array String :=
    match e with
    | .app f a => go a (go f acc)
    | .lam _ d b _ | .forallE _ d b _ => go b (go d acc)
    | .letE _ t v b _ => go b (go v (go t acc))
    | .mdata _ b | .proj _ _ b => go b acc
    | e => acc.push (toString e)
  (go e #[]).qsort (· < ·)

/-- A random rewrite walk from the left-hand side of `lem`, with generic filters. -/
abbrev RcCache := IO.Ref (Std.HashMap (Name × Bool) Bool)

def rcWalk (lem : Name) (steps : Nat) (seed : Nat) (maxLen : Nat := 160) (budget : Nat := 1) (cache : RcCache)
    (deadline : Nat := 0) : MetaM Json := do
  IO.setRandSeed seed
  let info ← getConstInfo lem
  forallTelescopeReducing info.type fun xs concl => do
    let some (_, lhs, _) := concl.eq? | return Json.mkObj [("error", "not an equation")]
    let some ctx := (← xs.mapM rcBinder).mapM id | return Json.mkObj [("error", "inaccessible binder name")]
    let ref ← createModuleTreeRef
    let hyps ← localHypotheses
    let lhs := rcCanon lhs
    let mut t := lhs
    let mut seen : Array Expr := #[lhs]
    let mut used : NameSet := NameSet.empty.insert lem  -- its own left-hand side: a free first step
    let mut shown : Array String := #[← rcPP lhs]  -- distinct as printed, not only as terms
    let mut terms : Array Json := #[Json.str (← rcPP t)]
    let mut parens : Array Json := #[Json.str (← rcPPParens t)]
    let mut rws : Array Json := #[]
    let mut altNames : Array (Array Name) := #[]
    let mut rejected : Array Nat := #[0, 0, 0, 0, 0]
    let mut reordered := false  -- a pure reordering (comm, swap) is allowed once per walk
    let mut vocab ← rcVocab lhs
    let mut spent := 0
    for _ in [0:steps] do
      let goal := (← mkFreshExprMVar (← mkEq t t)).mvarId!
      -- cheap index lookup, then execute candidates in random order and keep the first that passes
      let cands := (← rewriteCandidates hyps ref t).filterMap fun (l, symm, w) =>
        match l with | .inr n => if used.contains n then none else some (n, symm, w) | .inl _ => none
      let cands ← rcShuffle cands
      let cands := if (← IO.rand 0 9) < 6 then cands.filter (!·.2.1) ++ cands.filter (·.2.1) else cands
      let len ← rcSize t
      let mctx ← getMCtx
      let leaves := rcLeaves t
      let mut pick : Option (Expr × Name × Bool × Bool) := none
      for (name, symm, w) in cands do
        if deadline > 0 && (← IO.monoMsNow) > deadline then break  -- out of time: keep the walk so far
        let det ← match (← cache.get)[(name, symm)]? with
          | some b => pure b
          | none => do let b ← rcUsable name symm; cache.modify (·.insert (name, symm) b); pure b
        unless det do rejected := rejected.modify 2 (· + 1); continue
        let some r ← withoutModifyingState (withMCtx mctx (rwLemma mctx goal t .assumption (.inr name) symm w)) | continue
        let eNew? ← withMCtx r.mctx do
          let eNew := rcCanon (← instantiateMVars r.result.eNew)
          return if eNew.hasMVar || seen.contains eNew then none else some eNew
        let some eNew := eNew? | continue
        let newText ← rcPP eNew
        let newLen := newText.length
        if shown.contains newText then continue
        let perm := rcLeaves eNew == leaves
        if perm && reordered then rejected := rejected.modify 4 (· + 1); continue
        if (newText.splitOn "⋯").length > 1 || (newText.splitOn "✝").length > 1 then rejected := rejected.modify 0 (· + 1); continue
        if newLen > maxLen || newLen > 2 * len + 10 || (symm && 10 * newLen > 13 * len + 60) then rejected := rejected.modify 0 (· + 1); continue
        let fresh := (← rcVocab eNew).toList.filter (!vocab.contains ·)
        if spent + fresh.length > budget then rejected := rejected.modify 3 (· + 1); continue
        if ← withoutModifyingState (try withTransparency .default (isDefEq t eNew) catch _ => pure true) then
          rejected := rejected.modify 1 (· + 1); continue
        if (← rcMatches name symm t) != 1 then rejected := rejected.modify 2 (· + 1); continue
        pick := some (eNew, name, symm, perm)
        break
      let some (eNew, name, symm, perm) := pick | break
      reordered := reordered || perm
      -- other lemmas that also rewrite this term: distractors for the prompt's lemma glossary
      let mut alts : Array Name := #[]  -- statements are printed only once the walk succeeds
      for (n, _, _) in cands do
        if alts.size ≥ 4 then break
        unless n == name || used.contains n || alts.contains n do alts := alts.push n
      used := used.insert name
      let fresh := (← rcVocab eNew).toList.filter (!vocab.contains ·)
      spent := spent + fresh.length
      vocab := fresh.foldl NameSet.insert vocab
      let stmt ← rcPP (← getConstInfo name).type
      rws := rws.push (Json.mkObj [("lemma", toString name), ("symm", symm), ("statement", stmt)])
      altNames := altNames.push alts
      t := eNew
      seen := seen.push eNew
      shown := shown.push (← rcPP t)
      terms := terms.push (Json.str (← rcPP t))
      parens := parens.push (Json.str (← rcPPParens t))
    -- every printed term must denote exactly its term when pasted back into Lean, so that every prefix
    -- of the walk is itself a walk; cut the walk before the first term that does not
    let mut ok := 0
    for e in seen do
      unless ← rcSame (← rcPP e) e do break
      ok := ok + 1
    if ok == 0 then return Json.mkObj [("error", "printed term does not round-trip")]
    let mut steps : Array Json := #[]
    for (rw, names) in (rws.zip altNames).extract 0 (ok - 1) do
      let alts ← names.mapM fun n => do
        return Json.mkObj [("lemma", toString n), ("statement", ← rcPP (← getConstInfo n).type)]
      steps := steps.push (rw.setObjVal! "alts" (Json.arr alts))
    return Json.mkObj [("start", toString lem), ("universes", toJson (info.levelParams.map toString)),
      ("context", Json.arr (ctx.map Json.str)), ("terms", Json.arr (terms.extract 0 ok)), ("parens", Json.arr (parens.extract 0 ok)),
      ("steps", Json.arr steps), ("rejected_size_plumbing_ambiguous_vocab_reorder", toJson rejected.toList)]

/-- One walk per start lemma, in one REPL call; failures come back as `{"error": ...}`. Each walk gets
`heartbeats` (thousands) and, if `walkMs` > 0, stops extending after `walkMs` milliseconds. -/
def rcBatch (lems : Array Name) (steps seed maxLen budget : Nat) (heartbeats : Nat := 50000) (walkMs : Nat := 0) :
    MetaM Json := do
  let cache : RcCache ← IO.mkRef {}
  let mut out := #[]
  for i in [0:lems.size] do
    -- each walk gets its own heartbeat budget, and running out of it (a runtime exception, which plain
    -- `try` does not catch) costs that walk only, not the batch
    let now ← IO.monoMsNow
    let deadline := if walkMs == 0 then 0 else now + walkMs
    let w ← withoutModifyingState <| withCurrHeartbeats <|
      withTheReader Core.Context ({ · with maxHeartbeats := heartbeats * 1000 }) <|
      tryCatchRuntimeEx (rcWalk lems[i]! steps (seed + i) maxLen budget cache deadline)
        (fun _ => pure (Json.mkObj [("error", "exception")]))
    out := out.push (w.setObjVal! "start" (toString lems[i]!))
  return Json.arr out

/-- Mathlib's equational theorems: name, module, binder count, lhs depth. -/
def rcEqLemmas (path : String) : MetaM Unit := do
  let env ← getEnv
  let mut lines : Array String := #[]
  for (c, info) in env.constants.toList do
    if c.isInternal || c.isImplementationDetail then continue
    let .thmInfo _ := info | continue
    let some mod := env.getModuleIdxFor? c | continue
    let modName := env.header.moduleNames[mod.toNat]!
    unless (`Mathlib).isPrefixOf modName do continue
    let (hyps, _, concl) ← forallMetaTelescopeReducing info.type
    if let some (_, lhs, _) := concl.eq? then
      lines := lines.push s!"{c}\t{modName}\t{hyps.size}\t{lhs.approxDepth.toNat}"
  IO.FS.writeFile path (String.intercalate "\n" lines.toList)

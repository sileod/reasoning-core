#!/usr/bin/env python3
"""artifacts.py — paper artifacts named by WHAT THEY SHOW, over one shared cell layer.

Design goals (all satisfied here so the paper can be built from partial, live results):
  • named by role, not mechanism  → @artifact("scale_crossover_ladder", shows="…")
  • code reuse                     → every artifact reads cells through ONE data layer (find/stat/reward)
  • seed-count-agnostic            → renders whatever exists; every number carries its n (1 seed ⇒ '*')
  • pair discussion ⇄ artifact     → each cited number is a CLAIM 'artifact.key'. Prose cites \\clm{artifact.key}
                                     (auto-refreshes) and wraps its text in %%<artifact:ID>…%%</artifact:ID>.
  • refresh signal                 → `status` diffs claims vs last `freeze` and (with --paper) greps the
                                     draft for the IDs whose value moved → tells you exactly what prose to revisit.

Run:  python -m paper_exports.artifacts build [id|all] | list | freeze | status [--paper DIR]
"""
import argparse, glob, json, re, time
from pathlib import Path
from statistics import mean, pstdev

OUT = Path(__file__).resolve().parent
PR = OUT.parent / "per_task_results"
TEX = OUT                       # paper-facing .tex — the paper's `generated/` symlink points HERE, so \input{generated/<id>}
GEN = OUT / "generated"         # bookkeeping only (.md tables, claims.json/freeze) — never \input'd
RX = re.compile(r"influence_COLL-([a-z_]+)_([A-Za-z0-9]+)_S(\d+)_T(\d+)_M(\d+)_fwdolci_pretrained\.json$")
MODELS = {"HL135": "135M", "HL360": "360M", "HL17": "1.7B", "HLOLMO": "OLMo-1B", "HL3B": "3B"}
REASON = ["bbh", "mmlu_math_cloze", "mmlu_logic_cloze"]        # reasoning-transfer legs (dev)

# ── shared data layer ─────────────────────────────────────────────────────────
def _arm(path):
    d = json.loads(Path(path).read_text())
    return d.get("baseline") or {}, (d.get("tasks") or {}).get("__COLLECTION__")

def red(path, leg):
    """%NLL-reduction on one leg from one cell; None if the cell is empty/mid-write/missing the leg."""
    b, a = _arm(path)
    if not a or a.get(leg + "_delta") is None or not b.get(leg + "_nll"):
        return None
    return -a[leg + "_delta"] / b[leg + "_nll"] * 100.0

def find(coll, tag, T, mix=20):
    """{seed: path} for every COMPLETE cell at this protocol point (any number of seeds)."""
    out = {}
    for f in glob.glob(str(PR / f"influence_COLL-{coll}_{tag}_S*_T{T}_M{mix}_fwdolci_pretrained.json")):
        m = RX.search(f)
        if m and _arm(f)[1]:
            out[int(m.group(3))] = f
    return out

def stat(coll, tag, T, legs=REASON, mix=20):
    """(mean, sem, n) of the seed-averaged mean-over-legs transfer score. n=0 ⇒ nothing yet."""
    per_seed = []
    for p in find(coll, tag, T, mix).values():
        vals = [red(p, l) for l in legs]
        vals = [v for v in vals if v is not None]
        if vals:
            per_seed.append(mean(vals))
    if not per_seed:
        return (float("nan"), 0.0, 0)
    return (mean(per_seed), pstdev(per_seed) / len(per_seed) ** .5 if len(per_seed) > 1 else 0.0, len(per_seed))

def reward(coll, tag):
    """(mean end-of-train solve-rate, n) pooled over all reward-bearing cells for this model×collection."""
    vs = []
    for T in (300, 600, 1200, 2400, 4800):
        for p in find(coll, tag, T).values():
            r = _arm(p)[1].get("reward_final")
            if r is not None:
                vs.append(r)
    return (mean(vs), len(vs)) if vs else (float("nan"), 0)

# ── claims registry (single source of truth for every inline number) ──────────
CLAIMS, ART = {}, {}
def claim(cid, value, fmt="{:+.2f}", n=None, note=""):
    """Register a number cited in prose; returns it rendered (with '*' when single-seed)."""
    s = fmt.format(value) + ("*" if n == 1 else "")
    CLAIMS[cid] = {"value": round(value, 4), "render": s, "n": n, "note": note}
    return s

def artifact(aid, shows):
    def deco(fn): ART[aid] = (shows, fn); return fn
    return deco

def md_table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|",
                      *("| " + " | ".join(map(str, r)) + " |" for r in rows)])

def tex_esc(s):
    s = str(s)
    for a, b in [("±", r"$\pm$"), ("—", "--"), ("−", r"$-$"), ("≪", r"$\ll$"), ("⊥", r"$\perp$"),
                 ("%", r"\%"), ("&", r"\&")]:
        s = s.replace(a, b)
    return s.replace("*", r"$^{*}$").replace("_", r"\_")

def tex_table(aid, shows, headers, rows, note=""):
    """A ready-to-\\input booktabs float (author adds nothing; \\label{tab:<id>})."""
    body = [r"\begin{table}[t]\centering", f"\\caption{{{tex_esc(shows)}}}\\label{{tab:{aid}}}",
            f"\\begin{{tabular}}{{l{'c' * (len(headers) - 1)}}}", r"\toprule",
            " & ".join(tex_esc(h) for h in headers) + r" \\", r"\midrule",
            *(" & ".join(tex_esc(c) for c in r) + r" \\" for r in rows), r"\bottomrule", r"\end{tabular}"]
    if note:
        body.append(r"\\[2pt]{\footnotesize " + tex_esc(note) + "}")
    return "\n".join(body + [r"\end{table}"])

def cell(m, s, n):
    return "—" if n == 0 else f"{m:+.2f}±{s:.2f}" + ("*" if n == 1 else "")

# ── artifacts (named by what they SHOW; all reuse the data layer above) ────────
@artifact("main_transfer_table", shows="Reasoning-transfer %NLL-red for every collection × model at T300 (headline table)")
def _main(T=300):
    tags = [t for t in MODELS if any(find(c, t, T) for c in ("rc", "rgym"))]
    colls = ["rc", "rgym", "rgym_noho", "synlogic", "pw"]
    rows = []
    for c in colls:
        row = [c]
        for t in tags:
            m, s, n = stat(c, t, T); row.append(cell(m, s, n))
            if c in ("rc", "rgym"):
                claim(f"main_transfer_table.{c}_{MODELS[t]}", m, n=n)
        rows.append(row)
    for t in tags:                                             # rc−rgym lead per model = the headline number
        (rm, _, rn), (gm, _, gn) = stat("rc", t, T), stat("rgym", t, T)
        if rn and gn: claim(f"main_transfer_table.lead_{MODELS[t]}", rm - gm, n=min(rn, gn))
    return (["collection"] + [MODELS[t] for t in tags], rows)

@artifact("scale_crossover_ladder", shows="rc−rgym transfer lead vs training steps, per model (the scale/compute crossover; defeats 'rc only easier for small models')")
def _ladder():
    Ts = [300, 600, 1200, 2400, 4800]
    rows = []
    for t in [x for x in MODELS if any(find("rc", x, T) for T in Ts)]:
        row = [MODELS[t]]
        for T in Ts:
            (rm, _, rn), (gm, _, gn) = stat("rc", t, T), stat("rgym", t, T)
            n = min(rn, gn)
            row.append(claim(f"scale_crossover_ladder.{MODELS[t]}_T{T}", rm - gm, n=n) if n else "—")
        rows.append(row)
    return (["model / steps"] + [f"T{T}" for T in Ts], rows)

@artifact("saturation_reward_table", shows="End-of-training solve-rate (free-gen reward) per collection × model — learnability/headroom, NOT transfer")
def _reward():
    colls = ["rc", "rgym", "rgym_noho", "synlogic", "pw"]
    tags = [t for t in MODELS if any(reward(c, t)[1] for c in colls)]
    rows = []
    for c in colls:
        row = [c]
        for t in tags:
            r, n = reward(c, t)
            row.append(claim(f"saturation_reward_table.{c}_{MODELS[t]}", r, "{:.3f}", n=n) if n else "—")
        rows.append(row)
    return (["collection"] + [MODELS[t] for t in tags], rows,
            "pooled over available steps per cell; n annotated. Reward = task.score_answer on held-out aux, instruct-mode.")

@artifact("difficulty_confound_rebuttal", shows="Composed rebuttal to 'rc helps only because it is easier for small models' (reuses ladder + reward claims)")
def _rebuttal():
    L = lambda k: CLAIMS.get(f"scale_crossover_ladder.{k}", {}).get("render", "—")
    R = lambda k: CLAIMS.get(f"saturation_reward_table.{k}", {}).get("render", "—")
    return ("**Claim to defeat:** rc's edge is a small-model-difficulty artifact → vanishes at scale.\n\n"
            "1. **Scale-persistence** — rc−rgym lead at 3B: "
            f"T300 {L('3B_T300')} → T600 {L('3B_T600')} → T1200 {L('3B_T1200')} → T2400 {L('3B_T2400')}. "
            "rc crosses ahead by T600 and (seed 43) re-widens at T2400 as rgym saturates.\n"
            f"2. **Widening on a fresh small base (135M):** {L('135M_T300')} → {L('135M_T600')} → {L('135M_T1200')}.\n"
            f"3. **Headroom** — 3B still solves only rc {R('rc_3B')} by free-gen (≪1.0): learnable, not trivial.\n"
            "4. **Difficulty ⊥ transfer** across collections (pw easy+useless, synlogic hard+useless, rc learnable+useful).\n\n"
            "_'*' = single-seed (provisional). Never argue 'rc is hard' — its reward is highest; argue persistence + headroom._")

# ── build / doc / refresh ─────────────────────────────────────────────────────
def emit(aid, content):
    """Table artifact (headers, rows[, note]) → .md (human) + .tex (ready \\input float).
       Prose artifact (str) → .md only (its numbers live in claims.tex via \\clm)."""
    shows = ART[aid][0]
    hdr = f"artifact:{aid} | shows: {shows} | generated: {time.strftime('%Y-%m-%d %H:%M')}"
    if isinstance(content, tuple):
        headers, rows = content[0], content[1]; note = content[2] if len(content) > 2 else ""
        md = md_table(headers, rows) + (f"\n\n_{note}_" if note else "")
        (TEX / f"{aid}.tex").write_text(f"% {hdr}\n" + tex_table(aid, shows, headers, rows, note) + "\n")
    else:
        md = content
    (GEN / f"{aid}.md").write_text(f"<!-- {hdr} -->\n\n" + md + "\n")
    return md

def build(which):
    GEN.mkdir(exist_ok=True)
    ids = list(ART) if which in ("all", None) else [which]
    for aid in ids:
        print(f"\n### {aid} — {ART[aid][0]}\n"); print(emit(aid, ART[aid][1]()))
    (GEN / "claims.json").write_text(json.dumps(CLAIMS, indent=2, sort_keys=True))
    tex = ["% single source of truth for inline numbers — prose cites \\clm{artifact.key}",
           "\\makeatletter\\def\\clm#1{\\csname clm@#1\\endcsname}",
           *(f"\\@namedef{{clm@{k}}}{{{v['render']}}}" for k, v in sorted(CLAIMS.items())), "\\makeatother"]
    (TEX / "claims.tex").write_text("\n".join(tex) + "\n")
    bundle = ["% all result TABLES — \\input in the BODY. (inline numbers: \\input{generated/claims} in the PREAMBLE)",
              *(f"\\input{{generated/{aid}}}" for aid in ART if (TEX / f"{aid}.tex").exists())]
    (TEX / "paper_artifacts.tex").write_text("\n".join(bundle) + "\n")
    doc()  # keep the how-to-generate doc in sync
    print(f"\n-> {len(ids)} artifact(s), {len(CLAIMS)} claims → {TEX}/  (paper uses \\input{{generated/<id>}})")

def doc():
    lines = ["# Paper artifacts — how to (re)generate & pair with prose", "",
             "Every artifact is generated by `python -m paper_exports.artifacts build <id>` and writes",
             "`generated/<id>.md`. Every inline number is a **claim** `id.key` in `generated/claims.json`;",
             "the paper cites it as `\\clm{id.key}` (\\input `generated/claims.tex`) so numbers auto-refresh.", "",
             "**Pair discussion ⇄ artifact:** wrap the paragraph discussing an artifact in",
             "`%%<artifact:ID>` … `%%</artifact:ID>` and cite its numbers via `\\clm{ID.key}`.",
             "After new results: `build all` then `status --paper <draft>` lists the claim IDs whose value",
             "moved and where they are discussed → refresh exactly those paragraphs.", "",
             "| artifact id | shows | claims | status |", "|---|---|---|---|"]
    for aid, (shows, fn) in ART.items():
        ks = [k for k in CLAIMS if k.startswith(aid + ".")]
        prov = "⚠ has single-seed*" if any(CLAIMS[k]["n"] == 1 for k in ks) else ("ok" if ks else "—")
        lines.append(f"| `{aid}` | {shows} | {len(ks)} | {prov} |")
    (OUT / "ARTIFACTS.md").write_text("\n".join(lines) + "\n")

def status(paper=None):
    fz = json.loads((GEN / "claims.freeze.json").read_text()) if (GEN / "claims.freeze.json").exists() else {}
    cur = json.loads((GEN / "claims.json").read_text())
    moved = [k for k in cur if k in fz and abs(cur[k]["value"] - fz[k]["value"]) > 1e-6]
    new = [k for k in cur if k not in fz]
    prov = [k for k, v in cur.items() if v["n"] == 1]
    print(f"claims: {len(cur)} total | {len(moved)} moved since freeze | {len(new)} new | {len(prov)} single-seed*")
    for k in moved: print(f"  ~ {k}: {fz[k]['render']} → {cur[k]['render']}")
    for k in prov:  print(f"  * {k} = {cur[k]['render']}  (provisional — needs a 2nd seed)")
    if paper and (moved or prov):
        import subprocess
        for k in moved + prov:
            hits = subprocess.run(["grep", "-rn", k, paper], capture_output=True, text=True).stdout.strip()
            if hits: print(f"  ↳ {k} discussed in:\n" + "\n".join("      " + h for h in hits.splitlines()))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "list", "freeze", "status"])
    ap.add_argument("id", nargs="?", default="all")
    ap.add_argument("--paper", help="draft dir to grep for moved/provisional claim IDs (status)")
    a = ap.parse_args()
    if a.cmd == "build":  build(a.id)
    elif a.cmd == "list": build("all") if not (GEN / "claims.json").exists() else None; doc(); print((OUT / "ARTIFACTS.md").read_text())
    elif a.cmd == "freeze":
        build("all"); (GEN / "claims.freeze.json").write_text((GEN / "claims.json").read_text()); print("froze claims snapshot")
    elif a.cmd == "status": status(a.paper)

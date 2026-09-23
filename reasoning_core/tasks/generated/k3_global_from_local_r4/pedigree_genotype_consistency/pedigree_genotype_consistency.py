import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'pedigree_genotype_consistency (variant 2 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_global_from_local_r4/pedigree_genotype_consistency',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1705404348,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

MODES = ("AR", "AD", "XR", "XD")
MODE_WORDS = {"AR": "autosomal recessive", "AD": "autosomal dominant",
              "XR": "X-linked recessive", "XD": "X-linked dominant"}

A = frozenset("A")
a = frozenset("a")
Aa = frozenset("aA")
DIPLOID = (A, a, Aa)


def _diploid_classes(mode, affected):
    if mode == "AR":
        return [a] if affected else [A, Aa]
    if mode == "AD":
        return [A, Aa] if affected else [a]
    if mode == "XR":
        return [a] if affected else [A, Aa]
    return [A, Aa] if affected else [a]


def _male_classes(mode, affected):
    if mode == "XR":
        return [a] if affected else [A]
    return [A] if affected else [a]


def _valid_auto(mom, dad, child):
    if child == A:
        return "A" in mom and "A" in dad
    if child == a:
        return "a" in mom and "a" in dad
    return (("A" in mom and "a" in dad) or ("a" in mom and "A" in dad))


def _valid_x_son(mom, child):
    return child.issubset(mom)


def _valid_x_daught(mom, dad, child):
    dadA = next(iter(dad))
    rest = child - frozenset({dadA})
    return dadA in child and len(rest) == 1 and rest.issubset(mom)


def _valid_child(mode, sex, mom, dad, kid, g):
    if mode in ("AR", "AD"):
        return _valid_auto(g[mom], g[dad], g[kid])
    if sex[kid] == "M":
        return _valid_x_son(g[mom], g[kid])
    return _valid_x_daught(g[mom], g[dad], g[kid])


def _geno_str(g):
    if len(g) == 2:
        return "Aa"
    x = next(iter(g))
    return x + x


def _build_pedigree(n_members):
    members = []
    fams = []
    nid = 0
    n_founders = max(2, min(3, n_members))
    for i in range(n_founders):
        members.append(("m%d" % nid, "F" if i % 2 == 0 else "M", 0))
        nid += 1
    attempts = 0
    while len(members) < n_members and attempts < 200:
        attempts += 1
        fems = [m for m in members if m[1] == "F"]
        mas = [m for m in members if m[1] == "M"]
        if not fems or not mas:
            break
        mom = random.choice(fems)
        dad = random.choice(mas)
        if mom[0] == dad[0]:
            continue
        k = random.randint(1, 3)
        kids = []
        for _ in range(k):
            if len(members) >= n_members:
                break
            sex = "F" if random.random() < 0.5 else "M"
            gen = max(mom[2], dad[2]) + 1
            m = ("m%d" % nid, sex, gen)
            nid += 1
            members.append(m)
            kids.append(m[0])
        if kids:
            fams.append((mom[0], dad[0], kids))
    return members, fams


def _assign_genotypes(mode, members, fams):
    sex = {m[0]: m[1] for m in members}
    child_fam = {}
    for mom, dad, kids in fams:
        for kid in kids:
            child_fam[kid] = (mom, dad)
    geno = {}
    order = sorted(members, key=lambda m: (m[2], m[0]))
    for mid, s, _g in order:
        if mid in child_fam:
            mom, dad = child_fam[mid]
            momg, dadg = geno[mom], geno[dad]
            if mode in ("AR", "AD"):
                valid = [c for c in DIPLOID if _valid_auto(momg, dadg, c)]
                geno[mid] = random.choice(valid)
            elif s == "M":
                geno[mid] = frozenset([random.choice(sorted(momg))])
            else:
                dadA = sorted(dadg)[0]
                momA = random.choice(sorted(momg))
                geno[mid] = frozenset({dadA, momA})
        else:
            if mode in ("AR", "AD") or s == "F":
                geno[mid] = random.choice(DIPLOID)
            else:
                geno[mid] = random.choice([A, a])
    return geno, sex


def _enumerate(mode, sex, pheno, fams, ids):
    child_fam = {}
    for mom, dad, kids in fams:
        for kid in kids:
            child_fam[kid] = (mom, dad)
    cand = {}
    for mid in ids:
        aff = pheno[mid]
        if mode in ("AR", "AD") or sex[mid] == "F":
            cand[mid] = _diploid_classes(mode, aff)
        else:
            cand[mid] = _male_classes(mode, aff)
    assign = {}
    counts = {mid: {} for mid in ids}
    res_count = [0]

    def dfs(pos):
        if pos == len(ids):
            res_count[0] += 1
            for mid, g in assign.items():
                counts[mid][g] = True
            return
        mid = ids[pos]
        for g in cand[mid]:
            assign[mid] = g
            ok = True
            for mom, dad, kids in fams:
                if mom in assign and dad in assign:
                    for kid in kids:
                        if kid in assign and not _valid_child(mode, sex, mom, dad, kid, assign):
                            ok = False
                            break
                    if not ok:
                        break
            if ok:
                dfs(pos + 1)
        assign.pop(mid, None)

    dfs(0)
    return res_count[0], counts


@dataclass
class PedigreeConfig(Config):
    n_members: int = 5
    max_query: int = 3
    min_query: int = 2
    allow_x: int = 0

    def apply_difficulty(self, level):
        self.n_members = stochastic_rounding(4 + level)
        self.max_query = stochastic_rounding(2 + level // 2)
        self.min_query = stochastic_rounding(2 + level // 3)
        self.allow_x = 1 if level >= 3 else 0


class PedigreeGenotypeConsistency(Task):
    summary = ("Pedigrees with phenotypes under a stated mode, autosomal or X-linked, dominant or "
               "recessive: Mendelian segregation through matings and sibships; answer each queried "
               "member's forced genotype as a canonical AA/Aa/aa token string in pedigree-input order.")
    design_choice = ("Forced genotypes are requested as a canonical string listing each queried "
                     "member's genotype (e.g., AA, Aa, aa) in the order they appear in the pedigree "
                     "input.")
    config_cls = PedigreeConfig

    def generate_entry(self):
        modes = ("AR", "AD") if not self.config.allow_x else MODES
        for _attempt in range(400):
            n_members = self.config.n_members
            mode = random.choice(modes)
            members, fams = _build_pedigree(n_members)
            if len(fams) == 0 or len(members) < self.config.min_query:
                continue
            geno, sex = _assign_genotypes(mode, members, fams)
            pheno = {}
            for mid, s, _g in members:
                g = geno[mid]
                if mode in ("AR", "AD"):
                    aff = (g == a) if mode == "AR" else (g != a)
                elif s == "M":
                    allel = next(iter(g))
                    aff = (allel == "a") if mode == "XR" else (allel == "A")
                else:
                    aff = (g == a) if mode == "XR" else (g != a)
                pheno[mid] = aff

            ids = sorted(m[0] for m in members)
            res_count, counts = _enumerate(mode, sex, pheno, fams, ids)
            if res_count == 0:
                continue
            forced = {mid for mid in ids if len(counts[mid]) == 1}
            diploid_forced = []
            for mid in ids:
                if mid not in forced:
                    continue
                if mode in ("AR", "AD") or sex[mid] == "F":
                    diploid_forced.append(mid)
            if len(set(pheno.values())) < 2 or len(diploid_forced) < self.config.min_query:
                continue
            if len(diploid_forced) > self.config.max_query:
                chosen = sorted(random.sample(diploid_forced, self.config.max_query))
            else:
                chosen = sorted(diploid_forced)
            answer_tokens = []
            for mid in chosen:
                g = next(iter(counts[mid].keys()))
                answer_tokens.append(_geno_str(g))
            answer = " ".join(answer_tokens)
            if not all(t in ("AA", "Aa", "aa") for t in answer_tokens):
                continue
            metadata = {
                "mode": mode,
                "mode_word": MODE_WORDS[mode],
                "members": [[mid, sex[mid], ("affected" if pheno[mid] else "unaffected")]
                            for mid in ids],
                "families": [[mom, dad, kids] for mom, dad, kids in fams],
                "query": chosen,
                "constructed_genotypes": {mid: _geno_str(geno[mid]) for mid in ids},
                "answer_tokens": answer_tokens,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("could not build a consistent pedigree")

    def render_prompt(self, metadata):
        lines = []
        mode = metadata["mode"]
        if mode == "AR":
            rules = ("affected persons are aa (two disease alleles); unaffected persons are AA or Aa. "
                     "A disease allele is recessive: an affected person inherits one from each parent.")
        elif mode == "AD":
            rules = ("affected persons are AA or Aa; unaffected persons are aa. A single disease allele "
                     "is enough to cause the disorder, so an affected child must have an affected parent.")
        elif mode == "XR":
            rules = ("for females affected are aa and unaffected are AA or Aa; for males (one X, no "
                     "homologue) affected are a and unaffected are A. A male gets his X from his mother.")
        else:
            rules = ("for females affected are AA or Aa and unaffected are aa; for males (one X) "
                     "affected are A and unaffected are a. A male gets his X from his mother.")
        lines.append(
            f"The condition follows {metadata['mode_word']} inheritance. Under this mode, {rules}")
        lines.append("")
        lines.append("The family members (sex and phenotype):")
        for mid, s, ph in metadata["members"]:
            lines.append(f"  {mid}: {s.lower()}, {ph}")
        lines.append("")
        lines.append("Matings (a family lists the two parents then their children):")
        for mom, dad, kids in metadata["families"]:
            lines.append(f"  {mom} and {dad} are parents of {', '.join(kids)}.")
        lines.append("")
        query = ", ".join(metadata["query"])
        lines.append(
            f"A member's genotype is forced when every genotype assignment consistent with the "
            f"pedigree and the mode gives that member the same genotype. Give the forced genotype "
            f"(AA, Aa or aa) of, in this exact order, {query}.")
        lines.append("")
        n = len(metadata["query"])
        example = " ".join(["Aa"] * n)
        lines.append(f"Answer with {n} space-separated genotype tokens in that order, for example "
                     f"`{example}`.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        norm = " ".join(answer.strip().split())
        gold = " ".join(entry.answer.strip().split())
        return 1.0 if norm == gold else 0.0

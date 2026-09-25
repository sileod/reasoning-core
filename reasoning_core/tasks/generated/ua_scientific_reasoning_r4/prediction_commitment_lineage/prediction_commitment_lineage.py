import random

from reasoning_core.template import Config, Entry, Task


class LineageConfig(Config):
    num_claims: int = 3
    num_tests: int = 4
    num_versions: int = 4
    data_pool: int = 12
    access_size: int = 1
    max_parents: int = 2

    def apply_difficulty(self, level):
        self.num_claims = 2 + level
        self.num_tests = 3 + level
        self.num_versions = 3 + level
        self.data_pool = 12 + 3 * level
        self.access_size = 1 + level // 2
        self.max_parents = 1 + level // 2


def _lineage_versions(parents, v):
    """Return the set of version indices in v's lineage (v plus all ancestors)."""
    anc = {v}
    stack = list(parents[v])
    while stack:
        x = stack.pop()
        if x not in anc:
            anc.add(x)
            stack.extend(parents[x])
    return anc


class PredictionCommitmentLineage(Task):
    summary = "Track hypothesis revisions, analysis choices, and data access through branching study histories; distinguish genuinely held-out tests from inherited data reuse and return the uncontaminated claim-test pairs."
    design_choice = "Represent each study history as a directed acyclic graph where nodes are analysis versions and edges are revisions; answers are a canonical list of (claim, test) identifiers that are uncontaminated."
    config_cls = LineageConfig

    def generate_entry(self):
        cfg = self.config
        V = cfg.num_versions
        C = cfg.num_claims
        M = cfg.num_tests
        D = cfg.data_pool
        asize = max(1, cfg.access_size)

        parents = [[] for _ in range(V)]
        for v in range(1, V):
            possible = list(range(v))
            k = random.randint(0, min(len(possible), cfg.max_parents))
            parents[v] = sorted(random.sample(possible, k))

        intro = [random.randrange(V) for _ in range(D)]

        seen = []
        for v in range(V):
            lin = _lineage_versions(parents, v)
            seen.append({d for d in range(D) if intro[d] in lin})

        test_pool = list(range(M))
        test_owner = random.sample(test_pool, C)

        pairs = []
        for c in range(C):
            t = test_owner[c]
            v = random.randrange(V)
            fresh = [d for d in range(D) if d not in seen[v]]
            reused = sorted(seen[v])
            picked = min(asize, D)
            if fresh and random.random() < 0.5 and picked <= len(fresh):
                acc = random.sample(fresh, picked)
            else:
                base = [random.choice(reused)] if reused else []
                rest_pool = [d for d in range(D) if d != (base[0] if base else None)]
                need = max(0, picked - len(base))
                if need:
                    base += random.sample(rest_pool, min(need, len(rest_pool)))
                acc = base
            acc = list(dict.fromkeys(acc))
            uncont = all(d not in seen[v] for d in acc)
            assert uncont == (set(acc).isdisjoint(seen[v]))
            assert 1 <= t + 1 <= M and 0 <= v < V
            pairs.append({"claim": c + 1, "test": t + 1, "version": v,
                          "access": sorted(acc), "uncontaminated": bool(uncont)})

        clean = sorted((p["claim"], p["test"]) for p in pairs if p["uncontaminated"])
        ans = ",".join(f"{a}:{b}" for a, b in clean) if clean else "none"

        return Entry(
            metadata={
                "num_versions": V,
                "num_claims": C,
                "num_tests": M,
                "data_pool": D,
                "parents": [sorted(p) for p in parents],
                "intro": intro,
                "pairs": pairs,
            },
            answer=ans,
        )

    def render_prompt(self, metadata):
        V = metadata["num_versions"]
        D = metadata["data_pool"]
        parts = [
            f"A study evolved through {V} analysis versions (numbered 1..{V}) and "
            f"{metadata['num_claims']} claims, each evaluated by one test. "
            "There are %d data items (numbered 1..%d); each was introduced by one version."
            % (D, D),
        ]
        parts.append("Data item m was introduced by version " +
                     ", ".join(f"{i+1}:v{int(metadata['intro'][i])+1}" for i in range(D)) + ".")
        for v in range(V):
            par = [p + 1 for p in metadata["parents"][v]] if metadata["parents"][v] else []
            if par:
                parts.append(f"Version {v+1} was derived by revising version(s) "
                             + " and ".join(str(p) for p in par) + ".")
            else:
                parts.append(f"Version {v+1} is the initial version with no ancestors.")
        for p in metadata["pairs"]:
            accs = " ".join("d" + str(x + 1) for x in p["access"])
            parts.append(
                f"Claim {p['claim']} was evaluated by running test {p['test']} at version "
                f"{p['version']+1}; test {p['test']} reads data {{ {accs} }}."
            )
        parts.append(
            "A claim-test pair is contaminated by inherited data reuse when any data item the "
            "test reads was introduced by the version where the claim was evaluated or by any of "
            "that version's ancestor versions. It is genuinely held out (uncontaminated) when all "
            "of the data the test reads was introduced only by versions outside that whole lineage. "
            "List the claim:test pairs that are uncontaminated, in increasing claim order, "
            "comma-separated (e.g. '1:4,3:2'); write 'none' if there are none."
        )
        return " ".join(parts)


TASK_META = {'parent_source_id': None,
 'idea': 'prediction_commitment_lineage (variant 1 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r4/prediction_commitment_lineage',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2305351643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

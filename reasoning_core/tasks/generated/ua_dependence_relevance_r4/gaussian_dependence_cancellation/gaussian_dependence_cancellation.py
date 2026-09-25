import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'gaussian_dependence_cancellation (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dependence_relevance_r4/gaussian_dependence_cancellation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _linear_solve(a, b):
    a = [list(row) for row in a]
    b = list(b)
    n = len(b)
    for col in range(n):
        pivot = None
        for r in range(col, n):
            if a[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        b[col], b[pivot] = b[pivot], b[col]
        pv = a[col][col]
        a[col] = [x / pv for x in a[col]]
        b[col] = b[col] / pv
        for r in range(n):
            if r == col:
                continue
            factor = a[r][col]
            if factor == 0:
                continue
            a[r] = [x - factor * y for x, y in zip(a[r], a[col])]
            b[r] = b[r] - factor * b[col]
    return b


def _inverse(m):
    n = len(m)
    ident = [[Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]
    aug = [list(m[i]) + ident[i] for i in range(n)]
    for col in range(n):
        pivot = None
        for r in range(col, n):
            if aug[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        pv = aug[col][col]
        aug[col] = [x / pv for x in aug[col]]
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            if factor == 0:
                continue
            aug[r] = [x - factor * y for x, y in zip(aug[r], aug[col])]
    return [row[n:] for row in aug]


def _schur_kl(k, l, _, precision):
    sub = [[precision[i][j] for j in l] for i in l]
    if not l:
        return precision
    inv_ll = _inverse(sub)
    if inv_ll is None:
        return None
    for i in range(len(k)):
        for j in range(len(k)):
            acc = precision[k[i]][k[j]]
            for a in range(len(l)):
                for b in range(len(l)):
                    acc = acc - precision[k[i]][l[a]] * inv_ll[a][b] * precision[l[b]][k[j]]
            precision[k[i]][k[j]] = acc
    return precision


def _exact_independence(cov, query, latent):
    n = len(cov)
    prec = _inverse(cov)
    if prec is None:
        return None
    k = [i for i in range(n) if query[i] in "XY"]
    l = [i for i in range(n) if query[i] == "Q" or latent[i]]
    suff = _schur_kl(k, l, None, [list(row) for row in prec])
    if suff is None:
        return None
    xk = [i for i in k if query[i] == "X"][0]
    yk = [i for i in k if query[i] == "Y"][0]
    return suff[k.index(xk)][k.index(yk)] == 0


def _make_psd(n, rng, denom_range, val_range):
    for _ in range(200):
        L = [[Fraction(0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            L[i][i] = Fraction(rng.randrange(1, val_range + 1), rng.randrange(1, denom_range + 1))
            for j in range(i):
                L[i][j] = Fraction(rng.randrange(-val_range, val_range + 1),
                                   rng.randrange(1, denom_range + 1))
        cov = [[Fraction(0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                s = Fraction(0)
                for t in range(min(i, j) + 1):
                    s = s + L[i][t] * L[j][t]
                cov[i][j] = s
        if all(cov[i][i] > 0 for i in range(n)):
            return cov
    raise RuntimeError("could not build PSD matrix")


@dataclass
class GaussianDependenceCancellationConfig(Config):
    n: int = 3
    denom_range: int = 4
    val_range: int = 3

    def apply_difficulty(self, level):
        self.n = 3 + level
        self.denom_range = 3 + level
        self.val_range = 3 + level


class GaussianDependenceCancellation(Task):
    summary = "Determine exact independence after observing and marginalizing variables in rational Gaussian systems; vary covariance and precision inputs, latent paths, and coefficient cancellations; answer queried relations."
    design_choice = "Instances give a covariance matrix with symbolic rational entries and a query like 'X⊥Y|Z'; solvers compute whether the Schur complement entry is exactly zero and answer 'yes' or 'no'."
    config_cls = GaussianDependenceCancellationConfig

    def generate_entry(self):
        config = self.config
        n = config.n
        c = config
        labels = ["X", "Y"] + ["Z%d" % i for i in range(1, n - 1)]
        want_yes = random.random() < 0.5
        x_i, y_i = 0, 1

        for _ in range(200):
            nz = [i for i in range(2, n)]
            num_latent = random.randrange(0, len(nz) + 1)
            latent_idx = random.sample(nz, num_latent)
            latent = [False] * n
            for i in latent_idx:
                latent[i] = True

            obs_zz = [i for i in nz if not latent[i]]
            if not obs_zz:
                continue
            num_cond = random.randrange(1, len(obs_zz) + 1)
            cond = random.sample(obs_zz, num_cond)

            query = ["Q"] * n
            query[x_i] = "X"
            query[y_i] = "Y"
            for i in cond:
                query[i] = "Z"

            cov = None
            if want_yes:
                driver = cond[random.randrange(len(cond))]
                cov = self._driver_cov(n, c, driver_idx=driver,
                                       driven=(x_i, y_i), latent=latent)
            else:
                latent_avail = [i for i in nz if latent[i]]
                if not latent_avail:
                    cov = _make_psd(n, random, c.denom_range, c.val_range)
                else:
                    driver = latent_avail[random.randrange(len(latent_avail))]
                    cov = self._driver_cov(n, c, driver_idx=driver,
                                           driven=(x_i, y_i), latent=latent)

            if cov is None:
                continue
            ans = _exact_independence(cov, query, latent)
            if ans is None:
                continue
            if want_yes and not ans:
                continue
            if (not want_yes) and ans:
                continue

            cov_str = [[str(cov[i][j]) for j in range(n)] for i in range(n)]
            cond_str = ", ".join(labels[i] for i in sorted(cond))
            lat_str = ", ".join(labels[i] for i in sorted([i for i in range(n) if latent[i]]))
            answer = "yes" if ans else "no"
            entry = Entry(metadata={
                "covariance": cov_str,
                "latent": latent,
                "query": query,
                "labels": labels,
                "conditioning": cond_str,
                "latent_str": lat_str or "none",
            }, answer=answer)
            return entry
        raise RuntimeError("no instance generated")

    def _driver_cov(self, n, c, driver_idx, driven, latent):
        var_d = Fraction(random.randrange(1, c.val_range + 1),
                         random.randrange(1, c.denom_range + 1))
        alphas = {}
        for i in driven:
            alphas[i] = Fraction(random.randrange(-c.val_range, c.val_range + 1),
                                 random.randrange(1, c.denom_range + 1))
            if alphas[i] == 0:
                alphas[i] = Fraction(1, 1)
        cov = [[Fraction(0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    s = Fraction(0)
                    if i == driver_idx:
                        s = s + var_d
                    if i in alphas:
                        s = s + alphas[i] * alphas[i] * var_d
                    if i != driver_idx:
                        s = s + Fraction(random.randrange(1, c.val_range + 1),
                                         random.randrange(1, c.denom_range + 1))
                    cov[i][j] = s
                elif i == driver_idx and j in alphas:
                    cov[i][j] = alphas[j] * var_d
                elif j == driver_idx and i in alphas:
                    cov[i][j] = alphas[i] * var_d
                elif i in alphas and j in alphas:
                    cov[i][j] = alphas[i] * alphas[j] * var_d
                else:
                    cov[i][j] = Fraction(0)
        return cov

    def render_prompt(self, metadata):
        n = len(metadata["covariance"])
        mat = "\\begin{pmatrix}\n"
        for i in range(n):
            row = " & ".join(metadata["covariance"][i])
            mat += row + " \\\\\n"
        mat += "\\end{pmatrix}"
        lat = metadata["latent_str"]
        if lat == "none":
            lat_phrase = "No variables are latent, so nothing is marginalized out;"
        elif "," in lat:
            lat_phrase = "The latent variables %s are marginalized out (integrated over);" % lat
        else:
            lat_phrase = "The latent variable %s is marginalized out (integrated over);" % lat
        return ("Consider a zero-mean multivariate Gaussian over variables %s. "
                "Its covariance matrix is\n%s\n"
                "%s the other "
                "variables are observed. Decide whether the queried conditional independence holds "
                "exactly, under rational arithmetic.\n"
                "Is X independent of Y given %s? Answer exactly with the single word 'yes' or 'no'.") % (
            ", ".join(metadata["labels"]), mat, lat_phrase, metadata["conditioning"])

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip().lower() == gold else 0.0

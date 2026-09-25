import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class OrbitalImpulseRebaseliningConfig(Config):
    scale: int = 1
    results_dp: int = 3

    def apply_difficulty(self, level):
        self.scale = 1 + level
        self.results_dp = 3


def _type_of_e(e):
    if e < 0.02:
        return "circular"
    if e < 0.96:
        return "elliptic"
    if e < 1.05:
        return "parabolic"
    return "hyperbolic"


def _impulse_state(mu, r, v0, dv, sgn):
    v1 = v0 + sgn * dv
    h = r * v1
    eps = v1 * v1 / 2.0 - mu / r
    e2 = 1.0 + 2.0 * eps * h * h / (mu * mu)
    return h, eps, math.sqrt(max(0.0, e2))


def _mass_state(mu2, r, v):
    h = r * v
    eps = v * v / 2.0 - mu2 / r
    e2 = 1.0 + 2.0 * eps * h * h / (mu2 * mu2)
    return h, eps, math.sqrt(max(0.0, e2))


def _apsides_gold(mu, h, e):
    typ = _type_of_e(e)
    if typ == "circular":
        return typ, {"r": h * h / (mu * (1.0 + e))}
    if typ == "elliptic":
        rp = h * h / (mu * (1.0 + e))
        ra = h * h / (mu * (1.0 - e))
        rmin = min(rp, ra)
        rmax = max(rp, ra)
        return typ, {"rp": rmin, "ra": rmax}
    rp = h * h / (mu * (1.0 + e))
    return typ, {"rp": rp}


def _gold_vals(metadata):
    mode = metadata["mode"]
    if mode == "impulse":
        h, _e, e = _impulse_state(metadata["mu"], metadata["r"], metadata["v0"],
                                  metadata["dv"], metadata["sgn"])
        if metadata["query"] == "h":
            return {"h": h}
        typ, vals = _apsides_gold(metadata["mu"], h, e)
        return dict(vals, type=typ)
    if mode == "mass":
        h, _e, e = _mass_state(metadata["mu2"], metadata["r"], metadata["v"])
        if metadata["query"] == "h":
            return {"h": h}
        typ, vals = _apsides_gold(metadata["mu2"], h, e)
        return dict(vals, type=typ)
    h = math.sqrt(metadata["mu"] * 2.0 * metadata["rp"] * metadata["ra"]
                  / (metadata["rp"] + metadata["ra"]))
    return {"h": h}


def _gold_string(metadata):
    g = _gold_vals(metadata)
    dp = metadata["results_dp"]
    if "h" in g:
        return f"h={round(g['h'], dp):.{dp}f}"
    typ = g["type"]
    vals = {k: round(v, dp) for k, v in g.items() if k != "type"}
    parts = " ".join(f"{k}={v:.{dp}f}" for k, v in vals.items())
    return f"{typ} {parts}"


def _parse_user(answer):
    if not isinstance(answer, str):
        return None
    try:
        words = answer.strip().split()
    except Exception:
        return None
    if not words:
        return None
    head = words[0]
    if head.startswith("h="):
        if len(words) != 1:
            return None
        return {"h": float(head.split("=")[1])}
    vals = {}
    for w in words[1:]:
        if "=" not in w:
            return None
        k, v = w.split("=")
        try:
            vals[k] = float(v)
        except ValueError:
            return None
    if not vals:
        return None
    return dict(vals, type=head)


def _close(a, b, tol=1e-2):
    return abs(a - b) <= tol


def _render(metadata):
    L = []
    L.append("A craft orbits a point central body with a fixed gravitational "
             "parameter (mu). We consider an instantaneous rebaselining of its "
             "orbit and want the resulting orbit's invariants. For a two-body "
             "orbit the specific angular momentum is h = r * v_t where v_t is the "
             "tangential speed, the specific orbital energy is eps = v^2/2 - mu/r, "
             "and the eccentricity satisfies e^2 = 1 + 2*eps*h^2/mu^2. The orbit "
             "type follows from e: e=0 circular, 0<e<1 elliptic, e=1 parabolic, "
             "e>1 hyperbolic.")
    L.append("")
    mode = metadata["mode"]
    if mode == "impulse":
        L.append("At its current apside the craft is a distance "
                 f"r = {metadata['r']:.4g} from the central body, moving purely "
                 f"tangentially with speed v = {metadata['v0']:.4f}. A "
                 f"{'prograde' if metadata['sgn'] > 0 else 'retrograde'} impulse "
                 f"of magnitude {metadata['dv']:.4f} immediately alters its "
                 "tangential speed (prograde adds to v, retrograde subtracts), "
                 "while r and the gravitational parameter stay the same. mu = "
                 f"{metadata['mu']:.4g}.")
    elif mode == "mass":
        L.append("The craft is a distance "
                 f"r = {metadata['r']:.4g} from the central body, moving purely "
                 f"tangentially with speed v = {metadata['v']:.4f}. The central "
                 "body's mass suddenly changes so its gravitational parameter goes "
                 f"from mu1 = {metadata['mu1']:.4g} to mu2 = "
                 f"{metadata['mu2']:.4g}; the craft's position and velocity vector "
                 "are unchanged at that instant.")
    else:
        L.append("The craft coasts between two specified apsides of its elliptic "
                 f"orbit: periapsis radius rp = {metadata['rp']:.4g} and apoapsis "
                 f"radius ra = {metadata['ra']:.4g}. At each apside its velocity "
                 "is purely tangential. The central body's gravitational parameter "
                 f"is mu = {metadata['mu']:.4g}.")
    L.append("")
    if metadata["query"] == "h":
        L.append("Report the specific angular momentum h of the resulting orbit, "
                 "rounded to 3 decimal places, as 'h=<value>' (for example "
                 "'h=12.500').")
    else:
        L.append("Report the type of the resulting orbit and its periapsis (and, "
                 "for a bound orbit, apoapsis) radius, rounded to 3 decimal "
                 "places. Use exactly: 'circular r=<r>' for e=0; "
                 "'elliptic rp=<rp> ra=<ra>' for an ellipse; 'parabolic rp=<rp>' "
                 "for e=1; 'hyperbolic rp=<rp>' for e>1. For example "
                 "'elliptic rp=1.500 ra=3.200'.")
    return "\n".join(L)


class OrbitalImpulseRebaselining(Task):
    summary = "Update orbital invariants through velocity impulses, central-mass changes and coasting between specified apsides; return the resulting orbit type, turning radii or specific angular momentum."
    config_cls = OrbitalImpulseRebaseliningConfig
    design_choice = "Answer form: return a canonical orbit-type label ('circular', 'elliptic', 'parabolic', 'hyperbolic') plus either periapsis/apoapsis radii or specific angular momentum, depending on the queried quantity."

    def generate_entry(self):
        cfg = self.config
        s = cfg.scale
        dp = cfg.results_dp
        mu_primes = [2, 3, 5, 7, 11]
        mode = random.choice(["impulse", "mass", "coast"])
        query = random.choice(["apsides", "apsides", "h"])
        if mode == "impulse":
            mu = s * random.choice(mu_primes)
            p = s * random.randint(2, 4)
            typ = random.choice(["circular", "elliptic", "parabolic", "hyperbolic"])
            if typ == "circular":
                e = 0.0
            elif typ == "elliptic":
                e = random.randint(1, 9) / 10.0
            elif typ == "parabolic":
                e = 1.0
            else:
                e = 1.0 + random.randint(1, 9) / 10.0
            r = p / (1.0 + e)
            h_hi = math.sqrt(mu * p)
            v1 = h_hi / r
            while True:
                sgn = random.choice([-1, 1])
                dv = round(v1 * random.uniform(0.08, 0.45), 4)
                v0 = v1 - sgn * dv
                if v0 > 0:
                    break
            v0r = round(v0, 4)
            dvr = round(dv, 4)
            h, _e, ef = _impulse_state(mu, r, v0r, dvr, sgn)
            metadata = {
                "mode": "impulse", "query": query, "mu": float(mu),
                "r": float(r), "v0": v0r, "dv": dvr, "sgn": int(sgn),
                "results_dp": dp,
            }
        elif mode == "mass":
            mu1 = s * random.choice(mu_primes)
            mu2 = s * random.choice(mu_primes)
            r = float(s * random.randint(3, 6))
            v = float(s * random.randint(2, 5))
            if _mass_state(mu2, r, v)[0] <= 0:
                v += 1.0
                r += 1.0
            metadata = {
                "mode": "mass", "query": query, "mu1": float(mu1),
                "mu2": float(mu2), "r": r, "v": v, "results_dp": dp,
            }
        else:
            rp = float(s * random.randint(2, 6))
            ra = rp + float(s * random.randint(1, 5))
            mu = float(s * random.choice(mu_primes))
            metadata = {
                "mode": "coast", "query": query, "mu": mu,
                "rp": rp, "ra": ra, "results_dp": dp,
            }
        answer = _gold_string(metadata)
        g = _gold_vals(metadata)
        type_label = g.get("type")
        if type_label == "parabolic":
            # parabolic orbit is fine physically; h > 0 guaranteed.
            pass
        if ("h" in g and not (g["h"] > 0)):
            raise RuntimeError("non-positive angular momentum")
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return _render(metadata)

    def score_answer(self, answer, entry):
        gold = _gold_vals(entry.metadata)
        user = _parse_user(answer)
        if user is None:
            return 0.0
        if "h" in gold:
            if "h" not in user:
                return 0.0
            return 1.0 if _close(user["h"], gold["h"]) else 0.0
        if user.get("type") != gold.get("type"):
            return 0.0
        gp = dict(gold)
        gp.pop("type", None)
        up = dict(user)
        up.pop("type", None)
        if set(gp.keys()) != set(up.keys()):
            return 0.0
        for k in gp:
            if not _close(up[k], gp[k]):
                return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'orbital_impulse_rebaselining (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dynamic_structures_r5/orbital_impulse_rebaselining',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

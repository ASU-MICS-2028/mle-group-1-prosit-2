"""Stress tests for ADR 0021 (Ghana: decline Type_2 and other unseen types, 300 GHS starter for Type_3). Needs `zindi_submissions.py --read-exact` first.

Pass rules, written before these tests ran (the main cost table was already known):
A  Beats every policy that gives full-size loans to 10%+ of applicants: on public AND private, at all 4 repeat values, and in 95%+ of draws from the rate uncertainty.
B  Against declining everyone: extra cost at most 15 GHS per applicant with no repeat value; wins 50%+ of draws at 16 GHS; wins 95%+ at 180 and 360 GHS.
C  Beats the full-size policies in 90%+ of the assumption combinations.
D  Still beats them using Ghana's real loan amounts, mean and median per group.
E  Still beats them if starter loans default twice as often as measured.
F  Costs at most 15 GHS more than the cheapest of the 729 policies at each repeat value, including when that policy is picked on the other part of the data.
"""
import itertools
from pathlib import Path
import numpy as np, pandas as pd

T = Path(__file__).resolve().parent.parent / "learnings" / "tables"
FUTURES = (0, 16, 180, 360); FULL, START, DECLINE = 0, 1, 2
PROPOSED = "DSSSSD"  # Type_2, T3 first, T3 riskiest, band 4, bands 1-3, other
POLICIES = np.array(list(itertools.product(range(3), repeat=6)))
CODE = lambda s: tuple("FSD".index(c) for c in s)
NAMED = {"proposed: Type_3 starter, rest declined": "DSSSSD", "decline everyone": "DDDDDD", "approve everyone": "FFFFFF", "Type_3 all full, rest declined": "DFFFFD",
         "Type_3 bands 1-4 full, rest declined": "DDDFFD", "Type_3 bands 1-3 full, rest declined": "DDDDFD", "bands 1-3 full, first loans starter": "DSDDFD", "Type_3 bands 1-3 starter only": "DDDDSD"}


def per_group(rate, loans, amount=3000., fee=.03, recovered=.1, chase=16., starter=300., mult=1., future=0.):
    """Cost per applicant by [..., group, action]. Same rules as ADR 0020: decline loses fee + future on good payers; a starter keeps the future and its own fee."""
    w = loans / loans.sum(); ps = np.minimum(1, rate * mult); fees = np.minimum(starter, amount) * fee
    full = rate * (amount * (1 - recovered) + chase)
    st = ps * (np.minimum(starter, amount) * (1 - recovered) + chase) + (1 - ps) * (amount * fee - fees)
    dec = (1 - rate) * (amount * fee + future)
    return np.stack([full, st, dec], -1) * w[..., None]


def costs(c): return c[..., np.arange(6), POLICIES].sum(-1)


def run(seed=553, draws=5000):
    s = pd.read_csv(T / "11b_ghana_segments.csv"); names = s.segment.tolist(); loans = s.loans.to_numpy(); share = s.share_public[0]
    pub, pri = s.public / (loans * share), s.private / (loans * (1 - share)); allr = (s.public + s.private) / loans
    assert names[4] == "Type_3 bands 1-3" and abs(loans.sum() - 3525) < 1e-6
    ix = lambda code: int(np.flatnonzero((POLICIES == CODE(code)).all(1))[0])
    prop = ix(PROPOSED); wl = loans / loans.sum()
    big = np.flatnonzero((POLICIES == FULL).dot(wl) >= .10)  # full-size loans for 10%+ of applicants
    verdict = {}
    # 1. each part separately, and pick-on-one, test-on-the-other
    rows, a_ok, f_ok = [], True, True
    for f in FUTURES:
        cp, cq, ca = (costs(per_group(r.to_numpy(), loans, future=f)) for r in (pub, pri, allr))
        rows.append(dict(future=f, proposed_public=cp[prop], proposed_private=cq[prop], proposed_all=ca[prop], best_full_public=cp[big].min(), best_full_private=cq[big].min(), best_full_policy="".join("FSD"[i] for i in POLICIES[big[ca[big].argmin()]]),
                         best_any=ca.min(), best_any_policy="".join("FSD"[i] for i in POLICIES[ca.argmin()]), picked_on_public_tested_on_private=cq[cp.argmin()], picked_on_private_tested_on_public=cp[cq.argmin()], proposed_extra_vs_best=ca[prop] - ca.min()))
        a_ok &= cp[prop] < cp[big].min() and cq[prop] < cq[big].min()
        f_ok &= ca[prop] - ca.min() <= 15 and cq[prop] - cq[cp.argmin()] <= 15 and cp[prop] - cp[cq.argmin()] <= 15
    t = pd.DataFrame(rows); t.to_csv(T / "11c_ghana_parts.csv", index=False)
    # 2. uncertainty in the rates, cautiously counting customers rather than loans
    rng = np.random.default_rng(seed); n = s.customers.to_numpy(); r = rng.beta(1 + allr.to_numpy() * n, 1 + (1 - allr.to_numpy()) * n, (draws, 6))
    rows = []
    for f in FUTURES:
        c = costs(per_group(r, loans, future=f)); bf = c[:, big].min(1)
        for nm, code in {**NAMED, "best policy with full loans for 10%+": None}.items():
            o = bf if code is None else c[:, ix(code)]; d = c[:, prop] - o
            if code != PROPOSED: rows.append(dict(future=f, against=nm, proposed_wins=(d < 0).mean(), diff_mean=d.mean(), diff_low=np.quantile(d, .025), diff_high=np.quantile(d, .975)))
    u = pd.DataFrame(rows); u.to_csv(T / "11c_ghana_uncertainty.csv", index=False)
    w = lambda f, nm: u[(u.future == f) & (u.against == nm)].proposed_wins.iloc[0]
    a_ok &= all(w(f, "best policy with full loans for 10%+") >= .95 for f in FUTURES)
    base = costs(per_group(allr.to_numpy(), loans)); d0 = base[prop] - base[ix("DDDDDD")]
    b_ok = d0 <= 15 and w(16, "decline everyone") >= .5 and w(180, "decline everyone") >= .95 and w(360, "decline everyone") >= .95
    # 3. assumptions
    rows = []
    for typ, rec, ch, st, m, f in itertools.product((1500., 3000., 6000., 15537.), (0, .1, .3), (16., 32.), (150., 300., 600.), (.5, 1, 1.5, 2, 3), FUTURES):
        c = costs(per_group(allr.to_numpy(), loans, amount=typ, recovered=rec, chase=ch, starter=st, mult=m, future=f))
        rows.append(dict(typical=typ, recovered=rec, chase=ch, starter=st, starter_default_mult=m, future=f, proposed=c[prop], best_full=c[big].min(), decline=c[ix("DDDDDD")], best_any=c.min()))
    g = pd.DataFrame(rows); g["beats_full"] = g.proposed < g.best_full; g["beats_decline"] = g.proposed < g.decline; g.to_csv(T / "11c_ghana_assumptions.csv", index=False)
    c_share = g.beats_full.mean(); summ = pd.concat([g.groupby(k)[["beats_full", "beats_decline"]].mean().rename_axis("value").reset_index().assign(assumption=k) for k in ("typical", "recovered", "chase", "starter", "starter_default_mult", "future")])
    summ.to_csv(T / "11c_ghana_assumptions_summary.csv", index=False)
    # 4. real amounts per group, 5. starter default multiplier
    rows, d_ok = [], True
    for label, a in (("mean amount", s.mean_amount.to_numpy()), ("median amount", s.median_amount.to_numpy())):
        for f in FUTURES:
            c = costs(per_group(allr.to_numpy(), loans, amount=a, future=f)); rows.append(dict(amounts=label, future=f, proposed=c[prop], best_full=c[big].min(), decline=c[ix("DDDDDD")], best_any=c.min(), best_any_policy="".join("FSD"[i] for i in POLICIES[c.argmin()])))
            d_ok &= c[prop] < c[big].min()
    pd.DataFrame(rows).to_csv(T / "11c_ghana_real_amounts.csv", index=False); real = pd.DataFrame(rows)
    rows, e_ok = [], True
    for m in (.5, 1, 1.5, 2, 3, 4, 5, 7):
        for f in FUTURES:
            c = costs(per_group(allr.to_numpy(), loans, mult=m, future=f)); rows.append(dict(starter_default_mult=m, type3_starter_default=(s.public + s.private)[1:5].sum() / loans[1:5].sum() * m, future=f, proposed=c[prop], best_full=c[big].min(), decline=c[ix("DDDDDD")]))
            if m == 2: e_ok &= c[prop] < c[big].min()
    mt = pd.DataFrame(rows); mt.to_csv(T / "11c_ghana_starter_default.csv", index=False)
    # 6. what actually happens: money per 1,000 applicants, no repeat value
    d = (s.public + s.private).to_numpy() * 1000 / 3525; k = loans * 1000 / 3525; rows = []
    for nm, code in NAMED.items():
        a = np.array(CODE(code)); size = np.where(a == FULL, 3000., 300.)[:]; on = a != DECLINE
        lent = (k * size * on).sum(); fees = ((k - d) * size * .03 * on).sum(); lost = (d * (size * .9 + 16) * on).sum()
        rows.append(dict(policy=nm, offered=k[on].sum(), good_payers_served=(k - d)[on].sum(), good_payers_refused=(k - d)[~on].sum(), defaults=d[on].sum(), lent=lent, fees=fees, lost=lost, net=fees - lost, lost_share_of_lent=lost / lent if lent else np.nan))
    m = pd.DataFrame(rows); m.to_csv(T / "11c_ghana_money.csv", index=False)
    verdict = dict(zip("ABCDEF", (a_ok, b_ok, c_share >= .9, d_ok, e_ok, f_ok)))
    v = pd.DataFrame([dict(rule=x, passed=bool(y)) for x, y in verdict.items()]); v.to_csv(T / "11c_ghana_verdict.csv", index=False)
    pd.set_option("display.width", 220)
    for x in (t, u, summ, real, mt[mt.future.isin([0, 16])], m): print(x.round(3).to_string(index=False)); print()
    print("assumption combos beating full:", round(c_share, 3), "beating decline:", round(g.beats_decline.mean(), 3), "extra vs decline at 0:", round(d0, 1)); print(g[~g.beats_full].groupby(["starter", "starter_default_mult"]).size().to_string()); print(verdict)
    assert (per_group(allr.to_numpy(), loans)[0, 2] > 0) and abs(base[ix("DDDDDD")] - 78.6) < .1 and abs(base[prop] - 88.7) < .1  # matches ADR 0021's table


def every_policy(seed=553, draws=2000):
    """The same six rules, applied to all 729 policies. A full-size policy is compared with the other full-size policies, not itself."""
    s = pd.read_csv(T / "11b_ghana_segments.csv"); loans = s.loans.to_numpy(); share = s.share_public[0]; wl = loans / loans.sum()
    pub, pri, allr = (s.public / (loans * share)).to_numpy(), (s.private / (loans * (1 - share))).to_numpy(), ((s.public + s.private) / loans).to_numpy()
    big = np.flatnonzero((POLICIES == FULL).dot(wl) >= .10); dec = int(np.flatnonzero((POLICIES == DECLINE).all(1))[0]); N = len(POLICIES)
    def rival(c):  # cheapest full-size policy other than the one being judged; c is [..., 729]
        o = np.sort(c[..., big], -1); m = np.broadcast_to(o[..., :1], c.shape).copy(); idx = c[..., big].argmin(-1)
        if c.ndim == 1: m[big[idx]] = o[1]
        else: m[np.arange(c.shape[0]), big[idx]] = o[:, 1]
        return m
    a = np.ones(N, bool); f = np.ones(N, bool); d_ok = np.ones(N, bool); e_ok = np.ones(N, bool)
    r = np.random.default_rng(seed).beta(1 + allr * s.customers, 1 + (1 - allr) * s.customers, (draws, 6)); wins = {}; wind = {}
    for fu in FUTURES:
        cp, cq, ca = (costs(per_group(x, loans, future=fu)) for x in (pub, pri, allr))
        a &= (cp < rival(cp)) & (cq < rival(cq)); f &= (ca - ca.min() <= 15) & (cq - cq[cp.argmin()] <= 15) & (cp - cp[cq.argmin()] <= 15)
        c = costs(per_group(r, loans, future=fu)); wins[fu] = (c < rival(c)).mean(0); wind[fu] = (c < c[:, [dec]]).mean(0); a &= wins[fu] >= .95
        for am in (s.mean_amount.to_numpy(), s.median_amount.to_numpy()):
            x = costs(per_group(allr, loans, amount=am, future=fu)); d_ok &= x < rival(x)
        x = costs(per_group(allr, loans, mult=2, future=fu)); e_ok &= x < rival(x)
    base = costs(per_group(allr, loans)); b = (base - base[dec] <= 15) & (wind[16] >= .5) & (wind[180] >= .95) & (wind[360] >= .95)
    grid = list(itertools.product((1500., 3000., 6000., 15537.), (0, .1, .3), (16., 32.), (150., 300., 600.), (.5, 1, 1.5, 2, 3), FUTURES)); beat = np.zeros(N)
    for typ, rec, ch, st, m, fu in grid:
        x = costs(per_group(allr, loans, amount=typ, recovered=rec, chase=ch, starter=st, mult=m, future=fu)); beat += x < rival(x)
    t = pd.DataFrame({"policy": ["".join("FSD"[i] for i in p) for p in POLICIES], "A": a, "B": b, "C": beat / len(grid) >= .9, "D": d_ok, "E": e_ok, "F": f, "offered": (POLICIES != DECLINE).dot(wl), "full_size": (POLICIES == FULL).dot(wl), "worst_draw_win_vs_full": np.min([wins[x] for x in FUTURES], 0), "assumption_win_vs_full": beat / len(grid), "cost_future_0": base, "cost_future_16": costs(per_group(allr, loans, future=16)), "cost_future_180": costs(per_group(allr, loans, future=180))})
    t["passed"] = t[list("ABCDEF")].sum(axis=1); t = t.sort_values(["passed", "worst_draw_win_vs_full"], ascending=False); t.to_csv(T / "11c_ghana_all_policies.csv", index=False)
    pd.set_option("display.width", 220); print(t.passed.value_counts().sort_index().to_string()); print(t.head(12).round(3).to_string(index=False)); print(t[t.policy == PROPOSED].round(3).to_string(index=False)); print(t[list("ABCDEF")].sum().to_string())


if __name__ == "__main__":
    run(); every_policy()

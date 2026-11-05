"""Cohort simulation.

For a touch at time t (days) in channel ch, with `alive` the share of the cohort still subscribed:

    w(t)  = floor + (1 - floor) * exp(-t / tau)          intent decay since entering the flow
    f     = 1 / (1 + fat * n48)                           fatigue: n48 = touches in the previous 48 h
    conv  = alive * r_ch * kR * w(t) * f                  conversion
    unsub = alive * u_ch * (1 + ufat * n48)               unsubscribes
    rev   = conv * V * incrementality                     incremental revenue

All parameters are hypotheses (data/params.json); none is estimated from data.
"""
from __future__ import annotations
import math


def simulate(P: dict, sched: list) -> list[dict]:
    ts = sorted((list(x) for x in sched), key=lambda x: x[0])
    alive = 1.0
    rows = []
    for i, x in enumerate(ts):
        t, ch = x[0], x[1]
        n48 = sum(1 for j in range(i) if t - ts[j][0] <= 2)
        w = P["floor"] + (1 - P["floor"]) * math.exp(-t / P["tau"])
        f = 1 / (1 + P["fat"] * n48)
        m = x[4] if len(x) > 4 and x[4] is not None else 1
        r = (P["re"] if ch == "e" else P["rs"]) * P["kR"] * m
        conv = min(alive, alive * r * w * f)
        un = min(alive - conv, alive * (P["ue"] if ch == "e" else P["us"]) * (1 + P["ufat"] * n48))
        clicks = alive * (P["ctrE"] if ch == "e" else P["ctrS"]) * (0.4 + 0.6 * w)
        cost = alive * (P["ce"] if ch == "e" else P["cs"])
        rows.append({"t": t, "ch": ch, "name": x[2] if len(x) > 2 else "", "dest": x[3] if len(x) > 3 else "", "aliveIn": alive,
                     "conv": conv, "un": un, "clicks": clicks, "cost": cost, "rev": conv * P["V"] * P["inc"], "aliveOut": alive - conv - un})
        alive = alive - conv - un
    return rows


def summarize(rows: list[dict], N: float) -> dict:
    keys = ["sends", "sendsE", "sendsS", "conv", "rev", "cost", "costE", "costS", "revE", "revS", "un", "clicks"]
    s = dict.fromkeys(keys, 0.0)
    for r in rows:
        s["sends"] += r["aliveIn"]
        if r["ch"] == "e":
            s["sendsE"] += r["aliveIn"]; s["costE"] += r["cost"]; s["revE"] += r["rev"]
        else:
            s["sendsS"] += r["aliveIn"]; s["costS"] += r["cost"]; s["revS"] += r["rev"]
        s["conv"] += r["conv"]; s["rev"] += r["rev"]; s["cost"] += r["cost"]; s["un"] += r["un"]; s["clicks"] += r["clicks"]
    o = {k: v * N for k, v in s.items()}
    o["net"] = o["rev"] - o["cost"]
    o["roi"] = o["net"] / o["cost"] if o["cost"] else 0.0
    o["aliveEnd"] = rows[-1]["aliveOut"] if rows else 1.0
    o["touches"] = len(rows)
    return o


def rev_share(rows: list[dict], days: float) -> float:
    tot = sum(r["rev"] for r in rows)
    return sum(r["rev"] for r in rows if r["t"] <= days) / tot if tot else 0.0


def flat_sched() -> list:
    return [[d, "e", "Weekly email", "Continue"] for d in range(7, 176, 7)]


def agg_sched() -> list:
    a = [[0.04, "e", "x", "Continue"], [0.2, "s", "x", "Continue"]]
    for d in range(1, 31):
        a.append([d, "e", "x", "Continue"])
        if d % 2 == 0:
            a.append([d + 0.3, "s", "x", "Continue"])
    a += [[d, "e", "x", "Continue"] for d in range(37, 176, 7)]
    return a


def pools(g: dict) -> dict:
    s1 = g["vis"] * g["s1"]; s2 = s1 * g["s2"]; ap = s2 * g["ap"]
    return {"vis": g["vis"], "s1": s1, "s2": s2, "ap": ap, "first": s1 - ap, "acc": ap * g["ac"], "fail": ap * (1 - g["ac"]),
            "asnef": ap * 0.35 * (1 - g["ac"]) + ap * 0.05, "hq": ap * 0.12, "cold": g["cold"], "applied": ap}


def type_params(params: dict, key: str, **over) -> dict:
    t = params["types"][key]
    base = {**params["defaults"], "re": t["re"], "rs": t["rs"], "tau": t["tau"], "V": t["V"], "kR": params["response_multiplier"],
            "inc": params["incrementality"], "ce": params["cost_email"], "cs": params["cost_sms"]}
    base.update(over)
    return base

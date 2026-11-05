"""Compute every number used by the paper, README and tests; write results/results.json.

Run:  python -m remarketing_planner.results
"""
from __future__ import annotations
import json
from pathlib import Path
from . import data as D, model as M, __version__


def build(params: dict) -> dict:
    N = params["cohort"]
    types = {}
    for k, T in params["types"].items():
        P = M.type_params(params, k)
        rows = M.simulate(P, T["sched"]); s = M.summarize(rows, N)
        fl = M.summarize(M.simulate(P, M.flat_sched()), N); ag = M.summarize(M.simulate(P, M.agg_sched()), N)
        types[k] = {"label": T["label"], "L0": T["L0"], "V": T["V"], "re": T["re"], "rs": T["rs"], "tau": T["tau"], "touches": len(rows),
                    "net": s["net"], "rev": s["rev"], "cost": s["cost"], "roi": s["roi"], "conv": s["conv"], "un": s["un"], "aliveEnd": s["aliveEnd"],
                    "ltv": T["L0"] + s["net"] / N, "r24": M.rev_share(rows, 1), "r7": M.rev_share(rows, 7),
                    "flat": {"net": fl["net"], "un": fl["un"]}, "agg": {"net": ag["net"], "un": ag["un"]},
                    "rows": [{"t": r["t"], "ch": r["ch"], "conv": r["conv"], "un": r["un"], "alive": r["aliveOut"], "rev": r["rev"] * N, "cost": r["cost"] * N, "clicks": r["clicks"] * N} for r in rows]}
    T = params["types"]["applied"]
    run = lambda **o: M.summarize(M.simulate(M.type_params(params, "applied", **o), T["sched"]), N)["net"]
    base = M.type_params(params, "applied"); h = params["sensitivity_shock"]
    sens = [["Response +25%", run(kR=1 + h)], ["Response -25%", run(kR=1 - h)], ["Value +25%", run(V=T["V"] * (1 + h))], ["Value -25%", run(V=T["V"] * (1 - h))],
            ["Incrementality +25%", run(inc=params["incrementality"] * (1 + h))], ["Incrementality -25%", run(inc=params["incrementality"] * (1 - h))],
            ["Unsubscribe +25%", run(ue=base["ue"] * (1 + h), us=base["us"] * (1 + h))], ["Unsubscribe -25%", run(ue=base["ue"] * (1 - h), us=base["us"] * (1 - h))]]
    return {"model_version": __version__, "params": {k: v for k, v in params.items() if k not in ("types", "mods")}, "p3": {"types": types, "sens": sens, "base": run()}}


def main(out=None) -> dict:
    res = build(D.load_params())
    path = Path(out) if out else D.ROOT / "results" / "results.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(res, indent=1), encoding="utf-8")
    a = res["p3"]["types"]["applied"]
    print(f"results written to {path}: applied net {a['net']:,.0f} EUR per 10k leads, ROI {a['roi']:.2f}, LTV {a['ltv']:.2f}")
    return res


if __name__ == "__main__":
    main()

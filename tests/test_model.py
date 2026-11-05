import math
import json
import pytest
from remarketing_planner import data, model, results, __version__

P = data.load_params()
N = P["cohort"]


def run(key="applied", **over):
    tp = model.type_params(P, key, **over)
    rows = model.simulate(tp, P["types"][key]["sched"])
    return rows, model.summarize(rows, N)


def test_reproduces_headline_applied_segment():
    rows, s = run()
    assert round(s["net"]) == 9808
    assert round(s["roi"], 1) == 2.6
    assert round(P["types"]["applied"]["L0"] + s["net"] / N, 2) == 11.98
    assert round(model.rev_share(rows, 1), 2) == 0.61


def test_cohort_is_conserved():
    for key, T in P["types"].items():
        rows, s = run(key)
        conv = sum(r["conv"] for r in rows); un = sum(r["un"] for r in rows)
        assert math.isclose(conv + un + rows[-1]["aliveOut"], 1.0, rel_tol=1e-9), key
        assert all(r["aliveOut"] >= -1e-12 for r in rows)


def test_independent_recomputation_of_first_touch():
    T = P["types"]["applied"]; tp = model.type_params(P, "applied")
    t, ch = T["sched"][0][0], T["sched"][0][1]
    w = tp["floor"] + (1 - tp["floor"]) * math.exp(-t / tp["tau"])
    expected = 1.0 * (tp["re"] if ch == "e" else tp["rs"]) * w
    assert math.isclose(model.simulate(tp, T["sched"])[0]["conv"], expected, rel_tol=1e-12)


def test_monotonicity():
    base = run()[1]["net"]
    assert run(kR=1.25)[1]["net"] > base > run(kR=0.75)[1]["net"]
    assert run(V=P["types"]["applied"]["V"] * 1.25)[1]["net"] > base
    assert run(ue=0.0, us=0.0)[1]["aliveEnd"] > run()[1]["aliveEnd"]


def test_zero_incrementality_means_pure_cost():
    _, s = run(inc=0.0)
    assert s["rev"] == 0 and s["net"] == -s["cost"]


def test_more_touches_cost_more_and_unsubscribe_more():
    _, flat = None, model.summarize(model.simulate(model.type_params(P, "applied"), model.flat_sched()), N)
    _, agg = None, model.summarize(model.simulate(model.type_params(P, "applied"), model.agg_sched()), N)
    assert agg["cost"] > flat["cost"] and agg["un"] > flat["un"]


def test_strategy_ranking_documented_in_paper():
    """Front-loaded beats a weekly email in every segment where the flow is profitable; the aggressive daily plan
    earns slightly more net profit in two segments but loses more subscribers (reported in the paper)."""
    res = results.build(P)["p3"]["types"]
    for k in ("applied", "first", "hq"):
        assert res[k]["net"] > res[k]["flat"]["net"]
        assert res[k]["agg"]["un"] > res[k]["un"] * 0.9


def test_sensitivity_shock_matches_ui_labels():
    assert P["sensitivity_shock"] == 0.25


def test_funnel_pools_are_consistent():
    pl = model.pools(P["funnel"])
    assert math.isclose(pl["first"] + pl["ap"], pl["s1"])
    assert math.isclose(pl["acc"] + pl["fail"], pl["ap"])


def test_results_json_is_current():
    res = json.loads((data.ROOT / "results" / "results.json").read_text(encoding="utf-8"))
    assert res["model_version"] == __version__
    assert res["p3"]["base"] == pytest.approx(results.build(P)["p3"]["base"])


def test_readme_quotes_current_headline():
    assert "9,808" in (data.ROOT / "README.md").read_text(encoding="utf-8")

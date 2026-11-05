"""The HTML prototype keeps a JavaScript mirror of the model; it must agree with the Python reference."""
import json
import shutil
import subprocess
import pytest
from remarketing_planner import data, model, results

ROOT = data.ROOT


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_prototype_matches_python():
    html = ROOT / "prototype" / "index.html"
    if not html.exists():
        pytest.skip("run `make prototype` first")
    out = json.loads(subprocess.run(["node", str(ROOT / "tests" / "js_parity.js"), str(html)], capture_output=True, text=True, check=True).stdout)
    ref = results.build(data.load_params())["p3"]["types"]
    for k, v in out.items():
        assert v["net"] == pytest.approx(ref[k]["net"], rel=1e-9)
        assert v["r24"] == pytest.approx(ref[k]["r24"], rel=1e-9)
        assert v["flat"] == pytest.approx(ref[k]["flat"]["net"], rel=1e-9)
        assert v["agg"] == pytest.approx(ref[k]["agg"]["net"], rel=1e-9)

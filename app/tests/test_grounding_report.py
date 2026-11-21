import csv

import demo_data
import grounding_report as g


def test_report_counts_pass_fail_and_unavailable(tmp_path):
    R = demo_data.demo_replay()
    calls = {"n": 0}

    def ask(p, url):
        calls["n"] += 1
        if calls["n"] % 3 == 0:
            raise ConnectionError()
        top = p.split("only these may be quoted): ")[1].split("\n")[0].split(", ")[0]
        return f'It keys on "{top}".' if calls["n"] % 3 == 1 else 'It keys on "banana".'

    out = tmp_path / "r.csv"
    s = g.run(R, n=12, ask=ask, out=str(out))
    assert s["n"] == 12 and s["passed"] + s["failed"] + s["llm_unavailable"] == 12 and s["passed"] == 4 and s["failed"] == 4 and s["llm_unavailable"] == 4
    assert len(list(csv.DictReader(open(out, encoding="utf-8")))) == 12

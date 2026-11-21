"""Tiny template helper: every number in a generated document comes from thesis_numbers.json.
Placeholders:  {{ID}} -> display value;  {{ID|ci}} -> "[lo, hi]";  {{ID|pct}} -> percentage;  {{ID|status}};  {{ID|raw}}.
An unknown id raises, so a document can never silently contain a number that is not in the truth file."""
import json, re
from pathlib import Path

SHOW = Path(__file__).resolve().parents[1]

def numbers():
    return {c["id"]: c for c in json.loads((SHOW / "thesis_numbers.json").read_text(encoding="utf-8"))["claims"]}

def render(text: str, N=None) -> str:
    N = N or numbers()
    def rep(m):
        cid, _, fmt = m.group(1).partition("|"); c = N[cid.strip()]; fmt = fmt.strip()
        if fmt == "ci": return f"[{c['ci'][0]:.3f}, {c['ci'][1]:.3f}]" if c["ci"] else "n/a"
        if fmt == "pct": return f"{100 * float(c['value']):.1f}%"
        if fmt == "status": return c["status"]
        if fmt == "raw": return str(c["value"])
        return c["display"]
    return re.sub(r"\{\{([^}]+)\}\}", rep, text)

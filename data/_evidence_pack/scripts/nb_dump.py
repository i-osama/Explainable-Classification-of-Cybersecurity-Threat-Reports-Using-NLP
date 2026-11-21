"""Dump every notebook to nb_src/<name>.txt (code + markdown + truncated text outputs) so settings
can be cited as notebook:cell and grepped. Read-only on the notebooks."""
import json
from common import ROOT, PACK

out = PACK / "nb_src"; out.mkdir(exist_ok=True)
nbs = sorted(list((ROOT / "Experiments").glob("*.ipynb")) + list(ROOT.glob("*.ipynb")))
for nb in nbs:
    d = json.loads(nb.read_text(encoding="utf-8"))
    L = []
    for i, c in enumerate(d["cells"]):
        L.append(f"\n# ==== CELL {i} [{c['cell_type']}] exec={c.get('execution_count')} ====")
        L.append("".join(c["source"]))
        if c["cell_type"] == "code":
            txt = []
            for o in c.get("outputs", []):
                if o.get("output_type") == "stream":
                    txt.append("".join(o.get("text", "")))
                elif "data" in o and "text/plain" in o["data"]:
                    txt.append("".join(o["data"]["text/plain"]))
                elif o.get("output_type") == "error":
                    txt.append("ERROR: " + o.get("ename", "") + " " + o.get("evalue", ""))
            t = "\n".join(txt)
            if t.strip():
                lines = t.splitlines()
                if len(lines) > 400:
                    lines = lines[:250] + [f"... [{len(lines)-400} lines cut] ..."] + lines[-150:]
                L.append(f"# ---- OUTPUT (cell {i}) ----")
                L += ["#> " + x[:400] for x in lines]
    (out / (nb.stem + ".txt")).write_text("\n".join(L), encoding="utf-8")
    print(f"{nb.name}: cells={len(d['cells'])} lines={sum(x.count(chr(10))+1 for x in L)}")

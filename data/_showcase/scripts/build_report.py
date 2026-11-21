"""T7: report/index.html: one self-contained file (images inlined, sortable tables in vanilla JS).
All numbers come from thesis_numbers.json via {{id}} placeholders or from the claims table itself."""
import base64, html, json, re, sys
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _tpl import render, numbers, SHOW

N = numbers(); FIG = SHOW / "figures"
def img(stem, cap):
    b = base64.b64encode((FIG / f"{stem}.png").read_bytes()).decode()
    alt = ""
    for l in (FIG / "FIGURES.md").read_text(encoding="utf-8").splitlines():
        if l.startswith(f"| {stem} |"): alt = l.split("|")[-2].strip()
    return f'<figure><img alt="{html.escape(alt)}" src="data:image/png;base64,{b}"><figcaption>{cap}</figcaption></figure>'
def md_inline(t):
    t = html.escape(t); t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t); t = re.sub(r"`(.+?)`", r"<code>\1</code>", t); return t
def bullets(text):
    out, items = [], []
    for l in text.strip().splitlines():
        if l.startswith("- "): items.append(f"<li>{md_inline(l[2:])}</li>")
        elif l.strip():
            if items: out.append("<ul>" + "".join(items) + "</ul>"); items = []
            out.append(f"<p>{md_inline(l)}</p>")
    if items: out.append("<ul>" + "".join(items) + "</ul>")
    return "\n".join(out)
def table(head, rows, cls="sortable"):
    return f'<table class="{cls}"><thead><tr>' + "".join(f"<th>{html.escape(h)}</th>" for h in head) + "</tr></thead><tbody>" + \
           "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table>"
def c(i): return html.escape(N[i]["display"])
def ci(i): return f"[{N[i]['ci'][0]:.3f}, {N[i]['ci'][1]:.3f}]" if N[i]["ci"] else ""

readme = (SHOW / "README.md").read_text(encoding="utf-8")
story = readme.split("## One-page story")[1].split("## Verify in 10 minutes")[0]
systems = [("Frequency prior", "B0"), ("bge matcher, zero-shot", "B10a"), ("TF-IDF + SVM", "B6"), ("SecBERT, 3-seed average", "B8"), ("RoBERTa, 3-seed average", "B7"), ("Classifiers-only ensemble", "B9"),
           ("Matcher, 3-seed ensemble", "B10c"), ("Fusion, equal weights", "B11.avg"), ("Fusion (3,1,1,1), seed-averaged", "B13a")]
sys_rows = [[n, c(i), ci(i), c(i + ".mrr3") if i + ".mrr3" in N else c("B13b"), f"<code>{i}</code>"] for n, i in systems]
cmp_rows = [[html.escape(N[i]["label"].replace(", delta P@1", "")), c(i), ci(i), c(i + ".p"), c(i + ".holm"), html.escape(N[i]["note"].split(": ")[-1])] for i in ("C1", "C2", "C3", "C4", "ABL.A1", "ABL.A2", "ABL.A3", "ABL.A4")]
bk = ["unseen", "1_4", "5_9", "10_19", "20_49", "50plus"]
sup_rows = [[b.replace("_", "-").replace("plus", "+"), c(f"G4.n.{b}")] + [f"{c(f'G4.{s}.{b}')} {ci(f'G4.{s}.{b}')}" for s in ("svm", "roberta", "secbert", "matcher", "fusion")] for b in bk]
faith = [[html.escape(N[k]["label"].replace("Faithfulness: ", "").replace(", SHAP minus random", "")), c(k + ".shap"), c(k + ".random"), c(k), ci(k), html.escape(N[k]["note"].split(";")[0].split(": ")[-1])] for k in ("E5.del_auc", "E5.ins_auc", "E5.comp_prob", "E5.suff_prob")]
st = yaml.safe_load((SHOW / "STATUS.yaml").read_text(encoding="utf-8"))["items"]
st_rows = [[i["id"], html.escape(i["area"]), html.escape(i["item"]), f'<span class="st {i["state"]}">{i["state"]}</span>', f"<code>{html.escape(i['evidence'])}</code>"] for i in st]
claim_rows = [[f"<code>{k}</code>", html.escape(v["thesis_section"]), html.escape(v["label"]), html.escape(v["display"]), ci(k), f'<span class="st {v["status"]}">{v["status"]}</span>', f"<code>{html.escape(v['source_file'])}</code>"] for k, v in N.items()]
todo = [[f"<code>{k}</code>", html.escape(v["label"]), f"<code>{html.escape(v['source_file'])}</code>"] for k, v in N.items() if v["status"] == "TODO-COLAB"]
nf = [[f"<code>{k}</code>", html.escape(v["label"]), html.escape(v["definition"])] for k, v in N.items() if v["status"] == "NOT-FOUND"]

BODY = f"""
<h1>Explainable classification of cyber-threat reports</h1>
<p class="sub">Research showcase: sentence-level mapping of CTI text to MITRE ATT&amp;CK techniques (TRAM). Every number on this page is rendered from <code>thesis_numbers.json</code>; claim ids are shown in the tables.</p>
<nav><a href="#story">Story</a><a href="#pipeline">Pipeline</a><a href="#data">Data</a><a href="#results">Results</a><a href="#errors">Error analysis</a><a href="#xai">Explainability</a><a href="#limits">Limits</a><a href="#done">What we did</a><a href="#todo">Still to do</a><a href="#repro">Reproducibility</a><a href="#claims">All numbers</a></nav>
<h2 id="story">1 One-page story</h2>{bullets(render(story, N))}
<h2 id="pipeline">2 Pipeline and protocol</h2>{img("fig01_architecture", "Four components and the late fusion.")}{img("fig02_protocol", "What is fitted, what is selected on the development set only, and what is reported.")}
<h2 id="data">3 Data card</h2>
<p>{{{{A1}}}} sentences; {{{{A2}}}} train / dev / test; {{{{A3}}}} labels in training; {{{{A4}}}} in test ({{{{A5}}}} seen + unseen). Overlap with train: {{{{A6}}}}. Truncated at 128 tokens: {{{{A7}}}}.
Description file: {{{{A8}}}}. The dataset licence is not documented in the project, so no sentence text is shipped; tables carry ids and hashes only.</p>
{img("fig04_data_long_tail", "Sentences per split and the long tail of training labels.")}{img("fig03_er_diagram", "Data models used for every shipped table.")}
<h2 id="results">4 Results with intervals</h2>
{table(["system", "P@1", "95% CI", "MRR@3", "claim id"], sys_rows)}
<p>Fusion headline definitions: seed-averaged {{{{B13a}}}}; seed-paired {{{{B12a}}}}; notebook definition (matcher seed varied) {{{{B12nb}}}}. Weights: {{{{B14}}}}.</p>
{img("fig05_all_systems", "All systems with 95% bootstrap intervals.")}
<h3>Paired comparisons (family of 8, Holm-corrected)</h3>
{table(["comparison", "delta P@1", "95% CI", "McNemar p", "Holm p", "supported"], cmp_rows)}
{img("fig07_forest_deltas", "Paired differences in P@1.")}{img("fig09_ablation", "Fusion with one component removed.")}{img("fig08_weight_sensitivity", "Sensitivity to the fusion weights; circle = (3,1,1,1), square = (4,1,1,1).")}
<h2 id="errors">5 Error analysis</h2>
{table(["train support of rarest gold label", "n", "SVM", "RoBERTa", "SecBERT", "Matcher", "Fusion"], sup_rows)}
{img("fig06_support_buckets", "P@1 by label frequency.")}{img("fig10_fixed_broken", "Sentences fixed and broken by the fusion.")}{img("fig11_tactic_heatmap", "P@1 by tactic.")}{img("fig12_top_confusions", "Most frequent confusions of the fusion.")}{img("fig13_reliability", "Calibration of the classifiers.")}
<h2 id="xai">6 Explainability</h2>
<p>Explained model: RoBERTa, seed 42 ({{{{E1}}}}). Deletion test on the fixed sample: {{{{E2}}}} logits, {{{{E3}}}}; on all eligible test sentences: {{{{E2.all}}}} logits, {{{{E3.all}}}}.</p>
{table(["measure", "SHAP order", "random order", "difference", "95% CI", "supported"], faith)}
{img("fig15_faithfulness_curves", "Deletion and insertion curves.")}{img("fig14_shap_examples", "Three rule-selected examples (RoBERTa only).")}{img("fig19_human_agreement", "First human study: agreement at chance.")}
<h2 id="limits">7 Limitations and negative findings</h2>
<ul><li>RoBERTa and SecBERT are not better than the SVM with statistical support (C3, C4).</li><li>The gain of the fusion over the matcher ensemble does not survive correction for multiple tests (C2).</li>
<li>The fusion does not help unseen or rare techniques; a pre-registered support-aware fusion did not change that (success rule met: {{{{G9.v2.success}}}}).</li>
<li>Explanations cover one component; its top-1 label differs from the fusion's on {{{{E4}}}} test sentences.</li><li>Human agreement on plausibility is at chance (alpha {{{{D1}}}}).</li>
<li>The published baseline was not re-run; split and training mode are not verified to match.</li><li>Reading 256 instead of 128 tokens at inference gives no gain on the truncated sentences (RoBERTa hits {{{{G11.roberta}}}}).</li></ul>
{img("fig16_latency_accuracy", "CPU latency against accuracy.")}
<h2 id="done">8 What we did</h2>{img("fig17_process_timeline", "Timeline reconstructed from file timestamps.")}
<h2 id="todo">9 What is still to do</h2>{img("fig18_status_board", "Status board by area.")}
{table(["id", "area", "item", "state", "evidence"], st_rows)}
<h3>Waiting for a Colab run</h3>{table(["claim id", "item", "notebook"], todo)}
<h3>Not found (never claimed)</h3>{table(["id", "item", "where it was searched"], nf)}
<h2 id="repro">10 Reproducibility</h2>
<p>From the showcase folder: <code>python scripts/run_tests.py</code>, <code>python scripts/verify_claims.py</code>, <code>python scripts/check_hashes.py</code>. Details: <code>INVIGILATOR_GUIDE.md</code>. Colab steps: <code>notebooks/RUN_ORDER.md</code> (none has been run on Colab).</p>
<h2 id="claims">11 All numbers</h2><p>Click a column header to sort.</p>
{table(["id", "section", "label", "value", "95% CI", "status", "source"], claim_rows)}
"""
CSS = """body{font-family:Georgia,'Times New Roman',serif;max-width:1040px;margin:0 auto;padding:16px;color:#1a1a1a;background:#fff;line-height:1.5}
h1{font-size:1.7em;margin-bottom:.1em}h2{border-bottom:2px solid #0072B2;padding-bottom:3px;margin-top:2em}.sub{color:#555}
nav{position:sticky;top:0;background:#fff;padding:6px 0;border-bottom:1px solid #ddd;display:flex;flex-wrap:wrap;gap:12px;font-size:.9em}nav a{color:#0072B2;text-decoration:none}
table{border-collapse:collapse;width:100%;font-size:.86em;margin:1em 0;display:block;overflow-x:auto}th,td{border:1px solid #ccc;padding:4px 7px;text-align:left;vertical-align:top}
th{background:#eef3f8;cursor:pointer;white-space:nowrap}tr:nth-child(even) td{background:#fafafa}code{font-size:.9em;background:#f3f3f3;padding:0 3px}
figure{margin:1.2em 0;text-align:center}figure img{max-width:100%;height:auto;border:1px solid #eee}figcaption{font-size:.88em;color:#444}
.st{font-size:.8em;padding:1px 6px;border-radius:3px;white-space:nowrap;border:1px solid #999}.DONE,.RECOMPUTED,.VERIFIED{background:#d9f0e6}.PARTIAL{background:#fbf3c4}
.NEGATIVE-RESULT{background:#f8d9cc}.TODO-COLAB{background:#d8ecf9}.TODO-AUTHOR{background:#fde7c2}.NOT-FOUND,.NOTES-ONLY{background:#e6e6e6}.FUTURE-WORK{background:#ecd9e8}"""
JS = """document.querySelectorAll('table.sortable th').forEach(function(th){th.addEventListener('click',function(){var t=th.closest('table'),b=t.tBodies[0],i=Array.prototype.indexOf.call(th.parentNode.children,th),
d=th.dataset.d=th.dataset.d==='a'?'d':'a',r=Array.prototype.slice.call(b.rows);r.sort(function(x,y){var a=x.cells[i].innerText.trim(),c=y.cells[i].innerText.trim(),p=parseFloat(a.replace(/[^0-9.+-]/g,'')),q=parseFloat(c.replace(/[^0-9.+-]/g,''));
var v=(!isNaN(p)&&!isNaN(q)&&/^[+-]?[0-9]/.test(a)&&/^[+-]?[0-9]/.test(c))?p-q:a.localeCompare(c);return d==='a'?v:-v});r.forEach(function(x){b.appendChild(x)})})});"""
out = SHOW / "report"; out.mkdir(exist_ok=True)
page = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>TTP mapping showcase</title><style>{CSS}</style></head><body>{render(BODY, N)}<script>{JS}</script></body></html>'
assert "{{" not in page, "unresolved placeholder"
(out / "index.html").write_text(page, encoding="utf-8")
print(f"report/index.html: {len(page) / 1e6:.1f} MB, {page.count('<figure>')} figures, {page.count('<table')} tables, external references: {len(re.findall(r'(src|href)=.https?://', page))}")

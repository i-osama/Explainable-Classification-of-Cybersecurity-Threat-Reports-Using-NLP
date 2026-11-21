"""T8: QA gates. Writes results/qa_gates.json and prints one line per gate. Exit 1 if any gate fails.
Gates: tests, verify_claims, number consistency, notebooks, figures, links, secrets/PII/dataset text, hashes, zip size."""
import json, re, subprocess, sys
from pathlib import Path
import nbformat
sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import audit_numbers as A
SHOW = Path(__file__).resolve().parents[1]; ROOT = SHOW.parent; G = []
def gate(name, ok, detail): G.append({"gate": name, "result": "PASS" if ok else "FAIL", "detail": detail}); print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}"[:230])
def run(script, *args):
    r = subprocess.run([sys.executable, "-X", "utf8", str(SHOW / "scripts" / script), *args], capture_output=True, text=True, encoding="utf-8", cwd=SHOW)
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1]

rc, last = run("run_tests.py"); gate("tests", rc == 0, last + " (runner: scripts/run_tests.py; pytest not installed)")
rc, last = run("verify_claims.py"); gate("verify_claims within 0.001", rc == 0, last)

# ---- number consistency: README, report, notebook markdown
J = json.loads((SHOW / "thesis_numbers.json").read_text(encoding="utf-8")); reg = []; A.flatten(J, reg); reg = sorted(set(reg))
allow = set(A.DEFAULT_ALLOW) | {l.split("#")[0].strip() for l in (SHOW / "configs" / "number_whitelist.txt").read_text(encoding="utf-8").splitlines() if l.split("#")[0].strip()}
def scan(text):
    bad = []; t = A.clean_for_numbers(text)
    for m in A.NUM.finditer(t):
        tok = m.group().strip()
        try: val, pct, dec, d = A.parse_token(tok)
        except Exception: continue
        if A.kind_of(val, pct, dec) in ("year", "int<10"): continue
        if tok.lstrip("+-−– ").rstrip("%") in allow or str(val) in allow or A.matches(val, pct, dec, d, reg): continue
        bad.append((tok, t[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")))
    return bad
def strip_md(t):                                                   # code, paths and ids are not prose numbers; marked worked examples are invented on purpose
    t = re.sub(r"<!-- illustrative -->.*?<!-- /illustrative -->", " ", t, flags=re.S)
    return re.sub(r"`[^`]*`", " ", re.sub(r"```.*?```", " ", t, flags=re.S))
docs = {"README.md": strip_md((SHOW / "README.md").read_text(encoding="utf-8"))}
for f in ("EXPLAINER_MATCHER_FUSION.md", "Q1_MANUSCRIPT_BRIEF.md", "WEB_CLAUDE_PROMPT.md"):      # Q1 plan documents written for the article
    if (SHOW / "thesis_feed" / f).exists(): docs[f"thesis_feed/{f}"] = strip_md((SHOW / "thesis_feed" / f).read_text(encoding="utf-8"))
h = (SHOW / "report" / "index.html").read_text(encoding="utf-8")
h = re.sub(r"<(script|style)>.*?</\1>", " ", h, flags=re.S); h = re.sub(r'src="data:[^"]*"', "", h); h = re.sub(r"<code>.*?</code>", " ", h, flags=re.S); docs["report/index.html"] = re.sub(r"<[^>]+>", " ", h)
for p in sorted((SHOW / "notebooks").glob("*.ipynb")):
    docs[f"notebooks/{p.name}"] = strip_md("\n".join(c.source for c in nbformat.read(p, 4).cells if c.cell_type == "markdown"))
bad = {k: scan(v) for k, v in docs.items()}; nbad = sum(len(v) for v in bad.values())
gate("number consistency (README, report, notebook text)", nbad == 0, f"{len(docs)} documents; unregistered numeric tokens: {nbad}" + ("; e.g. " + "; ".join(f"{k}: {t} [{c.strip()[:50]}]" for k, v in bad.items() for t, c in v[:2])[:400] if nbad else ""))

# ---- notebooks
nbs = sorted((SHOW / "notebooks").glob("*.ipynb")); okv = 0; logs = 0; claims_run = []
for p in nbs:
    nb = nbformat.read(p, 4)
    try: nbformat.validate(nb); okv += 1
    except Exception: pass
    lp = SHOW / "results" / "smoke_logs" / f"{p.stem}.json"
    logs += int(lp.exists() and json.loads(lp.read_text())["status"] == "PASS")
    if "NOT RUN ON COLAB" not in nb.cells[0].source or any(c.get("outputs") for c in nb.cells if c.cell_type == "code"): claims_run.append(p.name)
gate("notebooks valid, smoke-logged, not presented as run", okv == len(nbs) == logs and not claims_run, f"{len(nbs)} notebooks; nbformat valid {okv}; smoke PASS {logs}; with outputs or without NOT-RUN header: {claims_run or 'none'}")

# ---- figures
fm = (SHOW / "figures" / "FIGURES.md").read_text(encoding="utf-8"); stems = sorted({p.stem for p in (SHOW / "figures").glob("fig*.png")}); miss = []
for s in stems:
    row = [l for l in fm.splitlines() if l.startswith(f"| {s} |")]
    if not (SHOW / "figures" / f"{s}.svg").exists() or not row or len(row[0].split("|")[-2].strip()) < 40: miss.append(s)
gate("figures: png + svg + FIGURES.md row + alt text", len(stems) == 19 and not miss, f"{len(stems)} figures; incomplete: {miss or 'none'}")

# ---- links (paths quoted in the landing documents)
missing = []
for doc in ("README.md", "INVIGILATOR_GUIDE.md", "notebooks/RUN_ORDER.md", "figures/FIGURES.md"):
    for tok in re.findall(r"`([^`\s]+\.(?:md|py|json|yaml|csv|html|ipynb|ps1|cff|txt|parquet))`", (SHOW / doc).read_text(encoding="utf-8")):
        if any(ch in tok for ch in "*<>{") or tok.startswith(("MyDrive", "showcase_runs", "run_match_2", "human_study", "manifest_", "ckpt_", "matcher_state", "THESIS_DELTA")): continue
        t = tok.replace("\\", "/"); cands = [SHOW / t, ROOT / t, (SHOW / doc).parent / t, SHOW / "results" / t, SHOW / "scripts" / t, SHOW / "docs" / t, ROOT / "_evidence_pack" / t, SHOW / "figures" / t, SHOW / "notebooks" / t]
        if not any(c.exists() for c in cands): missing.append(f"{doc}: {tok}")
gate("link check (file paths in landing documents)", not missing, f"missing: {missing[:6] or 'none'}")

# ---- secrets, PII, dataset text
from ttpmap.data import load_split, norm_text
sents = {norm_text(t) for sp in ("train", "dev", "test") for t in load_split(sp)["text"] if len(str(t)) >= 60}
tracked = subprocess.run(["git", "ls-files", "_showcase"], capture_output=True, text=True, cwd=ROOT).stdout.split("\n")
hits = []
PAT = [("user path", re.compile(r"C:\\\\?Users\\\\?\w+", re.I)), ("email", re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", re.I)), ("secret", re.compile(r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|hf_[A-Za-z0-9]{30,})")),
       ("rater file name", re.compile("hand_check_v2_roberta_pw_s42" + r"_+(By|rated)", re.I))]      # split so the commit guard does not flag this file
ALLOW_TEXT = {"_showcase/scripts/qa_gates.py", "_showcase/scripts/git_commit.ps1", "_showcase/scripts/audit_numbers.py"}
for f in tracked:
    p = ROOT / f
    if not f or not p.exists() or p.suffix.lower() in (".png", ".svg", ".parquet") or p.stat().st_size > 6e6: continue
    try: t = p.read_text(encoding="utf-8", errors="ignore")
    except Exception: continue
    if f not in ALLOW_TEXT:
        for name, rx in PAT:
            m = rx.search(t)
            if m and not (name == "email" and m.group().endswith(("@huawei.com", "@0", "@1", "@3", "@5", "@k", "@10"))): hits.append(f"{f}: {name} ({m.group()[:40]})")
    tn = norm_text(re.sub(r"<[^>]+>", " ", t)) if p.suffix == ".html" else norm_text(t)
    n_s = sum(1 for s in sents if s in tn)
    if n_s > 3: hits.append(f"{f}: {n_s} full dataset sentences")
gate("no secrets, user paths, PII or dataset text beyond short excerpts", not hits, f"{len([x for x in tracked if x])} tracked files scanned; findings: {hits[:5] or 'none'}")

rc, last = run("check_hashes.py"); gate("hashes recorded and matching", rc == 0, last)
zp = ROOT / "_showcase.zip"
gate("zip under 50 MB", zp.exists() and zp.stat().st_size < 50e6, f"{zp.stat().st_size / 1e6:.1f} MB" if zp.exists() else "zip not built yet (run scripts/package.py)")
(SHOW / "results" / "qa_gates.json").write_text(json.dumps(G, indent=1), encoding="utf-8")
sys.exit(0 if all(g["result"] == "PASS" for g in G) else 1)

"""Streamlit app: ranked ATT&CK techniques, conformal set, triage flag, SHAP words and a grounded explanation.

Run:  streamlit run app.py        (set TTPMAP_ROOT to the thesis folder, TTPMAP_DEMO=1 for synthetic data)
"""
import html
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

import core
import explain
import home

st.set_page_config(page_title="ATT&CK threat-report explainer", layout="wide")
ROOT = os.environ.get("TTPMAP_ROOT", r"E:\Osamas Paper")
TIERS = ["High confidence", "Medium confidence", "Low confidence: analyst review"]
TIER_COL = ["#1B7F5A", "#B7791F", "#B42318"]
MODES = ["Start here", "Try a sentence", "Check a whole report", "Train and check", "Browse test sentences",
         "Compare: GPU, CPU, local AI", "Advanced: classifiers only"]
HOME, LIVE, REPORT, TRAIN, REPLAY, COMPARE, CLS = MODES
MODE_HELP = ["What this is, in one minute.", "Type one sentence: get the technique, the words that mattered and how sure it is.",
             "Paste a report: get a technique for every sentence, as a table you can download.",
             "Teach it your own examples, then see proof that it learned them.",
             "The 725 thesis test sentences, with the stored results.",
             "The same models on GPU or CPU, and a local AI chatbot, side by side.",
             "Expert view: three models without the matcher."]
MAX_WORDS = 40  # live SHAP cost grows with n_perm x (2 x words + 1) model passes: one sentence, not a paragraph
APP_DIR = Path(__file__).parent
CSS = """<style>
h1, h2, h3, .verdict .tid {font-family: Bahnschrift, "Segoe UI", sans-serif; letter-spacing: .01em;}
h1 {font-weight: 600;}
.sub {color: #3A4A66; margin: -.6rem 0 1rem 0;}
.verdict {border-left: 6px solid var(--tier); background: #FFFFFF; padding: .8rem 1rem; border-radius: 4px; margin-bottom: .8rem;}
.verdict .tid {font-size: 2.1rem; line-height: 1.1; color: #14213D;}
.verdict .tname {font-size: 1.05rem; color: #14213D;}
.verdict .chip {display: inline-block; margin-top: .4rem; padding: .1rem .6rem; border-radius: 999px; background: var(--tier); color: #FFFFFF; font-size: .85rem;}
.shap span {border-radius: 3px; padding: 0 1px;}
</style>"""


@st.cache_resource(show_spinner="Loading saved scores (the SVM refit takes a moment)...")
def get_replay(root, demo):
    if demo:
        import demo_data
        return demo_data.demo_replay()
    return core.load_replay(root)


@st.cache_resource(show_spinner="Loading the models on CPU (first time about 1-2 minutes)...")
def get_live(root, full):
    import live
    return live.load(get_replay(root, False).art, full)


def comps_for(root, full):
    """Live components; after teach mode the SVM is the retrained one (session only)."""
    import live
    cs, t = get_live(root, full), st.session_state.get("taught")
    return [live.SvmComp(t["art"]) if c.name == "svm" else c for c in cs] if t else cs


def cal_live(R, full):
    t = st.session_state.get("taught")
    return t["cal"][full] if t else (R.cal_full if full else R.cal_cls)


def taught_banner():
    t = st.session_state.get("taught")
    if t:
        st.info(f"This is the custom-trained version: your {t['n']} examples are included (a demo feature, not a thesis result). "
                "Undo it in 'Train and check'.")


def report_ui(R, root, full, n_perm, alpha, use_llm, url):
    import live
    st.caption("Paste a threat report or upload a file. Every sentence (up to 300) is scored with the "
               + ("full fusion (3,1,1,1)." if full else "classifier-only fusion.") + " About 0.15 s per sentence; SHAP only for the one you pick.")
    up = st.file_uploader("Upload a .txt, .md or .csv file (or paste below)", type=["txt", "md", "csv"], key="report_file")
    text = st.text_area("Report text", height=180, key="report")
    if st.button("Find techniques", type="primary"):
        try:
            src = core.read_upload(up.name, up.getvalue()) if up is not None else text
        except (ValueError, UnicodeError) as e:
            src = ""
            st.error(f"File not read ({type(e).__name__}): use a UTF-8 .txt file or a CSV with a text column.")
        sents = core.split_sentences(src)
        st.session_state.pop("report_exp", None)
        if not sents:
            st.warning("No sentence of 3 or more words found. Paste report text or upload a file.")
        else:
            with st.spinner(f"Scoring {len(sents)} sentences on CPU..."):
                st.session_state["report_res"] = (sents, live.score_batch(comps_for(root, full), sents, live.FULL_W if full else None), full,
                                                  memory_hits(root, full, sents))
    res = st.session_state.get("report_res")
    if not res or res[2] != full:
        return
    sents, S, _, hits = res
    cal = cal_live(R, full)
    rows = []
    for i, (sent, row) in enumerate(zip(sents, S)):
        a = core.assess(row, cal, alpha)
        rows.append({"#": i + 1, "sentence": sent, "top technique": R.name(R.labels[int(a["order"][0])]), "confidence": TIERS[a["tier"]],
                     "set size": len(a["set"])})
        if any(hits):
            rows[-1]["from your examples"] = R.name(hits[i][0][0]) if hits[i] else ""
    st.dataframe(rows, hide_index=True, width="stretch", column_config={"#": st.column_config.NumberColumn(width="small"),
                 "sentence": st.column_config.TextColumn(width="large"), "set size": st.column_config.NumberColumn(width="small")})
    st.download_button("Download results (CSV)", pd.DataFrame(rows).to_csv(index=False).encode("utf-8"), "techniques_found.csv", "text/csv")
    k = st.selectbox("Explain sentence", range(len(sents)), format_func=lambda i: f"{i + 1}: {sents[i][:100]}")
    if st.button("Explain this sentence"):
        n_words = len(core.split_units(sents[k]))
        if n_words > MAX_WORDS:
            st.warning(f"Sentence {k + 1} has {n_words} words; SHAP is limited to {MAX_WORDS}. Its prediction is in the table.")
        else:
            with st.spinner("Explaining on CPU..."):
                st.session_state["report_exp"] = (k, live.analyse(comps_for(root, full), sents[k], n_perm, weights=live.FULL_W if full else None))
    e = st.session_state.get("report_exp")
    if e and e[0] == k:
        o = e[1]
        render(R, sents[k], o["scores"], cal, o["units"], o["values"], R.labels[o["k"]], None, alpha, "full" if full else "cls", use_llm, url)


def load_sample():
    try:
        ex = json.loads((APP_DIR / "examples_teach.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    st.session_state["teach"], st.session_state["teach_check"] = "\n".join(ex["train"]), "\n".join(ex["check"])


@st.cache_resource(show_spinner="Reading the 604 thesis check sentences with the matcher (once)...")
def get_dev_emb(root):
    import teach
    return teach.matcher_emb(get_live(root, True), get_replay(root, False).art["dev"]["texts"])


def labelled(text, up, R):
    rows, errs = core.parse_labelled(text, R.labels)
    if up is not None:
        try:
            r2, e2 = core.validate_rows(core.read_labelled_csv(up.getvalue()), R.labels, 2)
        except (ValueError, KeyError, StopIteration, SyntaxError) as ex:
            r2, e2 = [], [f"CSV not read: it needs a text column and a labels column ({type(ex).__name__})."]
        rows, errs = rows + r2, errs + e2
    return rows, errs


def train_ui(R, root):
    import live
    import teach
    st.subheader("Train and check")
    st.markdown("Teach the tool a technique with a few example sentences. Then test it on **other** sentences. "
                "The page shows whether it really learned, and checks that it did not get worse on the thesis sentences.")
    st.button("Load a ready-made example", on_click=load_sample)
    st.caption("One sentence per line: technique code, colon, sentence. Example:  T1486: The ransomware encrypted every file on the shared drive.")
    c1, c2 = st.columns(2)
    text = c1.text_area("1. Training examples", height=170, key="teach")
    check = c2.text_area("2. Test sentences (different wording, not used for training)", height=170, key="teach_check")
    up = c1.file_uploader("Or upload training examples as CSV (text and labels columns)", type=["csv"], key="teach_file")
    if st.button("Train and check", type="primary"):
        rows, errs = labelled(text, up, R)
        crow, cerrs = core.parse_labelled(check, R.labels)
        kept, msgs = teach.split_check(rows, crow)
        for msg in (errs + cerrs)[:10]:
            st.error(msg)
        for msg in msgs:
            st.info(msg)
        if len(rows) > 500:
            st.error(f"{len(rows)} sentences: at most 500 per training in this demo.")
        elif rows:
            full = R.cal_full is not None
            t0 = time.perf_counter()
            with st.spinner(f"Training with {len(rows)} examples, then checking {len(kept)} test sentences and the 604 thesis sentences..."):
                art2 = core.retrain_svm(R.art, rows)
                cal = {False: core.calib_for(art2, False), True: core.calib_for(art2, True) if full else None}
                comps0 = get_live(root, full)
                comps1 = [live.SvmComp(art2) if c.name == "svm" else c for c in comps0]
                tm = teach.load_t(root) if full else None
                mem = teach.build_memory(comps0, rows, tm) if tm is not None else None
                w = live.FULL_W if full else (1, 1, 1)
                tr_texts, ck_texts = [s for s, _ in rows], [s for s, _ in kept]
                tr_rep = teach.check_report(teach.predict(comps0, R.labels, tr_texts, None, w), teach.predict(comps1, R.labels, tr_texts, mem, w),
                                            [ids for _, ids in rows])
                before, after = teach.predict(comps0, R.labels, ck_texts, None, w), teach.predict(comps1, R.labels, ck_texts, mem, w)
                E_dev = get_dev_emb(root) if mem is not None else None
                dev = (teach.dev_p1(R, R.art, None, E_dev), teach.dev_p1(R, art2, mem, E_dev))
            st.session_state["taught"] = {"art": art2, "n": len(rows), "cal": cal, "s": time.perf_counter() - t0, "memory": mem,
                                          "result": {"train": tr_rep, "check": teach.check_report(before, after, [ids for _, ids in kept]),
                                                     "dev": dev, "rows": kept, "before": before, "after": after}}
            for k in ("live", "report_res", "report_exp"):
                st.session_state.pop(k, None)
        elif not errs:
            st.warning("Type at least one training example first, or load the ready-made example.")
    t = st.session_state.get("taught")
    if not t:
        return
    res = t["result"]
    ok, msg = teach.verdict(res["train"], res["check"], *res["dev"])
    (st.success if ok else st.warning)(msg)
    if res["rows"]:
        st.dataframe([{"test sentence": s, "expected": ", ".join(ids), "before training": R.name(b["top"]),
                       "after training": R.name(a["top"]) + (f"  (like your example {a['example'] + 1}, similarity {a['sim']:.2f})"
                                                             if a["source"] == "memory" else ""),
                       "right now": "yes" if a["top"] in ids else "no"}
                      for (s, ids), b, a in zip(res["rows"], res["before"], res["after"])], hide_index=True, width="stretch")
    m = t.get("memory")
    st.caption(f"Trained in {t['s']:.1f} s: the SVM was refit on {len(R.art['train']['texts'])} thesis sentences + {t['n']} examples"
               + (f", and the example memory is on (a new sentence with similarity >= {m.t:.2f} to an example gets its technique; "
                  "threshold set on thesis train/dev data)" if m else ", example memory off (no calibration file in this folder)")
               + ". 'Try a sentence' and 'Check a whole report' now use the trained version until you press Undo or close the page. "
                 "A demo feature, not a thesis result.")
    if st.button("Undo: back to the thesis model"):
        for k in ("taught", "live", "report_res", "report_exp"):
            st.session_state.pop(k, None)
        st.rerun()


def memory_hits(root, full, texts):
    """Example-memory matches for these sentences after training (full fusion only: the memory uses the matcher)."""
    import teach
    t = st.session_state.get("taught")
    if not t or not t.get("memory") or not full or not texts:
        return [None] * len(texts)
    return t["memory"].lookup(teach.matcher_emb(get_live(root, True), texts))


@st.cache_resource(show_spinner="Reading the GPU score files...")
def get_gpu_s42(root):
    import compare
    return compare.gpu_fused_s42(get_replay(root, False))


def answer_rows(R, ids, gold):
    return [{"rank": r + 1, "technique": R.name(t), "gold": "yes" if t in gold else ""} for r, t in enumerate(ids)]


def compare_ui(R, root, url):
    import compare
    st.subheader("Compare: GPU vs CPU vs local LLM")
    st.info("Short answer: running the same model on a GPU or on a CPU changes the speed, not the answer. "
            "Changing the model changes the answer: the trained fusion is the most accurate, the local LLM alone the least.")
    res = compare.results_dir(root)

    st.markdown("#### 1. Accuracy on all 725 test sentences (thesis runs)")
    ms, ms_sum = compare.cpu_ms(R)
    rows = compare.ranking(R)
    st.dataframe([{"result": r["rank"], "system": r["system"], "test P@1": f"{r['P@1']:.3f}",
                   "95% CI": f"[{r['ci'][0]:.3f}, {r['ci'][1]:.3f}]" if r["ci"] else "",
                   "seconds per sentence": r["seconds"] if r["seconds"] else (f"{ms_sum / 1000:.2f} on CPU (scores only)" if ms_sum else ""),
                   "runs on": r["runs on"]} for r in rows], hide_index=True, width="stretch")
    st.caption("P@1 = share of sentences whose first answer is a gold technique. Ids in thesis_numbers.json: "
               + ", ".join(r["id"] for r in rows) + (", G10.ms.*" if ms_sum else "") + ". Fusion seconds = sum of the median CPU latency "
               "of its 4 models (" + ", ".join(f"{k} {v} ms" for k, v in ms.items()) + ").")

    st.markdown("#### 2. Same model, GPU vs CPU")
    left, right = st.columns(2)
    with left:
        st.markdown("**Trained models (matcher, SVM, RoBERTa, SecBERT)**")
        G = get_gpu_s42(root)
        chk = compare.parity(root)
        if G is not None:
            p1 = np.mean([R.labels[int(G[i].argmax())] in R.gold[i] for i in range(len(R.texts))])
            st.markdown(f"Seed-42 fusion from the GPU score files: test P@1 **{p1:.3f}** (build-time check, not a thesis number).")
        if chk:
            st.dataframe([{"check (live CPU vs stored GPU scores)": k, "value": v} for k, v in (
                ("sentences compared", chk["rows"]), ("matcher, largest score difference", f"{chk['matcher_max_abs_diff']:.1e}"),
                ("RoBERTa, largest z difference", f"{chk['roberta_z_max_abs_diff']:.1e}"),
                ("SecBERT, largest z difference", f"{chk['secbert_z_max_abs_diff']:.1e}"),
                ("same top-1 as notebook 06", chk["nb06_top1_agree"]), ("result", chk["status"]))], hide_index=True, width="stretch")
            st.caption("Differences are rounding noise (GPU and CPU add numbers in a different order). Section 3 repeats the check on any sentence.")
        st.caption("This PC's GTX 960 (Maxwell, 4 GB) is too old for current PyTorch CUDA, so these models run on its CPU.")
    with right:
        st.markdown(f"**Local LLM ({compare.LLM_MODEL} in Ollama)**")
        bench = compare.placement_bench(res)
        if bench:
            ref = next((b["ids"] for b in bench if b["num_gpu"] == "9"), None)
            st.dataframe([{"where": "CPU only" if b["num_gpu"] == "0" else f"{b['num_gpu']} of 29 layers on GPU" + (" (thesis run)" if b["num_gpu"] == "9" else ""),
                           "seconds per request": float(b["s_per_request"]), "GPU memory MiB": int(b["vram_mib"]),
                           "answers same as thesis run": "yes" if b["ids"] == ref else "no"} for b in bench], hide_index=True, width="stretch")
            if ref:
                ch = [sum(x != y for x, y in zip(b["ids"].split(" | "), ref.split(" | "))) for b in bench]
                n = len(ref.split(" | "))
                st.caption(f"Benchmark on {n} dev prompts (results/llm_raw/bench_placement.csv). The whole model (about 5.5 GB) does not fit in 4 GB, "
                           f"so GPU-only is impossible. More GPU layers = faster; with 12 or 14 layers {max(ch)} of {n} answers changed, "
                           "because the LLM's close calls are sensitive to rounding.")
        else:
            st.caption("bench_placement.csv not found in this folder.")

    st.markdown("#### 3. One test sentence, three answers")
    n = len(R.texts)
    i = st.number_input(f"Test sentence (1-{n})", 1, n, 1, key="cmp_row") - 1
    st.markdown(f"> {R.texts[i]}")
    gold = R.gold[i]
    st.caption("Gold: " + ", ".join(R.name(g) for g in gold))
    c_gpu, c_cpu = st.columns(2)
    with c_gpu:
        st.markdown("**GPU** (stored scores, cloud GPU)")
        if G is None:
            st.warning("GPU score files not found in this folder.")
        else:
            st.dataframe(answer_rows(R, compare.top_k(G[i], R.labels), gold), hide_index=True, width="stretch")
            st.caption("Computed once on the GPU, read here: 0 s.")
    with c_cpu:
        st.markdown("**CPU** (same models, run now on this PC)")
        if R.cal_full is None:
            st.warning("Needs the retrained matcher (results/colab/matcher_ft20_s42).")
        elif st.button("Run on this PC's CPU", key="cmp_cpu_btn"):
            import live
            try:
                comps = get_live(root, True)  # the thesis SVM, never a taught one: GPU and CPU must run the same models
                t0 = time.perf_counter()
                row = live.score_batch(comps, [R.texts[i]], live.FULL_W)[0]
                st.session_state["cmp_cpu"] = (i, row, time.perf_counter() - t0, compare.torch_gpu()[1])
            except Exception as e:
                st.error(f"CPU run failed: {type(e).__name__}: {e}")
        c = st.session_state.get("cmp_cpu")
        if c and c[0] == i:
            _, row, sec, dev = c
            st.dataframe(answer_rows(R, compare.top_k(row, R.labels), gold), hide_index=True, width="stretch")
            if G is not None:
                same = compare.top_k(row, R.labels) == compare.top_k(G[i], R.labels)
                st.caption(f"{sec:.2f} s on CPU. Top-3 {'same as' if same else 'DIFFERENT from'} GPU; largest score difference "
                           f"{float(np.abs(row - G[i]).max()):.1e}. {dev}.")
    st.markdown(f"**Local LLM** ({compare.LLM_MODEL} in Ollama on this PC)")
    c_stored, c_now = st.columns(2)
    with c_stored:
        L = compare.llm_rows(res)
        names = {v: lab for v, lab, *_ in compare.LLM_VARIANTS}
        if L:
            st.dataframe([{"thesis run (stored)": names[v], "answer": ", ".join(L[v][i]["ids"]) if i in L[v] else "",
                           "top-1 gold": ("yes" if L[v][i]["ids"] and L[v][i]["ids"][0] in gold else "no") if i in L[v] else "",
                           "seconds": L[v][i].get("seconds") if i in L[v] else None} for v in L], hide_index=True, width="stretch")
            st.caption("Seconds of the thesis run, which read the sentences one after another with the same technique list, so Ollama "
                       "could reuse the list it had already read.")
        else:
            st.caption("Stored LLM answers (results/llm_raw/*_test.jsonl) are not in this folder.")
    with c_now:
        where = st.radio("Run the LLM now on", ["CPU only (num_gpu 0)", "9 of 29 layers on the GPU (thesis run)"], key="cmp_where",
                         horizontal=True)
        ng = 0 if where.startswith("CPU") else 9
        if st.button(f"Ask {compare.LLM_MODEL} now (list of 180 techniques)", key="cmp_llm_btn"):
            if not compare.has_model(url):
                st.error(f"Ollama with {compare.LLM_MODEL} not reachable at {compare.host(url)}. Start Ollama, then retry.")
            else:
                try:
                    with st.spinner(f"Asking {compare.LLM_MODEL} ({where}); the first call or a placement change loads the model "
                                    "(CPU only: about 1 minute)..."):
                        cat = compare.catalog(R, compare.stix_names_last_wins(root))
                        a = compare.ask_llm(compare.closed_prompt(R.texts[i], cat), url, ng, set(R.labels))
                    st.session_state.setdefault("cmp_llm", {})[(i, ng)] = a
                except Exception as e:
                    st.error(f"LLM call failed: {type(e).__name__}: {e}")
        done = [(k[1], v) for k, v in st.session_state.get("cmp_llm", {}).items() if k[0] == i]
        if done:
            st.dataframe([{"run now on": "CPU only" if g == 0 else f"{g} layers on GPU", "answer": ", ".join(a["ids"]),
                           "top-1 gold": "yes" if a["ids"] and a["ids"][0] in gold else "no", "total s": round(a["wall_s"], 1),
                           "model load s": round(a["load_s"], 1), "reading prompt s": round(a["prompt_s"], 1),
                           "writing answer s": round(a["gen_s"], 1)}
                          for g, a in sorted(done)], hide_index=True, width="stretch")
            st.caption("Same prompt and settings as the thesis run (temperature 0, seed 0). Run both placements to compare. "
                       "The GPU layers mostly speed up reading the prompt; a second sentence with the same placement is faster "
                       "because Ollama reuses the technique list it has already read.")


def build_check(root):
    """live_parity.json written by check_live_parity.py at build time (portable folder: data/models)."""
    p = Path(root) / "models" / "live_parity.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def examples():
    try:
        return json.loads((APP_DIR / "examples.json").read_text(encoding="utf-8"))["examples"]
    except (OSError, ValueError, KeyError):
        return []


@st.cache_data(show_spinner=False)
def cached_explain(text, explained, name, desc, units, values, use_llm, url, note):
    return explain.explain(text, explained, name, desc, units, values, use_llm, url, note)


def shap_html(units, values):
    mx = max(abs(v) for v in values) or 1.0
    spans = []
    for u, v in zip(units, values):
        a = min(abs(v) / mx, 1) * 0.75
        col = f"rgba(214,39,40,{a:.2f})" if v > 0 else f"rgba(31,119,180,{a:.2f})"
        spans.append(f'<span title="{v:+.3f}" style="background:{col}">{html.escape(u)}</span>')  # escape: CTI text may hold markup
    return '<div class="shap" style="white-space:pre-wrap;line-height:2.1;font-size:1.05rem">' + "".join(spans) + "</div>"


def verdict(R, top, tier, margin):
    name = html.escape(R.names.get(top, ""))
    return (f'<div class="verdict" style="--tier:{TIER_COL[tier]}"><div class="tid">{html.escape(top)}</div>'
            f'<div class="tname">{name}</div><span class="chip">{TIERS[tier]} (margin {margin:.2f})</span></div>')


def render(R, text, row, cal, units, values, explained, gold, alpha, kind, use_llm, url, shap_note=""):
    """kind: "replay" (seed-averaged fusion B13a), "full" (live full fusion, seed 42) or "cls" (live classifier-only)."""
    fusion = kind == "replay"
    a = core.assess(row, cal, alpha)
    top = R.labels[int(a["order"][0])]
    left, right = st.columns([5, 6])
    with left:
        st.subheader("Predicted techniques")
        st.markdown(verdict(R, top, a["tier"], a["margin"]), unsafe_allow_html=True)
        st.markdown(home.plain_line(R, top, a["tier"]))
        if gold is not None:
            ok = top in gold
            st.caption(f"Gold: {', '.join(gold)}  |  top-1 {'matches' if ok else 'does NOT match'} gold")
        st.dataframe([{"rank": r + 1, "technique": R.name(R.labels[j]), "score": round(float(row[j]), 2), "train sentences": int(R.train_count[j])}
                      for r, j in enumerate(a["top5"])], hide_index=True, width="stretch",
                     column_config={"rank": st.column_config.NumberColumn(width="small"), "technique": st.column_config.TextColumn(width="large"),
                                    "score": st.column_config.NumberColumn(width="small"),
                                    "train sentences": st.column_config.NumberColumn("train n", help="training sentences with this label", width="small")})
        cs = [R.name(R.labels[j]) for j in a["set"]]
        if cs:
            st.markdown(f"**Conformal set (alpha {alpha}, {len(cs)} label{'s' if len(cs) != 1 else ''}):** " + "; ".join(cs))
        else:
            st.markdown(f"**Conformal set (alpha {alpha}): empty.** No technique passes the threshold; send to an analyst.")
        if fusion:
            st.caption(f"Thesis, fusion on test: coverage {R.num('CP1.fusion.score.a10.cov') if alpha == 0.10 else R.num('CP1.fusion.score.a20.cov')}, "
                       f"mean size {R.num('CP1.fusion.score.a10.size') if alpha == 0.10 else R.num('CP1.fusion.score.a20.size')}. "
                       f"Marginal guarantee only: for unseen labels coverage is {R.num('CP1.b.unseen.fusion')}.")
        else:
            st.caption(("Full-fusion (seed 42)" if kind == "full" else "Classifier-only") + " thresholds are fitted on dev here. "
                       "They have not been evaluated on test: no coverage claim.")
        st.markdown(f"**Triage: {TIERS[a['tier']]}** (top-1 minus top-2 margin {a['margin']:.2f})")
        if fusion and R.sel:
            s = R.sel[0.5 if a["tier"] == 0 else 0.9]
            if a["tier"] < 2:
                st.caption(f"Thesis: selective P@1 {s['p1']:.3f} over the {s['cov']:.1%} of test sentences at or above this margin level.")
        for lvl, msg in R.flags(top):
            (st.warning if lvl == "warn" else st.info)(msg)
        gone = R.set_drift(a["set"], top)
        if gone:
            st.warning("Also in the set but not active in the latest ATT&CK: " + "; ".join(f"{l} ({m})" for l, m in gone))
    with right:
        st.subheader("Why: SHAP words")
        if explained is None or values is None or len(values) != len(units):
            st.info("No stored SHAP for this sentence." if values is None or explained is None else "SHAP values do not line up with the words; not shown.")
            return
        st.caption(f"Explains: {R.name(explained)}. Red raises that score, blue lowers it. "
                   + (shap_note or {"replay": "RoBERTa seed 42 only (stored run, 40 permutations).", "full": "Full fusion (3,1,1,1), seed 42, live run.",
                                    "cls": "Classifier-only fusion, live run."}[kind]))
        st.markdown(shap_html(units, values), unsafe_allow_html=True)
        note = "" if explained == top else (f"Caution: the fused ranking puts {R.name(top)} first, so these words do not explain the fused answer.")
        if note:
            st.warning(note)
        with st.spinner("Writing explanation..."):
            e = cached_explain(text, explained, R.name(explained), R.desc.get(explained, ""), tuple(units), tuple(values), use_llm, url, note)
        st.subheader("Explanation")
        st.write(e["text"])
        badge = {True: "grounding check passed", False: f"grounding check FAILED, template shown ({e['reason']})", None: "LLM not used" if e["reason"] == "template" else e["reason"]}[e["grounded"]]
        st.caption(f"Source: {e['source']} | {badge}. The check only verifies that quoted words come from SHAP; no analyst study supports plausibility.")


def limits(R):
    with st.expander("What this tool does not show (numbers from thesis_numbers.json)"):
        for text, ids in core.LIMITS:
            st.markdown(f"- {text}: **" + " / ".join(R.num(i) for i in ids) + "**")
        st.markdown(
            f"- Replay ranks with the seed-averaged fusion (B13a). Its SHAP explains the full fusion of seed 42 (notebook 06) for {len(R.fshap)} test sentences, "
            "and RoBERTa seed 42 for the other sentences; the caption says which.\n"
            "- Live full fusion uses seed 42 only, with the matcher retrained on Kaggle (not bit-identical to the original matcher runs).\n"
            "- Generative explanations are a new feature with no evaluation. No claim is made that analysts find them useful.\n"
            "- Parts of this tool and its text were written with AI assistance (disclose per your thesis rules).")


# ---------------- page ----------------
st.markdown(CSS, unsafe_allow_html=True)
st.title("ATT&CK threat-report explainer")
st.session_state.setdefault("demo", core.env_flag("TTPMAP_DEMO") or not (Path(ROOT) / "Dataset").exists())
st.session_state.setdefault("mode", HOME)
mode = st.sidebar.radio("What do you want to do?", MODES, key="mode", captions=MODE_HELP, disabled=st.session_state["demo"])
adv = st.sidebar.expander("Advanced settings")
with adv:
    alpha = st.radio("Conformal alpha (risk level of the answer set)", [0.10, 0.20], format_func=lambda a: f"{a:.2f}")
    use_llm = st.toggle("Explain with local qwen2.5:7b (Ollama)", value=False)
    url = st.text_input("Ollama URL", "http://localhost:11434")
    if use_llm:
        st.caption("Ollama is running." if explain.ollama_up(url) else "Ollama not reachable: the template text will be used.")
    demo = st.toggle("Synthetic demo data", key="demo")
    root = st.text_input("Thesis folder", ROOT, disabled=demo)


def go(m):
    st.session_state["mode"] = m

try:
    R = get_replay(root, demo)
except Exception as e:
    st.error(f"Could not load the thesis folder {root!r}: {type(e).__name__}: {e}")
    st.stop()
lo_hi = R.cis.get("B13a")
p100 = home.per100(R, "B13a")
st.markdown(f'<p class="sub">Reads one sentence of a cyber-attack report and names the attacker technique (MITRE ATT&CK). '
            + (f"First answer right for {p100} of 100 new test sentences " if p100 is not None else "First answer right: see ")
            + f'(B13a = {R.num("B13a")}' + (f", 95% CI {lo_hi[0]:.3f} to {lo_hi[1]:.3f}" if lo_hi else "") + "). Runs offline on this PC.</p>",
            unsafe_allow_html=True)
if R.banner:
    st.warning(R.banner)

if demo or mode == REPLAY:
    wrong_only = st.sidebar.checkbox("Only sentences where fusion top-1 is not gold")
    rows = [i for i in range(len(R.texts)) if not wrong_only or R.labels[int(R.S[i].argmax())] not in R.gold[i]]
    if not rows:
        st.info("No sentence matches this filter.")
        st.stop()
    pos = st.sidebar.number_input(f"Sentence (1-{len(rows)})", 1, len(rows), 1) - 1
    i = rows[pos]
    text = R.texts[i]
    st.markdown(f"> {text}")
    fs = R.fshap.get(i)
    rec = fs or R.shap.get(i, {})
    note = "Full fusion SHAP (3,1,1,1), seed 42, retrained matcher, 40 permutations (notebook 06)." if fs else ""
    render(R, text, R.S[i], R.cal, ["".join(p) for p in core.split_units(text)], rec.get("values"), rec.get("label"), R.gold[i], alpha, "replay",
           use_llm, url, note)
elif mode == HOME:
    home.home_ui(R, [(m, h) for m, h in zip(MODES, MODE_HELP) if m != HOME], go)
    st.stop()
elif mode == TRAIN:
    train_ui(R, root)
elif mode == COMPARE:
    compare_ui(R, root, url)
else:
    full = mode in (LIVE, REPORT) and R.cal_full is not None  # report mode falls back to classifier-only without the matcher
    if mode == LIVE and R.cal_full is None:
        st.error("Live full fusion needs the retrained matcher (results/colab/matcher_ft20_s42 with matcher_state.pt). Use the classifier-only mode.")
        st.stop()
    import live
    taught_banner()
    with adv:
        n_perm = st.slider("Explanation detail (SHAP permutations)", 5, 40, 10)
        st.caption("40 = thesis setting. Cost is about n_perm x (2 x words + 1) model passes; fewer permutations are noisier.")
    if mode == REPORT:
        report_ui(R, root, full, n_perm, alpha, use_llm, url)
        limits(R)
        st.stop()
    chk = build_check(root) if full and "taught" not in st.session_state else None
    if chk:
        lo, hi = chk["full_s42_test_p1_ci"]
        st.sidebar.caption(f"Build-time check of this live system (seed 42, not a thesis number): test P@1 {chk['full_s42_test_p1']:.3f} "
                           f"[{lo:.3f}, {hi:.3f}]; live vs stored scores: {chk['status']}.")
    ex = examples()
    if ex:
        st.caption("Try an example (hand-written, not from the dataset):")
        for c, e in zip(st.columns(len(ex)), ex):
            if c.button(e["title"], width="stretch"):
                st.session_state["text"] = e["text"]
    text = st.text_area("Threat-report sentence", height=100, key="text")
    n_words = len(core.split_units(text))
    if chk and n_words:
        per_pass = chk["seconds_per_sentence_full_nperm10"] / (10 * (2 * chk.get("example_words", 16) + 1))
        st.caption(f"{n_words} words: about {per_pass * n_perm * (2 * n_words + 1):.0f} s on the PC that built this folder (older laptops are slower).")
    if st.button("Analyse", type="primary"):  # never disabled: a disabled button swallows the first click after typing
        if not text.strip():
            st.warning("Type or paste one threat-report sentence first, or click an example.")
        elif n_words > MAX_WORDS:
            st.warning(f"Live mode explains one sentence of up to {MAX_WORDS} words; this text has {n_words}. "
                       "Shorten it to the sentence that describes one action.")
        else:
            try:
                with st.spinner("Scoring and explaining on CPU..."):
                    st.session_state["live"] = (text, full, live.analyse(comps_for(root, full), text, n_perm, weights=live.FULL_W if full else None))
            except Exception as e:
                st.error(f"Live mode failed: {type(e).__name__}: {e}")
    if "live" in st.session_state and st.session_state["live"][1] == full:
        t, _, o = st.session_state["live"]
        hit = memory_hits(root, full, [t])[0]
        if hit:
            st.info(f"Custom-trained answer: {R.name(hit[0][0])}. This sentence is very close to your training example {hit[2] + 1} "
                    f"(similarity {hit[1]:.2f}). Below: what the four models say on their own.")
        st.caption("Latency, batch 1: " + ", ".join(f"{k} {v:.0f} ms" for k, v in o["ms"].items()) + f" | SHAP {o['shap_s']:.0f} s | additivity error {o['additivity_error']:.1e}")
        render(R, t, o["scores"], cal_live(R, full), o["units"], o["values"], R.labels[o["k"]], None, alpha, "full" if full else "cls",
               use_llm, url)
limits(R)

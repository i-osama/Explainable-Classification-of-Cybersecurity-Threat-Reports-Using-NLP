"""Process timeline reconstructed from FILE TIMESTAMPS only (modification times of result files and notebooks, as
recorded in _evidence_pack/00_hashes.csv and on disk) plus the evidence-pack / showcase build. No event is invented:
each row names the files whose timestamps define it. Writes results/process_timeline.csv."""
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import EVIDENCE, RESULTS, ROOT, SHOWCASE

h = pd.read_csv(EVIDENCE / "00_hashes.csv"); h["t"] = pd.to_datetime(h["mtime"]); h["path"] = h["path"].str.replace("\\", "/")
def span(prefix, contains=None):
    x = h[h.path.str.startswith(prefix)]
    if contains: x = x[x.path.str.contains(contains)]
    return x.t.min(), x.t.max(), len(x)
def nb(name):
    p = ROOT / "Experiments" / name; t = pd.Timestamp(p.stat().st_mtime, unit="s", tz="UTC").tz_convert("Asia/Dhaka").tz_localize(None); return t, t, 1
E = [("Data", "Dataset files obtained (TRAM dev/test, combined train, ATT&CK descriptions)", *span("Dataset/"), "Dataset/*"),
     ("Classifiers", "First TRAM classifier notebook (pilot)", *nb("Exp_0_tram.ipynb"), "Experiments/Exp_0_tram.ipynb"),
     ("Classifiers", "Head learning-rate probe", *nb("Exp_01_Tram.ipynb"), "Experiments/Exp_01_Tram.ipynb"),
     ("Classifiers", "15-epoch runs, RoBERTa and SecBERT, seeds 42-44", *span("runs_tram_1.1_epoch_15/"), "runs_tram_1.1_epoch_15/*"),
     ("Classifiers", "30-epoch runs with higher head learning rate (final classifiers)", *span("run_tram_2_epoc_30/"), "run_tram_2_epoc_30/*"),
     ("Matcher", "Zero-shot and first fine-tuned matcher, 20-epoch seed 42", *span("run_match_1/", "zeroshot|ft_s42|ft20_s42"), "run_match_1/{zeroshot,ft_s42,ft20_s42}"),
     ("Matcher", "Matcher seeds 43 and 44", *span("run_match_1/", "ft20_s43|ft20_s44"), "run_match_1/ft20_s43, ft20_s44"),
     ("Fusion", "Fusion weights and final results table", *span("run_match_1/final_results_table"), "run_match_1/final_results_table.csv"),
     ("Matcher", "256-token description ablation and label-rarity chart", *span("run_match_1/", "L256|label_rarity"), "run_match_1/ft20L256_*, label_rarity.png"),
     ("Classifiers", "Classifier runs re-saved with checkpoints (pw / nopw, seeds 42-44)", *span("Exp_1_4_run_tram_2_epoc_30/"), "Exp_1_4_run_tram_2_epoc_30/*"),
     ("Explainability", "SHAP pilots (token-level, then word-level with 10 permutations)", *span("Exp_3_0_shap/", "shap_roberta|shap_v1"), "Exp_3_0_shap/shap_roberta_pw_s42.jsonl, shap_v1_*"),
     ("Explainability", "Deletion test on the 100-sentence sample", *span("Exp_3_0_shap/", "deletion_test"), "Exp_3_0_shap/deletion_test_v2_roberta_pw_s42.csv"),
     ("Human study", "Rating sheets filled and agreement computed", *span("Exp_3_0_shap/", "hand_check|rater_agreement"), "Exp_3_0_shap/ rating sheets (by role), rater_agreement_v2_*.csv"),
     ("Explainability", "Word-level SHAP for all test sentences (40 permutations)", *span("Exp_3_0_shap/", "shap_v2"), "Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl")]
def mt(p): return pd.Timestamp(p.stat().st_mtime, unit="s", tz="UTC").tz_convert("Asia/Dhaka").tz_localize(None)
ev = [p for p in EVIDENCE.glob("*.md")] + [p for p in EVIDENCE.glob("*.csv")]
E.append(("Audit", "Evidence pack: every claim recomputed from saved predictions", min(map(mt, ev)), max(map(mt, ev)), len(ev), "_evidence_pack/*.md, *.csv"))
sc = [p for p in (SHOWCASE / "results").glob("*.csv")] + [SHOWCASE / "thesis_numbers.json"]
E.append(("Showcase", "Showcase: package, tests, pre-registered analyses, truth file", min(map(mt, sc)), max(map(mt, sc)), len(sc), "_showcase/results/*.csv, thesis_numbers.json"))
d = pd.DataFrame(E, columns=["track", "event", "first_timestamp", "last_timestamp", "n_files", "evidence_files"]).sort_values("first_timestamp")
d["basis"] = "reconstructed from file timestamps"
d.to_csv(RESULTS / "process_timeline.csv", index=False)
print(d[["first_timestamp", "track", "event"]].to_string(index=False)[:2600])

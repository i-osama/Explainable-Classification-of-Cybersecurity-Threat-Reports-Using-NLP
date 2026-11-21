"""Q1 plan Task 5: de-duplication of the sibling sources against TRAM dev/test (prereg 16)."""
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import DATA
from ttpmap.data import dedup_against, norm_text


def test_dedup_against_exact_and_near():
    ref = ["The actor ran PowerShell to download the second stage payload from the server."]
    df = pd.DataFrame({"text": ["the actor ran   powershell to download the second stage payload from the server.",
                                "The actor ran PowerShell to download the second stage payload from the server today.",
                                "Different text about credential dumping."]})
    kept, n = dedup_against(df, ref)
    assert kept["text"].tolist() == ["Different text about credential dumping."]
    assert n == {"exact": 1, "near": 1}


def test_dedup_against_without_near():
    kept, n = dedup_against(pd.DataFrame({"text": ["a b c d e f g h i j k", "x"]}), ["a b c d e f g h i j"], near=False)
    assert len(kept) == 2 and n == {"exact": 0, "near": 0}


def test_siblings_have_no_test_overlap_after_dedup():
    f = DATA / "combined_train.csv"
    if not f.exists():
        return "SKIP"
    from ttpmap.data import load_split
    sib = pd.read_csv(f).rename(columns={"text1": "text"}); sib = sib[sib.source_dataset != "tram"]
    ref = pd.concat([load_split("dev"), load_split("test")])["text"].tolist()
    kept, _ = dedup_against(sib, ref)
    assert not (set(kept["text"].map(norm_text)) & set(map(norm_text, ref)))

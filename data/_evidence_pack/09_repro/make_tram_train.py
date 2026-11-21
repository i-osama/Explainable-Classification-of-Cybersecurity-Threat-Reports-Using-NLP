"""Rebuild tram_train.tsv from Dataset/combined_train.csv (rows with source_dataset == 'tram').
The file is NOT shipped in the pack because no license text for the TRAM data exists in the project folder.
    python make_tram_train.py  [output path, default: ./tram_train.tsv]
Check: 3,468 rows, 180 distinct labels, SVM P@1 on tram_test.tsv = 0.742 (see smoke_test.py)."""
import sys
from pathlib import Path
import pandas as pd
src = Path(r"E:\Osamas Paper\Dataset\combined_train.csv")
out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "tram_train.tsv"
df = pd.read_csv(src)
t = df[df["source_dataset"] == "tram"][["text1", "labels"]]
assert len(t) == 3468
t.to_csv(out, sep="\t", index=False)
print("wrote", out, len(t), "rows")

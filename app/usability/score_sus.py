"""Score System Usability Scale (SUS) answers (Brooke 1996).

    python usability/score_sus.py usability/sus_responses.csv

CSV columns: participant, q1 ... q10, each answer 1 (strongly disagree) to 5 (strongly agree).
Odd items count (answer - 1), even items count (5 - answer); the sum x 2.5 gives 0-100 per participant.
With 3-5 participants report the scores and the mean as DESCRIPTIVE only (no test, no confidence claim).
"""
import csv
import statistics
import sys


def sus(answers):
    a = list(answers)
    if len(a) != 10 or any(not isinstance(x, int) or not 1 <= x <= 5 for x in a):
        raise ValueError(f"SUS needs 10 answers from 1 to 5, got {a}")
    return 2.5 * sum((x - 1) if i % 2 == 0 else (5 - x) for i, x in enumerate(a))


def score_file(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            ans = [int(r[f"q{i}"]) if str(r[f"q{i}"]).strip() else None for i in range(1, 11)]
            rows.append({"participant": r["participant"], "sus": sus(ans)})
    s = [r["sus"] for r in rows]
    summary = {"n": len(s), "mean": round(statistics.mean(s), 2), "sd": round(statistics.stdev(s), 2) if len(s) > 1 else None,
               "min": min(s), "max": max(s)}
    return rows, summary


if __name__ == "__main__":
    rows, summary = score_file(sys.argv[1] if len(sys.argv) > 1 else "usability/sus_responses.csv")
    for r in rows:
        print(f"{r['participant']}: {r['sus']:.1f}")
    print(summary)

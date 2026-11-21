"""Real-data check of "Train and check" with the ready-made example (examples_teach.json). Not a thesis number.

Before/after on the example's test sentences, and P@1 on the 604 thesis dev sentences (with and without the example
memory), with the real models on CPU. Writes _build/train_check_verification.json.

    python check_train.py          (TTPMAP_ROOT = thesis folder or the portable data folder)
"""
import json
import os
import time
from pathlib import Path

import core
import live
import teach


def main():
    root = os.environ.get("TTPMAP_ROOT", r"E:\Osamas Paper")
    R = core.load_replay(root)
    ex = json.loads((Path(__file__).parent / "examples_teach.json").read_text(encoding="utf-8"))
    rows, e1 = core.parse_labelled("\n".join(ex["train"]), R.labels)
    check, e2 = core.parse_labelled("\n".join(ex["check"]), R.labels)
    assert not e1 and not e2, e1 + e2
    t0 = time.perf_counter()
    comps0 = live.load(R.art, full=True)
    tm = teach.load_t(root)
    art2 = core.retrain_svm(R.art, rows)
    comps1 = [live.SvmComp(art2) if c.name == "svm" else c for c in comps0]
    mem = teach.build_memory(comps0, rows, tm)
    w = live.FULL_W
    ck = [s for s, _ in check]
    before, svm_only, after = (teach.predict(comps0, R.labels, ck, None, w), teach.predict(comps1, R.labels, ck, None, w),
                               teach.predict(comps1, R.labels, ck, mem, w))
    tr = teach.check_report(teach.predict(comps0, R.labels, [s for s, _ in rows], None, w),
                            teach.predict(comps1, R.labels, [s for s, _ in rows], mem, w), [i for _, i in rows])
    E_dev = teach.matcher_emb(comps0, R.art["dev"]["texts"])
    dev = {"before": teach.dev_p1(R, R.art, None, E_dev), "svm_only": teach.dev_p1(R, art2, None, E_dev),
           "after": teach.dev_p1(R, art2, mem, E_dev), "memory_fired_on_dev": sum(h is not None for h in mem.lookup(E_dev))}
    tech = rows[0][1][0]
    out = {"technique": tech, "train_support_in_thesis": int(R.train_count[R.labels.index(tech)]), "t": tm,
           "check": teach.check_report(before, after, [i for _, i in check]),
           "check_svm_only_right": sum(a["top"] in i for a, (_, i) in zip(svm_only, check)),
           "train": tr, "dev": dev, "verdict": teach.verdict(tr, teach.check_report(before, after, [i for _, i in check]), dev["before"], dev["after"]),
           "rows": [{"sentence": s, "before": b["top"], "svm_only": v["top"], "after": a["top"], "source": a["source"], "sim": a["sim"]}
                    for (s, _), b, v, a in zip(check, before, svm_only, after)],
           "seconds": round(time.perf_counter() - t0, 1), "note": "build-time check of the demo feature; not a thesis number"}
    p = Path(__file__).parent / "_build" / "train_check_verification.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0 if out["verdict"][0] else 1


if __name__ == "__main__":
    raise SystemExit(main())

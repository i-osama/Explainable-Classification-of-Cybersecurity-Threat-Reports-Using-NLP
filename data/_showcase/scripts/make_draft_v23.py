"""Prompt E2: _showcase/Thesis_Draft_v2.3.docx = Thesis_Draft_v2.2.docx with the 13 stale confidence intervals (1,000-resample values)
replaced by the 10,000-resample values of thesis_numbers.json. Only digits change (each new string has the old length); every other
byte of the .docx is copied unchanged. The v2.2 file is only read. Writes _showcase/CHANGELOG_v2.3.md and checks the result:
the paragraph texts of v2.2 and v2.3 differ in exactly these 13 places.
Usage: python scripts/make_draft_v23.py"""
import html, json, re, sys, zipfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

SHOW = Path(__file__).resolve().parents[1]; ROOT = SHOW.parent
SRC, DST = ROOT / "Thesis_Draft_v2.2.docx", SHOW / "Thesis_Draft_v2.3.docx"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_numbers as A

CL = {c["id"]: c for c in json.loads((SHOW / "thesis_numbers.json").read_text(encoding="utf-8"))["claims"]}
# (paragraph index in audit_numbers.load_paragraphs order, old text, claim id); the table cells 686-692 sit under the row labels shown in CHANGELOG
FIX = [(192, "−0.015 to +0.040", "C3"), (676, "0.003 to 0.037", "C2.mrr"), (676, "−0.015 to +0.040", "C3"), (676, "−0.018 to +0.020", "C3.mrr"),
       (676, "−0.022 to +0.025", "C4"), (676, "−0.015 to +0.020", "C4.mrr"), (686, "[+0.003, +0.037]", "C2.mrr"), (688, "[−0.015, +0.040]", "C3"),
       (689, "[−0.018, +0.020]", "C3.mrr"), (691, "[−0.022, +0.025]", "C4"), (692, "[−0.015, +0.020]", "C4.mrr"), (790, "−0.015 to +0.040", "C3"),
       (798, "[−0.015, +0.040]", "C3"),
       # point estimate, not an interval: RoBERTa minus SecBERT delta MRR@3 is 0.0016 (+0.002), the draft has +0.003 (same stale 1,000-resample source)
       (676, "+0.003 (−0.016", "point:C4.mrr"), (692, "+0.003 [−0.016", "point:C4.mrr")]
TOK = re.compile(r"[+\-−]?\d+\.\d+")


def fmt(x, like):
    """x at the precision and sign style of the draft token `like` (Unicode minus, explicit plus), rounded half up."""
    d = len(like.split(".")[1]); q = Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    s = f"{abs(q):.{d}f}"
    if q < 0: return ("−" if "−" in like or "-" not in like else "-") + s
    return ("+" + s) if like.startswith("+") else s


def cid_of(c): return c.split(":", 1)[-1]


def new_text(old, cid):
    if cid.startswith("point:"):                       # only the first number (the point estimate) changes
        t = TOK.findall(old)[0]; out = old.replace(t, fmt(CL[cid_of(cid)]["value"], t), 1); assert len(out) == len(old); return out
    lo, hi = CL[cid]["ci"]; toks = TOK.findall(old); assert len(toks) == 2, old
    out = old.replace(toks[0], fmt(lo, toks[0]), 1)
    i = out.rfind(toks[1]); out = out[:i] + fmt(hi, toks[1]) + out[i + len(toks[1]):]
    assert len(out) == len(old), (old, out)
    return out


def main():
    xml = zipfile.ZipFile(SRC).read("word/document.xml").decode("utf-8")
    # outer paragraphs in document order (= audit_numbers.walk order) and the w:t text segments inside each
    paras, depth, cur = [], 0, None
    for m in re.finditer(r"<w:p(?:\s[^>]*)?/>|<w:p(?:\s[^>]*)?>|</w:p>|<w:t(?:\s[^>]*)?>([^<]*)</w:t>", xml):
        g = m.group(0)
        if g.startswith("<w:p") and g.endswith("/>"):
            if depth == 0: paras.append([])
        elif g.startswith("<w:p"):
            if depth == 0: cur = []; paras.append(cur)
            depth += 1
        elif g == "</w:p>":
            depth -= 1
        elif depth > 0:
            cur.append((m.start(1), m.end(1), html.unescape(m.group(1))))
    P = A.load_paragraphs(SRC)
    assert len(paras) == len(P), (len(paras), len(P))
    edits, log, expect = {}, [], {}
    for idx, old, cid in FIX:
        segs = paras[idx]; text = "".join(s[2] for s in segs); expect.setdefault(idx, P[idx]["text"])
        assert text == expect[idx], f"paragraph {idx}: raw text differs from audit_numbers text"
        assert text.count(old) == 1, f"paragraph {idx}: {old!r} found {text.count(old)} times"
        new = new_text(old, cid); k = text.index(old); expect[idx] = text.replace(old, new)
        pos = 0; per = {}
        for si, (a, b, t) in enumerate(segs):
            for j in range(len(t)):
                g_ = pos + j
                if k <= g_ < k + len(old) and old[g_ - k] != new[g_ - k]: per.setdefault(si, {})[j] = new[g_ - k]
            pos += len(t)
        for si, ch in per.items():
            a, b, t = segs[si]; t2 = "".join(ch.get(j, c) for j, c in enumerate(t))
            edits[(a, b)] = html.escape(t2, quote=False)          # one entry per text node: the latest text wins
            segs[si] = (a, b, t2)
        head = next((P[i]["text"] for i in range(idx, -1, -1) if P[i]["style"].startswith("Heading")), "")
        row = next((P[i]["text"] for i in range(idx - 1, idx - 4, -1) if P[i]["in_table"] and not TOK.search(P[i]["text"])), "") if P[idx]["in_table"] else ""
        log.append((idx, head, row, text[max(0, k - 60): k + len(old) + 20], old, new, cid))
    for (a, b), t in sorted(edits.items(), reverse=True):
        xml = xml[:a] + t + xml[b:]
    with zipfile.ZipFile(SRC) as zi, zipfile.ZipFile(DST, "w") as zo:
        for info in zi.infolist():
            zo.writestr(info, xml.encode("utf-8") if info.filename == "word/document.xml" else zi.read(info.filename))
    # verify: only the 13 places changed
    P2 = A.load_paragraphs(DST); assert len(P2) == len(P)
    changed = [(i, sum(a != b for a, b in zip(p["text"], q["text"]))) for i, (p, q) in enumerate(zip(P, P2)) if p["text"] != q["text"]]
    assert all(len(p["text"]) == len(q["text"]) for p, q in zip(P, P2))
    want = {}
    for idx, old, cid in FIX: want[idx] = want.get(idx, 0) + sum(a != b for a, b in zip(old, new_text(old, cid)))
    assert dict(changed) == want, (changed, want)
    for idx, old, cid in FIX: assert new_text(old, cid) in P2[idx]["text"]
    L = ["# CHANGELOG v2.3", "", f"`Thesis_Draft_v2.3.docx` = `Thesis_Draft_v2.2.docx` with {sum(not c.startswith('point:') for _, _, c in FIX)} confidence intervals changed from the old 1,000-resample values to the "
         "10,000-resample values in `thesis_numbers.json` (paired percentile bootstrap, seed 20261114). Only digits changed; no prose, layout or other number was touched. "
         "Rows marked `point:` correct a point estimate that came from the same stale source (registry value 0.0016 shown as +0.002). "
         "Generated and checked by `scripts/make_draft_v23.py` (the paragraph texts of v2.2 and v2.3 differ in exactly these places).", "",
         "| # | para | section | table row | context (v2.2) | old | new | claim id | claim |", "|---|---|---|---|---|---|---|---|---|"]
    for n, (idx, head, row, ctx, old, new, cid) in enumerate(log, 1):
        L.append(f"| {n} | {idx} | {head[:50]} | {row[:40]} | …{ctx.replace('|', '/')}… | {old} | {new} | `{cid}` | {CL[cid_of(cid)]['label']} |")
    L += ["", f"Characters changed per paragraph: {dict(changed)}. Paragraph numbers follow `scripts/audit_numbers.py` (body order, table cells included)."]
    (SHOW / "CHANGELOG_v2.3.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{DST.name}: {len(FIX)} number strings changed in {len(changed)} paragraphs; CHANGELOG_v2.3.md written")


if __name__ == "__main__":
    main()

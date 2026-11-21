#!/usr/bin/env python3
"""
Number audit for the thesis .docx.

What it does
  1. Reads word/document.xml of the .docx (real Word fields and tables included).
  2. Splits the document into regions: front matter, body (Chapter 1 up to the
     References heading), references, appendices.
  3. Extracts every number in the text (equations are skipped), ignoring
     citation brackets [12], cross-references (Table 3.1, Section 5.2 ...),
     and years.
  4. Checks each number against a registry (thesis_numbers.json, any nesting)
     with rounding-aware matching: 0.796 matches 0.7963 or 0.796.
  5. Lists yellow-highlighted placeholders and word counts.

Outputs (in --out): audit_ledger.csv, placeholders.csv, audit_report.md, words.json
Exit status: 1 if any strict number (decimal, percent, integer >= 10) is neither
registered nor allowed, else 0.  Use --no-fail to always exit 0.

Usage
  python3 audit_numbers.py Thesis.docx --registry thesis_numbers.json --out audit/
  python3 audit_numbers.py Thesis.docx --out audit/          # ledger only
"""
import argparse, csv, json, re, sys, zipfile, collections
from decimal import Decimal
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

# ----------------------------------------------------------------- reading
def walk(el, in_table=False):
    for ch in el:
        if ch.tag == W + 'tbl':
            yield from walk(ch, True)
        elif ch.tag == W + 'p':
            yield ch, in_table
        else:
            yield from walk(ch, in_table)

def load_paragraphs(path):
    z = zipfile.ZipFile(path)
    root = ET.fromstring(z.read('word/document.xml'))
    body = root.find(W + 'body')
    out = []
    for i, (p, in_table) in enumerate(walk(body)):
        ps = p.find(W + 'pPr/' + W + 'pStyle')
        style = ps.get(W + 'val') if ps is not None else ''
        segs = []   # (text, highlighted)
        field_instr = ''
        for r in p.iter(W + 'r'):
            hl = r.find(W + 'rPr/' + W + 'highlight') is not None
            txt = ''.join(t.text or '' for t in r.findall(W + 't'))
            instr = ''.join(t.text or '' for t in r.findall(W + 'instrText'))
            field_instr += instr
            if txt:
                segs.append((txt, hl))
        out.append(dict(idx=i, style=style, in_table=in_table,
                        text=''.join(s for s, _ in segs), segs=segs,
                        field=field_instr))
    return out

def assign_regions(paras):
    region, seen_body = 'front', False
    for p in paras:
        if p['style'] == 'Heading1' and not seen_body:
            seen_body = True
            region = 'body'
        elif p['style'] == 'ReferenceHead':
            region = 'refs'
        elif p['style'] == 'AppendixHead' and region in ('refs', 'body'):
            region = 'appendix'
        p['region'] = region
    return paras

# ----------------------------------------------------------------- numbers
XREF = re.compile(r'\b(?:Tables?|Figures?|Fig\.|Sections?|Chapters?|Eq\.|Equations?|Appendix|Appendices)\s*\(?[A-Z\d][\d.]*[A-Za-z]?\)?')
CITE = re.compile(r'\[\d+(?:\s*[,–-]\s*\d+)*\]')
NUM = re.compile(r'(?<![\w.])(?:[+\-−–]\s?)?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?')

def clean_for_numbers(text):
    t = CITE.sub(' ', text)
    t = XREF.sub(' ', t)
    return t

def parse_token(tok):
    t = tok.replace(',', '').replace('−', '-').replace('–', '-').replace(' ', '')
    pct = t.endswith('%')
    t = t.rstrip('%').lstrip('+-')
    dec = '.' in t
    d = len(t.split('.')[1]) if dec else 0
    return Decimal(t), pct, dec, d

def kind_of(val, pct, dec):
    if pct: return 'percent'
    if dec: return 'decimal'
    if 1900 <= val <= 2100: return 'year'
    if val >= 10: return 'int>=10'
    return 'int<10'

def flatten(obj, acc):
    if isinstance(obj, bool): return
    if isinstance(obj, (int, float)): acc.append(Decimal(str(obj)))
    elif isinstance(obj, str):
        for m in NUM.finditer(obj):
            try: acc.append(parse_token(m.group())[0])
            except Exception: pass
    elif isinstance(obj, dict):
        for v in obj.values(): flatten(v, acc)
    elif isinstance(obj, (list, tuple)):
        for v in obj: flatten(v, acc)

def matches(val, pct, dec, d, registry):
    """Rounding-aware: a token with d decimals matches r if |r-val| <= 0.5*10^-d."""
    tol = Decimal('0.5') * (Decimal(10) ** -d) + Decimal('1e-12')
    cands = [val]
    if pct: cands.append(val / 100)           # 72.5% may be stored as 0.725
    for c in cands:
        dd = d + (2 if (pct and c != val) else 0)
        t = Decimal('0.5') * (Decimal(10) ** -dd) + Decimal('1e-12')
        for r in registry:
            if abs(abs(r) - c) <= t:
                return True
    return False

DEFAULT_ALLOW = {  # settings stated in the methods; edit freely
    '128', '16', '20', '30', '42', '43', '44', '64', '5', '40', '3', '12', '14',
}

def audit(paras, registry, allow):
    ledger = collections.OrderedDict()
    for p in paras:
        if p['region'] == 'refs' or p['field'].strip().startswith(('TOC', 'PAGEREF', 'SEQ', 'STYLEREF')):
            continue
        if p['style'].startswith(('TOC', 'TableofFigures')):
            continue
        text = p['text']
        placeholder_spans = [s for s, h in p['segs'] if h]
        t = clean_for_numbers(text)
        for m in NUM.finditer(t):
            tok = m.group().strip()
            try:
                val, pct, dec, d = parse_token(tok)
            except Exception:
                continue
            k = kind_of(val, pct, dec)
            if k in ('year', 'int<10'):
                status = 'ignored'
            elif tok.lstrip('+-−– ').rstrip('%') in allow or str(val) in allow:
                status = 'allowed'
            elif registry and matches(val, pct, dec, d, registry):
                status = 'registered'
            else:
                status = 'UNREGISTERED' if registry else 'ledger'
            in_ph = any(tok.strip('+-−–%') in s for s in placeholder_spans)
            if in_ph and status == 'UNREGISTERED':
                status = 'placeholder'
            key = (tok.replace(' ', ''), p['idx'])
            s = max(0, m.start() - 45); e = min(len(t), m.end() + 45)
            ledger[key] = dict(token=tok.replace(' ', ''), kind=k, status=status,
                               region=p['region'], para=p['idx'],
                               table='yes' if p['in_table'] else '',
                               context=t[s:e].replace('\n', ' '))
    return list(ledger.values())

# ----------------------------------------------------------------- words
def word_counts(paras):
    wc = lambda s: len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-./%±]*", s))
    out = collections.Counter()
    for p in paras:
        if p['field'].strip().startswith(('TOC', 'PAGEREF')) or p['style'].startswith(('TOC', 'TableofFigures')):
            continue
        n = wc(p['text'])
        r = p['region']
        if r == 'body':
            if p['style'] == 'Caption': out['body_captions'] += n
            elif p['in_table']: out['body_tables'] += n
            elif p['style'].startswith('Heading'): out['body_headings'] += n
            else: out['body_paragraph_text'] += n
        else:
            out[r] += n
    out['body_text_only'] = out['body_paragraph_text']
    out['body_text_plus_headings'] = out['body_paragraph_text'] + out['body_headings']
    out['body_all_incl_tables_captions'] = (out['body_paragraph_text'] + out['body_headings'] +
                                            out['body_tables'] + out['body_captions'])
    return dict(out)

# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('docx'); ap.add_argument('--registry'); ap.add_argument('--out', default='audit')
    ap.add_argument('--allow', help='file with one allowed token per line')
    ap.add_argument('--no-fail', action='store_true')
    a = ap.parse_args()
    import os; os.makedirs(a.out, exist_ok=True)

    paras = assign_regions(load_paragraphs(a.docx))
    registry = []
    if a.registry:
        flatten(json.load(open(a.registry, encoding='utf-8')), registry)
        registry = sorted(set(registry))
    allow = set(DEFAULT_ALLOW)
    if a.allow: allow |= {l.strip() for l in open(a.allow) if l.strip()}

    ledger = audit(paras, registry, allow)
    with open(f'{a.out}/audit_ledger.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['token', 'kind', 'status', 'region', 'para', 'table', 'context'])
        w.writeheader(); w.writerows(ledger)

    ph = []
    for p in paras:
        for s, h in p['segs']:
            if h: ph.append(dict(para=p['idx'], region=p['region'], placeholder=s.strip()))
    with open(f'{a.out}/placeholders.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['para', 'region', 'placeholder']); w.writeheader(); w.writerows(ph)

    wc = word_counts(paras)
    json.dump(wc, open(f'{a.out}/words.json', 'w'), indent=1)

    by = collections.Counter((r['status'], r['kind']) for r in ledger)
    bad = [r for r in ledger if r['status'] == 'UNREGISTERED']
    lines = [f'# Number audit: {a.docx}', '',
             f'- registry numbers loaded: {len(registry)}',
             f'- numbers checked: {len(ledger)}',
             f'- placeholders (highlighted runs): {len(ph)} in {len({x["para"] for x in ph})} paragraphs',
             f'- words: {json.dumps(wc)}', '', '## Status by kind', '']
    for (s, k), n in sorted(by.items()): lines.append(f'- {s} / {k}: {n}')
    if bad:
        lines += ['', '## UNREGISTERED (not in registry, not allowed)', '']
        for r in bad:
            lines.append(f'- [{r["region"]} p{r["para"]}{" table" if r["table"] else ""}] `{r["token"]}` ...{r["context"]}...')
    open(f'{a.out}/audit_report.md', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:12]))
    if bad: print(f'\n{len(bad)} UNREGISTERED numbers; see {a.out}/audit_report.md')
    sys.exit(1 if (bad and not a.no_fail) else 0)

if __name__ == '__main__':
    main()

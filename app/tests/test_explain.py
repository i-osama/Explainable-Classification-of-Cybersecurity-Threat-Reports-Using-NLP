import explain

UNITS = ["the ", "attacker ", "dumped ", "lsass ", "memory ", "with ", "procdump."]
VALS = [0.0, 0.2, 1.5, 2.0, 0.8, -0.3, 1.1]
ALLOWED = [w for w, _ in explain.top_words(UNITS, VALS)]


def test_top_words_positive_only_sorted():
    assert ALLOWED == ["lsass", "dumped", "procdump.", "memory", "attacker"]
    assert explain.top_words(["a ", "b"], [-1, -2]) == []


def test_grounded_pass_and_fail_cases():
    ok = lambda t: explain.grounded(t, ALLOWED, "T1003")[0]
    assert ok('It keys on "lsass" and "dumped" for T1003.')
    assert ok("It keys on “procdump”.")                       # curly quotes, edge punctuation stripped
    assert not ok("No quotes here.")
    assert not ok('It keys on "lsass" and "powershell".')              # word not in SHAP top-k
    assert not ok('It keys on "lsass" and matches T1059.')             # wrong technique id
    assert not ok('It keys on "the".')                                  # zero-attribution word is not allowed


def test_explain_template_llm_and_fallbacks():
    args = ("txt", "T1003", "T1003 Dump", "desc", UNITS, VALS)
    t = explain.explain(*args)
    assert t["source"] == "template" and '"lsass"' in t["text"]
    good = explain.explain(*args, use_llm=True, ask=lambda p, url: 'Mentions "lsass" and "dumped".')
    assert good["grounded"] is True and good["source"] == explain.MODEL
    bad = explain.explain(*args, use_llm=True, ask=lambda p, url: 'It is about "ransomware".')
    assert bad["grounded"] is False and bad["source"] == "template" and "rejected" in bad
    def boom(p, url): raise TimeoutError()
    down = explain.explain(*args, use_llm=True, ask=boom)
    assert down["source"] == "template" and "unavailable" in down["reason"]


def test_prompt_only_offers_shap_words():
    p = explain.prompt("txt", "T1003", "T1003 Dump", "desc", explain.top_words(UNITS, VALS))
    assert "lsass" in p and "the," not in p and "Do not mention any technique id other than T1003" in p

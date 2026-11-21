"""Start page and plain-language text, for visitors without an AI or security background.

Numbers come from thesis_numbers.json through R.num(); nothing here is typed by hand.
"""
from __future__ import annotations

import re

import streamlit as st

TIER_WORDS = ("It is very sure.", "It is fairly sure.", "It is not sure: a person should check this one.")

GLOSSARY = {
    "Threat report": "A text written by security analysts about an attack: what the attackers did, step by step.",
    "MITRE ATT&CK": "A free public catalogue of attacker behaviour. Each behaviour has a code, like T1082.",
    "Technique": "One attacker behaviour in that catalogue, for example T1082 System Information Discovery: collecting details about a computer.",
    "First answer right (P@1)": "How often the tool's first answer is one of the correct techniques, on sentences it never saw while learning.",
    "Confidence": "How far the first answer is ahead of the second. Far ahead: very sure. Close: a person should check.",
    "Coloured words": "Red words pushed the answer up, blue words pushed it down. This is called SHAP.",
    "Fusion": "Four models vote. The matcher's vote counts three times, the other three count once each.",
    "Matcher": "A model that compares the sentence with the official description of every technique and picks the closest.",
    "GPU and CPU": "Two kinds of computer chips. A GPU is faster for AI, a CPU is in every laptop. Both give the same answer here.",
    "Local AI (LLM)": "A general chatbot-style model running on this laptop (qwen2.5:7b). It was not trained for this task.",
    "Training": "Showing the tool new labelled examples so it can recognise similar sentences next time.",
}


def first_sentence(desc: str, max_chars: int = 220) -> str:
    """First sentence of an ATT&CK description, without markdown links or code marks."""
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", str(desc or "")).replace("`", "").strip()
    m = re.search(r"(?<=[a-z0-9\)])\.\s", s)
    s = s[: m.start() + 1] if m else s
    return s if len(s) <= max_chars else s[: max_chars].rsplit(" ", 1)[0] + "..."


def plain_line(R, top: str, tier: int) -> str:
    """One sentence a non-specialist can read under the answer box."""
    what = first_sentence(R.desc.get(top, ""))
    what = what[0].lower() + what[1:] if what else ""
    return f"The tool thinks this sentence describes **{R.name(top)}**" + (f": {what}" if what else ".") + f" {TIER_WORDS[tier]}"


def per100(R, id_):
    try:
        return round(float(str(R.num(id_)).split()[0]) * 100)
    except ValueError:
        return None


def home_ui(R, modes, go) -> None:
    """modes: [(mode name, one-line help)] of the other pages; go(mode) switches to that page."""
    st.subheader("What is this?")
    st.markdown("A research prototype from a thesis project. It reads **one sentence from a cyber-attack report** and names "
                "the attacker behaviour it describes, using the public **MITRE ATT&CK** catalogue. It also shows **which words** "
                "led to the answer and **how sure** it is. It suggests; a security analyst decides.")
    fus, llm = per100(R, "B13a"), per100(R, "L1.closed.p1")
    c1, c2, c3 = st.columns(3)
    with c1.container(border=True):
        st.markdown("**The problem**\n\nSecurity teams read long attack reports. They tag each attacker action with an ATT&CK "
                    "code by hand. That is slow and needs experts.")
    with c2.container(border=True):
        st.markdown("**What the tool does**\n\nYou paste a sentence. It answers with the technique code and name, colours the "
                    "words that mattered, and gives a confidence level.")
    with c3.container(border=True):
        st.markdown("**How good it is**\n\n" + (f"On 725 test sentences it never saw while learning, its first answer was right "
                    f"**{fus} of 100** times." if fus is not None else "Its accuracy is in the thesis registry.")
                    + (f" A general AI chatbot on this laptop got **{llm} of 100**." if llm is not None else ""))
    st.markdown("#### How it works, in three steps")
    s1, s2, s3 = st.columns(3)
    s1.markdown("**1. Read.** Four different models read the sentence: a keyword model, two language models trained on "
                "threat-report sentences, and a matcher that compares the sentence with each technique's official description.")
    s2.markdown("**2. Vote.** Their scores are added up. The matcher's vote counts three times: this mix scored best on the "
                "development sentences, before the final test.")
    s3.markdown("**3. Explain.** Red words pushed the answer up, blue words pushed it down. A confidence level says when a "
                "person should check.")
    st.markdown("#### What you can do here")
    cols = st.columns(3)
    for i, (m, help_) in enumerate(modes):
        with cols[i % 3].container(border=True):
            st.button(m, key=f"go_{i}", on_click=go, args=(m,), width="stretch")
            st.caption(help_)
    with st.expander("Words used on these pages"):
        for k, v in GLOSSARY.items():
            st.markdown(f"**{k}.** {v}")

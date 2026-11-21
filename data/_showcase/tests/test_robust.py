"""Q1 plan Task 3: perturbations for the robustness and shortcut test (prereg 14)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ttpmap import robust

STIX = [
    {"type": "attack-pattern", "name": "PowerShell"},
    {"type": "attack-pattern", "name": "Ingress Tool Transfer"},
    {"type": "tool", "name": "PowerShell", "x_mitre_aliases": ["PowerShell"]},
    {"type": "malware", "name": "Emotet", "x_mitre_aliases": ["Emotet", "Geodo"]},
    {"type": "tool", "name": "Net"},
    {"type": "intrusion-set", "name": "APT29", "aliases": ["APT29", "Cozy Bear"]},
    {"type": "intrusion-set", "name": "OldGroup", "revoked": True},
]


def test_mask_entities_word_boundary():
    out = robust.mask_entities("Emotet and APT29 used x; Emotetx stays", ["Emotet", "APT29"])
    assert out == "[ENT] and [ENT] used x; Emotetx stays"


def test_mask_entities_longest_first_and_case_sensitive():
    assert robust.mask_entities("Cozy Bear and cozy bear", ["Cozy", "Cozy Bear"]) == "[ENT] and cozy bear"


def test_load_entity_names_groups_and_software():
    groups = robust.load_entity_names(STIX, ("intrusion-set",))
    assert set(groups) == {"APT29", "Cozy Bear"}                      # revoked group dropped
    soft = robust.load_entity_names(STIX, ("malware", "tool"))
    assert set(soft) == {"Emotet", "Geodo"}


def test_technique_names_never_masked():
    soft = robust.load_entity_names(STIX, ("malware", "tool"))
    assert "PowerShell" not in soft and "Net" not in soft            # in a technique name / shorter than 4 characters


def test_mask_iocs():
    s = "connects to 10.0.0.1 and evil.com, drops C:\\x\\a.exe, hash d41d8cd98f00b204e9800998ecf8427e"
    out = robust.mask_iocs(s)
    assert out.count("[IOC]") == 4 and out.startswith("connects to [IOC] and [IOC], drops [IOC], hash [IOC]")


def test_mask_iocs_keeps_plain_text():
    s = "The actor used spearphishing to gain access."
    assert robust.mask_iocs(s) == s


def test_typo_deterministic_and_rate():
    s = "The adversary executed malicious payloads through scheduled tasks repeatedly."
    assert robust.typo(s, 0.05, 7) == robust.typo(s, 0.05, 7)
    assert robust.typo(s, 0.0, 7) == s
    t = robust.typo(s, 1.0, 7)
    assert t != s and len(t) == len(s) and sorted(t) == sorted(s)      # only swaps


def test_lower_nopunct():
    assert robust.lower_nopunct("It ran cmd.exe, then (quietly) exited!") == "it ran cmd exe then quietly exited"

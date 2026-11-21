# 05 Error and rarity analysis

Systems: SVM (refit), RoBERTa and SecBERT (3-seed probability average), Matcher (3-seed score average), Fusion (3,1,1,1) seed-averaged, Classifiers-only (reference). All on the 725 test sentences. [RECOMPUTED]

## 1. P@1 by train support of the sentence's rarest gold label

Bucket rule fixed in the task brief: unseen, 1-4, 5-9, 10-19, 20-49, 50+. F1 column in the CSV = macro label-F1 over the test labels whose own train support falls in the bucket, using each system's top-1 label as its prediction (the matcher and the fusion have no threshold).

| bucket | n sent. | SVM | RoBERTa | SecBERT | Matcher | Fusion | Cls-only |
|---|---|---|---|---|---|---|---|
| unseen (0) | 10 | 0.000 | 0.000 | 0.000 | 0.200 | 0.000 | 0.000 |
| 1-4 | 34 | 0.206 | 0.294 | 0.176 | 0.559 | 0.294 | 0.176 |
| 5-9 | 30 | 0.400 | 0.500 | 0.400 | 0.600 | 0.567 | 0.467 |
| 10-19 | 66 | 0.606 | 0.636 | 0.697 | 0.667 | 0.712 | 0.667 |
| 20-49 | 216 | 0.722 | 0.759 | 0.755 | 0.750 | 0.819 | 0.787 |
| 50+ | 369 | 0.875 | 0.859 | 0.867 | 0.862 | 0.897 | 0.886 |

## 2. Per-tactic P@1

Tactics from ATT&CK Enterprise v12.1 STIX (`external/enterprise-attack-12.1.json`, downloaded from github.com/mitre-attack/attack-stix-data; not part of the original project files). A sentence is counted under every tactic of every gold label, so rows overlap. Test labels without a tactic in v12.1 (revoked/deprecated): none.

| tactic | n | SVM | RoBERTa | SecBERT | Matcher | Fusion |
|---|---|---|---|---|---|---|
| defense-evasion | 191 | 0.723 | 0.743 | 0.738 | 0.759 | 0.801 |
| discovery | 181 | 0.790 | 0.773 | 0.790 | 0.801 | 0.834 |
| command-and-control | 130 | 0.815 | 0.777 | 0.769 | 0.800 | 0.815 |
| privilege-escalation | 95 | 0.737 | 0.737 | 0.747 | 0.789 | 0.758 |
| execution | 94 | 0.787 | 0.798 | 0.840 | 0.766 | 0.862 |
| persistence | 76 | 0.671 | 0.724 | 0.697 | 0.737 | 0.724 |
| collection | 72 | 0.681 | 0.792 | 0.708 | 0.819 | 0.833 |
| credential-access | 39 | 0.769 | 0.769 | 0.769 | 0.769 | 0.769 |
| reconnaissance | 18 | 0.889 | 0.778 | 0.833 | 0.556 | 0.889 |
| lateral-movement | 16 | 0.438 | 0.500 | 0.625 | 0.688 | 0.688 |
| exfiltration | 13 | 0.538 | 0.538 | 0.538 | 0.538 | 0.615 |
| initial-access | 12 | 0.500 | 0.500 | 0.667 | 0.833 | 0.750 |
| impact | 10 | 0.300 | 0.400 | 0.400 | 0.700 | 0.500 |

## 3. Top confusions (Fusion; all systems in `05_top20_confusions.csv`)

Counting rule: every wrong top-1 sentence contributes one (gold, predicted) pair per gold label.

| gold | predicted | n | relation |
|---|---|---|---|
| T1069 Permission Groups Discovery | T1087 Account Discovery | 4 | unrelated technique family |
| T1552.001 Credentials In Files | T1003 OS Credential Dumping | 4 | unrelated technique family |
| T1001 Data Obfuscation | T1132 Data Encoding | 3 | unrelated technique family |
| T1021.002 SMB/Windows Admin Shares | T1018 Remote System Discovery | 2 | unrelated technique family |
| T1005 Data from Local System | T1105 Ingress Tool Transfer | 2 | unrelated technique family |
| T1569.002 Service Execution | T1543.003 Windows Service | 2 | unrelated technique family |
| T1001 Data Obfuscation | T1573 Encrypted Channel | 2 | unrelated technique family |
| T1070.004 File Deletion | T1518.001 Security Software Discovery | 2 | unrelated technique family |
| T1140 Deobfuscate/Decode Files or Information | T1027 Obfuscated Files or Information | 2 | unrelated technique family |
| T1069 Permission Groups Discovery | T1560 Archive Collected Data | 1 | unrelated technique family |
| T1018 Remote System Discovery | T1560 Archive Collected Data | 1 | unrelated technique family |
| T1098 Account Manipulation | T1087 Account Discovery | 1 | unrelated technique family |
| T1548.001 Setuid and Setgid | T1016 System Network Configuration Discovery | 1 | unrelated technique family |
| T1041 Exfiltration Over C2 Channel | T1105 Ingress Tool Transfer | 1 | unrelated technique family |
| T1040 Network Sniffing | T1071 Application Layer Protocol | 1 | unrelated technique family |
| T1115 Clipboard Data | T1113 Screen Capture | 1 | unrelated technique family |
| T1547.004 Winlogon Helper DLL | T1070 Indicator Removal | 1 | unrelated technique family |
| T1095 Non-Application Layer Protocol | T1571 Non-Standard Port | 1 | unrelated technique family |
| T1197 BITS Jobs | T1105 Ingress Tool Transfer | 1 | unrelated technique family |
| T1087 Account Discovery | T1033 System Owner/User Discovery | 1 | unrelated technique family |

## 4. Parent vs sub-technique confusions (share of each system's top-1 errors)

| system | errors | pred is parent | pred is sub-technique | siblings | unrelated family |
|---|---|---|---|---|---|
| SVM | 187 | 1 | 3 | 3 | 180 |
| RoBERTa | 177 | 0 | 2 | 3 | 172 |
| SecBERT | 178 | 1 | 2 | 2 | 173 |
| Matcher | 162 | 2 | 1 | 2 | 157 |
| Fusion | 143 | 0 | 2 | 2 | 139 |

Technique-level P@1 (prediction and gold reduced to the parent technique): SVM 0.752, RoBERTa 0.763, SecBERT 0.761, Matcher 0.783, Fusion 0.808.

## 5. Sentences fixed vs broken by the fusion

Reference = best single system chosen by **DEV** P@1 (not test): SVM 0.738, RoBERTa 0.778, SecBERT 0.758, Matcher 0.785 -> **Matcher** (test P@1 0.777). Examples = the 10 lowest test sentence ids in each group (rule fixed before looking).

- vs Matcher: fixed 51, broken 32, net +19 (+0.0262 P@1); both right 531, both wrong 111
- vs Classifiers-only: fixed 23, broken 2, net +21 (+0.0290 P@1); both right 559, both wrong 141

**fixed (vs Matcher), 10 lowest ids:**

| id | gold | Matcher pred | fusion pred | sentence |
|---|---|---|---|---|
| 65 | T1055 | T1547.008 | T1055 | can inject content into lsass.exe to load a module. |
| 79 | T1029 | T1497.003 | T1029 | can sleep for a given number of seconds. |
| 95 | T1518.001 | T1562.001 | T1518.001 | checks for the presence of certain security-related processes and deletes its installer/uninstaller component  |
| 156 | T1005 | T1048 | T1005 | exfiltrates data collected from the victim mobile device. |
| 201 | T1027 | T1573 | T1027 | has encrypted its payload with RC4. |
| 208 | T1204 | T1598.003 | T1204 | has lured users to click links to malicious HTML applications delivered via spearphishing emails. |
| 254 | T1046 | T1018 | T1046 | has used the publicly available tool SoftPerfect Network Scanner as well as a custom tool called GOLDIRONY to  |
| 264 | T1083 | T1039 | T1083 | identified and extracted all Word documents on a server by using a command containing * .doc and *.docx. The a |
| 296 | T1106 | T1055 | T1106 | leverages the Windows API calls: VirtualAlloc(), WriteProcessMemory(), and CreateRemoteThread() for process in |
| 339 | T1003 | T1110 | T1003 | regularly deploys both publicly available and custom password retrieval tools on victims. |

**broken (vs Matcher), 10 lowest ids:**

| id | gold | Matcher pred | fusion pred | sentence |
|---|---|---|---|---|
| 10 | T1069 | T1069 | T1087 | actors used the following command following exploitation of a machine with  malware to list local groups: net  |
| 16 | T1548.001 | T1548.001 | T1016 | adds the setuid flag to a binary so it can easily elevate in the future. |
| 30 | T1547.004 | T1547.004 | T1070 | A  variant registers as a Winlogon Event Notify DLL to establish persistence. |
| 69 | T1087 | T1087 | T1033 | can obtain a list of users. |
| 84 | T1546.003 | T1546.003 | T1047 | can use a WMI script to achieve persistence. |
| 141 | T1547.008 | T1547.008 | T1574.002 | drops a malicious file (sspisrv.dll) alongside a copy of lsass.exe, which is used to register a service that l |
| 148 | T1486 | T1486 | T1132 | encrypts data using Base64 before being sent to the command and control server. |
| 150 | T1012 | T1012 | T1070 | enumerates Registry keys associated with event logs. |
| 166 | T1552.001 | T1552.001 | T1003 | gathers credentials in files for chrome, 1password, and keychains. |
| 168 | T1082 | T1082 | T1005 | gathers information on the system and local drives. |

## 6. Truncated sentences and multi-label sentences (P@1)

| subset | n | SVM | RoBERTa | SecBERT | Matcher | Fusion |
|---|---|---|---|---|---|---|
| truncated >128 RoBERTa tokens | 34 | 0.676 | 0.529 | 0.647 | 0.529 | 0.676 |
| not truncated | 691 | 0.745 | 0.767 | 0.760 | 0.789 | 0.809 |
| multi-label | 90 | 0.789 | 0.733 | 0.744 | 0.711 | 0.789 |
| single-label | 635 | 0.735 | 0.759 | 0.756 | 0.786 | 0.805 |

Note: with n=34 the 95% half-width of a P@1 value is about +/-0.15; multi-label rows are easier for P@1 by construction (more gold labels to hit).

## 7. Calibration (optional)

ECE, 10 equal-width bins, confidence = sigmoid probability of the top-1 label, correctness = top-1 is gold. Only the transformer classifiers output probabilities.

| model | seed | ECE | mean confidence | P@1 |
|---|---|---|---|---|
| roberta | 42 | 0.169 | 0.908 | 0.757 |
| roberta | 43 | 0.181 | 0.922 | 0.743 |
| roberta | 44 | 0.168 | 0.909 | 0.754 |
| secbert | 42 | 0.125 | 0.855 | 0.743 |
| secbert | 43 | 0.147 | 0.878 | 0.748 |
| secbert | 44 | 0.142 | 0.868 | 0.739 |

roberta: ECE 0.172 +/- 0.007; secbert: ECE 0.138 +/- 0.012
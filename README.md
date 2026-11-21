# Explainable Classification of Cybersecurity Threat Reports Using NLP

Sentence-level mapping of cyber-threat-intelligence text to MITRE ATT&CK techniques, with word-level explanations.

**Author:** Osama Bin Hashim

## What is in this repository

| Path | Contents |
|---|---|
| `app/` | Streamlit demo app (replay, live inference, explanations, training check) |
| `launcher/` | Portable Windows launcher, repair and verification scripts |
| `data/_showcase/` | Curated research package: notebooks, results, figures, thesis feed, docs, tests |
| `data/_evidence_pack/` | Auditable evidence: dataset checks, statistics, error analysis, SHAP, reproducibility scripts |
| `README_DEMO.md` | How to run the offline demo on Windows |

## Quick start

```bat
START_DEMO.bat
```

The demo opens locally at `http://127.0.0.1:8501`. It needs no internet once the runtime and models are present.

To check the installation:

```bat
CHECK_DEMO.bat
```

## What is not uploaded

GitHub rejects individual files larger than 100 MB and is not a model or runtime store. The following are deliberately excluded by `.gitignore`:

- `runtime/` - local Python environment (about 1.4 GB, 52,000 files)
- `logs/` - local run logs
- `data/Dataset/`, `data/Experiments/`, `data/models/` and the training runs - raw data and model weights (about 9 GB)
- `*.safetensors`, `*.pt`, `*.npy` and other large artifacts

The curated, small results needed to audit the thesis are in `data/_showcase/` and `data/_evidence_pack/`.

## Main result

Fusion P@1 **0.803** [0.774, 0.832] (seed-averaged), +0.029 over the classifiers-only ensemble. The gain over the matcher ensemble does not survive Holm correction (p = 0.190), and the fusion does not help rare or unseen techniques. See `data/_showcase/README.md` for the full, honest status board.

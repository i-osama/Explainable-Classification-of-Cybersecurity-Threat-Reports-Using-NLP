# CI templates: UNTESTED

These three files were written but **never executed**: no Docker build was run, no GitHub Actions run exists, `ruff` and `pre-commit` are not installed here.
They are templates for the author to activate after choosing a licence and deciding whether the repository becomes public.

| file | purpose | to activate |
|---|---|---|
| `Dockerfile` | CPU image that runs the data-free tests | `docker build -f _showcase/ci/Dockerfile -t ttpmap .` from the repository root |
| `tests.yml` | GitHub Actions workflow: data-free tests on push | copy to `.github/workflows/tests.yml` at the repository root |
| `pre-commit-config.yaml` | ruff lint and format hooks | copy to `.pre-commit-config.yaml` at the repository root, then `pre-commit install` |

Without the dataset and the saved predictions (not in the repository), the data-dependent tests report SKIP; the metric, fusion, statistics, schema and leakage-guard tests run.

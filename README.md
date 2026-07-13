# AWS ML Ops Lab — Incident Risk Classifier + Triage API

A hands-on lab that maps to the **AWS Certified Machine Learning Engineer – Associate (MLA-C01)** exam
domains, built like a small production system rather than a notebook.

**Use case:** given simulated service-incident/log records, predict an incident's **risk level**
(`low` / `medium` / `high`). Later this becomes a triage API.

## Why this project
- Mirrors real MLOps: data prep → training → evaluation → deployment → monitoring.
- Every AWS service used is justified, has a cheaper alternative noted, and has cleanup steps.
- Doubles as a resume/portfolio project for AI platform / MLOps / backend-AI roles.

## Ground rules (baked into how we work)
- No employer/internal/customer data — everything here is synthetic.
- No credentials in the repo. AWS auth comes from your local profile / env only.
- Every AWS command is explained before it runs and requires your approval.
- Prefer low-cost resources; clean up everything (`scripts/cleanup.sh`, `docs/cost-cleanup.md`).

## Exam domain map
| Domain | Weight | Where in this lab |
|---|---|---|
| 1. Data Preparation for ML | 28% | `src/prepare_data.py`, S3, Glue, Athena |
| 2. ML Model Development | 26% | `src/train.py`, `src/evaluate.py`, SageMaker training |
| 3. Deployment & Orchestration | 22% | `src/predict.py`, SageMaker endpoint/batch, Step Functions, Lambda |
| 4. Monitoring, Maintenance, Security | 24% | CloudWatch, IAM, KMS, Model Monitor, Budgets |

## Repo layout
```
ai-mlops-incident-lab/
  README.md
  requirements.txt
  docs/            architecture, exam notes, wrong-answer log, cost/cleanup
  data/            synthetic dataset (raw) + processed outputs (gitignored)
  notebooks/       scratch exploration
  src/             prepare_data / train / evaluate / predict
  infra/           terraform-or-cdk (added when we reach Domain 3)
  tests/           unit tests for the data pipeline
  scripts/         data generator + cleanup
```

## Quickstart (local, Section 1)
```bash
cd ai-mlops-incident-lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py            # (already run once; regenerates data/sample_incidents.csv)
python src/prepare_data.py                 # writes data/processed/{train,test}.csv + report
pytest -q
```

## Progress
- [x] Section 1 — Local repo, synthetic data, data prep (Domain 1 foundation)
- [ ] Section 2 — S3 + Glue + Athena (Domain 1 on AWS)
- [ ] Section 3 — SageMaker training + evaluation (Domain 2)
- [ ] Section 4 — Deployment: endpoint/batch + Step Functions + Lambda (Domain 3)
- [ ] Section 5 — Monitoring, IAM, KMS, Budgets (Domain 4)

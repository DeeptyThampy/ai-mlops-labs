# Architecture

## Target end-state (built incrementally)
```
                       ┌─────────────────────────────────────────────┐
                       │                 AWS Account                  │
  raw CSV  ──upload──▶ │  S3 (raw/)  ──Glue crawler──▶ Glue Catalog   │
                       │      │                             │         │
                       │      │                          Athena SQL   │  ← Domain 1
                       │      ▼                                        │
                       │  prepare_data (local or Processing job)       │
                       │      │                                        │
                       │      ▼                                        │
                       │  S3 (processed/) ──▶ SageMaker Training ──▶   │  ← Domain 2
                       │                         model artifact (S3)   │
                       │                              │                │
                       │           ┌──────────────────┴─────────┐     │
                       │           ▼                            ▼      │
                       │   SageMaker Endpoint            Batch Transform│  ← Domain 3
                       │           ▲                                    │
                       │      Lambda + API Gateway (triage API)         │
                       │           ▲                                    │
                       │      Step Functions (orchestrate prep→train→   │
                       │                       eval→register→deploy)    │
                       │                                                │
                       │  CloudWatch logs/metrics/alarms, Model Monitor │  ← Domain 4
                       │  IAM least-priv roles, KMS/S3 encryption,      │
                       │  AWS Budgets                                   │
                       └────────────────────────────────────────────── ┘
```

## Build order
1. **Local** (done): synthetic data + `prepare_data.py` + tests.
2. **S3 + Glue + Athena**: land raw data, catalog it, query with SQL.
3. **SageMaker training**: train on processed data, produce a versioned model artifact.
4. **Deployment + orchestration**: endpoint/batch, Lambda triage API, Step Functions pipeline.
5. **Monitoring + security**: CloudWatch alarms, Model Monitor, IAM/KMS, Budgets.

## Decision log
| Decision | Choice | Cheaper/simpler alternative | Why chosen |
|---|---|---|---|
| Data format | CSV now, Parquet on S3 | keep CSV | Parquet is columnar → cheaper Athena scans |
| Model | scikit-learn classifier | SageMaker built-in XGBoost | sklearn is enough for tabular; simplest first |
| Compute for prep | local script | SageMaker Processing job | local is free while iterating |

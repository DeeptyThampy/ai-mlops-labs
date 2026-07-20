# MLA-C01 Exam Notes — taught, not listed

How to read this file: each idea is explained in plain English, then tied to *our code*,
then to *the exam trap* AWS likes to set. New to a term? Check `docs/glossary.md`.

Legend:
- 💡 **Idea** — the concept in plain words
- 🔧 **In our lab** — where you see it in the code
- ⚠️ **Exam trap** — the wrong answer AWS dangles

---

## Domain 1 — Data Preparation for ML (28% of the exam)

This domain is really one story: *raw, messy data comes in → you turn it into clean,
trustworthy, model-ready data → without cheating.* Here's that story in pieces.

### 1. Get the data in and know its shape (ingest + validate)

💡 Before you transform anything, confirm the data is what you think it is. Right columns?
Right types? This is **schema validation** — a bouncer checking IDs at the door.

🔧 In our lab: `validate_schema()` fails loudly if a required column is missing, *before*
we waste time cleaning.

⚠️ Exam trap: skipping validation and "discovering" a broken column only after training
produces garbage. Data-integrity checks belong *up front*.

### 2. Clean the mess

💡 Real data is dirty: mixed case (`PAYMENTS` vs `payments`), stray spaces, blanks,
duplicates, text where numbers should be. Cleaning normalizes all of that.

🔧 In our lab: `clean()` lowercases/trims text, forces number columns to real numbers
(blanks → "missing"), maps True/False to 1/0, and drops exact duplicate incidents.

⚠️ Exam trap: treating `"payments"` and `"PAYMENTS"` as two different services — inconsistent
categories silently split your data and hurt the model.

### 3. Handle missing values

💡 Models can't train on blanks. You either drop rows or **impute** (fill in a sensible value).
We fill numeric blanks with the **median** (the middle value), which is robust to outliers —
one crazy-high latency won't drag it around like the average (mean) would.

🔧 In our lab: we compute medians and fill gaps with them.

⚠️ Exam trap: choosing mean when the data has big outliers. Median is the safer default for
skewed data like latencies.

### 4. Make better signals (feature engineering)

💡 You often help the model by combining raw columns into more meaningful **features** —
e.g., averaging CPU and memory into one `resource_pressure` number.

🔧 In our lab: `engineer()` adds `resource_pressure`, `is_peak_severity`, and `log_len`.

⚠️ Exam trap: accidentally building a feature from information you wouldn't have at prediction
time — that's leakage (see #6).

### 5. Turn categories into numbers (encoding)

💡 Models only do math, so text categories must become numbers. **One-hot encoding** makes a
0/1 column per category; **label encoding** maps the target classes to integers.

🔧 In our lab: `pd.get_dummies()` one-hot encodes `service`/`region`/`severity`; a `LabelEncoder`
maps low/medium/high for the target.

⚠️ Exam trap: encoding train and test differently so columns don't line up. We fix this by
aligning test's columns to train's.

### 6. Split honestly — the big one (train/test split + no leakage)

💡 Split data into **train** (model studies this) and **test** (you grade on this, hidden).
The rule that trips everyone: **split FIRST, then fit your cleaning/scaling/encoding on the
training half only.** If you fit on everything before splitting, the model indirectly "sees"
the test data — that's **data leakage**, and your score becomes a lie.

🔧 In our lab: we `train_test_split(... stratify=y)` *before* computing medians or encoders,
then apply those to test. Stratify keeps the rare "high" class proportional in both halves.

⚠️ Exam trap (the classic): "96% in testing, 71% in production — why?" → leakage from fitting
transforms on the full dataset. Memorize this shape.

### 7. Keep training and serving identical (avoid train/serve skew)

💡 The model must get data prepared the *same way* in production as in training. If prep differs,
the live model sees weird inputs and quietly degrades — **train/serve skew**.

🔧 In our lab: we save the fitted transforms to `preprocess.joblib` so serving reuses the exact
same logic instead of re-implementing it.

⚠️ Exam trap: re-deriving preprocessing separately for serving. Reuse the saved artifact.

📘 Deeper reference: [flashcards](flashcards.md) Card 11 (train/serve skew) + Card 12 (`preprocess.joblib`).

### 8. Fix imbalance the right way

💡 Our classes are lopsided (mostly "low"). A lazy model scores high by always guessing "low."

🔧 Later in training we'll use class weighting / resampling and judge with per-class recall/F1.

⚠️ Exam trap: "collect a bigger *test* set" does nothing for imbalance. Fixes happen on the
*training* data (weighting, oversampling/SMOTE) and in your *choice of metric*.

📘 Deeper reference: [flashcards](flashcards.md) Cards 1–10 (imbalance, accuracy, recall / precision / F1, class weighting, SMOTE).

### The AWS side of Domain 1 (built in Section 2)

- **S3** — where all data lives (raw + processed). The data lake.
- **Glue Crawler** — auto-detects schema and fills the **Glue Data Catalog**. It *describes*,
  it does *not transform* (⚠️ common trap).
- **Athena** — SQL over S3 files, serverless, pay per byte scanned. Queries in place; does *not*
  load into a warehouse (that's Redshift — ⚠️ trap).
- **Parquet + partitioning** — the standard way to make Athena cheaper (scan fewer bytes).
- **Encryption** — turn on S3 encryption (SSE-S3 or SSE-KMS) so data is protected at rest.

📘 Deeper reference: [flashcards](flashcards.md) Cards A1–A14 (S3 mental model, Glue Data Catalog, Crawler vs CTAS vs Glue ETL, Athena, Parquet, partitioning, CTAS, Snappy).

---

## Domain 2 — ML Model Development (26%)
*Filled in during Section 3. Preview: pick an algorithm, train on the processed data, tune
hyperparameters, and evaluate with the right metric (accuracy lies on imbalanced data).*

## Domain 3 — Deployment & Orchestration (22%)
*Filled in during Section 4. Preview: real-time **endpoint** vs **batch transform** (cost!),
a **Lambda** + API front door, and a **Step Functions** pipeline tying prep→train→deploy together.*

## Domain 4 — Monitoring, Maintenance, Security (24%)
*Filled in during Section 5. Preview: **CloudWatch** logs/metrics/alarms, **Model Monitor** for
drift, **IAM** least privilege, **KMS** encryption, and **AWS Budgets** so you never get surprised.*

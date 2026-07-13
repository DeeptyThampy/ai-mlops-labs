# Glossary — plain-English ML & AWS terms

Your reference sheet. Every term is: **what it is** (no jargon) → *why it matters*.
Skim this whenever a term feels fuzzy. Grows as the lab grows.

---

## Part A — Core ML / MLOps ideas

**MLOps**
"DevOps, but for machine learning." All the practices and tooling that take a model
from a one-off experiment to a reliable, monitored production service — version control,
automated pipelines, deployment, monitoring, retraining.
*Why it matters:* it's literally what this certification tests. The exam isn't "can you
do math," it's "can you operate ML systems."

**Schema validation**
Checking that incoming data has the columns and data types you expect *before* you use it.
Like a bouncer checking IDs at the door.
*Why it matters:* if a column silently disappears or a number arrives as text, it can
corrupt training or crash serving. Catching it early is a data-integrity best practice (Domain 1).

**Feature**
A single input signal the model learns from — e.g., `latency_ms` or `cpu_util`. A row of
features describes one incident.
*Why it matters:* models learn from features, not raw logs. Choosing good ones is half the game.

**Feature engineering**
Creating better input signals from raw data — e.g., averaging `cpu_util` + `mem_util` into
a new `resource_pressure` feature.
*Why it matters:* often the single biggest lever on model quality — bigger than the algorithm choice.

**Encoding**
Turning non-number data into numbers, because models only do math. "payments" → numbers.
- *One-hot encoding:* one yes/no (0/1) column per category (a `service_payments` column that's 1 or 0).
- *Label encoding:* map each category to an integer (used for the target: low=1, medium=2, high=0).
*Why it matters:* forget to encode and training fails; encode inconsistently between train and
serving and you get train/serve skew (below).

**Train/test split**
Splitting your data into a part the model learns from (**train**) and a part you hide to grade
it honestly (**test**).
*Why it matters:* like studying from practice problems but grading yourself on a *fresh* exam.
Grading on data the model already saw gives a fake-high score.

**Stratified split**
A train/test split that keeps the same class proportions in both halves (so if 8% of incidents
are "high," both train and test stay ~8% "high").
*Why it matters:* with imbalanced classes, a naive split can leave almost no rare examples in one side.

**Data leakage**
When information the model shouldn't have at prediction time sneaks into training — most commonly
by fitting your cleaning/scaling on the *whole* dataset before splitting.
*Why it matters:* the model looks amazing in testing, then fails in production. It's the #1
subtle ML bug and a favorite exam trap. Fix: **split first, then fit transforms on train only.**

**Train/serve skew**
When the data preparation during training differs from the preparation during live prediction,
so the model sees differently-shaped data in production and quietly degrades.
*Why it matters:* fix by reusing the *exact same* transform code/artifacts in both places
(that's why we save `preprocess.joblib`).

**Class imbalance**
When some target classes are much rarer than others (70% low, 8% high).
*Why it matters:* a lazy model can score high just by always guessing "low." Fix with class
weighting / oversampling (e.g., SMOTE) and judge with per-class recall/F1, not plain accuracy.

**Model artifact**
The saved output of training — the trained model in a file, ready to load and make predictions.
*Why it matters:* it's what you version, store (in S3), and deploy. Deployment = shipping this file.

**Hyperparameter**
A setting you choose *before* training that controls how the model learns (e.g., tree depth,
learning rate) — as opposed to the values the model learns on its own.
*Why it matters:* "hyperparameter tuning" (trying combinations to find the best) is a Domain 2 topic.

**Inference**
Using a trained model to make a prediction on new data. "Real-time inference" = one request at
a time; "batch inference" = a big pile at once.

**Drift**
When live data slowly changes over time so it no longer looks like the training data, and the
model gets worse without anyone touching it.
*Why it matters:* detecting drift is the whole reason Model Monitor exists (Domain 4).

---

## Part B — AWS services & data formats

**S3 (Simple Storage Service)**
AWS's cloud file storage — effectively unlimited "buckets" that hold files ("objects"). Cheap,
durable, the foundation of almost every AWS data workflow.
*Why it matters:* your raw data, processed data, and model artifacts all live in S3. It's the
"data lake" landing zone in this lab.

**Glue Data Catalog**
A central "table of contents" that describes what data you have and its schema (columns + types),
so query tools know how to read your S3 files. It stores *metadata*, not the data itself.
*Why it matters:* Athena and others read the Catalog to understand your S3 files.

**Glue Crawler**
A robot that scans your S3 files, guesses the schema, and fills in the Data Catalog automatically.
*Why it matters — exam trap:* a crawler **describes** data; it does **not** transform it.
Transformation is a Glue ETL job / SageMaker Processing, not the crawler.

**Athena**
Run SQL queries directly on files sitting in S3 — no database server to manage ("serverless").
You pay **per amount of data scanned**.
*Why it matters — exam trap:* Athena queries data *in place*; it does not load data into a
warehouse (that's Redshift). Cost is driven by bytes scanned → see Parquet + partitioning.

**Parquet**
A file format that stores data **by column** instead of by row, and compresses it.
*Why it matters:* queries that read only a few columns scan far less data → faster and cheaper
Athena. Converting CSV → Parquet is a classic cost-optimization answer.

**Partitioning**
Organizing S3 files into folders by a key (e.g., `region=us-east-1/…`) so a query filtering on
that key can skip irrelevant folders entirely.
*Why it matters:* less data scanned = cheaper Athena. Pairs with Parquet as the go-to cost fix.

**SageMaker**
AWS's all-in-one ML platform: prepare data, train models, host them for predictions, and monitor
them — all managed for you.
*Why it matters:* the star of this exam. Most Domain 2–4 questions involve a SageMaker feature.

**Endpoint (SageMaker real-time endpoint)**
A live, always-on web address that returns predictions one request at a time (real-time inference).
*Why it matters — cost trap:* it bills **per hour it's running**, whether or not anyone calls it.
The #1 source of surprise SageMaker bills. Delete it when done.

**Batch transform**
Run predictions on a big batch of data all at once, then automatically shut down.
*Why it matters:* no always-on cost. If you don't need instant per-request answers, this is the
cheaper choice — a common "reduce cost" exam answer vs. a real-time endpoint.

**Step Functions**
AWS's workflow orchestrator: chains steps (prep → train → evaluate → deploy) into one automated
pipeline, with retries and branching, drawn as a visual "state machine."
*Why it matters:* the go-to service for *orchestrating* an ML pipeline (Domain 3).

**Lambda**
Run small pieces of code on demand without managing any servers ("serverless function"). Scales
to zero when idle.
*Why it matters:* the glue between services and a common front door for a lightweight prediction
API. Cheap because you pay per invocation, not per hour.

**CloudWatch**
AWS's monitoring hub: collects **logs** (text output), **metrics** (numbers over time), and fires
**alarms** when something crosses a threshold.
*Why it matters:* your first stop for "is it healthy / what went wrong" (Domain 4).

**IAM (Identity and Access Management)**
Controls **who can do what** in AWS, via roles and policies. "Least privilege" = grant only the
permissions actually needed.
*Why it matters:* security questions lean heavily on IAM; the trap answer is usually the one that
grants too-broad permissions (e.g., `*`).

**KMS (Key Management Service)**
Manages the encryption keys used to encrypt your data at rest (e.g., S3 objects, model artifacts).
*Why it matters:* "encrypt data at rest with a customer-managed KMS key" is a standard secure-design
answer (Domains 1 & 4).

**Model Monitor (SageMaker)**
A feature that watches a deployed model's incoming data and predictions for **drift** and quality
problems, and alerts you.
*Why it matters:* the canonical answer to "how do I detect my model degrading in production" (Domain 4).

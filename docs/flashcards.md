# MLA-C01 Flashcards — quick reference

Skimmable Q&A cards for pre-exam review. For the *story* of how each concept fits the lab, see [exam-notes.md](exam-notes.md). For plain-English definitions, see [glossary.md](glossary.md). For questions you missed and rules distilled from them, see [wrong-answer-log.md](wrong-answer-log.md).

**How to use:** skim weekly, drill the week before the exam. When you can answer the front of a card without looking at the back, you've internalized it.

---

## Contents

**Part 1 — ML fundamentals** (Cards 1–12)
Class imbalance, accuracy, recall, precision, F1, class weighting, SMOTE, train/serve skew, `preprocess.joblib`.

**Part 2 — AWS data services** (Cards A1–A14)
S3, Glue Data Catalog, Crawler vs CTAS vs Glue ETL, Athena, CSV vs Parquet, partitioning, CTAS, Snappy.

**Part 3 — SageMaker services** (Cards S1+; added as we build Sections 3–5)
Training jobs, real-time endpoints, batch transform, network modes.

Each Part ends with an *Exam Pattern* recap.

---

## Part 1 — ML fundamentals

Domain 1 concepts + the metric vocabulary for Domain 2.

---

## Card 1 — Class Imbalance

**Front**

What is class imbalance?

**Back**

Class imbalance means one prediction class appears much more often than another.

Example:

* 90 low-risk incidents
* 8 medium-risk incidents
* 2 high-risk incidents

The dataset is dominated by the `low` class.

### Why it matters

A model may learn to predict the common class most of the time and ignore rare but important classes.

### Memory line

> Class imbalance = the answer categories are unevenly represented.

---

## Card 2 — Accuracy

**Front**

What is accuracy?

**Back**

Accuracy measures the percentage of all predictions that were correct.

```text
Accuracy = correct predictions ÷ total predictions
```

Example:

```text
90 correct predictions ÷ 100 total = 90% accuracy
```

### Why it can be misleading

Suppose the dataset contains:

* 90 low-risk incidents
* 8 medium-risk incidents
* 2 high-risk incidents

A model that always predicts `low` gets 90% accuracy, despite missing every medium- and high-risk incident.

### Memory line

> Accuracy asks, “How many total predictions were correct?”

---

## Card 3 — Recall

**Front**

What is recall for a class?

**Back**

Recall measures how many real examples of a class the model successfully found.

For the high-risk class:

```text
High-risk recall =
high-risk incidents correctly predicted
÷
all actual high-risk incidents
```

Example:

There are 10 genuinely high-risk incidents.

The model catches 7.

```text
Recall = 7 ÷ 10 = 70%
```

### What happened to the other three?

They were high risk, but the model incorrectly predicted something else.

These are called **false negatives**.

### Memory line

> Recall asks, “Of everything that truly belonged to this class, how much did we catch?”

---

## Card 4 — Why High-Risk Recall Matters

**Front**

Why might recall be more important than accuracy for incident risk?

**Back**

Missing a truly high-risk incident can be costly.

Suppose the model has:

```text
95% overall accuracy
30% high-risk recall
```

The model looks good based on accuracy but catches only 30% of high-risk incidents.

For an incident system, that could be unacceptable.

### Memory line

> High accuracy does not guarantee that rare, important incidents are being caught.

---

## Card 5 — Precision

**Front**

What is precision?

**Back**

Precision measures how often the model is correct when it predicts a particular class.

For high risk:

```text
High-risk precision =
correct high-risk predictions
÷
all high-risk predictions made by the model
```

Example:

The model labels 10 incidents as high risk.

Only 6 are truly high risk.

```text
Precision = 6 ÷ 10 = 60%
```

The other four are false alarms, called **false positives**.

### Memory line

> Precision asks, “When the model says high risk, how often is it right?”

---

## Card 6 — Recall vs. Precision

**Front**

What is the difference between recall and precision?

**Back**

### Recall

Of all the real high-risk incidents, how many did we catch?

### Precision

Of all the incidents we called high risk, how many really were high risk?

Example:

```text
High recall, low precision:
Catch almost every dangerous incident,
but produce many false alarms.

High precision, low recall:
Most alerts are correct,
but many dangerous incidents are missed.
```

### Memory line

> Recall worries about missing real cases.
> Precision worries about false alarms.

---

## Card 7 — F1 Score

**Front**

What is the F1 score?

**Back**

F1 combines precision and recall into one score.

```text
F1 = 2 × (precision × recall)
         ÷ (precision + recall)
```

You do not usually need to calculate it manually for the exam. Understand what it represents.

### Why use it?

F1 is useful when:

* classes are imbalanced
* both missed incidents and false alarms matter
* accuracy alone is misleading

### Example

```text
Precision = 80%
Recall = 20%
```

The model does not get a great F1 score because recall is poor.

F1 becomes high only when both precision and recall are reasonably strong.

### Memory line

> F1 balances precision and recall.

---

## Card 8 — Class Weighting

**Front**

What is class weighting?

**Back**

Class weighting tells the model:

> “Mistakes on rare classes should count more heavily.”

Suppose high-risk incidents are rare.

Without weighting:

```text
Missing one low-risk incident = ordinary mistake
Missing one high-risk incident = ordinary mistake
```

With class weighting:

```text
Missing one high-risk incident = more expensive mistake
```

The model is encouraged to pay more attention to the minority class.

### Important detail

Class weighting does not create additional rows.

It changes how strongly the model is penalized for mistakes.

### Example

```python
class_weight="balanced"
```

Many scikit-learn classifiers support this option.

### Memory line

> Class weighting changes the cost of mistakes, not the amount of data.

---

## Card 9 — SMOTE

**Front**

What is SMOTE?

**Back**

SMOTE stands for:

**Synthetic Minority Oversampling Technique**

It creates artificial training examples for a minority class.

Suppose training data contains:

```text
900 low-risk incidents
50 high-risk incidents
```

SMOTE creates additional synthetic high-risk examples based on patterns in the existing high-risk rows.

It does not simply copy the same row repeatedly. It creates new points between similar minority examples.

### Why use it?

It gives the model more minority-class examples to learn from.

### Critical rule

Apply SMOTE only to the training set.

Never apply SMOTE before train/test splitting, and never apply it to the test set.

Otherwise, the test results can become misleading or leaked.

### Memory line

> SMOTE creates synthetic minority examples in training only.

---

## Card 10 — SMOTE vs. Class Weighting

**Front**

How are SMOTE and class weighting different?

**Back**

### SMOTE

Creates additional synthetic minority-class training examples.

```text
Changes the training data
```

### Class weighting

Makes errors on minority classes count more.

```text
Changes the training penalty
```

### Simple comparison

```text
SMOTE:
“Give the model more high-risk examples.”

Class weighting:
“Punish the model more when it misses high-risk examples.”
```

Both are possible approaches to class imbalance.

---

## Card 11 — Train/Serve Skew

**Front**

What is train/serve skew?

**Back**

Train/serve skew happens when input data is prepared differently during training and live prediction.

Example:

During training:

```text
error_rate = 0.08
cpu_util = 0.75
```

During live inference:

```text
error_rate = 8
cpu_util = 75
```

Training used decimals, but production used percentages.

The model receives numbers, but their meanings are wrong.

Other examples:

* training uses dollars, production uses cents
* training fills missing CPU with `0.56`, production fills it with `0`
* training uses `severity_p1`, production sends `"P1"`
* training lowercases service names, production does not
* live feature columns appear in a different order

### Memory line

> Train/serve skew = training preparation and live preparation do not match.

---

## Card 12 — Why Save `preprocess.joblib`?

**Front**

Why did we save `preprocess.joblib`?

**Back**

Some preprocessing values are learned from the training data.

Our file saves:

* training-set medians
* expected feature-column names and order
* the label encoder

Example:

```text
Training median CPU = 0.56
```

When a live incident has missing CPU data, serving should use the same `0.56`.

It should not invent a new replacement value.

The saved feature list also helps ensure that live data reaches the model in the same column order used during training.

### Important limitation

In our current project, `preprocess.joblib` does not contain all cleaning and feature-engineering code.

The serving API must still correctly perform steps such as:

* trimming and lowercasing strings
* parsing booleans
* creating `resource_pressure`
* creating `log_len`
* one-hot encoding categories

### Memory line

> `preprocess.joblib` saves training-time preparation information so serving can remain consistent.

---

## One-Minute Review — ML fundamentals

## Class imbalance

Some target classes occur much more often than others.

## Accuracy

Percentage of all predictions that were correct.

## Recall

Of all real examples of a class, how many did the model find?

## Precision

Of all predictions for a class, how many were correct?

## F1 score

One score balancing precision and recall.

## Class weighting

Makes mistakes on minority classes more costly.

## SMOTE

Creates synthetic minority-class examples in the training data.

## Train/serve skew

Live inputs are prepared differently from training inputs.

## `preprocess.joblib`

Stores training-time preprocessing values and expected feature structure.

---

## Exam Pattern to Remember — ML

```text
High accuracy + rare important class
→ Check recall, precision and F1.

Minority class ignored
→ Consider class weighting or SMOTE.

SMOTE applied before splitting
→ Data leakage.

Training and production transforms differ
→ Train/serve skew.

Need identical preparation in production
→ Reuse saved preprocessing artifacts and logic.
```

---

## Part 2 — AWS data services

Section 2 of the lab. These cards cover how AWS stores, catalogs, and queries the raw data that a model will eventually train on. **Not ML concepts** — the AWS infrastructure that surrounds an ML pipeline.

---

## Card A1 — S3 has no real folders

**Front**

If S3 is a key-value store, how do folders work?

**Back**

They don't — not really. S3 stores objects under **keys** like `raw/incidents/sample.csv`. The `/` characters are just part of the key. The console *renders* keys that share a prefix as if they were folders, but there is no folder object underneath.

Uploading an object with a new key path makes the "folder" appear automatically. You never need to pre-create a folder.

### Memory line

> S3 folders are a UI illusion. Everything is a key + a value.

---

## Card A2 — Our lab's S3 prefixes

**Front**

What are the three prefixes we set up in `s3://mla-c01-lab/`?

**Back**

```text
raw/incidents/          ← source CSV (input data)
processed/              ← Parquet output written by CTAS
athena-results/         ← where Athena writes every query's result
```

Each prefix is a *pattern in object keys*, not a real folder.

---

## Card A3 — Glue Data Catalog

**Front**

Where do Athena "tables" actually live?

**Back**

**In the Glue Data Catalog** — a metadata store, not in S3.

A catalog entry says:

```text
table name  = incidents
schema      = incident_id STRING, timestamp STRING, ...
location    = s3://mla-c01-lab/raw/incidents/
format      = CSV
```

S3 holds only the byte files. The catalog holds the pointer + schema. Athena reads the catalog to know *what* and *where* to read.

### Memory line

> S3 holds the values. The Glue Data Catalog holds the "table" itself.

---

## Card A4 — Glue Crawler vs Glue ETL vs CTAS

**Front**

Three Glue-adjacent tools. Which one does what?

**Back**

| Tool | Job | Creates files? | Creates catalog entry? |
|---|---|---|---|
| Glue Crawler | Points at existing S3 files → infers schema → registers table | No | Yes |
| Athena CTAS | Runs a SELECT and writes result as new S3 files + registers table | Yes | Yes |
| Glue ETL job | Custom Python/Spark transformations, scheduled | Yes | Optional |

A common exam mistake: assuming Crawler can convert CSV to Parquet. **It can't** — Crawler only reads existing files. CTAS or Glue ETL do the writing.

### Memory line

> Crawler discovers. CTAS creates + registers. Glue ETL transforms with code.

---

## Card A5 — Athena

**Front**

What is Athena?

**Back**

A **serverless SQL query engine** for data in S3. You don't provision a cluster; you pay per query.

- **Metadata source:** Glue Data Catalog (table names, schemas, S3 paths)
- **Data source:** the S3 files pointed to by the catalog
- **Billing:** ~$5 per TB scanned

Every query = "read the bytes from S3, apply SQL, return rows, write result to the configured results location."

### Memory line

> Athena = SQL over S3, no server, pay per TB scanned.

---

## Card A6 — Athena vs Redshift vs EMR

**Front**

Which analytics service fits which situation?

**Back**

| Situation | Right service |
|---|---|
| Ad-hoc SQL on S3, least ops overhead | **Athena** |
| Warehouse for repeated heavy analytics, complex joins | **Redshift** (provisioned cluster) |
| Query S3 from an existing Redshift cluster | **Redshift Spectrum** |
| Custom Spark/Hive/Presto on S3 at massive scale | **EMR** |

Exam trap phrasing to watch for: *"least operational overhead"* almost always means **Athena**. Redshift is a distractor because it's SQL — but it needs a cluster.

---

## Card A7 — Athena query results location

**Front**

Where does Athena write query results, and how does it know?

**Back**

Athena writes every query's result as an object into an S3 prefix you configure in the **workgroup settings** (`Manage → Location of query result`).

For this lab: `s3://mla-c01-lab/athena-results/`

Each query produces two objects:

```text
<uuid>.csv           ← the rows
<uuid>.csv.metadata  ← schema/type info
```

If you never configure a location, Athena refuses to run queries. The prefix doesn't need to exist beforehand — S3 creates it when the first object is written.

---

## Card A8 — Data scanned = the whole cost story

**Front**

Why do we care about "Data scanned" under every query?

**Back**

Athena bills per TB scanned. Cost = `data_scanned × $5/TB`.

For our 70 KB CSV, cost is microscopic — but at TB scale, the same query pattern can differ by 100–1000× depending on file format and partitioning.

### Memory line

> Data scanned is the Athena bill. Reduce it via Parquet + partitioning + compression.

---

## Card A9 — CSV vs Parquet (row-oriented vs columnar)

**Front**

Why does CSV always scan the whole file, but Parquet doesn't?

**Back**

**CSV is row-oriented.** All 13 columns of a row are stored end-to-end on one line. To get column 3, you have to read the entire row. Filtering happens *after* reading.

**Parquet is columnar.** Each column is stored in its own segment. `SELECT service, region` reads only two column segments — often 5–10× less bytes.

Parquet also stores per-column min/max stats and supports **predicate pushdown** — the engine can skip whole row groups whose stats don't overlap the filter.

### Memory line

> CSV = one line per row. Parquet = one segment per column + built-in stats.

---

## Card A10 — Partitioning + Hive-style paths

**Front**

What does "partitioned by severity" actually do to S3?

**Back**

It splits the data into subfolders whose paths follow the **Hive convention** `column=value/`:

```text
s3://mla-c01-lab/processed/incidents_parquet/severity=P1/<file>.parquet
                                             severity=P2/<file>.parquet
                                             severity=P3/<file>.parquet
                                             severity=P4/<file>.parquet
```

Athena and Glue auto-recognize this convention. A query like `WHERE severity = 'P1'` reads only the `severity=P1/` subfolder — this is called **partition pruning**.

**Rule of thumb:** partition on the columns you filter by most often, with reasonable cardinality (handful to a few hundred values, not millions).

---

## Card A11 — Multi-column partitions and their order

**Front**

`partitioned_by = ARRAY['region', 'severity']` vs `ARRAY['severity', 'region']` — what changes?

**Back**

The **first column becomes the outer folder**:

```text
ARRAY['region', 'severity']
→ region=us-east-1/severity=P1/file.parquet
→ region=us-east-1/severity=P2/file.parquet

ARRAY['severity', 'region']
→ severity=P1/region=us-east-1/file.parquet
→ severity=P1/region=us-west-2/file.parquet
```

Put the column that appears in **most WHERE clauses first** — Athena skips whole subtrees at the top level.

Also: **the SELECT list must end with the partition columns in the same order** as the array. Athena uses column position, not name, to identify partitions.

### Memory line

> First-in-array = outer folder. SELECT ends with partition columns in the same order.

---

## Card A12 — CTAS

**Front**

What does `CREATE TABLE AS SELECT` do in Athena?

**Back**

Two things in one statement:

1. Runs the SELECT and **writes the result as new S3 objects** at `external_location`.
2. **Registers a new catalog table** pointing at those files with the new schema/format/partitioning.

Common use: convert CSV to partitioned Parquet without leaving Athena.

```sql
CREATE TABLE incidents_parquet
WITH (
  format = 'PARQUET',
  parquet_compression = 'SNAPPY',
  external_location = 's3://.../incidents_parquet/',
  partitioned_by = ARRAY['severity']
) AS
SELECT ..., severity  -- partition column LAST
FROM incidents;
```

**Gotchas:**
- Partition columns must be last in the SELECT.
- `external_location` must not already contain data.
- CTAS has a 100-partition limit per query (recognize, don't memorize).

---

## Card A13 — Snappy

**Front**

What is Snappy?

**Back**

A **fast compression algorithm**, open-sourced by Google, commonly used inside Parquet files.

Trade-off it makes: **not the smallest file, but very fast to decompress.** Gzip gives smaller files but takes longer to read back. For query workloads where the same file is read many times, cheap decompression matters more than the last few % of size savings.

Snappy is the near-default for Parquet on AWS.

### Memory line

> Snappy prioritizes read speed over squeeze ratio.

---

## Card A14 — Multiple Parquet copies from one source

**Front**

Can I create multiple Parquet datasets from the same CSV source?

**Back**

Yes, freely — each CTAS is independent:

```text
incidents          — CSV, no partitions (source)
incidents_parquet  — Parquet, partitioned by severity
incidents_parquet_2 — Parquet, partitioned by region + severity
```

Each needs its own `external_location` and creates its own catalog table.

**Trade-off:** each copy is real bytes on S3. Storage cost multiplies. In practice, teams pick **one** partitioning scheme that matches their dominant query pattern rather than keeping many copies.

---

## Exam Pattern to Remember — AWS Section 2

```text
Customer wants to reduce Athena query cost
→ Convert to Parquet + partition on filter columns + Snappy.

Need to query S3 with SQL, least ops overhead
→ Athena, not Redshift.

Need to convert CSV to Parquet in place
→ Athena CTAS (or Glue ETL for custom logic).

Need to discover schema of existing files
→ Glue Crawler.

WHERE clause is "cheaper" on CSV
→ False. Athena scans the whole CSV regardless.

SELECT only 2 columns from CSV
→ Still scans the whole file. Only Parquet skips columns.
```

---

## Part 3 — SageMaker services

Sections 3–5 of the lab. Domains 2, 3, and 4 all lean heavily on SageMaker. Cards will be added as we build each section.

---

## Card S1 — SageMaker at a glance

**Front**

What is SageMaker, and what are its four main workflow concepts?

**Back**

SageMaker is AWS's managed service for the entire ML lifecycle. You hand it your data + code and it handles the compute and infrastructure.

**(a) Training job**
- Spins up a container, trains your model, writes the model artifact to S3, tears the container down.
- **Ephemeral** — bills only while running. Typical run for our lab data = 3–10 minutes.

**(b) Real-time endpoint**
- Persistent HTTPS service that serves predictions live.
- **Bills continuously while it exists**, even if no one calls it. THE cost trap of this exam. Delete when done.

**(c) Batch transform**
- One-off scoring of a large dataset offline. No persistent endpoint.
- Bills only while the job runs. Cheaper than a real-time endpoint when you don't need per-request answers.

**(d) Networking modes**
- **Default** — container can reach the internet (to pull dependencies, etc.).
- **VPC mode** — container runs inside your VPC. You control routing / security groups / NACLs. Higher operational overhead.
- **Network isolation mode** — SageMaker-native flag: container has zero network access. Managed entirely by SageMaker, no VPC plumbing needed. First choice when the requirement is *"no external access + least operational overhead"*.

### Memory line

> Training + endpoint + batch = compute options. Network isolation = built-in lockdown, no VPC plumbing.


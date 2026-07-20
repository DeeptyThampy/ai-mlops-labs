# Wrong-Answer Log

Personalized MLA-C01 review sheet.

- **Rules & Traps** — distilled insight per topic. Skim weekly; drill before exam.
- **Attempts Log** — one entry per question. Compact metadata visible; AWS's full wrong-answer explanations preserved verbatim inside a collapsible block.

**Legend**

| Status | Meaning |
|---|---|
| ✅ | Correct on first try, confident |
| 🟡 | Correct but guessed / unsure — still review |
| ❌ | Wrong |

**Domains** — D1 Data Prep (28%) · D2 Model Dev (26%) · D3 Deploy/Orchestration (22%) · D4 Monitoring/Security (24%)

**How to use**

- After each question: add compact entry to **Attempts Log**, paste AWS's full wrong-option explanations inside the collapsible `<details>` block, then distill 1-3 one-liners into **Rules & Traps**.
- **Weekly**: read only Rules & Traps. ~5 min.
- **Pre-exam (2 weeks out)**: read Rules & Traps, then re-attempt ❌ and 🟡 questions with options hidden. If you miss one again, expand its `<details>` block and re-read AWS's own explanations. That verbatim text is what you're going to need at that moment — that's why it stays in the file.

---

## Rules & Traps

### SageMaker networking [D4]

- **Network isolation mode** — container has zero network access, managed entirely by SageMaker, no VPC plumbing required. First choice when the constraint is *"least operational overhead"* AND *"no external access"*. _(Q1)_
- **VPC-only mode + SG or NACL** — reaches the same end goal, but requires VPC configuration → higher operational overhead. Pick only when other VPC-native controls are needed for reasons beyond just blocking traffic. _(Q1)_
- **VPC interface endpoints** — provide *private access to AWS APIs* (e.g. SageMaker API, SageMaker Runtime) from inside your VPC. They are **not** a resource-access blocker between compute and the internet. Different tool for a different job. _(Q1)_
- **SageMaker Canvas** — no-code ML UI for building models. Not a network control at all. When Canvas appears as an answer to a networking question, it's almost always a distractor. _(Q1)_

### SageMaker model onboarding [D3]

- **BYOC — Bring Your Own Container** — compose a Dockerfile that packages your model + serving code, push to ECR, SageMaker runs it. The universal path for models written in an *unsupported language* (R, custom C++, exotic frameworks). Constraint pattern: *"least operational overhead"* + *"existing models in R/other language"* → BYOC beats rewriting. _(Q2)_
- **Built-in algorithms** — pre-implemented AWS algorithms (XGBoost, Linear Learner, KMeans, etc). They are training/inference implementations for *new* models; NOT a way to onboard *existing* models. If a question says "bring my existing model" and offers "built-in algorithm" — trap. _(Q2)_
- **SageMaker SDK framework helpers** — cover Python frameworks (TensorFlow, PyTorch, sklearn, XGBoost). Do NOT cover R. Translating source language just to use the SDK adds overhead — usually the wrong pick when BYOC is on the table. _(Q2)_
- **SageMaker Canvas onboarding** — Canvas can import a model, but only *after* it's registered in the SageMaker model registry. Not a shortcut for bringing raw model files in. _(Q2)_

### Cross-account access [D4]

- **Cross-account IAM role** — the canonical AWS pattern for granting a *third-party account* access to your resources. Create the role in the *data-owner's* account, put the third-party's account ID in the trust policy, they assume it and receive temporary credentials. Temporary creds work for BOTH programmatic (SDK/CLI) AND console access. _(Q3)_
- **AWS Organizations** — a governance layer for accounts *you own* (billing consolidation, service control policies, OU structure). NOT a mechanism for third-party access. ⚠️ **Trap signal**: if the scenario has "*startup*", "*partner*", "*vendor*", "*third-party*", "*external company*" → Organizations is the wrong tool, even though "multi-account" pattern-matches to it. _(Q3)_
- **S3 resource-based bucket policy** — provides *programmatic* access only. If the requirement includes AWS *Console* access, bucket policy alone is insufficient — need IAM role. Also: bucket policy always lives on the bucket in the *data-owner's* account, not the consumer's. _(Q3)_
- **S3 ACLs** — legacy, basic read/write control at bucket/object level. Do not provide combined programmatic + console access. AWS actively steers away from ACLs in favor of IAM + bucket policies. When ACL and IAM are both options, IAM wins. _(Q3)_
- ⚠️ **Trap phrase to memorize**: *"programmatically AND through the AWS Management Console"* → rules out bucket-policy-only answers. Console access implies temporary credentials → IAM role. _(Q3)_

### Preprocessing orchestration on AWS [D3]

**Canonical serverless preprocessing pattern**: `S3 upload → S3 Event Notification → Step Functions → SageMaker Processing Job → processed artifacts back to S3`. Learn each piece's role so you can spot which combination the question wants. _(Q4)_

- **SageMaker Processing Job** — ML-focused compute. Ships with **pre-built Docker images** for TensorFlow, PyTorch, sklearn, XGBoost, MXNet. You provide a Python script; SageMaker runs it inside a framework-preloaded container against your S3 data. First choice when the task is *"preprocess with TF/PyTorch/etc. with least operational overhead"*. _(Q4)_
- **AWS Glue ETL** — managed ETL for **structured / tabular** data. Python or Scala scripts. Great for CSV/Parquet/JSON transformations feeding a data lake. Does NOT ship with ML framework images — picking Glue when you need TF/PyTorch means installing frameworks yourself → added overhead. _(Q4)_
- **Amazon ECS on Fargate** — general-purpose serverless containers. You bring the Docker image; AWS runs it. Works for ML preprocessing, but you build/maintain the framework container → more overhead than SageMaker Processing. ⚠️ Trap: "serverless and managed" pattern-matches to Fargate, but SageMaker Processing is *more* managed for ML specifically. _(Q4)_
- **AWS Lambda** — short-lived event-driven functions. 15-min timeout, up to 10 GB memory, deployment package size limits. Fine for tiny glue/transforms, NOT for framework-heavy image preprocessing over batches. ⚠️ Trap: writing Lambda to *poll* S3 for new files — use S3 Event Notifications instead, they fire natively. _(Q4)_
- **S3 Event Notifications** — S3 fires an event (ObjectCreated, ObjectRemoved, etc.) to SNS/SQS/Lambda/EventBridge. Native, no polling, near-zero operational overhead. Default answer for "*new file arrives → trigger something*". _(Q4)_
  - **Mental model**: ONE config — *"when X event → send to destination Y."* The destination IS the action-taker; no separate "notify then trigger" step.
  - **Four possible destinations**: SNS · SQS · Lambda · EventBridge. Step Functions is NOT a direct target — you go S3 → EventBridge → Step Functions (modern) or S3 → Lambda → Step Functions (older). Exam usually accepts the shorthand "S3 event → Step Functions" without spelling out the bridge.
- **Step Functions** — serverless workflow orchestrator (state machine). Coordinates multi-service pipelines with retries and error handling. When the answer set contains "trigger + preprocess + train", Step Functions is almost always the orchestrator. _(Q4)_

⚠️ **Meta-trap from Q4**: *"using framework X"* in the stem does NOT mean "avoid AWS-managed services." SageMaker Processing *runs* your TF/PyTorch script inside a pre-built container. The framework requirement is a hint about compute needs, not a constraint against SageMaker. _(Q4)_

### SageMaker Automatic Model Tuning / HPO [D2]

- **AMT (Automatic Model Tuning) / Hyperparameter Tuning Job** — SageMaker automates the search for hyperparameter values (learning rate, depth, etc). You define a search space + objective metric + max jobs; SageMaker runs training jobs in parallel and converges via Bayesian optimization. Hands-on in Section 3 of the lab. _(Q5)_
- **Warm start tuning job** — reuse the results of a *previous* tuning job to seed the new search. Faster convergence + lower compute than starting fresh. A new tuning job (not warm start) throws away prior knowledge. _(Q5)_
- **Warm start type — TRANSFER_LEARNING vs IDENTICAL_DATA_AND_ALGORITHM** — the exam trap:
  - `IDENTICAL_DATA_AND_ALGORITHM` = new tuning job must use the SAME data + algorithm as the parent. Only useful for extending an interrupted job. **Impossible with new data.**
  - `TRANSFER_LEARNING` = flexible — allows new data, new hyperparameter ranges, new algorithm params. The "normal" choice.
  - ⚠️ **Single-phrase decider**: if the stem says *"new data"*, *"updated data"*, *"changed dataset"* → **TRANSFER_LEARNING**, always. _(Q5)_
- **Early stopping — `Auto` vs `max_training_jobs`** — both save compute, but only one uses the objective metric:
  - `early_stopping_type=Auto` — SageMaker kills individual training jobs mid-flight when their objective metric (accuracy, F1, etc.) is below the running median across sibling jobs. **Accuracy-based.**
  - `max_training_jobs` — hard cap on the total count of training jobs the tuner can run. **Count-based.** Does NOT use the metric.
  - ⚠️ **Trap phrase**: *"save compute time if training accuracy is not improving"* → accuracy-based → **early stopping Auto**, NOT max_jobs cap. _(Q5)_

### SageMaker Training Input Modes [D2]

Every SageMaker training job pulls data from S3 to the training container in one of three modes. Switching between them is a single config parameter (`input_mode=`).

- **File mode** (default) — downloads the ENTIRE dataset from S3 to the container's local disk BEFORE training begins. Slow startup, needs local disk for full dataset. Works with everything. _(Q6)_
- **Pipe mode** — STREAMS records from S3 directly into the training algorithm. Fast startup, ~no local disk. But: sequential access only, and not all frameworks/algorithms support it cleanly. _(Q6)_
- **Fast file mode** — hybrid. Training starts as soon as SageMaker identifies the S3 files (metadata only). Files stream on-demand AND get copied to local disk in parallel. Fast startup PLUS random-access file semantics for your code. Needs local disk sized for full dataset. Works with all frameworks. _(Q6)_
- ⚠️ **The exam decision rule for "reduce training time, LEAST operational overhead" on large S3 data** → **fast file mode**. It's a single config change. No new services, no data copies, no code rewrite. _(Q6)_
- ⚠️ **Trap: FSx for Lustre / EFS** — genuinely fast shared file systems, but each is a separate managed service to provision, mount, monitor, and secure → operational overhead. Only pick when the scenario needs shared storage across many concurrent training jobs. _(Q6)_
- ⚠️ **Trap: compressing S3 data** — the decompression step on the training instance usually eats the transfer time savings. Nearly never the "least overhead" answer. _(Q6)_

### SageMaker Clarify — explainability and bias metrics [D4]

Three techniques from Clarify, often confused because two are "feature-focused." The one-word discriminators are **LOCAL vs GLOBAL vs GROUP-FAIRNESS**.

- **Shapley values — LOCAL** — for ONE prediction, decompose that prediction into per-feature contributions. Answers *"Why did the model produce THIS output for THIS row?"* Origin: cooperative game theory. _(Q7)_
- **Partial Dependence Plots (PDPs) — GLOBAL** — for ONE feature, plot the average predicted outcome as that feature varies across its range (holding others integrated over). Answers *"What is the average marginal effect of this feature across the dataset?"* _(Q7)_
- **Difference in Proportions of Labels (DPL) — GROUP FAIRNESS** — compare positive-label rates across sensitive facet groups (region, gender, etc.). A pre-training bias metric. Answers *"Is my training data imbalanced with respect to this group?"* _(Q7)_
- ⚠️ **The Shapley-vs-PDP swap trap** (blurring point): both are feature-focused. The distinction is **scope of the analysis**:
  - Shapley operates on **one prediction**, decomposing it into per-feature contributions.
  - PDP operates on **one feature**, showing its average marginal effect across many predictions.
- **Stem-word decoders** — memorize these:
  - *"contribution of each feature **IN A** prediction"* → **Shapley** _(Q7)_
  - *"difference in the predicted outcome **AS AN input feature changes**"* → **PDP** _(Q7)_
  - *"imbalance of positive outcomes between **facet values**"* → **DPL** _(Q7)_

### SageMaker MLOps features [D4]

Four closely-related services in the "operating models in production" cluster. All four are common exam distractors for each other.

- **Model Monitor** — continuously observes deployed model quality: data drift, model drift, bias drift, feature attribution drift. Runs on a schedule against endpoint traffic. **Use when**: *"gauge model quality in production"*, *"detect drift"*, *"monitor deployed model."* _(Q10)_
- **Data Capture** — a feature *of SageMaker endpoints* (a config flag on deploy). Records inbound requests and outbound predictions to S3, **asynchronously**, without impacting production traffic. **Use when**: *"collect production data for retraining / debugging / monitoring."* Data Capture is often the raw-input mechanism Model Monitor consumes. _(Q10)_
- **Model Registry** — catalog for production models. Versioning, approval workflow, metadata association, CI/CD-driven deployment. **Use when**: *"manage model versions"*, *"approval gate"*, *"CI/CD for models."* NOT for retraining, NOT for data collection. _(Q10)_
- **Experiments** — a Studio feature to automatically track training runs: hyperparameters, metrics, artifacts. Compares run variants. **Use when**: *"track and compare training experiments"*, *"log run metrics and params."* NOT for collecting production data. _(Q10)_
- **Amazon QuickSight** — BI dashboarding tool. Can invoke a SageMaker model for column-level predictions in a dashboard, but is NOT a mechanism for *retraining* or *improving* a model. _(Q10)_
- ⚠️ **Trap decider for retraining/monitoring questions**:
  - *"collect production data → retrain"* → **Data Capture** (raw traffic) → Model Monitor optional to gauge quality first
  - *"detect drift / quality dip"* → **Model Monitor**
  - *"manage model versions / approvals"* → **Model Registry**
  - *"compare training run variants"* → **Experiments**

<!-- Add new topic sections here as questions arrive. Anticipated topics:
     Training jobs [D2] · Endpoints & batch transform [D3] · Feature Store [D1/D2] ·
     Data ingestion — S3/Glue/Athena [D1] · IAM & KMS [D4] · Monitoring & drift [D4] -->

---

## Attempts Log

### Q1 — SageMaker network isolation for internal-only model [D4] ✅

- **Stem**: 3rd-party recommendation system on SageMaker; must be internal; training + inference containers cannot access customer VPC resources or the internet. Constraint: **least operational overhead**.
- **Options**: (A) network isolation mode · (B) Canvas + VPC interface endpoint · (C) VPC-only + SGs · (D) VPC-only + NACLs
- **My answer**: A → **Correct**: A
- **Trap phrase**: *"least operational overhead"*
- **Rules surfaced**: [SageMaker networking](#sagemaker-networking-d4)

<details>
<summary>AWS explanations for the wrong options (click to expand)</summary>

**B. Use SageMaker Canvas. Configure an Amazon VPC interface endpoint to block internet access.**

SageMaker Canvas provides a no-code ML interface to create models. SageMaker Canvas does not provide a separate network protection mechanism. A VPC interface endpoint provides private communication between a VPC and the SageMaker API or Amazon SageMaker Runtime. However, a VPC interface endpoint does not block access to resources within a customer's VPC.

*Learn more about network isolation.*

**C. Configure SageMaker in VPC only mode. Configure security groups to block internet access.**

You can use a VPC to launch AWS resources within your own isolated virtual network. Security groups are a security control that you can use to control access to your AWS resources. You can protect your data and resources by managing security groups and restricting internet access from your VPC. However, this solution requires additional network configuration and therefore increases operational overhead.

**D. Configure SageMaker in VPC only mode. Configure a network access control list (network ACL) to block internet access.**

You can use a VPC to launch AWS resources within your own isolated virtual network. You can use a network ACL to allow or deny inbound and outbound traffic to subnets within a VPC. This solution requires additional networking configuration to create and maintain the VPC. Therefore, this solution requires additional operational overhead.

</details>

---

### Q2 — Bringing existing R models into SageMaker [D3] ✅

- **Stem**: Company has ML models built in R over several years. Wants to use SageMaker to deploy + monitor them. Constraint: **least operational overhead**.
- **Options**: (A) SageMaker built-in algorithm · (B) R Dockerfile → BYOC · (C) translate source to Python + SDK · (D) SageMaker Canvas
- **My answer**: B → **Correct**: B
- **Trap phrase**: *"least operational overhead"* — same phrase as Q1; recurring exam signal to prefer AWS-managed / language-native paths over hand-plumbed alternatives.
- **Rules surfaced**: [SageMaker model onboarding](#sagemaker-model-onboarding-d3)

<details>
<summary>AWS explanations (click to expand)</summary>

**B (correct). Compose an R Dockerfile to bring existing R models as containers into SageMaker.**

You can use the SageMaker SDK to bring existing ML models that are written in R into SageMaker by using the "bring your own container" option. This solution requires the least operational overhead because you only need to compose a Dockerfile for each existing model.

**A. Use a SageMaker built-in algorithm to bring R models into SageMaker.**

SageMaker built-in algorithms are common ML algorithms that AWS provides and maintains. There are no SageMaker built-in algorithms to bring existing R models into SageMaker.

**C. Translate the source code to Python. Use the SageMaker SDK to bring Python models into SageMaker.**

The SageMaker SDK includes functions that you can use to onboard existing Python models that are written in supported frameworks. Then you can bring the existing Python models into SageMaker. However, this solution requires you to translate the source code from R to Python. Therefore, this solution requires additional operational overhead.

**D. Use SageMaker Canvas to bring R models into SageMaker.**

SageMaker Canvas is a no-code ML service. You can use SageMaker Canvas to import existing models to SageMaker. However, you must register the models in the SageMaker model registry before you can import the models into SageMaker Canvas.

</details>

---

### Q3 — Delegating S3 data access to a third-party (startup) [D4] ❌

- **Stem**: Company wants to delegate ML model development to an ML startup. Startup has its own AWS account. Company's training data is in S3. Access needed **both programmatically and through the AWS Management Console**.
- **Options**: (A) cross-account IAM role · (B) S3 ACL in company account · (C) resource-based bucket policy in startup's account · (D) AWS Organizations OU
- **My answer**: D → **Correct**: A
- **Trap that got me**: "multi-account" → AWS Organizations. But Organizations governs accounts *you own*, not third-party access. The word "*startup*" (external company) should have flipped the mental model toward cross-account IAM role.
- **Trap phrase**: *"programmatically AND through the AWS Management Console"* — the AND rules out programmatic-only mechanisms (bucket policy). Console access ⇒ temporary credentials ⇒ IAM role.
- **Rules surfaced**: [Cross-account access](#cross-account-access-d4)

<details>
<summary>AWS explanations (click to expand)</summary>

**A (correct). Create a role in the company's AWS account. Assume this IAM role from the ML startup's AWS account.**

IAM roles provide permissions to AWS services or users to access AWS resources securely. These roles are used to delegate access within an AWS account or across different AWS accounts. When assuming an IAM role, a user or service temporarily takes on the permissions and policies that are associated with that role. This action gives the user or service the ability to perform actions on AWS resources that are based on the permissions that are granted by the role without the need to use long-term credentials, such as access keys.

To provide access to a user in one AWS account (the ML startup's account) to resources in another AWS account (the company's account), you must create an IAM role in the company's account with the necessary permissions and trust relationship and then specify the ML startup account's ID. The user in the client account can then assume the role and obtain temporary credentials for secure cross-account access. Configuring cross-account IAM roles is the only way to provide both programmatic and console access to S3 buckets across accounts.

**B. Create an ACL in the company's AWS account.**

IAM policies on AWS define permissions for users, groups, or roles. These policies also specify the allowed or denied actions on resources, which provides fine-grained access control. ACLs are used in Amazon S3 to manage basic read and write permissions for buckets and objects. ACLs determine which AWS accounts or users have access to specific S3 resources at the bucket and object levels, which provides a basic level of access management. IAM policies and ACLs do not meet the requirements because IAM policies and ACLs do not offer both programmatic and console access.

**C. Create a resource-based bucket policy in the ML startup's AWS account.**

Resource-based bucket policies, specifically for S3 buckets, give you the ability to control access to your bucket's resources. These policies are attached directly to the S3 bucket. IAM policies and resource-based bucket policies are powerful for access control. However, these policies provide only programmatic access. In this scenario, IAM roles with cross-account access are a more suitable solution. Cross-account IAM roles secure the delegation of permissions and temporary credentials for both programmatic and console access. Additionally, if you use a resource-based bucket policy to access data, the policy should be set up on the bucket in the company's account where the data is stored.

**D. Set up AWS Organizations in the company's account and add the ML startup's account to an existing organizational unit (OU) in the organization.**

Organizations is a service that gives you the ability to consolidate multiple AWS accounts into an organization that you create and centrally manage. Organizations provides features for policy-based management, consolidated billing, and OU structure. Organizations is designed for managing accounts within the same administrative domain and is not designed for securely sharing data with a third-party account.

</details>

---

### Q4 — Weekly image preprocessing pipeline with TF/PyTorch [D3] ❌

- **Stem**: Weekly image data lands in S3; must preprocess (resize, color correct, augment) using TensorFlow / PyTorch; write processed data back as TFRecords; model retrained weekly. **Select THREE.** Constraint: **least operational overhead**.
- **Options**: (A) Glue ETL · (B) ECS Fargate · (C) SageMaker Processing Job · (D) Lambda polling S3 · (E) S3 Event Notifications · (F) Step Functions
- **My picks (per paste)**: B, C, E → **Correct set**: C, E, F. Missed F, false-picked B.
- **Trap that got me**: read *"using frameworks such as TF/PyTorch"* as *"can't use SageMaker"* → assumed we had to bring our own container → picked Fargate. Actually SageMaker Processing ships with pre-built TF/PyTorch containers, so it's the *most* framework-native answer.
- **Trap phrase**: *"using frameworks such as TensorFlow and PyTorch"* — this is a hint about compute capability required, not a constraint against SageMaker.
- **Rules surfaced**: [Preprocessing orchestration on AWS](#preprocessing-orchestration-on-aws-d3)

<details>
<summary>AWS explanations (click to expand)</summary>

**C (correct). Create a processing job to process the data on Amazon SageMaker.**

You can use SageMaker processing jobs for data processing, analysis, and ML model training. You can use SageMaker processing jobs to perform transformations on images by using a script in multiple programming languages. In this scenario, you can run the custom code on data that is uploaded to Amazon S3. SageMaker processing jobs provide ready-to-use Docker images for popular ML frameworks and tools. Additionally, SageMaker offers built-in support for various frameworks including TensorFlow, PyTorch, Apache MXNet, scikit-learn, XGBoost, and more.

**E (correct). Enable Amazon S3 Event Notifications to be invoked when new files are uploaded to the S3 bucket.**

You can use Amazon S3 Event Notifications to receive notifications when predefined events occur in an S3 bucket. You can use event notifications to invoke an event. In this scenario, you can use the event to run a step function as the destination.

**F (correct). Use AWS Step Functions to orchestrate the steps.**

Step Functions is a serverless orchestration service that you can use to coordinate and sequence multiple AWS services into serverless workflows. In this scenario, the predefined workflow can include a processing job.

**A. Use AWS Glue extract, transform, and load (ETL) jobs to process the images.**

AWS Glue is a fully managed ETL service that you can use to prepare and transform data for analysis and storage. You can use AWS Glue ETL jobs to define and perform transformations on your data. You can create Python or Scala scripts to perform the necessary transformations. Then, AWS Glue will manage the underlying infrastructure to run the job. AWS Glue supports data processing by using ETL jobs. However, AWS Glue does not provide ready-to-use Docker images for popular ML frameworks such as TensorFlow and PyTorch. This solution would require custom scripts and additional operational overhead to manually import the necessary frameworks.

**B. Use Amazon ECS on AWS Fargate to process the data.**

Amazon ECS on Fargate is a serverless container orchestration service. You can use Amazon ECS on Fargate to run containers without the need to manage the underlying infrastructure. You can use Amazon ECS on Fargate to process data. However, this solution requires more operational overhead than a solution that runs custom code by using a SageMaker processing job.

**D. Use an AWS Lambda function to detect new uploaded files in Amazon S3.**

Lambda is a serverless compute service that you can use to run code without the need to provision or manage servers. Lambda is suitable for event-driven architectures and microservice applications. A solution that writes a custom Lambda function to detect new file uploads to Amazon S3 would require the function to run at all times. Instead, you can use Amazon S3 Event Notifications to invoke running the step function.

</details>

---

### Q5 — Warm start HPO with new data + accuracy-based early stopping [D2] ❌

- **Stem**: Data scientist wants to retrain a previously-AMT-tuned model using **new data**. Wants to (a) reuse previous tuning-job results for efficiency, (b) **save compute if training accuracy is not improving**.
- **Options**: (A) warm start TRANSFER_LEARNING + early stopping Auto · (B) NEW tuning job + max training jobs cap · (C) warm start TRANSFER_LEARNING + max training jobs cap · (D) warm start IDENTICAL_DATA_AND_ALGORITHM + decrease training jobs + early stopping Auto
- **My answer**: B → **Correct**: A
- **Trap that got me**: no prior AMT / warm-start knowledge; guessed. All four options looked plausible without knowing the mechanics.
- **The two-clause decider**: stem has *"new data"* AND *"save compute if accuracy is not improving"*. Two independent phrases, each rules out three options:
  - *"new data"* → must be `TRANSFER_LEARNING` (not IDENTICAL) → kills D. Not-warm-start also throws away prior knowledge → kills B.
  - *"if accuracy is not improving"* → must be `early_stopping=Auto` (accuracy-based) — NOT `max_training_jobs` (count-based) → kills B and C.
  - Only A satisfies both. ✅
- **Rules surfaced**: [SageMaker Automatic Model Tuning / HPO](#sagemaker-automatic-model-tuning--hpo-d2)
- **Lab coverage**: this concept gets hands-on in Section 3 of the lab (SageMaker Training + AMT + warm start).

<details>
<summary>AWS explanations (click to expand)</summary>

**A (correct). Run a warm start tuning job by setting the type to TRANSFER_LEARNING. Choose the Auto setting for the early stopping parameter.**

SageMaker AMT searches for the most suitable version of a model by running training jobs based on the algorithm and objective criteria. You can use a warm start tuning job to use the results from previous training jobs as a starting point. You can set the early stopping parameter to Auto to enable early stopping. SageMaker can use early stopping to compare the current objective metric (accuracy) against the median of the running average of the objective metric. Then, early stopping can determine whether or not to stop the current training job. The TRANSFER_LEARNING setting can use different input data, hyperparameter ranges, and other hyperparameter tuning job parameters than the parent tuning jobs.

**B. Run a hyperparameter tuning job with an updated input data configuration. Configure the maximum number of training jobs that can be run before the tuning job is stopped.**

SageMaker AMT searches for the most suitable version of a model by running training jobs based on the algorithm and objective criteria. A new hyperparameter tuning job would not use previous tuning job results. A solution that sets the maximum number of training jobs saves compute time by running only a limited number of jobs. However, this feature does not use model accuracy as the objective.

**C. Run a warm start tuning job by setting the type to TRANSFER_LEARNING. Configure the maximum number of training jobs that can be run before the tuning job is stopped.**

SageMaker AMT searches for the most suitable version of a model by running training jobs based on the algorithm and objective criteria. You can use a warm start tuning job to use the results from previous training jobs as a starting point. The TRANSFER_LEARNING setting can use different input data, hyperparameter ranges, and other hyperparameter tuning job parameters than the parent tuning jobs. A solution that sets the maximum number of training jobs saves compute time by running only a limited number of jobs. However, this feature does not use model accuracy as the objective.

**D. Run a warm start tuning job by setting the type to IDENTICAL_DATA_AND_ALGORITHM, and decrease the total number of training jobs. Choose the Auto setting for the early stopping parameter.**

SageMaker AMT searches for the most suitable version of a model by running training jobs based on the algorithm and objective criteria. You can use a warm start tuning job to use the results from previous training jobs as a starting point. You can set the early stopping parameter to Auto to enable early stopping. SageMaker can use early stopping to compare the current objective metric (accuracy) against the median of the running average of the objective metric. Then, early stopping can determine whether or not to stop the current training job. However, the IDENTICAL_DATA_AND_ALGORITHM setting assumes the same input data and training image as the previous tuning jobs. Therefore, this solution would not be suitable for a new dataset. To decrease the total number of training jobs would save compute time. However, this solution does not use model accuracy as the objective.

</details>

---

### Q6 — Reducing SageMaker training time for large S3 dataset [D2] ❌

- **Stem**: k-means clustering on SageMaker, 100 GB dataset in S3 (10 files × 10 GB). Training taking longer than expected. Reduce training time. Constraint: **least operational overhead**.
- **Options**: (A) FSx for Lustre + copy from S3 · (B) SageMaker default EFS + copy from S3 · (C) Compress dataset in S3, decompress on instance · (D) **Fast file mode** with sufficient local storage
- **My answer**: C → **Correct**: D
- **Trap that got me**: no prior knowledge of SageMaker input modes (file / pipe / fast file). Compressing sounded intuitively "faster transfer" but adds a decompression step that usually eats the savings.
- **The killer distinction**: fast file mode is a **single config parameter change** (`input_mode="FastFile"`). Everything else adds a service (FSx, EFS) or a preprocessing step (compression). "Least operational overhead" almost always favors the config-only option.
- **Rules surfaced**: [SageMaker Training Input Modes](#sagemaker-training-input-modes-d2)
- **Lab coverage**: Section 3 will add a hands-on comparing file mode vs fast file mode with CloudWatch timing.

<details>
<summary>AWS explanations (click to expand)</summary>

**D (correct). Set the input mode to fast file mode in the training configuration in SageMaker. Ensure that the training instance has enough storage capacity for the entire dataset.**

Input modes include file mode, pipe mode, and fast file mode. File mode downloads training data to a local directory in a Docker container. Pipe mode streams data directly to the training algorithm. Therefore, pipe mode can lead to better performance. Fast file mode provides the benefits of both file mode and pipe mode. For example, fast file mode gives SageMaker the flexibility to access entire files in the same way as file mode. Additionally, fast file mode provides the better performance of pipe mode.

Before you begin training, fast file mode identifies S3 data source files. However, fast file mode does not download the files. Instead, fast file mode gives the model the ability to begin training before the entire dataset has finished loading. Therefore, fast file mode decreases the startup time. As the training progresses, the entire dataset will load. Therefore, you must have enough space within the storage capacity of the training instance. This solution provides an update to only a single parameter and does not require any code changes. Therefore, this solution requires the least operational overhead.

**A. Create an Amazon FSx for Lustre file system. Copy the dataset from Amazon S3 to the FSx for Lustre file system. Set the file system as the model's data source.**

FSx for Lustre is a managed, high-performance file system that provides fast processing of workloads. FSx for Lustre could reduce the training time. However, this solution requires you to monitor system health and manage security access controls. Therefore, this solution requires additional operational overhead.

**B. Copy the dataset from Amazon S3 to the SageMaker domain's default Amazon Elastic File System (Amazon EFS) file system. Set the file system as the model's data source.**

Amazon EFS is managed elastic file storage system that can scale on demand as you add or remove files. Amazon EFS could reduce the training time. However, this solution requires you to monitor system health and manage security access controls. Therefore, this solution requires additional operational overhead.

**C. Compress the dataset in the S3 bucket. Ensure that the training instance has enough storage capacity for both the compressed and decompressed dataset.**

A solution that compresses the data will reduce the data transfer time. However, to decompress the data adds extra steps before training can begin. The extra steps might add more time to the process than the possible reduction in time from the compression. To use fast file mode would require less operational overhead than this solution.

</details>

---

### Q7 — Matching Clarify explainability/bias techniques to use cases [D4] ❌

- **Stem**: Match three techniques (Shapley values, PDPs, DPL) — all from SageMaker Clarify — to three use cases.
- **Use cases**:
  1. Identify the difference in the predicted outcome as an input feature changes
  2. Quantify the contribution of each feature in a prediction
  3. Measure the imbalance of positive outcomes between different facet values
- **My matches**: 1→Shapley, 2→PDPs, 3→DPL → **Correct**: 1→PDPs, 2→Shapley, 3→DPL
- **Trap that got me**: swapped Shapley and PDPs. Both operate on features so they blurred. Didn't know the local-vs-global distinction.
- **The killer distinction — memorize**:
  - **Shapley = LOCAL** (per prediction: *"why THIS prediction?"*) → contribution of features **IN a** prediction
  - **PDP = GLOBAL** (per feature: *"what does varying X do to predictions on average?"*) → predicted outcome **as** feature changes
  - **DPL = GROUP FAIRNESS** → imbalance across facet values (bias metric)
- **Rules surfaced**: [SageMaker Clarify — explainability and bias metrics](#sagemaker-clarify--explainability-and-bias-metrics-d4)
- **Lab coverage**: Section 5 (Domain 4) will run a Clarify processing job on the trained incident model, view actual Shapley reports + PDPs in Studio, and generate a DPL report on `region`.

<details>
<summary>Definitions and use-case mapping (click to expand)</summary>

**Shapley values** — from cooperative game theory. For a *single prediction*, decompose the prediction into per-feature contributions (positive or negative). Answers *"For this specific row, why did the model produce this output?"* This is per-prediction local attribution.

Correct match: use case 2 — *"Quantify the contribution of each feature in a prediction."*

**Partial Dependence Plots (PDPs)** — for a *single feature*, plot the average predicted value across the range of that feature, with all other features integrated over. Shows the feature's average marginal effect across the dataset. Global, not per-row.

Correct match: use case 1 — *"Identify the difference in the predicted outcome as an input feature changes."*

**Difference in Proportions of Labels (DPL)** — a fairness metric. Given a sensitive facet (e.g., region, gender), compare the positive-label rates across groups. Pre-training bias detection.

Correct match: use case 3 — *"Measure the imbalance of positive outcomes between different facet values."*

</details>

---

### Q10 — Retraining a production model with production data [D4] ✅

- **Stem**: ML model in production. Improve model quality without impacting performance. Also retrain with additional data. Constraint: **least development effort**.
- **Options**: (A) Model Registry to collect new data · (B) Experiments to collect new data · (C) **Model Monitor + Data Capture on the endpoint** · (D) QuickSight to make predictions and retrain from results
- **My answer**: C → **Correct**: C
- **Why C wins**: Data Capture is the built-in endpoint feature specifically for recording inbound requests + outbound predictions to S3 — asynchronously, no impact on prod traffic. That's exactly the "additional data for retraining" mechanism. Model Monitor then uses that captured data to detect quality issues. Both are configured on the endpoint — minimal dev effort.
- **Trap phrases that discriminate**:
  - *"collect new data"* → Data Capture (raw traffic recorder), NOT Model Registry (catalog) or Experiments (training-run tracker)
  - *"without impacting the model's performance"* → the "runs asynchronously" property of Data Capture
- **Rules surfaced**: [SageMaker MLOps features](#sagemaker-mlops-features-d4)

<details>
<summary>AWS explanations (click to expand)</summary>

**C (correct). Use Amazon SageMaker Model Monitor. Enable Data Capture on the endpoint, and use that data for model re-training.**

You can use SageMaker Model Monitor to effectively gauge model quality. Data Capture is a feature of SageMaker endpoints. You can use Data Capture to record data that you can then use for training, debugging, and monitoring. Then, you could use the new data that is captured by Data Capture to re-train the model. Data Capture runs asynchronously without impacting production traffic.

**A. Use Amazon SageMaker Model Registry to collect new data. Use the new data for re-training.**

You can use SageMaker Model Registry to create a catalog of models for production, to manage the versions of a model, and to associate metadata to the model. Additionally, SageMaker Model Registry can manage approvals and automate model deployment for continuous integration and continuous delivery (CI/CD). You would not use SageMaker Model Registry for model re-training.

**B. Use Amazon SageMaker Experiments to collect new data. Use the new data to re-train the model.**

SageMaker Experiments is a feature of SageMaker Studio that you can use to automatically create ML experiments by using different combinations of data, algorithms, and parameters. You would not use SageMaker Experiments to collect new data for model re-training.

**D. Use Amazon QuickSight to make predictions for the model. Re-train the model based on the prediction results.**

You can use QuickSight to make predictions for a column in a model dataset. However, you would not use QuickSight to improve the quality of a model.

</details>

---

<!-- Copy this template block (without the outer HTML comment wrapper) for each new attempt. -->
<!--
### Qn — one-line topic [Dx] ✅/🟡/❌

- **Stem**: (1-2 sentence summary of the scenario + the constraint qualifier)
- **Options**: (A) ... · (B) ... · (C) ... · (D) ...
- **My answer**: X → **Correct**: Y
- **Trap phrase**: (the qualifier that decided it, if any — e.g. "least operational overhead")
- **Rules surfaced**: (link to Rules & Traps section, or "new — added under [topic]")

<details>
<summary>AWS explanations for the wrong options (click to expand)</summary>

**B. ...**
(paste AWS text verbatim)

**C. ...**
(paste AWS text verbatim)

**D. ...**
(paste AWS text verbatim)

</details>

Then distill the takeaway into 1-3 bullets in Rules & Traps above, tagged _(Qn)_.
-->

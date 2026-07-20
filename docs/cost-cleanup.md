# Cost & Cleanup

**Golden rule**: the expensive things in this lab are **always-on compute** — SageMaker endpoints and Studio notebook instances. Data storage (S3), serverless query (Athena), and event glue (Lambda, Step Functions, S3 Events, EventBridge) are pennies.

Realistic cost for the full lab if you follow the daily habit: **$10–25 total.** The bad case (SageMaker endpoint left running for a week) is **$50–100**. All the difference is discipline.

---

## The daily habit that prevents sticker shock

**Every day you work on this lab — 30 seconds, non-negotiable:**

1. Open [Cost Explorer](https://console.aws.amazon.com/cost-management/home#/cost-explorer). Look at yesterday's total. If it's more than $2 and you didn't run a training job or endpoint, investigate.
2. Open [Billing Home → Bills](https://console.aws.amazon.com/billing/home). Skim the "By service" section. Any line item you don't recognize = investigate.

**Every night before you close your laptop:**

Run through the "Before closing my laptop" checklist at the bottom of this file. It takes about 90 seconds.

**Every week (Sunday works):**

Open the [Budgets console](https://console.aws.amazon.com/billing/home#/budgets) and confirm your alarms are still armed. Confirm your account-total bill vs where you expect to be. If you're at week 2 and already at $30, something is running that shouldn't be.

Do all three. The two-minute daily habit prevents the two-hour-of-panic monthly bill.

---

## Prices at a glance (US-East-1, approximate)

Round numbers so you can eyeball the risk while working. See the [SageMaker pricing page](https://aws.amazon.com/sagemaker/pricing/) for exact figures.

### Compute (bills while running or provisioned)

| Resource | Instance | Cost / hour | Cost / day | Cost / month | Bill while... |
|---|---|---|---|---|---|
| SageMaker training job | `ml.m5.large` | ~$0.12 | — | — | job is running (usually 3-10 min) |
| SageMaker training job | `ml.m5.xlarge` | ~$0.23 | — | — | same |
| **SageMaker real-time endpoint** | `ml.m5.large` | **~$0.12** | **~$2.76** | **~$84** | **endpoint EXISTS. Delete it.** |
| SageMaker batch transform | `ml.m5.large` | ~$0.12 | — | — | job is running only |
| SageMaker Processing job | `ml.m5.large` | ~$0.12 | — | — | job is running only |
| **Studio notebook** | `ml.t3.medium` | **~$0.06** | **~$1.34** | **~$40** | **notebook is running. Shut it down.** |
| Studio Domain itself | — | free | — | — | never bills — instances inside it do |

### Storage / query (pennies, essentially free at our data volume)

| Resource | Rate | Our expected usage | Cost |
|---|---|---|---|
| S3 Standard storage | $0.023 / GB-month | ~50 MB total | << $0.01 / month |
| S3 requests | $0.005 / 1K PUT, $0.0004 / 1K GET | thousands | ~$0.01 |
| Glue Crawler | $0.44 / DPU-hr, 10-min minimum | 2-5 crawls | $0.07 × 2-5 = $0.14–0.36 |
| Glue Data Catalog | first 1M objects free | ~10 objects | $0 |
| Athena | $5 / TB scanned | scan ~10 MB per query | < $0.001 per query |
| CloudWatch Logs | 5 GB / month free | << 1 GB | $0 |
| Lambda | 1M free requests / month | dozens | $0 |
| Step Functions Standard | 4K free transitions / month | hundreds | $0 |

### Cost traps to actively avoid

| Resource | Cost | Rule |
|---|---|---|
| **NAT Gateway** | **$32 / month + $0.045 / GB** just to exist | ⚠️ **Never provision one for this lab.** Use S3 gateway endpoints (free) if you need private routing. |
| KMS customer-managed key | $1 / month per key | Only create one if a section requires it; schedule for deletion when done. AWS-managed keys are free. |
| SageMaker Serverless Inference | pay-per-inference-second | Fine, but easy to forget the *provisioned* variant. Real-time endpoints are the trap, not serverless. |
| Elastic IP (unattached) | $3.60 / month | If you accidentally allocate one and detach — release it. |

---

## Guardrails to set up BEFORE Section 2

Do these once, then forget about them (they alert you if anything goes sideways).

### 1. Budgets alarm — 5 minutes, free

1. Open the [Budgets console](https://console.aws.amazon.com/billing/home#/budgets).
2. Click **Create budget** → **Customize (advanced)** → **Cost budget** → Next.
3. **Budget name**: `mla-c01-lab-monthly`
4. **Period**: Monthly. **Budget amount**: **$10** fixed. Next.
5. **Alert threshold 1**: 80% of actual (i.e. $8 actual). Email = your Gmail.
6. **Alert threshold 2**: 100% of actual ($10). Same email.
7. (Optional) **Alert threshold 3**: 100% of *forecasted*. Same email. This one warns you *before* you hit the limit.
8. Save.

Then create a second budget:

1. Same steps, but **Budget amount = $25**, alerts at 80% and 100% actual. This is your "something is definitely wrong" trigger.

Both budgets are free. Alarms fire via email — check your Gmail promptly if one comes in.

### 2. Cost Explorer — enable once

1. Open [Cost Explorer](https://console.aws.amazon.com/cost-management/home#/cost-explorer).
2. Click **Launch Cost Explorer**. It takes ~24 hours to become useful (needs a day of data).
3. Bookmark the URL. This is your daily 30-second dashboard.

### 3. Billing email — verify it's yours

1. Open [Account Settings](https://console.aws.amazon.com/billing/home#/account).
2. Confirm "Alternate contacts → Billing" is set to your Gmail (`deepty.thampy@gmail.com`). If your Gmail can't receive AWS bill emails, you can't be warned.

---

## Section-by-section teardown

These are the commands to run at the end of each section (or when switching to another section). Filled in as we build each section.

### Section 2 — S3 + Glue + Athena

Placeholders — replace with your actual names when created:

```bash
export BUCKET="mla-c01-lab-<your-suffix>"
export GLUE_DB="incidents_db"
export CRAWLER="incidents_crawler"

# Empty and delete the bucket
aws s3 rm s3://$BUCKET --recursive
aws s3 rb s3://$BUCKET

# Delete the crawler and Glue database (drops all catalog metadata)
aws glue delete-crawler --name $CRAWLER
aws glue delete-database --name $GLUE_DB

# Athena workgroup default is fine — no separate cleanup needed unless you created one
```

### Section 3 — SageMaker Training + AMT

```bash
# Training and tuning jobs stop when they finish — no persistent bill. But:
# - Delete their outputs from S3 if you don't need them:
aws s3 rm s3://$BUCKET/models/ --recursive

# - Studio notebook must be MANUALLY stopped:
#   Open Studio → Kernel Sessions & Terminals → Shut down all
#   Then in the Studio UI top-right, choose "Shutdown all" for the app.
#   Verify no notebook instance is running (there should be no "Running" status).
```

### Section 4 — Endpoint + Batch + Lambda + Step Functions

⚠️ **This is the section with the highest cost risk. Run these EVERY time you finish a work session, not just at section-end.**

```bash
export ENDPOINT="incident-risk-endpoint"

# 🔴 CRITICAL: delete the real-time endpoint
aws sagemaker delete-endpoint --endpoint-name $ENDPOINT
aws sagemaker delete-endpoint-config --endpoint-config-name $ENDPOINT
aws sagemaker delete-model --model-name $ENDPOINT-model

# Confirm nothing is left
aws sagemaker list-endpoints --status-equals InService
# ↑ Should print an empty list. If not, delete anything that appears.

# Lambda, Step Functions, EventBridge rules — free at our volume, but tidy up anyway:
aws lambda delete-function --function-name <your-lambda-name>
aws stepfunctions delete-state-machine --state-machine-arn <arn>
```

### Section 5 — CloudWatch + IAM + KMS + Clarify

```bash
# CloudWatch log groups — free at our volume, but delete for cleanliness:
aws logs delete-log-group --log-group-name /aws/sagemaker/TrainingJobs
aws logs delete-log-group --log-group-name /aws/lambda/<your-fn>

# KMS keys cost $1/mo. Schedule deletion (7-30 day waiting window required):
aws kms schedule-key-deletion --key-id <key-id> --pending-window-in-days 7

# IAM roles are free — leave or delete based on preference
```

---

## Before closing my laptop — nightly checklist

⭐ **Print or bookmark this. Do it every night you worked on the lab.**

```
[ ] Any SageMaker endpoint still running?
    aws sagemaker list-endpoints --status-equals InService
    ↳ If yes: delete it.

[ ] Any Studio notebook / app still running?
    Open Studio → look for "Running" status in top bar
    ↳ If yes: Shutdown all.

[ ] Any training/processing/tuning job still running?
    aws sagemaker list-training-jobs --status-equals InProgress
    aws sagemaker list-processing-jobs --status-equals InProgress
    aws sagemaker list-hyper-parameter-tuning-jobs --status-equals InProgress
    ↳ If yes and it's supposed to be running, fine. If accidental, stop it.

[ ] Any FSx / EFS mount created that you don't need?
    aws fsx describe-file-systems
    ↳ If yes and unused: delete.

[ ] Any elastic IP allocated but unattached?
    aws ec2 describe-addresses --query "Addresses[?AssociationId==null]"
    ↳ If yes: release.
```

If all five checks come back empty, you can close your laptop knowing tomorrow's bill won't move meaningfully.

---

## If you see a surprise charge

1. **Don't panic** — AWS bills are almost always correctable if caught in the same billing cycle.
2. Open Cost Explorer, group by **Service**, look at yesterday's spend to isolate what's costing money.
3. Group by **Usage Type** next — this tells you *what within the service* (e.g., `SageMaker:EndpointUsage` vs `SageMaker:TrainingUsage`).
4. Delete the offending resource immediately using the section commands above.
5. If the total surprise is > $50, open a support case: [AWS Support → Create case](https://console.aws.amazon.com/support/home#/case/create) → **Account and billing** → describe as "unintended lab resource left running." AWS is usually generous with one-time credits for genuine oversights on new accounts, especially exam-prep contexts. Not guaranteed — but worth asking.

---

## Recap of what "disciplined" means in practice

- Budgets alarms set to $10 and $25 → you get emailed early.
- Cost Explorer bookmarked → you glance daily.
- Nightly checklist run → nothing bills overnight.
- Endpoints deleted immediately after each experiment → no $84/month surprise.
- No NAT Gateway → no $32/month surprise.
- Section teardown commands run at end of each section → no forgotten resources.

Follow this and the whole lab should sit under $25. Skip these and you can hit $100 without meaning to.

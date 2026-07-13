# Cost & Cleanup

Golden rule: **the expensive things in this lab are always-on compute** — SageMaker
endpoints and notebook instances. Data storage (S3) and serverless query (Athena) are cheap.

## What costs money (by section)
| Section | Resource | Cost driver | Danger level |
|---|---|---|---|
| 1 (local) | none | — | none |
| 2 | S3 storage | GB-months | 💲 low |
| 2 | Athena | TB scanned | 💲 low (Parquet/partitions) |
| 2 | Glue crawler | crawler-minutes + DPU | 💲 low |
| 3 | SageMaker **training job** | instance-seconds (ephemeral) | 💲 low-med |
| 4 | SageMaker **real-time endpoint** | instance-HOURS, always on | 🔴 HIGH |
| 4 | SageMaker notebook instance | instance-hours, always on | 🔴 HIGH |

## Standing habits
- Set an **AWS Budget** with an email alert *before* creating anything (Section 5, but do it now).
- Prefer **batch transform** over a real-time endpoint while learning — it spins up, runs, spins down.
- **Delete endpoints the moment you're done.** This is the #1 surprise-bill source in SageMaker.

## Cleanup
Run `scripts/cleanup.sh` (added per section). Each AWS resource we create gets a
matching delete command documented in the section where it's introduced.

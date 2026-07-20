# Wrong-Answer Log

Personalized MLA-C01 review sheet.

- **Rules & Traps** — distilled insight per topic. Skim weekly; drill before the exam.
- **Attempts Log** — one compact record per question. Provenance for each rule; use to re-test yourself.

**Legend**

| Status | Meaning |
|---|---|
| ✅ | Correct on first try, confident |
| 🟡 | Correct but guessed / unsure — still review |
| ❌ | Wrong |

**Domains** — D1 Data Prep (28%) · D2 Model Dev (26%) · D3 Deploy/Orchestration (22%) · D4 Monitoring/Security (24%)

**How to use this file**

- After each Skill Builder / TD / section quiz question, add an entry to **Attempts Log** in the compact format shown.
- Extract the one-line takeaway into **Rules & Traps** under the right topic. Tag with the source Q number.
- **Weekly**: read only the Rules & Traps section. 5 minutes.
- **Week before the exam**: read Rules & Traps, then re-attempt every ❌ and 🟡 question by stem (options hidden).

---

## Rules & Traps

### SageMaker networking [D4]

- **Network isolation mode** — container has zero network access, managed entirely by SageMaker, no VPC plumbing required. First choice when the constraint is *"least operational overhead"* AND *"no external access"*. _(Q1)_
- **VPC-only mode + SG or NACL** — same end goal, but requires VPC configuration → higher operational overhead. Only pick when you also need VPC-native controls for other reasons. _(Q1)_
- **VPC interface endpoints** — provide *private access to AWS APIs* from inside your VPC. They are **not** a resource-access blocker between compute and internet. Different tool. _(Q1)_
- **SageMaker Canvas** — no-code ML UI. Not a network control. If Canvas appears as the answer to a networking question, it's usually a distractor. _(Q1)_

<!-- Add new topic sections here as questions arrive. Suggested topics to expect:
     Training jobs [D2] · Endpoints & batch transform [D3] · Feature Store [D1/D2] ·
     Data ingestion (S3/Glue/Athena) [D1] · IAM & KMS [D4] · Monitoring & drift [D4] -->

---

## Attempts Log

### Q1 — SageMaker network isolation for internal-only model [D4] ✅
## Full Question - 
A company wants to use a new recommendation system that was developed by a third-party partner. The system's model will be deployed on Amazon SageMaker.
To meet security requirements, the recommendation system must be only internal.The training and inference containers should not have access to any resource within a customer's VPC or on the internet.Which solution will meet these requirements with the LEAST operational overhead?
- **Stem**: 3rd-party recommendation system on SageMaker; must be internal; training + inference containers cannot access customer VPC resources or the internet. Constraint: **least operational overhead**.
- **Options**: (A) network isolation mode · (B) Canvas + VPC interface endpoint · (C) VPC-only + SGs · (D) VPC-only + NACLs
- **My answer**: A → **Correct**: A
- **Trap phrase**: *"least operational overhead"*
- **Rules surfaced**: [SageMaker networking](#sagemaker-networking-d4)

---

<!-- Copy this template for each new attempt. Delete this HTML comment wrapper for real entries. -->
<!--
### Qn — one-line topic [Dx] ✅/🟡/❌
- **Stem**: (1-2 sentences)
- **Options**: (A) ... · (B) ... · (C) ... · (D) ...
- **My answer**: X → **Correct**: Y
- **Trap phrase**: (the constraint word that decided it, if any)
- **Rules surfaced**: (link to the Rules & Traps section, or "new — added under [topic]")

Then extract the takeaway into a bullet in Rules & Traps above, tagged _(Qn)_.
-->

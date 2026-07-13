"""Generate a synthetic service-incident dataset.

Stdlib-only on purpose: producing sample data must require zero pip installs.
The data is deliberately *messy* (missing values, mixed case, stray whitespace,
a few duplicates, some outliers) so the data-prep step has real work to do —
which is exactly what MLA-C01 Domain 1 tests.

Signal we bake in (so a model can actually learn something):
    risk rises with error_rate, latency, cpu/mem pressure, alert count,
    P1/P2 severity, and a recent deploy. We add noise so it isn't trivial.
"""

import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)  # reproducible dataset

N = 600
SERVICES = ["auth-api", "payments", "search", "notifications", "billing", "gateway"]
REGIONS = ["us-east-1", "us-west-2", "eu-west-1", "ap-south-1"]
SEVERITIES = ["P1", "P2", "P3", "P4"]
ERROR_SNIPPETS = [
    "connection timeout to upstream",
    "5xx spike from dependency",
    "OOMKilled pod restart",
    "latency SLO breach",
    "database connection pool exhausted",
    "TLS handshake failure",
    "rate limit exceeded",
    "healthcheck failing",
]

OUT = "data/sample_incidents.csv"


def risk_from(features):
    """Compute a latent risk score, then bucket it. Adds noise on purpose."""
    sev_weight = {"P1": 3.0, "P2": 2.0, "P3": 1.0, "P4": 0.3}[features["severity"]]
    score = (
        features["error_rate"] * 4.0
        + (features["latency_ms"] / 1000.0)
        + features["cpu_util"] * 1.5
        + features["mem_util"] * 1.2
        + features["num_alerts"] * 0.4
        + (1.5 if features["deploy_recent"] else 0.0)
        + sev_weight
    )
    score += random.gauss(0, 0.8)  # noise so the task isn't deterministic
    if score >= 8.5:
        return "high"
    if score >= 5.0:
        return "medium"
    return "low"


def main():
    rows = []
    start = datetime(2026, 1, 1, 0, 0, 0)

    for i in range(N):
        severity = random.choices(SEVERITIES, weights=[1, 2, 4, 3])[0]
        f = {
            "severity": severity,
            "error_rate": round(random.betavariate(2, 5), 3),          # 0..1, skewed low
            "latency_ms": max(5, int(random.gauss(400, 250))),
            "cpu_util": round(min(1.0, max(0.02, random.gauss(0.55, 0.2))), 3),
            "mem_util": round(min(1.0, max(0.05, random.gauss(0.6, 0.18))), 3),
            "num_alerts": max(0, int(random.gauss(3, 2))),
            "deploy_recent": random.random() < 0.35,
        }
        row = {
            "incident_id": f"INC-{10000 + i}",
            "timestamp": (start + timedelta(minutes=7 * i)).isoformat(),
            # mixed case + whitespace on purpose (dirty categorical)
            "service": random.choice(SERVICES).upper() if i % 11 == 0 else random.choice(SERVICES),
            "region": random.choice(REGIONS),
            "severity": severity,
            "error_rate": f["error_rate"],
            "latency_ms": f["latency_ms"],
            "cpu_util": f["cpu_util"],
            "mem_util": f["mem_util"],
            "num_alerts": f["num_alerts"],
            "deploy_recent": f["deploy_recent"],
            "log_message": f"  {random.choice(ERROR_SNIPPETS)}  ",  # stray whitespace
            "risk_label": risk_from(f),
        }
        rows.append(row)

    # Inject missing values into ~4% of a few columns.
    for r in random.sample(rows, k=int(N * 0.04)):
        r["latency_ms"] = ""
    for r in random.sample(rows, k=int(N * 0.03)):
        r["cpu_util"] = ""

    # Inject a handful of exact duplicates (dedup should catch these).
    rows.extend([dict(r) for r in random.sample(rows, k=8)])

    fieldnames = list(rows[0].keys())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()

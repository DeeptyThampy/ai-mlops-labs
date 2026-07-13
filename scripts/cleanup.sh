#!/usr/bin/env bash
# Cleanup for the AWS ML Ops Lab.
#
# SAFETY:
#   - This script does NOT run any AWS command automatically.
#   - Each AWS resource we create in later sections gets its delete command
#     appended here, COMMENTED OUT, so you review + uncomment deliberately.
#   - Nothing here touches your AWS account until you edit and run it yourself.
set -euo pipefail

echo "Local cleanup only (safe):"
echo "  removing generated artifacts (processed data, models, caches)"

rm -rf data/processed models .pytest_cache
find . -type d -name __pycache__ -prune -exec rm -rf {} +

echo "Done. AWS resources are NOT touched by this run."
echo
echo "AWS cleanup commands are added per-section below, commented out."
echo "Review each one before uncommenting."

# ---------------------------------------------------------------------------
# Section 2 (S3 / Glue / Athena)  — added later
# aws s3 rm s3://<your-bucket>/ --recursive
# aws s3api delete-bucket --bucket <your-bucket>
# aws glue delete-crawler --name <crawler>
# aws glue delete-table --database-name <db> --name <table>
#
# Section 3/4 (SageMaker)  — added later
# aws sagemaker delete-endpoint --endpoint-name <name>
# aws sagemaker delete-endpoint-config --endpoint-config-name <name>
# aws sagemaker delete-model --model-name <name>
# ---------------------------------------------------------------------------

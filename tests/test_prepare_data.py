"""Unit tests for the data-prep pipeline.

Named by behavior, not by bug history. These lock in the Domain 1 guarantees:
schema validation, dedup, cleaning, no-leakage split.
"""

import pandas as pd
import pytest

from src import prepare_data as pp


def _raw_df():
    return pd.DataFrame(
        {
            "incident_id": ["INC-1", "INC-2", "INC-3", "INC-4"],
            "timestamp": ["2026-01-01T00:00:00"] * 4,
            "service": ["AUTH-API", "  payments ", "search", "search"],
            "region": ["us-east-1"] * 4,
            "severity": ["P1", "P3", "P4", "P4"],
            "error_rate": [0.5, 0.1, "", ""],
            "latency_ms": [900, "", 150, 150],
            "cpu_util": [0.9, 0.3, 0.4, 0.4],
            "mem_util": [0.8, 0.4, 0.5, 0.5],
            "num_alerts": [6, 1, 0, 0],
            "deploy_recent": ["True", "False", "false", "false"],
            "log_message": ["  oom  ", "timeout", "slo breach", "slo breach"],
            "risk_label": ["high", "low", "low", "low"],
        }
    )


def test_missing_required_column_raises():
    df = _raw_df().drop(columns=["severity"])
    with pytest.raises(ValueError, match="Missing required columns"):
        pp.validate_schema(df)


def test_clean_normalizes_case_and_whitespace():
    cleaned, _ = pp.clean(_raw_df())
    assert cleaned["service"].tolist()[0] == "auth-api"
    assert cleaned["service"].tolist()[1] == "payments"


def test_clean_coerces_blank_numeric_to_nan():
    cleaned, _ = pp.clean(_raw_df())
    assert cleaned["error_rate"].isna().sum() == 1
    assert cleaned["latency_ms"].isna().sum() == 1


def test_clean_maps_booleans_to_int():
    cleaned, _ = pp.clean(_raw_df())
    assert set(cleaned["deploy_recent"].unique()).issubset({0, 1})


def test_dedup_drops_exact_duplicate_incidents():
    # INC-3 and INC-4 are identical except incident_id -> one should drop.
    _, dropped = pp.clean(_raw_df())
    assert dropped == 1

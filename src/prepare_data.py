"""Data preparation for the incident-risk classifier (MLA-C01 Domain 1).

Pipeline (each step is one named function):
  1. load_raw            - read the CSV into a DataFrame
  2. validate_schema     - required columns must exist
  3. clean               - normalize strings, coerce numerics, dedup, booleans
  4. build_feature_matrix- pick input columns; separate X and y
  5. split_train_test    - stratified train/test split (BEFORE fitting anything)
  6. fit_imputer         - compute medians on TRAIN only (no leakage)
  7. apply_imputer       - fill NaNs in train and test using those medians
  8. engineer_features   - derive resource_pressure, is_peak_severity, log_len
                           (runs AFTER imputation so no NaNs sneak into features)
  9. encode_categoricals - one-hot encode; align test columns to train
 10. encode_target       - LabelEncoder on the target
 11. save_artifacts      - persist medians, feature columns, encoder (train/serve parity)
 12. write_splits        - train.csv / test.csv
 13. write_report        - data-quality report JSON
"""

import argparse
import json
import os

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

RAW_DEFAULT = "data/sample_incidents.csv"
OUT_DIR_DEFAULT = "data/processed"
MODELS_DIR = "models"

REQUIRED_COLUMNS = [
    "incident_id", "timestamp", "service", "region", "severity",
    "error_rate", "latency_ms", "cpu_util", "mem_util",
    "num_alerts", "deploy_recent", "log_message", "risk_label",
]
NUMERIC_COLS = ["error_rate", "latency_ms", "cpu_util", "mem_util", "num_alerts"]
CATEGORICAL_COLS = ["service", "region", "severity"]
# Columns fed into the pipeline as inputs (before engineering).
# log_message is here only so engineer_features can derive log_len; it's dropped after.
FEATURE_INPUT_COLS = NUMERIC_COLS + ["deploy_recent", "log_message"] + CATEGORICAL_COLS
TARGET = "risk_label"


# --- Load + validate -------------------------------------------------------

def load_raw(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found. Run: python scripts/generate_data.py"
        )
    return pd.read_csv(path)


def validate_schema(df):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


# --- Clean -----------------------------------------------------------------

def clean(df):
    df = df.copy()

    for col in CATEGORICAL_COLS + ["log_message"]:
        df[col] = df[col].astype(str).str.strip().str.lower()

    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["deploy_recent"] = (
        df["deploy_recent"].astype(str).str.strip().str.lower()
        .map({"true": 1, "false": 0, "1": 1, "0": 0})
        .fillna(0).astype(int)
    )

    before = len(df)
    df = df.drop_duplicates(subset=[c for c in df.columns if c != "incident_id"])
    dropped_dupes = before - len(df)

    return df, dropped_dupes


# --- Feature matrix + split ------------------------------------------------

def build_feature_matrix(df):
    return df[FEATURE_INPUT_COLS].copy(), df[TARGET].copy()


def split_train_test(X, y, test_size, seed):
    return train_test_split(X, y, test_size=test_size, random_state=seed, stratify=y)


# --- Imputation (fit on train only) ---------------------------------------

def fit_imputer(X_train):
    """Compute median for each numeric column, using training data only."""
    return X_train[NUMERIC_COLS].median()


def apply_imputer(medians, *splits):
    """Fill NaNs in each split using the fitted medians. Returns new DataFrames."""
    return tuple(split.fillna(medians) for split in splits)


# --- Feature engineering (runs AFTER imputation) --------------------------

def engineer_features(*splits):
    """Derive features from cleaned + imputed inputs. Per-row transform,
    so it applies identically to train and test with no leakage risk."""
    return tuple(_engineer_one(split) for split in splits)


def _engineer_one(df):
    df = df.copy()
    df["resource_pressure"] = (df["cpu_util"] + df["mem_util"]) / 2.0
    df["is_peak_severity"] = df["severity"].isin(["p1", "p2"]).astype(int)
    df["log_len"] = df["log_message"].str.len()
    # log_message was only kept so we could compute log_len; drop the raw text now.
    return df.drop(columns=["log_message"])


# --- Encoding --------------------------------------------------------------

def encode_categoricals(X_train, X_test):
    X_train = pd.get_dummies(X_train, columns=CATEGORICAL_COLS)
    X_test = pd.get_dummies(X_test, columns=CATEGORICAL_COLS)
    # Align test columns to train's set (test may be missing rare categories).
    X_test = X_test.reindex(columns=X_train.columns, fill_value=0)
    return X_train, X_test


def encode_target(y_train, y_test):
    # LabelEncoder sorts alphabetically -> high=0, low=1, medium=2.
    # For a classifier target these are just IDs, not a ranking.
    le = LabelEncoder().fit(["low", "medium", "high"])
    return le, le.transform(y_train), le.transform(y_test)


# --- Persist + write -------------------------------------------------------

def save_artifacts(medians, feature_columns, le, out_path):
    joblib.dump(
        {
            "medians": medians,
            "feature_columns": list(feature_columns),
            "label_encoder": le,
        },
        out_path,
    )


def write_splits(X_train, y_train_enc, X_test, y_test_enc, out_dir):
    train_out = X_train.copy()
    train_out[TARGET] = y_train_enc
    test_out = X_test.copy()
    test_out[TARGET] = y_test_enc
    train_out.to_csv(os.path.join(out_dir, "train.csv"), index=False)
    test_out.to_csv(os.path.join(out_dir, "test.csv"), index=False)


def write_report(dropped_dupes, X_train, X_test, class_counts, medians, out_dir):
    report = {
        "raw_rows": int(len(X_train) + len(X_test) + dropped_dupes),
        "rows_after_dedup": int(len(X_train) + len(X_test)),
        "duplicates_dropped": int(dropped_dupes),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "num_features": int(X_train.shape[1]),
        "class_balance": {k: int(v) for k, v in class_counts.items()},
        "imputed_medians": {k: float(v) for k, v in medians.items()},
    }
    with open(os.path.join(out_dir, "data_quality_report.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    return report


# --- Orchestration ---------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=RAW_DEFAULT)
    ap.add_argument("--out-dir", default=OUT_DIR_DEFAULT)
    ap.add_argument("--test-size", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    df = load_raw(args.raw)
    validate_schema(df)
    df, dropped_dupes = clean(df)

    X, y = build_feature_matrix(df)
    X_train, X_test, y_train, y_test = split_train_test(X, y, args.test_size, args.seed)

    medians = fit_imputer(X_train)
    X_train, X_test = apply_imputer(medians, X_train, X_test)

    X_train, X_test = engineer_features(X_train, X_test)
    X_train, X_test = encode_categoricals(X_train, X_test)
    le, y_train_enc, y_test_enc = encode_target(y_train, y_test)

    save_artifacts(medians, X_train.columns, le, os.path.join(MODELS_DIR, "preprocess.joblib"))
    write_splits(X_train, y_train_enc, X_test, y_test_enc, args.out_dir)
    report = write_report(
        dropped_dupes, X_train, X_test, df[TARGET].value_counts(), medians, args.out_dir
    )

    print(json.dumps(report, indent=2))
    print(f"\nWrote train/test + report to {args.out_dir}/ and transformers to {MODELS_DIR}/")


if __name__ == "__main__":
    main()

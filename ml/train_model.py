"""
Train a threat-classification model and save it to ml/model.pkl.

Pipeline:
    1. Generate (or load) the synthetic dataset
    2. Extract features via feature_engineering.py
    3. Train a RandomForestClassifier with hyperparameter tuning
    4. Evaluate on a held-out test set
    5. Serialize the trained model to model.pkl

Usage:
    cd <project-root>
    python -m ml.train_model                 # generate data + train
    python -m ml.train_model --dataset ml/dataset.csv   # use existing CSV
"""

import argparse
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split, GridSearchCV

from ml.feature_engineering import extract_features_df

# ── Paths ───────────────────────────────────────────────
ML_DIR = Path(__file__).resolve().parent
MODEL_PATH = ML_DIR / "model.pkl"
DATASET_PATH = ML_DIR / "dataset.csv"


def load_or_generate_dataset(csv_path: Path | None = None) -> pd.DataFrame:
    """Load an existing CSV or generate a fresh synthetic dataset."""
    path = csv_path or DATASET_PATH

    if path.exists():
        print(f"📄 Loading dataset from {path}")
        return pd.read_csv(path)

    print("📦 No dataset found — generating synthetic data…")
    from ml.generate_dataset import generate_dataset
    generate_dataset(n_rows=2000)
    return pd.read_csv(DATASET_PATH)


def train(df: pd.DataFrame) -> RandomForestClassifier:
    """Train a RandomForestClassifier and print evaluation metrics."""

    # ── Feature extraction ──────────────────────────────
    X = extract_features_df(df)
    y = df["label"].values

    print(f"\n📊 Dataset: {len(df)} samples, {X.shape[1]} features")
    print(f"   Class distribution: valid={int(y.sum())}, invalid={int(len(y) - y.sum())}")

    # ── Train / test split ──────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── Hyperparameter search ───────────────────────────
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [5, 10, None],
        "min_samples_split": [2, 5],
    }

    print("\n🔍 Running grid search (RandomForest)…")
    grid = GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid,
        cv=3,
        scoring="f1",
        n_jobs=-1,
        verbose=0,
    )
    grid.fit(X_train, y_train)

    best_model = grid.best_estimator_
    print(f"   Best params: {grid.best_params_}")
    print(f"   Best CV F1:  {grid.best_score_:.4f}")

    # ── Evaluation on test set ──────────────────────────
    y_pred = best_model.predict(X_test)

    print(f"\n✅ Test Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["invalid", "valid"]))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # ── Feature importance ──────────────────────────────
    from ml.feature_engineering import FEATURE_NAMES
    importances = best_model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    print("\n🏆 Feature Importance:")
    for i in sorted_idx:
        print(f"   {FEATURE_NAMES[i]:20s}  {importances[i]:.4f}")

    return best_model


def save_model(model: RandomForestClassifier, path: Path = MODEL_PATH) -> None:
    """Serialize the trained model to disk."""
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"\n💾 Model saved → {path}  ({path.stat().st_size / 1024:.1f} KB)")


# ── CLI ─────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train threat classification model")
    parser.add_argument("--dataset", type=str, default=None, help="Path to CSV dataset")
    args = parser.parse_args()

    csv_path = Path(args.dataset) if args.dataset else None
    df = load_or_generate_dataset(csv_path)
    model = train(df)
    save_model(model)

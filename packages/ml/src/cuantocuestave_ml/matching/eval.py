"""Matching evaluation against ground truth CSV.
Used by CI: pytest packages/ml/tests/test_matching_eval.py
"""
from pathlib import Path

import polars as pl


GROUND_TRUTH_PATH = Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "matching_ground_truth.csv"

PRECISION_THRESHOLD = 0.90
RECALL_THRESHOLD = 0.85


def load_ground_truth(path: Path = GROUND_TRUTH_PATH) -> pl.DataFrame:
    return pl.read_csv(path)


def evaluate(predictions: pl.DataFrame, ground_truth: pl.DataFrame) -> dict[str, float]:
    """Compute precision, recall, F1 for matching predictions.

    predictions: DataFrame with columns [listing_id, predicted_canonical_id]
    ground_truth: DataFrame with columns [listing_id, true_canonical_id]
    """
    merged = predictions.join(ground_truth, on="listing_id", how="inner")
    tp = (merged["predicted_canonical_id"] == merged["true_canonical_id"]).sum()
    precision = tp / len(merged) if len(merged) > 0 else 0.0
    recall = tp / len(ground_truth) if len(ground_truth) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}

import pytest
from app.evaluation.metrics import BinaryMetrics


def test_perfect_classifier_metrics():
    bm = BinaryMetrics(tp=50, tn=50, fp=0, fn=0, inconclusive=0, total=100)
    assert bm.sensitivity == 1.0
    assert bm.specificity == 1.0
    assert bm.precision == 1.0
    assert bm.f1 == 1.0
    assert bm.balanced_accuracy == 1.0
    assert bm.mcc == 1.0
    assert bm.inconclusive_rate == 0.0


def test_imbalanced_dataset_mcc_balanced_acc():
    # 5 authentic, 1000 tampered (mimicking historical test set)
    # If a trivial classifier predicts TAMPERED for all:
    # TP = 1000, FN = 0, FP = 5, TN = 0
    trivial_bm = BinaryMetrics(tp=1000, tn=0, fp=5, fn=0, inconclusive=0, total=1005)
    assert trivial_bm.sensitivity == 1.0
    assert trivial_bm.specificity == 0.0
    # Balanced accuracy reveals the failure: exactly 50%!
    assert trivial_bm.balanced_accuracy == 0.50
    # MCC is undefined (None) when TN=0: denominator sqrt((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN)) = 0
    # This correctly reflects that MCC cannot be computed for a trivial all-positive classifier
    # when there are zero true negatives in the dataset.
    assert trivial_bm.mcc is None  # undefined — not 0.0


def test_zero_division_safety():
    empty_bm = BinaryMetrics(tp=0, tn=0, fp=0, fn=0, inconclusive=10, total=10)
    assert empty_bm.sensitivity is None
    assert empty_bm.specificity is None
    assert empty_bm.precision is None
    assert empty_bm.f1 is None
    assert empty_bm.balanced_accuracy is None
    assert empty_bm.mcc is None
    assert empty_bm.inconclusive_rate == 1.0


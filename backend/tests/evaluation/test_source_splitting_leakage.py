import pytest
from app.evaluation.manifest import DatasetManifest, SpecimenRecord


def test_source_splitting_prevents_leakage():
    # 5 source images, each having 4 derivative manipulated variants
    specimens = []
    for s_idx in range(5):
        source_id = f"SRC-{s_idx:03d}"
        for m_idx, m_type in enumerate(["COPY_MOVE", "SPLICING", "OBJECT_REMOVAL", "RETOUCHING"]):
            specimens.append(
                SpecimenRecord(
                    specimen_id=f"SPEC-{s_idx}-{m_idx}",
                    source_id=source_id,
                    ground_truth="TAMPERED",
                    manipulation_type=m_type,
                )
            )

    partitioned = DatasetManifest.split_by_source(specimens, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2)

    # Verify that all specimens with the same source_id have the identical dataset_split!
    source_to_splits = {}
    for rec in partitioned:
        if rec.source_id not in source_to_splits:
            source_to_splits[rec.source_id] = set()
        source_to_splits[rec.source_id].add(rec.dataset_split)

    for src_id, splits in source_to_splits.items():
        assert len(splits) == 1, f"Data leakage detected! Source {src_id} has specimens across multiple splits: {splits}"


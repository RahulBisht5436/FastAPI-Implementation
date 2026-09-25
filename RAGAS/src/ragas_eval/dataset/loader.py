from __future__ import annotations

import json
from pathlib import Path

from ragas_eval.dataset.schema import GoldenDataset


def load_golden_dataset(path: str | Path) -> GoldenDataset:
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Golden dataset not found: {dataset_path}")

    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    return GoldenDataset.model_validate(payload)


def validate_manifest_hash(dataset: GoldenDataset, live_manifest_hash: str) -> None:
    if not dataset.require_manifest_match:
        return
    if not dataset.kb_manifest_hash:
        raise ValueError(
            "Dataset requires manifest matching but kb_manifest_hash is missing."
        )
    if dataset.kb_manifest_hash != live_manifest_hash:
        raise ValueError(
            "KB manifest hash mismatch. Re-ingest documents and update the golden "
            f"dataset or disable require_manifest_match. expected="
            f"{dataset.kb_manifest_hash}, actual={live_manifest_hash}"
        )

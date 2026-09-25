from ragas_eval.dataset.loader import load_golden_dataset, validate_manifest_hash


def test_load_golden_dataset():
    dataset = load_golden_dataset("data/golden/v1.json")
    assert dataset.version == "1.0.0"
    assert len(dataset.samples) >= 10


def test_manifest_validation_passes_for_current_hash():
    dataset = load_golden_dataset("data/golden/v1.json")
    validate_manifest_hash(dataset, dataset.kb_manifest_hash or "")


def test_manifest_validation_fails_on_mismatch():
    dataset = load_golden_dataset("data/golden/v1.json")
    try:
        validate_manifest_hash(dataset, "deadbeef")
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass

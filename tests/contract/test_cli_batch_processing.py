import pytest


def test_cli_batch_processing_contract():
    """T006: Contract test for batch processing command.

    Assert the BatchProcessor exposes `process_files` and it raises
    NotImplementedError until implemented.
    """
    from hlpr.cli.batch import BatchProcessor

    bp = BatchProcessor()
    assert hasattr(bp, "process_files")
    with pytest.raises(NotImplementedError):
        bp.process_files(["a.txt"])

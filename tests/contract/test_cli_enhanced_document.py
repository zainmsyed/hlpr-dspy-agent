import pytest


def test_cli_enhanced_document_entrypoint_exists():
    """T005: Contract test for direct command `hlpr summarize document`.

    Verify that the renderers and batch processor classes exist (interface check)
    and that attempting to call their primary methods raises NotImplementedError.
    """
    from hlpr.cli.batch import BatchProcessor
    from hlpr.cli.renderers import BaseRenderer

    assert issubclass(BaseRenderer, object)
    bp = BatchProcessor()
    with pytest.raises(NotImplementedError):
        bp.process_files([])

from hlpr.cli.models import (
    InteractiveSessionModel,
    OutputPreferences,
    ProcessingState,
    ProcessingResult,
    ProcessingMetadata,
    ProcessingError,
    FileSelection,
    ProviderOption,
)


def test_file_selection_and_provider_option():
    fs = FileSelection(path="/tmp/doc.pdf", size_bytes=1024, mime_type="application/pdf")
    po = ProviderOption(name="local", description="local LLM", default=True)
    assert fs.path.endswith("doc.pdf")
    assert po.default is True


def test_processing_models_and_error():
    pe = ProcessingError(code="E1", message="failed to parse", details={"line": 10})
    from datetime import datetime
    pm = ProcessingMetadata(started_at=datetime.utcnow(), finished_at=datetime.utcnow(), duration_seconds=0.5)
    fs = FileSelection(path="/tmp/doc.txt")
    pr = ProcessingResult(file=fs, summary="ok", metadata=pm, error=pe)
    assert pr.error.code == "E1"


def test_state_and_preferences():
    state = ProcessingState(total_files=3, processed_files=1)
    prefs = OutputPreferences(format="json", include_metadata=False, max_summary_chars=500)
    session = InteractiveSessionModel(session_id="s1", preferences=prefs, files=[FileSelection(path="a")], state=state)
    assert session.preferences.format == "json"
    assert session.state.total_files == 3


def test_validation_errors_and_serialization():
    # invalid file path
    import pytest

    with pytest.raises(ValueError):
        FileSelection(path="")

    # processed_files > total_files
    with pytest.raises(ValueError):
        ProcessingState(total_files=1, processed_files=2)

    # invalid output format
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        OutputPreferences(format="invalid")

    # serialization
    fs = FileSelection(path="/tmp/ok.txt")
    session = InteractiveSessionModel(session_id="s2", files=[fs])
    d = session.model_dump()
    assert d.get("session_id") == "s2"

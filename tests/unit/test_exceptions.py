from hlpr.exceptions import (
    ConfigurationError,
    DocumentProcessingError,
    HlprError,
    SummarizationError,
)


def test_hlpr_error_default_str_and_dict():
    e = HlprError("generic")
    # stringification prefers message attr when present
    assert "generic" in str(e)
    d = e.to_dict()
    assert "error" in d
    assert "error_code" in d


def test_document_processing_error_serialization():
    err = DocumentProcessingError(message="failed to parse", details={"path": "/f"})
    assert err.status_code() == 400
    j = err.to_dict()
    assert j["error"] == "failed to parse"
    assert j["error_code"] == "DOCUMENT_PROCESSING_ERROR"
    assert j["details"]["path"] == "/f"


def test_summarization_and_configuration_errors():
    s = SummarizationError(message="llm down")
    c = ConfigurationError(message="bad cfg")
    assert s.status_code() == 422
    assert c.status_code() == 500
    assert s.to_dict()["error_code"] == "SUMMARIZATION_ERROR"
    assert c.to_dict()["error_code"] == "CONFIGURATION_ERROR"

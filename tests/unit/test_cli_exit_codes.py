
from typer.testing import CliRunner

from hlpr.cli.main import app
from hlpr.exceptions import (
    ConfigurationError,
    DocumentProcessingError,
    HlprError,
    SummarizationError,
)

runner = CliRunner()


def _parse_short(_p):
    return "short"


def test_summarization_error_maps_to_exit_5(monkeypatch, tmp_path):
    """If the summarizer raises SummarizationError the CLI should exit 5."""
    test_file = tmp_path / "test_document.txt"
    test_file.write_text("short content")

    # Parser returns extracted text (short so summarize_document() is used)
    def _parse_short(_p):
        return "short"

    monkeypatch.setattr(
        "hlpr.document.parser.DocumentParser.parse_file", _parse_short,
    )

    # Summarizer raises SummarizationError during summarize_document
    def _raise(_self, *_, **__):
        msg = "summarizer failed"
        raise SummarizationError(msg)

    monkeypatch.setattr(
        "hlpr.document.summarizer.DocumentSummarizer.summarize_document", _raise,
    )

    result = runner.invoke(app, ["summarize", "document", str(test_file)])
    assert result.exit_code == 5


def test_document_processing_error_maps_to_exit_6(monkeypatch, tmp_path):
    """If the parser raises DocumentProcessingError the CLI should exit 6."""
    test_file = tmp_path / "test_document.txt"
    test_file.write_text("content")

    def _raise_parse(_p):
        msg = "parse failed"
        raise DocumentProcessingError(msg)

    monkeypatch.setattr(
        "hlpr.document.parser.DocumentParser.parse_file",
        _raise_parse,
    )

    result = runner.invoke(app, ["summarize", "document", str(test_file)])
    assert result.exit_code == 6


def test_configuration_error_maps_to_exit_2(monkeypatch, tmp_path):
    """If building the summarizer raises ConfigurationError the CLI should exit 2."""
    test_file = tmp_path / "test_document.txt"
    test_file.write_text("content")

    monkeypatch.setattr(
        "hlpr.document.parser.DocumentParser.parse_file", _parse_short,
    )

    # Make the constructor raise ConfigurationError
    def _bad_init(_self, *_, **__):
        msg = "bad config"
        raise ConfigurationError(msg)

    monkeypatch.setattr(
        "hlpr.document.summarizer.DocumentSummarizer.__init__", _bad_init,
    )

    result = runner.invoke(app, ["summarize", "document", str(test_file)])
    assert result.exit_code == 2


def test_generic_hlpr_error_maps_to_exit_3(monkeypatch, tmp_path):
    """A generic HlprError should map to exit code 3."""
    test_file = tmp_path / "test_document.txt"
    test_file.write_text("content")

    monkeypatch.setattr(
        "hlpr.document.parser.DocumentParser.parse_file", _parse_short,
    )

    def _raise_generic(_self, *_, **__):
        msg = "generic"
        raise HlprError(msg)

    monkeypatch.setattr(
        "hlpr.document.summarizer.DocumentSummarizer.summarize_document",
        _raise_generic,
    )

    result = runner.invoke(app, ["summarize", "document", str(test_file)])
    assert result.exit_code == 3

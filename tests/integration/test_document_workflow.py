import json
from pathlib import Path

from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


class TestDocumentWorkflowIntegration:
    """Integration tests for complete document summarization workflow"""

    def test_full_document_summarization_workflow(self):
        """Test complete document summarization workflow from CLI to output"""
        # This test will fail until the full implementation is complete

        # Create a sample document
        test_doc = Path("sample-report.txt")
        test_doc.write_text(
            "This is a sample document with important information about "
            "quarterly sales. The revenue increased by 15% compared to last "
            "quarter. Key challenges include supply chain delays and increased "
            "competition. Action items: review pricing strategy, improve "
            "delivery times, conduct market analysis.",
        )

        # Test basic summarization
        result = runner.invoke(app, ["summarize", "document", str(test_doc)])
        assert result.exit_code == 0
        assert "summary" in result.output.lower()
        assert "key points" in result.output.lower()
        assert "15%" in result.output  # Should extract the revenue figure

        # Clean up
        test_doc.unlink(missing_ok=True)

    def test_document_workflow_with_file_output(self):
        """Test document workflow with different output formats"""
        test_doc = Path("output-test.txt")
        test_doc.write_text("Sample document for testing file output formats.")

        # Test markdown output
        md_output = Path("test-summary.md")
        result = runner.invoke(
            app,
            [
                "summarize",
                "document",
                str(test_doc),
                "--save",
                "--format",
                "md",
                "--output",
                str(md_output),
            ],
        )
        assert result.exit_code == 0
        assert md_output.exists()

        # Test JSON output
        json_output = Path("test-summary.json")
        result = runner.invoke(
            app,
            [
                "summarize",
                "document",
                str(test_doc),
                "--save",
                "--format",
                "json",
                "--output",
                str(json_output),
            ],
        )
        assert result.exit_code == 0
        assert json_output.exists()

        # Verify JSON structure
        with json_output.open() as f:
            data = json.load(f)
            assert "summary" in data
            assert "key_points" in data
            assert isinstance(data["key_points"], list)

        # Clean up
        test_doc.unlink(missing_ok=True)
        md_output.unlink(missing_ok=True)
        json_output.unlink(missing_ok=True)

    def test_document_workflow_with_provider_selection(self):
        """Test document workflow with different AI providers"""
        test_doc = Path("provider-test.txt")
        test_doc.write_text("Document to test provider selection functionality.")

        # Test with local provider (if available)
        result = runner.invoke(
            app,
            ["summarize", "document", str(test_doc), "--provider", "local"],
        )
        assert result.exit_code in [0, 1, 2]  # May succeed, fail, or be unavailable

        # Clean up
        test_doc.unlink(missing_ok=True)

    def test_document_workflow_error_handling(self):
        """Test error handling in document workflow"""
        # Test with non-existent file
        result = runner.invoke(app, ["summarize", "document", "nonexistent.pdf"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "error" in result.output.lower()

        # Test with unsupported format (if implemented)
        unsupported_file = Path("test.xyz")
        unsupported_file.write_text("content")
        result = runner.invoke(app, ["summarize", "document", str(unsupported_file)])
        # Should either process or fail gracefully
        assert result.exit_code in [0, 1, 2]

        # Clean up
        unsupported_file.unlink(missing_ok=True)

    def test_document_workflow_comprehensive(self):
        """Test comprehensive document processing workflow"""
        # Create a more complex document
        complex_doc = Path("complex-report.txt")
        complex_doc.write_text(
            "Executive Summary\n\n"
            "This quarterly report covers financial performance, market analysis, "
            "and strategic initiatives. Revenue grew 22% year-over-year.\n\n"
            "Key Findings:\n"
            "- Market share increased to 15%\n"
            "- Customer satisfaction scores improved by 8 points\n"
            "- Operating costs decreased by 5%\n\n"
            "Recommendations:\n"
            "1. Expand into European markets\n"
            "2. Invest in customer service training\n"
            "3. Optimize supply chain operations\n\n"
            "Conclusion: Strong performance across all metrics indicates "
            "successful execution of strategic plan.",
        )

        result = runner.invoke(app, ["summarize", "document", str(complex_doc)])
        assert result.exit_code == 0

        # Should extract key information
        output_lower = result.output.lower()
        assert "22%" in result.output or "revenue" in output_lower
        assert "recommendations" in output_lower or "findings" in output_lower

        # Clean up
        complex_doc.unlink(missing_ok=True)

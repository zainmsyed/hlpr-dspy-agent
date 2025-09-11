"""Document parser for extracting text from various file formats."""

import logging
from pathlib import Path
from typing import Optional

try:
    # Prefer the PyPDF2 namespace if available for backward compatibility
    from PyPDF2 import PdfReader  # type: ignore
except Exception:
    try:
        # Newer package name used by many installs
        from pypdf import PdfReader  # type: ignore
    except Exception:
        # Keep a clear name in module namespace; consumers should check and
        # raise a helpful error when attempting to use PDF parsing.
        PdfReader = None

from docx import Document as DocxDocument

from hlpr.models.document import Document, FileFormat

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parser for extracting text content from document files.

    Supports PDF, DOCX, TXT, and MD file formats using specialized libraries
    for each format with appropriate error handling.
    """

    @staticmethod
    def parse_file(file_path: str | Path) -> str:
        """Parse a document file and extract its text content.

        Args:
            file_path: Path to the document file

        Returns:
            Extracted text content from the document

        Raises:
            ValueError: If file format is unsupported or parsing fails
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Determine format from file extension
        extension = path.suffix.lower().lstrip(".")
        try:
            file_format = FileFormat(extension)
        except ValueError:
            raise ValueError(f"Unsupported file format: {extension}")

        # Parse based on format
        try:
            if file_format == FileFormat.PDF:
                return DocumentParser._parse_pdf(path)
            elif file_format == FileFormat.DOCX:
                return DocumentParser._parse_docx(path)
            elif file_format in (FileFormat.TXT, FileFormat.MD):
                return DocumentParser._parse_text(path)
            else:
                raise ValueError(f"Unsupported format: {file_format}")
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise ValueError(f"Failed to parse document: {e}")

    @staticmethod
    def _parse_pdf(file_path: Path) -> str:
        """Parse PDF file and extract text content.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content

        Raises:
            ValueError: If PDF parsing fails or PDF library not available
        """
        if PdfReader is None:
            raise ValueError("PDF parsing not available - install PyPDF2 or pypdf package")

        try:
            reader = PdfReader(file_path)
            text_content = []

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    text_content.append(page_text)

            if not text_content:
                raise ValueError("No text content found in PDF (may be image-based)")

            return "\n\n".join(text_content)

        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {e}")

    @staticmethod
    def _parse_docx(file_path: Path) -> str:
        """Parse DOCX file and extract text content.

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text content

        Raises:
            ValueError: If DOCX parsing fails
        """
        try:
            doc = DocxDocument(file_path)
            text_content = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)

            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text_content.append(cell.text)

            if not text_content:
                raise ValueError("No text content found in DOCX file")

            return "\n\n".join(text_content)

        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {e}")

    @staticmethod
    def _parse_text(file_path: Path) -> str:
        """Parse text-based file (TXT, MD) and return content.

        Args:
            file_path: Path to text file

        Returns:
            File content as string

        Raises:
            ValueError: If file cannot be read
        """
        try:
            with file_path.open("r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                raise ValueError("File is empty or contains no readable text")

            return content

        except UnicodeDecodeError:
            raise ValueError("File encoding is not UTF-8 compatible")
        except Exception as e:
            raise ValueError(f"Failed to read text file: {e}")

    @staticmethod
    def validate_document(document: Document) -> bool:
        """Validate that a document can be parsed.

        Args:
            document: Document instance to validate

        Returns:
            True if document can be parsed, False otherwise
        """
        try:
            # Try to parse a small portion to validate
            path = Path(document.path)

            if document.format == FileFormat.PDF:
                reader = PdfReader(path)
                if len(reader.pages) == 0:
                    return False
                # Try to extract text from first page
                first_page = reader.pages[0]
                text = first_page.extract_text()
                return bool(text.strip())

            elif document.format == FileFormat.DOCX:
                doc = DocxDocument(path)
                return bool(doc.paragraphs or doc.tables)

            elif document.format in (FileFormat.TXT, FileFormat.MD):
                with path.open("r", encoding="utf-8") as f:
                    content = f.read(1024)  # Read first 1KB
                    return bool(content.strip())

            return False

        except Exception:
            return False

    @staticmethod
    def get_document_info(file_path: str | Path) -> dict:
        """Get basic information about a document without full parsing.

        Args:
            file_path: Path to the document file

        Returns:
            Dictionary with document information

        Raises:
            ValueError: If file cannot be analyzed
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = path.suffix.lower().lstrip(".")
        try:
            file_format = FileFormat(extension)
        except ValueError:
            raise ValueError(f"Unsupported file format: {extension}")

        info = {
            "path": str(path.absolute()),
            "format": file_format.value,
            "size_bytes": path.stat().st_size,
            "can_parse": False,
        }

        try:
            # Quick validation
            if file_format == FileFormat.PDF:
                reader = PdfReader(path)
                info["page_count"] = len(reader.pages)
                info["can_parse"] = len(reader.pages) > 0

            elif file_format == FileFormat.DOCX:
                doc = DocxDocument(path)
                info["paragraph_count"] = len(doc.paragraphs)
                info["table_count"] = len(doc.tables)
                info["can_parse"] = bool(doc.paragraphs or doc.tables)

            elif file_format in (FileFormat.TXT, FileFormat.MD):
                with path.open("r", encoding="utf-8") as f:
                    sample = f.read(1024)
                    info["sample_text"] = sample[:200] + "..." if len(sample) > 200 else sample
                    info["can_parse"] = bool(sample.strip())

        except Exception as e:
            info["error"] = str(e)

        return info
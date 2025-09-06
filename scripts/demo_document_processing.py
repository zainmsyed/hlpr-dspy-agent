"""Demo script for the enhanced document summarizer with file processing support."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.workflows.documents.summarizer import DocumentSummarizer
from src.workflows.documents.processor import DocumentProcessor
import tempfile

def demo_text_processing():
    """Demo processing text directly."""
    print("=== Demo: Text Processing ===")
    summarizer = DocumentSummarizer()

    text = """
    This is a sample document about artificial intelligence.
    AI is transforming many industries including healthcare, finance, and education.
    Machine learning models can now process vast amounts of data.
    The future of AI looks promising with advances in natural language processing.
    """

    result = summarizer.run(text)
    print(f"Summary: {result}")
    print()

def demo_file_processing():
    """Demo processing a text file."""
    print("=== Demo: File Processing ===")

    # Create a temporary text file
    content = """Company Report: Q3 2024

    Revenue increased by 15% this quarter, reaching $2.5 million.
    Our AI-powered analytics platform gained 500 new enterprise customers.
    Key challenges include supply chain disruptions and increased competition.
    Looking ahead to Q4, we expect continued growth in the cloud services sector.

    Important dates:
    - Board meeting: December 15, 2024
    - Product launch: January 2025
    - Annual conference: March 2025
    """

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_file = f.name

    try:
        summarizer = DocumentSummarizer()
        result = summarizer.process_file(temp_file)

        print(f"Summary: {result.summary}")
        print(f"Key Takeaways: {len(result.key_takeaways)} items")
        print(f"Entities Found: {len(result.entities)} items")
        print(f"Processing Time: {result.processing_time:.2f}s")
        print(f"Confidence: {result.confidence}")

    finally:
        os.unlink(temp_file)
    print()

def demo_supported_formats():
    """Demo supported file formats."""
    print("=== Demo: Supported Formats ===")
    formats = DocumentProcessor.get_supported_formats()
    print(f"Supported file formats: {', '.join(formats)}")
    print()

if __name__ == "__main__":
    print("Document Summarizer Demo")
    print("=" * 50)

    demo_supported_formats()
    demo_text_processing()
    demo_file_processing()

    print("Demo completed!")
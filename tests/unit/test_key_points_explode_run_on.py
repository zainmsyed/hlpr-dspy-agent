from hlpr.llm.dspy_integration import DSPyDocumentSummarizer


def test_explode_run_on_bullets_splits_long_item():
    long_item = (
        "Zain has nearly a decade of healthcare operations experience, specifically in billing and revenue cycle optimization. "
        "He has a proven track record of driving revenue growth through biosimilar implementation (generating $4M). "
        "His clinical background as a Clinical Oncology Pharmacist provides valuable workflow understanding. "
        "He possesses hands-on experience with AI, including a newsletter series focused on AI solutions."
    )

    result = DSPyDocumentSummarizer._explode_run_on_bullets([long_item])

    # Expect multiple items after splitting on sentences due to length and multiple sentence boundaries
    assert len(result) >= 3
    assert result[0].startswith("Zain has nearly a decade")
    assert result[1].startswith("He has a proven track record")

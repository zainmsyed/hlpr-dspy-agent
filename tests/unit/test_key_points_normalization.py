from hlpr.llm.dspy_integration import DSPyDocumentSummarizer


def test_normalize_key_points_merges_multiline_string_and_strips_markers():
    # Simulate model output where bullets are split across lines and use various markers
    raw = (
        "• wrtr\n"
        "is a terminal-based markdown writing application.\n"
        "• It was developed using 'vibe coding'\n"
        "- AI-assisted coding with Cursor Composer w Sonnet.\n"
        "- The project is currently in alpha and available on GitHub.\n"
    )

    result = DSPyDocumentSummarizer._normalize_key_points(raw)

    # Expect continuation lines to be merged and markers removed
    assert result == [
        "wrtr is a terminal-based markdown writing application.",
        "It was developed using 'vibe coding' - AI-assisted coding with Cursor Composer w Sonnet.",
        "The project is currently in alpha and available on GitHub.",
    ]


def test_normalize_key_points_list_input_and_continuations():
    raw_list = [
        "* First item",
        "continued details",
        "2. Second item",
        "more info",
        "• Third item only",
    ]

    result = DSPyDocumentSummarizer._normalize_key_points(raw_list)

    assert result == [
        "First item continued details",
        "Second item more info",
        "Third item only",
    ]

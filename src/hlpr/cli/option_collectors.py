"""Helpers to collect options for the guided interactive session.

This module extracts the option-collection responsibilities from
`InteractiveSession` so the session class can remain focused on orchestration
and flow control. The helpers are small, synchronous, and test-friendly.
"""

from typing import Any

from hlpr.models.interactive import ProcessingOptions


def collect_basic_options(prompt_provider: Any) -> ProcessingOptions:
    """Collect basic options using the provided prompt provider.

    This mirrors the behavior previously implemented as a method on
    InteractiveSession, returning a `ProcessingOptions` instance.
    """
    provider = prompt_provider.provider_prompt()
    fmt = prompt_provider.format_prompt()
    temp = prompt_provider.temperature_prompt()
    save, outpath = prompt_provider.save_file_prompt()
    return ProcessingOptions(
        provider=provider,
        format=fmt,
        temperature=temp,
        save=save,
        output_path=outpath,
    )


def collect_advanced_options(
    base_options: ProcessingOptions, prompt_provider: Any
) -> dict[str, object]:
    """Collect advanced option fields and return a dict of updates.

    The caller can merge these updates into an existing ProcessingOptions
    instance. Keeping this function return a plain dict keeps the
    responsibilities narrow and easy to test.
    """
    # base_options is accepted for API compatibility with the original
    # InteractiveSession method but not required by the simple collector.
    # Keep the parameter to avoid changing callers; signal lint that it's
    # intentionally unused by prefixing with underscore in the local name.
    _ = base_options
    return prompt_provider.advanced_options_prompt()

import time

from hlpr.cli.interactive import InteractiveSession
import os



class FastPromptProvider:
    def provider_prompt(self):
        return "local"

    def format_prompt(self):
        return "rich"

    def temperature_prompt(self):
        return 0.3

    def save_file_prompt(self):
        return (False, None)

    def advanced_options_prompt(self):
        return {"chunk_size": 8192}


def test_collect_options_is_fast():
    """Ensure collect_basic_options and collect_advanced_options return quickly
    when prompts use defaults (simulated by a fast PromptProvider).
    """
    session = InteractiveSession(prompt_provider=FastPromptProvider())
    start = time.perf_counter()
    base = session.collect_basic_options()
    mid = time.perf_counter()
    adv = session.collect_advanced_options(base)
    end = time.perf_counter()

    # Basic collection should be nearly instant; threshold configurable via env
    threshold = float(os.environ.get("HLPR_PROMPT_THRESHOLD", "0.12"))
    assert (mid - start) < threshold, f"collect_basic_options too slow: {(mid-start):.3f}s"
    # Advanced collection also should be quick
    assert (end - mid) < threshold, f"collect_advanced_options too slow: {(end-mid):.3f}s"
    # Sanity checks
    assert base.provider == "local"
    assert adv.chunk_size == 8192

from hlpr.logging_utils import build_safe_extra, new_context


def test_build_safe_extra_sanitizes_filename():
    ctx = new_context("cid-1")
    extra = build_safe_extra(ctx, file_name="/home/user/secret/report.pdf")
    assert extra["file_name"] == "report.pdf"
    assert extra["correlation_id"] == "cid-1"


def test_build_safe_extra_truncates_error():
    ctx = new_context("cid-2")
    long_err = "x" * 600
    extra = build_safe_extra(ctx, error=long_err)
    assert len(extra["error"]) < len(long_err)
    assert extra["error"].endswith("...[truncated]")

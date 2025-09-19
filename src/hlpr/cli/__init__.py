"""CLI package for hlpr.

Expose the main `app` object so CLI entrypoints can import `hlpr.cli.app`.
This keeps backwards-compatible `hlpr` console scripts working.
"""

from hlpr.cli.main import app

__all__ = ["app"]

import pytest
import sys
from pathlib import Path

# Ensure project root is on sys.path so tests can import `src` package
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def sample_email_text():
    return "Invoice: please pay by EOD"

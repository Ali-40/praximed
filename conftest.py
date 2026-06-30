"""
Root conftest — ensures the praximed directory is on sys.path so that
`from backend.app.xxx import yyy` works without a package install.
"""
import sys
from pathlib import Path

# Insert the repo root (the directory containing this file) at the front of
# sys.path so pytest can resolve the `backend` top-level package.
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

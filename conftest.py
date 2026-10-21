"""Root-level pytest configuration.

Adds the ``backend/`` directory to ``sys.path`` so that ``import app.*``
resolves correctly when pytest is invoked from the project root.  The CI
workflow achieves the same effect via ``PYTHONPATH: backend``; this file
makes local ``pytest tests/`` invocations work without any environment
variable setup.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

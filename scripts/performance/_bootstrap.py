from __future__ import annotations

import sys
from pathlib import Path


def ensure_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "utils.py").exists():
            root = parent
            break
    else:
        root = current.parent

    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return root
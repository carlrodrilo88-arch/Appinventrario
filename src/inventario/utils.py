from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def open_file(path: Path) -> None:
    resolved = path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"No existe el archivo: {resolved}")

    if sys.platform.startswith("win"):
        os.startfile(str(resolved))
        return

    if sys.platform == "darwin":
        subprocess.run(["open", str(resolved)], check=True)
        return

    subprocess.run(["xdg-open", str(resolved)], check=True)

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np


@dataclass(frozen=True)
class Airfoil:
    name: str
    x: np.ndarray
    y: np.ndarray


def read_selig_dat(path: str | Path) -> Airfoil:
    """Read Selig/UIUC .dat airfoil coordinate file."""
    path = Path(path)
    lines = path.read_text(encoding="utf-8", errors="ignore").strip().splitlines()
    if not lines:
        raise ValueError(f"Empty file: {path}")

    name = lines[0].strip() or path.stem
    coords: list[tuple[float, float]] = []

    for line in lines[1:]:
        s = line.strip()
        if not s:
            continue
        parts = s.replace(",", " ").split()
        if len(parts) < 2:
            continue
        try:
            x, y = float(parts[0]), float(parts[1])
        except ValueError:
            continue
        coords.append((x, y))

    if len(coords) < 20:
        raise ValueError(f"Not enough coordinate points parsed from {path} (got {len(coords)})")

    x = np.array([c[0] for c in coords], dtype=float)
    y = np.array([c[1] for c in coords], dtype=float)
    return Airfoil(name=name, x=x, y=y)

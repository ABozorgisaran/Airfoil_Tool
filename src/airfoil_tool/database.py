from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
from typing import Iterable


@dataclass(frozen=True)
class AirfoilDB:
    root: Path

    def list(self) -> list[Path]:
        if not self.root.exists():
            return []
        return sorted(p for p in self.root.glob("*.dat") if p.is_file())

    def names(self) -> list[str]:
        return [p.name for p in self.list()]

    def find(self, query: str) -> list[Path]:
        """Case-insensitive substring match on filename."""
        q = query.strip().lower()
        return [p for p in self.list() if q in p.name.lower()]

    def random(self) -> Path:
        files = self.list()
        if not files:
            raise FileNotFoundError(f"No .dat files found in {self.root}")
        return random.choice(files)         
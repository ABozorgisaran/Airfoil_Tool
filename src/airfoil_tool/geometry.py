from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from .io import Airfoil


@dataclass(frozen=True)
class GeometrySummary:
    name: str
    chord: float
    area: float
    perimeter: float
    max_thickness: float
    x_tmax: float
    max_camber: float
    x_cmax: float
    le_radius_est: float


def le_index(x: np.ndarray) -> int:
    return int(np.argmin(x))


def normalize_to_unit_chord(af: Airfoil) -> Airfoil:
    """Translate so LE is at (0,0) and scale so chord is ~1."""
    x = af.x.copy()
    y = af.y.copy()

    ile = le_index(x)
    x -= x[ile]
    y -= y[ile]

    chord = float(np.max(x) - np.min(x))
    if chord <= 1e-12:
        raise ValueError("Chord appears zero after translation; check coordinates.")

    x /= chord
    y /= chord
    return Airfoil(name=af.name, x=x, y=y)


def split_upper_lower(af: Airfoil):
    """Split closed curve into upper/lower using LE index. Returns monotonic x arrays."""
    x, y = af.x, af.y
    ile = le_index(x)

    xu, yu = x[: ile + 1], y[: ile + 1]
    xl, yl = x[ile:], y[ile:]

    # enforce increasing x for interpolation
    if xu[0] > xu[-1]:
        xu, yu = xu[::-1], yu[::-1]
    if xl[0] > xl[-1]:
        xl, yl = xl[::-1], yl[::-1]

    return xu, yu, xl, yl


def camber_thickness(af: Airfoil, n: int = 400):
    xu, yu, xl, yl = split_upper_lower(af)
    xq = np.linspace(0.0, 1.0, n)

    yuq = np.interp(xq, xu, yu, left=float(yu[0]), right=float(yu[-1]))
    ylq = np.interp(xq, xl, yl, left=float(yl[0]), right=float(yl[-1]))

    camber = 0.5 * (yuq + ylq)
    thickness = (yuq - ylq)
    return xq, camber, thickness


def polygon_area(x: np.ndarray, y: np.ndarray) -> float:
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def polyline_length(x: np.ndarray, y: np.ndarray) -> float:
    dx = np.diff(x)
    dy = np.diff(y)
    return float(np.sum(np.hypot(dx, dy)))


def estimate_le_radius(af: Airfoil) -> float:
    """Rough LE radius estimate using circle-through-3-points around LE."""
    x, y = af.x, af.y
    i = le_index(x)

    i0 = max(i - 2, 0)
    i1 = i
    i2 = min(i + 2, len(x) - 1)

    p0 = np.array([x[i0], y[i0]])
    p1 = np.array([x[i1], y[i1]])
    p2 = np.array([x[i2], y[i2]])

    a = np.linalg.norm(p1 - p2)
    b = np.linalg.norm(p0 - p2)
    c = np.linalg.norm(p0 - p1)

    s = 0.5 * (a + b + c)
    area_sq = max(s * (s - a) * (s - b) * (s - c), 0.0)
    A = math.sqrt(area_sq) if area_sq > 0 else 0.0
    if A < 1e-12:
        return float("nan")
    return float((a * b * c) / (4.0 * A))


def summarize_geometry(af: Airfoil) -> GeometrySummary:
    x, y = af.x, af.y
    chord = float(np.max(x) - np.min(x))
    area = abs(polygon_area(x, y))
    perimeter = polyline_length(x, y)

    xq, cam, th = camber_thickness(af, n=500)
    it = int(np.argmax(th))
    ic = int(np.argmax(np.abs(cam)))

    return GeometrySummary(
        name=af.name,
        chord=chord,
        area=area,
        perimeter=perimeter,
        max_thickness=float(th[it]),
        x_tmax=float(xq[it]),
        max_camber=float(cam[ic]),
        x_cmax=float(xq[ic]),
        le_radius_est=estimate_le_radius(af),
    )

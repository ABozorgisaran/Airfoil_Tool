from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from .io import Airfoil

def solve_vortex_panel(*args, **kwargs):
    print("Vortex panel solver placeholder running...")
    return {
        "CL": 0.5,
        "CD": 0.02
    }

@dataclass(frozen=True)
class PanelSolution:
    alpha_deg: float
    cl: float
    cm_c4: float
    x_coll: np.ndarray
    y_coll: np.ndarray
    cp: np.ndarray


def _close_polygon(x: np.ndarray, y: np.ndarray):
    if abs(x[0] - x[-1]) > 1e-12 or abs(y[0] - y[-1]) > 1e-12:
        x = np.append(x, x[0])
        y = np.append(y, y[0])
    return x, y


def _panel_geom(x: np.ndarray, y: np.ndarray):
    dx = np.diff(x)
    dy = np.diff(y)
    s = np.hypot(dx, dy)
    if np.any(s < 1e-12):
        raise ValueError("Degenerate panel length detected; check coordinates.")

    tx = dx / s
    ty = dy / s
    nx = -ty
    ny = tx

    xc = 0.5 * (x[:-1] + x[1:])
    yc = 0.5 * (y[:-1] + y[1:])
    return dx, dy, s, tx, ty, nx, ny, xc, yc


def induced_velocity_unit_vortex_panel(x1, y1, x2, y2, xp, yp):
    """Velocity induced at P by a constant-strength unit vortex panel."""
    dx = x2 - x1
    dy = y2 - y1
    L = math.hypot(dx, dy)
    cos_t = dx / L
    sin_t = dy / L

    # local coords
    x = (xp - x1) * cos_t + (yp - y1) * sin_t
    y = -(xp - x1) * sin_t + (yp - y1) * cos_t

    eps = 1e-12
    y = y if abs(y) > eps else (eps if y >= 0 else -eps)

    r1 = x * x + y * y
    r2 = (x - L) * (x - L) + y * y

    u_local = (1.0 / (4.0 * math.pi)) * math.log(r2 / r1)
    th1 = math.atan2(y, x)
    th2 = math.atan2(y, x - L)
    v_local = (1.0 / (2.0 * math.pi)) * (th2 - th1)

    # back to global
    u = u_local * cos_t - v_local * sin_t
    v = u_local * sin_t + v_local * cos_t
    return u, v


def solve_vortex_panel(af: Airfoil, alpha_deg: float, v_inf: float = 1.0) -> PanelSolution:
    """
    Inviscid 2D vortex panel method with a simple Kutta condition:
    gamma(TE-upper panel) + gamma(TE-lower panel) = 0
    Assumes .dat order TE->upper->LE->lower->TE.
    """
    x, y = _close_polygon(af.x.copy(), af.y.copy())
    dx, dy, s, tx, ty, nx, ny, xc, yc = _panel_geom(x, y)
    n = len(s)

    a = math.radians(alpha_deg)
    u_inf = v_inf * math.cos(a)
    v_inf_y = v_inf * math.sin(a)

    A = np.zeros((n + 1, n), dtype=float)
    b = np.zeros((n + 1,), dtype=float)

    for i in range(n):
        b[i] = -(u_inf * nx[i] + v_inf_y * ny[i])
        for j in range(n):
            uij, vij = induced_velocity_unit_vortex_panel(
                x[j], y[j], x[j + 1], y[j + 1], xc[i], yc[i]
            )
            A[i, j] = uij * nx[i] + vij * ny[i]

    # Kutta row
    A[-1, 0] = 1.0
    A[-1, -1] = 1.0
    b[-1] = 0.0

    gamma, *_ = np.linalg.lstsq(A, b, rcond=None)

    # tangential velocity and Cp
    vt = np.zeros(n, dtype=float)
    for i in range(n):
        vti = u_inf * tx[i] + v_inf_y * ty[i]
        for j in range(n):
            uij, vij = induced_velocity_unit_vortex_panel(
                x[j], y[j], x[j + 1], y[j + 1], xc[i], yc[i]
            )
            vti += gamma[j] * (uij * tx[i] + vij * ty[i])
        vt[i] = vti

    cp = 1.0 - (vt / v_inf) ** 2

    # integrate pressure to get force coefficients
    dfx = -cp * nx * s
    dfy = -cp * ny * s

    cfx = float(np.sum(dfx))
    cfy = float(np.sum(dfy))

    cl = -cfx * math.sin(a) + cfy * math.cos(a)

    # moment about quarter chord
    x_ref, y_ref = 0.25, 0.0
    cm_c4 = float(np.sum((xc - x_ref) * dfy - (yc - y_ref) * dfx))

    return PanelSolution(alpha_deg=alpha_deg, cl=float(cl), cm_c4=float(cm_c4),
                         x_coll=xc, y_coll=yc, cp=cp)
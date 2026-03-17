from __future__ import annotations
import matplotlib.pyplot as plt

from .panel import PanelSolution


def plot_cp(sol: PanelSolution, title: str = "") -> None:
    plt.figure()
    plt.scatter(sol.x_coll, sol.cp, s=10)
    plt.gca().invert_yaxis()
    plt.grid(True)
    t = title or f"Cp @ alpha={sol.alpha_deg:.2f} deg, CL={sol.cl:.3f}"
    plt.title(t)
    plt.xlabel("x/c")
    plt.ylabel("Cp")
    plt.show()

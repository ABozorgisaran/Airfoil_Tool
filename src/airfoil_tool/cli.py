from __future__ import annotations
from .database import AirfoilDB

import argparse
import csv
from pathlib import Path
import numpy as np

from .io import read_selig_dat
from .geometry import normalize_to_unit_chord, summarize_geometry
from .panel import solve_vortex_panel
from .plotting import plot_cp


def _write_kv_csv(d: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["field", "value"])
        for k, v in d.items():
            w.writerow([k, v])


def cmd_analyze(args: argparse.Namespace) -> int:
    af = normalize_to_unit_chord(read_selig_dat(args.dat))
    s = summarize_geometry(af)

    print(f"\nAirfoil: {s.name}")
    print(f"Chord:            {s.chord:.6f}")
    print(f"Area:             {s.area:.6f}")
    print(f"Perimeter:        {s.perimeter:.6f}")
    print(f"Max thickness:    {s.max_thickness:.6f} at x={s.x_tmax:.3f}")
    print(f"Max camber:       {s.max_camber:.6f} at x={s.x_cmax:.3f}")
    print(f"LE radius (est.): {s.le_radius_est:.6f}\n")

    if args.out:
        _write_kv_csv(s.__dict__, Path(args.out))
        print(f"Saved -> {args.out}")
    return 0


def cmd_polar(args: argparse.Namespace) -> int:
    af = normalize_to_unit_chord(read_selig_dat(args.dat))
    alphas = np.arange(args.alpha_start, args.alpha_end + 1e-12, args.alpha_step)

    rows = []
    for a in alphas:
        sol = solve_vortex_panel(af, float(a))
        rows.append({"alpha_deg": float(a), "cl": sol.cl, "cm_c4": sol.cm_c4})
        print(f"alpha={a:7.3f}  CL={sol.cl: .5f}  Cm(c/4)={sol.cm_c4: .5f}")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["alpha_deg", "cl", "cm_c4"])
            w.writeheader()
            w.writerows(rows)
        print(f"Saved -> {args.out}")

    return 0


def cmd_plot_cp(args: argparse.Namespace) -> int:
    af = normalize_to_unit_chord(read_selig_dat(args.dat))
    sol = solve_vortex_panel(af, args.alpha)
    plot_cp(sol, title=f"{af.name} Cp @ alpha={args.alpha:.2f} deg")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="airfoil-tool", description="Airfoil analysis CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("analyze", help="Geometry summary")
    pa.add_argument("dat", help="Path to airfoil .dat")
    pa.add_argument("--out", help="Write summary CSV")
    pa.set_defaults(func=cmd_analyze)

    pp = sub.add_parser("polar", help="Compute inviscid polar (CL, Cm)")
    pp.add_argument("dat", help="Path to airfoil .dat")
    pp.add_argument("--alpha-start", type=float, default=-4.0)
    pp.add_argument("--alpha-end", type=float, default=12.0)
    pp.add_argument("--alpha-step", type=float, default=1.0)
    pp.add_argument("--out", help="Write polar CSV")
    pp.set_defaults(func=cmd_polar)

    pc = sub.add_parser("plot-cp", help="Plot Cp distribution")
    pc.add_argument("dat", help="Path to airfoil .dat")
    pc.add_argument("--alpha", type=float, default=4.0)
    pc.set_defaults(func=cmd_plot_cp)

        # DB: list
    pl = sub.add_parser("list-db", help="List available airfoils in the local database")
    pl.add_argument("--db", default="data/uiuc", help="Database folder (default: data/uiuc)")
    pl.set_defaults(func=cmd_list_db)

    # DB: find
    pf = sub.add_parser("find-db", help="Find airfoils by filename substring")
    pf.add_argument("query", help="Substring to search for (case-insensitive)")
    pf.add_argument("--db", default="data/uiuc", help="Database folder (default: data/uiuc)")
    pf.add_argument("--limit", type=int, default=50, help="Max results to print")
    pf.set_defaults(func=cmd_find_db)

    # DB: random
    pr = sub.add_parser("random-db", help="Pick a random airfoil and optionally solve at alpha")
    pr.add_argument("--db", default="data/uiuc", help="Database folder (default: data/uiuc)")
    pr.add_argument("--alpha", type=float, default=None, help="If set, compute Cp/CL/Cm at alpha (deg)")
    pr.set_defaults(func=cmd_random_db)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))

def cmd_list_db(args: argparse.Namespace) -> int:
    db = AirfoilDB(Path(args.db))
    files = db.list()
    if not files:
        print(f"No .dat files found in: {args.db}")
        return 1
    for p in files:
        print(p.name)
    print(f"\nTotal: {len(files)} airfoils")
    return 0


def cmd_find_db(args: argparse.Namespace) -> int:
    db = AirfoilDB(Path(args.db))
    hits = db.find(args.query)
    if not hits:
        print("No matches.")
        return 1
    for p in hits[: args.limit]:
        print(p.name)
    if len(hits) > args.limit:
        print(f"... and {len(hits) - args.limit} more")
    return 0


def cmd_random_db(args: argparse.Namespace) -> int:
    db = AirfoilDB(Path(args.db))
    pick = db.random()
    print(f"Random pick: {pick.name}")

    # Reuse your existing commands on the random airfoil:
    af = normalize_to_unit_chord(read_selig_dat(pick))
    s = summarize_geometry(af)
    print(f"Max thickness: {s.max_thickness:.4f} at x/c={s.x_tmax:.3f}")
    print(f"Max camber:    {s.max_camber:.4f} at x/c={s.x_cmax:.3f}")

    if args.alpha is not None:
        sol = solve_vortex_panel(af, args.alpha)
        print(f"alpha={args.alpha:.2f} deg  CL={sol.cl:.4f}  Cm(c/4)={sol.cm_c4:.4f}")
    return 0

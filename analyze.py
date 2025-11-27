from __future__ import annotations

import argparse
import csv
import math
import os
import re
from typing import Dict, List, Optional, Tuple

from utils import choose_experiment, list_experiments

SOLO_DIRNAME = "solo"
COMB_DIRNAME = "comb"

RESULT_LINE_RE = re.compile(
    r"^\s*(?P<name>[^|]+)\|\s*Result:\s*(?P<val>[\d.eE+-]+)\s*$"
)


# ---------- math helpers ----------
def geom_mean(vals: List[float]) -> float:
    """Geometric mean, ignoring non-positive values (shouldn't happen)."""
    v = [float(x) for x in vals if x > 0]
    if not v:
        return 0.0
    logs = [math.log(x) for x in v]
    return math.exp(sum(logs) / len(logs))


def geom_stddev(vals: List[float]) -> float:
    """Geometric stddev as multiplicative factor: exp(std(logs))."""
    v = [float(x) for x in vals if x > 0]
    if len(v) < 2:
        return 1.0  # multiplicative factor 1 => no spread
    logs = [math.log(x) for x in v]
    mean_log = sum(logs) / len(logs)
    var = sum((x - mean_log) ** 2 for x in logs) / (len(logs))  # population var
    std_log = math.sqrt(var)
    return math.exp(std_log)


def parse_result_file(path: str) -> Dict[str, float]:
    """Read a .res file and return dict name->value (can contain multiple lines)"""
    d: Dict[str, float] = {}
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = RESULT_LINE_RE.match(line)
            if not m:
                continue
            name = m.group("name").strip()
            val = float(m.group("val"))
            d[name] = val
    return d


# ---------- collect runs ----------
def collect_solo_runs(solo_folder: str) -> Dict[str, List[float]]:
    """Return dict: name -> [values] from solo/*.res files."""
    data: Dict[str, List[float]] = {}
    if not os.path.isdir(solo_folder):
        return data
    for fname in os.listdir(solo_folder):
        if not fname.endswith(".res"):
            continue
        full = os.path.join(solo_folder, fname)
        parsed = parse_result_file(full)
        # filename: <name>_Execution-<i>.res
        base = fname.rsplit("_Execution-", 1)[0]
        # prefer parsed value if present, else fallback to base name
        if parsed:
            # there may be one line; take value by key for base if exists, else take first
            if base in parsed:
                data.setdefault(base, []).append(parsed[base])
            else:
                # add all parsed values (usually one)
                for v in parsed.values():
                    data.setdefault(base, []).append(v)
        else:
            # no parseable lines — ignore
            continue
    return data


def collect_comb_runs(comb_folder: str) -> Dict[Tuple[str, str], List[float]]:
    """Return dict keyed by ordered pair (A,B) -> list of A's observed values."""
    data: Dict[Tuple[str, str], List[float]] = {}
    if not os.path.isdir(comb_folder):
        return data

    for fname in os.listdir(comb_folder):
        if not fname.endswith(".res") or "_vs_" not in fname:
            continue

        full = os.path.join(comb_folder, fname)
        base = fname.rsplit("_Execution-", 1)[0]

        try:
            nameA, nameB = base.split("_vs_", 1)
        except ValueError:
            continue

        parsed = parse_result_file(full)

        # get A
        valA = parsed.get(nameA)
        if valA is None:
            for k, v in parsed.items():
                if k == nameA or k.startswith(nameA):
                    valA = v
                    break

        # get B
        valB = parsed.get(nameB)
        if valB is None:
            for k, v in parsed.items():
                if k == nameB or k.startswith(nameB):
                    valB = v
                    break

        # insert only once when A == B
        # avoid double counting when A == B.
        if nameA == nameB:
            if valA is not None:
                data.setdefault((nameA, nameA), []).append(valA)
            continue

        # normal case (A != B)
        if valA is not None:
            data.setdefault((nameA, nameB), []).append(valA)
        if valB is not None:
            data.setdefault((nameB, nameA), []).append(valB)

    return data


# ---------- analysis ----------
def analyze_experiment(
    exp_path: str, out_csv: str = "matrix.csv", stats_csv: str = "stats.csv"
):
    solo_folder = os.path.join(exp_path, SOLO_DIRNAME)
    comb_folder = os.path.join(exp_path, COMB_DIRNAME)

    solo_runs = collect_solo_runs(solo_folder)
    comb_runs = collect_comb_runs(comb_folder)

    workloads = sorted(solo_runs.keys())
    if not workloads:
        print("Cant find solo-run workloads in ", solo_folder)
        return

    # compute solo stats
    solo_stats = {}
    for w in workloads:
        vals = solo_runs.get(w, [])
        gm = geom_mean(vals) if vals else 0.0
        gstd = geom_stddev(vals) if vals else 1.0
        solo_stats[w] = {"n": len(vals), "geom_mean": gm, "geom_std": gstd}

    # compute comb stats (for ordered pairs)
    comb_stats = {}  # (A,B) -> {n, geom_mean, geom_std}
    for A in workloads:
        for B in workloads:
            key = (A, B)
            vals = comb_runs.get(key, [])
            if vals:
                gm = geom_mean(vals)
                gstd = geom_stddev(vals)
                comb_stats[key] = {"n": len(vals), "geom_mean": gm, "geom_std": gstd}
            else:
                # leave absent if no data
                pass

    # build matrix of impact %
    matrix: Dict[str, Dict[str, Optional[float]]] = {}
    for A in workloads:
        matrix[A] = {}
        A_solo = solo_stats[A]["geom_mean"]
        for B in workloads:
            if A == B:
                # check if we have A with A data (self interference)
                s = comb_stats.get((A, A))
                if s:
                    ratio = s["geom_mean"] / A_solo if A_solo else None
                else:
                    ratio = None
            else:
                s = comb_stats.get((A, B))
                if s:
                    ratio = s["geom_mean"] / A_solo if A_solo else None
                else:
                    ratio = None
            if ratio is None:
                matrix[A][B] = None
            else:
                matrix[A][B] = (ratio - 1.0) * 100.0  # percent change

    # --- print summary ---
    print("\nSelected experiment:", os.path.basename(exp_path))
    print("Solo workloads (geom mean, geom std (factor), n):")
    for w in workloads:
        s = solo_stats[w]
        # convert geom_std factor to percent approx: (gstd - 1) * 100
        gstd_pct = (s["geom_std"] - 1.0) * 100.0
        print(
            f"  {w:20s} mean={s['geom_mean']:.3f}  gstd_factor={s['geom_std']:.3f} (~{gstd_pct:.1f}%)  n={s['n']}"
        )

    print("\nPair stats (only present pairs):")
    for (A, B), s in sorted(comb_stats.items()):
        gstd_pct = (s["geom_std"] - 1.0) * 100.0
        print(
            f"  {A:12s} w/ {B:12s} mean={s['geom_mean']:.3f}  gstd_factor={s['geom_std']:.3f} (~{gstd_pct:.1f}%)  n={s['n']}"
        )

    # --- print matrix ---
    print(
        "\nImpact matrix:"
        "\n(Performance impact of A when runned in same process as B)"
        "\n(row = workload A, column = workload B)"
    )
    hdr = "A\\B".ljust(20) + "".join(b.rjust(12) for b in workloads)
    print(hdr)
    for A in workloads:
        row = A.ljust(20)
        for B in workloads:
            v = matrix[A][B]
            if v is None:
                row += "   -".rjust(12)
            else:
                row += f"{v:11.2f}%"
        print(row)

    # --- write CSVs ---
    # matrix CSV
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([""] + workloads)
        for A in workloads:
            row = [A]
            for B in workloads:
                v = matrix[A][B]
                if v is None:
                    row.append("")
                else:
                    row.append(f"{v:.6f}")
            w.writerow(row)
    print(f"\nMatrix CSV written to: {out_csv}")

    # detailed stats CSV
    with open(stats_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["type", "workload_A", "workload_B", "n", "geom_mean", "geom_std_factor"]
        )
        for wname, s in solo_stats.items():
            w.writerow(
                [
                    "solo",
                    wname,
                    "",
                    s["n"],
                    f"{s['geom_mean']:.9g}",
                    f"{s['geom_std']:.9g}",
                ]
            )
        for (A, B), s in comb_stats.items():
            w.writerow(
                ["pair", A, B, s["n"], f"{s['geom_mean']:.9g}", f"{s['geom_std']:.9g}"]
            )
    print(f"Stats CSV written to: {stats_csv}")

    return {
        "workloads": workloads,
        "solo_stats": solo_stats,
        "comb_stats": comb_stats,
        "matrix": matrix,
    }


def analyze():
    p = argparse.ArgumentParser()
    p.add_argument("--res", default="./res", help="res dir (default ./res)")
    p.add_argument(
        "--identifier",
        help="Experiment identifier. (Just a nametag)",
    )
    args = p.parse_args()

    if args.identifier is None:
        exps = list_experiments(args.res)
        chosen = choose_experiment(exps)
        if not chosen:
            return
        _, path, _ = chosen
    else:
        path = os.path.join(args.res, args.identifier)

    analyze_experiment(
        path,
        out_csv=os.path.join(path, "matrix.csv"),
        stats_csv=os.path.join(path, "stats.csv"),
    )


if __name__ == "__main__":
    analyze()

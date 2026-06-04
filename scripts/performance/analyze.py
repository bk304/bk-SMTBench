from __future__ import annotations

from _bootstrap import ensure_project_root

PROJECT_ROOT = ensure_project_root()

import argparse
import csv
import math
import os
import re
from typing import Dict, List, Optional, Tuple

from utils import choose_experiment, list_experiments

SOLO_DIRNAME = "solo"
COMB_DIRNAME = "comb"

# Regex to match lines like "workload_name | IPC: 1.23"
RESULT_LINE_RE = re.compile(r"^\s*(?P<name>[^|]+)\|\s*(?P<rest>.*)$")


def geom_mean(vals: List[float]) -> float:
    values = [float(x) for x in vals if x > 0]
    if not values:
        return 0.0
    logs = [math.log(x) for x in values]
    return math.exp(sum(logs) / len(logs))


def geom_stddev(vals: List[float]) -> float:
    values = [float(x) for x in vals if x > 0]
    if len(values) < 2:
        return 1.0
    logs = [math.log(x) for x in values]
    mean_log = sum(logs) / len(logs)
    var = sum((x - mean_log) ** 2 for x in logs) / len(logs)
    return math.exp(math.sqrt(var))


def parse_result_file(path: str) -> Dict[str, float]:
    values: Dict[str, float] = {}
    with open(path, "r", encoding="utf-8", errors="ignore") as file_handle:
        for line in file_handle:
            match = RESULT_LINE_RE.match(line)
            if not match:
                continue
            name = match.group("name").strip()
            rest = match.group("rest")
            ipc_match = re.search(
                r"IPC:\s*([0-9]*\.?[0-9]+(?:[eE][+-]?\d+)?)",
                rest,
                re.IGNORECASE,
            )
            if not ipc_match:
                continue
            try:
                values[name] = float(ipc_match.group(1))
            except ValueError:
                continue
    return values


def collect_solo_runs(solo_folder: str) -> Dict[str, List[float]]:
    data: Dict[str, List[float]] = {}
    if not os.path.isdir(solo_folder):
        return data

    for fname in os.listdir(solo_folder):
        if not fname.endswith(".res"):
            continue
        full_path = os.path.join(solo_folder, fname)
        parsed = parse_result_file(full_path)
        workload_name = fname.rsplit("_Execution-", 1)[0]
        if not parsed:
            continue

        if workload_name in parsed:
            data.setdefault(workload_name, []).append(parsed[workload_name])
            continue

        for value in parsed.values():
            data.setdefault(workload_name, []).append(value)

    return data


def collect_comb_runs(comb_folder: str) -> Dict[Tuple[str, str], List[float]]:
    data: Dict[Tuple[str, str], List[float]] = {}
    if not os.path.isdir(comb_folder):
        return data

    for fname in os.listdir(comb_folder):
        if not fname.endswith(".res") or "_vs_" not in fname:
            continue

        full_path = os.path.join(comb_folder, fname)
        base_name = fname.rsplit("_Execution-", 1)[0]

        try:
            name_a, name_b = base_name.split("_vs_", 1)
        except ValueError:
            continue

        parsed = parse_result_file(full_path)

        value_a = parsed.get(name_a)
        if value_a is None:
            for parsed_name, parsed_value in parsed.items():
                if parsed_name == name_a or parsed_name.startswith(name_a):
                    value_a = parsed_value
                    break

        value_b = parsed.get(name_b)
        if value_b is None:
            for parsed_name, parsed_value in parsed.items():
                if parsed_name == name_b or parsed_name.startswith(name_b):
                    value_b = parsed_value
                    break

        if name_a == name_b:
            if value_a is not None:
                data.setdefault((name_a, name_a), []).append(value_a)
            continue

        if value_a is not None:
            data.setdefault((name_a, name_b), []).append(value_a)
        if value_b is not None:
            data.setdefault((name_b, name_a), []).append(value_b)

    return data


def _ordered_workloads(solo_runs: Dict[str, List[float]]) -> List[str]:
    return sorted(solo_runs.keys())


def _build_pair_matrix(
    workloads: List[str],
    pair_stats: Dict[Tuple[str, str], Dict[str, float]],
) -> Dict[str, Dict[str, Optional[float]]]:
    matrix: Dict[str, Dict[str, Optional[float]]] = {}
    for workload_a in workloads:
        matrix[workload_a] = {}
        for workload_b in workloads:
            stats = pair_stats.get((workload_a, workload_b))
            matrix[workload_a][workload_b] = stats["geom_mean"] if stats else None
    return matrix


def _write_section_header(writer: csv.writer, name: str) -> None:
    writer.writerow(["table", name])


def _write_stats_table(
    writer: csv.writer,
    solo_stats: Dict[str, Dict[str, float]],
    workloads: List[str],
) -> None:
    _write_section_header(writer, "solo_ipc_stats")
    writer.writerow(["workload", "geom_mean_ipc", "geom_stdev_ipc", "n"])
    for workload in workloads:
        stats = solo_stats[workload]
        writer.writerow(
            [
                workload,
                f"{stats['geom_mean']:.9g}",
                f"{stats['geom_std']:.9g}",
                stats["n"],
            ]
        )
    writer.writerow([])


def _write_matrix_table(
    writer: csv.writer,
    name: str,
    workloads: List[str],
    matrix: Dict[str, Dict[str, Optional[float]]],
) -> None:
    _write_section_header(writer, name)
    writer.writerow(["workload"] + workloads)
    for workload_a in workloads:
        row = [workload_a]
        for workload_b in workloads:
            value = matrix[workload_a][workload_b]
            row.append("" if value is None else f"{value:.9g}")
        writer.writerow(row)
    writer.writerow([])


def _build_ideal_matrix(
    workloads: List[str], solo_stats: Dict[str, Dict[str, float]]
) -> Dict[str, Dict[str, float]]:
    matrix: Dict[str, Dict[str, float]] = {}
    for workload_a in workloads:
        matrix[workload_a] = {}
        for workload_b in workloads:
            matrix[workload_a][workload_b] = (
                solo_stats[workload_a]["geom_mean"] + solo_stats[workload_b]["geom_mean"]
            )
    return matrix


def _build_real_total_matrix(
    workloads: List[str], pair_matrix: Dict[str, Dict[str, Optional[float]]]
) -> Dict[str, Dict[str, Optional[float]]]:
    matrix: Dict[str, Dict[str, Optional[float]]] = {}
    for workload_a in workloads:
        matrix[workload_a] = {}
        for workload_b in workloads:
            value_a = pair_matrix[workload_a][workload_b]
            value_b = pair_matrix[workload_b][workload_a]
            if value_a is None or value_b is None:
                matrix[workload_a][workload_b] = None
            else:
                matrix[workload_a][workload_b] = value_a + value_b
    return matrix


def _build_delta_matrix(
    workloads: List[str],
    ideal_matrix: Dict[str, Dict[str, float]],
    real_matrix: Dict[str, Dict[str, Optional[float]]],
) -> Dict[str, Dict[str, Optional[float]]]:
    matrix: Dict[str, Dict[str, Optional[float]]] = {}
    for workload_a in workloads:
        matrix[workload_a] = {}
        for workload_b in workloads:
            ideal = ideal_matrix[workload_a][workload_b]
            real = real_matrix[workload_a][workload_b]
            if ideal == 0 or real is None:
                matrix[workload_a][workload_b] = None
            else:
                matrix[workload_a][workload_b] = ((real - ideal) / ideal) * 100.0
    return matrix

def _build_ipc_delta_matrix(
    workloads: List[str],
    pair_matrix: Dict[str, Dict[str, Optional[float]]],
    solo_stats: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, Optional[float]]]:
    matrix: Dict[str, Dict[str, Optional[float]]] = {}
    for a in workloads:
        matrix[a] = {}
        ipc_solo = solo_stats[a]["geom_mean"]

        for b in workloads:
            ipc_co = pair_matrix[a][b]

            if ipc_co is None or ipc_solo == 0:
                matrix[a][b] = None
            else:
                matrix[a][b] = ((ipc_co - ipc_solo) / ipc_solo) * 100.0
    return matrix


def analyze_experiment(exp_path: str, result_csv: str = "result.csv"):
    solo_folder = os.path.join(exp_path, SOLO_DIRNAME)
    comb_folder = os.path.join(exp_path, COMB_DIRNAME)

    solo_runs = collect_solo_runs(solo_folder)
    comb_runs = collect_comb_runs(comb_folder)

    workloads = _ordered_workloads(solo_runs)
    if not workloads:
        print("Cant find solo-run workloads in ", solo_folder)
        return

    solo_stats: Dict[str, Dict[str, float]] = {}
    for workload in workloads:
        values = solo_runs.get(workload, [])
        solo_stats[workload] = {
            "n": len(values),
            "geom_mean": geom_mean(values) if values else 0.0,
            "geom_std": geom_stddev(values) if values else 1.0,
        }

    pair_stats: Dict[Tuple[str, str], Dict[str, float]] = {}
    for workload_a in workloads:
        for workload_b in workloads:
            values = comb_runs.get((workload_a, workload_b), [])
            if not values:
                continue
            pair_stats[(workload_a, workload_b)] = {
                "n": len(values),
                "geom_mean": geom_mean(values),
                "geom_std": geom_stddev(values),
            }

    pair_matrix = _build_pair_matrix(workloads, pair_stats)
    ideal_matrix = _build_ideal_matrix(workloads, solo_stats)
    real_matrix = _build_real_total_matrix(workloads, pair_matrix)
    delta_matrix = _build_delta_matrix(workloads, ideal_matrix, real_matrix)
    ipc_delta_matrix = _build_ipc_delta_matrix(workloads, pair_matrix, solo_stats)

    print("\nSelected experiment:", os.path.basename(exp_path))
    print("Solo workloads (geom mean, geom std (factor), n):")
    for workload in workloads:
        stats = solo_stats[workload]
        gstd_pct = (stats["geom_std"] - 1.0) * 100.0
        print(
            f"  {workload:20s} mean={stats['geom_mean']:.3f}  gstd_factor={stats['geom_std']:.3f} (~{gstd_pct:.1f}%)  n={stats['n']}"
        )

    print("\nPair IPC matrix (geom mean IPC of workload A when paired with workload B):")
    hdr = "A\\B".ljust(20) + "".join(workload.rjust(12) for workload in workloads)
    print(hdr)
    for workload_a in workloads:
        row = workload_a.ljust(20)
        for workload_b in workloads:
            value = pair_matrix[workload_a][workload_b]
            row += ("   -".rjust(12) if value is None else f"{value:11.2f}")
        print(row)

    result_path = os.path.join(exp_path, result_csv)
    with open(result_path, "w", newline="", encoding="utf-8") as file_handle:
        writer = csv.writer(file_handle)
        _write_stats_table(writer, solo_stats, workloads)
        _write_matrix_table(writer, "pair_ipc_matrix", workloads, pair_matrix)
        _write_matrix_table(writer, "ideal_ipc_matrix", workloads, ideal_matrix)
        _write_matrix_table(writer, "real_ipc_matrix", workloads, real_matrix)
        _write_matrix_table(writer, "ideal_to_real_delta_percent_matrix", workloads, delta_matrix)
        _write_matrix_table(writer, "ipc_delta_percent_matrix", workloads, ipc_delta_matrix)


    print(f"\nResult CSV written to: {result_path}")

    return {
        "workloads": workloads,
        "solo_stats": solo_stats,
        "pair_stats": pair_stats,
        "pair_matrix": pair_matrix,
        "ideal_matrix": ideal_matrix,
        "real_matrix": real_matrix,
        "delta_matrix": delta_matrix,
        "ipc_delta_matrix": ipc_delta_matrix,
    }


def analyze():
    parser = argparse.ArgumentParser()
    parser.add_argument("--res", default="./res", help="res dir (default ./res)")
    parser.add_argument("--identifier", help="Experiment identifier. (Just a nametag)")
    parser.add_argument("--out", default="result.csv", help="output CSV filename")
    args = parser.parse_args()

    if args.identifier is None:
        exps = list_experiments(args.res)
        chosen = choose_experiment(exps)
        if not chosen:
            return
        _, path, _ = chosen
    else:
        path = os.path.join(args.res, args.identifier)

    analyze_experiment(path, result_csv=args.out)


if __name__ == "__main__":
    analyze()
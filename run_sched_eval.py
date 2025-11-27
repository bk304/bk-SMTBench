import argparse
import glob
import json
import os
import subprocess
import time
from typing import List

from utils import choose_experiment, list_experiments

DEFAULT_DURATION = 10
DEFAULT_PAUSE = 1.0  # small delay between executions just to avoid "noise"
DEFAULT_PROFILE_NAME = "sched_eval_profile.json"


def load_sets(json_path: str) -> List[List[str]]:
    with open(json_path, "r") as f:
        data = json.load(f)
    raw_sets = data.get("sets", data)
    normalized = []
    for item in raw_sets:
        if isinstance(item, list):
            normalized.append(item)
        elif isinstance(item, dict):
            # Looking for keys "members" or "set" or "workloads"
            if "members" in item and isinstance(item["members"], list):
                normalized.append(item["members"])
            elif "workloads" in item and isinstance(item["workloads"], list):
                normalized.append(item["workloads"])
            else:
                # Trying to extract any list inside the dictonary
                lists = [v for v in item.values() if isinstance(v, list)]
                if lists:
                    normalized.append(lists[0])
                else:
                    raise ValueError(f"Unable to interpret item from set: {item}")
        else:
            raise ValueError(f"Invalid format in file of sets: {item}")
    return normalized


def load_workloads_from_bin(bin_folder: str):
    bins = glob.glob(os.path.join(bin_folder, "*.out"))
    mapping = {os.path.basename(b).replace(".out", ""): b for b in bins}
    return mapping  # name -> path


def run_single_set(set_id: int, workload_paths: List[str], duration: int):
    """
    Run all binaries from a set as subprocess.
    There is no taskset to let the scheduler decide.
    Everything is beening throw in /dev/null
    """
    procs = []
    for path in workload_paths:
        cmd = [path, str(duration)]
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(p)
    for p in procs:
        p.wait()


def main():
    p = argparse.ArgumentParser(
        description="Run scheduler-eval workloads from generated sets"
    )
    p.add_argument("--bin", default="./bin", help="bin dir (default ./bin)")
    p.add_argument("--res", default="./res", help="res dir (default ./res)")
    p.add_argument(
        "--profile",
        help="JSON generated with gen_sched_eval_profile.py",
    )
    p.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_DURATION,
        help="Duration for each workload in seconds",
    )
    p.add_argument(
        "--iterations", type=int, default=1, help="How many times to repeat each set"
    )
    p.add_argument(
        "--pause",
        type=float,
        default=DEFAULT_PAUSE,
        help="Delay between each execution of a set",
    )
    args = p.parse_args()

    if args.profile is None:
        exps = list_experiments(args.res)
        chosen = choose_experiment(exps)
        if not chosen:
            return
        _, path, _ = chosen
        profile_path = os.path.join(path, DEFAULT_PROFILE_NAME)
    else:
        profile_path = args.profile

    print(f"Loading sets: {profile_path}")
    sets = load_sets(profile_path)

    print(f"Loading workloads: {args.bin}")
    name2path = load_workloads_from_bin(args.bin)
    available_names = set(name2path.keys())
    print(
        f"Workloads avaliable ({len(available_names)}): {sorted(list(available_names))}"
    )

    # validading if all names appear in bin
    missing = set()
    for s in sets:
        for wl in s:
            if wl not in available_names:
                missing.add(wl)
    if missing:
        print(
            "ERROR: These workloads are missing (did you forgot to compile them with make?): ",
            args.bin,
        )
        for m in sorted(missing):
            print("  -", m)
        print("Check the names in generated_sets.json vs ./bin/*.out")
        return

    # Converting set names to paths
    sets_paths = []
    for s in sets:
        sets_paths.append([name2path[wl] for wl in s])

    total_runs = len(sets_paths) * args.iterations
    print(f"{len(sets_paths)} sets loaded. Total planned executions: {total_runs}\n")

    start_time = time.time()
    run_id = 0

    for iteration in range(args.iterations):
        for i, workloads in enumerate(sets_paths):
            run_id += 1
            elapsed = int(time.time() - start_time)
            remaining = (total_runs * args.duration) - elapsed
            if remaining < 0:
                remaining = 0
            hrs = remaining // 3600
            mins = (remaining % 3600) // 60
            secs = remaining % 60

            print(
                f"[{run_id}/{total_runs}] ETA: {hrs}h {mins}m {secs}s "
                f"=> Executing set {i + 1}/{len(sets_paths)} ({len(workloads)} workloads)"
            )

            run_single_set(i, workloads, args.duration)
            time.sleep(args.pause)

    print("\nDone!")


if __name__ == "__main__":
    main()

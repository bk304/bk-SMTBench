import os
from datetime import datetime
from typing import List, Optional, Tuple


def read_workloads_from_bin(bin_dir: str, keep_extension: bool = True) -> list[str]:
    """
    Scan a directory for workload binaries (.out files).
    """
    files = sorted(f for f in os.listdir(bin_dir) if f.endswith(".out"))
    if keep_extension:
        return files
    return [os.path.splitext(f)[0] for f in files]


def get_unique_smt_groups():
    base = "/sys/devices/system/cpu"
    groups = set()

    for name in os.listdir(base):
        if not name.startswith("cpu"):
            continue
        num = name[3:]
        if not num.isdigit():
            continue

        topo_path = f"{base}/{name}/topology/thread_siblings_list"

        if not os.path.exists(topo_path):
            continue

        with open(topo_path, "r") as f:
            content = f.read().strip()

        ids = []
        for part in content.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                ids.extend(range(start, end + 1))
            else:
                ids.append(int(part))

        groups.add(tuple(sorted(ids)))

    return sorted(groups)


def list_experiments(res_root: str) -> List[Tuple[str, str, float]]:
    """Return list of (name, full_path, mtime) for subfolders in res_root sorted by mtime ascending."""
    if not os.path.isdir(res_root):
        return []
    out = []
    for name in os.listdir(res_root):
        full = os.path.join(res_root, name)
        if os.path.isdir(full):
            try:
                mtime = os.path.getmtime(full)
            except OSError:
                mtime = 0.0
            out.append((name, full, mtime))
    out.sort(key=lambda x: x[2])
    return out


def choose_experiment(
    experiments: List[Tuple[str, str, float]],
) -> Optional[Tuple[str, str, float]]:
    if not experiments:
        print("No experiment found. You need to run runner.py first.")
        return None
    print("Experiments found:")
    for idx, (name, full, mtime) in enumerate(experiments, start=1):
        dt = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {idx:>2}: {name}  (modified: {dt})")
    default_idx = len(experiments)
    prompt = f"\nChoose an experiment [1-{default_idx}] (ENTER = {default_idx} — {experiments[-1][0]}): "
    while True:
        choice = input(prompt).strip()
        if choice == "":
            return experiments[-1]
        if choice.isdigit():
            i = int(choice)
            if 1 <= i <= default_idx:
                return experiments[i - 1]
        print(
            "Invalid choise. Write a valid number or just press Enter to select the last experiment."
        )

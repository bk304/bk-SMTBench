import glob
import os
import subprocess
import time

DEFAULT_ITERATIONS = 1
DEFAULT_DURATION = 10

BIN_FOLDER = "./bin"
RES_FOLDER = "./res"
RES_SOLO_FOLDER = "solo"
RES_COMB_FOLDER = "comb"


def combinations(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i] += 1
        for j in range(i + 1, r):
            indices[j] = indices[i]
        yield tuple(pool[i] for i in indices)


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


def execute():
    num_iterations = input(f"Number of executions [default={DEFAULT_ITERATIONS}]: ")
    duration = input(f"Duration [default={DEFAULT_DURATION}]: ")
    experiment_identifier = input("Experiment identifier: ")

    if num_iterations == "":
        num_iterations = DEFAULT_ITERATIONS
    if duration == "":
        duration = DEFAULT_DURATION

    num_iterations = int(num_iterations)

    if not os.path.isdir(BIN_FOLDER) or not os.listdir(BIN_FOLDER):
        print(f"Missing binaries at {BIN_FOLDER}")
        exit(-1)

    # GCC version
    version_full_text = subprocess.run(
        ["gcc", "--version"], capture_output=True, text=True
    ).stdout.strip()
    version_full_text = version_full_text.split("\n")[0]

    # Parameters read
    print(f"Interations: {num_iterations}")
    print(f"Duration: {duration}")
    print(f"Executables folder: {BIN_FOLDER}")
    print(f"Results folder: {RES_FOLDER}")
    print(f"GCC version: {version_full_text}")

    # Create required folders
    os.makedirs(RES_FOLDER, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    experiment_dir = os.path.join(RES_FOLDER, f"{experiment_identifier}_{timestamp}")
    experiment_solo_dir = os.path.join(experiment_dir, RES_SOLO_FOLDER)
    experiment_comb_dir = os.path.join(experiment_dir, RES_COMB_FOLDER)
    os.makedirs(experiment_dir, exist_ok=False)
    os.makedirs(experiment_solo_dir, exist_ok=False)
    os.makedirs(experiment_comb_dir, exist_ok=False)
    print(f"Results will be saved in: {experiment_dir}\n")

    cpus = get_unique_smt_groups()
    cpu0, cpu1 = cpus[0]
    print(f"Using only the physical core: SMT pair = ({cpu0}, {cpu1})")

    # ========================= Execution ==============================

    print("Executing experiments...")
    binaries = glob.glob(f"{BIN_FOLDER}/*.out")
    total_binaries = len(binaries)
    print(f"{total_binaries} executables found..")
    binary_pairs = list(combinations(binaries, 2))
    total_combinations = len(binary_pairs) * num_iterations
    print(f"{total_combinations} binaries combinations..")

    total_planned_executions = total_binaries + total_combinations
    print(f"Total number of planned executions: {total_planned_executions}\n")

    estimated_total_seconds = float(total_planned_executions * float(duration))
    print(f"Estimated total time: ~{estimated_total_seconds / 60:.2f} minutes")

    start_time = time.time()
    current_run = 0

    # ========================= Solo ===================================

    for bin in binaries:
        for it in range(num_iterations):
            current_run += 1
            elapsed = time.time() - start_time
            remaining = estimated_total_seconds - int(elapsed)

            name = os.path.basename(bin).replace(".out", "")
            result_file = f"{name}_Execution-{it}.res"
            out_path = os.path.join(experiment_solo_dir, result_file)

            hrs = int(remaining // 3600)
            mins = int((remaining % 3600) // 60)
            secs = int(remaining % 60)
            print(
                (
                    f"[({current_run}/{total_planned_executions}) Estimated remainder: {hrs}h {mins}m {secs}s] "
                    f">> Executing ({bin} @ cpu{cpu0})"
                )
            )

            with open(out_path, "w") as output_file:
                # processo 1: binA em cpu0
                pA = subprocess.Popen(
                    ["taskset", "-c", str(cpu0), bin, str(duration)],
                    stdout=output_file,
                )

                pA.wait()

    # ========================= Combined ===============================

    for binA, binB in binary_pairs:
        for it in range(num_iterations):
            current_run += 1
            elapsed = time.time() - start_time
            remaining = estimated_total_seconds - int(elapsed)

            nameA = os.path.basename(binA).replace(".out", "")
            nameB = os.path.basename(binB).replace(".out", "")
            result_file = f"{nameA}_vs_{nameB}_Execution-{it}.res"
            out_path = os.path.join(experiment_comb_dir, result_file)

            hrs = int(remaining // 3600)
            mins = int((remaining % 3600) // 60)
            secs = int(remaining % 60)
            print(
                (
                    f"[({current_run}/{total_planned_executions}) Estimated remainder: {hrs}h {mins}m {secs}s] "
                    f">> Executing ({binA} @ cpu{cpu0}) e ({binB} @ cpu{cpu1})"
                )
            )

            with open(out_path, "w") as output_file:
                # processo 1: binA em cpu0
                pA = subprocess.Popen(
                    ["taskset", "-c", str(cpu0), binA, str(duration)],
                    stdout=output_file,
                )

                # processo 2: binB em cpu1
                pB = subprocess.Popen(
                    ["taskset", "-c", str(cpu1), binB, str(duration)],
                    stdout=output_file,
                )

                pA.wait()
                pB.wait()
    print("\nExperiments completed!")


if __name__ == "__main__":
    execute()

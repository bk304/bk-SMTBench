import subprocess
import os
import glob

DEFAULT_ITERATIONS = 1
DEFAULT_DURATION = 10
DEFAULT_BIN_FOLDER = "./bin"
DEFAULT_RES_FOLDER = "./res"


def combinations(iterable, r):
    # combinations('ABCD', 2) → AB AC AD BC BD CD
    # combinations(range(4), 3) → 012 013 023 123

    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))

    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i + 1, r):
            indices[j] = indices[j - 1] + 1
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

        cpu_id = int(num)
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
    bin_folder = input(f"Execs folder [default={DEFAULT_BIN_FOLDER}]: ")
    res_folder = input(f"Results folder [default={DEFAULT_RES_FOLDER}]: ")
    experiment_identifier = input("Experiment identifier: ")

    if num_iterations == "":
        num_iterations = DEFAULT_ITERATIONS
    if duration == "":
        duration = DEFAULT_DURATION
    if bin_folder == "":
        bin_folder = DEFAULT_BIN_FOLDER
    if res_folder == "":
        res_folder = DEFAULT_RES_FOLDER

    num_iterations = int(num_iterations)

    if not os.path.isdir(bin_folder) or not os.listdir(bin_folder):
        print(f"Missing binaries at {bin_folder}")
        exit(-1)

    # GCC version
    version_full_text = subprocess.run(
        ["gcc", "--version"], capture_output=True, text=True
    ).stdout.strip()
    version_full_text = version_full_text.split("\n")[0]

    # Parameters read
    print(f"Executions: {duration}")
    print(f"Executables folder: {bin_folder}")
    print(f"Results folder: {res_folder}")
    print(f"GCC version: {version_full_text}")

    # Create required folder
    os.makedirs(res_folder, exist_ok=True)

    print("Executing experiments...")
    binaries = glob.glob(f"{bin_folder}/*.out")
    print(f"{len(binaries)} executables found..")

    cpus = get_unique_smt_groups()
    cpu0, cpu1 = cpus[0]
    print(f"Usando apenas o núcleo físico: SMT pair = ({cpu0}, {cpu1})")

    for binA, binB in combinations(binaries, 2):
        for it in range(num_iterations):
            # nome do arquivo de log
            nameA = os.path.basename(binA).replace(".out", "")
            nameB = os.path.basename(binB).replace(".out", "")
            result_file = f"{nameA}_vs_{nameB}_Execution-{it}.Experiment-{experiment_identifier}.res"
            out_path = f"{res_folder}/{result_file}"

            print(f">> Rodando ({binA} @ cpu{cpu0}) e ({binB} @ cpu{cpu1})")

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


if __name__ == "__main__":
    execute()

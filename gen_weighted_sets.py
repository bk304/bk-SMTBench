import argparse
import csv
import itertools
import json
import os
import random
from collections import defaultdict
from math import comb


def read_workloads_from_bin(bin_dir="./bin"):
    bins = sorted(f for f in os.listdir(bin_dir) if f.endswith(".out"))
    names = [os.path.splitext(f)[0] for f in bins]
    return names


def read_matrix_csv(path):
    """
    Read matrix.csv from path.
    Returns dict-of-dict: mat[row][col] = float(value)
    """
    mat = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        hdr = next(reader)
        # hdr[0] is empty (index column), hdr[1:] are col names
        cols = [c.strip() for c in hdr[1:]]
        for row in reader:
            if not row:
                continue
            rowname = row[0].strip()
            values = row[1 : 1 + len(cols)]
            mat[rowname] = {}
            for c, v in zip(cols, values):
                try:
                    mat[rowname][c] = float(v)
                except ValueError:
                    raise ValueError(f"Maybe matrix.csv is formated wrong: {v!r}")
    return mat


def build_pair_weights(workloads, mat):
    """
    pair_weight(a,b) = ( |mat[a][b]| + |mat[b][a]| ) / 2
    Returns dict keyed by frozenset({a,b}) -> weight (float)
    """
    weights = {}
    for i, a in enumerate(workloads):
        for b in workloads[i + 1 :]:
            v_ab = abs(mat.get(a, {}).get(b, 0.0))
            v_ba = abs(mat.get(b, {}).get(a, 0.0))
            w = (v_ab + v_ba) / 2.0
            weights[frozenset((a, b))] = w
    return weights


def score_set(candidate, pair_weights, occurrences):
    """
    candidate: list of names
    score is sum over pairs w * 1/(1+occurrences[pair]) so undercovered pairs count more
    """
    s = 0.0
    for x, y in itertools.combinations(candidate, 2):
        key = frozenset((x, y))
        w = pair_weights.get(key, 0.0)
        s += w / (1.0 + occurrences.get(key, 0))
    return s


def generate_sets(
    workloads,
    pair_weights,
    k=16,
    M=100,
    tries=2000,
    seed=42,
    max_allow_top=None,
    top_list=None,
):
    """
    Generate up to M sets with k lenght.
    - tries: how many random candidates will be avaliated per set (more = better)
    - max_allow_top & top_list: optional. limit how many 'top' (worst case) per set
    """
    random.seed(seed)
    n = len(workloads)
    if k > n:
        raise ValueError("k must be less than the number of avaliable workloads")
    occurrences = defaultdict(int)  # counts how many times a pair already appeared
    sets = []
    all_pairs = set(pair_weights.keys())

    for idx in range(M):
        best = None
        best_score = -1.0
        for _ in range(tries):
            cand = random.sample(workloads, k)
            # optional
            if max_allow_top and top_list:
                top_cnt = sum(1 for w in cand if w in top_list)
                if top_cnt > max_allow_top:
                    continue
            sc = score_set(cand, pair_weights, occurrences)
            if sc > best_score:
                best_score = sc
                best = cand
        if best is None:
            # fallback: pick a random set
            best = random.sample(workloads, k)
        # registering occurencies
        for a, b in itertools.combinations(best, 2):
            occurrences[frozenset((a, b))] += 1
        sets.append({"set_index": idx, "members": sorted(best), "score": best_score})
    return sets, occurrences


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--matrix", required=True, help="path to matrix.csv")
    p.add_argument("--bin", default="./bin", help="bin dir (default ./bin)")
    p.add_argument("--k", type=int, default=16, help="set size (CPUs logical)")
    p.add_argument("--M", type=int, default=100, help="number of sets to generate")
    p.add_argument(
        "--tries",
        type=int,
        default=2000,
        help="candidates tested per set (performance knob)",
    )
    p.add_argument("--seed", type=int, default=42, help="random seed")
    p.add_argument("--out", default="generated_sets.json", help="output JSON file")
    p.add_argument(
        "--max_top_per_set",
        type=int,
        default=0,
        help="(optional) cap of top_k members in each set; 0 = disabled",
    )
    p.add_argument(
        "--top_k",
        type=int,
        default=32,
        help="(optional) define top_k worst workloads by pair-weight sum",
    )
    args = p.parse_args()

    workloads = read_workloads_from_bin(args.bin)
    print(f"Found {len(workloads)} workloads in {args.bin}")
    mat = read_matrix_csv(args.matrix)
    pair_weights = build_pair_weights(workloads, mat)

    # compute per-workload aggregate "badness" (sum of pair weights) to find top_k
    agg = {w: 0.0 for w in workloads}
    for pair, w in pair_weights.items():
        a, b = tuple(pair)
        agg[a] += w
        agg[b] += w
    top_list = sorted(workloads, key=lambda x: agg[x], reverse=True)[: args.top_k]

    max_top = args.max_top_per_set if args.max_top_per_set > 0 else None
    if max_top:
        print(f"Limiting up to {max_top} top workloads per set (top_k={args.top_k})")

    sets, occ = generate_sets(
        workloads,
        pair_weights,
        k=args.k,
        M=args.M,
        tries=args.tries,
        seed=args.seed,
        max_allow_top=max_top,
        top_list=top_list,
    )

    out = {
        "params": {
            "k": args.k,
            "M": args.M,
            "tries": args.tries,
            "seed": args.seed,
            "max_top_per_set": args.max_top_per_set,
            "top_k": args.top_k,
        },
        "workloads": workloads,
        "sets": sets,
        "pair_occurrences": {",".join(sorted(list(p))): c for p, c in occ.items()},
    }

    # fix pair_occurrences key formatting (frozenset -> "a,b")
    pair_occ = {}
    for p, cnt in occ.items():
        a, b = sorted(list(p))
        pair_occ[f"{a},{b}"] = cnt
    out["pair_occurrences"] = pair_occ

    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {args.out}")

    # print summary top pairs by weight
    print("\nTop pairs by weight (sample):")
    byw = sorted(pair_weights.items(), key=lambda x: x[1], reverse=True)[:20]
    for p, w in byw:
        a, b = sorted(list(p))
        print(f"  {a} , {b} -> {w:.3f}")


if __name__ == "__main__":
    main()

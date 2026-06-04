#!/usr/bin/env python3
"""
Plot stacked bar charts from perf_profile JSON output.

- Cada barra = um workload
- Segmentos = Branch, FP, INT_rest, Load, Store
- Mostra a composição percentual das instruções
- Cada categoria tem cor + textura (hatch) para melhor visualização
"""

from __future__ import annotations

from _bootstrap import ensure_project_root

PROJECT_ROOT = ensure_project_root()

import json
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import os

WORKLOAD_NAMES = {
    "branch_mispredict.out": "Branch Prediction Stress",
    "fp_add_ind.out": "FP Add (Ind.)",
    "fp_div_ind.out": "FP Div (Ind.)",
    "fp_mul_ind.out": "FP Mul (Ind.)",
    "fp_prf_stress.out": "FP Register Pressure",
    "long_dep_chain.out": "Int Add (Dep.)",
    "int_add_ind.out": "Int Add (Ind.)",
    "int_div_dep.out": "Int Div (Dep.)",
    "int_div_ind.out": "Int Div (Ind.)",
    "int_mul_ind.out": "Int Mul (Ind.)",
    "int_prf_stress.out": "Int Register Pressure",
    "memory_load_dep.out": "Mem Load 64 MiB (Dep.)",
    "memory_load_ind.out": "Mem Load 64 MiB (Ind.)",
    "memory_store_ind.out": "Mem Store 64 MiB (Ind.)"
}

WORKLOAD_ORDER = [
    "Branch Prediction Stress",
    "Int Register Pressure",
    "Int Add (Dep.)",
    "Int Add (Ind.)",
    "Int Mul (Ind.)",
    "Int Div (Dep.)",
    "Int Div (Ind.)",
    "FP Register Pressure",
    "FP Add (Ind.)",
    "FP Mul (Ind.)",
    "FP Div (Ind.)",
    "Mem Load 64 MiB (Dep.)",
    "Mem Load 64 MiB (Ind.)",
    "Mem Store 64 MiB (Ind.)"
]

def load_json_files(file_list):
    data_list = []
    for f in file_list:
        with open(f, 'r') as fp:
            data_list.append(json.load(fp))
    return data_list

def prepare_dataframe(data_list):
    rows = []
    for d in data_list:
        workload_name = d["workload_name"]
        display_name = WORKLOAD_NAMES.get(workload_name, workload_name)
        
        row = {
            "workload": display_name,
            "Branches": d["DERIVED"].get("Branches",0),
            "Floating-point": d["DERIVED"].get("FP_total",0),
            "Integer": d["DERIVED"].get("INT_rest",0),
            "Load": d["DERIVED"].get("Load",0),
            "Store": d["DERIVED"].get("Store",0)
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df.set_index("workload", inplace=True)

    df = df.reindex([w for w in WORKLOAD_ORDER if w in df.index])

    df_percent = df.div(df.sum(axis=1), axis=0) * 100
    return df_percent

def plot_stacked_bar(df):
    width_pt = 455.24413
    inches_per_pt = 1.0 / 72.27
    fig_width = width_pt * inches_per_pt
    fig_height = fig_width * 0.5

    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
        "font.size": 11,
        "axes.labelsize": 11,
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "figure.figsize": [fig_width, fig_height],
        "figure.autolayout": True,
    })

    fig, ax = plt.subplots()

    colors = {
        "Branches": "#f39c12",
        "Floating-point": "#3498db",
        "Integer": "#2ecc71",
        "Load": "#9b59b6",
        "Store": "#e74c3c"
    }

    hatches = {
        "Branches": "oo",
        "Floating-point": "xx",
        "Integer": "//",
        "Load": "..",
        "Store": "--"
    }

    bottom = pd.Series([0]*len(df), index=df.index)

    for col in df.columns:
        ax.bar(
            df.index, df[col], 
            bottom=bottom, 
            color=colors[col], 
            label=col, 
            hatch=hatches[col]
        )
        bottom += df[col]

    ax.yaxis.grid(True, linestyle=':', linewidth=0.8, alpha=0.7)

    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("Distrubuição de Instruções (\\%)")
    ax.set_xlabel("Workloads")

    ax.legend(
        title="Tipos de Instrução",
        loc='lower center',
        bbox_to_anchor=(0.5, 1.02),
        ncol=len(df.columns),
        fontsize=9,
        frameon=False,
        handletextpad=0.4,
        columnspacing=1.0
    )

    plt.tight_layout()
    plt.xticks(rotation=45, ha='right')
    plt.savefig("workloads.pdf", bbox_inches="tight")

def main():
    parser = argparse.ArgumentParser(description="Plot perf_profile JSON as stacked bar charts")
    parser.add_argument("json_files", nargs="+", help="JSON files from perf_profile.py")
    args = parser.parse_args()

    data_list = load_json_files(args.json_files)
    df = prepare_dataframe(data_list)
    plot_stacked_bar(df)

if __name__ == "__main__":
    main()
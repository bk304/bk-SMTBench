# Profiling

Essa pasta reúne os scripts usados para coletar dados dos workloads.

Use os scripts conforme a tarefa desejada:

`perf_profile.py`
Roda o `perf stat` em um workload individual e salva um JSON com os contadores e valores derivados.

Uso:
```bash
python3 scripts/profiling/perf_profile.py ./bin/<workload>.out --duration 20 --cpu 0
```

`dual_perf_profile.py`
Roda dois workloads ao mesmo tempo nos threads SMT do mesmo core físico e imprime os contadores de ambos.

Uso:
```bash
python3 scripts/profiling/dual_perf_profile.py ./bin/<a>.out ./bin/<b>.out --duration 20
```

`plot_profile.py`
Gera um gráfico com a composição percentual das instruções a partir dos JSONs produzidos por `perf_profile.py`.

Uso:
```bash
python3 scripts/profiling/plot_profile.py ./profiles/<workload>.json
```

`runner.py`
Executa todos os workloads em pares, organiza os resultados e salva cada experimento em `./res`.

Uso:
```bash
make
python3 scripts/performance/runner.py
```

Os binários precisam existir em `./bin`, mas cada comando pode ser usado de forma independente conforme a tarefa.
# Performance

Essa pasta reúne os scripts usados para transformar e visualizar os dados coletados.

Os scripts desta pasta são independentes e servem para tarefas diferentes.

`runner.py`
Executa todos os workloads em pares, organiza os resultados e salva cada experimento em `./res`.

Uso:
```bash
make
python3 scripts/performance/runner.py
```

`analyze.py`
Lê um experimento já salvo em `./res`, calcula os IPCs agregados e gera um único `result.csv` com todas as tabelas.

Uso:
```bash
python3 scripts/performance/analyze.py
```

O `runner.py` cria os dados, enquanto o `analyze.py` consome um experimento já salvo. Para plotar a composição de instruções, use `scripts/profiling/plot_profile.py`.
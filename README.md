Esse projeto é um benchmark para me ajudar a descobrir quais recursos são mais valiosos em uma arquitetura.

Os scripts principais estão organizados por tarefa:
* scripts/profiling/: coleta dos dados dos workloads e geração dos gráficos de composição.
* scripts/performance/: execução organizada dos workloads e análise dos resultados.
* scripts/corr/: script para me ajudar a calcular correlações de Pearson e Spearman.

O fluxo mais comum é executar a coleta com `scripts/performance/runner.py`, analisar com `scripts/performance/analyze.py`.

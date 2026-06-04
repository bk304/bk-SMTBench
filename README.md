[WIP]

Planejo implementar um escalonador que considera mais o Simutaneos-Multithread (SMT) no load-balance, assim aproveitando mais os recursos da CPU. 
Esse projeto é um benchmark para me ajudar a descobrir quais recursos são mais valiosos em uma arquitetura e também para me ajudar a medir o quão bem o escalonador funciona.

Recentemente a Intel fez um projeto muito parecido, o Cache Aware Scheduler, que tenta melhorar o uso da LLC atraves de modificação do comportamento do loadbalance.
Para medir a performance do scheduler deles foi usado: hackbench, schbench, Netperf/Tbench, stress-ng e ChaCha20-xiangshan.
Esses benchmarks são úteis para demonstrar o diferencial de performance após aplicar uma estratégia nova, porém não me ajudam a entender melhor o que um load-balance pode fazer para evitar degradação de desempenho por causa de compartilhamento de recursos via SMT.

Por enquanto, os scripts principais estão organizados por tarefa:
* scripts/profiling/: coleta dos dados dos workloads e geração dos gráficos de composição.
* scripts/performance/: execução organizada dos workloads e análise dos resultados.

O fluxo mais comum é executar a coleta com `scripts/performance/runner.py`, analisar com `scripts/performance/analyze.py` e, se quiser, gerar gráficos com `scripts/profiling/plot_profile.py`.

[TODO]
Acredito que existam 3 métricas importantes que o benchmark deve reportar:
* Worst-case slowdown: Pouco importa a vazão média se existe um caso que foi tremendamente degradado;
* 99p latency: Se a latência de tasks aumentar muito é um problema.
* Fairness: Se a perda de desempenho está sendo igual entre os workloads.

[Issues]
1. Eu não consegui fazer um workload para estressar a uop cache, pois não achei um contador de performance no Zen que me permitisse ler o uso da cache. Eu poderia medir a queda do IPC (Instructions Per Cycle), mas só isso não me garantiria de que é devido ao lotamento do uop cache.

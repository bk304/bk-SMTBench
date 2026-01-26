[WIP]

Planejo implementar um escalonador que considera mais o Simutaneos-Multithread (SMT) no load-balance, assim aproveitando mais os recursos da CPU. 
Esse projeto é um benchmark para me ajudar a descobrir quais recursos são mais valiosos em uma arquitetura e também para me ajudar a medir o quão bem o escalonador funciona.

Recentemente a Intel fez um projeto muito parecido, o Cache Aware Scheduler, que tenta melhorar o uso da LLC atraves de modificação do comportamento do loadbalance.
Para medir a performance do scheduler deles foi usado: hackbench, schbench, Netperf/Tbench, stress-ng e ChaCha20-xiangshan.
Esses benchmarks são úteis para demonstrar o diferencial de performance após aplicar uma estratégia nova, porém não me ajudam a entender melhor o que um load-balance pode fazer para evitar degradação de desempenho por causa de compartilhamento de recursos via SMT.

Por enquanto, há 2 scripts executáveis (logo haverá 3):
* runner.py: Esse script busca e executa todos os binários de workloads. A execução é feita em pares em uma única CPU, assim medindo o quão degradante cada workload é contra os outros. Todos os resultados são armazenados para analise posterior.
* analyze.py: Esse script serve para formatar os resultados objetivos pelo runner.py. Ele irá organizar e gerar tabelas .csv.
* [WIP] sched_evalution.py: Esse script deve usa a analise anterior para executar testes visando medir o quão bem o escalonador atual consegue lidar com o gerenciamento de recursos da CPU com SMT. Ou seja, o objetivo não é medir se estamos ganhando ou perdendo performance em algumas situações, mas sim testar se o escalonador está de fato conseguindo evitar casos onde há muita contenção de recursos.

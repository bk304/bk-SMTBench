[WIP]

Planejo implementar um escalonador que considera mais o Simutaneos-Multithread (SMT) no load-balance, assim aproveitando mais os recursos da CPU. 
Mas não achei nenhum benchmark que me ajudasse a medir o quão bem está funcionando. Então estou criando meu proprio benchmark.

Por enquanto, há 2 scripts executáveis (logo haverá 3):
* runner.py: Esse script busca e executa todos os binários de workloads. A execução é feita em pares em uma única CPU, assim medindo o quão degradante cada workload é contra os outros. Todos os resultados são armazenados para analise posterior.
* analyze.py: Esse script serve para formatar os resultados objetivos pelo runner.py. Ele irá organizar e gerar tabelas .csv.
* [WIP] sched_evalution.py: Esse script deve usa a analise anterior para executar testes visando medir o quão bem o escalonador atual consegue lidar com o gerenciamento de recursos da CPU com SMT.

#pragma once

#include <charconv>
#include <chrono>
#include <cstring>
#include <thread>

#include <stdlib.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>
#include <string.h>


volatile bool alive = true;
std::thread *timer;

struct perf_event_attr pe;
int fd_cycles, fd_instr;
long long count_cycles, count_instr;

static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
                            int cpu, int group_fd, unsigned long flags) {
    return syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
}

bool parse_int(const char* s, int &out) {
    auto [ptr, ec] = std::from_chars(s, s + std::strlen(s), out);
    return ec == std::errc() && *ptr == '\0';
}

void killAfter(int timeSeconds){
    std::this_thread::sleep_for(std::chrono::seconds(timeSeconds));
    alive = false;
}

void init(int argc, char* argv[]){

    int durationSeconds;
    if (argc != 2 || !parse_int(argv[1], durationSeconds)) {
        perror("Invalid parameter.");
        exit(EXIT_FAILURE);
    }

    alive = true;

    memset(&pe, 0, sizeof(struct perf_event_attr));
    pe.size = sizeof(struct perf_event_attr);
    pe.disabled = 1;          // Começa pausado
    pe.exclude_kernel = 1;    // IMPORTANTE: permite rodar sem sudo
    pe.exclude_hv = 1;

    // 1. Configurar contador de Ciclos
    pe.type = PERF_TYPE_HARDWARE;
    pe.config = PERF_COUNT_HW_CPU_CYCLES;
    fd_cycles = perf_event_open(&pe, 0, -1, -1, 0); // 0 = este processo

    // 2. Configurar contador de Instruções (Retired)
    pe.config = PERF_COUNT_HW_INSTRUCTIONS;
    fd_instr = perf_event_open(&pe, 0, -1, -1, 0);

    if (fd_cycles == -1 || fd_instr == -1) {
        perror("Erro ao abrir perf_event. Tente: sudo sysctl -w kernel.perf_event_paranoid=1");
        exit(EXIT_FAILURE);
    }

    timer = new std::thread(killAfter, durationSeconds);

    // 3. Inicia contadores
    ioctl(fd_cycles, PERF_EVENT_IOC_RESET, 0);
    ioctl(fd_cycles, PERF_EVENT_IOC_ENABLE, 0);
    ioctl(fd_instr, PERF_EVENT_IOC_RESET, 0);
    ioctl(fd_instr, PERF_EVENT_IOC_ENABLE, 0);
}

void fini(const char* name){
    ioctl(fd_cycles, PERF_EVENT_IOC_DISABLE, 0);
    ioctl(fd_instr, PERF_EVENT_IOC_DISABLE, 0);
    
    timer->join();

    read(fd_cycles, &count_cycles, sizeof(long long));
    read(fd_instr, &count_instr, sizeof(long long));
    close(fd_cycles);   
    close(fd_instr);

    printf("%s | Cyles: %lld | Instructions: %lld | IPC: %.2f\n", name, count_cycles, count_instr, count_cycles != 0 ? (double)count_instr / count_cycles : 0.0);

}

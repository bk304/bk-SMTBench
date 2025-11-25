#include <stdint.h>
#include <stdio.h>

#include "../workload.h"

const char* name = "int_mul_ind";

void workload() {
    uint64_t i = 0;

    // Inicializar registradores em assembly puro
    asm volatile(
        "mov $1, %%r12\n\t"
        "mov $1, %%r13\n\t"
        "mov $1, %%r14\n\t"
        "mov $1, %%r15\n\t"
        "mov $1, %%rbx\n\t"
        "mov $1, %%rbp\n\t"
        "mov $1, %%r8\n\t"
        "mov $1, %%r9\n\t"
        :
        :
        : "r12", "r13", "r14", "r15", "rbx", "rbp", "r8", "r9"
    );

    do {
        asm volatile(
            // 32 instruções IMUL puras
            "imul %%r12, %%r12\n\t"
            "imul %%r13, %%r13\n\t"
            "imul %%r14, %%r14\n\t"
            "imul %%r15, %%r15\n\t"
            "imul %%rbx, %%rbx\n\t"
            "imul %%rbp, %%rbp\n\t"
            "imul %%r8, %%r8\n\t"
            "imul %%r9, %%r9\n\t"

            "imul %%r12, %%r12\n\t"
            "imul %%r13, %%r13\n\t"
            "imul %%r14, %%r14\n\t"
            "imul %%r15, %%r15\n\t"
            "imul %%rbx, %%rbx\n\t"
            "imul %%rbp, %%rbp\n\t"
            "imul %%r8, %%r8\n\t"
            "imul %%r9, %%r9\n\t"

            "imul %%r12, %%r12\n\t"
            "imul %%r13, %%r13\n\t"
            "imul %%r14, %%r14\n\t"
            "imul %%r15, %%r15\n\t"
            "imul %%rbx, %%rbx\n\t"
            "imul %%rbp, %%rbp\n\t"
            "imul %%r8, %%r8\n\t"
            "imul %%r9, %%r9\n\t"

            "imul %%r12, %%r12\n\t"
            "imul %%r13, %%r13\n\t"
            "imul %%r14, %%r14\n\t"
            "imul %%r15, %%r15\n\t"
            "imul %%rbx, %%rbx\n\t"
            "imul %%rbp, %%rbp\n\t"
            "imul %%r8, %%r8\n\t"
            "imul %%r9, %%r9\n\t"
            :
            :
            : "r12", "r13", "r14", "r15", "rbx", "rbp", "r8", "r9"
        );
        i++;
    } while (alive);

    printf("%s | Result: %lu\n", name, i);
}

int main(int argc, char* argv[]) {
    int durationSeconds;
    if (argc != 2 || !parse_int(argv[1], durationSeconds)) {
        fprintf(stderr, "Invalid parameter.\n");
        return -1;
    }

    init_workload(durationSeconds);
    workload();
    fini_workload();

    return 0;
}

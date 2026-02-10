#include <stdint.h>
#include <stdio.h>

#include <cstdint>

#include "../workload.h"

const char* name = "long_dep_chain";

void workload() {
    uint64_t i = 0;

    asm volatile(
        "xor %%r12, %%r12\n\t"
        :
        :
        : "r12"
    );

    do {
        asm volatile(
            // Cadeia longa e totalmente dependente
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"

            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"

            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            :
            :
            : "r12", "memory"
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

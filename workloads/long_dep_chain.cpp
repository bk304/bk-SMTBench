#include <stdint.h>

#include <cstdint>

#include "../workload.h"

const char* name = "long_dep_chain";

void workload() {
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
    } while (alive);
}

int main(int argc, char* argv[]) {
    init(argc, argv);
    workload();
    fini(name);

    return 0;
}

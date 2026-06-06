#include <stdint.h>

#include <cstdint>

#include "../workload.h"

const char* name = "int_add_dep";

void workload() {
    asm volatile(
        "xor %%r12, %%r12\n\t"
        :
        :
        : "r12"
    );

    do {
        asm volatile(
            ".align 64\n\t"

            // Cadeia longa e totalmente dependente
            ".rept 50\n\t"
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
            ".endr\n\t"
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

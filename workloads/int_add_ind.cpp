#include <stdint.h>
#include <stdio.h>

#include <cstdint>

#include "../workload.h"

const char* name = "int_add_ind";

void workload() {
    uint64_t i = 0;

    asm volatile(
        "xor %%r12, %%r12\n\t"
        "xor %%r13, %%r13\n\t"
        "xor %%r14, %%r14\n\t"
        "xor %%r15, %%r15\n\t"
        "xor %%rbx, %%rbx\n\t"
        "xor %%rbp, %%rbp\n\t"
        "xor %%r8, %%r8\n\t"
        "xor %%r9, %%r9\n\t"
        :
        :
        : "r12", "r13", "r14", "r15", "rbx", "rbp", "r8", "r9"
    );

    do {
        asm volatile(
            "add %%r12, %%r12\n\t"
            "add %%r13, %%r13\n\t"
            "add %%r14, %%r14\n\t"
            "add %%r15, %%r15\n\t"
            "add %%rbx, %%rbx\n\t"
            "add %%rbp, %%rbp\n\t"
            "add %%r8, %%r8\n\t"
            "add %%r9, %%r9\n\t"

            "add %%r12, %%r12\n\t"
            "add %%r13, %%r13\n\t"
            "add %%r14, %%r14\n\t"
            "add %%r15, %%r15\n\t"
            "add %%rbx, %%rbx\n\t"
            "add %%rbp, %%rbp\n\t"
            "add %%r8, %%r8\n\t"
            "add %%r9, %%r9\n\t"

            "add %%r12, %%r12\n\t"
            "add %%r13, %%r13\n\t"
            "add %%r14, %%r14\n\t"
            "add %%r15, %%r15\n\t"
            "add %%rbx, %%rbx\n\t"
            "add %%rbp, %%rbp\n\t"
            "add %%r8, %%r8\n\t"
            "add %%r9, %%r9\n\t"

            "add %%r12, %%r12\n\t"
            "add %%r13, %%r13\n\t"
            "add %%r14, %%r14\n\t"
            "add %%r15, %%r15\n\t"
            "add %%rbx, %%rbx\n\t"
            "add %%rbp, %%rbp\n\t"
            "add %%r8, %%r8\n\t"
            "add %%r9, %%r9\n\t"
            :
            :
            : "r12", "r13", "r14", "r15", "rbx", "rbp", "r8", "r9", "memory"
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

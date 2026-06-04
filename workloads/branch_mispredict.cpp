#include <stdint.h>

#include "../workload.h"

const char* name = "branch_mispredict";

// 3-way indirect branch
// Source: Agner Fog
void workload() {

    while (alive) {
        asm volatile(
            "mov $1000, %%edi\n\t"
            "xor %%eax, %%eax\n\t"
            "xor %%r8d, %%r8d\n\t"
            ".align 16\n\t"
            "LL9:\n\t"
            "nop\n\t"
            "inc %%eax\n\t"
            "lea L9_1(%%rip), %%rbx\n\t"
            "lea L9_2(%%rip), %%rcx\n\t"
            "lea L9_3(%%rip), %%rdx\n\t"
            "cmp $2, %%eax\n\t"
            "cmovb %%rbx, %%rcx\n\t"
            "cmova %%rdx, %%rcx\n\t"
            "cmova %%r8d, %%eax\n\t"
            "nop\n\t"
            "jmp *%%rcx\n\t"
            "nop\n\t"
            "L9_1:\n\t nop\n\t"
            "L9_2:\n\t nop\n\t"
            "L9_3:\n\t nop\n\t nop\n\t"
            "dec %%edi\n\t"
            "jnz LL9\n\t"
            :
            :
            : "eax", "edi", "rbx", "rcx", "rdx", "r8", "cc"
        );
    }
}

int main(int argc, char* argv[]) {
    init(argc, argv);
    workload();
    fini(name);

    return 0;
}

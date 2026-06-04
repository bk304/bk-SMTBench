#include <stdint.h>

#include "../workload.h"

const char* name = "int_div_ind";

void workload() {
    uint64_t count = 0;

    asm volatile("mov $0x1, %%rbx" : : : "rbx");

    do {
        asm volatile("mov $12345, %%rax" ::: "rax");
        asm volatile("mov $0, %%rdx" ::: "rdx");
        asm volatile("idiv %%rbx" ::: "rax", "rdx");

        asm volatile("mov $12346, %%rax" ::: "rax");
        asm volatile("mov $0, %%rdx" ::: "rdx");
        asm volatile("idiv %%rbx" ::: "rax", "rdx");

        asm volatile("mov $12347, %%rax" ::: "rax");
        asm volatile("mov $0, %%rdx" ::: "rdx");
        asm volatile("idiv %%rbx" ::: "rax", "rdx");

        asm volatile("mov $12348, %%rax" ::: "rax");
        asm volatile("mov $0, %%rdx" ::: "rdx");
        asm volatile("idiv %%rbx" ::: "rax", "rdx");

        asm volatile("mov $12349, %%rax" ::: "rax");
        asm volatile("mov $0, %%rdx" ::: "rdx");
        asm volatile("idiv %%rbx" ::: "rax", "rdx");

        asm volatile("mov $12350, %%rax" ::: "rax");
        asm volatile("mov $0, %%rdx" ::: "rdx");
        asm volatile("idiv %%rbx" ::: "rax", "rdx");

        asm volatile("mov $12351, %%rax" ::: "rax");
        asm volatile("mov $0, %%rdx" ::: "rdx");
        asm volatile("idiv %%rbx" ::: "rax", "rdx");

        asm volatile("mov $12352, %%rax" ::: "rax");
        asm volatile("mov $0, %%rdx" ::: "rdx");
        asm volatile("idiv %%rbx" ::: "rax", "rdx");
    } while (alive);
    asm volatile("mov %%rbx, %0" : "=r"(count) : : "rbx");

    volatile int64_t avoidOtimization = count;
    (void)avoidOtimization;
}

int main(int argc, char* argv[]) {
    init(argc, argv);
    workload();
    fini(name);

    return 0;
}

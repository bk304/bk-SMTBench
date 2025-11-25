#include <stdint.h>
#include <stdio.h>

#include "../workload.h"

const char* name = "int_div_ind";

void workload() {
    uint64_t i = 0, count = 0;

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
      i++;
    } while (alive);
    asm volatile("mov %%rbx, %0" : "=r"(count) : : "rbx");

    volatile int64_t avoidOtimization = count;
    (void)avoidOtimization;

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

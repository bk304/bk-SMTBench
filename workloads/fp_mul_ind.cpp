#include <stdint.h>
#include <stdio.h>

#include "../workload.h"

const char* name = "fp_mul_ind";

void workload() {
    uint64_t i = 0;
    double count = 0.00, in = 1.00;

    asm volatile("push %0" ::"r"(in) :);

    asm volatile("subsd %%xmm0, %%xmm0" : : : "xmm0");
    asm volatile("subsd %%xmm1, %%xmm1" : : : "xmm1");
    asm volatile("subsd %%xmm2, %%xmm2" : : : "xmm2");
    asm volatile("subsd %%xmm3, %%xmm3" : : : "xmm3");
    asm volatile("subsd %%xmm4, %%xmm4" : : : "xmm4");
    asm volatile("subsd %%xmm5, %%xmm5" : : : "xmm5");
    asm volatile("subsd %%xmm6, %%xmm6" : : : "xmm6");
    asm volatile("subsd %%xmm7, %%xmm7" : : : "xmm7");

    asm volatile("movsd (%%rsp), %%xmm0" : : : "xmm0");
    asm volatile("movsd (%%rsp), %%xmm1" : : : "xmm1");
    asm volatile("movsd (%%rsp), %%xmm2" : : : "xmm2");
    asm volatile("movsd (%%rsp), %%xmm3" : : : "xmm3");
    asm volatile("movsd (%%rsp), %%xmm4" : : : "xmm4");
    asm volatile("movsd (%%rsp), %%xmm5" : : : "xmm5");
    asm volatile("movsd (%%rsp), %%xmm6" : : : "xmm6");
    asm volatile("movsd (%%rsp), %%xmm7" : : : "xmm7");

    asm volatile("pop %%rbx" : : : "rbx");

    do {
      asm volatile("mulsd %%xmm0, %%xmm0" : : : "xmm0");
      asm volatile("mulsd %%xmm1, %%xmm1" : : : "xmm1");
      asm volatile("mulsd %%xmm2, %%xmm2" : : : "xmm2");
      asm volatile("mulsd %%xmm3, %%xmm3" : : : "xmm3");
      asm volatile("mulsd %%xmm4, %%xmm4" : : : "xmm4");
      asm volatile("mulsd %%xmm5, %%xmm5" : : : "xmm5");
      asm volatile("mulsd %%xmm6, %%xmm6" : : : "xmm6");
      asm volatile("mulsd %%xmm7, %%xmm7" : : : "xmm7");

      asm volatile("mulsd %%xmm0, %%xmm0" : : : "xmm0");
      asm volatile("mulsd %%xmm1, %%xmm1" : : : "xmm1");
      asm volatile("mulsd %%xmm2, %%xmm2" : : : "xmm2");
      asm volatile("mulsd %%xmm3, %%xmm3" : : : "xmm3");
      asm volatile("mulsd %%xmm4, %%xmm4" : : : "xmm4");
      asm volatile("mulsd %%xmm5, %%xmm5" : : : "xmm5");
      asm volatile("mulsd %%xmm6, %%xmm6" : : : "xmm6");
      asm volatile("mulsd %%xmm7, %%xmm7" : : : "xmm7");

      asm volatile("mulsd %%xmm0, %%xmm0" : : : "xmm0");
      asm volatile("mulsd %%xmm1, %%xmm1" : : : "xmm1");
      asm volatile("mulsd %%xmm2, %%xmm2" : : : "xmm2");
      asm volatile("mulsd %%xmm3, %%xmm3" : : : "xmm3");
      asm volatile("mulsd %%xmm4, %%xmm4" : : : "xmm4");
      asm volatile("mulsd %%xmm5, %%xmm5" : : : "xmm5");
      asm volatile("mulsd %%xmm6, %%xmm6" : : : "xmm6");
      asm volatile("mulsd %%xmm7, %%xmm7" : : : "xmm7");

      asm volatile("mulsd %%xmm0, %%xmm0" : : : "xmm0");
      asm volatile("mulsd %%xmm1, %%xmm1" : : : "xmm1");
      asm volatile("mulsd %%xmm2, %%xmm2" : : : "xmm2");
      asm volatile("mulsd %%xmm3, %%xmm3" : : : "xmm3");
      asm volatile("mulsd %%xmm4, %%xmm4" : : : "xmm4");
      asm volatile("mulsd %%xmm5, %%xmm5" : : : "xmm5");
      asm volatile("mulsd %%xmm6, %%xmm6" : : : "xmm6");
      asm volatile("mulsd %%xmm7, %%xmm7" : : : "xmm7");
      i++;
    } while (alive);

    asm volatile("push $0x0" :::);
    asm volatile("movsd %%xmm0, (%%rsp)" : : :);
    asm volatile("mov (%%rsp), %0" : "=r"(count) : :);
    asm volatile("pop %%rbx" : : : "rbx");

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

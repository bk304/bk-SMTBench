#include <stdint.h>

#include "../workload.h"

const char* name = "fp_div_ind";

void workload() {
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
      asm volatile("divsd %%xmm0, %%xmm0" : : : "xmm0");
      asm volatile("divsd %%xmm1, %%xmm1" : : : "xmm1");
      asm volatile("divsd %%xmm2, %%xmm2" : : : "xmm2");
      asm volatile("divsd %%xmm3, %%xmm3" : : : "xmm3");
      asm volatile("divsd %%xmm4, %%xmm4" : : : "xmm4");
      asm volatile("divsd %%xmm5, %%xmm5" : : : "xmm5");
      asm volatile("divsd %%xmm6, %%xmm6" : : : "xmm6");
      asm volatile("divsd %%xmm7, %%xmm7" : : : "xmm7");

      asm volatile("divsd %%xmm0, %%xmm0" : : : "xmm0");
      asm volatile("divsd %%xmm1, %%xmm1" : : : "xmm1");
      asm volatile("divsd %%xmm2, %%xmm2" : : : "xmm2");
      asm volatile("divsd %%xmm3, %%xmm3" : : : "xmm3");
      asm volatile("divsd %%xmm4, %%xmm4" : : : "xmm4");
      asm volatile("divsd %%xmm5, %%xmm5" : : : "xmm5");
      asm volatile("divsd %%xmm6, %%xmm6" : : : "xmm6");
      asm volatile("divsd %%xmm7, %%xmm7" : : : "xmm7");

      asm volatile("divsd %%xmm0, %%xmm0" : : : "xmm0");
      asm volatile("divsd %%xmm1, %%xmm1" : : : "xmm1");
      asm volatile("divsd %%xmm2, %%xmm2" : : : "xmm2");
      asm volatile("divsd %%xmm3, %%xmm3" : : : "xmm3");
      asm volatile("divsd %%xmm4, %%xmm4" : : : "xmm4");
      asm volatile("divsd %%xmm5, %%xmm5" : : : "xmm5");
      asm volatile("divsd %%xmm6, %%xmm6" : : : "xmm6");
      asm volatile("divsd %%xmm7, %%xmm7" : : : "xmm7");

      asm volatile("divsd %%xmm0, %%xmm0" : : : "xmm0");
      asm volatile("divsd %%xmm1, %%xmm1" : : : "xmm1");
      asm volatile("divsd %%xmm2, %%xmm2" : : : "xmm2");
      asm volatile("divsd %%xmm3, %%xmm3" : : : "xmm3");
      asm volatile("divsd %%xmm4, %%xmm4" : : : "xmm4");
      asm volatile("divsd %%xmm5, %%xmm5" : : : "xmm5");
      asm volatile("divsd %%xmm6, %%xmm6" : : : "xmm6");
      asm volatile("divsd %%xmm7, %%xmm7" : : : "xmm7");
    } while (alive);

    asm volatile("push $0x0" :::);
    asm volatile("movsd %%xmm0, (%%rsp)" : : :);
    asm volatile("mov (%%rsp), %0" : "=r"(count) : :);
    asm volatile("pop %%rbx" : : : "rbx");

    volatile double avoidOtimization = count;
    (void)avoidOtimization;
}

int main(int argc, char* argv[]) {
    init(argc, argv);
    workload();
    fini(name);

    return 0;
}
